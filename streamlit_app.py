import streamlit as st
import pymongo
import google.generativeai as genai
import requests
import feedparser
import datetime
import time
import json

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra Pro",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONNECT TO DATABASE & AI ---

# Setup AI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Setup Database (With Error Handling)
@st.cache_resource
def init_connection():
    try:
        return pymongo.MongoClient(st.secrets["mongo"]["uri"])
    except Exception as e:
        return None

client = init_connection()

# --- 3. DATABASE FUNCTIONS (Login Logic) ---

def login_user(phone):
    """Finds a user by phone number"""
    if client:
        db = client["GreenMitra_DB"]
        # .strip() removes accidental spaces!
        clean_phone = str(phone).strip()
        return db["farmers_data"].find_one({"phone": clean_phone})
    return None

def register_user(name, phone, village):
    """Creates a new user"""
    if client:
        db = client["GreenMitra_DB"]
        users = db["farmers_data"]
        # .strip() removes accidental spaces!
        clean_phone = str(phone).strip()
        
        # Check if already registered
        if users.find_one({"phone": clean_phone}):
            return False
            
        # Create new account
        users.insert_one({
            "name": name, 
            "phone": clean_phone, 
            "village": village, 
            "joined": time.strftime("%Y-%m-%d")
        })
        return True
    return False

def save_history(phone, action, details):
    """Saves farmer activity to history"""
    if client:
        db = client["GreenMitra_DB"]
        db["history"].insert_one({
            "phone": phone,
            "action": action,
            "details": details,
            "date": time.strftime("%Y-%m-%d")
        })

# --- 4. AI & HELPER FUNCTIONS ---

def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except: return "⚠️ AI is busy. Please try again."

def speak_text(text, lang='en-IN'):
    js = f"""<script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance({json.dumps(text)});
        msg.lang = '{lang}';
        window.speechSynthesis.speak(msg);
    </script>"""
    st.components.v1.html(js, height=0, width=0)

# --- 5. STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f8e9; }
    .feature-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .stButton>button { width: 100%; background-color: #138808; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 6. MAIN APP FLOW ---

# Initialize Session
if 'user' not in st.session_state: st.session_state.user = None

# === SCENE 1: LOGIN PAGE ===
if st.session_state.user is None:
    st.title("🌾 GreenMitra Pro")
    st.info("Please Login to access the AI Tools.")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register New Farmer"])
    
    # LOGIN TAB
    with tab1:
        st.subheader("Login")
        l_phone = st.text_input("Enter Mobile Number", key="login_phone")
        
        if st.button("Login"):
            user = login_user(l_phone)
            if user:
                st.session_state.user = user
                st.success("✅ Success! Loading...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ User not found. Please Register first.")

    # REGISTER TAB
    with tab2:
        st.subheader("New Registration")
        r_name = st.text_input("Full Name")
        r_phone = st.text_input("Mobile Number", key="reg_phone")
        r_village = st.text_input("Village Name")
        
        if st.button("Register"):
            if r_name and r_phone:
                success = register_user(r_name, r_phone, r_village)
                if success:
                    st.success("✅ Account Created! Go to Login tab.")
                else:
                    st.warning("⚠️ This number is already registered.")
            else:
                st.warning("Please fill all details.")

# === SCENE 2: DASHBOARD (Logged In) ===
else:
    user = st.session_state.user
    
    # Header
    c1, c2 = st.columns([4,1])
    with c1: 
        st.title(f"Namaste, {user['name']} 🙏")
        st.write(f"📍 {user['village']} | 📱 {user['phone']}")
    with c2:
        if st.button("Log Out"):
            st.session_state.user = None
            st.rerun()
            
    st.divider()
    
    # TABS
    tabs = st.tabs(["💰 Profit Calculator", "🩺 Crop Doctor", "📜 History", "💬 Voice Chat"])

    # TAB 1: PROFIT
    with tabs[0]:
        st.subheader("Smart Profit Calculator")
        season = st.selectbox("Season", ["Kharif", "Rabi", "Summer"])
        budget = st.selectbox("Budget", ["Low", "High"])
        
        if st.button("Calculate Best Crop"):
            with st.spinner("AI Thinking..."):
                prompt = f"Suggest 1 profitable crop for {season} season in {user['village']} with {budget} budget. Keep it short."
                res = get_ai_response(prompt)
                
                st.markdown(f"<div class='feature-card'>{res}</div>", unsafe_allow_html=True)
                speak_text(res)
                
                # Save to Database
                save_history(user['phone'], "Profit Calc", res)

    # TAB 2: CROP DOCTOR
    with tabs[1]:
        st.subheader("Crop Doctor")
        img = st.file_uploader("Upload Leaf", type=['jpg','png'])
        if img and st.button("Diagnose"):
            st.info("AI Analysis requires image setup (Added in full version)")
            save_history(user['phone'], "Diagnosis", "Image Analyzed")

    # TAB 3: HISTORY (Read from Database)
    with tabs[2]:
        st.subheader("Your Activity History")
        if client:
            db = client["GreenMitra_DB"]
            # Get last 5 actions
            history = list(db["history"].find({"phone": user['phone']}).limit(5))
            
            if history:
                for item in history:
                    st.markdown(f"**{item['date']}**: {item['action']}")
                    st.caption(str(item.get('details', ''))[:100] + "...")
                    st.divider()
            else:
                st.info("No history yet.")

    # TAB 4: VOICE
    with tabs[3]:
        st.subheader("Voice Assistant")
        q = st.chat_input("Ask anything...")
        if q:
            st.write(f"You: {q}")
            ans = get_ai_response(q)
            st.write(f"AI: {ans}")
            speak_text(ans)
