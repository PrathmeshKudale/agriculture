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

# --- 3. CSS & JS (THE DEEP DARK MODE FIX) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* 1. APP THEME */
    .stApp { 
        background-color: #f1f8e9 !important; /* Earthy Mint Green */
        font-family: 'Poppins', sans-serif; 
    }
    
    /* 2. FORCE BLACK TEXT EVERYWHERE */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown, .stText, .stTextInput, .stSelectbox { 
        color: #1a1a1a !important; 
    }

    /* --- 3. THE "DEEP" DROPDOWN FIX --- */
    /* We target the specific 'Virtual List' Streamlit uses */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
    }
    
    /* The individual options */
    li[role="option"], li[data-baseweb="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* The text inside options */
    li[role="option"] span, li[data-baseweb="option"] span {
        color: #000000 !important;
    }
    
    /* Hover State - Green Highlight */
    li[role="option"]:hover, li[data-baseweb="option"]:hover {
        background-color: #e8f5e9 !important;
        color: #000000 !important;
    }
    
    /* Selected State - Dark Green */
    li[role="option"][aria-selected="true"], li[data-baseweb="option"][aria-selected="true"] {
        background-color: #138808 !important;
        color: #ffffff !important;
    }
    
    /* The Clickable Box */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
    }
    /* ------------------------------------- */

    /* 4. NAVBAR & HERO */
    .hero-container {
        background: white;
        border-bottom: 4px solid #ff9933;
        padding: 20px;
        margin: -1rem -1rem 20px -1rem;
        display: flex; align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* 5. CARDS & BUTTONS */
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

    /* 6. HIDE JUNK */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }
    
    /* 7. TABS */
    .stTabs [data-baseweb="tab-list"] { background: white; padding: 5px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: none; font-size: 14px; flex: 1; color: #333; }
    .stTabs [aria-selected="true"] { background: #138808 !important; color: white !important; }
    
    /* 8. INPUTS */
    input { color: black !important; caret-color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. JS VOICE ASSISTANT FUNCTION ---
def speak_text(text, lang_code):
    # This creates a hidden HTML element that uses browser's TTS
    js = f"""
    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = {json.dumps(text)};
        msg.lang = '{lang_code}';
        window.speechSynthesis.cancel(); // Stop previous
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

# --- 5. LOGIC & DATA ---
PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6000 Income Support", "link": "https://pmkisan.gov.in/"},
    {"name": "PMFBY", "desc": "Crop Insurance", "link": "https://pmfby.gov.in/"},
    {"name": "KCC Loan", "desc": "Kisan Credit Card", "link": "https://pib.gov.in/"},
    {"name": "e-NAM", "desc": "Sell Crops Online", "link": "https://enam.gov.in/"},
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

    # --- SETTINGS & LOCATION ---
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: 
            lang_map = {
                "English": "en-IN", "Marathi (मराठी)": "mr-IN", "Hindi (हिंदी)": "hi-IN",
                "Tamil (தமிழ்)": "ta-IN", "Telugu (తెలుగు)": "te-IN", "Kannada (ಕನ್ನಡ)": "kn-IN",
                "Gujarati (ગુજરાતી)": "gu-IN", "Punjabi (ਪੰਜਾਬੀ)": "pa-IN"
            }
            sel_lang_key = st.selectbox("Select Language / भाषा", list(lang_map.keys()))
            target_lang = sel_lang_key
            voice_lang_code = lang_map[sel_lang_key] # For Voice Assistant
            
        with c2: user_city = st.text_input("Village / गाव", "Kolhapur")
        with c3: 
            w_cond, w_temp = get_weather(user_city)
            st.markdown(f"<div style='background:white; padding:8px; border-radius:8px; text-align:center; margin-top:28px;'><b>{w_temp}°C</b><br>{w_cond}</div>", unsafe_allow_html=True)

    # --- TABS (Updated with Profit Calc) ---
    tabs = st.tabs(["🩺 Doctor", "💰 Profit & Plan", "📰 Yojana", "💬 Chat"])

    # === TAB 1: CROP DOCTOR (WITH VOICE) ===
    with tabs[0]:
        st.markdown(f"### 🩺 Crop Health Check ({target_lang})")
        c1, c2 = st.columns([1, 1])
        with c1: uploaded_file = st.file_uploader("Upload File", type=['jpg','png'])
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
                    # VOICE OUTPUT
                    speak_text(res.replace("*", ""), voice_lang_code)

    # === TAB 2: PROFIT CALCULATOR (NEW FEATURE) ===
    with tabs[1]:
        st.markdown(f"### 💰 Profit Calculator & Planner")
        st.info("💡 **AI Suggestion:** Find out which crop will give you maximum money this season.")
        
        c1, c2 = st.columns(2)
        with c1: 
            season = st.selectbox("Current Season", ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"])
            land_size = st.text_input("Land Size (Acres)", "2")
        with c2: 
            budget = st.selectbox("Investment Capability", ["Low Budget", "Medium Budget", "High Budget"])
            water = st.selectbox("Water Source", ["Rainfed (Low Water)", "Well/Canal (Medium)", "Drip Irrigation (High)"])

        if st.button("🚀 Suggest Profitable Crops"):
            with st.spinner("AI is calculating market trends..."):
                prompt = f"""
                Act as an Agriculture Economist.
                Season: {season}. Location: {user_city}, India.
                Budget: {budget}. Water: {water}.
                Task: Suggest 3 MOST PROFITABLE crops to plant NOW.
                For each crop, explain WHY it is profitable (Market demand, price).
                Output language: {target_lang}.
                Format: 
                1. Crop Name - Expected Profit/Acre
                2. ...
                """
                profit_plan = get_ai_response(prompt)
                st.markdown(f"<div class='feature-card' style='border-left: 5px solid #ff9933;'>{profit_plan}</div>", unsafe_allow_html=True)
                speak_text("Here are the most profitable crops for you.", voice_lang_code)

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

    # === TAB 4: CHAT WITH VOICE ===
    with tabs[3]:
        st.markdown(f"### 💬 Kisan Sahayak ({target_lang})")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input("Ask..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    reply = get_ai_response(f"Reply in {target_lang}. Q: {prompt}")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    # VOICE AUTO-SPEAK
                    speak_text(reply.replace("*", ""), voice_lang_code)

if __name__ == "__main__":
    main()
