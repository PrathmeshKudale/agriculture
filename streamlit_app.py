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

# ⚠️ PASTE KEYS HERE ⚠️
GOOGLE_API_KEY = "AIzaSyBOGJUsEF4aBtkgvyZ-Lhb-9Z87B6z9ziY"
WEATHER_API_KEY = "AIzaSyBOGJUsEF4aBtkgvyZ-Lhb-9Z87B6z9ziY"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    pass

# --- 2. CSS STYLING (FIXED INVISIBLE TEXT) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #f0f8f0; }
    
    /* Headers */
    h1, h2, h3 { color: #2e7d32 !important; }
    
    /* Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-size: 20px;
        width: 100%;
        border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    
    /* Result Box - THE FIX IS HERE */
    .result-box {
        background-color: #ffffff; /* White Background */
        color: #000000 !important; /* Force BLACK Text */
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #2e7d32;
    }
    /* Force text inside result box to be black */
    .result-box p, .result-box h3 {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{data['weather'][0]['main']}, {data['main']['temp']}°C"
        return None
    except:
        return None

def get_available_models():
    """Ask Google which models are allowed for this key"""
    try:
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception as e:
        return []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/188/188333.png", width=70)
    st.title("⚙️ Settings")
    
    # 1. MODEL SELECTOR
    st.subheader("🤖 Select AI Brain")
    my_models = get_available_models()
    if my_models:
        # Try to find 'flash' model automatically
        default_idx = 0
        for i, m in enumerate(my_models):
            if 'flash' in m:
                default_idx = i
                break
        selected_model_name = st.selectbox("Choose Model", my_models, index=default_idx)
        st.success(f"Connected: {selected_model_name}")
    else:
        st.error("❌ Key Error: Check your Google API Key.")
        selected_model_name = "models/gemini-1.5-flash"

    st.divider()

    # 2. WEATHER
    city = st.text_input("Village / City", "Pune")
    weather_context = get_weather(city)
    
    if weather_context:
        st.success(f"📍 Weather: {weather_context}")
    else:
        st.warning("⚠️ Manual Weather Mode")
        weather_context = st.radio("Weather", ["Sunny", "Rainy", "Cloudy"])
        
    st.divider()
    lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
    selected_lang = st.selectbox("Language", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]

# --- 5. MAIN APP ---
col1, col2 = st.columns([1, 5])
with col1:
    st.write("## 🌿") 
with col2:
    st.title("GreenMitra: AI Plant Doctor")

# --- 6. UPLOAD SECTION ---
input_method = st.radio("Input Method:", ["📂 Upload File", "📸 Camera"], horizontal=True)

image_file = None
if input_method == "📸 Camera":
    image_file = st.camera_input("Take Photo")
else:
    image_file = st.file_uploader("Drop image here", type=['jpg', 'jpeg', 'png', 'webp'])

# --- 7. ANALYSIS ---
if image_file:
    st.divider()
    col_img, col_result = st.columns([1, 1])
    
    with col_img:
        st.subheader("Your Scan")
        img = Image.open(image_file)
        st.image(img, use_container_width=True, caption="Uploaded Crop")

    with col_result:
        st.subheader("AI Diagnosis")
        
        if st.button("🔍 Analyze Crop (पीक तपासा)"):
            with st.spinner("🌱 AI is analyzing..."):
                try:
                    # Use the model selected in sidebar
                    model = genai.GenerativeModel(selected_model_name)
                    
                    prompt = f"""
                    Act as an Indian Agronomist.
                    CONTEXT: Location: {city}, Weather: {weather_context}.
                    TASK:
                    1. Identify Disease.
                    2. Suggest NATURAL Remedy.
                    3. If 'Rainy', warn NOT to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    response = model.generate_content([prompt, img])
                    result = response.text
                    
                    # Result Card with Black Text
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>✅ Diagnosis Report</h3>
                        <p>{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Audio
                    tts = gTTS(result, lang=lang_code)
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
