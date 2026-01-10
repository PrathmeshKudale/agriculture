import streamlit as st
from PIL import Image
from gtts import gTTS
import requests 
import base64
import json

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# ⚠️ PASTE YOUR KEYS HERE ⚠️
GOOGLE_API_KEY = "AIzaSyCBKJrGucoWrMEQMBTPV0d1HZN5AGnje80"
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40"

# --- 2. DIRECT API FUNCTION (Fixed Model Name) ---
def analyze_image_direct(api_key, image_bytes, prompt):
    """
    Direct connection using the 'latest' alias to fix 404 errors.
    """
    # Using 'gemini-1.5-flash-latest' often resolves the "not found" issue
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    # Encode Image
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                }
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

# --- 3. WEATHER FUNCTION ---
def get_weather_auto(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{data['weather'][0]['main']}, {data['main']['temp']}°C", data['weather'][0]['main']
    except:
        pass
    return "Unavailable", "Clear"

# --- 4. CSS STYLING ---
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: black;
    }
    .stButton>button {
        background-color: #2e7d32; color: white; border-radius: 25px;
        height: 50px; font-size: 18px; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    h1, h2, h3 { color: #1b5e20 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. SESSION ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = ""

# --- 6. LOGIN PAGE ---
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

# --- 7. DASHBOARD ---
def dashboard():
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        st.info("🤖 AI Brain: Flash Latest (Direct)")
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
                    
                    res = analyze_image_direct(GOOGLE_API_KEY, img_bytes, prompt)
                    
                    if "Error" in res:
                        st.error(f"❌ {res}")
                    else:
                        st.markdown(f'<div class="glass-card"><h3>✅ Report</h3><p>{res}</p></div>', unsafe_allow_html=True)
                        tts = gTTS(res, lang=lang_map[lang])
                        tts.save("cure.mp3")
                        st.audio("cure.mp3")
                    
                except Exception as e:
                    st.error(f"System Error: {e}")

# --- RUN ---
if st.session_state['logged_in']:
    dashboard()
else:
    login()
