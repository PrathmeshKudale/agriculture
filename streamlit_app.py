import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
from streamlit.components.v1 import html

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra",
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

# --- 3. CSS STYLING (Agrova Clean Look) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    .stApp { background-color: #f8fcf8; font-family: 'Poppins', sans-serif; color: #1f3a28; }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }

    /* HERO SECTION */
    .hero-container {
        background: linear-gradient(135deg, #134e28 0%, #2e7d32 100%);
        border-radius: 20px; padding: 40px; color: white;
        margin-bottom: 30px; box-shadow: 0 10px 30px rgba(46, 125, 50, 0.2);
    }
    .hero-title { font-size: 3rem; font-weight: 700; margin-bottom: 10px; }
    
    /* CARDS */
    .feature-card {
        background: white; border-radius: 16px; padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e0eadd;
        transition: transform 0.3s ease; height: 100%;
    }
    .feature-card:hover { transform: translateY(-5px); border-color: #81c784; }

    /* BUTTONS & INPUTS */
    .stButton>button {
        background-color: #4CAF50 !important; color: white !important;
        border-radius: 50px; padding: 12px 30px; font-weight: 600; width: 100%;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        border-radius: 12px; border: 1px solid #dcdcdc; background-color: white; color: #333;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { background-color: white; padding: 10px; border-radius: 50px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 30px; border: none; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #2e7d32 !important; color: white !important; }

    h1, h2, h3, h4 { color: #1b5e20 !important; }
    #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SMART LOGIC ---
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
    except Exception as e: return f"⚠️ Error: {str(e)}"

def get_weather(city):
    if not WEATHER_API_KEY: return "Cloudy", 28
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data['weather'][0]['main'], data['main']['temp']
    except: return "Clear", 25

# --- NEW FUNCTION: TRANSLATED NEWS ---
def fetch_translated_news(language):
    """
    Fetches English news and uses AI to translate it into the selected Indian Language.
    """
    try:
        # 1. Get Raw English News
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        
        headlines = []
        if feed.entries:
            for entry in feed.entries[:4]:
                headlines.append(f"- {entry.title} (Source: {entry.source.title})")
        
        raw_text = "\n".join(headlines)

        # 2. If Language is English, show directly
        if "English" in language:
            formatted_news = []
            for entry in feed.entries[:4]:
                clean_title = entry.title.split(" - ")[0]
                formatted_news.append(f"""
                <div style="background:#f1f8e9; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #4CAF50;">
                    <strong style="color:#2e7d32;">{clean_title}</strong><br>
                    <a href="{entry.link}" style="float:right; color:#4CAF50; text-decoration:none; font-weight:bold;">Read &rarr;</a>
                </div>""")
            return "".join(formatted_news)

        # 3. If Indian Language, Ask AI to Translate
        prompt = f"""
        Translate these agriculture news headlines into {language}.
        Format them as a clean HTML list.
        Headlines:
        {raw_text}
        
        Output format example:
        <div style="background:#f1f8e9; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #4CAF50;">
            <strong style="color:#2e7d32;">[Translated Headline]</strong><br>
        </div>
        """
        return get_ai_response(prompt)

    except: pass
    return "<div style='padding:20px; background:#fff3e0; color:#e65100;'>⚠️ Feed Unavailable.</div>"

# --- 5. MAIN APP LAYOUT ---
def main():
    # --- HERO SECTION ---
    st.markdown("""
        <div class="hero-container">
            <div style="max-width: 800px;">
                <div class="hero-title">GreenMitra AI</div>
                <div style="font-size:1.2rem;">Empowering Farmers in Every Language.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- SETTINGS ROW ---
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        with c1: name = st.text_input("Name / नाव", "Kisan Bhai")
        with c2: city = st.text_input("Village / गाव", "Pune")
        with c3: 
            # SELECT LANGUAGE
            lang = st.selectbox("Language / भाषा", [
                "English", 
                "Marathi (मराठी)", 
                "Hindi (हिंदी)", 
                "Tamil (தமிழ்)", 
                "Telugu (తెలుగు)", 
                "Urdu (اردو)", 
                "Gujarati (ગુજરાતી)", 
                "Kannada (ಕನ್ನಡ)", 
                "Malayalam (മലയാളം)", 
                "Punjabi (ਪੰਜਾਬੀ)", 
                "Assamese (অসমীয়া)", 
                "Odia (ଓଡ଼ିଆ)"
            ])
        with c4: 
            w_cond, w_temp = get_weather(city)
            st.markdown(f"""
            <div style="text-align:center; background:white; padding:5px; border-radius:10px; border:1px solid #ddd;">
                <h3 style="margin:0; color:#2e7d32;">{w_temp}°C</h3>
                <small>{w_cond}</small>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # --- TABS ---
    tabs = st.tabs(["🌾 Crop Doctor", "📢 Yojana (Schemes)", "🤖 Kisan Chat", "📅 My Planner"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"""
            <div class="feature-card">
                <h3>📸 AI Crop Diagnosis</h3>
                <p>Selected Language: <b>{lang}</b></p>
                <p>Upload a photo. The AI will write the report in your language.</p>
            </div>
            """, unsafe_allow_html=True)
            mode = st.radio("Select Source", ["Upload Image", "Open Camera"], horizontal=True)
            
        with c2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            file = st.camera_input("Take Photo") if mode == "Open Camera" else st.file_uploader("Upload File", type=['jpg','png'])
            
            if file:
                st.image(file, width=200, caption="Uploaded Sample")
                if st.button("Analyze Now"):
                    with st.spinner(f"Analyzing in {lang}..."):
                        img_bytes = file.getvalue()
                        prompt = f"You are an expert Agronomist. Identify the disease, give remedies. Reply strictly in {lang} language."
                        res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                        st.markdown(f"<div style='background:#f1f8e9; padding:20px; border-radius:10px;'>{res}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: NEWS & SCHEMES (AUTO-TRANSLATED) ===
    with tabs[1]:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### 📡 Live Updates ({lang})")
            if st.button("🔴 Fetch & Translate News"):
                with st.spinner("Fetching and Translating..."):
                    news_html = fetch_translated_news(lang)
                    st.markdown(news_html, unsafe_allow_html=True)
            else:
                st.info("Click the button to load news in your language.")

        with col2:
            st.markdown(f"### 🏛️ Famous Schemes ({lang})")
            # We ask AI to generate the static list in the user's language
            if st.button("Load Schemes List"):
                with st.spinner("Loading..."):
                    scheme_prompt = f"List 3 famous Indian government agriculture schemes (like PM-KISAN) with 1-line description in {lang}."
                    res = get_ai_response(scheme_prompt)
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)

    # === TAB 3: CHAT (MULTI-LANGUAGE) ===
    with tabs[2]:
        st.markdown('<div class="feature-card" style="min-height:500px;">', unsafe_allow_html=True)
        st.subheader(f"💬 Chat ({lang})")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"Namaste! I speak {lang}. Ask me anything."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # CRITICAL: Force AI to use the selected language
                    system_prompt = f"Act as an Indian Agriculture Expert. Reply strictly in {lang} language. User Question: {prompt}"
                    ai_reply = get_ai_response(system_prompt)
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 4: PLANNER ===
    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="feature-card">
                <h3>📅 Crop Calendar</h3>
                <p>Track your crop age.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton", "Sugarcane"])
            date = st.date_input("Sowing Date", datetime.date.today())
            days = (datetime.date.today() - date).days
            st.markdown(f"<h1 style='text-align:center; color:#2e7d32; font-size:60px; margin:0;'>{days}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Days Old</p>", unsafe_allow_html=True)
            if days < 20: st.info("🌱 Germination Phase")
            elif days < 60: st.success("🌿 Vegetative Phase")
            else: st.warning("🌾 Harvest Phase")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("""
    <div style="text-align:center; padding:30px; margin-top:50px; color:#888; border-top:1px solid #eee;">
        <p>© 2026 GreenMitra AI • Empowering Rural India</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
