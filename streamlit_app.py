import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json

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

# --- 3. 3D & MODERN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* 1. APP THEME */
    .stApp { background-color: #f1f8e9 !important; font-family: 'Poppins', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown { color: #1a1a1a !important; }

    /* 2. DROPDOWN FIX (White Box) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
    }
    li[data-baseweb="option"] { background-color: #ffffff !important; color: #000000 !important; }
    li[data-baseweb="option"]:hover { background-color: #e8f5e9 !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #ccc !important; }
    
    /* 3. MODERN CARDS (Glass Effect + 3D Shadow) */
    .hero-container { background: white; border-bottom: 4px solid #ff9933; padding: 20px; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    
    .feature-card {
        background: white; 
        border-radius: 16px; 
        padding: 20px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05), 0 6px 6px rgba(0,0,0,0.05); /* 3D Lift */
        border: 1px solid #ffffff;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    .feature-card:hover { transform: translateY(-3px); } /* Slight lift on hover */

    /* 4. ANIMATED VOICE SECTION (Pulse Effect) */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(19, 136, 8, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(19, 136, 8, 0); }
        100% { box-shadow: 0 0 0 0 rgba(19, 136, 8, 0); }
    }
    
    .voice-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%);
        border: 2px solid #138808;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        animation: pulse-green 2s infinite;
        margin-bottom: 20px;
    }

    /* 5. BUTTONS & TABS */
    .stButton>button {
        background: linear-gradient(to right, #138808, #0f6b06) !important; /* Gradient Green */
        color: white !important;
        border-radius: 10px; border: none; font-weight: 600; width: 100%; padding: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] { background: white; padding: 8px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: none; font-size: 14px; flex: 1; color: #333; }
    .stTabs [aria-selected="true"] { background: #138808 !important; color: white !important; }
    
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ADVANCED FUNCTIONS ---
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

PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year income support for all landholding farmers.", "link": "https://pmkisan.gov.in/"},
    {"name": "PMFBY (Insurance)", "desc": "Crop insurance scheme with lowest premium rates.", "link": "https://pmfby.gov.in/"},
    {"name": "Kisan Credit Card", "desc": "Low interest loans (4%) for farming needs.", "link": "https://pib.gov.in/"},
    {"name": "e-NAM Market", "desc": "Online trading platform to sell crops for better prices.", "link": "https://enam.gov.in/"},
    {"name": "Soil Health Card", "desc": "Free soil testing reports to check fertilizer needs.", "link": "https://soilhealth.dac.gov.in/"},
    {"name": "PM-KUSUM", "desc": "Subsidy for installing Solar Pumps on farms.", "link": "https://pmkusum.mnre.gov.in/"}
]

def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return next((m for m in models if 'flash' in m), "models/gemini-1.5-flash")
    except: return "models/gemini-1.5-flash"

def get_ai_response(prompt, image=None):
    try:
        model = genai.GenerativeModel(get_working_model())
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

# --- 5. MAIN APP ---
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
                <p style='font-size:14px; margin:0; color:#555 !important;'>India's Advanced Kisan Assistant</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- SETTINGS ---
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: 
            lang_map = {
                "English": "en-IN", "Marathi (मराठी)": "mr-IN", "Hindi (हिंदी)": "hi-IN",
                "Tamil (தமிழ்)": "ta-IN", "Telugu (తెలుగు)": "te-IN", "Kannada (ಕನ್ನಡ)": "kn-IN",
                "Gujarati (ગુજરાતી)": "gu-IN"
            }
            sel_lang_key = st.selectbox("Select Language / भाषा", list(lang_map.keys()))
            target_lang = sel_lang_key
            voice_lang_code = lang_map[sel_lang_key]
            
        with c2: user_city = st.text_input("Village / गाव", "Kolhapur")
        with c3: 
            w_cond, w_temp = get_weather(user_city)
            st.markdown(f"<div style='background:white; padding:8px; border-radius:8px; text-align:center; margin-top:28px;'><b>{w_temp}°C</b><br>{w_cond}</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🩺 Doctor", "🌱 Smart Farm", "📰 Yojana", "💬 Voice Chat"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 Crop Health ({target_lang})")
        c1, c2 = st.columns([1, 1])
        with c1: uploaded_file = st.file_uploader("Select File", type=['jpg','png'], label_visibility="collapsed")
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
                    st.success("Complete")
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)
                    speak_text(res.replace("*", ""), voice_lang_code)

    # === TAB 2: SMART FARM (Simplified Language) ===
    with tabs[1]:
        st.markdown(f"### 🌱 Smart Farm ({target_lang})")
        tool = st.radio("Select Tool:", ["💰 Profit Calculator", "📅 Weekly Planner"], horizontal=True)
        st.markdown("---")

        if "Profit" in tool:
            # SIMPLIFIED FARMER LANGUAGE
            c1, c2 = st.columns(2)
            with c1: 
                season = st.selectbox("Season / हंगाम", ["Kharif (Monsoon / पावसाळा)", "Rabi (Winter / हिवाळा)", "Zaid (Summer / उन्हाळा)"])
                budget = st.selectbox("Budget / गुंतवणूक", ["Low (कमी)", "Medium (मध्यम)", "High (जास्त)"])
            with c2: 
                water = st.selectbox("Water / पाणी", ["Rainfed (केवळ पाऊस)", "Well/Bore (विहीर/बोअर)", "Full Irrigation (मुबलक पाणी)"])
                land = st.text_input("Land / जमीन", "1 Acre")
            
            if st.button("🚀 Calculate Profit / नफा शोधा"):
                with st.spinner("Analyzing..."):
                    prompt = f"Suggest 3 most profitable crops for Season: {season}, Location: {user_city}, Budget: {budget}, Water: {water}. Output in {target_lang}."
                    res = get_ai_response(prompt)
                    st.markdown(f"<div class='feature-card' style='border-left:5px solid #ff9933'>{res}</div>", unsafe_allow_html=True)
                    speak_text("Here is the profit plan.", voice_lang_code)

        else:
            c1, c2 = st.columns(2)
            with c1: crop_name = st.text_input("Crop Name", "Sugarcane")
            with c2: sow_date = st.date_input("Sowing Date", datetime.date.today())
            
            days_old = (datetime.date.today() - sow_date).days
            st.write(f"**Crop Age:** {days_old} Days")

            if st.button("📝 Create Schedule"):
                with st.spinner("Creating Plan..."):
                    prompt = f"Create weekly schedule for {crop_name} (Age: {days_old} days). Language: {target_lang}."
                    res = get_ai_response(prompt)
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)

    # === TAB 3: SCHEMES ===
    with tabs[2]:
        st.markdown("### 🏛️ Schemes")
        cols = st.columns(2)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 2]:
                st.markdown(f"<div class='feature-card' style='padding:10px; text-align:center;'><b>{scheme['name']}</b><br><a href='{scheme['link']}'>View</a></div>", unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🔄 Get Latest News"):
            with st.spinner("Fetching..."):
                news_html = fetch_translated_news(target_lang)
                st.markdown(news_html, unsafe_allow_html=True)

    # === TAB 4: 3D VOICE CHAT ===
    with tabs[3]:
        st.markdown(f"### 💬 Voice Assistant")
        
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        # 3D PULSING VOICE BOX
        st.markdown("""
            <div class="voice-box">
                <h3 style="color:#138808; margin:0;">🎙️ Tap Below to Speak</h3>
                <p style="color:#666; font-size:12px;">(बोलण्यासाठी खालील बटण दाबा)</p>
            </div>
        """, unsafe_allow_html=True)

        # SAFETY CHECK IMPORT
        try:
            from streamlit_mic_recorder import speech_to_text
            audio_text = speech_to_text(
                language=voice_lang_code,
                start_prompt="🟢 START (सुरू करा)",
                stop_prompt="🔴 STOP (थांबवा)",
                just_once=True,
                key='STT_KEY'
            )
        except ImportError:
            st.error("⚠️ Voice Library Missing! Please verify requirements.txt")
            audio_text = None
        except Exception:
            st.warning("⚠️ Voice unavailable on this browser. Use text below.")
            audio_text = None
        
        text_input = st.chat_input("...or type here")
        prompt = audio_text if audio_text else text_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_ai_response(f"Reply in {target_lang}. Q: {prompt}")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    speak_text(reply.replace("*", ""), voice_lang_code)

if __name__ == "__main__":
    main()
