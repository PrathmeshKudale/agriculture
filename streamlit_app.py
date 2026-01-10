import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Get Key from Secrets (Cloud) or use fallback (Local)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyBBj9OEPx9D6pfN8FvcYNy1bvsmjW3TFlA"

genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. SMART GENERATOR FUNCTION ---
# This is the FIX for the 404 Error
def get_ai_response(prompt, image):
    try:
        # Attempt 1: Try the fast 'Flash' model
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content([prompt, image])
    except Exception:
        # Attempt 2: If Flash fails (404), switch to 'Pro-Vision' (Stable)
        # This handles the Cloud error automatically
        model = genai.GenerativeModel('gemini-pro-vision')
        return model.generate_content([prompt, image])

def process_image(image_file):
    """
    Fixes the 'File Path' issue by keeping image in Memory (RAM).
    """
    try:
        img = Image.open(image_file)
        # Fix orientation/color for mobile uploads
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        return None

# --- 3. APP INTERFACE ---
st.set_page_config(page_title="Agri-Mitra", page_icon="🌾")

st.title("🌾 Agri-Mitra")
st.caption("Works on Mobile & Desktop")

# Sidebar Settings
with st.sidebar:
    st.header("Settings")
    lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
    selected_lang = st.selectbox("Language", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]
    weather = st.radio("Weather", ["Sunny", "Rainy", "Cloudy"])

# --- 4. MAIN UPLOAD ---
st.info("📸 Upload photo / फोटो टाका")
enable_camera = st.checkbox("Use Camera")

if enable_camera:
    file_upload = st.camera_input("Take Photo")
else:
    file_upload = st.file_uploader("Choose Image", type=['jpg', 'jpeg', 'png', 'webp'])

# --- 5. MAIN LOGIC ---
if file_upload:
    img = process_image(file_upload)
    
    if img:
        st.image(img, caption="Crop Ready", use_container_width=True)
        
        if st.button("Analyze (पीक तपासा)", key="analyze_btn"):
            with st.spinner("Analyzing..."):
                try:
                    # Create the Prompt
                    prompt = f"""
                    Act as an Indian Agriculture Expert.
                    Context: Weather is {weather}.
                    1. Identify the crop disease.
                    2. Suggest a Natural Remedy.
                    3. If weather is 'Rainy', warn not to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    # CALL THE SMART FUNCTION
                    response = get_ai_response(prompt, img)
                    
                    st.success("Report Generated:")
                    st.write(response.text)
                    
                    # Audio
                    tts = gTTS(response.text, lang=lang_code)
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.warning("Try taking the photo again.")
