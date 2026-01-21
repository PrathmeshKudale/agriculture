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

# --- 4. CORE FUNCTIONS (News, Weather, Image) ---
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
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
        response = model.generate_content([prompt, image_parts[0]])
        return response.text
    except Exception as e: return f"Error: {e}"

# --- 5. CHATBOT LOGIC (THE NEW PART) ---
def farmer_chatbot():
    # 1. Initialize Chat History if not present
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Namaste! I am GreenMitra AI. Ask me anything about farming, seeds, or diseases."}
        ]

    # 2. Display Previous Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Handle New User Input
    if prompt := st.chat_input("Type your question here (e.g., Best fertilizer for rice?)..."):
        # Add User Message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # STRICT SYSTEM INSTRUCTION FOR FARMER BOT
                    system_prompt = f"""
                    You are 'GreenMitra', an expert Indian Agriculture Assistant.
                    - Answer ONLY farming-related questions (Crops, Diseases, Weather, Government Schemes).
                    - If the user asks about movies, cricket, or politics, politely say you only know farming.
                    - Keep answers SIMPLE, short, and practical for a farmer.
                    - User Question: {prompt}
                    """
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(system_prompt)
                    ai_reply = response.text
                    
                    st.markdown(ai_reply)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                except Exception as e:
                    st.error("Network Error. Please try again.")

# --- 6. MAIN APP LAYOUT ---
def main():
    c1, c2 = st.columns([1, 4])
    with c1: st.write("## 🌿 AI")
    with c2: st.write("## GreenMitra: Next-Gen")
    
    # ADDED THE 4TH TAB HERE
    tabs = st.tabs(["📸 Crop Doctor", "🚀 Live Schemes", "🤖 Ask AI (Chat)", "📅 Smart Planner"])

    # === TAB 1: CROP DOCTOR ===
    with tabs[0]:
        st.markdown('<div class="glass-card"><h4>🩺 AI Plant Diagnosis</h4><p>Upload a leaf photo.</p></div>', unsafe_allow_html=True)
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
                    with st.spinner("AI is analyzing..."):
                        img_bytes = file.getvalue()
                        prompt = "You are an Agronomist. Identify the disease, give organic remedy, and chemical remedy. Keep it under 150 words."
                        res = analyze_crop(GOOGLE_API_KEY, img_bytes, prompt)
                        st.markdown(f'<div class="glass-card"><b>✅ Diagnosis:</b><br>{res}</div>', unsafe_allow_html=True)

    # === TAB 2: LIVE SCHEMES ===
    with tabs[1]:
        st.markdown('<div class="glass-card"><h4>📡 Live Google News Radar</h4></div>', unsafe_allow_html=True)
        if st.button("🔄 Scan Google News"):
            with st.spinner("Scanning..."):
                latest_news = fetch_latest_schemes()
                st.markdown(f'<div class="glass-card">{latest_news}</div>', unsafe_allow_html=True)
                
       # --- REPLACING THE OLD SCHEMES LIST WITH THIS BIG DATABASE ---
        st.markdown("### 🏛️ Active Schemes Database (All India)")
        
        schemes = [
            {
                "name": "PM-KISAN Samman Nidhi", 
                "tag": "Central Govt", 
                "desc": "₹6,000 per year income support for all landholding farmers (paid in 3 installments)."
            },
            {
                "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)", 
                "tag": "Insurance", 
                "desc": "Crop insurance scheme with lowest premium (2% for Kharif, 1.5% for Rabi) against natural calamities."
            },
            {
                "name": "Kisan Credit Card (KCC)", 
                "tag": "Loan / Credit", 
                "desc": "Short-term credit for crops at low interest rates (4% if repaid timely)."
            },
            {
                "name": "Namo Shetkari MahaSanman Nidhi", 
                "tag": "Maharashtra", 
                "desc": "Additional ₹6,000 per year specifically for farmers in Maharashtra (Total ₹12k with PM-KISAN)."
            },
            {
                "name": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)", 
                "tag": "Irrigation", 
                "desc": "Subsidies for drip/sprinkler irrigation systems. Motto: 'Har Khet Ko Pani'."
            },
            {
                "name": "Soil Health Card Scheme", 
                "tag": "Soil Health", 
                "desc": "Free soil testing and report card to help farmers choose the right fertilizers."
            },
            {
                "name": "e-NAM (National Agriculture Market)", 
                "tag": "Market / Mandi", 
                "desc": "Online trading platform to sell crops to buyers across India for better prices."
            },
            {
                "name": "Paramparagat Krishi Vikas Yojana (PKVY)", 
                "tag": "Organic Farming", 
                "desc": "Financial assistance of ₹50,000 per hectare for adopting organic farming."
            }
        ]
        
        # Displaying them in cards
        for s in schemes:
            st.markdown(f"""
            <div class="glass-card" style="padding: 15px; border-left: 5px solid #2e7d32;">
                <h5 style="margin:0;">{s['name']} 
                    <span style="background:#e8f5e9; padding:2px 8px; border-radius:10px; font-size:12px; border: 1px solid #2e7d32; float:right;">{s['tag']}</span>
                </h5>
                <p style="margin:5px 0 0 0; font-size:14px; color:#333 !important;">{s['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    # === TAB 3: AI CHATBOT (NEW FEATURE) ===
    with tabs[2]:
        st.markdown('<div class="glass-card"><h4>🤖 Farmer Chat Assistant</h4><p>Chat with AI about your farm problems.</p></div>', unsafe_allow_html=True)
        # This runs the chatbot function we created above
        farmer_chatbot()

    # === TAB 4: PLANNER ===
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
