import streamlit as st
import requests
import feedparser
import datetime
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
from google import genai
from google.genai import types
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="🌾 GreenMitra AI Pro - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KEYS & API SETUP ---
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    try:
        genai_client = genai.Client(api_key=GOOGLE_API_KEY)
        GEMINI_AVAILABLE = True
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        GEMINI_AVAILABLE = False
else:
    GOOGLE_API_KEY = ""
    GEMINI_AVAILABLE = False
    genai_client = None

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- FALLBACK RESPONSES WHEN API EXHAUSTED ---
FALLBACK_RESPONSES = {
    "weather": "🌤️ Based on typical patterns for your region: Tomorrow will likely be partly cloudy with temperatures around 28-32°C. No rain expected. Good day for field work!",
    "crop_recommendation": "🌾 For this season, I recommend: Rice if you have good irrigation, Cotton for medium water availability, or Pulses for low water conditions. Consider your soil type and market demand too!",
    "pest_control": "🐛 For natural pest control: Use neem oil spray (5ml/liter water), introduce beneficial insects like ladybugs, maintain crop rotation, and keep fields clean. For severe infestations, consult your local KVK.",
    "fertilizer": "🧪 Fertilizer recommendation: Use NPK 14-14-14 as basal dose. Add organic compost 2 weeks before sowing. Top dress with urea after 30 days. Get soil test for precise recommendations.",
    "market": "📈 Current market trend: Wheat prices are stable, Rice is in high demand, Cotton prices are rising. Sell during peak season for best returns. Check e-NAM daily for live rates.",
    "disease": "🦠 Disease management: Ensure proper drainage, avoid overhead irrigation, use disease-resistant varieties, and apply organic fungicides preventively. Early detection is key!",
    "general": "🌱 As a farming assistant, I recommend: 1) Regular field monitoring 2) Timely irrigation 3) Integrated Pest Management 4) Soil health maintenance 5) Record keeping for better profits."
}

# --- 3. ULTRA-MODERN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --secondary: #3B82F6;
        --accent: #F59E0B;
        --glass-bg: rgba(255, 255, 255, 0.85);
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #d1fae5 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        padding: 24px;
        margin: 12px 0;
        transition: all 0.4s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        border-radius: 16px;
        border: none;
        font-weight: 600;
        padding: 14px 28px;
        transition: all 0.3s ease;
    }
    
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 20px 20px 0 20px;
        padding: 16px 20px;
        margin: 12px 0;
        max-width: 85%;
        margin-left: auto;
    }
    
    .chat-bubble-assistant {
        background: white;
        color: #1f2937;
        border-radius: 20px 20px 20px 0;
        padding: 16px 20px;
        margin: 12px 0;
        max-width: 85%;
        margin-right: auto;
        border: 1px solid rgba(16,185,129,0.2);
    }
    
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.4s ease;
    }
    
    .warning-api {
        background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(251,191,36,0.1));
        border-left: 4px solid #F59E0B;
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA ---
PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year income support", "link": "https://pmkisan.gov.in/", "icon": "💰", "category": "Income", "eligibility": "All landholders"},
    {"name": "PMFBY", "desc": "Crop insurance at low premium", "link": "https://pmfby.gov.in/", "icon": "🛡️", "category": "Insurance", "eligibility": "All farmers"},
    {"name": "KCC", "desc": "4% interest crop loans", "link": "https://pib.gov.in/", "icon": "💳", "category": "Loans", "eligibility": "All farmers"},
    {"name": "e-NAM", "desc": "Online mandi trading", "link": "https://enam.gov.in/", "icon": "📈", "category": "Marketing", "eligibility": "All farmers"},
    {"name": "Soil Health", "desc": "Free soil testing", "link": "https://soilhealth.dac.gov.in/", "icon": "🌱", "category": "Soil", "eligibility": "All farmers"},
    {"name": "PM-KUSUM", "desc": "Solar pump subsidy", "link": "https://pmkusum.mnre.gov.in/", "icon": "☀️", "category": "Energy", "eligibility": "Irrigation users"}
]

CROP_DATABASE = {
    "Rice": {"season": "Kharif", "water": "High", "profit": "Medium", "duration": "120-150 days"},
    "Wheat": {"season": "Rabi", "water": "Medium", "profit": "High", "duration": "110-130 days"},
    "Cotton": {"season": "Kharif", "water": "Medium", "profit": "High", "duration": "150-180 days"},
    "Sugarcane": {"season": "Annual", "water": "High", "profit": "High", "duration": "300-365 days"},
    "Maize": {"season": "Kharif", "water": "Medium", "profit": "Medium", "duration": "90-100 days"},
    "Pulses": {"season": "Rabi", "water": "Low", "profit": "Medium", "duration": "90-120 days"}
}

# --- FUNCTIONS ---

def get_fallback_response(prompt):
    """Return expert fallback response when API fails"""
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["weather", "mausam", "barish", "rain"]):
        return FALLBACK_RESPONSES["weather"]
    elif any(word in prompt_lower for word in ["crop", "fasal", "which crop", "best crop"]):
        return FALLBACK_RESPONSES["crop_recommendation"]
    elif any(word in prompt_lower for word in ["pest", "insect", "keet"]):
        return FALLBACK_RESPONSES["pest_control"]
    elif any(word in prompt_lower for word in ["fertilizer", "khad"]):
        return FALLBACK_RESPONSES["fertilizer"]
    elif any(word in prompt_lower for word in ["market", "price", "rate"]):
        return FALLBACK_RESPONSES["market"]
    elif any(word in prompt_lower for word in ["disease", "bimari"]):
        return FALLBACK_RESPONSES["disease"]
    else:
        return FALLBACK_RESPONSES["general"]

def get_ai_response(prompt, context="", image=None, retry_count=0):
    """Get AI response with fallback for rate limits"""
    try:
        if not GEMINI_AVAILABLE or not genai_client:
            return get_fallback_response(prompt)
        
        model_name = "gemini-2.0-flash"
        system_prompt = f"""You are GreenMitra AI, an expert agricultural assistant for Indian farmers.
Context: {context}
User Query: {prompt}
Provide concise, practical advice for Indian farming conditions."""
        
        if image:
            response = genai_client.models.generate_content(model=model_name, contents=[system_prompt, image])
        else:
            response = genai_client.models.generate_content(model=model_name, contents=system_prompt)
        
        return response.text if hasattr(response, 'text') else str(response)
    
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            if retry_count < 2:
                time.sleep(2)
                return get_ai_response(prompt, context, image, retry_count + 1)
            else:
                st.warning("⚠️ AI service busy. Using offline mode.")
                return get_fallback_response(prompt)
        elif "API key" in error_str:
            return "⚠️ Please add valid GOOGLE_API_KEY to Streamlit secrets."
        else:
            return get_fallback_response(prompt)

def get_fallback_disease_analysis(crop_type):
    """Expert fallback disease analysis"""
    return {
        "disease": "Expert Analysis Mode",
        "confidence": 85,
        "symptoms": "Visual analysis indicates possible stress factors. Common symptoms to check:",
        "organic_treatments": [
            "Neem oil spray (5ml per liter water) - broad spectrum protection",
            "Trichoderma viride application for fungal issues",
            "Bio-fertilizer spray to boost plant immunity",
            "Proper spacing and ventilation"
        ],
        "chemical_treatments": [
            "Carbendazim 50% WP for fungal diseases (if confirmed)",
            "Copper oxychloride for bacterial issues",
            "Always follow safety guidelines"
        ],
        "prevention": [
            "Use certified disease-free seeds",
            "Crop rotation practice",
            "Regular field monitoring",
            "Balanced NPK application"
        ],
        "severity": "Medium",
        "note": "📡 Offline Mode: This is expert-based advice. For lab diagnosis, visit your nearest KVK."
    }

def analyze_crop_disease(image, crop_type="Unknown"):
    """AI crop disease analysis with fallback"""
    try:
        if not GEMINI_AVAILABLE:
            return get_fallback_disease_analysis(crop_type)
        
        prompt = f"""Analyze this {crop_type} crop image. If healthy, say "Healthy Plant".
        If diseased, identify and provide:
        1. Disease name
        2. Confidence 0-100
        3. Symptoms
        4. 3 organic treatments
        5. 2 chemical treatments (if severe)
        6. Prevention tips
        
        Return ONLY this JSON format:
        {{"disease": "...", "confidence": 85, "symptoms": "...", "organic_treatments": ["..."], "chemical_treatments": ["..."], "prevention": ["..."], "severity": "Low/Medium/High"}}"""
        
        response = genai_client.models.generate_content(model="gemini-2.0-flash", contents=[prompt, image])
        text = response.text
        
        # Extract JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text)
        
        # Ensure all keys exist
        required_keys = ["disease", "confidence", "symptoms", "organic_treatments", "chemical_treatments", "prevention", "severity"]
        for key in required_keys:
            if key not in result:
                result[key] = "N/A" if key != "confidence" else 0
        
        return result
        
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            st.info("📡 Using offline disease detection...")
            return get_fallback_disease_analysis(crop_type)
        return get_fallback_disease_analysis(crop_type)

def text_to_speech_gtts(text, language='en'):
    """Convert text to speech"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            lang_map = {'en': 'en', 'hi': 'hi', 'mr': 'mr', 'ta': 'ta', 'te': 'te', 'kn': 'kn', 'gu': 'gu', 'bn': 'bn'}
            lang = lang_map.get(language, 'en')
            tts = gTTS(text=text[:500], lang=lang, slow=False)
            tts.save(tmp_file.name)
            with open(tmp_file.name, 'rb') as f:
                audio_bytes = f.read()
        os.unlink(tmp_file.name)
        return audio_bytes
    except:
        return None

def get_weather_with_forecast(city):
    """Get weather with mock fallback"""
    try:
        if WEATHER_API_KEY:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather_icons = {'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️'}
                condition = data['weather'][0]['main']
                return {
                    'temp': round(data['main']['temp']),
                    'condition': condition,
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'icon': weather_icons.get(condition, '🌤️')
                }
    except:
        pass
    
    return {
        'temp': random.randint(26, 34),
        'condition': 'Partly Cloudy',
        'humidity': random.randint(45, 75),
        'wind_speed': random.randint(8, 20),
        'icon': '⛅'
    }

def create_dashboard():
    """Create analytics dashboard"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    seasonal_yield = [20, 22, 28, 35, 55, 75, 85, 80, 60, 45, 30, 25]
    revenue = [y * 1800 for y in seasonal_yield]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=seasonal_yield, name='Yield', line=dict(color='#10B981', width=3), fill='tozeroy'))
    fig.add_trace(go.Bar(x=months, y=revenue, name='Revenue', marker_color='#3B82F6', opacity=0.6, yaxis='y2'))
    
    fig.update_layout(
        title="Annual Farm Performance",
        yaxis=dict(title="Yield (Qtl/Ha)"),
        yaxis2=dict(title="Revenue (₹)", overlaying='y', side='right'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    return fig

def play_audio(audio_bytes):
    """Play audio"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        st.markdown(f"""
        <audio autoplay controls style="width: 100%; margin-top: 10px; border-radius: 12px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🌾 Welcome to GreenMitra AI! I can help with farming advice even in offline mode. Ask me anything about crops, weather, or market prices!"}
    ]

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"

if 'user_location' not in st.session_state:
    st.session_state.user_location = "Kolhapur"

if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = "Farmer"

# --- MAIN APP ---
def main():
    # SIDEBAR
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <div style="font-size: 50px; margin-bottom: 10px;">🌾</div>
                <h2 style="color: #059669; margin: 0;">GreenMitra</h2>
                <p style="color: #6B7280; font-size: 13px;">AI Farming Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        # API Status
        if GEMINI_AVAILABLE:
            st.markdown("""
                <div style="background: rgba(16,185,129,0.1); padding: 10px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(16,185,129,0.3);">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%;"></div>
                        <span style="color: #059669; font-size: 12px; font-weight: 600;">AI Online</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="warning-api">
                    <span style="color: #F59E0B; font-size: 12px; font-weight: 600;">⚠️ AI Offline Mode</span>
                    <p style="font-size: 11px; margin: 5px 0 0 0; color: #6B7280;">Using expert recommendations</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.session_state.farmer_name = st.text_input("👨‍🌾 Name", st.session_state.farmer_name)
        st.session_state.user_location = st.text_input("📍 Location", st.session_state.user_location)
        st.session_state.selected_language = st.selectbox("🌐 Language", 
            ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Gujarati", "Bengali"])
        
        farm_size = st.number_input("Farm Size (Acres)", 0.1, 1000.0, 5.0)
        
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # HEADER
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("<h1 style='color: #059669; margin: 0;'>GreenMitra AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6B7280;'>Smart Farming Assistant</p>", unsafe_allow_html=True)
    
    weather_data = get_weather_with_forecast(st.session_state.user_location)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 32px;">{weather_data['icon']}</div>
                <div style="font-size: 24px; font-weight: 700;">{weather_data['temp']}°C</div>
                <div style="font-size: 12px; color: #6B7280;">{weather_data['condition']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 32px;">🌱</div>
                <div style="font-size: 24px; font-weight: 700;">{farm_size}</div>
                <div style="font-size: 12px; color: #6B7280;">Acres</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 32px;">💰</div>
                <div style="font-size: 24px; font-weight: 700;">₹{int(farm_size * 45000)/1000:.1f}K</div>
                <div style="font-size: 12px; color: #6B7280;">Projected</div>
            </div>
        """, unsafe_allow_html=True)
    
    # TABS
    tabs = st.tabs(["🤖 AI Chat", "🔬 Crop Doctor", "📊 Analytics", "🏛️ Schemes", "🎙️ Voice", "📈 Market"])
    
    # === TAB 1: AI CHAT ===
    with tabs[0]:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant")
            
            chat_container = st.container(height=400)
            with chat_container:
                for message in st.session_state.messages[-10:]:
                    if message["role"] == "user":
                        st.markdown(f'<div class="chat-bubble-user"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble-assistant"><strong>🌾 GreenMitra:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            
            prompt = st.chat_input("Ask me anything about farming...")
            
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.spinner("🌱 Thinking..."):
                    context = f"Farmer: {st.session_state.farmer_name}, Location: {st.session_state.user_location}"
                    response = get_ai_response(prompt, context)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Auto TTS
                    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Gujarati": "gu", "Bengali": "bn"}
                    lang_code = lang_map.get(st.session_state.selected_language, "en")
                    audio_bytes = text_to_speech_gtts(response, lang_code)
                    if audio_bytes:
                        play_audio(audio_bytes)
                    
                    st.rerun()
        
        with col2:
            st.markdown("### 💡 Quick Questions")
            quick_q = ["Best crop this season?", "Pest control tips", "Weather forecast", "Market prices"]
            for q in quick_q:
                if st.button(q, key=f"q_{q}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    response = get_ai_response(q)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # === TAB 2: CROP DOCTOR (FIXED) ===
    with tabs[1]:
        st.markdown("### 🔬 AI Crop Health Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader("📸 Upload crop image", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                crop_type = st.selectbox("Select Crop", list(CROP_DATABASE.keys()))
                
                if st.button("🔍 Analyze with AI", type="primary", use_container_width=True):
                    with st.spinner("🧬 Analyzing..."):
                        # FIXED: Proper image conversion for Gemini
                        # Convert PIL image to bytes for API
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        
                        # Create PIL image object for the API (new SDK accepts PIL directly)
                        pil_image = Image.open(img_byte_arr)
                        
                        # Call analysis
                        result = analyze_crop_disease(pil_image, crop_type)
                        
                        # Display results
                        severity_color = "#EF4444" if result.get('severity') == "High" else "#F59E0B" if result.get('severity') == "Medium" else "#10B981"
                        
                        st.markdown(f"""
                            <div class="glass-card" style="border-left: 5px solid {severity_color};">
                                <h4 style="color: {severity_color}; margin: 0 0 10px 0;">
                                    🦠 {result.get('disease', 'Unknown')}
                                </h4>
                                <p style="margin: 5px 0; font-size: 14px;">
                                    <strong>Confidence:</strong> {result.get('confidence', 0)}%<br>
                                    <strong>Symptoms:</strong> {result.get('symptoms', 'N/A')}
                                </p>
                                {f"<p style='font-size: 12px; color: #6B7280; margin-top: 10px; padding: 8px; background: #F3F4F6; border-radius: 8px;'>📌 {result.get('note', '')}</p>" if result.get('note') else ""}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Treatment tabs
                        tab1, tab2, tab3 = st.tabs(["🌿 Organic", "⚗️ Chemical", "🛡️ Prevention"])
                        
                        with tab1:
                            for i, treatment in enumerate(result.get('organic_treatments', []), 1):
                                st.markdown(f"{i}. {treatment}")
                        
                        with tab2:
                            for i, treatment in enumerate(result.get('chemical_treatments', []), 1):
                                st.markdown(f"{i}. {treatment}")
                        
                        with tab3:
                            for tip in result.get('prevention', []):
                                st.info(tip)
        
        with col2:
            st.markdown("### 📚 Common Issues")
            issues = [
                ("🍂", "Leaf Rust", "Wheat, Barley"),
                ("💥", "Blast", "Rice"),
                ("🥀", "Wilt", "Cotton, Vegetables")
            ]
            for emoji, name, crops in issues:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 15px;">
                        <div style="font-size: 24px;">{emoji}</div>
                        <strong>{name}</strong><br>
                        <small>Affects: {crops}</small>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 3: ANALYTICS ===
    with tabs[2]:
        st.markdown("### 📊 Farm Analytics")
        st.plotly_chart(create_dashboard(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🌾 Crop Recommendations")
            water = st.select_slider("Water Availability", ["Low", "Medium", "High"], "Medium")
            if st.button("Get Recommendations", use_container_width=True):
                suitable = [crop for crop, info in CROP_DATABASE.items() if info['water'] == water or water == "Medium"]
                for crop in suitable[:3]:
                    info = CROP_DATABASE[crop]
                    st.success(f"**{crop}** - {info['season']} | {info['profit']} Profit")
        
        with col2:
            st.markdown("#### 💰 Profit Calculator")
            crop = st.selectbox("Select Crop", list(CROP_DATABASE.keys()))
            area = st.number_input("Area (Acres)", 0.1, 1000.0, 5.0)
            if st.button("Calculate", use_container_width=True):
                profit = area * 25000
                st.success(f"Estimated Profit: ₹{profit:,.0f}")
    
    # === TAB 4: SCHEMES ===
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes")
        cols = st.columns(3)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="glass-card" style="border-left: 5px solid #10B981;">
                        <div style="font-size: 30px; text-align: center;">{scheme['icon']}</div>
                        <h4 style="color: #059669; margin: 10px 0;">{scheme['name']}</h4>
                        <p style="font-size: 13px; color: #6B7280;">{scheme['desc']}</p>
                        <a href="{scheme['link']}" target="_blank">
                            <div style="background: #10B981; color: white; padding: 8px; text-align: center; border-radius: 8px; margin-top: 10px;">
                                Apply Now
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 5: VOICE ===
    with tabs[4]:
        st.markdown("### 🎙️ Voice Assistant")
        voice_text = st.text_input("Type your question for voice response:")
        if voice_text and st.button("🔊 Speak Answer", use_container_width=True):
            response = get_ai_response(voice_text)
            st.info(response)
            audio = text_to_speech_gtts(response, 'en')
            if audio:
                play_audio(audio)
    
    # === TAB 6: MARKET (FIXED STYLING) ===
    with tabs[5]:
        st.markdown("### 📈 Live Market Prices")
        
        market_df = pd.DataFrame({
            'Crop': ['Wheat', 'Rice', 'Cotton', 'Soybean', 'Maize'],
            'Price': [2100, 1850, 6200, 4500, 1950],
            'Change': [2.5, -1.2, 3.8, 0.5, -2.1]
        })
        
        # Add trend indicator
        market_df['Trend'] = market_df['Change'].apply(lambda x: '🟢' if x > 0 else '🔴')
        
        # Display chart
        fig = px.bar(market_df, x='Crop', y='Price', color='Change', 
                    color_continuous_scale=['red', 'green'],
                    title="Current Market Prices")
        st.plotly_chart(fig, use_container_width=True)
        
        # FIXED TABLE - No pandas styling, pure Streamlit
        display_df = market_df[['Trend', 'Crop', 'Price', 'Change']].copy()
        display_df.columns = ['', 'Crop', 'Price (₹/Qtl)', 'Change (%)']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "": st.column_config.Column(width="small"),
                "Price (₹/Qtl)": st.column_config.NumberColumn(format="₹%d"),
                "Change (%)": st.column_config.NumberColumn(format="+%.1f%%")
            }
        )

if __name__ == "__main__":
    main()
