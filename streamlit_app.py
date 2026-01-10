import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra | Smart Farming",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ⚠️ PASTE YOUR KEYS HERE
GOOGLE_API_KEY = "PASTE_YOUR_NEW_GOOGLE_KEY_HERE"
WEATHER_API_KEY = "PASTE_YOUR_OPENWEATHER_KEY_HERE"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- 2. CUSTOM CSS (MAKES IT ATTRACTIVE) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f0f8f0;
    }
    /* Title Styling */
    h1 {
        color: #2e7d32;
        font-family: 'Helvetica', sans-serif;
    }
    /* Button Styling */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-size: 18px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: #ffffff;
    }
    /* Result Card */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2e7d32;
    }
    /* Hide Streamlit Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_weather(city):
    """Fetches live weather context"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            desc = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"{desc.title()}, {temp}°C"
        return None
    except:
        return None

def get_model():
    """Finds the best available model"""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return genai.GenerativeModel(m.name)
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return genai.GenerativeModel('gemini-pro-vision')

# --- 4. SIDEBAR (SETTINGS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1598/1598196.png", width=80)
    st.title("⚙️ Settings")
    
    st.subheader("📍 Location")
    city = st.text_input("Village Name", "Kolhapur")
    
    # Live Weather Check
    weather_context = get_weather(city)
    if weather_context:
        st.success(f"🌤️ Live: {weather_context}")
    else:
        st.warning("⚠️ Weather API unavailable. Using Manual.")
        weather_context = st.selectbox("Manual Weather", ["Sunny", "Rainy", "Cloudy"])

    st.divider()
    
    st.subheader("🗣️ Language")
    lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
    selected_lang = st.selectbox("Select Language", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]

# --- 5. MAIN INTERFACE ---
# Hero Section
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.write("") # Spacer
    st.markdown("## 🌿")
with col_title:
    st.title("GreenMitra")
    st.caption("AI-Powered Sustainable Farming Assistant")

st.markdown("---")

# Input Section (Tabs for Better UX)
tab1, tab2 = st.tabs(["📸 Camera (कॅमेरा)", "📂 Upload File (फोटो टाका)"])

image_file = None

with tab1:
    st.info("Ensure the crop leaf is clearly visible.")
    cam_img = st.camera_input("Tap to Snap")
    if cam_img:
        image_file = cam_img

with tab2:
    st.info("Drag and drop your image file below.")
    up_img = st.file_uploader("Browse Files", type=['jpg', 'jpeg', 'png', 'webp'])
    if up_img:
        image_file = up_img

# --- 6. DIAGNOSIS LOGIC ---
if image_file:
    # Show Image
    st.markdown("### Your Scan:")
    img = Image.open(image_file)
    st.image(img, use_container_width=True, caption="Uploaded Crop")
    
    # Action Button
    if st.button("🔍 Analyze Crop Now (पीक तपासा)", key="analyze"):
        with st.spinner("🌱 AI Doctor is analyzing leaf & weather..."):
            try:
                model = get_model()
                
                # Smart Prompt
                prompt = f"""
                Act as an expert Indian Agronomist.
                
                CONTEXT:
                - Farmer Location: {city}
                - Live Weather: {weather_context}
                
                TASK:
                1. **Identify the Disease** visible in the photo.
                2. **Suggest a Natural/Organic Remedy** (No chemicals).
                3. **Weather Warning:** If weather is 'Rainy' or 'Rain', strictly warn: "Do not spray today due to rain."
                4. Provide the response in **{selected_lang}** language.
                5. Keep the tone helpful and easy to understand for a farmer.
                """
                
                response = model.generate_content([prompt, img])
                result = response.text
                
                # Show Result in a nice Card
                st.markdown(f"""
                <div class="result-card">
                    <h3>📢 Diagnosis Report</h3>
                    <p>{result}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Audio Player
                tts = gTTS(result, lang=lang_code)
                tts.save("advice.mp3")
                st.audio("advice.mp3")
                
            except Exception as e:
                st.error(f"Analysis Failed: {e}")
                st.info("Check your API Keys in Settings.")

# --- 7. FOOTER ---
st.markdown("---")
st.markdown("<center>Made with ❤️ for Farmers | Buildathon 2026</center>", unsafe_allow_html=True)
