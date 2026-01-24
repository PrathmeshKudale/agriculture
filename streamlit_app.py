import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai

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

# --- 3. "IONIC" MOBILE CSS (Optimized) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* GLOBAL RESET */
    .stApp { background-color: #f4f9f4; font-family: 'Poppins', sans-serif; color: #1a1a1a; }
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }

    /* MOBILE TEXT SIZE FIXES */
    @media (max-width: 600px) {
        .hero-title { font-size: 1.8rem !important; }
        .hero-subtitle { font-size: 0.9rem !important; }
        h1, h2, h3 { font-size: 1.5rem !important; }
        p, li { font-size: 0.9rem !important; }
        .feature-card { padding: 15px !important; }
    }

    /* HERO SECTION */
    .hero-container {
        background: linear-gradient(135deg, #0f5132 0%, #198754 100%);
        border-radius: 0 0 25px 25px; 
        padding: 30px 20px; 
        color: white; 
        margin: -1rem -1rem 20px -1rem;
        box-shadow: 0 10px 30px rgba(25, 135, 84, 0.2);
    }
    .hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .hero-subtitle { opacity: 0.9; margin-top: 5px; font-weight: 300; }

    /* CARDS */
    .feature-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.03); border: 1px solid #eef5ee;
        transition: transform 0.2s;
    }
    
    /* SCHEMES GRID */
    .scheme-card { 
        background: #e9f7ef; border-radius: 15px; padding: 15px; 
        border: 1px solid #c3e6cb; text-align: center; margin-bottom: 10px;
    }
    .scheme-title { font-weight: 700; color: #198754; font-size: 14px; margin-bottom: 5px; }
    .scheme-desc { font-size: 12px; color: #555; }

    /* NEWS CARD */
    .news-card { 
        background: white; border-radius: 12px; padding: 15px; 
        margin-bottom: 15px; border-left: 5px solid #198754; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
    }
    
    /* BUTTONS */
    .stButton>button { 
        background: #198754 !important; color: white !important; 
        border-radius: 50px; border: none; font-weight: 600; width: 100%; 
    }
    .stButton>button:hover { background: #146c43 !important; }

    /* TAB BAR */
    .stTabs [data-baseweb="tab-list"] { background: white; padding: 8px; border-radius: 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); gap: 5px; }
    .stTabs [data-baseweb="tab"] { border-radius: 40px; border: none; font-size: 13px; flex: 1; }
    .stTabs [aria-selected="true"] { background: #198754 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA & LOGIC ---
PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year income support.", "link": "https://pmkisan.gov.in/"},
    {"name": "PMFBY", "desc": "Crop insurance scheme.", "link": "https://pmfby.gov.in/"},
    {"name": "Kisan Credit Card", "desc": "Low interest loans (4%).", "link": "https://pib.gov.in/"},
    {"name": "e-NAM", "desc": "Online crop trading.", "link": "https://enam.gov.in/"},
    {"name": "Soil Health Card", "desc": "Free soil testing.", "link": "https://soilhealth.dac.gov.in/"},
    {"name": "PM-KUSUM", "desc": "Solar Pump Subsidy.", "link": "https://pmkusum.mnre.gov.in/"}
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
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        headlines = [f"TITLE: {entry.title} | LINK: {entry.link}" for entry in feed.entries[:5]]
        raw_text = "\n".join(headlines)

        prompt = f"""
        Act as a News Editor. Translate these news items into {language}.
        Format as HTML:
        <div class="news-card">
            <div class="news-headline">HEADLINE</div>
            <div class="news-body">Summary in {language}.</div>
            <a href="LINK" style="color:#198754; font-weight:bold; display:block; margin-top:5px;">Read More &rarr;</a>
        </div>
        Input: {raw_text}
        """
        return get_ai_response(prompt)
    except: return "<div style='padding:15px; color:red;'>News Unavailable</div>"

# --- 5. APP LAYOUT ---
# --- 5. APP LAYOUT ---
def main():
    # Initialize Camera State
    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False

    # --- HERO SECTION (NAVBAR STYLE) ---
    # We use a 2-column layout: Small Logo (left) + Title (right)
    
    col1, col2 = st.columns([1, 4]) # col1 is small (logo), col2 is big (text)
    
    with col1:
        # Display Logo (Small Size)
        try:
            st.image("logo.png", width=85) # Fixed small width
        except:
            st.warning("No logo found")
            
    with col2:
        # Display Title next to logo
        st.markdown("""
            <div style="margin-top: 10px;">
                <h1 style="margin:0; font-size: 28px; color:#0f5132;">GreenMitra</h1>
                <p style="margin:0; font-size: 14px; color:#555;">Farmer's Assistant</p>
            </div>
        """, unsafe_allow_html=True)

    # --- SETTINGS ROW ---
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True) # Tiny spacer
        c1, c2 = st.columns([2, 1])
        with c1: 
            lang_options = {"English": "English", "Marathi (मराठी)": "Marathi", "Hindi (हिंदी)": "Hindi", "Tamil (தமிழ்)": "Tamil", "Telugu (తెలుగు)": "Telugu", "Kannada (ಕನ್ನಡ)": "Kannada", "Gujarati (ગુજરાતી)": "Gujarati", "Punjabi (ਪੰਜਾਬੀ)": "Punjabi", "Odia (ଓଡ଼ିଆ)": "Odia"}
            selected_lang_label = st.selectbox("Select Language / भाषा", list(lang_options.keys()))
            target_lang = lang_options[selected_lang_label]
        with c2: 
            w_cond, w_temp = get_weather("Pune")
            st.markdown(f"<div style='background:white; padding:10px; border-radius:10px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-top:28px;'><b>{w_temp}°C</b> {w_cond}</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🌾 Crop Doctor", "📰 News & Schemes", "💬 Chat", "📅 Plan"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 AI Doctor ({target_lang})")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="feature-card">
                <p><b>Option 1:</b> Upload a photo.</p>
            </div>
            """, unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload Image", type=['jpg','png'])

        with col2:
            st.markdown(f"""
            <div class="feature-card">
                <p><b>Option 2:</b> Live Camera</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.show_camera:
                if st.button("📸 Start Camera"):
                    st.session_state.show_camera = True
                    st.rerun()
            else:
                img_file = st.camera_input("Scan Crop")
                if st.button("❌ Close Camera"):
                    st.session_state.show_camera = False
                    st.rerun()
                if img_file:
                    uploaded_file = img_file 

        if uploaded_file:
            st.image(uploaded_file, width=150)
            if st.button("Diagnose Crop Now"):
                with st.spinner("Analyzing..."):
                    img_bytes = uploaded_file.getvalue()
                    prompt = f"Identify crop disease. Suggest remedy. OUTPUT IN {target_lang}."
                    res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                    st.success("Analysis Complete")
                    st.write(res)

    # === TAB 2: NEWS & SCHEMES ===
    with tabs[1]:
        st.markdown("### 🏛️ Major Schemes")
        cols = st.columns(3)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 3]:
                st.markdown(f"""<div class="scheme-card"><div class="scheme-title">{scheme['name']}</div><div class="scheme-desc">{scheme['desc']}</div><a href="{scheme['link']}" style="color:#198754;">Open</a></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"### 🔴 Trending News ({target_lang})")
        if st.button("🔄 Refresh Live News"):
            with st.spinner("Fetching news..."):
                news_html = fetch_translated_news(target_lang)
                st.markdown(news_html, unsafe_allow_html=True)

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
                    reply = get_ai_response(f"Reply in {target_lang}. Question: {prompt}")
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
