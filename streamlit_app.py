import streamlit as st
from PIL import Image
import requests 
import base64
import io
from gtts import gTTS

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# --- 2. SECURE KEY HANDLING ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("🚨 Critical Error: Google API Key is missing in Secrets!")
    st.stop()

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- 3. SMART FUNCTIONS ---
def get_working_models(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'].replace('models/', '') for m in data.get('models', []) 
                      if 'generateContent' in m.get('supportedGenerationMethods', [])]
            return models
    except:
        pass
    return []

def analyze_image_direct(api_key, model_name, image_bytes, prompt):
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

# --- 4. STYLING ---
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

# --- 5. DASHBOARD (Direct Access) ---
def dashboard():
    with st.sidebar:
        st.title("👤 Farmer") # Default Name
        
        st.subheader("🤖 AI Brain")
        available_models = get_working_models(GOOGLE_API_KEY)
        
        if available_models:
            default_idx = 0
            for i, m in enumerate(available_models):
                if 'flash' in m and '1.5' in m: default_idx = i
            selected_model = st.selectbox("Select Model", available_models, index=default_idx)
            st.success("✅ Online")
        else:
            selected_model = "gemini-1.5-flash"
            st.warning("⚠️ Using Default Model")

        st.markdown("---")
        city = st.text_input("Village", "Kolhapur")
        w_text, w_cond = get_weather_auto(city)
        st.success(f"📍 {w_text}")
        st.markdown("---")
        lang = st.selectbox("Language", ["Marathi", "Hindi", "English"])
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        
        # Removed Logout Button

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
                    
                    # --- PROMPT: 120-300 Words ---
                    prompt = f"""
                    You are an expert Indian Agronomist. 
                    CONTEXT: Location: {city}, Weather: {w_text}.
                    
                    Analyze this crop image and provide a report in {lang}.
                    **Strict Requirement:** The response must be between 120 and 300 words.
                    
                    Cover these points:
                    1. **Disease Identification:** Name the disease/pest.
                    2. **Symptoms:** Brief description.
                    3. **Natural Remedy:** Organic/home solutions.
                    4. **Weather Advice:** Specific advice based on {w_cond}.
                    """
                    
                    res = analyze_image_direct(GOOGLE_API_KEY, selected_model, img_bytes, prompt)
                    
                    if "Error" in res:
                        st.error(f"❌ {res}")
                    else:
                        st.markdown(f'<div class="glass-card"><h3>✅ Report</h3><p>{res}</p></div>', unsafe_allow_html=True)
                        try:
                            clean_text = res.replace('*', '').replace('#', '')
                            tts = gTTS(clean_text, lang=lang_map[lang])
                            audio_bytes = io.BytesIO()
                            tts.write_to_fp(audio_bytes)
                            audio_bytes.seek(0)
                            st.audio(audio_bytes, format="audio/mp3")
                        except Exception:
                            st.info("ℹ️ Audio output is optimized for Localhost.")
                    
                except Exception as e:
                    st.error(f"System Error: {e}")

# --- RUN DIRECTLY ---
if __name__ == "__main__":
    dashboard()
