import streamlit as st
import pymongo
import google.generativeai as genai
import requests
import feedparser
import time
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GreenMitra 2.0", page_icon="🌾", layout="wide")

# --- 2. API SETUP (AI + DB) ---
# Connect AI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Connect Database
@st.cache_resource
def init_connection():
    try:
        return pymongo.MongoClient(st.secrets["mongo"]["uri"])
    except Exception as e:
        return None

client = init_connection()

# --- 3. DATABASE FUNCTIONS ---
def login_user(phone):
    if client:
        db = client["GreenMitra_DB"]
        return db["farmers_data"].find_one({"phone": phone})
    return None

def register_user(name, phone, village):
    if client:
        db = client["GreenMitra_DB"]
        users = db["farmers_data"]
        if users.find_one({"phone": phone}):
            return False
        users.insert_one({"name": name, "phone": phone, "village": village, "joined": time.strftime("%Y-%m-%d")})
        return True
    return False

def save_profit_calculation(phone, crop, profit):
    """Saves the AI result to the database!"""
    if client:
        db = client["GreenMitra_DB"]
        db["history"].insert_one({
            "phone": phone,
            "crop": crop,
            "profit": profit,
            "date": time.strftime("%Y-%m-%d")
        })

# --- 4. AI FUNCTIONS ---
def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except: return "⚠️ AI Server Busy. Try again."

def speak_text(text):
    js = f"""<script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance({json.dumps(text)});
        msg.lang = 'en-IN';
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js, height=0, width=0)

# --- 5. MAIN APP FLOW ---
if 'user' not in st.session_state: st.session_state.user = None

# === SCENE 1: LOGIN PAGE ===
if st.session_state.user is None:
    st.title("🌾 GreenMitra: Farmer Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        phone = st.text_input("Mobile Number", placeholder="98XXXXXXXX")
        if st.button("Login"):
            user = login_user(phone)
            if user:
                st.session_state.user = user
                st.success("Login Successful!")
                time.sleep(1)
                st.rerun()
            else: st.error("User not found.")

    with tab2:
        name = st.text_input("Full Name")
        reg_phone = st.text_input("Mobile (User ID)")
        village = st.text_input("Village")
        if st.button("Register"):
            if register_user(name, reg_phone, village): st.success("Registered! Go to Login.")
            else: st.error("User already exists.")

# === SCENE 2: THE DASHBOARD (LOGGED IN) ===
else:
    user = st.session_state.user
    
    # Header
    c1, c2 = st.columns([4,1])
    with c1: st.title(f"Namaste, {user['name']} 🙏")
    with c2: 
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
            
    st.info(f"📍 Village: {user['village']} | 📱 ID: {user['phone']}")

    # TABS
    tabs = st.tabs(["💰 Profit Calculator", "🩺 Crop Doctor", "📜 History"])

    # --- TAB 1: PROFIT CALCULATOR (With Database Save!) ---
    with tabs[0]:
        st.subheader("Smart Profit Calculator")
        c1, c2 = st.columns(2)
        with c1: season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])
        with c2: budget = st.selectbox("Budget", ["Low", "High"])
        
        if st.button("🚀 Calculate & Save"):
            with st.spinner("AI is thinking..."):
                # 1. Ask AI
                prompt = f"Suggest 1 profitable crop for Season: {season}, Budget: {budget}, Village: {user['village']}. Keep it short."
                result = get_ai_response(prompt)
                
                # 2. Show Result
                st.success("Analysis Complete")
                st.write(result)
                
                # 3. SAVE TO MONGODB (The Startup Feature)
                save_profit_calculation(user['phone'], "AI Recommendation", result)
                st.toast("✅ Saved to your History!")
                
                speak_text("I have found the best crop for you.")

    # --- TAB 2: CROP DOCTOR ---
    with tabs[1]:
        st.subheader("AI Crop Doctor")
        img = st.file_uploader("Upload Leaf Photo", type=['jpg','png'])
        if img and st.button("Diagnose"):
            st.write("🤖 Analysis: This is a demo diagnosis. (Add Image AI code here)")

    # --- TAB 3: HISTORY (DATABASE READING) ---
    with tabs[2]:
        st.subheader("📜 Your Saved Data")
        if client:
            db = client["GreenMitra_DB"]
            # Find data for THIS user only
            history = list(db["history"].find({"phone": user['phone']}))
            
            if history:
                for item in history:
                    with st.expander(f"📅 {item['date']} - Recommendation"):
                        st.write(item['profit'])
            else:
                st.info("No saved history yet. Go to Calculator!")
