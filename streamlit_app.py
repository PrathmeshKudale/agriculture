import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
from streamlit.components.v1 import html

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra App",
    page_icon="🌾",
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

# --- 3. "IONIC/EPIC" MOBILE CSS ( The Magic Part ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* GLOBAL THEME */
    .stApp { background-color: #f4f9f4; font-family: 'Poppins', sans-serif; color: #1a1a1a; }
    
    /* HIDE DEFAULT HEADER/FOOTER */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* 📱 MOBILE OPTIMIZATIONS */
    @media (max-width: 600px) {
        .hero-title { font-size: 1.8rem !important; }
        .hero-subtitle { font-size: 0.9rem !important; }
        .feature-card { padding: 15px !important; margin-bottom: 10px !important; }
        .card-icon { width: 40px !important; height: 40px !important; font-size: 20px !important; }
        .stButton>button { padding: 10px 20px !important; font-size: 14px !important; }
    }

    /* EPIC HERO SECTION */
    .hero-container {
        background: linear-gradient(135deg, #0f5132 0%, #198754 100%);
        border-radius: 24px; padding: 30px; color: white;
        margin-bottom: 25px; box-shadow: 0 15px 30px rgba(25, 135, 84, 0.25);
        position: relative; overflow: hidden;
    }
    .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .hero-subtitle { opacity: 0.9; margin-top: 5px; font-weight: 300; }
    
    /* GLASS/IONIC CARDS */
    .feature-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03); border: 1px solid #eef5ee;
        transition: transform 0.2s; height: 100%;
    }
    .feature-card:hover { transform: translateY(-3px); border-color: #198754; }

    /* ICONS */
    .card-icon {
        background: #e9f7ef; color: #198754; width: 50px; height: 50px;
        border-radius: 12px; display: flex; align-items: center; justify-content: center;
        font-size: 24px; margin-bottom: 15px;
    }

    /* TEXT COLORS (Fixed for Light Mode) */
    h1, h2, h3, h4 { color: #0f5132 !important; }
    p, span, li, label { color: #333333 !important; }
    .stMarkdown p { color: #444 !important; }

    /* PILL BUTTONS */
    .stButton>button {
        background: #198754 !important; color: white !important;
        border-radius: 50px; border: none; font-weight: 600;
        box-shadow: 0 4px 12px rgba(25, 135, 84, 0.3);
        width: 100%; transition: all 0.2s;
    }
    .stButton>button:hover { transform: scale(1.02); background: #146c43 !important; }

    /* TAB BAR (Like an App) */
    .stTabs [data-baseweb="tab-list"] {
        background: white; padding: 8px; border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px; border: none; font-size: 14px; flex: 1;
    }
    .stTabs [aria-selected="true"] {
        background: #198754 !important; color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SMART LOGIC (FIXED LANGUAGES) ---
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
    except Exception as e: return f"⚠️ System Error: {str(e)}"

def get_weather(city):
    if not WEATHER_API_KEY: return "Sunny", 30
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data['weather'][0]['main'], data['main']['temp']
    except: return "Clear", 25

def fetch_translated_news(language):
    """
    Forces AI to translate English news into the user's SELECTED language.
    """
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        
        headlines = []
        if feed.entries:
            for entry in feed.entries[:4]:
                headlines.append(f"- {entry.title}")
        
        raw_text = "\n".join(headlines)

        # AI TRANSLATOR AGENT
        prompt = f"""
        Act as a professional translator.
        Translate these agricultural news headlines into {language} language.
        Output MUST be a simple list of headlines.
        Headlines:
        {raw_text}
        """
        translated_text = get_ai_response(prompt)
        
        # Format HTML
        return f"""
        <div style="background:white; padding:20px; border-radius:15px; border:1px solid #eee;">
            <h4 style="color:#198754; margin-top:0;">📢 Updates in {language}</h4>
            <div style="color:#444; white-space: pre-line;">{translated_text}</div>
        </div>
        """
    except:
        return "<div style='padding:15px; color:red;'>News Unavailable</div>"

# --- 5. APP LAYOUT ---
def main():
    # --- HEADER ---
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">GreenMitra</div>
            <div class="hero-subtitle">Next-Gen AI for Indian Farmers</div>
        </div>
    """, unsafe_allow_html=True)

    # --- SETTINGS (CARD STYLE) ---
    with st.container():
        st.markdown('<div class="feature-card" style="padding:15px; margin-bottom:20px;">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1: 
            # FIXED LANGUAGE SELECTOR
            lang_options = {
                "English": "English",
                "Marathi (मराठी)": "Marathi",
                "Hindi (हिंदी)": "Hindi",
                "Tamil (தமிழ்)": "Tamil",
                "Telugu (తెలుగు)": "Telugu",
                "Kannada (ಕನ್ನಡ)": "Kannada",
                "Gujarati (ગુજરાતી)": "Gujarati",
                "Punjabi (ਪੰਜਾਬੀ)": "Punjabi",
                "Malayalam (മലയാളം)": "Malayalam",
                "Odia (ଓଡ଼ିଆ)": "Odia"
            }
            selected_lang_label = st.selectbox("Select Language / भाषा", list(lang_options.keys()))
            target_lang = lang_options[selected_lang_label] # This sends clean "Marathi", "Tamil" to AI

        with c2: city = st.text_input("Village / गाव", "Pune")
        with c3:
            w_cond, w_temp = get_weather(city)
            st.markdown(f"<div style='text-align:center; color:#198754;'><b>{w_temp}°C</b><br><small>{w_cond}</small></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TABS (BOTTOM NAV STYLE) ---
    tabs = st.tabs(["🌾 Doctor", "📰 News", "💬 Chat", "📅 Plan"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 AI Crop Doctor ({target_lang})")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("""
            <div class="feature-card">
                <div class="card-icon">📸</div>
                <p>Upload a photo. I will identify the disease and give medicine in <b>%s</b>.</p>
            </div>
            """ % target_lang, unsafe_allow_html=True)
            mode = st.radio("Source", ["Upload", "Camera"], horizontal=True, label_visibility="collapsed")
            
        with c2:
            file = st.camera_input("Scan") if mode == "Camera" else st.file_uploader("Upload", type=['jpg','png'])
            if file:
                st.image(file, width=150)
                if st.button("Analyze Now"):
                    with st.spinner("Scanning..."):
                        img_bytes = file.getvalue()
                        # STRICT LANGUAGE PROMPT
                        prompt = f"You are an Agronomist. Identify crop disease. Suggest Organic and Chemical remedy. OUTPUT MUST BE IN {target_lang} LANGUAGE ONLY."
                        res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                        st.markdown(f"<div class='feature-card' style='border-left:5px solid #198754;'>{res}</div>", unsafe_allow_html=True)

    # === TAB 2: NEWS (TRANSLATED) ===
    with tabs[1]:
        st.markdown(f"### 📢 Live Yojana ({target_lang})")
        if st.button("🔄 Refresh News"):
            news_html = fetch_translated_news(target_lang)
            st.markdown(news_html, unsafe_allow_html=True)
        else:
            st.info(f"Click above to load news in {target_lang}.")

    # === TAB 3: CHAT (MULTI-LANGUAGE) ===
    with tabs[2]:
        st.markdown(f"### 🤖 Kisan Sahayak ({target_lang})")
        
        # Clear chat if language changes to avoid confusion
        if "last_lang" not in st.session_state or st.session_state.last_lang != target_lang:
            st.session_state.messages = []
            st.session_state.last_lang = target_lang

        if not st.session_state.messages:
             st.session_state.messages = [{"role": "assistant", "content": f"Namaste! Ask me anything in {target_lang}."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about seeds, weather..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # FORCE AI LANGUAGE
                    system_prompt = f"Act as an Indian Agriculture Expert. Reply ONLY in {target_lang} language. Keep answers short. Question: {prompt}"
                    ai_reply = get_ai_response(system_prompt)
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # === TAB 4: PLANNER ===
    with tabs[3]:
        st.markdown("### 📅 Crop Calendar")
        c1, c2 = st.columns(2)
        with c1: crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton", "Sugarcane"])
        with c2: date = st.date_input("Sowing Date", datetime.date.today())
        
        days = (datetime.date.today() - date).days
        st.markdown(f"""
        <div class="feature-card" style="text-align:center; padding:30px;">
            <h1 style="color:#198754; font-size:4rem; margin:0;">{days}</h1>
            <p>Days Old</p>
            <div style="background:#e9f7ef; padding:10px; border-radius:10px; margin-top:10px;">
                { "🌱 Germination Phase" if days < 20 else "🌿 Vegetative Phase" if days < 60 else "🌾 Harvest Phase" }
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
