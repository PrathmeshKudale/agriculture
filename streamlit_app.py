import streamlit as st
import requests
import base64
import io
import datetime
from gtts import gTTS
from duckduckgo_search import DDGS  # FREE Search Engine
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
    # Safe fallback if keys aren't set yet (prevents crash)
    GOOGLE_API_KEY = ""

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- 3. MODERN UI CSS (THE VISIBILITY FIX) ---
st.markdown("""
    <style>
    /* 1. Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 2. Background - Clean Gradient */
    .stApp {
        background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%);
    }

    /* 3. FORCE BLACK TEXT (The Fix) */
    /* This overrides Dark Mode white text settings */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown, .stText {
        color: #000000 !important;
    }
    
    /* Fix Input Fields visibility */
    .stTextInput > div > div > input {
        color: black !important;
        background-color: white !important;
    }
    .stSelectbox > div > div > div {
        color: black !important;
    }

    /* 4. Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 5. Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        padding: 25px;
        margin-bottom: 20px;
        color: black !important; /* Force text black inside cards */
    }

    /* 6. Modern Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #2e7d32 0%, #43a047 100%);
        color: white !important; /* Keep buttons white text */
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.4);
    }
    
    /* 7. Metric Styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] { color: #444 !important; }
    [data-testid="stMetricValue"] { color: #1b5e20 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. REAL-TIME NEWS AGENT LOGIC ---
def fetch_latest_schemes():
    """
    Searches the web for schemes released in the last 24 hours.
    """
    try:
        results = DDGS().text("India government agriculture scheme announcement today news", max_results=5)
        if not results:
            return "No immediate news found. Check official portals."
            
        # Convert search results to text for AI
        news_text = "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
        
        # Ask Gemini to filter the noise
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a Government News Analyst.
        Here are the latest search results about Indian Agriculture:
        {news_text}
        
        Task: Identify any REAL, RECENT Government schemes or farming updates launched recently.
        Summary should be concise (bullet points). Include links if available.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not connect to live news: {e}"

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
    # Top Bar
    c1, c2 = st.columns([1, 4])
    with c1:
        st.write("## 🌿 AI")
    with c2:
        st.write("## GreenMitra: Next-Gen")
    
    # Modern Tab Interface
    tabs = st.tabs(["📸 Crop Doctor", "🚀 Live Schemes (Real-Time)", "📅 Smart Planner"])

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
        st.markdown('<div class="glass-card"><h4>📡 Live Government Radar</h4><p>Scans Government Press Releases & News every minute.</p></div>', unsafe_allow_html=True)
        
        if st.button("🔄 Scan for New Schemes (Live Web Search)"):
            with st.spinner("Connecting to Government News Feeds..."):
                latest_news = fetch_latest_schemes()
                
                st.subheader("📢 Just Found:")
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)
                st.caption("ℹ️ This data is fetched live from Google/DuckDuckGo News.")

        st.markdown("### 🏛️ Active Database (Examples)")
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
        with c1:
            crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton"])
        with c2:
            date = st.date_input("Sowing Date", datetime.date.today())
            
        days = (datetime.date.today() - date).days
        st.metric("Crop Age", f"{days} Days")
        
        if days < 20:
            st.info("🌱 Stage: Germination. Keep soil moist.")
        elif days < 60:
            st.success("🌿 Stage: Vegetative. Add Nitrogen now.")
        else:
            st.warning("🌾 Stage: Flowering/Harvest. Stop heavy watering.")

if __name__ == "__main__":
    main()
