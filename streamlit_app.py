import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json
from streamlit_mic_recorder import speech_to_text

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra (Kisan)",
    page_icon="🇮🇳",
    layout="wide",
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

# --- 3. CSS (HD BACKGROUND + SAFE DROPDOWN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* 1. HD BACKGROUND IMAGE */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2832&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Poppins', sans-serif;
    }
    
    /* 2. OVERLAY (To make text readable) */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.4);
        pointer-events: none;
        z-index: -1;
    }

    /* 3. TEXT VISIBILITY */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown, .stText { 
        color: #1a1a1a !important; 
    }

    /* 4. SAFE DROPDOWN FIX (Won't break clicking) */
    /* Only change colors, don't touch position/pointer-events */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc !important;
    }
    div[data-baseweb="popover"], ul[data-baseweb="menu"] {
        background-color: white !important;
    }
    li[data-baseweb="option"] {
        color: black !important;
        background-color: white !important;
    }
    li[data-baseweb="option"]:hover {
        background-color: #e8f5e9 !important;
    }

    /* 5. GLASS NAVBAR */
    .hero-container {
        background: rgba(255, 255, 255, 0.95);
        border-bottom: 4px solid #ff9933;
        padding: 20px;
        margin: -1rem -1rem 20px -1rem;
        display: flex; align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }

    /* 6. WHITE CARDS */
    .feature-card {
        background: #ffffff; 
        border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
    
    /* 7. BUTTONS */
    .stButton>button {
        background: #138808 !important; color: white !important;
        border-radius: 8px; border: none; font-weight: 600; width: 100%; padding: 12px;
    }
    .stButton>button:hover { background: #0f6b06 !important; }

    /* 8. TABS */
    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(255, 255, 255, 0.9); 
        padding: 5px; border-radius: 10px; 
    }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: none; font-size: 14px; flex: 1; color: #333; }
    .stTabs [aria-selected="true"] { background: #138808 !important; color: white !important; }
    
    input { color: black !important; caret-color: black !important; }
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. JS VOICE OUTPUT ---
def speak_text(text, lang_code):
    js = f"""
    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = {json.dumps(text)};
        msg.lang = '{lang_code}';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

# --- 5. LOGIC ---
PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year income support.", "link": "https://pmkisan.gov.in/"},
    {"name": "PMFBY (Insurance)", "desc": "Crop insurance scheme.", "link": "https://pmfby.gov.in/"},
    {"name": "Kisan Credit Card", "desc": "Low interest loans (4%).", "link": "https://pib.gov.in/"},
    {"name": "e-NAM Market", "desc": "Online trading platform.", "link": "https://enam.gov.in/"}
]

def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for model in available_models:
            if 'flash' in model: return model
        return available_models[0] if available_models else "models/gemini-1.5-flash"
    except: return "models/gemini-1.5-flash"

def get_ai_response(prompt, image=None):
    model_name = get_working_model()
    try:
        model = genai.GenerativeModel(model_name)
        return model.generate_content([prompt, image] if image else prompt).text
    except Exception as e: return f"⚠️ Server Busy. ({str(e)})"

def get_weather(city):
    if not WEATHER_API_KEY: return "Sunny", 32
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data['weather'][0]['main'], data['main']['temp']
    except: return "Clear", 28

def fetch_translated_news(language):
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        headlines = [f"- {e.title}" for e in feed.entries[:4]]
        raw_text = "\n".join(headlines)
        prompt = f"Translate these headlines to {language}. Format as HTML Cards. Input: {raw_text}"
        return get_ai_response(prompt)
    except: return "News unavailable."

# --- 6. MAIN APP ---
def main():
    if "show_camera" not in st.session_state: st.session_state.show_camera = False

    # --- HERO HEADER ---
    col1, col2 = st.columns([1, 5])
    with col1:
        try: st.image("logo.jpg", width=130) 
        except: st.write("🌾")
    with col2:
        st.markdown("""
            <div style="padding-top: 25px;">
                <h1 style='font-size:32px; margin:0; line-height:1; color:#138808 !important;'>GreenMitra AI</h1>
                <p style='font-size:14px; margin:0; color:#555 !important;'>India's Smart Kisan Assistant</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- SETTINGS (GLASS BOX) ---
    # This "feature-card" makes sure text is readable over the image
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True) 
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: 
            lang_map = {
                "English": "en-IN", "Marathi (मराठी)": "mr-IN", "Hindi (हिंदी)": "hi-IN",
                "Tamil (தமிழ்)": "ta-IN", "Telugu (తెలుగు)": "te-IN", "Kannada (ಕನ್ನಡ)": "kn-IN",
                "Gujarati (ગુજરાતી)": "gu-IN", "Punjabi (ਪੰਜਾਬੀ)": "pa-IN"
            }
            # Standard Selectbox (Reliable)
            sel_lang_key = st.selectbox("Select Language / भाषा", list(lang_map.keys()))
            target_lang = sel_lang_key
            voice_lang_code = lang_map[sel_lang_key]
            
        with c2: user_city = st.text_input("Village / गाव", "Kolhapur")
        with c3: 
            w_cond, w_temp = get_weather(user_city)
            st.markdown(f"<div style='background:#e9f7ef; padding:8px; border-radius:8px; text-align:center;'><b>{w_temp}°C</b><br>{w_cond}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🩺 Doctor", "🌱 Smart Farm", "📰 Yojana", "💬 Chat"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 Crop Health Check ({target_lang})")
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1: uploaded_file = st.file_uploader("Upload File", type=['jpg','png'], label_visibility="collapsed")
        with c2:
            if not st.session_state.show_camera:
                if st.button("📸 Open Camera"): st.session_state.show_camera = True; st.rerun()
            else:
                cam_file = st.camera_input("Scan")
                if st.button("❌ Close"): st.session_state.show_camera = False; st.rerun()
                if cam_file: uploaded_file = cam_file

        if uploaded_file:
            st.image(uploaded_file, width=150)
            if st.button("🔍 Diagnose & Speak"):
                with st.spinner(f"Analyzing in {target_lang}..."):
                    img_bytes = uploaded_file.getvalue()
                    prompt = f"Identify crop disease. Suggest Organic & Chemical remedy. OUTPUT IN {target_lang}. Keep it short."
                    res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                    st.write(res)
                    speak_text(res.replace("*", ""), voice_lang_code)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: SMART FARM ===
    with tabs[1]:
        st.markdown(f"### 🌱 Smart Farm Manager ({target_lang})")
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        tool_choice = st.radio("Select Tool:", ["💰 Profit Calculator", "📅 Weekly Planner"], horizontal=True)
        st.markdown("---")

        if tool_choice == "💰 Profit Calculator":
            c1, c2 = st.columns(2)
            with c1: 
                season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])
                land = st.text_input("Land (Acres)", "2")
            with c2: 
                budget = st.selectbox("Budget", ["Low", "Medium", "High"])
                water = st.selectbox("Water", ["Rainfed", "Well", "Drip"])
            
            if st.button("🚀 Find Profitable Crops"):
                with st.spinner("Analyzing Market..."):
                    prompt = f"Suggest 3 most profitable crops for Season: {season}, Location: {user_city}, Budget: {budget}, Water: {water}. Output in {target_lang}."
                    res = get_ai_response(prompt)
                    st.write(res)
                    speak_text("Here are the best crops for you.", voice_lang_code)
        
        else: 
            c1, c2 = st.columns(2)
            with c1: crop_name = st.text_input("Crop Name", "Sugarcane")
            with c2: sow_date = st.date_input("Sowing Date", datetime.date.today())
            
            days_old = (datetime.date.today() - sow_date).days
            st.write(f"**Crop Age:** {days_old} Days")

            if st.button("📝 Create Schedule"):
                with st.spinner("Creating Plan..."):
                    prompt = f"Create a detailed weekly schedule for {crop_name} (Age: {days_old} days). Language: {target_lang}. Include fertilizer, water, and disease prevention."
                    res = get_ai_response(prompt)
                    st.write(res)
                    speak_text("I have created your weekly schedule.", voice_lang_code)
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 3: NEWS & SCHEMES ===
    with tabs[2]:
        st.markdown("### 🏛️ Schemes")
        cols = st.columns(2)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 2]:
                st.markdown(f"<div class='feature-card' style='padding:10px; text-align:center;'><b>{scheme['name']}</b><br><a href='{scheme['link']}'>View</a></div>", unsafe_allow_html=True)

        st.markdown(f"### 📰 News ({target_lang})")
        if st.button("🔄 Refresh News"):
            with st.spinner("Fetching..."):
                news_html = fetch_translated_news(target_lang)
                st.markdown(f"<div class='feature-card'>{news_html}</div>", unsafe_allow_html=True)

    # === TAB 4: VOICE CHAT ===
    with tabs[3]:
        st.markdown(f"### 💬 Kisan Sahayak ({target_lang})")
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        st.write("🎤 **Speak (Tap):**")
        audio_text = speech_to_text(language=voice_lang_code, start_prompt="🟢 Start", stop_prompt="🔴 Stop", just_once=True, key='STT')
        
        text_input = st.chat_input("...or type here")
        
        prompt = None
        if audio_text: prompt = audio_text
        elif text_input: prompt = text_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_ai_response(f"Reply in {target_lang}. Q: {prompt}")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    speak_text(reply.replace("*", ""), voice_lang_code)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
