import streamlit as st
from PIL import Image
import requests 
import base64
import io
import datetime
from gtts import gTTS

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra Pro",
    page_icon="🌾",
    layout="wide"
)

# --- 2. SECURE KEYS ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("🚨 Critical Error: Google API Key is missing!")
    st.stop()

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- 3. DATABASE OF SCHEMES (Mock Data) ---
# In a real app, this would come from a Live Government API.
SCHEMES_DB = {
    "Maharashtra": [
        {"name": "MahaDBT Farmer Scheme", "benefit": "Subsidies for tractors and drip irrigation.", "link": "https://mahadbt.maharashtra.gov.in/"},
        {"name": "Gopinath Munde Shetkari Apghat Vima Yojana", "benefit": "Insurance cover of ₹2 Lakh for accidental death.", "link": "#"},
        {"name": "Magel Tyala Shettale", "benefit": "Financial aid for building farm ponds.", "link": "#"}
    ],
    "Karnataka": [
        {"name": "Raitha Siri", "benefit": "₹10,000 per hectare for millet growers.", "link": "#"},
        {"name": "Krushi Bhagya", "benefit": "Rainwater harvesting assistance.", "link": "#"}
    ],
    "Uttar Pradesh": [
        {"name": "UP Kisan Karj Mafi Yojana", "benefit": "Loan waiver for small farmers.", "link": "#"},
        {"name": "Solar Pump Yojana", "benefit": "75% subsidy on solar pumps.", "link": "#"}
    ],
    "All India": [
        {"name": "PM-KISAN", "benefit": "₹6,000 per year income support.", "link": "https://pmkisan.gov.in/"},
        {"name": "Pradhan Mantri Fasal Bima Yojana", "benefit": "Lowest premium crop insurance.", "link": "https://pmfby.gov.in/"},
        {"name": "Kisan Credit Card (KCC)", "benefit": "Low interest loans for farming needs.", "link": "#"}
    ]
}

# --- 4. SMART FUNCTIONS ---
def get_weather(city):
    if not WEATHER_API_KEY: return "Unavailable", "Clear", 25
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return f"{data['weather'][0]['main']}", data['weather'][0]['main'], data['main']['temp']
    except:
        pass
    return "Unavailable", "Clear", 25

def analyze_image_ai(api_key, image_bytes, prompt):
    # This is your existing AI function
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error analyzing image."
    except:
        return "Connection Error."

# --- 5. APP UI ---
def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🌾 GreenMitra")
        st.write("Jai Kisan! (Farmer's Best Friend)")
        
        # Profile Settings
        st.header("⚙️ Profile")
        name = st.text_input("Your Name", "Farmer")
        city = st.text_input("Village/City", "Pune")
        lang = st.selectbox("Language", ["Marathi", "Hindi", "English"])
        lang_map = {"Marathi": "mr", "Hindi": "hi", "English": "en"}
        
        # Weather Check (Runs always)
        w_text, w_cond, w_temp = get_weather(city)
        st.success(f"📍 {city}: {w_temp}°C, {w_text}")

    # --- MAIN TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Crop Doctor", "📅 Daily Planner", "📜 Govt Schemes", "🌍 Global Tech"])

    # === TAB 1: CROP DOCTOR (Your AI) ===
    with tab1:
        st.header("📸 AI Crop Doctor (पीक डॉक्टर)")
        st.info("Upload a photo to detect diseases instantly.")
        
        mode = st.radio("Input:", ["📂 Upload Image", "📸 Take Photo"], horizontal=True)
        file = None
        if mode == "📸 Take Photo": 
            file = st.camera_input("Capture")
        else: 
            file = st.file_uploader("Select File", type=['jpg','png','jpeg'])
            
        if file:
            st.image(file, width=300)
            if st.button("🔍 Diagnose Crop"):
                with st.spinner("Consulting AI Expert..."):
                    img_bytes = file.getvalue()
                    prompt = f"""
                    Act as an expert Indian Agronomist. Language: {lang}.
                    Location: {city}, Weather: {w_text}.
                    1. Name the Disease.
                    2. Natural/Organic Remedy.
                    3. Chemical Remedy (only if urgent).
                    4. Weather Warning if weather is {w_cond}.
                    Keep it simple and direct for a farmer.
                    """
                    res = analyze_image_ai(GOOGLE_API_KEY, img_bytes, prompt)
                    st.markdown(f'<div class="glass-card">{res}</div>', unsafe_allow_html=True)
                    
                    # Audio
                    try:
                        clean_text = res.replace('*', '').replace('#', '')
                        tts = gTTS(clean_text, lang=lang_map[lang])
                        audio_bytes = io.BytesIO()
                        tts.write_to_fp(audio_bytes)
                        audio_bytes.seek(0)
                        st.audio(audio_bytes, format="audio/mp3")
                    except:
                        st.warning("Audio unavailable on cloud.")

    # === TAB 2: DAILY PLANNER (New Feature) ===
    with tab2:
        st.header("📅 Daily Farm Planner (दैनंदिन नियोजन)")
        
        col1, col2 = st.columns(2)
        with col1:
            crop_name = st.selectbox("Select Crop", ["Wheat", "Rice", "Sugarcane", "Tomato", "Cotton"])
            sowing_date = st.date_input("Sowing Date (पेरणी तारीख)", datetime.date(2024, 1, 1))
        
        with col2:
            # Logic: Calculate Age
            today = datetime.date.today()
            age_days = (today - sowing_date).days
            
            st.metric(label="Crop Age (Days)", value=f"{age_days} Days")
            
            # Logic: Automatic Alert based on Age
            alert_msg = "✅ Crop is healthy. Keep monitoring."
            if age_days < 10:
                alert_msg = "🌱 Germination Stage: Ensure light watering. Do not use heavy fertilizers."
            elif 20 < age_days < 40:
                alert_msg = "🌿 Vegetative Stage: Check for weeds now. Apply Nitrogen (Urea) if leaves are yellow."
            elif 60 < age_days < 80:
                alert_msg = "🌸 Flowering Stage: CRITICAL! Do not spray chemicals now or you kill bees. Water regularly."
            elif age_days > 100:
                alert_msg = "🌾 Harvest Stage: Stop watering 10 days before cutting."
            
            st.info(f"📢 **Today's Advice:** {alert_msg}")
            
            # Weather Warning Logic
            if "Rain" in w_cond:
                st.error("🌧️ **RAIN ALERT:** Do not spray any medicine today! It will wash away.")

    # === TAB 3: GOVT SCHEMES (New Feature) ===
    with tab3:
        st.header("📜 Government Schemes (शासकीय योजना)")
        selected_state = st.selectbox("Select Your State", list(SCHEMES_DB.keys()))
        
        st.write(f"Showing schemes for: **{selected_state}**")
        
        for scheme in SCHEMES_DB[selected_state]:
            with st.expander(f"🏛️ {scheme['name']}"):
                st.write(f"**Benefit:** {scheme['benefit']}")
                st.markdown(f"[Apply Here / More Info]({scheme['link']})")

    # === TAB 4: GLOBAL TECH (New Idea) ===
    with tab4:
        st.header("🌍 Global Best Practices (Smart Farming)")
        st.write("Technologies used in Israel/USA adapted for India:")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🛒 Direct-to-Consumer Market")
            st.caption("Sell without middlemen (Coming Soon)")
            st.button("List My Crop for Sale")
            
        with c2:
            st.subheader("🚁 Drone Rental Service")
            st.caption("Rent a drone for spraying medicine (Coming Soon)")
            st.button("Find Drone Pilot Nearby")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f8ff; }
    .glass-card { 
        background: white; padding: 20px; border-radius: 10px; 
        border-left: 5px solid #2e7d32; box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
    }
    h1, h2, h3 { color: #1b5e20; }
    </style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
