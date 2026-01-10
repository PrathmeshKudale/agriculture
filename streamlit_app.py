import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import requests

# --- 1. CONFIGURATION ---
# ⚠️ Google Key (Keep this secret!)
GOOGLE_API_KEY = "AIzaSyCgjvuZXfh7NwVN2-gIvs17x8Bdlh0SdX4"

# ⚠️ PASTE YOUR OPENWEATHER KEY HERE
# Get it from openweathermap.org (It takes 2 mins)
WEATHER_API_KEY = "4a3fc3c484c492d967514dc42f86cb40" 

# Configure Google AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- 2. HELPER FUNCTIONS ---

# A. Dynamic Model Finder (Fixes 404 Error)
def get_available_models():
    try:
        model_list = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        return model_list
    except:
        return []

# B. Weather Fetcher (New Feature!)
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            main = data['weather'][0]['main']
            desc = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"{main} ({desc}), {temp}°C"
        else:
            return None
    except:
        return None

# --- 3. SIDEBAR SETTINGS ---
with st.sidebar:
    st.title("🔧 GreenMitra Settings")
    
    # --- MODEL SELECTOR ---
    st.subheader("1. AI Brain")
    available_models = get_available_models()
    if available_models:
        # Auto-select Flash if available
        index = 0
        for i, m in enumerate(available_models):
            if "flash" in m: index = i
        selected_model_name = st.selectbox("Model", available_models, index=index)
    else:
        st.error("Invalid Google API Key")
        selected_model_name = "models/gemini-1.5-flash"

    st.divider()

    # --- WEATHER SELECTOR (SMART) ---
    st.subheader("2. Location & Weather")
    city = st.text_input("Enter Village/City Name", "Kolhapur")
    
    # Try to fetch live weather
    live_weather = get_weather(city)
    
    if live_weather:
        st.success(f"✅ Live: {live_weather}")
        weather_context = live_weather
    else:
        # Fallback to Manual if API fails or City wrong
        if WEATHER_API_KEY == "PASTE_YOUR_OPENWEATHER_KEY_HERE":
            st.warning("⚠️ Weather Key Missing. Using Manual Mode.")
        else:
            st.warning("⚠️ City not found. Selecting manually.")
        weather_context = st.radio("Manual Weather", ["Sunny", "Rainy", "Cloudy"])

    st.divider()

    # --- LANGUAGE ---
    st.subheader("3. Language")
    lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
    selected_lang = st.selectbox("Select", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]

# --- 4. MAIN APP ---
st.title("GreenMitra 🌍")
st.caption(f"📍 Context: {city} | 🌦️ Weather: {weather_context}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Scan Crop")
    enable_camera = st.checkbox("Use Camera")
    image_file = st.camera_input("Take Photo") if enable_camera else st.file_uploader("Upload Image")
    
    if image_file:
        img = Image.open(image_file)
        st.image(img, caption="Crop Ready", use_container_width=True)

with col2:
    st.subheader("Eco Diagnosis")
    
    if image_file and st.button("Analyze (पीक तपासा)", key="analyze"):
        with st.spinner("Analyzing with Live Weather Context..."):
            try:
                model = genai.GenerativeModel(selected_model_name)
                
                # The Smart Prompt
                prompt = f"""
                Act as an Indian Agriculture Expert.
                
                CRITICAL CONTEXT:
                - Location: {city}
                - Live Weather: {weather_context}
                
                TASKS:
                1. Identify the disease in the image.
                2. Suggest a NATURAL remedy (Desi Upay).
                3. WEATHER LOGIC: If weather is Rain/Rainy, warn the farmer: "Do not spray now."
                4. Reply in {selected_lang}.
                """
                
                response = model.generate_content([prompt, img])
                result = response.text
                
                st.info(result)
                
                tts = gTTS(result, lang=lang_code)
                tts.save("cure.mp3")
                st.audio("cure.mp3")
                
            except Exception as e:
                st.error(f"Error: {e}")
