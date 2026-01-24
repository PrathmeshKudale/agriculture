import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai

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

# --- 3. "INDIAN GOVT STYLE" CSS (High Contrast) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Hind:wght@400;600&display=swap'); /* Good for Indian Langs */

    /* GLOBAL RESET & TEXT VISIBILITY FIX */
    .stApp { background-color: #f8fcf8; font-family: 'Poppins', 'Hind', sans-serif; }
    
    /* FORCE BLACK TEXT EVERYWHERE */
    h1, h2, h3, h4, h5, h6, p, div, span, li, label, .stMarkdown { 
        color: #1a1a1a !important; 
    }
    
    /* INPUT FIELDS VISIBILITY */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        color: #000 !important;
        background-color: #fff !important;
        border: 1px solid #ccc;
    }

    /* HIDE DEFAULT HEADER */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* NAVBAR STYLE HERO */
    .hero-container {
        background: white;
        border-bottom: 4px solid #ff9933; /* Saffron Line */
        padding: 15px 20px;
        margin: -1rem -1rem 20px -1rem;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .hero-logo { width: 50px; margin-right: 15px; }
    .hero-text h1 { font-size: 24px; margin: 0; color: #138808 !important; /* India Green */ }
    .hero-text p { font-size: 12px; margin: 0; color: #666 !important; font-weight: 600; text-transform: uppercase; }

    /* CARDS */
    .feature-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
    
    /* BUTTONS */
    .stButton>button {
        background: #138808 !important; /* India Green */
        color: white !important;
        border-radius: 8px; border: none; font-weight: 600; width: 100%;
        padding: 12px; font-size: 16px;
    }
    .stButton>button:hover { background: #0f6b06 !important; }

    /* TAB BAR */
    .stTabs [data-baseweb="tab-list"] { background: white; padding: 5px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; border: none; font-size: 14px; flex: 1; color: #333; }
    .stTabs [aria-selected="true"] { background: #138808 !important; color: white !important; }

    /* PLANNER TIMELINE STYLE */
    .plan-step {
        border-left: 3px solid #ff9933; margin-left: 10px; padding-left: 20px; padding-bottom: 20px; position: relative;
    }
    .plan-step::before {
        content: "●"; color: #ff9933; font-size: 20px; position: absolute; left: -11px; top: -5px;
    }
    .plan-title { font-weight: bold; color: #138808 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & LOGIC ---
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
    except Exception as e: return f"⚠️ Server Busy. Try again. ({str(e)})"

def get_weather(city):
    if not WEATHER_API_KEY: return "Sunny", 32
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data['weather'][0]['main'], data['main']['temp']
    except: return "Clear", 28

# --- 5. MAIN APP ---
def main():
    # Camera State
    if "show_camera" not in st.session_state: st.session_state.show_camera = False

    # --- NAVBAR HERO ---
    col1, col2 = st.columns([1, 5])
    with col1:
        try: st.image("logo.jpg", width=60) # Looks for logo.jpg
        except: st.write("🌾")
    with col2:
        st.markdown("""
            <div>
                <h1 style='font-size:22px; margin:0;'>GreenMitra AI</h1>
                <p style='font-size:12px; margin:0;'>India's Smart Kisan Assistant</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- SETTINGS (Card) ---
    with st.container():
        c1, c2 = st.columns([2, 1])
        with c1: 
            # STRICT LANGUAGE MAP
            lang_map = {
                "English": "English", "Marathi (मराठी)": "Marathi", "Hindi (हिंदी)": "Hindi",
                "Tamil (தமிழ்)": "Tamil", "Telugu (తెలుగు)": "Telugu", "Kannada (ಕನ್ನಡ)": "Kannada",
                "Gujarati (ગુજરાતી)": "Gujarati", "Punjabi (ਪੰਜਾਬੀ)": "Punjabi", "Odia (ଓଡ଼ିଆ)": "Odia",
                "Bengali (বাংলা)": "Bengali", "Malayalam (മലയാളം)": "Malayalam"
            }
            sel_lang = st.selectbox("Select Language / भाषा", list(lang_map.keys()))
            target_lang = lang_map[sel_lang]
        with c2: 
            w_cond, w_temp = get_weather("Pune")
            st.markdown(f"<div style='background:#e9f7ef; padding:8px; border-radius:8px; text-align:center; margin-top:28px;'><b>{w_temp}°C</b><br>{w_cond}</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🩺 Doctor", "📅 AI Planner", "📰 Yojana", "💬 Chat"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 Crop Health Check ({target_lang})")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.info("Option 1: Upload Photo")
            uploaded_file = st.file_uploader("Select File", type=['jpg','png'], label_visibility="collapsed")
        with c2:
            st.info("Option 2: Live Camera")
            if not st.session_state.show_camera:
                if st.button("📸 Open Camera"):
                    st.session_state.show_camera = True
                    st.rerun()
            else:
                cam_file = st.camera_input("Scan")
                if st.button("❌ Close"):
                    st.session_state.show_camera = False
                    st.rerun()
                if cam_file: uploaded_file = cam_file

        if uploaded_file:
            st.image(uploaded_file, width=150)
            if st.button("🔍 Diagnose Disease"):
                with st.spinner(f"Consulting AI Expert in {target_lang}..."):
                    img_bytes = uploaded_file.getvalue()
                    prompt = f"You are an Indian Agriculture Expert. Analyze this crop image. 1. Identify Disease. 2. Give Organic Solution. 3. Give Chemical Solution. OUTPUT STRICTLY IN {target_lang} LANGUAGE."
                    res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                    st.success("Report Ready")
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)

    # === TAB 2: AI SMART PLANNER (NEW & UPGRADED) ===
    with tabs[1]:
        st.markdown(f"### 📅 Smart Crop Manager ({target_lang})")
        st.markdown(f"Use AI to generate a schedule for your farm.")
        
        c1, c2 = st.columns(2)
        with c1: crop_name = st.text_input("Crop Name (e.g., Rice, Tomato)", "Tomato")
        with c2: sow_date = st.date_input("Sowing Date", datetime.date.today())
        
        days_old = (datetime.date.today() - sow_date).days
        
        # Display Crop Age
        st.markdown(f"""
        <div style="background:#fff3e0; padding:15px; border-radius:10px; border-left:5px solid #ff9933; margin:10px 0;">
            <h4 style="margin:0;">🌱 Crop Age: {days_old} Days</h4>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🤖 Generate Weekly Schedule"):
            with st.spinner(f"Creating Schedule in {target_lang}..."):
                # AI PROMPT FOR PLANNER
                prompt = f"""
                Act as an Expert Farm Manager.
                Crop: {crop_name}.
                Age: {days_old} days.
                Location: India.
                Language: {target_lang}.
                
                Task: Create a detailed schedule for THIS WEEK (Week {(days_old//7)+1}).
                Include:
                1. Fertilizer to apply now.
                2. Water requirement (High/Low).
                3. Disease to watch out for at this stage.
                
                Format as a clean list with emojis.
                """
                schedule = get_ai_response(prompt)
                st.markdown(f"<div class='feature-card'>{schedule}</div>", unsafe_allow_html=True)

    # === TAB 3: NEWS & SCHEMES ===
    with tabs[2]:
        st.markdown("### 🏛️ Sarkari Yojana")
        cols = st.columns(2)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 2]:
                st.markdown(f"""<div class='feature-card' style='padding:10px; text-align:center;'>
                <b>{scheme['name']}</b><br><small>{scheme['desc']}</small><br>
                <a href='{scheme['link']}' style='color:#138808; font-weight:bold;'>View</a></div>""", unsafe_allow_html=True)

        st.markdown(f"### 📰 Latest News ({target_lang})")
        if st.button("🔄 Load News"):
            with st.spinner("Fetching..."):
                try:
                    feed = feedparser.parse("https://news.google.com/rss/search?q=India+Agriculture+Schemes&hl=en-IN&gl=IN&ceid=IN:en")
                    headlines = [e.title for e in feed.entries[:4]]
                    txt = "\n".join(headlines)
                    prompt = f"Translate these 4 headlines to {target_lang}. Format as bullet points with '📰' icon. \n{txt}"
                    news_res = get_ai_response(prompt)
                    st.markdown(f"<div class='feature-card'>{news_res}</div>", unsafe_allow_html=True)
                except: st.error("News offline.")

    # === TAB 4: CHAT ===
    with tabs[3]:
        st.markdown(f"### 💬 Kisan Sahayak ({target_lang})")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        if prompt := st.chat_input(f"Ask in {target_lang}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    # STRICT LANGUAGE ENFORCEMENT
                    sys_prompt = f"You are an Indian Farming Expert. You MUST reply in {target_lang} language ONLY. Question: {prompt}"
                    reply = get_ai_response(sys_prompt)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
