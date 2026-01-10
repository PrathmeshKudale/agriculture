import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GreenMitra", page_icon="🌿", layout="wide")

# ⚠️ REPLACE WITH YOUR *NEW* KEYS ⚠️
GOOGLE_API_KEY = "AIzaSyBbEXluYKFFHlkLk26SSGwMy-AIdYEcPxU"
WEATHER_API_KEY = "03daa4ea2ddc9ec25536fe66d8631cb5"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    pass

# --- 2. CSS STYLING ---
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
    }
    .stButton>button {
        background-color: #2e7d32; color: white; border-radius: 25px;
        height: 50px; font-size: 18px; width: 100%; border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    h1, h2, h3 { color: #1b5e20 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return f"{data['weather'][0]['main']}, {data['main']['temp']}°C", data['weather'][0]['main']
    except:
        pass
    return "Unavailable", "Clear"

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = ""

# --- 5. LOGIN PAGE ---
def login():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="glass-card" style="text-align:center;"><h1>🌿 GreenMitra</h1><p>Smart Assistant</p></div>', unsafe_allow_html=True)
        st.write("")
        email = st.text_input("📧 Email")
        # ALLOW ANY PASSWORD (FOR DEMO)
        password = st.text_input("🔑 PIN (Any Number)", type="password")
        
        if st.button("Login"):
            if email and password.isdigit():
                st.session_state['logged_in'] = True
                st.session_state['user'] = email.split('@')[0]
                st.rerun()
            else:
                st.error("Enter Email and Numeric PIN")

# --- 6. DASHBOARD ---
def dashboard():
    # SIDEBAR
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        
        st.subheader("🤖 AI Brain")
        # USE THE SAFEST MODEL NAME
        model_name = "gemini-1.5-flash" 
        st.info(f"Active: {model_name}")

        st.markdown("---")
        city = st.text_input("Village", "Kolhapur")
        w_text, w_cond = get_weather(city)
        st.success(f"📍 {w_text}")
        
        st.markdown("---")
        lang = st.selectbox("Language", ["Marathi", "Hindi", "English"])
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # MAIN
    c1, c2 = st.columns([1, 5])
    with c1: st.write("# 🌿")
    with c2: st.title("GreenMitra Dashboard")
    
    # INPUT
    mode = st.radio("Input:", ["📂 Upload", "📸 Camera"], horizontal=True)
    file = None
    if mode == "📸 Camera": file = st.camera_input("Scan")
    else: file = st.file_uploader("Upload", type=['jpg','png','jpeg'])
        
    if file:
        st.image(file, width=300)
        
        if st.button("🔍 Analyze (पीक तपासा)"):
            with st.spinner("Diagnosing..."):
                try:
                    # 1. SETUP MODEL
                    model = genai.GenerativeModel(model_name)
                    
                    # 2. IMAGE SETUP
                    img = Image.open(file)
                    
                    # 3. PROMPT
                    prompt = f"""
                    Expert Agronomist. Location: {city}, Weather: {w_text}.
                    1. Disease Name. 2. Natural Remedy. 
                    3. If {w_cond} is Rainy, warn farmer.
                    4. Language: {lang}.
                    """
                    
                    # 4. RUN
                    response = model.generate_content([prompt, img])
                    res = response.text
                    
                    # 5. OUTPUT
                    st.markdown(f'<div class="glass-card" style="color:black;"><h3>✅ Report</h3><p>{res}</p></div>', unsafe_allow_html=True)
                    
                    # 6. AUDIO
                    tts = gTTS(res, lang=lang_map[lang])
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    # ERROR DIAGNOSIS
                    err = str(e)
                    if "403" in err:
                        st.error("❌ KEY BLOCKED: Your Google Key is invalid. Get a new one.")
                    elif "404" in err:
                        st.error("❌ MODEL ERROR: Run 'pip install --upgrade google-generativeai' in terminal.")
                    else:
                        st.error(f"Error: {err}")

# --- RUN ---
if st.session_state['logged_in']: dashboard()
else: login()
