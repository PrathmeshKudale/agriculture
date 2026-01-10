import streamlit as st
from PIL import Image
from gtts import gTTS
import google.generativeai as genai
import io

# --- 1. CONFIGURATION ---
# Try to get key from Cloud Secrets, else use the one you pasted
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyCgjvuZXfh7NwVN2-gIvs17x8Bdlh0SdX4"

genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. MOBILE IMAGE FIX ---
def load_image(image_file):
    """
    Reads image directly from memory (fixes 'File Path' error).
    Resizes huge mobile photos to prevent timeouts.
    """
    try:
        img = Image.open(image_file)
        
        # Convert to RGB (Fixes errors with some Android formats)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize image to max 800px (Crucial for mobile speed)
        img.thumbnail((800, 800))
        return img
    except Exception as e:
        st.error(f"Error reading image: {e}")
        return None

# --- 3. PAGE SETUP ---
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
st.info("📸 Upload a photo of the crop")

# Allow Camera AND File Upload
enable_camera = st.checkbox("Use Camera (Recommended for Mobile)")
file_upload = None

if enable_camera:
    file_upload = st.camera_input("Take Photo")
else:
    # Accept multiple mobile formats
    file_upload = st.file_uploader("Choose Image", type=['jpg', 'jpeg', 'png', 'webp'])

# --- 5. LOGIC ---
if file_upload:
    # Step 1: Process Image using our Fix Function
    img = load_image(file_upload)
    
    if img:
        st.image(img, caption="Ready to Scan", use_container_width=True)
        
        if st.button("Analyze (पीक तपासा)", key="analyze_btn"):
            with st.spinner("Analyzing..."):
                try:
                    # Smart Model Selection
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                    except:
                        model = genai.GenerativeModel('gemini-pro-vision')
                    
                    prompt = f"""
                    Act as an Indian Agriculture Expert.
                    Context: Weather is {weather}.
                    1. Identify the crop disease.
                    2. Suggest a Natural Remedy.
                    3. If weather is 'Rainy', warn not to spray.
                    4. Reply in {selected_lang}.
                    """
                    
                    response = model.generate_content([prompt, img])
                    
                    # Display Report
                    st.success("Report Generated:")
                    st.write(response.text)
                    
                    # Audio
                    tts = gTTS(response.text, lang=lang_code)
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                    
                except Exception as e:
                    st.error(f"Connection Error: {e}")
                    st.warning("Try taking a photo with lower resolution if it fails.")
