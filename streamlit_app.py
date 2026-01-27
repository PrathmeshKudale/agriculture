import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json
# NEW: Import Voice Library (Ensure requirements.txt is updated)
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

# --- 3. ADVANCED CSS (Mint Theme + Fixed Dropdown) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* 1. APP THEME */
    .stApp { 
        background-color: #f1f8e9 !important; /* Mint Green */
        font-family: 'Poppins', sans-serif; 
    }
    
    /* 2. TEXT VISIBILITY */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown { 
        color: #1a1a1a !important; 
    }

    /* 3. DROPDOWN FIX (The "White Box" Rule) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
    }
    li[data-baseweb="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    li[data-baseweb="option"]:hover {
        background-color: #e8f5e9 !important; /* Green Hover */
        color: #000000 !important;
    }
    li[data-baseweb="option"][aria-selected="true"] {
        background-color: #138808 !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* 4. NAVBAR & CARDS */
    .hero-container {
        background: white; border-bottom: 4px solid #ff9933;
        padding: 20px; margin: -1rem -1rem 20px -1rem;
        display: flex; align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .feature-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
    .stButton>button {
        background: #138808 !important; color: white !important;
        border-radius: 8px; border: none; font-weight: 600; width: 100%; padding: 12px;
    }
    .stButton>button:hover { background: #0f6b06 !important; }

    /* 5. TABS & UTILS */
    .stTabs [data-baseweb="tab-list"] { background: white; padding: 5px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: none; font-size: 14px; flex: 1; color: #333; }
    .stTabs [aria-selected="true"] { background: #138808 !important; color: white !important; }
    
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ADVANCED FUNCTIONS (Voice & AI) ---

# Text-to-Speech (The app speaks back to the farmer)
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
                "Gujarati (ગુજરાતી)": "gu-IN", "Punjabi (ਪੰਜਾਬੀ)": "pa-IN"
            }
            # The Dropdown (Now fixed with CSS)
            sel_lang_key = st.selectbox("Select Language / भाषा", list(lang_map.keys()))
            target_lang = sel_lang_key
            voice_lang_code = lang_map[sel_lang_key]
            
        with c2: user_city = st.text_input("Village / गाव", "Kolhapur")
        with c3: 
            w_cond, w_temp = get_weather(user_city)
            st.markdown(f"<div style='background:white; padding:8px; border-radius:8px; text-align:center; margin-top:28px;'><b>{w_temp}°C</b><br>{w_cond}</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🩺 Doctor", "🌱 Smart Farm", "📰 Yojana", "💬 Chat"])

    # === TAB 1: CROP DOCTOR (Voice Enabled) ===
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
                    st.success("Analysis Complete")
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)
                    # ADVANCED: Speak the result
                    speak_text(res.replace("*", ""), voice_lang_code)

    # === TAB 2: SMART FARM (Profit + Planner) ===
    with tabs[1]:
        st.markdown(f"### 🌱 Smart Farm Manager ({target_lang})")
        
        # Switcher for Advanced Tools
        tool = st.radio("Select Tool:", ["💰 Profit Calculator (New Crop)", "📅 Weekly Planner (Current Crop)"], horizontal=True)
        st.markdown("---")

        if "Profit" in tool:
            st.info("💡 **AI Market Analysis:** Find the most profitable crop for your land.")
            c1, c2 = st.columns(2)
            with c1: 
                season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])
                budget = st.selectbox("Investment", ["Low", "Medium", "High"])
            with c2: 
                water = st.selectbox("Water Source", ["Rainfed", "Well/Canal", "Drip Irrigation"])
                land = st.text_input("Land Size", "1 Acre")
            
            if st.button("🚀 Calculate Profit"):
                with st.spinner("Analyzing Market Trends..."):
                    prompt = f"Suggest 3 most profitable crops for Season: {season}, Location: {user_city}, Budget: {budget}, Water: {water}. Output in {target_lang}."
                    res = get_ai_response(prompt)
                    st.markdown(f"<div class='feature-card' style='border-left:5px solid #ff9933'>{res}</div>", unsafe_allow_html=True)
                    speak_text("Here are the best crops for you.", voice_lang_code)

        else:
            st.info("📅 **Smart Schedule:** Get a to-do list for your standing crop.")
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
                st.markdown(news_html, unsafe_allow_html=True)

    # === TAB 4: ADVANCED VOICE CHAT ===
    with tabs[3]:
        st.markdown(f"### 💬 Kisan Sahayak ({target_lang})")
        
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        # ADVANCED: Voice Input
        st.write("🎤 **Tap to Speak / बोलण्यासाठी टॅप करा:**")
        audio_text = speech_to_text(language=voice_lang_code, start_prompt="🟢 Start Recording", stop_prompt="🔴 Stop Recording", just_once=True, key='STT')
        
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
                    # ADVANCED: Speak Reply
                    speak_text(reply.replace("*", ""), voice_lang_code)

if __name__ == "__main__":
    main()
