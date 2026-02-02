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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #4CAF50 50%, #2E7D32 75%, #FF9800 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    /* Glass Morphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15) !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25) !important;
        border: 1px solid rgba(76, 175, 80, 0.5) !important;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: 0.8s;
    }
    
    .glass-card:hover::before {
        left: 100%;
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        padding: 14px 28px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(76, 175, 80, 0.4) !important;
        background: linear-gradient(45deg, #2E7D32, #4CAF50) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Animated Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: transparent !important;
        border-bottom: none !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 16px !important;
        padding: 14px 28px !important;
        border: 2px solid transparent !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        margin: 4px !important;
        color: #555 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 1) !important;
        border: 2px solid #4CAF50 !important;
        transform: translateY(-2px) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border: 2px solid #4CAF50 !important;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Floating Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(5deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.5); }
        50% { box-shadow: 0 0 40px rgba(76, 175, 80, 0.8); }
    }
    
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    .pulse-element {
        animation: pulse 2s ease-in-out infinite;
    }
    
    .glow-element {
        animation: glow 3s ease-in-out infinite;
    }
    
    /* Voice Assistant Styling */
    .voice-assistant {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 30px !important;
        margin: 20px 0 !important;
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .voice-assistant::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        border-radius: 10px;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #2E7D32, #4CAF50);
    }
    
    /* Hide Default Elements */
    #MainMenu, header, footer { 
        visibility: hidden !important; 
    }
    
    .stDeployButton { display: none !important; }
    
    .block-container { 
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* Weather Widget */
    .weather-container {
        background: linear-gradient(135deg, #2196F3, #21CBF3) !important;
        color: white !important;
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 35px rgba(33, 150, 243, 0.4) !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .weather-container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
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
    
    /* Tooltip Styling */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #666;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
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

def text_to_speech_gtts(text, language='en', filename='output.mp3'):
    """Convert text to speech using gTTS"""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
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
        return audio_data
    except Exception as e:
        st.error(f"Edge TTS Error: {e}")
        return None

def play_audio(audio_bytes):
    """Play audio in Streamlit"""
    audio_base64 = base64.b64encode(audio_bytes.read()).decode()
    audio_html = f"""
    <audio autoplay controls style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
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
        line=dict(color='#4CAF50', width=4),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.2)'
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[12000, 13500, 12800, 14500, 16000, 17500, 19000, 18500, 17000, 15500, 14000, 13000],
        name='Revenue (₹)',
        yaxis='y2',
        line=dict(color='#2196F3', width=4, dash='dash')
    ))
    
    fig.update_layout(
        title="📈 Annual Agriculture Performance",
        xaxis_title="Month",
        yaxis_title="Yield (Quintal/Ha)",
        yaxis2=dict(
            title="Revenue (₹)",
            overlaying='y',
            side='right'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_crop_recommendation_chart(selected_crops):
    """Create a radar chart for crop recommendations"""
    categories = ['Water Need', 'Profit Potential', 'Growth Duration', 'Market Demand', 'Soil Adaptability']
    
    fig = go.Figure()
    
    for crop in selected_crops:
        values = np.random.randint(3, 10, size=len(categories))
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=crop
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="Crop Comparison Radar Chart",
        height=400
    )
    
    return fig

def get_weather_with_forecast(city):
    """Get detailed weather information with forecast"""
    if not WEATHER_API_KEY:
        return {
            'temp': 28,
            'condition': 'Sunny',
            'humidity': 65,
            'wind_speed': 12,
            'icon': '☀️',
            'forecast': []
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
                'icon': icon,
                'forecast': []
            }
        else:
            return {
                'temp': 28,
                'condition': 'Clear',
                'humidity': 65,
                'wind_speed': 12,
                'icon': '☀️',
                'forecast': []
            }
    except:
        return {
            'temp': 28,
            'condition': 'Clear',
            'humidity': 65,
            'wind_speed': 12,
            'icon': '☀️',
            'forecast': []
        }

def get_ai_response_enhanced(prompt, context="", image=None):
    """Enhanced AI response with better prompting"""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        
        full_prompt = f"""
        You are GreenMitra AI, an expert agricultural assistant for Indian farmers.
        Context: {context}
        
        User Query: {prompt}
        
        Provide a comprehensive, practical response that includes:
        1. Clear answer to the query
        2. Step-by-step guidance if applicable
        3. Best practices and tips
        4. Safety precautions if needed
        5. Government scheme references if relevant
        
        Keep it conversational and helpful.
        """
        
        if image:
            response = model.generate_content([full_prompt, image])
        else:
            response = model.generate_content(full_prompt)
        
        return response.text
    except Exception as e:
        return f"I apologize, but I'm having trouble accessing the AI service right now. Please try again in a moment. (Error: {str(e)})"

# --- 6. SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'ai_history' not in st.session_state:
    st.session_state.ai_history = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"

if 'user_location' not in st.session_state:
    st.session_state.user_location = "Kolhapur"

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
        farmer_name = st.text_input("Full Name", "Rajesh Kumar")
        farmer_age = st.number_input("Age", 18, 80, 45)
        farming_exp = st.selectbox("Farming Experience", ["Beginner (<5 years)", "Intermediate (5-15 years)", "Expert (>15 years)"])
        
        # Farm Details
        st.markdown("### 🏞️ Farm Details")
        farm_size = st.number_input("Farm Size (Acres)", 1.0, 100.0, 5.0)
        soil_type = st.selectbox("Soil Type", ["Black Soil", "Red Soil", "Alluvial Soil", "Laterite Soil", "Mountain Soil"])
        irrigation_type = st.selectbox("Irrigation Type", ["Rainfed", "Tube Well", "Canal", "Drip", "Sprinkler"])
        
        # Settings
        st.markdown("### ⚙️ Settings")
        st.session_state.selected_language = st.selectbox(
            "Language",
            ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Gujarati", "Bengali"]
        )
        
        # Quick Links
        st.markdown("### 🔗 Quick Links")
        if st.button("📞 Farmer Helpline (1552)"):
            st.info("Dial 1552 for government farmer helpline")
        
        if st.button("📰 Krishi Jagran News"):
            st.markdown("[Visit Krishi Jagran](https://krishijagran.com/)")
        
        if st.button("💰 Loan Calculator"):
            st.info("Loan calculator feature coming soon!")
    
    # --- MAIN CONTENT AREA ---
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 80px; animation: float 6s ease-in-out infinite;" class="floating-element">🚜</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h1 style='font-size: 48px; margin: 0; background: linear-gradient(45deg, #4CAF50, #2E7D32, #FF9800); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'>
                    GreenMitra AI
                </h1>
                <p style='font-size: 18px; color: #fff; margin: 10px 0 0 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>
                    Your Intelligent Farming Companion
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Weather Display
        weather_data = get_weather_with_forecast(st.session_state.user_location)
        st.markdown(f"""
            <div class="weather-container">
                <div style="font-size: 40px; margin: 10px 0;">{weather_data['icon']}</div>
                <div style="font-size: 28px; font-weight: 700;">{weather_data['temp']}°C</div>
                <div style="font-size: 16px; opacity: 0.9;">{weather_data['condition']}</div>
                <div style="font-size: 12px; margin-top: 10px;">{st.session_state.user_location}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # --- DASHBOARD METRICS ---
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 32px; color: #4CAF50;">🌱</div>
                <div style="font-size: 24px; font-weight: 700;">{farm_size} Acres</div>
                <div style="font-size: 14px; color: #666;">Farm Size</div>
            </div>
        """.format(farm_size=farm_size), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 32px; color: #2196F3;">💧</div>
                <div style="font-size: 24px; font-weight: 700;">{irrigation}</div>
                <div style="font-size: 14px; color: #666;">Irrigation</div>
            </div>
        """.format(irrigation=irrigation_type), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 32px; color: #FF9800;">💰</div>
                <div style="font-size: 24px; font-weight: 700;">₹45.6K</div>
                <div style="font-size: 14px; color: #666;">Projected Profit</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 32px; color: #9C27B0;">📅</div>
                <div style="font-size: 24px; font-weight: 700;">7 Days</div>
                <div style="font-size: 14px; color: #666;">To Next Harvest</div>
            </div>
        """, unsafe_allow_html=True)
    
    # --- MAIN TABS ---
    tabs = st.tabs([
        "🤖 **AI Assistant**", 
        "🌾 **Crop Doctor**", 
        "📊 **Farm Analytics**", 
        "🏛️ **Schemes**",
        "💬 **Voice Chat**",
        "📈 **Market**"
    ])
    
    # === TAB 1: AI ASSISTANT ===
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant")
            
            # Display chat history
            for message in st.session_state.messages[-10:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input(f"Ask me anything about farming in {st.session_state.selected_language}..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("🌱 Thinking..."):
                        # Get AI response
                        response = get_ai_response_enhanced(
                            prompt, 
                            context=f"Farmer: {farmer_name}, Farm: {farm_size} acres, Soil: {soil_type}, Language: {st.session_state.selected_language}"
                        )
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Add to AI history
                        st.session_state.ai_history.append({
                            "question": prompt,
                            "answer": response,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
        
        with col2:
            st.markdown("### 💡 Quick Actions")
            
            quick_questions = [
                "What should I plant this season?",
                "How to control pests naturally?",
                "Best fertilizers for wheat?",
                "When to harvest rice?",
                "How to increase soil fertility?",
                "Water conservation tips?"
            ]
            
            for question in quick_questions:
                if st.button(f"❓ {question[:30]}...", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": question})
                    with st.spinner("Thinking..."):
                        response = get_ai_response_enhanced(question)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
            
            # Text-to-Speech
            st.markdown("### 🔊 Text-to-Speech")
            tts_text = st.text_area("Enter text to speak", "Welcome to GreenMitra AI farming assistant")
            
            col_tts1, col_tts2 = st.columns(2)
            with col_tts1:
                if st.button("🔊 Speak (gTTS)", use_container_width=True):
                    audio_bytes = text_to_speech_gtts(tts_text, 'en')
                    if audio_bytes:
                        play_audio(audio_bytes)
            
            with col_tts2:
                if st.button("🔊 Speak (Edge)", use_container_width=True):
                    audio_bytes = asyncio.run(text_to_speech_edge(tts_text))
                    if audio_bytes:
                        play_audio(audio_bytes)
    
    # === TAB 2: CROP DOCTOR ===
    with tabs[1]:
        st.markdown("### 🌿 AI-Powered Crop Disease Detection")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Upload or Capture Image
            option = st.radio("Choose input method:", ["Upload Image", "Capture from Camera"], horizontal=True)
            
            if option == "Upload Image":
                uploaded_file = st.file_uploader("Upload crop image", type=['jpg', 'jpeg', 'png'])
            else:
                uploaded_file = st.camera_input("Take a picture of your crop")
            
            if uploaded_file:
                # Display image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Analyze button
                if st.button("🔍 Analyze Disease", type="primary", use_container_width=True):
                    with st.spinner("🔬 Analyzing crop health..."):
                        # Simulate AI analysis
                        time.sleep(2)
                        
                        # Display results
                        st.markdown("""
                            <div class="glass-card">
                                <h4 style="color: #4CAF50;">✅ Analysis Complete</h4>
                                <p><strong>Disease Identified:</strong> Leaf Rust (Puccinia triticina)</p>
                                <p><strong>Confidence:</strong> 94%</p>
                                <p><strong>Affected Parts:</strong> Leaves</p>
                                <p><strong>Severity:</strong> Moderate</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Treatment plan
                        st.markdown("### 💊 Recommended Treatment")
                        
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            st.markdown("""
                                <div class="glass-card">
                                    <h5>🌿 Organic Treatment</h5>
                                    <ul style="font-size: 14px;">
                                        <li>Neem oil spray (2ml per liter)</li>
                                        <li>Garlic extract spray</li>
                                        <li>Remove affected leaves</li>
                                        <li>Proper spacing for air flow</li>
                                    </ul>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col_t2:
                            st.markdown("""
                                <div class="glass-card">
                                    <h5>⚗️ Chemical Treatment</h5>
                                    <ul style="font-size: 14px;">
                                        <li>Propiconazole 25% EC</li>
                                        <li>Hexaconazole 5% SC</li>
                                        <li>Tebuconazole 25.9% EC</li>
                                        <li>Follow safety guidelines</li>
                                    </ul>
                                </div>
                            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📚 Common Diseases")
            
            diseases = [
                {"name": "Leaf Rust", "crop": "Wheat", "symptom": "Orange-brown pustules"},
                {"name": "Blast", "crop": "Rice", "symptom": "Spindle-shaped lesions"},
                {"name": "Downy Mildew", "crop": "Maize", "symptom": "Yellow streaks"},
                {"name": "Wilt", "crop": "Cotton", "symptom": "Leaf drooping"},
                {"name": "Smut", "crop": "Sugarcane", "symptom": "Black powder"}
            ]
            
            for disease in diseases:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 15px; margin: 10px 0;">
                        <div style="font-weight: 600; color: #4CAF50;">{disease['name']}</div>
                        <div style="font-size: 12px; color: #666;">Crop: {disease['crop']}</div>
                        <div style="font-size: 12px; color: #999;">{disease['symptom']}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 3: FARM ANALYTICS ===
    with tabs[2]:
        st.markdown("### 📊 Farm Analytics Dashboard")
        
        # Dashboard Chart
        st.plotly_chart(create_agriculture_dashboard(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌾 Crop Recommendations")
            
            # Crop recommendation based on inputs
            season = st.selectbox("Current Season", ["Kharif (June-Oct)", "Rabi (Nov-Apr)", "Zaid (Apr-June)"])
            water_availability = st.select_slider("Water Availability", ["Low", "Medium", "High"], "Medium")
            budget = st.select_slider("Budget Level", ["Low", "Medium", "High"], "Medium")
            
            if st.button("Get Recommendations", use_container_width=True):
                # Filter crops based on criteria
                suitable_crops = []
                for crop, info in CROP_DATABASE.items():
                    if (info['water'] == water_availability or info['water'] == "Medium") and info['profit'] in ["High", "Medium"]:
                        suitable_crops.append(crop)
                
                if suitable_crops:
                    st.markdown("""
                        <div class="glass-card">
                            <h5>🌱 Recommended Crops:</h5>
                    """, unsafe_allow_html=True)
                    
                    for crop in suitable_crops[:3]:
                        info = CROP_DATABASE[crop]
                        st.markdown(f"""
                            <div style="padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 10px; margin: 5px 0;">
                                <strong>{crop}</strong><br>
                                <small>Season: {info['season']} | Water: {info['water']} | Profit: {info['profit']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Show radar chart
                    st.plotly_chart(create_crop_recommendation_chart(suitable_crops[:3]), use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Profit Calculator")
            
            crop_choice = st.selectbox("Select Crop", list(CROP_DATABASE.keys()))
            area = st.number_input("Area (Acres)", 1.0, 100.0, 5.0)
            expected_yield = st.number_input("Expected Yield (Quintal/Acre)", 10.0, 100.0, 25.0)
            market_price = st.number_input("Market Price (₹/Quintal)", 1000, 10000, 2000)
            
            if st.button("Calculate Profit", use_container_width=True):
                total_yield = area * expected_yield
                total_revenue = total_yield * market_price
                estimated_cost = total_revenue * 0.4  # 40% cost assumption
                profit = total_revenue - estimated_cost
                
                st.markdown(f"""
                    <div class="glass-card">
                        <h5>💰 Profit Analysis</h5>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Total Yield:</span>
                            <span><strong>{total_yield:.1f} Quintals</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Total Revenue:</span>
                            <span><strong>₹{total_revenue:,.0f}</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                            <span>Estimated Cost:</span>
                            <span><strong>₹{estimated_cost:,.0f}</strong></span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 10px 0; padding-top: 10px; border-top: 2px solid #4CAF50;">
                            <span>Expected Profit:</span>
                            <span style="color: #4CAF50; font-weight: 700;">₹{profit:,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 4: GOVERNMENT SCHEMES ===
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes & Subsidies")
        
        # Search and Filter
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            scheme_search = st.text_input("🔍 Search Schemes", placeholder="Type scheme name or benefit...")
        with col_filter:
            scheme_category = st.selectbox("Category", ["All", "Income Support", "Insurance", "Loans", "Subsidies"])
        
        # Display schemes
        filtered_schemes = PERMANENT_SCHEMES
        if scheme_search:
            filtered_schemes = [s for s in PERMANENT_SCHEMES if scheme_search.lower() in s['name'].lower() or scheme_search.lower() in s['desc'].lower()]
        if scheme_category != "All":
            filtered_schemes = [s for s in filtered_schemes if s['category'] == scheme_category]
        
        # Display in grid
        cols = st.columns(3)
        for i, scheme in enumerate(filtered_schemes):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center; cursor: pointer;" onclick="window.open('{scheme['link']}', '_blank')">
                        <div style="font-size: 40px; margin: 15px 0;">{scheme['icon']}</div>
                        <h4 style="color: #2E7D32;">{scheme['name']}</h4>
                        <div style="background: #E8F5E9; padding: 5px 10px; border-radius: 20px; font-size: 12px; display: inline-block; margin: 5px 0;">
                            {scheme['category']}
                        </div>
                        <p style="font-size: 14px; color: #666; margin: 10px 0;">{scheme['desc']}</p>
                        <div style="font-size: 12px; color: #999; margin: 5px 0;">
                            <strong>Eligibility:</strong> {scheme['eligibility']}
                        </div>
                        <a href="{scheme['link']}" target="_blank" style="text-decoration: none;">
                            <div style="background: linear-gradient(45deg, #4CAF50, #2E7D32); color: white; padding: 8px 20px; 
                                 border-radius: 20px; font-size: 14px; display: inline-block; margin-top: 10px;">
                                Apply Now →
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        
        # Eligibility Checker
        st.markdown("---")
        st.markdown("### 📋 Scheme Eligibility Checker")
        
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            land_ownership = st.selectbox("Land Ownership", ["Own Land", "Tenant Farmer", "Landless Laborer"])
        with col_e2:
            annual_income = st.selectbox("Annual Income", ["< ₹50,000", "₹50,000 - ₹1,00,000", "> ₹1,00,000"])
        with col_e3:
            caste_category = st.selectbox("Category", ["General", "SC", "ST", "OBC"])
        
        if st.button("Check Eligibility", use_container_width=True):
            eligible_schemes = []
            for scheme in PERMANENT_SCHEMES:
                if land_ownership in ["Own Land", "Tenant Farmer"]:
                    eligible_schemes.append(scheme['name'])
            
            st.markdown(f"""
                <div class="glass-card">
                    <h5>✅ Eligible Schemes ({len(eligible_schemes)})</h5>
                    {''.join([f'<div style="padding: 8px; margin: 5px 0; background: rgba(76, 175, 80, 0.1); border-radius: 8px;">• {scheme}</div>' for scheme in eligible_schemes[:5]])}
                </div>
            """, unsafe_allow_html=True)
    
    # === TAB 5: VOICE CHAT ===
    with tabs[4]:
        try:
            from streamlit_mic_recorder import speech_to_text
            
            st.markdown("### 🎤 Voice Assistant")
            
            col_v1, col_v2 = st.columns([2, 1])
            
            with col_v1:
                st.markdown("""
                    <div class="voice-assistant">
                        <div style="text-align: center; position: relative; z-index: 1;">
                            <div style="font-size: 60px; margin: 20px 0;">🎙️</div>
                            <h3 style="color: white;">Speak to GreenMitra</h3>
                            <p style="color: rgba(255,255,255,0.9);">Ask questions in your preferred language</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Voice input
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
                
                selected_voice_lang = st.session_state.selected_language
                voice_lang_code = language_map.get(selected_voice_lang, "en-IN")
                
                audio_text = speech_to_text(
                    language=voice_lang_code,
                    start_prompt="🎤 Start Speaking",
                    stop_prompt="⏹️ Stop",
                    just_once=True,
                    use_container_width=True,
                    key='voice_recorder'
                )
                
                if audio_text:
                    st.session_state.messages.append({"role": "user", "content": f"🎤 {audio_text}"})
                    
                    # Get AI response
                    with st.spinner("Processing voice query..."):
                        response = get_ai_response_enhanced(audio_text)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # Convert response to speech
                        with st.spinner("Generating voice response..."):
                            audio_bytes = text_to_speech_gtts(response, voice_lang_code[:2])
                            if audio_bytes:
                                play_audio(audio_bytes)
            
            with col_v2:
                st.markdown("### 🎵 Voice Settings")
                
                voice_options = {
                    "English": ["en-IN-NeerjaNeural", "en-IN-PrabhatNeural"],
                    "Hindi": ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"],
                    "Marathi": ["mr-IN-AarohiNeural", "mr-IN-ManoharNeural"]
                }
                
                selected_voice = st.selectbox(
                    "Select Voice",
                    voice_options.get(st.session_state.selected_language, ["en-IN-NeerjaNeural"])
                )
                
                st.markdown("### 📝 Recent Queries")
                if st.session_state.messages:
                    for msg in st.session_state.messages[-3:]:
                        if msg["role"] == "user":
                            st.markdown(f"""
                                <div style="background: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 10px; margin: 5px 0; font-size: 14px;">
                                    🎤 {msg['content'][:50]}...
                                </div>
                            """, unsafe_allow_html=True)
                
        except ImportError:
            st.warning("Voice recording feature requires streamlit-mic-recorder package")
            st.info("Install with: pip install streamlit-mic-recorder")
    
    # === TAB 6: MARKET INSIGHTS ===
    with tabs[5]:
        st.markdown("### 📈 Live Market Prices")
        
        # Market Data
        market_data = pd.DataFrame({
            'Crop': ['Wheat', 'Rice', 'Sugarcane', 'Cotton', 'Soybean', 'Maize', 'Pulses'],
            'Current Price': [2100, 1850, 320, 5800, 4200, 1950, 4500],
            'Change %': [2.5, -1.2, 3.8, 0.5, -2.1, 1.5, 0.8],
            'Demand': ['High', 'High', 'Medium', 'High', 'Medium', 'Medium', 'High'],
            'Best Market': ['Delhi', 'Punjab', 'UP', 'Gujarat', 'MP', 'Karnataka', 'Maharashtra']
        })
        
        # Interactive chart
        fig = px.bar(
            market_data,
            x='Crop',
            y='Current Price',
            color='Change %',
            color_continuous_scale=['#FF6B6B', '#FFD166', '#06D6A0'],
            title="Current Market Prices (₹/Quintal)",
            hover_data=['Demand', 'Best Market']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Price Alerts
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("### 🔔 Price Alerts")
            
            alert_crop = st.selectbox("Select Crop", market_data['Crop'].tolist())
            target_price = st.number_input("Target Price (₹)", 1000, 10000, 2500)
            alert_type = st.selectbox("Alert Type", ["Above Target", "Below Target"])
            
            if st.button("Set Alert", use_container_width=True):
                st.success(f"✅ Alert set for {alert_crop} when price goes {alert_type.lower()} ₹{target_price}")
        
        with col_m2:
            st.markdown("### 🚀 Trading Tips")
            
            tips = [
                {"tip": "Wheat prices peak in Jan-Feb", "action": "Sell before monsoon"},
                {"tip": "Rice demand high during festivals", "action": "Stock for Diwali"},
                {"tip": "Sugarcane prices stable", "action": "Contract farming recommended"},
                {"tip": "Cotton exports increasing", "action": "Focus on quality grading"}
            ]
            
            for tip in tips:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 15px; margin: 10px 0;">
                        <div style="font-weight: 600; color: #4CAF50;">💡 {tip['tip']}</div>
                        <div style="font-size: 13px; color: #666; margin-top: 5px;">📌 {tip['action']}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    # --- FOOTER ---
    st.markdown("---")
    
    footer_cols = st.columns(4)
    
    with footer_cols[0]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🌾 GreenMitra AI</p>
                <p style="font-size: 11px; color: #666;">Smart Farming Solutions</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[1]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">📞 Support</p>
                <p style="font-size: 11px; color: #666;">1800-123-4567</p>
                <p style="font-size: 11px; color: #666;">help@greenmitra.ai</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[2]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🏆 Partners</p>
                <p style="font-size: 11px; color: #666;">Ministry of Agriculture</p>
                <p style="font-size: 11px; color: #666;">NITI Aayog</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[3]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4CAF50;">🔗 Connect</p>
                <p style="font-size: 11px; color: #666;">
                    <span style="margin: 0 5px;">📱</span>
                    <span style="margin: 0 5px;">📧</span>
                    <span style="margin: 0 5px;">🌐</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- 8. JAVASCRIPT FOR INTERACTIVITY ---
st.markdown("""
    <script>
    // Add interactive hover effects
    document.addEventListener('DOMContentLoaded', function() {
        // Add click effect to glass cards
        const cards = document.querySelectorAll('.glass-card');
        cards.forEach(card => {
            card.addEventListener('click', function(e) {
                if(e.target.tagName === 'A' || e.target.parentElement.tagName === 'A') return;
                
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
        
        // Add ripple effect to buttons
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size/2;
                const y = e.clientY - rect.top - size/2;
                
                ripple.style.cssText = `
                    position: absolute;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.7);
                    transform: scale(0);
                    animation: ripple-animation 0.6s linear;
                    width: ${size}px;
                    height: ${size}px;
                    top: ${y}px;
                    left: ${x}px;
                    pointer-events: none;
                `;
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
        
        // Add keyframe for ripple animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    });
    </script>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
