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
    initial_sidebar_state="expanded" # Sidebar is back!
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

# --- 3. MODERN UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%); }
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown, .stText { color: #000000 !important; }
    .stTextInput > div > div > input { color: black !important; background-color: white !important; }
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 25px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2e7d32 0%, #43a047 100%);
        color: white !important;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); }
    .stChatMessage { background-color: rgba(255, 255, 255, 0.5); border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SMART FUNCTIONS (Auto-Model + Weather) ---
def get_working_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        for model in available_models:
            if 'flash' in model: return model
        if available_models: return available_models[0]
    except: pass
    return "models/gemini-1.5-flash"

def get_ai_response(prompt, image=None):
    model_name = get_working_model()
    try:
        model = genai.GenerativeModel(model_name)
        if image: return model.generate_content([prompt, image]).text
        else: return model.generate_content(prompt).text
    except Exception as e: return f"⚠️ Error: {str(e)}"

def get_weather(city):
    if not WEATHER_API_KEY: return "Unavailable", 25
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data['weather'][0]['main'], data['main']['temp']
    except: pass
    return "Clear", 25

def fetch_latest_schemes():
    try:
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        news_items = []
        if feed.entries:
            for entry in feed.entries[:5]:
                clean_title = entry.title.split(" - ")[0]
                news_items.append(f"🔹 **{clean_title}**\n*Source: {entry.source.title}* | [Read More]({entry.link})")
        if news_items: return "### 📢 Latest News (Live Feed)\n\n" + "\n\n".join(news_items)
    except: pass
    return "No recent updates found."

# --- 5. MAIN APP LAYOUT ---
def main():
    # --- SIDEBAR (RESTORED) ---
    with st.sidebar:
        st.title("👤 Farmer Profile")
        st.write("Set your location and language here.")
        
        name = st.text_input("Your Name", "Farmer")
        city = st.text_input("Village/City", "Kolhapur")
        
        # Language Selector
        lang = st.selectbox("Language / भाषा", ["English", "Marathi", "Hindi"])
        
        st.markdown("---")
        
        # Weather Display in Sidebar
        w_cond, w_temp = get_weather(city)
        st.markdown(f"""
        <div style="background:#e8f5e9; padding:15px; border-radius:10px; border:1px solid #2e7d32;">
            <h3 style="margin:0; color:#1b5e20;">📍 {city}</h3>
            <h2 style="margin:0; color:#2e7d32;">{w_temp}°C</h2>
            <p style="margin:0;">{w_cond}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # --- MAIN CONTENT ---
    c1, c2 = st.columns([1, 4])
    with c1: st.write("## 🌿 AI")
    with c2: st.write(f"## GreenMitra: Welcome, {name}")
    
    tabs = st.tabs(["📸 Crop Doctor", "🚀 Live Schemes", "🤖 Ask AI (Chat)", "📅 Smart Planner"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown('<div class="glass-card"><h4>🩺 AI Plant Diagnosis</h4></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            mode = st.radio("Select Input", ["Upload File", "Camera"], horizontal=True)
            file = None
            if mode == "Camera": file = st.camera_input("Scan Leaf")
            else: file = st.file_uploader("Upload Image", type=['jpg','png'])
        with col2:
            if file:
                st.image(file, width=200)
                if st.button("Diagnose Now"):
                    with st.spinner("AI is analyzing..."):
                        img_bytes = file.getvalue()
                        image_parts = {"mime_type": "image/jpeg", "data": img_bytes}
                        # Pass Language to Prompt
                        prompt = f"You are an Agronomist. Identify the disease, give remedy. Language: {lang}. Keep it under 150 words."
                        res = get_ai_response(prompt, image_parts)
                        st.markdown(f'<div class="glass-card"><b>✅ Report ({lang}):</b><br>{res}</div>', unsafe_allow_html=True)

    # === TAB 2: NEWS ===
    with tabs[1]:
        st.markdown('<div class="glass-card"><h4>📡 Live Google News Radar</h4></div>', unsafe_allow_html=True)
        if st.button("🔄 Scan Google News"):
            with st.spinner("Scanning..."):
                latest_news = fetch_latest_schemes()
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)

        st.markdown("### 🏛️ Famous Schemes")
        schemes = [{"name": "PM-KISAN", "desc": "₹6,000/year income support."}, {"name": "PMFBY", "desc": "Crop insurance scheme."}, {"name": "KCC", "desc": "Low interest Kisan Credit Card loans."}]
        for s in schemes:
            st.markdown(f"""<div class="glass-card" style="padding:10px; border-left:5px solid #2e7d32;"><h5>{s['name']}</h5><p>{s['desc']}</p></div>""", unsafe_allow_html=True)

    # === TAB 3: CHATBOT ===
    with tabs[2]:
        st.markdown('<div class="glass-card"><h4>🤖 Farmer Chat Assistant</h4></div>', unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"Namaste! Ask me in {lang}."}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about seeds, fertilizer..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Pass Language to Chatbot Prompt
                    system_prompt = f"Act as an Indian Agriculture Expert. Reply in {lang} language. User Question: {prompt}"
                    ai_reply = get_ai_response(system_prompt)
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    # === TAB 4: PLANNER ===
    with tabs[3]:
        st.markdown('<div class="glass-card"><h4>📅 Lifecycle Manager</h4></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton", "Sugarcane"])
        with c2: date = st.date_input("Sowing Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        st.metric("Crop Age", f"{days} Days")
        if days < 20: st.info("🌱 Stage: Germination.")
        elif days < 60: st.success("🌿 Stage: Vegetative.")
        else: st.warning("🌾 Stage: Harvest.")

if __name__ == "__main__":
    main()
