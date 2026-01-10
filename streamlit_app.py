import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests
import datetime

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# ⚠️ PASTE KEYS HERE ⚠️
GOOGLE_API_KEY = "AIzaSyBOGJUsEF4aBtkgvyZ-Lhb-9Z87B6z9ziY"
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    pass

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #f0f8f0; }
    h1, h2, h3 { color: #2e7d32 !important; }
    
    /* Login Box Styles */
    .login-box {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #2e7d32;
    }
    
    /* Green Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-size: 18px;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    
    /* Result Card */
    .result-box {
        background-color: #ffffff;
        color: #000000 !important;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (LOGIN LOGIC) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- 4. FUNCTIONS ---
def get_weather_auto(city):
    """
    Fully Automatic Weather Detection.
    No manual override. If it fails, it defaults silently to clear/sunny logic.
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            desc = data['weather'][0]['main']
            temp = data['main']['temp']
            return f"{desc}, {temp}°C", desc # Return text AND condition
        return "Unavailable", "Clear"
    except:
        return "Unavailable", "Clear"

def get_smart_model():
    try:
        # Try finding the best model automatically
        for m in genai.list_models():
            if 'flash' in m.name: return genai.GenerativeModel(m.name)
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro-vision')

# --- 5. LOGIN PAGE ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-box">
            <h2>🌿 Welcome to GreenMitra</h2>
            <p>Smart Sustainable Farming Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address")
        password = st.text_input("🔑 Password", type="password")
        
        if st.button("Login Securely"):
            if email and password:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = email.split('@')[0]
                st.rerun() # Refresh to show main app
            else:
                st.error("Please enter email and password.")

# --- 6. MAIN DASHBOARD ---
def main_app():
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/188/188333.png", width=60)
        st.title(f"👨‍🌾 Hello, {st.session_state['user_name']}")
        
        st.subheader("📍 Location Auto-Detect")
        city = st.text_input("Current Village/City", "Kolhapur")
        
        # AUTOMATIC WEATHER (Hidden Logic)
        weather_text, weather_condition = get_weather_auto(city)
        
        # Display nicely
        st.info(f"🌤️ Detected Weather:\n{weather_text}")
        
        st.divider()
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        selected_lang = st.selectbox("Language", list(lang_map.keys()))
        lang_code = lang_map[selected_lang]
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # Main Area
    col1, col2 = st.columns([1, 5])
    with col1: st.write("## 🌿")
    with col2: st.title("GreenMitra Dashboard")
    
    # Input
    input_method = st.radio("Select Input:", ["📂 Upload Photo", "📸 Live Camera"], horizontal=True)
    
    image_file = None
    if input_method == "📸 Live Camera":
        image_file = st.camera_input("Scan Crop")
    else:
        image_file = st.file_uploader("Drop image here", type=['jpg', 'png', 'webp'])

    # Analysis
    if image_file:
        st.divider()
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.image(image_file, caption="Scanned Crop", use_container_width=True)
            
        with c2:
            st.subheader("AI Diagnosis")
            if st.button("🚀 Analyze Now (आता तपासा)"):
                with st.spinner("🔄 Analyzing location, weather & crop health..."):
                    try:
                        model = get_smart_model()
                        img = Image.open(image_file)
                        
                        prompt = f"""
                        Act as an Expert Agronomist.
                        User: {st.session_state['user_name']}
                        Location: {city}
                        Live Weather: {weather_text} (Condition: {weather_condition})
                        
                        TASK:
                        1. Identify the Crop Disease.
                        2. Suggest 100% NATURAL Remedy (No chemicals).
                        3. SMART WARNING: If weather is '{weather_condition}' (Rain/Rainy), explicitly warn: "STOP! Do not spray today due to rain."
                        4. Reply in {selected_lang}.
                        """
                        
                        response = model.generate_content([prompt, img])
                        result = response.text
                        
                        # Show Result
                        st.markdown(f"""
                        <div class="result-box">
                            <h3>✅ Report Ready</h3>
                            <p style="color:black;">{result}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Audio
                        tts = gTTS(result, lang=lang_code)
                        tts.save("cure.mp3")
                        st.audio("cure.mp3")
                        
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- 7. APP FLOW CONTROL ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
