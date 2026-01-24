import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
from streamlit.components.v1 import html

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra News",
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

# --- 3. "NEWS WEBSITE" CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&display=swap'); /* For News Text */

    /* GLOBAL THEME */
    .stApp { background-color: #f4f9f4; font-family: 'Poppins', sans-serif; color: #1a1a1a; }
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* 📱 MOBILE OPTIMIZATIONS */
    @media (max-width: 600px) {
        .hero-title { font-size: 1.8rem !important; }
        .hero-subtitle { font-size: 0.9rem !important; }
        .news-card { padding: 15px !important; }
        .scheme-grid { grid-template-columns: 1fr !important; }
    }

    /* EPIC HERO SECTION */
    .hero-container {
        background: linear-gradient(135deg, #0f5132 0%, #198754 100%);
        border-radius: 0 0 25px 25px; /* Rounded bottom only */
        padding: 40px 20px; color: white; margin: -1rem -1rem 20px -1rem;
        box-shadow: 0 10px 30px rgba(25, 135, 84, 0.2);
    }
    .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .hero-subtitle { opacity: 0.9; margin-top: 5px; font-weight: 300; }

    /* NEWS WEBSITE CARD STYLE */
    .news-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #198754;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .news-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
    .news-headline { font-family: 'Merriweather', serif; font-size: 18px; font-weight: 700; color: #0f5132; margin-bottom: 8px; }
    .news-source { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .news-body { font-size: 14px; color: #444; line-height: 1.6; margin-top: 10px; }

    /* PERMANENT SCHEME GRID */
    .scheme-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin-top: 10px;
    }
    .scheme-card {
        background: #e9f7ef;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #c3e6cb;
        text-align: center;
    }
    .scheme-title { font-weight: 700; color: #198754; margin-bottom: 5px; }
    .scheme-desc { font-size: 13px; color: #555; }

    /* TAB BAR */
    .stTabs [data-baseweb="tab-list"] {
        background: white; padding: 8px; border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); gap: 5px;
    }
    .stTabs [data-baseweb="tab"] { border-radius: 40px; border: none; font-size: 14px; flex: 1; }
    .stTabs [aria-selected="true"] { background: #198754 !important; color: white !important; }

    /* BUTTONS */
    .stButton>button {
        background: #198754 !important; color: white !important;
        border-radius: 50px; border: none; font-weight: 600; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & LOGIC ---

# PERMANENT SCHEMES DATABASE (Static Data)
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
    Fetches Google News and styles it like a News Website Card.
    """
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        
        headlines = []
        if feed.entries:
            for entry in feed.entries[:5]:
                headlines.append(f"TITLE: {entry.title} | LINK: {entry.link} | SOURCE: {entry.source.title}")
        
        raw_text = "\n".join(headlines)

        # AI NEWS EDITOR & TRANSLATOR
        prompt = f"""
        Act as a News Editor for 'GreenMitra News'.
        1. Translate these news items into {language}.
        2. Format each item STRICTLY as HTML using this structure:
        
        <div class="news-card">
            <div class="news-source">SOURCE_NAME_HERE</div>
            <div class="news-headline">TRANSLATED_HEADLINE_HERE</div>
            <div class="news-body">Short 1-line summary in {language}.</div>
            <a href="LINK_HERE" style="color:#198754; font-weight:bold; text-decoration:none; font-size:14px; display:block; margin-top:10px;">Read Full Story &rarr;</a>
        </div>

        Input Data:
        {raw_text}
        """
        return get_ai_response(prompt)
    except:
        return "<div style='padding:15px; color:red;'>News Unavailable</div>"

# --- 5. APP LAYOUT ---
def main():
    # --- HERO HEADER ---
    st.markdown("""
        <div class="hero-container">
            <div style="text-align:center;">
                <div class="hero-title">GreenMitra</div>
                <div class="hero-subtitle">Farmers' Digital News & Assistant</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- SETTINGS ---
    with st.container():
        c1, c2 = st.columns([2, 1])
        with c1: 
            lang_options = {"English": "English", "Marathi (मराठी)": "Marathi", "Hindi (हिंदी)": "Hindi", "Tamil (தமிழ்)": "Tamil", "Telugu (తెలుగు)": "Telugu", "Kannada (ಕನ್ನಡ)": "Kannada", "Gujarati (ગુજરાતી)": "Gujarati", "Punjabi (ਪੰਜਾਬੀ)": "Punjabi", "Odia (ଓଡ଼ିଆ)": "Odia"}
            selected_lang_label = st.selectbox("Select Language / भाषा", list(lang_options.keys()))
            target_lang = lang_options[selected_lang_label]

        with c2: 
            w_cond, w_temp = get_weather("Pune") # Default for display
            st.markdown(f"<div style='background:white; padding:10px; border-radius:10px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.05);'><b>{w_temp}°C</b> {w_cond}</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["📰 News & Schemes", "🌾 Crop Doctor", "💬 Chat", "📅 Plan"])

    # === TAB 1: NEWS & SCHEMES (THE NEW UPDATE) ===
    with tabs[0]:
        # SECTION 1: PERMANENT SCHEMES (Static Grid)
        st.markdown("### 🏛️ Major Government Schemes (Permanent)")
        
        # Grid Layout for Permanent Schemes
        cols = st.columns(3)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="scheme-card">
                    <div class="scheme-title">{scheme['name']}</div>
                    <div class="scheme-desc">{scheme['desc']}</div>
                    <a href="{scheme['link']}" style="font-size:12px; color:#198754; font-weight:bold;">Official Site</a>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SECTION 2: LIVE NEWS FEED
        st.markdown(f"### 🔴 Trending Agriculture News ({target_lang})")
        if st.button("🔄 Refresh Live News"):
            with st.spinner(f"Fetching news from Times of India, PIB, and translating to {target_lang}..."):
                news_html = fetch_translated_news(target_lang)
                st.markdown(news_html, unsafe_allow_html=True)
        else:
            st.info("Click 'Refresh' to see the latest news headlines.")

    # === TAB 2: CROP DOCTOR ===
    with tabs[1]:
        st.markdown(f"### 🩺 AI Doctor ({target_lang})")
        c1, c2 = st.columns([1, 1])
        with c1:
            mode = st.radio("Input", ["Camera", "Upload"], horizontal=True)
            file = st.camera_input("Scan") if mode == "Camera" else st.file_uploader("Upload", type=['jpg','png'])
        with c2:
            if file:
                st.image(file, width=150)
                if st.button("Diagnose"):
                    with st.spinner("Analyzing..."):
                        img_bytes = file.getvalue()
                        prompt = f"Identify crop disease. Suggest remedy. OUTPUT IN {target_lang}."
                        res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                        st.success("Done!")
                        st.write(res)

    # === TAB 3: CHAT ===
    with tabs[2]:
        st.markdown(f"### 💬 Chat ({target_lang})")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    system_prompt = f"Reply in {target_lang}. Question: {prompt}"
                    reply = get_ai_response(system_prompt)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

    # === TAB 4: PLANNER ===
    with tabs[3]:
        st.markdown("### 📅 Planner")
        date = st.date_input("Sowing Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        st.metric("Crop Age", f"{days} Days")

if __name__ == "__main__":
    main()
