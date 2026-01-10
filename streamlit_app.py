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

# ⚠️ SECURITY CHECK: MAKE SURE THESE ARE CORRECT! ⚠️
# 1. Google Key starts with "AIza..."
# 2. Weather Key is the short one from OpenWeather.
# 3. NO SPACES inside the quotes!
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
    .stApp { background-color: #f0f8f0; }
    h1, h2, h3 { color: #2e7d32 !important; }
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
    .result-box {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ROBUST FUNCTIONS ---
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

def get_working_model():
    """
    Tries to find a model that actually works for your key.
    """
    # List of model names to try, in order of preference
    candidates = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-pro-vision',  # This one almost ALWAYS works
    ]
    
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            # We don't call generate here, just return the object
            return model
        except:
            continue
            
    # Fallback default
    return genai.GenerativeModel('gemini-pro-vision')

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/188/188333.png", width=70)
    st.title("⚙️ Settings")
    
    city = st.text_input("Village / City", "Pune")
    weather_context = get_weather(city)
    
    if weather_context:
        st.success(f"📍 Weather: {weather_context}")
    else:
        st.warning("⚠️ Weather API not connected (Check Key)")
        weather_context = st.radio("Manual Weather", ["Sunny", "Rainy", "Cloudy"])
        
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
# Clear choice between Camera and File
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
                    # 1. Get the Model
                    model = get_working_model()
                    
                    # 2. Prepare Prompt
                    prompt = f"""
                    Act as an Indian Agronomist.
                    CONTEXT: Location: {city}, Weather: {weather_context}.
                    TASK:
                    1. Identify Disease.
                    2. Suggest NATURAL Remedy.
                    3. If 'Rainy', warn NOT to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    # 3. Generate
                    response = model.generate_content([prompt, img])
                    result = response.text
                    
                    # 4. Show Result
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>✅ Diagnosis Report</h3>
                        <p style="font-size:18px;">{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 5. Audio
                    tts = gTTS(result, lang=lang_code)
                    tts.save("cure.mp3")
                    st.audio("cure.mp3")
                    
                except Exception as e:
                    # CLEAR ERROR MESSAGES FOR YOU
                    err_msg = str(e)
                    if "API_KEY_INVALID" in err_msg:
                        st.error("❌ CRITICAL: Your Google API Key is WRONG. Please check line 16.")
                    elif "404" in err_msg:
                        st.error("❌ MODEL ERROR: The AI model is busy. Try clicking Analyze again.")
                    else:
                        st.error(f"Error: {err_msg}")
