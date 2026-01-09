import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai

# --- 1. CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyBLYJ--ocxx46M8LtQ0KplVYAdR5bTKD9I"
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. SMART FUNCTION TO FIND CORRECT MODEL ---
def get_vision_model():
    """Automatically finds a model that supports images"""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'vision' in m.name or 'flash' in m.name or 'pro' in m.name:
                    return m.name
    except:
        pass
    return 'gemini-1.5-flash' # Fallback

# Get the correct model name dynamically
valid_model_name = get_vision_model()
model = genai.GenerativeModel(valid_model_name)

# --- 3. APP HEADER ---
st.set_page_config(page_title="Agri-Mitra", page_icon="🌾")
st.title("🌾 Agri-Mitra: Real AI")
st.write(f"Connected to AI Brain: `{valid_model_name}`") # Debug info for you

# --- 4. INPUTS ---
lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
lang_name = st.selectbox("Language", list(lang_map.keys()))
lang_code = lang_map[lang_name]

enable_camera = st.checkbox("Use Camera")
image_file = st.camera_input("Photo") if enable_camera else st.file_uploader("Upload Image")

# --- 5. MAIN LOGIC ---
if image_file:
    img = Image.open(image_file)
    st.image(img, caption="Crop", use_column_width=True)
    
    if st.button("Get Cure"):
        with st.spinner("AI is thinking..."):
            try:
                prompt = f"""
                Identify the plant disease and give a Natural Remedy in {lang_name}.
                Keep it short.
                """
                response = model.generate_content([prompt, img])
                st.success(response.text)
                
                # Audio
                tts = gTTS(response.text, lang=lang_code)
                tts.save("audio.mp3")
                st.audio("audio.mp3")
                
            except Exception as e:
                st.error(f"Error: {e}")
