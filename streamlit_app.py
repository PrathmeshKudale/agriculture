import streamlit as st
import google.generativeai as genai
import requests
import feedparser
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
from gtts import gTTS
import tempfile
import os
import base64
import json

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="GreenMitra AI Pro",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SETUP AI (Stable Version) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    AI_AVAILABLE = True
else:
    AI_AVAILABLE = False

# --- 3. MODERN UI STYLES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(120deg, #e0f2f1 0%, #a5d6a7 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #2e7d32, #43a047);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    
    .chat-user {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        text-align: right;
        color: #1565c0;
    }
    
    .chat-ai {
        background: white;
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        border-left: 5px solid #2e7d32;
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. INTELLIGENT FUNCTIONS ---

def get_ai_response(prompt, lang="English", image=None):
    """The Brain: Connects to Gemini and Translates"""
    if not AI_AVAILABLE:
        return "⚠️ AI Key Missing. Please check secrets.toml."
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # FORCE LANGUAGE INSTRUCTION
        system_instruction = f"You are GreenMitra, an expert Indian Agriculture Consultant. Reply in {lang} language. Keep answers short, practical, and helpful for farmers."
        
        full_prompt = [system_instruction, prompt]
        
        if image:
            full_prompt.append(image)
            
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def text_to_audio(text, lang_name):
    """The Voice: Speaks in the correct accent"""
    try:
        # Map full name to code
        code_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta"}
        lang_code = code_map.get(lang_name, "en")
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            with open(fp.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
        os.unlink(fp.name)
        
        # Embed Audio Player
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
            <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 5. MAIN APP UI ---

def main():
    # --- SIDEBAR (Settings) ---
    with st.sidebar:
        st.title("🌾 GreenMitra Pro")
        
        # LANGUAGE SELECTOR (Crucial for your fix)
        selected_lang = st.selectbox(
            "Select Language / भाषा", 
            ["English", "Marathi", "Hindi", "Tamil"]
        )
        
        st.divider()
        st.info("👨‍🌾 Farmer ID: P-1024")
        st.success("🟢 Online Mode")

    # --- TAB NAVIGATION ---
    tabs = st.tabs(["💬 Chat (विचार)", "🩺 Doctor", "📈 Market", "💰 Profit"])

    # === TAB 1: CHAT ===
    with tabs[0]:
        st.markdown(f"### 🤖 Ask AI ({selected_lang})")
        
        # Chat History
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        for role, text in st.session_state.chat_history:
            css_class = "chat-user" if role == "User" else "chat-ai"
            st.markdown(f"<div class='{css_class}'><b>{role}:</b> {text}</div>", unsafe_allow_html=True)

        # Input
        user_query = st.chat_input("Ask a question...")
        
        if user_query:
            # 1. Show User Message
            st.session_state.chat_history.append(("User", user_query))
            st.rerun()

        # Process Response (After Rerun)
        if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "User":
            last_query = st.session_state.chat_history[-1][1]
            
            with st.spinner("Thinking..."):
                # Call AI with the SELECTED LANGUAGE
                ai_reply = get_ai_response(last_query, lang=selected_lang)
                
                # Add to History
                st.session_state.chat_history.append(("GreenMitra", ai_reply))
                
                # Show Response & Speak
                st.markdown(f"<div class='chat-ai'><b>GreenMitra:</b> {ai_reply}</div>", unsafe_allow_html=True)
                text_to_audio(ai_reply, selected_lang)

    # === TAB 2: CROP DOCTOR ===
    with tabs[1]:
        st.markdown("### 🩺 Plant Disease Detector")
        
        img_file = st.file_uploader("Upload Leaf Photo", type=["jpg", "png"])
        
        if img_file and st.button("Diagnose Disease"):
            img = Image.open(img_file)
            st.image(img, width=200, caption="Uploaded Image")
            
            with st.spinner("Scanning..."):
                # Pass Image + Language to AI
                diagnosis = get_ai_response(
                    f"Identify this plant disease and give remedy in {selected_lang}. Format as: Disease Name, Symptoms, Treatment.", 
                    lang=selected_lang, 
                    image=img
                )
                
                st.markdown(f"<div class='glass-card' style='border-left:5px solid red'>{diagnosis}</div>", unsafe_allow_html=True)
                text_to_audio(diagnosis, selected_lang)

    # === TAB 3: MARKET ===
    with tabs[2]:
        st.markdown("### 📈 Live Mandi Prices")
        # Dummy Data for UI (You can connect API later)
        data = {
            "Crop": ["Wheat", "Rice", "Cotton", "Soybean"],
            "Price (₹/Qtl)": [2125, 1950, 6200, 4800],
            "Trend": ["⬆️", "⬇️", "⬆️", "➖"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Chart
        fig = px.bar(df, x="Crop", y="Price (₹/Qtl)", color="Crop", title="Price Comparison")
        st.plotly_chart(fig, use_container_width=True)

    # === TAB 4: PROFIT ===
    with tabs[3]:
        st.markdown("### 💰 Smart Profit Calculator")
        
        c1, c2 = st.columns(2)
        with c1:
            acres = st.number_input("Land Size (Acres)", 1, 100, 5)
        with c2:
            budget = st.number_input("Budget (₹)", 1000, 500000, 20000)
            
        if st.button("Calculate Best Crop"):
            with st.spinner("Calculating..."):
                advice = get_ai_response(
                    f"I have {acres} acres land and ₹{budget} budget. Suggest the most profitable crop to grow right now in India. Explain why in {selected_lang}.",
                    lang=selected_lang
                )
                st.markdown(f"<div class='glass-card' style='border-left:5px solid green'>{advice}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
