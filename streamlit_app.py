import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
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

# --- 3. THE "FUTURISTIC AI" CSS (HTML/CSS ENGINE) ---
st.markdown("""
    <style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* GLOBAL RESET */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(153,94%,26%,0.2) 0px, transparent 50%),
            radial-gradient(at 100% 0%, hsla(153,94%,26%,0.2) 0px, transparent 50%);
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }
    
    p, label, .stMarkdown {
        color: #b0b0b0 !important;
        font-size: 1.1rem;
    }

    /* 3D GLASS CARDS */
    .glass-card {
        background: rgba(20, 20, 20, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 24px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }

    /* 3D HOVER EFFECT */
    .glass-card:hover {
        transform: translateY(-5px) scale(1.01);
        border: 1px solid rgba(0, 255, 136, 0.4);
        box-shadow: 0 20px 50px -10px rgba(0, 255, 136, 0.15);
    }

    /* GLOWING BUTTONS */
    .stButton>button {
        background: transparent;
        border: 2px solid #00ff88;
        color: #00ff88 !important;
        border-radius: 12px;
        padding: 15px 30px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
        width: 100%;
    }

    .stButton>button:hover {
        background: #00ff88;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
        transform: translateY(-2px);
    }

    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1f1f1f;
    }

    /* INPUT FIELDS */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333;
        border-radius: 10px;
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: #111;
        border: 1px solid #222;
        border-radius: 15px;
        transition: transform 0.2s;
    }
    .stChatMessage:hover {
        transform: translateX(5px);
        border-color: #00ff88;
    }
    
    /* ANIMATION PULSE */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
    .pulse-icon {
        animation: pulse-green 2s infinite;
        border-radius: 50%;
    }
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
    if not WEATHER_API_KEY: return "Offline", 25
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
            for entry in feed.entries[:5]:
                clean_title = entry.title.split(" - ")[0]
                news_items.append(f"🟢 **{clean_title}**\n*Source: {entry.source.title}* | [View]({entry.link})")
        if news_items: return "### ⚡ Live Intelligence Feed\n\n" + "\n\n".join(news_items)
    except: pass
    return "No live signal. Using backup database."

# --- 5. APP LAYOUT ---
def main():
    # SIDEBAR
    with st.sidebar:
        st.markdown("## 👤 COMMAND CENTER")
        name = st.text_input("Operator Name", "Farmer")
        city = st.text_input("Target Location", "Kolhapur")
        lang = st.selectbox("System Language", ["English", "Marathi", "Hindi"])
        
        st.markdown("---")
        w_cond, w_temp = get_weather(city)
        st.markdown(f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #00ff88; text-align:center;">
            <h3 style="margin:0; font-size:24px;">{w_temp}°C</h3>
            <p style="margin:0; color:#00ff88 !important; text-transform:uppercase; letter-spacing:2px;">{w_cond}</p>
            <p style="font-size:12px; margin-top:5px;">📍 {city} Sector</p>
        </div>
        """, unsafe_allow_html=True)

    # HEADER
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0;">GREENMITRA AI</h1>
        <p style="font-size: 1.2rem; color: #00ff88 !important; letter-spacing: 3px; text-transform: uppercase;">Next-Gen Agricultural Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # TABS
    tabs = st.tabs(["🧬 CROP DIAGNOSTICS", "📡 LIVE RADAR", "🤖 NEURAL CHAT", "📅 TACTICAL PLANNER"])

    # TAB 1: DIAGNOSIS
    with tabs[0]:
        st.markdown('<div class="glass-card"><h3>🧬 AI Visual Analysis</h3><p>Upload bio-sample for instant neural diagnosis.</p></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            mode = st.radio("Input Source", ["Upload File", "Camera"], horizontal=True)
            file = st.camera_input("Scan Bio-Sample") if mode == "Camera" else st.file_uploader("Upload Data", type=['jpg','png'])
        with c2:
            if file:
                st.image(file, width=250, caption="Sample Acquired")
                if st.button("INITIATE SCAN"):
                    with st.spinner("PROCESSING NEURAL NETWORKS..."):
                        img_bytes = file.getvalue()
                        prompt = f"Expert Agronomist. Identify disease, remedy. Language: {lang}. Short format."
                        res = get_ai_response(prompt, {"mime_type": "image/jpeg", "data": img_bytes})
                        st.markdown(f'<div class="glass-card" style="border-color:#00ff88;"><h4>✅ ANALYSIS COMPLETE</h4>{res}</div>', unsafe_allow_html=True)

    # TAB 2: NEWS
    with tabs[1]:
        st.markdown('<div class="glass-card"><h3>📡 Government Uplink</h3><p>Scanning frequency for latest schemes...</p></div>', unsafe_allow_html=True)
        if st.button("ACTIVATE RADAR"):
            with st.spinner("ESTABLISHING UPLINK..."):
                latest_news = fetch_latest_schemes()
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)
        
        st.markdown("### 💾 Offline Database")
        schemes = [{"name": "PM-KISAN", "id": "UID-01"}, {"name": "PMFBY", "id": "UID-02"}, {"name": "KCC", "id": "UID-03"}]
        c1, c2, c3 = st.columns(3)
        for idx, s in enumerate(schemes):
            with [c1, c2, c3][idx]:
                st.markdown(f"""<div class="glass-card" style="text-align:center;">
                    <h4 style="color:#00ff88;">{s['name']}</h4>
                    <p style="font-size:12px;">ID: {s['id']}</p>
                </div>""", unsafe_allow_html=True)

    # TAB 3: CHAT
    with tabs[2]:
        st.markdown('<div class="glass-card"><h3>🤖 Neural Assistant Interface</h3></div>', unsafe_allow_html=True)
        if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "System Online. Awaiting queries."}]
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("Enter Command..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("COMPUTING..."):
                    ai_reply = get_ai_response(f"Expert Agronomist. Lang: {lang}. Q: {prompt}")
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # TAB 4: PLANNER
    with tabs[3]:
        st.markdown('<div class="glass-card"><h3>📅 Lifecycle Monitor</h3></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: crop = st.selectbox("Target Organism", ["Wheat", "Rice", "Cotton"])
        with c2: date = st.date_input("Inception Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        st.metric("Organism Age", f"{days} Cycles")
        status = "🟢 OPTIMAL" if days < 60 else "🔴 HARVEST READY"
        st.markdown(f'<div class="glass-card" style="text-align:center;"><h1>{status}</h1></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
