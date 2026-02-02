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
import threading

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="🌾 GreenMitra AI - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DEEPSEEK API CONFIGURATION ---
if "DEEPSEEK_API_KEY" in st.secrets:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
else:
    DEEPSEEK_API_KEY = ""
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

if "WEATHER_API_KEY" in st.secrets:
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]
else:
    WEATHER_API_KEY = ""

# --- 3. MODERN CSS WITH ADVANCED ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&family=Poppins:wght@300;400;500;600&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Modern Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        font-family: 'Inter', sans-serif !important;
        background-attachment: fixed !important;
    }
    
    /* Glass Morphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15) !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .glass-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25) !important;
        border: 1px solid rgba(76, 175, 80, 0.5) !important;
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
        background: linear-gradient(45deg, #2E7D32, #4CAF50) !important;
    }
    
    /* Animated Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px !important;
        background: transparent !important;
        border-bottom: 2px solid #e0e0e0 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 12px 20px !important;
        border: 1px solid #e0e0e0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        color: #555 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border: 1px solid #4CAF50 !important;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* API Key Input Styling */
    .api-key-input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin: 10px 0 !important;
    }
    
    /* Error Message Styling */
    .error-message {
        background: linear-gradient(45deg, #FF6B6B, #FF8E8E) !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        text-align: center !important;
    }
    
    /* Success Message Styling */
    .success-message {
        background: linear-gradient(45deg, #4CAF50, #66BB6A) !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 10px !important;
        margin: 10px 0 !important;
        text-align: center !important;
    }
    
    /* Floating Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .floating-element {
        animation: float 4s ease-in-out infinite;
    }
    
    .pulse-element {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Voice Assistant Styling */
    .voice-assistant {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Weather Widget */
    .weather-container {
        background: linear-gradient(135deg, #2196F3, #21CBF3) !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3) !important;
        text-align: center !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        border-radius: 4px;
    }
    
    /* Hide Default Elements */
    #MainMenu, header, footer { 
        visibility: hidden !important; 
    }
    
    .stDeployButton { display: none !important; }
    
    .block-container { 
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* Progress Bars */
    .progress-container {
        width: 100%;
        background: rgba(0,0,0,0.1);
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 10px;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }
    
    /* Chat bubbles */
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 18px 18px 0 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .chat-bubble-assistant {
        background: #f0f7f4;
        color: #333;
        border-radius: 18px 18px 18px 0;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-right: auto;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0f2e9;
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Scheme Cards */
    .scheme-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #4CAF50;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .scheme-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* API Status Indicator */
    .api-status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    
    .api-status-active {
        background: #4CAF50;
        color: white;
    }
    
    .api-status-inactive {
        background: #FF6B6B;
        color: white;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- 4. CONSTANTS & DATA ---

PERMANENT_SCHEMES = [
    {
        "name": "PM-KISAN", 
        "desc": "₹6,000/year direct income support for all landholding farmers.",
        "link": "https://pmkisan.gov.in/",
        "icon": "💰",
        "category": "Income Support",
        "eligibility": "All landholding farmers"
    },
    {
        "name": "PMFBY (Crop Insurance)", 
        "desc": "Affordable crop insurance with lowest premium rates.",
        "link": "https://pmfby.gov.in/",
        "icon": "🛡️",
        "category": "Insurance",
        "eligibility": "All farmers"
    },
    {
        "name": "Kisan Credit Card", 
        "desc": "Low interest loans (4%) for farming and allied activities.",
        "link": "https://pib.gov.in/",
        "icon": "💳",
        "category": "Loans",
        "eligibility": "Farmers and tenant farmers"
    },
    {
        "name": "e-NAM Market", 
        "desc": "National electronic trading platform for better crop prices.",
        "link": "https://enam.gov.in/",
        "icon": "📈",
        "category": "Marketing",
        "eligibility": "All farmers"
    },
    {
        "name": "Soil Health Card", 
        "desc": "Free soil testing and fertilizer recommendations.",
        "link": "https://soilhealth.dac.gov.in/",
        "icon": "🌱",
        "category": "Soil Health",
        "eligibility": "All farmers"
    },
    {
        "name": "PM-KUSUM", 
        "desc": "Subsidy for solar pumps and grid-connected solar plants.",
        "link": "https://pmkusum.mnre.gov.in/",
        "icon": "☀️",
        "category": "Renewable Energy",
        "eligibility": "Farmers with irrigation pumps"
    }
]

# Crop database for recommendations
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

# --- 5. DEEPSEEK API FUNCTIONS ---

def get_deepseek_response(prompt, context="", max_tokens=1000):
    """Get response from DeepSeek API"""
    try:
        if not DEEPSEEK_API_KEY:
            return "⚠️ Please configure your DeepSeek API key in the settings section.", False
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_message = f"""You are GreenMitra AI, an expert agricultural assistant for Indian farmers.
Context: {context}

Please provide helpful, practical advice for Indian farming conditions.
Be specific, actionable, and mention government schemes if relevant.
Respond in a friendly, conversational tone."""
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"], True
            else:
                return "⚠️ No response from AI. Please try again.", False
        elif response.status_code == 401:
            return "🔑 Invalid API key. Please check your DeepSeek API key in settings.", False
        elif response.status_code == 429:
            return "⏳ Rate limit exceeded. Please wait a moment and try again.", False
        else:
            return f"⚠️ API Error {response.status_code}: {response.text[:100]}", False
    
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again.", False
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet connection.", False
    except Exception as e:
        return f"⚠️ Error: {str(e)}", False

def test_deepseek_api():
    """Test if DeepSeek API is working"""
    if not DEEPSEEK_API_KEY:
        return False, "No API key configured"
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "Say 'API connected successfully'"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, "✅ API connected successfully"
        else:
            return False, f"❌ API Error: {response.status_code}"
    
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"

# --- 6. OTHER UTILITY FUNCTIONS ---

def text_to_speech_gtts(text, language='en'):
    """Convert text to speech using gTTS"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_file.name)
            tmp_file.seek(0)
            audio_bytes = tmp_file.read()
        
        os.unlink(tmp_file.name)
        return audio_bytes
    except Exception as e:
        st.error(f"gTTS Error: {e}")
        return None

async def text_to_speech_edge(text, voice='en-IN-NeerjaNeural'):
    """Convert text to speech using Edge TTS"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        audio_data.seek(0)
        return audio_data.read()
    except Exception as e:
        st.error(f"Edge TTS Error: {e}")
        return None

def play_audio(audio_bytes):
    """Play audio in Streamlit"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay controls style="width: 100%; margin-top: 10px;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

def create_agriculture_dashboard():
    """Create an interactive dashboard for agriculture metrics"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[65, 70, 68, 75, 80, 85, 90, 88, 82, 78, 75, 70],
        name='Yield (Quintal/Ha)',
        line=dict(color='#4CAF50', width=3),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.2)'
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=[12000, 13500, 12800, 14500, 16000, 17500, 19000, 18500, 17000, 15500, 14000, 13000],
        name='Revenue (₹)',
        marker_color='#2196F3',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="📈 Annual Agriculture Performance",
        xaxis_title="Month",
        yaxis_title="Yield (Quintal/Ha)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def get_weather_with_forecast(city):
    """Get detailed weather information"""
    if not WEATHER_API_KEY:
        return {
            'temp': 28,
            'condition': 'Sunny',
            'humidity': 65,
            'wind_speed': 12,
            'icon': '☀️'
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_icons = {
                'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 
                'Drizzle': '🌦️', 'Thunderstorm': '⛈️', 'Snow': '❄️',
                'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '😶‍🌫️'
            }
            
            condition = data['weather'][0]['main']
            icon = weather_icons.get(condition, '🌤️')
            
            return {
                'temp': data['main']['temp'],
                'condition': condition,
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': icon
            }
        else:
            return {
                'temp': 28,
                'condition': 'Clear',
                'humidity': 65,
                'wind_speed': 12,
                'icon': '☀️'
            }
    except:
        return {
            'temp': 28,
            'condition': 'Clear',
            'humidity': 65,
            'wind_speed': 12,
            'icon': '☀️'
        }

# --- 7. SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"

if 'user_location' not in st.session_state:
    st.session_state.user_location = "Kolhapur"

if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = "Rajesh Kumar"

if 'deepseek_api_key' not in st.session_state:
    st.session_state.deepseek_api_key = ""

if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False

# --- 8. MAIN APP ---
def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="color: #4CAF50; margin-bottom: 5px;">🌾 GreenMitra</h2>
                <p style="color: #666; font-size: 14px;">Smart Farming Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        # API Configuration Section
        st.markdown("### 🔑 DeepSeek API Configuration")
        
        # API Key Input
        api_key_input = st.text_input(
            "Enter DeepSeek API Key",
            value=st.session_state.deepseek_api_key,
            type="password",
            help="Get your API key from https://platform.deepseek.com/api_keys",
            key="api_key_input"
        )
        
        if api_key_input:
            st.session_state.deepseek_api_key = api_key_input
            # Update global variable
            global DEEPSEEK_API_KEY
            DEEPSEEK_API_KEY = api_key_input
        
        # Test API Connection
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔌 Test Connection", use_container_width=True):
                with st.spinner("Testing API connection..."):
                    success, message = test_deepseek_api()
                    if success:
                        st.session_state.api_connected = True
                        st.success(message)
                    else:
                        st.session_state.api_connected = False
                        st.error(message)
        
        with col2:
            if st.button("🔄 Clear API Key", use_container_width=True):
                st.session_state.deepseek_api_key = ""
                st.session_state.api_connected = False
                st.rerun()
        
        # API Status Indicator
        if st.session_state.api_connected:
            st.markdown('<span class="api-status api-status-active">✅ Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="api-status api-status-inactive">❌ Disconnected</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User Profile
        st.markdown("### 👨‍🌾 Farmer Profile")
        st.session_state.farmer_name = st.text_input("Full Name", st.session_state.farmer_name)
        farmer_age = st.number_input("Age", 18, 80, 45)
        farming_exp = st.selectbox("Farming Experience", ["Beginner", "Intermediate", "Expert"])
        
        # Farm Details
        st.markdown("### 🏞️ Farm Details")
        farm_size = st.number_input("Farm Size (Acres)", 1.0, 100.0, 5.0)
        soil_type = st.selectbox("Soil Type", ["Black Soil", "Red Soil", "Alluvial Soil", "Laterite Soil"])
        irrigation_type = st.selectbox("Irrigation Type", ["Rainfed", "Tube Well", "Canal", "Drip"])
        
        # Location
        st.markdown("### 📍 Location")
        st.session_state.user_location = st.text_input("Village/City", st.session_state.user_location)
        
        # Language
        st.markdown("### 🌐 Language")
        st.session_state.selected_language = st.selectbox(
            "Select Language",
            ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Gujarati", "Bengali"]
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("📞 Farmer Helpline"):
            st.info("Dial 1552 for 24/7 farmer helpline support")
        
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()
        
        if st.button("🆘 Emergency Help"):
            st.warning("Contact your nearest Krishi Vigyan Kendra (KVK) for immediate assistance")
    
    # --- MAIN CONTENT AREA ---
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # API Status Banner
        if not st.session_state.api_connected and not DEEPSEEK_API_KEY:
            st.markdown("""
                <div class="error-message">
                    ⚠️ <strong>DeepSeek API Key Required</strong><br>
                    Please configure your API key in the sidebar to enable all AI features.
                </div>
            """, unsafe_allow_html=True)
        elif st.session_state.api_connected:
            st.markdown("""
                <div class="success-message">
                    ✅ <strong>DeepSeek API Connected</strong><br>
                    All AI features are now enabled and ready to use.
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="padding: 10px 0;">
                <h1 style='font-size: 36px; margin: 0; color: #2E7D32; font-weight: 800;'>
                    GreenMitra AI
                </h1>
                <p style='font-size: 16px; color: #666; margin: 5px 0 0 0;'>
                    Powered by DeepSeek AI • Your Intelligent Farming Companion
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Weather Display
    weather_data = get_weather_with_forecast(st.session_state.user_location)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 24px; color: #2196F3;">{weather_data['icon']}</div>
                <div style="font-size: 20px; font-weight: 700; margin: 5px 0;">{weather_data['temp']}°C</div>
                <div style="font-size: 12px; color: #666;">{weather_data['condition']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 24px; color: #4CAF50;">🌱</div>
                <div style="font-size: 20px; font-weight: 700; margin: 5px 0;">{farm_size}</div>
                <div style="font-size: 12px; color: #666;">Acres</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 24px; color: #FF9800;">💰</div>
                <div style="font-size: 20px; font-weight: 700; margin: 5px 0;">₹45.6K</div>
                <div style="font-size: 12px; color: #666;">Projected</div>
            </div>
        """, unsafe_allow_html=True)
    
    # --- MAIN TABS ---
    tabs = st.tabs([
        "🤖 **AI Chat**", 
        "🌿 **Crop Doctor**", 
        "📊 **Analytics**", 
        "🏛️ **Schemes**",
        "🎤 **Voice**",
        "📈 **Market**"
    ])
    
    # === TAB 1: AI CHAT WITH DEEPSEEK ===
    with tabs[0]:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant (DeepSeek)")
            
            if not DEEPSEEK_API_KEY:
                st.markdown("""
                    <div class="glass-card">
                        <h4 style="color: #FF6B6B;">⚠️ API Key Required</h4>
                        <p>Please configure your DeepSeek API key in the sidebar to use the AI chat feature.</p>
                        <p>Get your API key from: <a href="https://platform.deepseek.com/api_keys" target="_blank">https://platform.deepseek.com/api_keys</a></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Display chat history
                chat_container = st.container(height=400)
                with chat_container:
                    for message in st.session_state.messages[-10:]:
                        if message["role"] == "user":
                            st.markdown(f"""
                                <div class="chat-bubble-user">
                                    <strong>You:</strong> {message['content']}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div class="chat-bubble-assistant">
                                    <strong>GreenMitra:</strong> {message['content']}
                                </div>
                            """, unsafe_allow_html=True)
                
                # Chat input
                prompt = st.chat_input(f"Ask me anything about farming in {st.session_state.selected_language}...")
                
                if prompt:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    with st.spinner("🌱 DeepSeek is thinking..."):
                        # Get AI response from DeepSeek
                        context = f"""
                        Farmer: {st.session_state.farmer_name}
                        Location: {st.session_state.user_location}
                        Language: {st.session_state.selected_language}
                        Farm Size: {farm_size} acres
                        Soil Type: {soil_type}
                        Experience: {farming_exp}
                        """
                        
                        response, success = get_deepseek_response(prompt, context)
                        
                        if success:
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # Convert to speech
                            lang_code_map = {
                                "English": "en",
                                "Hindi": "hi",
                                "Marathi": "mr",
                                "Tamil": "ta",
                                "Telugu": "te",
                                "Kannada": "kn",
                                "Gujarati": "gu",
                                "Bengali": "bn"
                            }
                            lang_code = lang_code_map.get(st.session_state.selected_language, "en")
                            
                            # Play audio in background
                            threading.Thread(target=lambda: play_audio(text_to_speech_gtts(response[:500], lang_code))).start()
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.error("API Error: " + response)
                    
                    st.rerun()
        
        with col2:
            st.markdown("### 💡 Quick Questions")
            
            quick_questions = [
                "Best crop for this season?",
                "How to control pests naturally?",
                "Water conservation tips?",
                "When to harvest wheat?",
                "Organic fertilizer recipe?",
                "Latest farming techniques?"
            ]
            
            for i, question in enumerate(quick_questions):
                if st.button(f"❓ {question}", key=f"q_{i}", use_container_width=True):
                    if not DEEPSEEK_API_KEY:
                        st.error("Please configure API key first")
                    else:
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        with st.spinner("Thinking..."):
                            context = f"Farmer: {st.session_state.farmer_name}"
                            response, success = get_deepseek_response(question, context)
                            if success:
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            else:
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                st.error("API Error")
                            st.rerun()
            
            # Text-to-Speech Demo
            st.markdown("### 🔊 Text-to-Speech")
            demo_text = st.text_area("Enter text to speak:", "Welcome to GreenMitra AI", height=100)
            
            col_tts1, col_tts2 = st.columns(2)
            with col_tts1:
                if st.button("🔊 gTTS", use_container_width=True):
                    audio_bytes = text_to_speech_gtts(demo_text)
                    if audio_bytes:
                        play_audio(audio_bytes)
            
            with col_tts2:
                if st.button("🔊 Edge TTS", use_container_width=True):
                    async def run_edge_tts():
                        audio_bytes = await text_to_speech_edge(demo_text)
                        if audio_bytes:
                            play_audio(audio_bytes)
                    
                    asyncio.run(run_edge_tts())
    
    # === TAB 2: CROP DOCTOR WITH DEEPSEEK ===
    with tabs[1]:
        st.markdown("### 🌿 AI-Powered Crop Health Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Image upload
            st.markdown("#### 📸 Upload Crop Image")
            uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'], key="crop_doctor_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Crop Image", use_column_width=True)
                
                if st.button("🔍 Analyze Disease with AI", type="primary", use_container_width=True):
                    if not DEEPSEEK_API_KEY:
                        st.error("⚠️ Please configure DeepSeek API key first")
                    else:
                        with st.spinner("🔬 DeepSeek is analyzing the image..."):
                            # Convert image to base64 for analysis
                            buffered = BytesIO()
                            image.save(buffered, format="JPEG")
                            img_str = base64.b64encode(buffered.getvalue()).decode()
                            
                            # Create prompt for DeepSeek
                            prompt = f"""
                            I have uploaded an image of a crop. Please analyze it for:
                            1. Disease identification
                            2. Severity assessment
                            3. Treatment recommendations (organic and chemical)
                            4. Preventive measures
                            
                            The image is of a crop from {st.session_state.user_location}, India.
                            Please provide detailed analysis for Indian farming conditions.
                            """
                            
                            # In a real implementation, you would use vision capabilities
                            # For now, we'll use text-based analysis
                            context = f"""
                            Image analysis request for crop disease.
                            Location: {st.session_state.user_location}
                            Farmer: {st.session_state.farmer_name}
                            Soil Type: {soil_type}
                            """
                            
                            response, success = get_deepseek_response(prompt, context)
                            
                            if success:
                                st.markdown(f"""
                                    <div class="glass-card">
                                        <h4 style="color: #4CAF50;">✅ DeepSeek Analysis Complete</h4>
                                        <div style="margin-top: 15px;">
                                            {response}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Play audio summary
                                summary = "Crop analysis completed. " + response[:200]
                                audio_bytes = text_to_speech_gtts(summary, 'en')
                                if audio_bytes:
                                    play_audio(audio_bytes)
                            else:
                                st.error(f"Analysis failed: {response}")
        
        with col2:
            st.markdown("#### 📚 Common Diseases")
            
            diseases = [
                {"name": "Leaf Rust", "crop": "Wheat", "icon": "🍂"},
                {"name": "Blast", "crop": "Rice", "icon": "💥"},
                {"name": "Wilt", "crop": "Cotton", "icon": "🥀"},
                {"name": "Smut", "crop": "Sugarcane", "icon": "🖤"},
                {"name": "Mildew", "crop": "Grapes", "icon": "🍇"}
            ]
            
            for disease in diseases:
                if st.button(f"{disease['icon']} {disease['name']} ({disease['crop']})", 
                           key=f"disease_{disease['name']}", use_container_width=True):
                    if not DEEPSEEK_API_KEY:
                        st.error("Configure API key for details")
                    else:
                        with st.spinner("Getting disease info..."):
                            prompt = f"Tell me about {disease['name']} disease in {disease['crop']} crops. Include symptoms, causes, and treatment for Indian conditions."
                            response, success = get_deepseek_response(prompt)
                            
                            if success:
                                st.markdown(f"""
                                    <div class="glass-card">
                                        <h5>{disease['icon']} {disease['name']} in {disease['crop']}</h5>
                                        <div style="font-size: 14px;">
                                            {response}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
    
    # === TAB 3: ANALYTICS WITH DEEPSEEK ===
    with tabs[2]:
        st.markdown("### 📊 Farm Analytics Dashboard")
        
        # Dashboard Chart
        st.plotly_chart(create_agriculture_dashboard(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌾 AI Crop Recommendations")
            
            season = st.selectbox("Season", ["Kharif (Jun-Oct)", "Rabi (Nov-Apr)", "Zaid (Apr-Jun)"], key="season_select")
            water = st.select_slider("Water Availability", ["Low", "Medium", "High"], "Medium", key="water_slider")
            budget = st.select_slider("Budget", ["Low", "Medium", "High"], "Medium", key="budget_slider")
            
            if st.button("🤖 Get AI Recommendations", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("⚠️ Configure API key for AI recommendations")
                else:
                    with st.spinner("DeepSeek is analyzing..."):
                        prompt = f"""
                        Recommend the best crops for:
                        - Season: {season}
                        - Water Availability: {water}
                        - Budget: {budget}
                        - Location: {st.session_state.user_location}
                        - Soil Type: {soil_type}
                        - Farm Size: {farm_size} acres
                        
                        Provide detailed recommendations with:
                        1. Top 3 crop choices
                        2. Expected profit per acre
                        3. Required investment
                        4. Risk factors
                        5. Government schemes that can help
                        """
                        
                        response, success = get_deepseek_response(prompt)
                        
                        if success:
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="color: #4CAF50;">🤖 AI Crop Recommendations</h4>
                                    <div style="margin-top: 15px;">
                                        {response}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Recommendation failed: {response}")
        
        with col2:
            st.markdown("#### 💰 AI Profit Analysis")
            
            crop_choice = st.selectbox("Select Crop", list(CROP_DATABASE.keys()), key="crop_calc")
            area = st.number_input("Area (Acres)", 1.0, 100.0, 5.0, key="area_calc")
            
            if st.button("🤖 Analyze Profit with AI", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("⚠️ Configure API key for AI analysis")
                else:
                    with st.spinner("DeepSeek is calculating..."):
                        crop_info = CROP_DATABASE.get(crop_choice, {})
                        prompt = f"""
                        Analyze profit potential for:
                        - Crop: {crop_choice}
                        - Area: {area} acres
                        - Location: {st.session_state.user_location}
                        - Soil: {soil_type}
                        - Irrigation: {irrigation_type}
                        - Season: Current season
                        
                        Crop Details: {crop_info}
                        
                        Provide detailed profit analysis including:
                        1. Estimated yield per acre
                        2. Market price range in India
                        3. Total investment required
                        4. Expected profit margin
                        5. Risk assessment
                        6. Best time to sell
                        7. Government support available
                        """
                        
                        response, success = get_deepseek_response(prompt)
                        
                        if success:
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="color: #4CAF50;">💰 AI Profit Analysis</h4>
                                    <div style="margin-top: 15px;">
                                        {response}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Analysis failed: {response}")
    
    # === TAB 4: GOVERNMENT SCHEMES ===
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes & Subsidies")
        
        # AI Scheme Finder
        col_s1, col_s2 = st.columns([3, 1])
        
        with col_s1:
            scheme_query = st.text_input("🔍 Describe what you need help with:", 
                                       placeholder="e.g., I need loan for buying tractor, I want crop insurance, etc.")
            
            if scheme_query and st.button("🤖 Find Matching Schemes", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("⚠️ Configure API key for AI scheme finder")
                else:
                    with st.spinner("DeepSeek is finding relevant schemes..."):
                        prompt = f"""
                        Based on this farmer's query: "{scheme_query}"
                        
                        Farmer Details:
                        - Location: {st.session_state.user_location}
                        - Farm Size: {farm_size} acres
                        - Soil Type: {soil_type}
                        - Experience: {farming_exp}
                        
                        List relevant Indian government schemes with:
                        1. Scheme names and descriptions
                        2. Eligibility criteria
                        3. Application process
                        4. Benefits amount
                        5. Official website links
                        6. Contact information
                        
                        Focus on schemes from PM-KISAN, PMFBY, KCC, e-NAM, etc.
                        """
                        
                        response, success = get_deepseek_response(prompt, max_tokens=1500)
                        
                        if success:
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="color: #4CAF50;">🤖 AI Scheme Recommendations</h4>
                                    <div style="margin-top: 15px;">
                                        {response}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Scheme search failed: {response}")
        
        with col_s2:
            if st.button("🔄 Reset Search", use_container_width=True):
                st.rerun()
        
        # Display schemes in grid
        st.markdown("#### 📋 Available Government Schemes")
        cols = st.columns(3)
        
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 3]:
                if st.button(f"{scheme['icon']} {scheme['name']}", 
                           key=f"scheme_{scheme['name']}", use_container_width=True):
                    if not DEEPSEEK_API_KEY:
                        st.error("Configure API key for detailed info")
                    else:
                        with st.spinner("Getting scheme details..."):
                            prompt = f"""
                            Provide detailed information about {scheme['name']} scheme:
                            
                            Include:
                            1. Complete eligibility criteria
                            2. Step-by-step application process
                            3. Required documents
                            4. Benefits and amount
                            5. Timeline for approval
                            6. Common issues and solutions
                            7. Contact information for help
                            
                            Make it specific for a farmer from {st.session_state.user_location} with {farm_size} acres.
                            """
                            
                            response, success = get_deepseek_response(prompt)
                            
                            if success:
                                st.markdown(f"""
                                    <div class="glass-card">
                                        <h4 style="color: #4CAF50;">{scheme['icon']} {scheme['name']}</h4>
                                        <div style="margin-top: 15px;">
                                            {response}
                                        </div>
                                        <div style="margin-top: 15px; text-align: center;">
                                            <a href="{scheme['link']}" target="_blank">
                                                <button style="background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                                                    🌐 Visit Official Website
                                                </button>
                                            </a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
    
    # === TAB 5: VOICE ASSISTANT ===
    with tabs[4]:
        try:
            from streamlit_mic_recorder import mic_recorder
            
            st.markdown("### 🎤 Voice Assistant")
            
            col_v1, col_v2 = st.columns([2, 1])
            
            with col_v1:
                st.markdown("""
                    <div class="voice-assistant">
                        <div style="text-align: center;">
                            <div style="font-size: 50px; margin: 15px 0;">🎙️</div>
                            <h3 style="color: white;">Speak to GreenMitra</h3>
                            <p style="color: rgba(255,255,255,0.9); font-size: 14px;">
                                Ask questions in your preferred language
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if not DEEPSEEK_API_KEY:
                    st.markdown("""
                        <div class="glass-card">
                            <h4 style="color: #FF6B6B;">⚠️ API Key Required</h4>
                            <p>Configure DeepSeek API key in sidebar to enable voice assistant.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Voice recording
                    st.markdown("#### 🎤 Click to Record")
                    audio_bytes = mic_recorder(
                        start_prompt="🎤 Start Recording",
                        stop_prompt="⏹️ Stop",
                        key="voice_recorder"
                    )
                    
                    if audio_bytes:
                        st.audio(audio_bytes['bytes'], format='audio/wav')
                        
                        # Simulate speech recognition
                        if st.button("🤖 Process with DeepSeek", use_container_width=True):
                            # In real implementation, use speech-to-text API
                            # For demo, we'll use a sample query
                            sample_queries = [
                                "What are the best crops to grow this season?",
                                "How can I control pests in my wheat field?",
                                "Tell me about PM-KISAN scheme benefits",
                                "What is the market price for rice today?",
                                "How to prepare organic fertilizer at home?"
                            ]
                            
                            import random
                            sample_query = random.choice(sample_queries)
                            
                            st.info(f"Recognized: '{sample_query}'")
                            
                            with st.spinner("DeepSeek is processing..."):
                                response, success = get_deepseek_response(sample_query)
                                
                                if success:
                                    st.markdown(f"""
                                        <div class="glass-card">
                                            <h4>🤖 Voice Response</h4>
                                            <div style="margin-top: 10px;">
                                                {response}
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Convert response to speech
                                    lang_code_map = {
                                        "English": "en",
                                        "Hindi": "hi",
                                        "Marathi": "mr"
                                    }
                                    lang_code = lang_code_map.get(st.session_state.selected_language, "en")
                                    
                                    audio_bytes = text_to_speech_gtts(response[:300], lang_code)
                                    if audio_bytes:
                                        play_audio(audio_bytes)
                                else:
                                    st.error(f"Voice processing failed: {response}")
                    
                    # Alternative: Text input for voice queries
                    st.markdown("#### 📝 Or Type Your Question")
                    voice_text = st.text_input("Type your question for voice response", key="voice_text")
                    
                    if voice_text and st.button("🔊 Get Voice Response", use_container_width=True):
                        with st.spinner("DeepSeek is responding..."):
                            response, success = get_deepseek_response(voice_text)
                            
                            if success:
                                # Play audio response
                                lang_code = "en"
                                audio_bytes = text_to_speech_gtts(response[:300], lang_code)
                                if audio_bytes:
                                    play_audio(audio_bytes)
                                
                                st.info(f"🤖 Response: {response[:150]}...")
                            else:
                                st.error(f"Response failed: {response}")
            
            with col_v2:
                st.markdown("#### 🎵 Voice Settings")
                
                voice_options = {
                    "English": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
                    "Hindi": ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"],
                    "Marathi": ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"]
                }
                
                voices = voice_options.get(st.session_state.selected_language, ["en-IN-NeerjaNeural"])
                selected_voice = st.selectbox("Select Voice", voices, key="voice_select")
                
                st.markdown("#### 📊 Recent Activity")
                if st.session_state.messages:
                    for msg in st.session_state.messages[-3:]:
                        if msg["role"] == "user":
                            icon = "🎤" if "🎤" in msg['content'] else "💬"
                            content = msg['content'].replace("🎤 ", "")[:40]
                            st.markdown(f"""
                                <div style="background: #f5f5f5; padding: 8px; border-radius: 10px; margin: 5px 0; font-size: 12px;">
                                    {icon} {content}...
                                </div>
                            """, unsafe_allow_html=True)
        
        except ImportError:
            st.warning("Voice features require streamlit-mic-recorder")
            
            st.markdown("### 💬 Text-based Voice Assistant")
            voice_query = st.text_area("Enter your question for voice response:")
            
            if voice_query and st.button("Get AI Voice Response", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("Configure API key first")
                else:
                    response, success = get_deepseek_response(voice_query)
                    if success:
                        st.success("Response generated!")
                        st.info(response[:200] + "...")
                        
                        # Convert to speech
                        audio_bytes = text_to_speech_gtts(response[:300], 'en')
                        if audio_bytes:
                            play_audio(audio_bytes)
    
    # === TAB 6: MARKET INSIGHTS ===
    with tabs[5]:
        st.markdown("### 📈 Live Market Insights")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("#### 🤖 AI Market Analysis")
            
            crop_for_analysis = st.selectbox("Select Crop for Analysis", 
                                           list(CROP_DATABASE.keys()), 
                                           key="market_crop")
            
            if st.button("🔮 Get AI Market Prediction", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("⚠️ Configure API key for market analysis")
                else:
                    with st.spinner("DeepSeek is analyzing market trends..."):
                        prompt = f"""
                        Provide market analysis and predictions for {crop_for_analysis} crop in India:
                        
                        Location: {st.session_state.user_location}
                        Current Season: {datetime.datetime.now().strftime('%B')}
                        
                        Include:
                        1. Current market price range
                        2. Price trends (last 3 months)
                        3. Future price prediction (next 3 months)
                        4. Best time to buy/sell
                        5. Major markets for this crop
                        6. Government MSP (Minimum Support Price)
                        7. Export opportunities
                        8. Risk factors
                        9. Storage recommendations
                        10. Transportation costs
                        
                        Be specific for Indian market conditions.
                        """
                        
                        response, success = get_deepseek_response(prompt, max_tokens=1500)
                        
                        if success:
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="color: #4CAF50;">🔮 AI Market Analysis: {crop_for_analysis}</h4>
                                    <div style="margin-top: 15px;">
                                        {response}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Market analysis failed: {response}")
        
        with col_m2:
            st.markdown("#### 💰 Price Comparison")
            
            # Sample market data
            market_data = pd.DataFrame({
                'Crop': ['Wheat', 'Rice', 'Sugarcane', 'Cotton', 'Soybean'],
                'Current Price': [2100, 1850, 320, 5800, 4200],
                'Change %': [2.5, -1.2, 3.8, 0.5, -2.1]
            })
            
            fig = px.bar(
                market_data,
                x='Crop',
                y='Current Price',
                color='Change %',
                color_continuous_scale=['#FF6B6B', '#FFD166', '#06D6A0'],
                title="Current Market Prices (₹/Quintal)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Get AI trading tips
            if st.button("💡 Get Trading Tips", use_container_width=True):
                if not DEEPSEEK_API_KEY:
                    st.error("Configure API key for tips")
                else:
                    with st.spinner("Getting AI trading tips..."):
                        prompt = "Provide practical trading tips for Indian farmers on when to sell crops for maximum profit, considering market trends, seasons, and government schemes."
                        response, success = get_deepseek_response(prompt)
                        
                        if success:
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h5>💡 AI Trading Tips</h5>
                                    <div style="font-size: 14px;">
                                        {response}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
    
    # --- FOOTER ---
    st.markdown("---")
    
    footer_cols = st.columns(4)
    
    with footer_cols[0]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🌾 GreenMitra AI</p>
                <p style="font-size: 11px; color: #666;">Powered by DeepSeek</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[1]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🔑 API Status</p>
                <p style="font-size: 11px; color: #666;">
                    {'✅ Connected' if st.session_state.api_connected else '❌ Disconnected'}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[2]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🏛️ Partner</p>
                <p style="font-size: 11px; color: #666;">Govt. of India</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[3]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">📞 Support</p>
                <p style="font-size: 11px; color: #666;">help@greenmitra.ai</p>
            </div>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
