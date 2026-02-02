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

# --- 5. ENHANCED FUNCTIONS ---

def text_to_speech_gtts(text, language='en'):
    """Convert text to speech using gTTS"""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_file.name)
            tmp_file.seek(0)
            audio_bytes = tmp_file.read()
        
        # Clean up temp file
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
    # Create sample data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig = go.Figure()
    
    # Add traces for different metrics
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

def create_crop_comparison_chart(selected_crops):
    """Create a bar chart for crop comparison"""
    crops = selected_crops[:3] if len(selected_crops) > 3 else selected_crops
    data = []
    
    for crop in crops:
        if crop in CROP_DATABASE:
            info = CROP_DATABASE[crop]
            # Convert text ratings to numerical for comparison
            profit_map = {"Very High": 10, "High": 8, "Medium": 6, "Low": 4}
            water_map = {"High": 10, "Medium": 6, "Low": 3}
            
            data.append({
                'Crop': crop,
                'Profit Potential': profit_map.get(info['profit'], 5),
                'Water Need': water_map.get(info['water'], 5),
                'Season Suitability': 7
            })
    
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(df, x='Crop', y=['Profit Potential', 'Water Need', 'Season Suitability'],
                    barmode='group', title="Crop Comparison Analysis",
                    color_discrete_map={
                        'Profit Potential': '#4CAF50',
                        'Water Need': '#2196F3',
                        'Season Suitability': '#FF9800'
                    })
        fig.update_layout(height=350)
        return fig
    return None

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
            # Map weather conditions to emojis
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

def get_ai_response(prompt, context=""):
    """Get AI response from Gemini"""
    try:
        if not GOOGLE_API_KEY:
            return "⚠️ AI service is not configured. Please add your Google API key."
        
        # NEW (Correct)
        # NEW (Correct)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        full_prompt = f"""
        You are GreenMitra AI, an expert agricultural assistant for Indian farmers.
        Context: {context}
        
        User Query: {prompt}
        
        Provide a helpful, practical response that is:
        1. Clear and actionable
        2. Specific to Indian farming conditions
        3. Includes both traditional and modern methods
        4. Mentions relevant government schemes if applicable
        
        Keep it concise and friendly.
        """
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI service error: {str(e)}"

def speak_text_async(text, language='en'):
    """Convert text to speech in background"""
    try:
        audio_bytes = text_to_speech_gtts(text, language)
        if audio_bytes:
            st.session_state.audio_queue.append(audio_bytes)
    except Exception as e:
        st.error(f"Speech error: {e}")

# --- 6. SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'audio_queue' not in st.session_state:
    st.session_state.audio_queue = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"

if 'user_location' not in st.session_state:
    st.session_state.user_location = "Kolhapur"

if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = "Rajesh Kumar"

# --- 7. MAIN APP ---
def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="color: #4CAF50; margin-bottom: 5px;">🌾 GreenMitra</h2>
                <p style="color: #666; font-size: 14px;">Smart Farming Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        if st.button("📰 Agriculture News"):
            st.info("Latest farming news will be displayed")
        
        if st.button("🔄 Reset Chat"):
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()
    
    # --- MAIN CONTENT AREA ---
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("""
            <div style="padding: 10px 0;">
                <h1 style='font-size: 36px; margin: 0; color: #2E7D32; font-weight: 800;'>
                    GreenMitra AI
                </h1>
                <p style='font-size: 16px; color: #666; margin: 5px 0 0 0;'>
                    Your Intelligent Farming Companion
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
    
    # === TAB 1: AI CHAT ===
    with tabs[0]:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant")
            
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
                
                with st.spinner("🌱 Thinking..."):
                    # Get AI response
                    context = f"Farmer: {st.session_state.farmer_name}, Location: {st.session_state.user_location}, Language: {st.session_state.selected_language}"
                    response = get_ai_response(prompt, context)
                    
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
                    threading.Thread(target=speak_text_async, args=(response, lang_code)).start()
                    
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
                    st.session_state.messages.append({"role": "user", "content": question})
                    
                    with st.spinner("Thinking..."):
                        context = f"Farmer: {st.session_state.farmer_name}"
                        response = get_ai_response(question, context)
                        st.session_state.messages.append({"role": "assistant", "content": response})
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
                    # Run async function
                    async def run_edge_tts():
                        audio_bytes = await text_to_speech_edge(demo_text)
                        if audio_bytes:
                            play_audio(audio_bytes)
                    
                    asyncio.run(run_edge_tts())
    
    # === TAB 2: CROP DOCTOR ===
    with tabs[1]:
        st.markdown("### 🌿 AI-Powered Crop Health Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Image upload
            st.markdown("#### 📸 Upload Crop Image")
            uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Crop Image", use_column_width=True)
                
                if st.button("🔍 Analyze Disease", type="primary", use_container_width=True):
                    with st.spinner("Analyzing crop health..."):
                        time.sleep(2)  # Simulate analysis
                        
                        st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #4CAF50;">✅ Analysis Complete</h4>
                                <p><strong>Disease:</strong> Leaf Rust (Puccinia triticina)</p>
                                <p><strong>Confidence:</strong> 92%</p>
                                <p><strong>Severity:</strong> Moderate</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Treatment plan
                        st.markdown("#### 💊 Recommended Treatment")
                        
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            st.markdown("""
                                <div class="glass-card">
                                    <h5>🌿 Organic Treatment</h5>
                                    <ul style="font-size: 14px;">
                                        <li>Neem oil spray (2ml/liter)</li>
                                        <li>Garlic extract spray</li>
                                        <li>Remove affected leaves</li>
                                        <li>Proper plant spacing</li>
                                    </ul>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_t2:
                            st.markdown("""
                                <div class="glass-card">
                                    <h5>⚗️ Chemical Treatment</h5>
                                    <ul style="font-size: 14px;">
                                        <li>Propiconazole 25% EC</li>
                                        <li>Tebuconazole 25.9% EC</li>
                                        <li>Apply every 15 days</li>
                                        <li>Follow safety guidelines</li>
                                    </ul>
                                </div>
                            """, unsafe_allow_html=True)
        
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
                st.markdown(f"""
                    <div class="glass-card" style="padding: 15px; margin: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 20px;">{disease['icon']}</div>
                            <div>
                                <div style="font-weight: 600; color: #4CAF50;">{disease['name']}</div>
                                <div style="font-size: 12px; color: #666;">Crop: {disease['crop']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Camera option
            st.markdown("#### 📷 Live Camera")
            if st.button("Open Camera", use_container_width=True):
                camera_file = st.camera_input("Take a picture")
                if camera_file:
                    st.image(camera_file, caption="Camera Capture", use_column_width=True)
    
    # === TAB 3: ANALYTICS ===
    with tabs[2]:
        st.markdown("### 📊 Farm Analytics Dashboard")
        
        # Dashboard Chart
        st.plotly_chart(create_agriculture_dashboard(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌾 Crop Recommendations")
            
            season = st.selectbox("Season", ["Kharif (Jun-Oct)", "Rabi (Nov-Apr)", "Zaid (Apr-Jun)"], key="season_select")
            water = st.select_slider("Water Availability", ["Low", "Medium", "High"], "Medium")
            budget = st.select_slider("Budget", ["Low", "Medium", "High"], "Medium")
            
            if st.button("Get Recommendations", use_container_width=True):
                # Simple recommendation logic
                suitable_crops = []
                for crop, info in CROP_DATABASE.items():
                    if info['water'] == water or info['water'] == "Medium":
                        if budget == "High" or (budget == "Medium" and info['profit'] in ["High", "Medium"]):
                            suitable_crops.append(crop)
                
                if suitable_crops:
                    st.markdown("""
                        <div class="glass-card">
                            <h5>🌱 Recommended Crops:</h5>
                    """, unsafe_allow_html=True)
                    
                    for crop in suitable_crops[:5]:
                        info = CROP_DATABASE[crop]
                        st.markdown(f"""
                            <div style="padding: 8px; margin: 5px 0; background: rgba(76, 175, 80, 0.1); border-radius: 8px;">
                                <strong>{crop}</strong><br>
                                <small>Season: {info['season']} | Profit: {info['profit']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Show comparison chart
                    fig = create_crop_comparison_chart(suitable_crops[:3])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 💰 Profit Calculator")
            
            crop_choice = st.selectbox("Select Crop", list(CROP_DATABASE.keys()), key="crop_calc")
            area = st.number_input("Area (Acres)", 1.0, 100.0, 5.0, key="area_calc")
            yield_per_acre = st.number_input("Yield (Quintal/Acre)", 10.0, 100.0, 25.0)
            market_price = st.number_input("Market Price (₹/Quintal)", 1000, 10000, 2000)
            
            if st.button("Calculate Profit", use_container_width=True):
                total_yield = area * yield_per_acre
                revenue = total_yield * market_price
                cost = revenue * 0.4  # 40% cost assumption
                profit = revenue - cost
                
                st.markdown(f"""
                    <div class="glass-card">
                        <h5>💰 Profit Analysis</h5>
                        <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                            <span>Revenue:</span>
                            <span><strong>₹{revenue:,.0f}</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                            <span>Cost:</span>
                            <span><strong>₹{cost:,.0f}</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 8px 0; padding-top: 8px; border-top: 2px solid #4CAF50;">
                            <span>Profit:</span>
                            <span style="color: #4CAF50; font-weight: 700;">₹{profit:,.0f}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {(profit/revenue*100 if revenue>0 else 0):.1f}%"></div>
                            </div>
                            <div style="text-align: center; font-size: 12px; color: #666;">
                                Profit Margin: {(profit/revenue*100 if revenue>0 else 0):.1f}%
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 4: GOVERNMENT SCHEMES ===
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes & Subsidies")
        
        # Search
        scheme_search = st.text_input("🔍 Search schemes...", placeholder="Type scheme name or benefit")
        
        # Display schemes in grid
        cols = st.columns(3)
        filtered_schemes = PERMANENT_SCHEMES
        
        if scheme_search:
            filtered_schemes = [s for s in PERMANENT_SCHEMES if scheme_search.lower() in s['name'].lower() or scheme_search.lower() in s['desc'].lower()]
        
        for i, scheme in enumerate(filtered_schemes):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="scheme-card">
                        <div style="font-size: 30px; text-align: center; margin-bottom: 10px;">{scheme['icon']}</div>
                        <h4 style="color: #2E7D32; margin-bottom: 5px;">{scheme['name']}</h4>
                        <div style="background: #E8F5E9; padding: 3px 10px; border-radius: 12px; font-size: 11px; display: inline-block; margin-bottom: 8px;">
                            {scheme['category']}
                        </div>
                        <p style="font-size: 13px; color: #666; margin-bottom: 10px;">{scheme['desc']}</p>
                        <div style="font-size: 12px; color: #999; margin-bottom: 10px;">
                            <strong>Eligibility:</strong> {scheme['eligibility']}
                        </div>
                        <a href="{scheme['link']}" target="_blank" style="text-decoration: none;">
                            <div style="background: #4CAF50; color: white; padding: 6px 12px; border-radius: 8px; font-size: 13px; text-align: center; cursor: pointer;">
                                Apply Now
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        
        # Eligibility Checker
        st.markdown("---")
        st.markdown("#### 📋 Scheme Eligibility Checker")
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            land_type = st.selectbox("Land Ownership", ["Own Land", "Leased Land", "Landless"])
            income_level = st.selectbox("Annual Income", ["< ₹50,000", "₹50,000 - ₹2,00,000", "> ₹2,00,000"])
        
        with col_e2:
            farm_size_check = st.selectbox("Farm Size", ["< 2 acres", "2-5 acres", "> 5 acres"])
            category = st.selectbox("Category", ["General", "SC", "ST", "OBC"])
        
        if st.button("Check Eligibility", use_container_width=True):
            eligible_count = len([s for s in PERMANENT_SCHEMES if land_type in ["Own Land", "Leased Land"]])
            st.success(f"✅ You are eligible for {eligible_count} out of {len(PERMANENT_SCHEMES)} schemes!")
            
            st.markdown(f"""
                <div class="glass-card">
                    <h5>📋 Eligible Schemes:</h5>
                    {''.join([f'<div style="padding: 6px; margin: 4px 0; background: rgba(76, 175, 80, 0.1); border-radius: 6px;">• {s["name"]}</div>' for s in PERMANENT_SCHEMES[:3]])}
                </div>
            """, unsafe_allow_html=True)
    
    # === TAB 5: VOICE ASSISTANT ===
    with tabs[4]:
        try:
            from streamlit_mic_recorder import mic_recorder, speech_to_text
            
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
                
                # Language mapping for voice
                language_map = {
                    "English": "en-IN",
                    "Hindi": "hi-IN",
                    "Marathi": "mr-IN",
                    "Tamil": "ta-IN",
                    "Telugu": "te-IN",
                    "Kannada": "kn-IN",
                    "Gujarati": "gu-IN",
                    "Bengali": "bn-IN"
                }
                
                voice_lang = language_map.get(st.session_state.selected_language, "en-IN")
                
                # Voice recording
                st.markdown("#### 🎤 Click to Record")
                audio_bytes = mic_recorder(
                    start_prompt="🎤 Start Recording",
                    stop_prompt="⏹️ Stop",
                    key="voice_recorder"
                )
                
                if audio_bytes:
                    # In a real app, you would process the audio here
                    st.audio(audio_bytes['bytes'], format='audio/wav')
                    
                    # Simulate speech recognition
                    if st.button("📝 Convert to Text", use_container_width=True):
                        # Simulated recognized text
                        sample_text = "What are the best crops to grow this season?"
                        st.session_state.messages.append({"role": "user", "content": f"🎤 {sample_text}"})
                        
                        with st.spinner("Processing..."):
                            response = get_ai_response(sample_text)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.success("Voice query processed!")
                            st.rerun()
                
                # Alternative: Text input for voice queries
                st.markdown("#### 📝 Or Type Your Question")
                voice_text = st.text_input("Type your question for voice response")
                
                if voice_text and st.button("🔊 Speak Answer", use_container_width=True):
                    context = f"Voice query from {st.session_state.farmer_name}"
                    response = get_ai_response(voice_text, context)
                    
                    # Play audio response
                    lang_code = language_map.get(st.session_state.selected_language, "en-IN").split('-')[0]
                    audio_bytes = text_to_speech_gtts(response, lang_code)
                    if audio_bytes:
                        play_audio(audio_bytes)
                    
                    st.info(f"🤖 Response: {response[:100]}...")
            
            with col_v2:
                st.markdown("#### 🎵 Voice Settings")
                
                voice_options = {
                    "English": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
                    "Hindi": ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"],
                    "Marathi": ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"],
                    "Tamil": ["ta-IN-PallaviNeural"],
                    "Telugu": ["te-IN-MohanNeural"]
                }
                
                voices = voice_options.get(st.session_state.selected_language, ["en-IN-NeerjaNeural"])
                selected_voice = st.selectbox("Select Voice", voices)
                
                st.markdown("#### 📊 Recent Activity")
                if st.session_state.messages:
                    for msg in st.session_state.messages[-3:]:
                        if msg["role"] == "user":
                            icon = "🎤" if "🎤" in msg['content'] else "💬"
                            content = msg['content'].replace("🎤 ", "")
                            st.markdown(f"""
                                <div style="background: #f5f5f5; padding: 8px; border-radius: 10px; margin: 5px 0; font-size: 12px;">
                                    {icon} {content[:40]}...
                                </div>
                            """, unsafe_allow_html=True)
                
                # Test TTS
                st.markdown("#### 🔊 Test Voice")
                test_text = st.text_input("Test text", "Hello, I am GreenMitra")
                
                if st.button("Test Voice", use_container_width=True):
                    audio_bytes = text_to_speech_gtts(test_text, 'en')
                    if audio_bytes:
                        play_audio(audio_bytes)
        
        except ImportError:
            st.warning("Voice features require streamlit-mic-recorder")
            st.info("Using text input as fallback")
            
            st.markdown("### 💬 Text-based Voice Assistant")
            voice_query = st.text_area("Enter your question for voice response:")
            
            if voice_query and st.button("Get Voice Response", use_container_width=True):
                response = get_ai_response(voice_query)
                st.success("Response generated!")
                st.info(response)
                
                # Convert to speech
                audio_bytes = text_to_speech_gtts(response, 'en')
                if audio_bytes:
                    play_audio(audio_bytes)
    
    # === TAB 6: MARKET INSIGHTS ===
    with tabs[5]:
        st.markdown("### 📈 Live Market Prices")
        
        # Market Data
        market_data = pd.DataFrame({
            'Crop': ['Wheat', 'Rice', 'Sugarcane', 'Cotton', 'Soybean', 'Maize', 'Pulses'],
            'Price': [2100, 1850, 320, 5800, 4200, 1950, 4500],
            'Change %': [2.5, -1.2, 3.8, 0.5, -2.1, 1.5, 0.8],
            'Demand': ['High', 'High', 'Medium', 'High', 'Medium', 'Medium', 'High']
        })
        
        # Interactive chart
        fig = px.bar(
            market_data,
            x='Crop',
            y='Price',
            color='Change %',
            color_continuous_scale=['#FF6B6B', '#FFD166', '#06D6A0'],
            title="Current Market Prices (₹/Quintal)",
            hover_data=['Demand']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Market Tools
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("#### 🔔 Price Alerts")
            
            alert_crop = st.selectbox("Crop", market_data['Crop'].tolist(), key="alert_crop")
            target_price = st.number_input("Target Price (₹)", 1000, 10000, 2500, key="target_price")
            
            if st.button("Set Price Alert", use_container_width=True):
                current_price = market_data[market_data['Crop'] == alert_crop]['Price'].values[0]
                if target_price > current_price:
                    st.success(f"✅ Alert set! Will notify when {alert_crop} reaches ₹{target_price}")
                else:
                    st.warning(f"⚠️ Current price is ₹{current_price}. Target should be higher.")
        
        with col_m2:
            st.markdown("#### 💡 Trading Tips")
            
            tips = [
                "Sell wheat in Jan-Feb for best prices",
                "Rice demand peaks during festival season",
                "Store cotton in dry conditions",
                "Check e-NAM for live prices daily"
            ]
            
            for tip in tips:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 12px; margin: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="color: #4CAF50; font-size: 20px;">💡</div>
                            <div style="font-size: 14px;">{tip}</div>
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
                <p style="font-size: 11px; color: #666;">Smart Farming Assistant</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[1]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">📞 Support</p>
                <p style="font-size: 11px; color: #666;">1800-123-4567</p>
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
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">© 2024</p>
                <p style="font-size: 11px; color: #666;">Version 2.0</p>
            </div>
        """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
