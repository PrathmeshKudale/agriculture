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
    /* Chat Message Styling */
    .stChatMessage { background-color: rgba(255, 255, 255, 0.5); border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SMART AI ENGINE (THE FIX) ---
def get_ai_response(prompt, image=None):
    """
    Tries 'gemini-1.5-flash' first. 
    If it fails (404 Error), it automatically switches to 'gemini-pro'.
    """
    models_to_try = ['gemini-1.5-flash', 'gemini-pro']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            if image:
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # If it's the last model and still fails, return the error
            if model_name == models_to_try[-1]:
                return f"⚠️ System Error: {str(e)}"
            # Otherwise, continue to the next model (Silent Switch)
            continue

# --- 5. CORE FUNCTIONS ---
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

def analyze_crop(api_key, image_bytes, prompt):
    if not api_key: return "API Key Missing."
    try:
        image_parts = {"mime_type": "image/jpeg", "data": image_bytes}
        # Use the Smart Switcher here
        return get_ai_response(prompt, image_parts)
    except Exception as e: return f"Error: {e}"

# --- 6. CHATBOT LOGIC ---
def farmer_chatbot():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Namaste! I am GreenMitra AI. Ask me about your farm."}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # System Prompt
                system_prompt = f"Act as an Indian Agriculture Expert. Keep answers short and simple. User Question: {prompt}"
                
                # Use the Smart Switcher here
                ai_reply = get_ai_response(system_prompt)
                
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# --- 7. MAIN APP LAYOUT ---
def main():
    c1, c2 = st.columns([1, 4])
    with c1: st.write("## 🌿 AI")
    with c2: st.write("## GreenMitra: Next-Gen")
    
    tabs = st.tabs(["📸 Crop Doctor", "🚀 Live Schemes", "🤖 Ask AI (Chat)", "📅 Smart Planner"])

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
                        prompt = "You are an Agronomist. Identify the disease, give organic remedy, and chemical remedy. Keep it under 150 words."
                        res = analyze_crop(GOOGLE_API_KEY, img_bytes, prompt)
                        st.markdown(f'<div class="glass-card"><b>✅ Diagnosis:</b><br>{res}</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="glass-card"><h4>📡 Live Google News Radar</h4></div>', unsafe_allow_html=True)
        if st.button("🔄 Scan Google News"):
            with st.spinner("Scanning..."):
                latest_news = fetch_latest_schemes()
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)

        st.markdown("### 🏛️ Famous Schemes")
        schemes = [
            {"name": "PM-KISAN", "tag": "Income", "desc": "₹6,000/year for all farmers."},
            {"name": "PMFBY", "tag": "Insurance", "desc": "Crop insurance with low premium."},
            {"name": "Kisan Credit Card", "tag": "Loan", "desc": "Low interest loans (4%)."}
        ]
        for s in schemes:
            st.markdown(f"""<div class="glass-card" style="padding:15px; border-left:5px solid #2e7d32;">
                <h5>{s['name']} <span style="float:right; font-size:12px; background:#e8f5e9; padding:2px 5px;">{s['tag']}</span></h5>
                <p style="font-size:14px; margin:0;">{s['desc']}</p></div>""", unsafe_allow_html=True)

    with tabs[2]:
        st.markdown('<div class="glass-card"><h4>🤖 Farmer Chat Assistant</h4></div>', unsafe_allow_html=True)
        farmer_chatbot()

    with tabs[3]:
        st.markdown('<div class="glass-card"><h4>📅 Lifecycle Manager</h4></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton"])
        with c2: date = st.date_input("Sowing Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        st.metric("Crop Age", f"{days} Days")
        if days < 20: st.info("🌱 Stage: Germination.")
        elif days < 60: st.success("🌿 Stage: Vegetative.")
        else: st.warning("🌾 Stage: Harvest.")

if __name__ == "__main__":
    main()
    
