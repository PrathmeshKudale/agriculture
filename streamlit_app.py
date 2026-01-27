import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json
from streamlit_mic_recorder import speech_to_text

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra",
    page_icon="🌿",
    layout="centered", # Mobile-first view
    initial_sidebar_state="collapsed"
)

# --- 2. KEYS ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    GOOGLE_API_KEY = ""

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- 3. "FARMERCHAT" MOBILE UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* 1. RESET BACKGROUND (Clean Mobile Look) */
    .stApp {
        background-color: #f3f4f6 !important; /* Light Grey like the app */
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. TEXT COLORS (Dark Black for readability) */
    h1, h2, h3, h4, p, div, span, label, li {
        color: #1f2937 !important; 
    }
    
    /* 3. CARD STYLE (The "Ionic" Look) */
    .mobile-card {
        background-color: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* 4. GREEN BANNER CARD */
    .green-banner {
        background-color: #d1fae5; /* Light Green */
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #10b981;
        color: #065f46 !important;
    }
    
    /* 5. WEATHER WIDGET */
    .weather-widget {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 6. BUTTONS (The "Ask" Button) */
    .stButton>button {
        background-color: #10b981 !important; /* App Green */
        color: white !important;
        border-radius: 50px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    
    /* 7. HIDE DEFAULT UI */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 8rem; }
    
    /* 8. CHAT INPUT FLOATING FIX */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        background: white;
        box-shadow: 0 -4px 6px -1px rgba(0,0,0,0.1);
        z-index: 999;
    }
    
    /* 9. DROPDOWN MENU FIX (Nuclear) */
    div[data-baseweb="popover"], ul[data-baseweb="menu"], li[data-baseweb="option"] {
        background-color: white !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIC ---
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return next((m for m in models if 'flash' in m), "models/gemini-1.5-flash")
    except: return "models/gemini-1.5-flash"

def get_ai_response(prompt, image=None):
    try:
        model = genai.GenerativeModel(get_working_model())
        return model.generate_content([prompt, image] if image else prompt).text
    except Exception as e: return f"System Error: {str(e)}"

def get_weather(city):
    if not WEATHER_API_KEY: return "Clear Sky", 29
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data['weather'][0]['description'].title(), int(data['main']['temp'])
    except: return "Clear", 29

def speak_text(text, lang_code):
    js = f"""<script>
        var msg = new SpeechSynthesisUtterance({json.dumps(text)});
        msg.lang = '{lang_code}';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js, height=0, width=0)

# --- 5. MAIN APP LAYOUT ---
def main():
    if "messages" not in st.session_state: 
        st.session_state.messages = [{"role": "assistant", "content": "Namaste! I am GreenMitra. How can I help your farm today?"}]
    if "user_city" not in st.session_state: st.session_state.user_city = "Kolhapur"

    # --- TOP BAR (Like the Screenshot) ---
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"### 📍 {st.session_state.user_city}")
        st.caption("Your Approximate Location")
    with c2:
        # Profile Icon Placeholder
        st.markdown("<div style='background:#10b981; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>GM</div>", unsafe_allow_html=True)

    # --- WEATHER WIDGET (Like the Screenshot) ---
    w_cond, w_temp = get_weather(st.session_state.user_city)
    st.markdown(f"""
    <div class="weather-widget">
        <div>
            <h1 style="margin:0; font-size:48px;">{w_temp}°C</h1>
            <p style="margin:0;">{w_cond}</p>
            <small style="color:#666;">Ideal conditions for planting.</small>
        </div>
        <div style="text-align:right;">
            <span style="font-size:40px;">⛅</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- GREEN BANNER (Like the Screenshot) ---
    st.markdown("""
    <div class="green-banner">
        <h3 style="margin:0; color:#065f46 !important;">Get better advice for your farm</h3>
        <p style="margin:0; font-size:14px; color:#065f46 !important;">Add your crop details for personalized AI tips.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- LANGUAGE SELECTOR (Small & Clean) ---
    lang_map = {"English": "en-IN", "Marathi": "mr-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN", "Kannada": "kn-IN"}
    selected_lang = st.selectbox("🌐 Change Language", list(lang_map.keys()))
    voice_lang = lang_map[selected_lang]

    # --- "GET STARTED" SUGGESTIONS (Like Screenshot) ---
    st.markdown("### Get Started")
    st.markdown("<p style='margin-top:-10px; margin-bottom:15px; color:#666 !important;'>Need help? Tap a question to get advice.</p>", unsafe_allow_html=True)

    # Quick Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Fertilizers?"):
            prompt = f"Which fertilizer is best for flowering stage? Answer in {selected_lang}."
            st.session_state.messages.append({"role": "user", "content": "Best fertilizer?"})
            res = get_ai_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": res})
            speak_text(res, voice_lang)
            st.rerun()
            
    with col2:
        if st.button("🐛 Pest Control?"):
            prompt = f"How to control pests organically? Answer in {selected_lang}."
            st.session_state.messages.append({"role": "user", "content": "Pest control?"})
            res = get_ai_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": res})
            speak_text(res, voice_lang)
            st.rerun()

    # --- CROP DOCTOR (Camera/Upload) ---
    st.markdown("### 📸 Scan Crop")
    c1, c2 = st.columns([1, 4])
    with c1:
        # Camera Icon Button styling
        st.markdown("<div style='font-size:30px;'>📷</div>", unsafe_allow_html=True)
    with c2:
        file = st.file_uploader("Upload or Take Photo", type=['jpg','png'], label_visibility="collapsed")
    
    if file:
        st.image(file, width=200, caption="Analyzing...")
        if st.button("Diagnose This Image"):
            with st.spinner("AI Doctor is checking..."):
                img_bytes = file.getvalue()
                prompt = f"Identify crop disease and suggest remedy. Output in {selected_lang} language."
                res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                st.session_state.messages.append({"role": "user", "content": "Diagnose this crop image."})
                st.session_state.messages.append({"role": "assistant", "content": res})
                speak_text(res.replace("*", ""), voice_lang)
                st.rerun()

    # --- CHAT INTERFACE (Bottom) ---
    st.markdown("---")
    st.markdown("### 💬 Chat History")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- INPUT BAR (Voice & Text) ---
    # We use Streamlit's native input because it's the most stable
    if user_input := st.chat_input(f"Ask anything in {selected_lang}..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = f"Act as an Indian Farm Expert. User asks: {user_input}. Reply in {selected_lang}."
                response = get_ai_response(full_prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                speak_text(response.replace("*", ""), voice_lang)

if __name__ == "__main__":
    main()
