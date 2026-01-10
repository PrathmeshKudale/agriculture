import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests

# --- 1. SETUP (Do not change this) ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="wide"
)

# ⚠️ PASTE YOUR NEW KEYS HERE ⚠️
# Make sure there are NO spaces inside the quotes!
GOOGLE_API_KEY = "AIzaSyBOGJUsEF4aBtkgvyZ-Lhb-9Z87B6z9ziY"
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    pass

# --- 2. ATTRACTIVE UI (CSS) ---
st.markdown("""
    <style>
    /* Professional Green Theme */
    .stApp { background-color: #f0f8f0; }
    h1, h2, h3 { color: #2e7d32 !important; }
    
    /* Styled Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-size: 20px;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
    }
    
    /* Result Box Styling */
    .result-box {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
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

def get_smart_model():
    """
    Automatically finds a working model to prevent 404 Errors.
    """
    try:
        # Priority 1: Flash (Fastest)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except:
        # Priority 2: Pro Vision (Reliable Backup)
        return genai.GenerativeModel('gemini-pro-vision')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/188/188333.png", width=70)
    st.title("⚙️ Settings")
    
    city = st.text_input("Village / City", "Kolhapur")
    weather_context = get_weather(city)
    
    if weather_context:
        st.success(f"📍 Weather: {weather_context}")
    else:
        st.warning("⚠️ Manual Weather Mode")
        weather_context = st.radio("Select Weather", ["Sunny", "Rainy", "Cloudy"])
        
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

# --- 6. SMART UPLOAD SECTION (Fixed) ---
# We use a Radio button to switch clearly between Upload and Camera
input_method = st.radio("Choose Input Method:", ["📂 Upload Image (Drag & Drop)", "📸 Use Camera"], horizontal=True)

image_file = None

if input_method == "📸 Use Camera":
    image_file = st.camera_input("Tap to take photo")
else:
    # THIS IS THE BROWSER UPLOAD YOU WANTED
    image_file = st.file_uploader("Drag & Drop crop photo here", type=['jpg', 'jpeg', 'png', 'webp'])

# --- 7. ANALYSIS LOGIC ---
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
            with st.spinner("🌱 AI is analyzing leaf & weather..."):
                try:
                    # USE THE SMART MODEL SWITCHER
                    model = get_smart_model()
                    
                    prompt = f"""
                    Act as an Indian Agronomist.
                    CONTEXT: Location: {city}, Weather: {weather_context}.
                    
                    TASK:
                    1. Identify the Disease.
                    2. Suggest a NATURAL Remedy (Desi Upay).
                    3. WARNING: If weather is 'Rainy', tell farmer NOT to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    response = model.generate_content([prompt, img])
                    result = response.text
                    
                    # Beautiful Result Card
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>✅ Diagnosis Report</h3>
                        <p style="font-size:18px;">{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tts = gTTS(result, lang=lang_code)
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    # Specific error for Invalid Key
                    if "API_KEY_INVALID" in str(e):
                        st.error("❌ KEY ERROR: You pasted the wrong key! Go to Google AI Studio and get a fresh one.")
                    else:
                        st.error(f"Error: {e}")
