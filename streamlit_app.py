import streamlit as st
import requests
import feedparser # We use this to read Google News
import datetime
import google.generativeai as genai
import base64
import io
from gtts import gTTS

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
    
    /* FORCE BLACK TEXT */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown, .stText {
        color: #000000 !important;
    }
    .stTextInput > div > div > input { color: black !important; background-color: white !important; }
    
    /* Cards */
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
    </style>
""", unsafe_allow_html=True)

# --- 4. GOOGLE NEWS RADAR (THE FIX) ---
# --- REPLACEMENT FUNCTION: CLEANER NEWS FEED ---

def fetch_latest_schemes():
    """
    Fetches LIVE news from Google News RSS.
    Includes a 'Beautiful Fallback' so it looks good even if AI fails.
    """
    news_items = []
    
    try:
        # Robust Google News URL
        feed_url = "https://news.google.com/rss/search?q=India+Agriculture+Schemes+Government+announce+launch+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            for entry in feed.entries[:5]: # Top 5 only
                clean_title = entry.title.split(" - ")[0]
                # Format as a clean Markdown list item
                news_items.append(f"🔹 **{clean_title}**\n*Source: {entry.source.title}* | [Read More]({entry.link})")
    except Exception as e:
        return f"⚠️ Connection Error: {e}"

    # Attempt AI Summarization
    try:
        if news_items:
            news_text = "\n".join([item.split("|")[0] for item in news_items]) # Send only text to AI, not links
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are a Farmer's News Anchor.
            Summarize these headlines into 3 short, exciting bullet points with emojis.
            Headlines: {news_text}
            """
            response = model.generate_content(prompt)
            return response.text
    except:
        pass # If AI fails, just use the beautiful raw list below

    # --- THE FIX: BEAUTIFUL FALLBACK ---
    # If AI fails (or key expires), show this clean list instead of a messy block.
    if news_items:
        return "### 📢 Latest News (Live Feed)\n\n" + "\n\n".join(news_items)
    
    return "No recent updates found."
    # If we found news, let AI summarize it
    if news_items:
        try:
            news_text = "\n".join(news_items)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are a Farmer's News Assistant.
            Here are the latest news headlines from Google News:
            {news_text}
            
            Task:
            1. Filter out political noise. Keep only REAL Scheme Updates.
            2. Summarize the top 3 most important updates for a farmer.
            3. Use Emoji bullet points.
            """
            response = model.generate_content(prompt)
            return response.text
        except:
            return "\n".join(news_items) # Fallback to raw list

    # Fail-Safe (If Google News returns nothing)
    return """
    **📡 Updates (Cached):**
    * **PM-KISAN:** 19th/20th Installment release date discussions are active.
    * **Kisan Credit Card:** New digital drive launched to issue KCC to dairy farmers.
    * **Digital Crop Survey:** Started in 12 states to help settle insurance claims faster.
    """

# --- 5. CORE FUNCTIONS ---
def get_weather(city):
    if not WEATHER_API_KEY: return "Unavailable", 25
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return data['weather'][0]['main'], data['main']['temp']
    except:
        pass
    return "Clear", 25

def analyze_crop(api_key, image_bytes, prompt):
    if not api_key: return "API Key Missing. Check Secrets."
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
        response = model.generate_content([prompt, image_parts[0]])
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- 6. MAIN APP LAYOUT ---
def main():
    c1, c2 = st.columns([1, 4])
    with c1: st.write("## 🌿 AI")
    with c2: st.write("## GreenMitra: Next-Gen")
    
    tabs = st.tabs(["📸 Crop Doctor", "🚀 Live Schemes (Google News)", "📅 Smart Planner"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown('<div class="glass-card"><h4>🩺 AI Plant Diagnosis</h4><p>Upload a leaf photo. Get results in 5 seconds.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            mode = st.radio("Select Input", ["Upload File", "Camera"], horizontal=True)
            file = None
            if mode == "Camera": file = st.camera_input("Scan Leaf")
            else: file = st.file_uploader("Upload Image", type=['jpg','png'])
        with col2:
            if file:
                st.image(file, use_column_width=True, caption="Analyzing...")
                if st.button("Diagnose Now"):
                    with st.spinner("AI is analyzing leaf texture..."):
                        img_bytes = file.getvalue()
                        prompt = "You are an Agronomist. Identify the disease, give organic remedy, and chemical remedy. Keep it under 150 words."
                        res = analyze_crop(GOOGLE_API_KEY, img_bytes, prompt)
                        st.markdown(f'<div class="glass-card"><b>✅ Diagnosis:</b><br>{res}</div>', unsafe_allow_html=True)

    # === TAB 2: LIVE REAL-TIME SCHEMES ===
    with tabs[1]:
        st.markdown('<div class="glass-card"><h4>📡 Live Google News Radar</h4><p>Scans Google News (India Edition) for the last 30 days.</p></div>', unsafe_allow_html=True)
        
        if st.button("🔄 Scan Google News (Live)"):
            with st.spinner("Scanning Google News Network..."):
                latest_news = fetch_latest_schemes()
                st.subheader("📢 Latest Headlines:")
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)
                st.caption("ℹ️ Source: Google News RSS (India/Agriculture).")

        st.markdown("### 🏛️ Active Schemes Database")
        schemes = [
            {"name": "PM-KISAN", "tag": "Income Support", "desc": "₹6,000/year for all farmers."},
            {"name": "Namo Shetkari", "tag": "Maharashtra", "desc": "Additional ₹6,000/year for MH farmers."},
        ]
        for s in schemes:
            st.markdown(f"""
            <div class="glass-card" style="padding: 15px; border-left: 5px solid #2e7d32;">
                <h5 style="margin:0;">{s['name']} <span style="background:#e8f5e9; padding:2px 8px; border-radius:10px; font-size:12px; border: 1px solid #2e7d32;">{s['tag']}</span></h5>
                <p style="margin:5px 0 0 0; font-size:14px;">{s['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    # === TAB 3: SMART PLANNER ===
    with tabs[2]:
        st.markdown('<div class="glass-card"><h4>📅 Crop Lifecycle Manager</h4></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton"])
        with c2: date = st.date_input("Sowing Date", datetime.date.today())
        days = (datetime.date.today() - date).days
        st.metric("Crop Age", f"{days} Days")
        if days < 20: st.info("🌱 Stage: Germination. Keep soil moist.")
        elif days < 60: st.success("🌿 Stage: Vegetative. Add Nitrogen now.")
        else: st.warning("🌾 Stage: Flowering/Harvest. Stop heavy watering.")

if __name__ == "__main__":
    main()
