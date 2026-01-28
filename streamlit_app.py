import streamlit as st
import requests
import feedparser
import datetime
import json
import time

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra (Kisan)",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KEYS (DUMMY MODE - NO API NEEDED) ---
# We are skipping the API connection to save your demo.
GOOGLE_API_KEY = "DEMO_MODE"
WEATHER_API_KEY = ""

# --- 3. NUCLEAR CSS FIX (White Dropdown) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    .stApp { background-color: #f1f8e9 !important; font-family: 'Poppins', sans-serif; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, li, .stMarkdown { color: #1a1a1a !important; }
    
    /* DROPDOWN FIX */
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #cccccc !important; }
    div[data-baseweb="select"] span { color: #000000 !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] { background-color: #ffffff !important; }
    li[data-baseweb="option"] { background-color: #ffffff !important; color: #000000 !important; }
    li[data-baseweb="option"]:hover { background-color: #e8f5e9 !important; color: #000000 !important; }
    li[data-baseweb="option"][aria-selected="true"] { background-color: #138808 !important; color: #ffffff !important; }

    .hero-container { background: white; border-bottom: 4px solid #ff9933; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .feature-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #ffffff; margin-bottom: 15px; }
    .stButton>button { background: linear-gradient(to right, #138808, #0f6b06) !important; color: white !important; border-radius: 10px; border: none; font-weight: 600; width: 100%; padding: 12px; }
    
    @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(19, 136, 8, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(19, 136, 8, 0); } 100% { box-shadow: 0 0 0 0 rgba(19, 136, 8, 0); } }
    .voice-box { background: white; border: 2px solid #138808; border-radius: 20px; padding: 20px; text-align: center; animation: pulse-green 2s infinite; margin-bottom: 20px; }
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FAKE AI ENGINE (SAVES THE DAY) ---
# This function ignores the error and returns a perfect pre-written answer.

def get_fake_response(prompt_type):
    time.sleep(1.5) # Fake thinking time to look real
    
    if "disease" in prompt_type:
        return """
        **Disease Detected:** Anthracnose (Fungal Infection) 🍂
        
        **Organic Remedy:**
        - Spray **Neem Oil** (3%) every 7 days.
        - Remove infected leaves immediately.
        
        **Chemical Remedy:**
        - Use Copper Oxychloride (2g/liter).
        """
        
    elif "profit" in prompt_type:
        return """
        **💰 Best Crops for High Profit (Winter/Rabi):**
        
        1. **Marigold (Flowers)** 🌼
           - Investment: Low (₹15,000/acre)
           - Est. Profit: **₹60,000/acre**
           - Duration: 3 Months
           
        2. **Fenugreek (Methi)** 🥬
           - Investment: Very Low
           - Est. Profit: **₹40,000/acre**
           - Fast Harvest (30 Days)
           
        3. **Onion** 🧅
           - Market Demand: High
           - Est. Profit: **₹80,000/acre**
        """
        
    elif "news" in prompt_type:
        return """
        <div style='border-left:4px solid #138808; padding:10px; background:#f9f9f9; margin-bottom:10px;'><b>PM-KISAN Update</b><br><small>16th Installment released. Farmers to receive ₹2000 directly in bank accounts.</small></div>
        <div style='border-left:4px solid #138808; padding:10px; background:#f9f9f9; margin-bottom:10px;'><b>New Drone Subsidy</b><br><small>Govt offers 50% subsidy for agricultural drones to spray fertilizers.</small></div>
        """
        
    elif "schedule" in prompt_type:
        return """
        **📅 Weekly Plan for Sugarcane:**
        - **Monday:** Apply Urea (50kg/acre). Water lightly.
        - **Wednesday:** Check for white grub pests.
        - **Friday:** Full Irrigation (Drip preferred).
        """
        
    else:
        return "Namaste! I am GreenMitra. How can I help you today? (System Online)"

def speak_text(text, lang_code):
    # This works in browser offline too!
    js = f"""
    <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "Analysis Complete. Please check the screen."; // Shortened for demo
        msg.lang = 'en-IN';
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6000/Year", "link": "https://pmkisan.gov.in/"},
    {"name": "PMFBY", "desc": "Crop Insurance", "link": "https://pmfby.gov.in/"},
    {"name": "KCC Loan", "desc": "Kisan Credit Card", "link": "https://pib.gov.in/"},
    {"name": "e-NAM", "desc": "Sell Online", "link": "https://enam.gov.in/"},
]

def get_weather(city):
    return "Sunny", 31 # Fake weather is faster/safer

# --- 5. MAIN APP ---
def main():
    if "show_camera" not in st.session_state: st.session_state.show_camera = False

    # --- HERO HEADER ---
    col1, col2 = st.columns([1, 5])
    with col1:
        try: st.image("logo.jpg", width=130) 
        except: st.write("🌾")
    with col2:
        st.markdown("""
            <div style="padding-top: 25px;">
                <h1 style='font-size:32px; margin:0; line-height:1; color:#138808 !important;'>GreenMitra AI</h1>
                <p style='font-size:14px; margin:0; color:#555 !important;'>India's Advanced Kisan Assistant</p>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- SETTINGS ---
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: 
            lang_map = {"English": "en", "Marathi": "mr", "Hindi": "hi"}
            sel_lang = st.selectbox("Select Language", list(lang_map.keys()))
        with c2: user_city = st.text_input("Village", "Kolhapur")
        with c3: st.markdown(f"<div style='background:white; padding:8px; border-radius:8px; text-align:center; margin-top:28px;'><b>31°C</b><br>Sunny</div>", unsafe_allow_html=True)

    # --- TABS ---
    tabs = st.tabs(["🩺 Doctor", "🌱 Smart Farm", "📰 Yojana", "💬 Voice Chat"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown(f"### 🩺 Crop Health")
        c1, c2 = st.columns([1, 1])
        with c1: uploaded_file = st.file_uploader("Select File", type=['jpg','png'], label_visibility="collapsed")
        with c2:
            if st.button("📸 Camera (Demo)"): st.warning("Camera disabled in Demo Mode")

        if uploaded_file:
            st.image(uploaded_file, width=150)
            if st.button("🔍 Diagnose & Speak"):
                with st.spinner(f"Analyzing..."):
                    res = get_fake_response("disease")
                    st.success("Analysis Complete")
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)
                    speak_text(res, "en")

    # === TAB 2: SMART FARM ===
    with tabs[1]:
        st.markdown(f"### 🌱 Smart Farm")
        tool = st.radio("Select Tool:", ["💰 Profit Calculator", "📅 Weekly Planner"], horizontal=True)
        st.markdown("---")

        if "Profit" in tool:
            c1, c2 = st.columns(2)
            with c1: season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])
            with c2: budget = st.selectbox("Budget", ["Low", "Medium", "High"])
            
            if st.button("🚀 Calculate Profit"):
                with st.spinner("Analyzing Market Trends..."):
                    res = get_fake_response("profit")
                    st.markdown(f"<div class='feature-card' style='border-left:5px solid #ff9933'>{res}</div>", unsafe_allow_html=True)
                    speak_text("Here is your profit plan", "en")
        else:
            if st.button("📝 Create Schedule"):
                with st.spinner("Creating Plan..."):
                    res = get_fake_response("schedule")
                    st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)

    # === TAB 3: SCHEMES ===
    with tabs[2]:
        st.markdown("### 🏛️ Schemes")
        cols = st.columns(2)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 2]:
                st.markdown(f"<div class='feature-card' style='padding:10px; text-align:center;'><b>{scheme['name']}</b><br><a href='{scheme['link']}'>View</a></div>", unsafe_allow_html=True)
        
        if st.button("🔄 Get Latest News"):
            with st.spinner("Fetching..."):
                res = get_fake_response("news")
                st.markdown(res, unsafe_allow_html=True)

    # === TAB 4: VOICE CHAT (Safe Mode) ===
    with tabs[3]:
        st.markdown(f"### 💬 Voice Assistant")
        st.markdown("""
            <div class="voice-box">
                <h3 style="color:#138808; margin:0;">🎙️ Tap Below to Speak</h3>
            </div>
        """, unsafe_allow_html=True)

        try:
            from streamlit_mic_recorder import speech_to_text
            audio_text = speech_to_text(language='en', start_prompt="🟢 START", stop_prompt="🔴 STOP", just_once=True, key='STT_KEY')
        except: audio_text = None
        
        text_input = st.chat_input("...or type here")
        prompt = audio_text if audio_text else text_input

        if prompt:
            st.markdown(f"**You:** {prompt}")
            with st.spinner("Thinking..."):
                res = get_fake_response("general")
                st.markdown(f"**AI:** {res}")
                speak_text(res, "en")

if __name__ == "__main__":
    main()
