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
    layout="centered",
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

# --- 3. CLEAN & SAFE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. APP BACKGROUND */
    .stApp {
        background-color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. TEXT COLORS */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #111827;
    }
    
    /* 3. CARD STYLE */
    .app-card {
        background-color: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* 4. WEATHER WIDGET */
    .weather-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.4);
        display: flex; justify-content: space-between; align-items: center;
    }
    .weather-box h1, .weather-box p { color: white !important; }

    /* 5. GREEN BUTTONS */
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 50px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background-color: #059669; color: white; }

    /* 6. INPUT FIELDS (Safe Styling) */
    .stTextInput input {
        background-color: white;
        color: black;
        border-radius: 10px;
    }
    
    /* 7. DROPDOWN FIX (Simplified) */
    /* We just ensure the background is white to avoid the black box issue */
    ul[data-baseweb="menu"] {
        background-color: white !important;
    }
    li[data-baseweb="option"] {
        color: black !important;
    }

    /* Hide Streamlit Header */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
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

def fetch_translated_news(language):
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        headlines = [f"- {e.title}" for e in feed.entries[:4]]
        raw_text = "\n".join(headlines)
        prompt = f"Translate these headlines to {language}. Format as simple HTML bullet points. Input: {raw_text}"
        return get_ai_response(prompt)
    except: return "News unavailable."

def speak_text(text, lang_code):
    js = f"""<script>
        var msg = new SpeechSynthesisUtterance({json.dumps(text)});
        msg.lang = '{lang_code}';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js, height=0, width=0)

# --- 5. MAIN APP ---
def main():
    if "messages" not in st.session_state: 
        st.session_state.messages = [{"role": "assistant", "content": "Namaste! How can I help your farm?"}]
    if "user_city" not in st.session_state: st.session_state.user_city = "Kolhapur"

    # --- TOP BAR ---
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"### 📍 {st.session_state.user_city}")
        st.caption("Your Location")
    with c2:
        st.markdown("<div style='background:#10b981; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>GM</div>", unsafe_allow_html=True)

    # --- WEATHER ---
    w_cond, w_temp = get_weather(st.session_state.user_city)
    st.markdown(f"""
    <div class="weather-box">
        <div>
            <h1 style="margin:0; font-size:42px;">{w_temp}°C</h1>
            <p style="margin:0; font-size:16px;">{w_cond}</p>
        </div>
        <div style="font-size:40px;">⛅</div>
    </div>
    """, unsafe_allow_html=True)

    # --- LANGUAGE SELECTOR ---
    # We use st.radio for fewer than 5 options if dropdown fails, but let's try standard selectbox first
    lang_map = {"English": "en-IN", "Marathi": "mr-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN"}
    selected_lang = st.selectbox("🌐 Choose Language / भाषा", list(lang_map.keys()))
    voice_lang = lang_map[selected_lang]

    # --- TABS ---
    tabs = st.tabs(["🌾 Doctor", "📰 News", "💬 Chat", "📅 Plan"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 Plant Diagnosis")
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.info("Option 1: Camera")
            cam = st.camera_input("Scan Leaf")
        with c2:
            st.info("Option 2: Upload")
            up = st.file_uploader("Upload File", type=['jpg','png'], label_visibility="collapsed")
        
        file = cam if cam else up
        
        if file:
            st.image(file, width=200)
            if st.button("Diagnose & Speak"):
                with st.spinner("Checking..."):
                    img_bytes = file.getvalue()
                    prompt = f"Identify crop disease. Suggest Organic remedy. Output in {selected_lang}."
                    res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                    st.success("Analysis Complete")
                    st.write(res)
                    speak_text(res.replace("*", ""), voice_lang)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: NEWS & SCHEMES ===
    with tabs[1]:
        st.markdown(f"### 📢 Schemes")
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        if st.button("🔄 Get Live News"):
            with st.spinner("Fetching..."):
                news = fetch_translated_news(selected_lang)
                st.markdown(news, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 3: CHATBOT ===
    with tabs[2]:
        st.markdown('<div class="app-card" style="min-height:400px;">', unsafe_allow_html=True)
        st.subheader("💬 Assistant")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        st.write("🎤 **Tap to Speak:**")
        audio_text = speech_to_text(language=voice_lang, start_prompt="🟢 Start", stop_prompt="🔴 Stop", just_once=True, key='STT')
        
        text_input = st.chat_input(f"Ask in {selected_lang}...")
        prompt = audio_text if audio_text else text_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    reply = get_ai_response(f"Act as Farm Expert. Reply in {selected_lang}. Q: {prompt}")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    speak_text(reply.replace("*", ""), voice_lang)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 4: PLANNER ===
    with tabs[3]:
        st.markdown("### 📅 Planner")
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        crop = st.text_input("Crop Name", "Tomato")
        date = st.date_input("Sowing Date", datetime.date.today())
        
        if st.button("Generate Schedule"):
            with st.spinner("Creating..."):
                days = (datetime.date.today() - date).days
                sch = get_ai_response(f"Create weekly schedule for {crop} (Age: {days} days) in {selected_lang}.")
                st.write(sch)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
