
import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# ⚠️ REPLACE WITH YOUR NEW KEY
GOOGLE_API_KEY = "AIzaSyBBj9OEPx9D6pfN8FvcYNy1bvsmjW3TFlA"

# Configure the API
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# --- 2. DYNAMIC MODEL FINDER (The Fix) ---
# This function gets the REAL list of models your key allows
def get_available_models():
    try:
        model_list = []
        for m in genai.list_models():
            # We only want models that can generate content
            if 'generateContent' in m.supported_generation_methods:
                model_list.append(m.name)
        return model_list
    except Exception as e:
        return []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🔧 Settings")
    
    # A. Model Selector (Fixes the 404 Error)
    st.subheader("Select AI Brain")
    available_models = get_available_models()
    
    if not available_models:
        st.error("❌ No models found! Your API Key might be invalid or new. Please generate a new key.")
        selected_model_name = "models/gemini-1.5-flash" # Fallback
    else:
        # We try to auto-select the best one, but you can change it
        default_index = 0
        for i, m in enumerate(available_models):
            if "flash" in m:
                default_index = i
                break
        selected_model_name = st.selectbox("Choose Model", available_models, index=default_index)
        st.success(f"Connected to: {selected_model_name}")

    # B. Language & Weather
    st.divider()
    lang_map = {"Marathi (मराठी)": "mr", "Hindi (हिंदी)": "hi", "English": "en"}
    selected_lang = st.selectbox("Language", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]
    
    weather = st.radio("Weather Condition", ["Sunny", "Rainy", "Cloudy"])

# --- 4. MAIN APP ---
st.title("GreenMitra 🌍")
st.caption("Theme: Sustainability & Smart Environments")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Scan For Healthy & Green Farming")
    enable_camera = st.checkbox("Use Camera")
    image_file = st.camera_input("Take Photo") if enable_camera else st.file_uploader("Upload Image")
    
    if image_file:
        img = Image.open(image_file)
        st.image(img, caption="Crop", use_container_width=True)

with col2:
    st.subheader("2. Eco Diagnosis")
    
    if image_file and st.button("Analyze (पीक तपासा)", key="analyze_btn"):
        with st.spinner("Analyzing..."):
            try:
                # Connect to the SPECIFIC model you selected
                model = genai.GenerativeModel(selected_model_name)
                
                prompt = f"""
                You are an Indian Agriculture Expert.
                Context: Weather is {weather}.
                1. Identify the disease.
                2. Suggest a NATURAL remedy.
                3. If weather is 'Rainy', warn NOT to spray.
                4. Reply in {selected_lang}.
                """
                
                response = model.generate_content([prompt, img])
                result = response.text
                
                # Show Text
                st.info(result)
                
                # Audio
                tts = gTTS(result, lang=lang_code)
                tts.save("cure.mp3")
                st.audio("cure.mp3")
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.warning("Tip: Try selecting a different model in the Sidebar!")
