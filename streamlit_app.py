import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Use secrets for Cloud, fallback to string for Local
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyBBj9OEPx9D6pfN8FvcYNy1bvsmjW3TFlA"

genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. HELPER FUNCTIONS ---
def get_model():
    # We use 'gemini-1.5-flash' for speed, fallback to 'pro-vision'
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except:
        return genai.GenerativeModel('gemini-pro-vision')

def process_image(image_file):
    """
    Fixes the 'File Path' issue by processing in Memory.
    Also resizes big mobile photos to prevent timeout.
    """
    try:
        # 1. Open directly from the uploaded buffer (No file path needed)
        img = Image.open(image_file)
        
        # 2. Convert to RGB (Fixes issues with PNG transparency on phones)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # 3. Resize if too big (Speeds up the App significantly)
        # Mobile cams are 4000px+, we resize to max 1024px
        img.thumbnail((1024, 1024)) 
        return img
    except Exception as e:
        st.error(f"Image Error: {e}")
        return None

# --- 3. APP UI ---
st.set_page_config(page_title="Agri-Mitra", page_icon="🌾")

st.title("🌾 Agri-Mitra")
st.caption("Works on Mobile & Desktop")

# Sidebar
with st.sidebar:
    st.header("Settings")
    lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
    selected_lang = st.selectbox("Language", list(lang_map.keys()))
    lang_code = lang_map[selected_lang]
    weather = st.radio("Weather", ["Sunny", "Rainy", "Cloudy"])

# --- 4. MAIN UPLOAD SECTION ---
st.info("📸 Upload a photo of the crop / पिकाचा फोटो टाका")

# We allow more types to prevent mobile errors
enable_camera = st.checkbox("Use Camera")
if enable_camera:
    file_upload = st.camera_input("Take Photo")
else:
    file_upload = st.file_uploader("Choose Image", type=['jpg', 'jpeg', 'png', 'webp'])

# --- 5. LOGIC ---
if file_upload:
    # PROCESS IMAGE (The Fix)
    img = process_image(file_upload)
    
    if img:
        st.image(img, caption="Ready to Scan", use_container_width=True)
        
        if st.button("Analyze (पीक तपासा)", key="go_btn"):
            with st.spinner("Analyzing..."):
                try:
                    model = get_model()
                    
                    prompt = f"""
                    Act as an Indian Agriculture Expert.
                    Context: Weather is {weather}.
                    1. Identify the crop disease.
                    2. Suggest a Natural Remedy.
                    3. If weather is 'Rainy', warn not to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    # Pass the processed PIL image object directly
                    response = model.generate_content([prompt, img])
                    
                    st.success("Report Generated:")
                    st.write(response.text)
                    
                    # Audio
                    tts = gTTS(response.text, lang=lang_code)
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                    
                except Exception as e:
                    st.error(f"Connection Error: {e}")
                    st.warning("If the image is huge, try a smaller one.")
