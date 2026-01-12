import streamlit as st
from PIL import Image
from gtts import gTTS
import requests 
import base64
import json
import io  # New import for memory handling

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# --- 2. SECURE KEY HANDLING ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    GOOGLE_API_KEY = st.sidebar.text_input("🔑 Enter Google API Key", type="password")
    WEATHER_API_KEY = st.sidebar.text_input("🌦️ Enter Weather API Key", type="password")

# --- 3. SMART FUNCTIONS ---

def get_working_models(api_key):
    if not api_key: return []
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'].replace('models/', '') for m in data.get('models', []) 
                      if 'generateContent' in m.get('supportedGenerationMethods', [])]
            return models
        else:
            return []
    except:
        return []

def analyze_image_direct(api_key, model_name, image_bytes, prompt):
    if not api_key: return "Please enter an API Key first."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Google Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection Error: {e}"

# --- 4. WEATHER FUNCTION ---
def get_weather_auto(city):
    if not WEATHER_API_KEY: return "Unavailable", "Clear"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{data['weather'][0]['main']}, {data['main']['temp']}°C", data['weather'][0]['main']
    except:
        pass
    return "Unavailable", "Clear"

# --- 5. CSS STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                    url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=3000");
        background-size: cover; background-attachment: fixed;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.95); padding: 30px; 
        border-radius: 15px; border-top: 5px solid #2e7d32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); color: black;
    }
    .stButton>button {
        background-color: #2e7d32; color: white; border-radius: 25px;
        height: 50px; font-size: 18px; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    h1, h2, h3 { color: #1b5e20 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 6. SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = ""

# --- 7. LOGIN PAGE ---
def login():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="glass-card" style="text-align:center;"><h1>🌿 GreenMitra</h1><p>Smart Assistant</p></div>', unsafe_allow_html=True)
        st.write("")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 PIN (Any Number)", type="password")
        if st.button("Login"):
            if email and password.isdigit():
                st.session_state['logged_in'] = True
                st.session_state['user'] = email.split('@')[0]
                st.rerun()
            else:
                st.error("Enter Email and Numeric PIN")

# --- 8. DASHBOARD ---
def dashboard():
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        
        st.subheader("🤖 AI Brain")
        if not GOOGLE_API_KEY:
            st.warning("⚠️ Enter Key Above")
            available_models = []
        else:
            available_models = get_working_models(GOOGLE_API_KEY)
        
        if available_models:
            default_idx = 0
            for i, m in enumerate(available_models):
                if 'flash' in m and '1.5' in m: default_idx = i
            selected_model = st.selectbox("Select Model", available_models, index=default_idx)
            st.success("✅ Online")
        else:
            selected_model = "gemini-1.5-flash"

        st.markdown("---")
        city = st.text_input("Village", "Kolhapur")
        w_text, w_cond = get_weather_auto(city)
        st.success(f"📍 {w_text}")
        st.markdown("---")
        lang = st.selectbox("Language", ["Marathi", "Hindi", "English"])
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        if st.button("Logout"):
            st.session_state['logged_in'] = False; st.rerun()

    c1, c2 = st.columns([1, 5])
    with c1: st.write("# 🌿")
    with c2: st.title("GreenMitra Dashboard")
    
    mode = st.radio("Input:", ["📂 Upload", "📸 Camera"], horizontal=True)
    file = None
    if mode == "📸 Camera": file = st.camera_input("Scan")
    else: file = st.file_uploader("Upload", type=['jpg','png','jpeg'])
        
    if file:
        st.image(file, width=300)
        
        if st.button("🔍 Analyze (पीक तपासा)"):
            with st.spinner("Diagnosing..."):
                try:
                    img_bytes = file.getvalue()
                    prompt = f"""
                    Expert Agronomist. Location: {city}, Weather: {w_text}.
                    1. Disease Name. 2. Natural Remedy. 
                    3. If {w_cond} is Rainy, warn farmer.
                    4. Language: {lang}.
                    """
                    res = analyze_image_direct(GOOGLE_API_KEY, selected_model, img_bytes, prompt)
                    
                    if "Error" in res:
                        st.error(f"❌ {res}")
                    else:
                        st.markdown(f'<div class="glass-card"><h3>✅ Report</h3><p>{res}</p></div>', unsafe_allow_html=True)
                        
                        # --- THE FIX: AUDIO IN MEMORY ---
                        # Instead of saving to "cure.mp3", we write to RAM
                        tts = gTTS(res, lang=lang_map[lang])
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3")
                    
                except Exception as e:
                    st.error(f"System Error: {e}")

if st.session_state['logged_in']: dashboard()
else: login()
