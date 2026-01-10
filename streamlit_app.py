import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests

# --- 1. SETUP ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# ⚠️ PASTE YOUR KEYS HERE ⚠️
# Make sure there are NO SPACES at the start or end!
GOOGLE_API_KEY = "AIzaSyArItSJJ8eMSUb7yZZPrVZuszjgZuYXWuM"
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40"

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
        background-size: cover;
        background-attachment: fixed;
    }
    .glass-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border-top: 6px solid #2e7d32;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 30px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    h1, h2, h3 { color: #1b5e20 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
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

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- 5. PAGE: LOGIN ---
def login_screen():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <h1>🌿 GreenMitra</h1>
            <p>Smart Sustainable Farming Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        email = st.text_input("📧 Email Address")
        password = st.text_input("🔑 Password (Hint: 1234)", type="password")
        
        if st.button("Login Securely"):
            if not email or not password:
                st.error("⚠️ Enter email and password")
            elif "@" not in email:
                st.error("❌ Invalid Email")
            elif password != "1234":
                st.error("❌ Wrong Password")
            else:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = email.split('@')[0]
                st.rerun()

# --- 6. PAGE: DASHBOARD ---
def main_dashboard():
    # SIDEBAR
    with st.sidebar:
        st.title(f"👤 {st.session_state['user_name']}")
        
        # 1. THE FIX: Hardcoded List (Always Works)
        st.subheader("🤖 AI Brain")
        
        # We force these options so the dropdown NEVER disappears
        model_options = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-pro",
            "gemini-pro-vision"
        ]
        
        selected_model = st.selectbox("Select Model", model_options, index=0)
        st.success(f"Active: {selected_model}")

        # 2. Location & Weather
        st.markdown("---")
        st.subheader("📍 Location")
        city = st.text_input("Village", "Kolhapur")
        w_text, w_cond = get_weather_auto(city)
        st.info(f"🌤️ Live Weather:\n{w_text}")
        
        # 3. Language
        st.markdown("---")
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        sel_lang = st.selectbox("Language", list(lang_map.keys()))
        lang_code = lang_map[sel_lang]
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    # MAIN CONTENT
    c1, c2 = st.columns([1, 5])
    with c1: st.write("# 🌿")
    with c2: st.title("GreenMitra Dashboard")
    
    # Input
    input_type = st.radio("Input:", ["📂 Upload Image", "📸 Camera"], horizontal=True)
    img_file = None
    
    if input_type == "📸 Camera":
        img_file = st.camera_input("Scan")
    else:
        img_file = st.file_uploader("Upload Crop", type=['jpg','png','webp'])
        
    if img_file:
        st.image(img_file, caption="Preview", width=300)
        
        if st.button("🔍 Analyze (पीक तपासा)"):
            with st.spinner("🌱 AI is diagnosing..."):
                try:
                    # Use the selected model
                    model = genai.GenerativeModel(selected_model)
                    img = Image.open(img_file)
                    
                    prompt = f"""
                    Role: Expert Agronomist.
                    Context: {city}, Weather: {w_text}.
                    Task: 
                    1. Disease Name. 
                    2. Natural Remedy.
                    3. If {w_cond} is Rainy, warn about spraying.
                    4. Lang: {sel_lang}.
                    """
                    
                    response = model.generate_content([prompt, img])
                    res_text = response.text
                    
                    # Result Card
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3>✅ Diagnosis Report</h3>
                        <p style="color:black; font-size:18px;">{res_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tts = gTTS(res_text, lang=lang_code)
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    # Clean Error Message
                    err = str(e)
                    if "404" in err:
                        st.error("⚠️ Model Error: Try selecting a different model from the Sidebar!")
                    elif "API_KEY" in err:
                        st.error("❌ API Key Error: Please check your Google Key.")
                    else:
                        st.error(f"Error: {e}")

# --- 7. APP RUNNER ---
if st.session_state['logged_in']:
    main_dashboard()
else:
    login_screen()
