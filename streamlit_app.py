import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests
import re  # For email validation

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra | Login",
    page_icon="🌿",
    layout="wide"
)

# ⚠️ PASTE KEYS HERE ⚠️
GOOGLE_API_KEY = "AIzaSyBOGJUsEF4aBtkgvyZ-Lhb-9Z87B6z9ziY"
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    pass

# --- 2. ADVANCED STYLING (The Attractive Part) ---
st.markdown("""
    <style>
    /* 1. Background Image for the Whole App */
    .stApp {
        background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                    url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=3000&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* 2. Login Card Styling */
    .login-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-top: 6px solid #2e7d32;
        margin-top: 50px;
    }
    
    /* 3. Text Styling */
    h1 { color: #1b5e20 !important; font-weight: 800; }
    p { font-size: 16px; color: #555; }
    
    /* 4. Input Fields */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    
    /* 5. Green Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 30px; /* Rounded pill shape */
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        width: 100%;
        border: none;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
    }
    .stButton>button:hover { 
        background-color: #1b5e20; 
        transform: translateY(-2px);
    }
    
    /* 6. Result Box */
    .result-box {
        background-color: white;
        color: black !important;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 8px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- 4. FUNCTIONS ---
def is_valid_email(email):
    # Simple Regex for Email Validation
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

def get_weather_auto(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{data['weather'][0]['main']}, {data['main']['temp']}°C", data['weather'][0]['main']
        return "Unavailable", "Clear"
    except:
        return "Unavailable", "Clear"

def get_model():
    # Model Switcher
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro-vision')

# --- 5. LOGIN PAGE (THE FIX) ---
def login_screen():
    # Layout: 3 Columns to center the box
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        # The Beautiful Header
        st.markdown("""
        <div class="login-card">
            <h1 style="margin-bottom:0px;">🌿 GreenMitra</h1>
            <p style="margin-top:5px;">AI-Powered Sustainable Farming</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        # Inputs
        email_input = st.text_input("📧 Email Address", placeholder="e.g. farmer@gmail.com")
        password_input = st.text_input("🔑 Password", type="password", placeholder="Enter PIN")
        
        st.write("") # Spacer
        
        if st.button("Log In Securely"):
            # 1. Check if Email is Empty
            if not email_input or not password_input:
                st.error("⚠️ Please fill in all fields.")
            
            # 2. Check Valid Email Format
            elif not is_valid_email(email_input):
                st.error("❌ Invalid Email Format! (Must have @ and .com)")
                
            # 3. Check Password (DEMO PASSWORD IS '1234')
            elif password_input != "1234":
                st.error("❌ Wrong Password! Hint: 1234")
                
            # 4. Success!
            else:
                st.success("✅ Login Successful!")
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = email_input.split('@')[0]
                st.rerun()

# --- 6. MAIN APP (AFTER LOGIN) ---
def main_dashboard():
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {st.session_state['user_name']}")
        st.markdown("---")
        
        # Auto Weather
        st.subheader("📍 Location")
        city = st.text_input("Village Name", "Pune")
        weather_text, weather_cond = get_weather_auto(city)
        st.info(f"🌤️ Live Weather:\n{weather_text}")
        
        st.markdown("---")
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        selected_lang = st.selectbox("Language", list(lang_map.keys()))
        lang_code = lang_map[selected_lang]
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # Main Area
    c1, c2 = st.columns([1, 5])
    with c1: st.write("# 🌿")
    with c2: st.title("GreenMitra Dashboard")
    
    st.write("---")
    
    # Input
    input_type = st.radio("Select Input:", ["📂 Upload Image", "📸 Live Camera"], horizontal=True)
    img_file = None
    
    if input_type == "📸 Live Camera":
        img_file = st.camera_input("Scan")
    else:
        img_file = st.file_uploader("Upload Crop Photo", type=['jpg','png','webp'])
        
    if img_file:
        st.image(img_file, caption="Scan Preview", width=300)
        
        if st.button("🔍 Analyze Crop (पीक तपासा)"):
            with st.spinner("🌱 AI is diagnosing..."):
                try:
                    model = get_model()
                    img = Image.open(img_file)
                    
                    prompt = f"""
                    Role: Expert Agronomist.
                    Context: {city}, Weather: {weather_text}.
                    Task: 
                    1. Disease Name. 
                    2. Natural Remedy (No Chemicals).
                    3. If {weather_cond} is Rainy, warn about spraying.
                    4. Lang: {selected_lang}.
                    """
                    
                    response = model.generate_content([prompt, img])
                    res_text = response.text
                    
                    # Result Card
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>✅ Diagnosis Report</h3>
                        <p style="color:black; font-size:18px;">{res_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tts = gTTS(res_text, lang=lang_code)
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 7. RUNNER ---
if st.session_state['logged_in']:
    main_dashboard()
else:
    login_screen()
