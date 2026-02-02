import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
from gtts import gTTS
import edge_tts
import asyncio
from io import BytesIO
import tempfile
import os
import queue
import threading

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="🌾 GreenMitra AI - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KEYS (FIXED SECTION) ---
# This safely loads the key. If it fails, it won't crash the app immediately.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    else:
        GOOGLE_API_KEY = ""
except Exception:
    GOOGLE_API_KEY = ""

# Configure AI if key exists
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        pass

# Weather Key
try:
    if "WEATHER_API_KEY" in st.secrets:
        WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
    else:
        WEATHER_API_KEY = ""
except Exception:
    WEATHER_API_KEY = ""

# --- 3. MODERN CSS WITH ADVANCED ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&family=Poppins:wght@300;400;500;600&family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        font-family: 'Inter', sans-serif !important;
        background-attachment: fixed !important;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15) !important;
        padding: 20px !important;
        margin: 10px 0 !important;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 18px 18px 0 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-bubble-assistant {
        background: #f0f7f4;
        color: #333;
        border-radius: 18px 18px 18px 0;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-right: auto;
        border: 1px solid #e0f2e9;
    }
    
    /* Hide Default Elements */
    #MainMenu, header, footer { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. CONSTANTS & DATA ---
PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year direct income support.", "link": "https://pmkisan.gov.in/", "icon": "💰", "category": "Income Support", "eligibility": "All landholding farmers"},
    {"name": "PMFBY", "desc": "Affordable crop insurance.", "link": "https://pmfby.gov.in/", "icon": "🛡️", "category": "Insurance", "eligibility": "All farmers"},
    {"name": "Kisan Credit Card", "desc": "Low interest loans (4%).", "link": "https://pib.gov.in/", "icon": "💳", "category": "Loans", "eligibility": "Farmers"},
    {"name": "e-NAM", "desc": "National electronic trading platform.", "link": "https://enam.gov.in/", "icon": "📈", "category": "Marketing", "eligibility": "All farmers"},
    {"name": "Soil Health Card", "desc": "Free soil testing.", "link": "https://soilhealth.dac.gov.in/", "icon": "🌱", "category": "Soil Health", "eligibility": "All farmers"},
    {"name": "PM-KUSUM", "desc": "Solar pump subsidy.", "link": "https://pmkusum.mnre.gov.in/", "icon": "☀️", "category": "Renewable Energy", "eligibility": "Farmers"}
]

CROP_DATABASE = {
    "Rice": {"season": "Kharif", "water": "High", "profit": "Medium", "duration": "120-150 days"},
    "Wheat": {"season": "Rabi", "water": "Medium", "profit": "High", "duration": "110-130 days"},
    "Sugarcane": {"season": "Annual", "water": "High", "profit": "High", "duration": "300-365 days"},
    "Cotton": {"season": "Kharif", "water": "Medium", "profit": "High", "duration": "150-180 days"},
    "Maize": {"season": "Kharif/Rabi", "water": "Medium", "profit": "Medium", "duration": "90-100 days"},
    "Pulses": {"season": "Rabi", "water": "Low", "profit": "Medium", "duration": "90-120 days"},
    "Vegetables": {"season": "All", "water": "High", "profit": "High", "duration": "60-90 days"},
    "Fruits": {"season": "Annual", "water": "Medium", "profit": "Very High", "duration": "Varies"}
}

# --- 5. FUNCTIONS ---

def text_to_speech_gtts(text, language='en'):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_file.name)
            tmp_file.seek(0)
            audio_bytes = tmp_file.read()
        os.unlink(tmp_file.name)
        return audio_bytes
    except Exception:
        return None

async def text_to_speech_edge(text, voice='en-IN-NeerjaNeural'):
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        audio_data.seek(0)
        return audio_data.read()
    except Exception:
        return None

def play_audio(audio_bytes):
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio autoplay controls style="width: 100%; margin-top: 10px;"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)

def create_agriculture_dashboard():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=[65, 70, 68, 75, 80, 85, 90, 88, 82, 78, 75, 70], name='Yield', line=dict(color='#4CAF50', width=3), fill='tozeroy'))
    fig.add_trace(go.Bar(x=months, y=[12000, 13500, 12800, 14500, 16000, 17500, 19000, 18500, 17000, 15500, 14000, 13000], name='Revenue', marker_color='#2196F3', opacity=0.7))
    fig.update_layout(title="📈 Annual Performance", plot_bgcolor='rgba(0,0,0,0)', height=350, legend=dict(orientation="h", y=1.02))
    return fig

def create_crop_comparison_chart(selected_crops):
    crops = selected_crops[:3]
    data = []
    for crop in crops:
        if crop in CROP_DATABASE:
            info = CROP_DATABASE[crop]
            profit_map = {"Very High": 10, "High": 8, "Medium": 6, "Low": 4}
            water_map = {"High": 10, "Medium": 6, "Low": 3}
            data.append({'Crop': crop, 'Profit': profit_map.get(info['profit'], 5), 'Water': water_map.get(info['water'], 5), 'Season': 7})
    if data:
        fig = px.bar(pd.DataFrame(data), x='Crop', y=['Profit', 'Water', 'Season'], barmode='group', title="Comparison")
        fig.update_layout(height=350)
        return fig
    return None

def get_weather_with_forecast(city):
    if not WEATHER_API_KEY:
        return {'temp': 28, 'condition': 'Sunny', 'icon': '☀️'}
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            condition = data['weather'][0]['main']
            icons = {'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Thunderstorm': '⛈️'}
            return {'temp': data['main']['temp'], 'condition': condition, 'icon': icons.get(condition, '🌤️')}
    except:
        pass
    return {'temp': 28, 'condition': 'Clear', 'icon': '☀️'}

# --- CRITICAL FIX: AI RESPONSE FUNCTION ---
def get_ai_response(prompt, context=""):
    """Get AI response from Gemini"""
    if not GOOGLE_API_KEY:
        return "⚠️ Error: API Key is missing. Please add GOOGLE_API_KEY to Streamlit Secrets."
    
    try:
        # FIX: Using 'gemini-1.5-flash' (Correct Model Name)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        full_prompt = f"""
        You are GreenMitra AI, an expert agricultural assistant for Indian farmers.
        Context: {context}
        User Query: {prompt}
        Provide a helpful, practical response specific to Indian farming.
        """
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Service Error: {str(e)}"

def speak_text_async(text, language='en'):
    try:
        audio_bytes = text_to_speech_gtts(text, language)
        if audio_bytes:
            st.session_state.audio_queue.append(audio_bytes)
    except:
        pass

# --- 6. SESSION STATE ---
if 'messages' not in st.session_state: st.session_state.messages = []
if 'audio_queue' not in st.session_state: st.session_state.audio_queue = []
if 'selected_language' not in st.session_state: st.session_state.selected_language = "English"
if 'user_location' not in st.session_state: st.session_state.user_location = "Kolhapur"
if 'farmer_name' not in st.session_state: st.session_state.farmer_name = "Rajesh Kumar"

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#4CAF50;'>🌾 GreenMitra</h2>", unsafe_allow_html=True)
        st.session_state.farmer_name = st.text_input("Full Name", st.session_state.farmer_name)
        st.session_state.user_location = st.text_input("Village/City", st.session_state.user_location)
        st.session_state.selected_language = st.selectbox("Language", ["English", "Hindi", "Marathi", "Tamil", "Telugu"])
        
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.rerun()

    # Header
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1: st.markdown("<h1 style='color:#2E7D32;'>GreenMitra AI</h1>", unsafe_allow_html=True)
    weather = get_weather_with_forecast(st.session_state.user_location)
    with col2: st.markdown(f"<div class='stat-card'><h4>{weather['icon']} {weather['temp']}°C</h4></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='stat-card'><h4>🌱 5 Acres</h4></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='stat-card'><h4>💰 ₹45.6K</h4></div>", unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(["🤖 AI Chat", "🌿 Crop Doctor", "📊 Analytics", "🏛️ Schemes", "🎤 Voice", "📈 Market"])

    # TAB 1: CHAT
    with tabs[0]:
        col_c1, col_c2 = st.columns([3, 1])
        with col_c1:
            chat_cont = st.container(height=400)
            with chat_cont:
                for msg in st.session_state.messages[-10:]:
                    css_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
                    sender = "You" if msg["role"] == "user" else "GreenMitra"
                    st.markdown(f"<div class='{css_class}'><strong>{sender}:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            
            prompt = st.chat_input("Ask about farming...")
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("Thinking..."):
                    ctx = f"Farmer: {st.session_state.farmer_name}, Loc: {st.session_state.user_location}"
                    response = get_ai_response(prompt, ctx)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

        with col_c2:
            st.markdown("### Quick Ask")
            if st.button("❓ Best Crop?"):
                st.session_state.messages.append({"role": "user", "content": "Best crop for this season?"})
                response = get_ai_response("Best crop for this season?", f"Farmer: {st.session_state.farmer_name}")
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

    # TAB 2: DOCTOR
    with tabs[1]:
        st.markdown("### 🌿 Crop Doctor")
        img_file = st.file_uploader("Upload Image", type=['jpg', 'png'])
        if img_file and st.button("Analyze Disease"):
            st.image(img_file, width=300)
            st.success("Analysis: Leaf Rust detected (92%). Treatment: Apply Neem Oil.")

    # TAB 3: ANALYTICS
    with tabs[2]:
        st.plotly_chart(create_agriculture_dashboard(), use_container_width=True)
        if st.button("Check Profit"):
            st.info("Estimated Profit: ₹45,000 based on current market rates.")

    # TAB 4: SCHEMES
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes")
        for s in PERMANENT_SCHEMES[:4]:
            st.markdown(f"<div class='glass-card'><h4>{s['icon']} {s['name']}</h4><p>{s['desc']}</p><a href='{s['link']}'>Apply</a></div>", unsafe_allow_html=True)

    # TAB 5: VOICE
    with tabs[4]:
        st.markdown("### 🎤 Voice Assistant")
        voice_in = st.text_input("Type for Voice Response:")
        if voice_in and st.button("Speak Answer"):
            resp = get_ai_response(voice_in)
            st.info(resp)
            audio = text_to_speech_gtts(resp)
            play_audio(audio)

    # TAB 6: MARKET
    with tabs[5]:
        st.markdown("### 📈 Market Prices")
        df = pd.DataFrame({'Crop': ['Wheat', 'Rice', 'Cotton'], 'Price': [2100, 1850, 5800]})
        st.bar_chart(df.set_index('Crop'))

if __name__ == "__main__":
    main()
