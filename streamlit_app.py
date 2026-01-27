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
    layout="centered", # Mobile-app style layout
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

# --- 3. FARMERCHAT THEME CSS (CLEAN & ATTRACTIVE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. APP BACKGROUND (Clean Grey) */
    .stApp {
        background-color: #f3f4f6 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* 2. TEXT VISIBILITY (Dark Grey/Black) */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #111827 !important;
    }
    .stMarkdown p { color: #374151 !important; } /* Softer grey for body text */
    
    /* 3. MOBILE APP CARDS */
    .app-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
    }
    
    /* 4. GREEN ACCENT CARD */
    .green-card {
        background-color: #ecfdf5; /* Very light green */
        border: 1px solid #10b981;
        border-radius: 16px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .green-card h3, .green-card p { color: #065f46 !important; }

    /* 5. WEATHER WIDGET STYLE */
    .weather-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.4);
        display: flex; justify-content: space-between; align-items: center;
    }
    .weather-box h1, .weather-box p, .weather-box small { color: white !important; }

    /* 6. BUTTONS (Emerald Green) */
    .stButton>button {
        background-color: #10b981 !important;
        color: white !important;
        border-radius: 50px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #059669 !important; }

    /* 7. INPUTS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px;
        border: 1px solid #d1d5db;
        background-color: white !important;
        color: black !important;
    }

    /* 8. TABS */
    .stTabs [data-baseweb="tab-list"] { background-color: white; padding: 5px; border-radius: 50px; gap: 5px; }
    .stTabs [data-baseweb="tab"] { border-radius: 30px; border: none; font-weight: 500; font-size: 14px; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; }

    /* HIDE HEADER/FOOTER */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 6rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIC FUNCTIONS ---
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
        # User Icon
        st.markdown("<div style='background:#10b981; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>GM</div>", unsafe_allow_html=True)

    # --- WEATHER WIDGET (Attractive Green Box) ---
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
    lang_map = {"English": "en-IN", "Marathi": "mr-IN", "Hindi": "hi-IN", "Tamil": "ta-IN", "Telugu": "te-IN"}
    selected_lang = st.selectbox("🌐 Choose Language / भाषा", list(lang_map.keys()))
    voice_lang = lang_map[selected_lang]

    # --- TABS FOR ALL SECTIONS ---
    tabs = st.tabs(["🌾 Doctor", "📰 News", "💬 Chat", "📅 Plan"])

    # === TAB 1: CROP DOCTOR (Clean UI) ===
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
                with st.spinner("AI Doctor is checking..."):
                    img_bytes = file.getvalue()
                    prompt = f"Identify crop disease. Suggest Organic remedy. Output in {selected_lang}."
                    res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                    
                    st.markdown(f"""
                    <div class="green-card">
                        <h3>✅ Diagnosis Result</h3>
                        <p>{res}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    speak_text(res.replace("*", ""), voice_lang)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: NEWS & SCHEMES (Clean UI) ===
    with tabs[1]:
        st.markdown(f"### 📢 Government Schemes")
        
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        schemes = [
            {"name": "PM-KISAN", "desc": "₹6,000/year support."},
            {"name": "PMFBY", "desc": "Crop Insurance."}
        ]
        for s in schemes:
            st.markdown(f"**{s['name']}**: {s['desc']}")
            st.markdown("---")
        
        if st.button("🔄 Get Live News"):
            with st.spinner("Fetching..."):
                news = fetch_translated_news(selected_lang)
                st.markdown(f"<div class='green-card'>{news}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 3: CHATBOT (FarmerChat Style) ===
    with tabs[2]:
        st.markdown('<div class="app-card" style="min-height:400px;">', unsafe_allow_html=True)
        st.subheader("💬 Ask Assistant")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        # Voice Input
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

    # === TAB 4: PLANNER (Clean UI) ===
    with tabs[3]:
        st.markdown("### 📅 Smart Planner")
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        crop = st.text_input("Crop Name", "Tomato")
        date = st.date_input("Sowing Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        
        st.markdown(f"""
        <div style="text-align:center; margin:20px;">
            <h1 style="color:#10b981; margin:0;">{days}</h1>
            <p>Days Old</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Generate Schedule"):
            with st.spinner("Creating..."):
                sch = get_ai_response(f"Create weekly schedule for {crop} (Age: {days} days) in {selected_lang}.")
                st.markdown(f"<div class='green-card'>{sch}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
