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

# --- 3. "AGROVA STYLE" CSS (Clean & Green) ---
st.markdown("""
    <style>
    /* IMPORT GOOGLE FONTS (Poppins for modern feel) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* GLOBAL RESET - LIGHT THEME */
    .stApp {
        background-color: #f8fcf8; /* Very light mint white */
        font-family: 'Poppins', sans-serif;
        color: #1f3a28;
    }

    /* REMOVE DEFAULT STREAMLIT PADDING */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* HERO SECTION STYLING */
    .hero-container {
        background: linear-gradient(135deg, #134e28 0%, #2e7d32 100%);
        border-radius: 20px;
        padding: 40px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(46, 125, 50, 0.2);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }

    /* CARD DESIGN (Agrova Style) */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e0eadd;
        transition: transform 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(46, 125, 50, 0.1);
        border-color: #81c784;
    }
    .card-icon {
        font-size: 30px;
        background: #e8f5e9;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        color: #2e7d32;
    }

    /* CUSTOM BUTTONS */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: none;
        border-radius: 50px; /* Pill shape */
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #388E3C !important;
        transform: scale(1.02);
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        border-radius: 12px;
        border: 1px solid #dcdcdc;
        background-color: white;
        color: #333;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        display: inline-flex; /* Fix for layout */
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 10px 20px;
        background-color: transparent;
        color: #555;
        font-weight: 600;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e7d32 !important;
        color: white !important;
    }
    
    /* TEXT COLORS */
    h1, h2, h3, h4 { color: #1b5e20 !important; }
    p, li { color: #4a5d50 !important; }
    
    /* HIDE DEFAULT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. SMART LOGIC (Kept exactly the same) ---
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

def fetch_latest_schemes():
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        news_items = []
        if feed.entries:
            for entry in feed.entries[:4]:
                clean_title = entry.title.split(" - ")[0]
                news_items.append(f"""
                <div style="background:#f1f8e9; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #4CAF50;">
                    <strong style="color:#2e7d32;">{clean_title}</strong><br>
                    <span style="font-size:12px; color:#666;">Source: {entry.source.title}</span> 
                    <a href="{entry.link}" style="float:right; color:#4CAF50; text-decoration:none; font-weight:bold;">Read &rarr;</a>
                </div>
                """)
        if news_items: return "".join(news_items)
    except: pass
    return "<div style='padding:20px; background:#fff3e0; border-radius:10px; color:#e65100;'>⚠️ Live Feed Unavailable. Checking Offline Database...</div>"

# --- 5. MAIN APP LAYOUT ---
def main():
    # --- HERO SECTION (HTML INJECTION) ---
    st.markdown("""
        <div class="hero-container">
            <div style="max-width: 800px;">
                <div class="hero-title">Empowering Indian Farmers</div>
                <div class="hero-subtitle">Next-Gen AI tools for smarter, sustainable farming. Crop diagnosis, live schemes, and expert chat in one place.</div>
            </div>
            <div style="position:absolute; right:-50px; top:-50px; width:200px; height:200px; background:rgba(255,255,255,0.1); border-radius:50%;"></div>
        </div>
    """, unsafe_allow_html=True)

    # --- SETTINGS ROW ---
    with st.container():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        with c1: name = st.text_input("Name / नाव", "Kisan Bhai")
        with c2: city = st.text_input("Village / गाव", "Pune")
        with c3: lang = st.selectbox("Language / भाषा", ["English", "Marathi", "Hindi"])
        with c4: 
            w_cond, w_temp = get_weather(city)
            st.markdown(f"""
            <div style="text-align:center; background:white; padding:5px; border-radius:10px; border:1px solid #ddd;">
                <h3 style="margin:0; color:#2e7d32;">{w_temp}°C</h3>
                <small>{w_cond}</small>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # --- MODERN TABS ---
    tabs = st.tabs(["🌾 Crop Doctor", "📢 Yojana & News", "🤖 Kisan Chat", "📅 My Planner"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("""
            <div class="feature-card">
                <div class="card-icon">📸</div>
                <h3>AI Crop Diagnosis</h3>
                <p>Upload a photo of your crop leaf. Our AI will detect diseases and suggest organic remedies instantly.</p>
            </div>
            """, unsafe_allow_html=True)
            mode = st.radio("Select Source", ["Upload Image", "Open Camera"], horizontal=True)
            
        with c2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            file = st.camera_input("Take Photo") if mode == "Open Camera" else st.file_uploader("Upload File", type=['jpg','png'])
            
            if file:
                st.image(file, width=200, caption="Uploaded Sample")
                if st.button("Analyze Crop Health"):
                    with st.spinner("Consulting AI Expert..."):
                        img_bytes = file.getvalue()
                        prompt = f"You are an expert Indian Agronomist. Identify the disease, give 1 organic and 1 chemical remedy. Language: {lang}."
                        res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                        st.success("Analysis Complete!")
                        st.markdown(f"<div style='background:#f1f8e9; padding:20px; border-radius:10px;'>{res}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # === TAB 2: NEWS & SCHEMES ===
    with tabs[1]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📡 Live Government Updates")
            if st.button("Refresh Feed"):
                st.rerun()
            news_html = fetch_latest_schemes()
            st.markdown(news_html, unsafe_allow_html=True)
            
        with col2:
            st.markdown("### 🏛️ Famous Schemes")
            schemes = [
                {"name": "PM-KISAN", "desc": "₹6,000/year support."},
                {"name": "PMFBY", "desc": "Crop Insurance."},
                {"name": "Soil Health Card", "desc": "Free soil testing."}
            ]
            for s in schemes:
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:12px; margin-bottom:10px; border:1px solid #eee; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="margin:0; color:#1b5e20;">{s['name']}</h4>
                    <p style="margin:0; font-size:13px; color:#666;">{s['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

    # === TAB 3: CHAT ===
    with tabs[2]:
        st.markdown('<div class="feature-card" style="min-height:500px;">', unsafe_allow_html=True)
        st.subheader("💬 Ask GreenMitra")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"Namaste {name}! How can I help your farm today?"}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about seeds, weather, or fertilizer..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    system_prompt = f"Act as an Indian Agriculture Expert. Reply in {lang}. User Question: {prompt}"
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
                <p>Track your crop age and get timely advice.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            crop = st.selectbox("Select Crop", ["Wheat (गहू)", "Rice (तांदूळ)", "Cotton (कापूस)", "Sugarcane (ऊस)"])
            date = st.date_input("Sowing Date", datetime.date.today())
            
            days = (datetime.date.today() - date).days
            st.markdown(f"<h1 style='text-align:center; color:#2e7d32; font-size:60px; margin:0;'>{days}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Days Old</p>", unsafe_allow_html=True)
            
            if days < 20: st.info("🌱 Phase: Germination. Keep soil moist.")
            elif days < 60: st.success("🌿 Phase: Vegetative. Apply Nitrogen.")
            else: st.warning("🌾 Phase: Maturity. Prepare for harvest.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("""
    <div style="text-align:center; padding:30px; margin-top:50px; color:#888; border-top:1px solid #eee;">
        <p>© 2026 GreenMitra AI • Empowering Rural India</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
