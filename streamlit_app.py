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
    # Initialize new Google GenAI client
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

# --- 3. ULTRA-MODERN CSS WITH GLASSMORPHISM & ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --secondary: #3B82F6;
        --accent: #F59E0B;
        --bg-light: #f0fdf4;
        --glass-bg: rgba(255, 255, 255, 0.85);
        --glass-border: rgba(255, 255, 255, 0.5);
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #d1fae5 100%);
        background-attachment: fixed;
    }
    
    /* Advanced Glassmorphism */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-radius: 24px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow), 0 0 0 1px rgba(255,255,255,0.5) inset;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255,255,255,0.8) inset;
    }
    
    .glass-card:hover::before {
        opacity: 1;
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #10B981, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Neon Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white !important;
        border-radius: 16px;
        border: none;
        font-weight: 600;
        font-size: 15px;
        padding: 14px 28px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3), 0 0 0 1px rgba(255,255,255,0.2) inset;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            to right,
            rgba(255,255,255,0) 0%,
            rgba(255,255,255,0.3) 50%,
            rgba(255,255,255,0) 100%
        );
        transform: rotate(30deg);
        transition: all 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4), 0 0 0 1px rgba(255,255,255,0.3) inset;
    }
    
    .stButton > button:hover::after {
        left: 100%;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.5);
        padding: 8px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 14px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        color: #6B7280;
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Floating Animation */
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(2deg); }
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.4); }
        50% { box-shadow: 0 0 40px rgba(16, 185, 129, 0.6); }
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    .pulse-glow {
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    /* Chat Bubbles Modern */
    .chat-bubble-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 20px 20px 0 20px;
        padding: 16px 20px;
        margin: 12px 0;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .chat-bubble-assistant {
        background: white;
        color: #1f2937;
        border-radius: 20px 20px 20px 0;
        padding: 16px 20px;
        margin: 12px 0;
        max-width: 85%;
        margin-right: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        position: relative;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .chat-bubble-assistant::before {
        content: '🌾';
        position: absolute;
        top: -10px;
        left: -10px;
        background: white;
        border-radius: 50%;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-size: 12px;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: all 0.4s ease;
        border: 1px solid rgba(255,255,255,0.5);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    /* Progress Bars */
    .progress-container {
        width: 100%;
        background: rgba(0,0,0,0.05);
        border-radius: 12px;
        margin: 12px 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .progress-bar {
        height: 12px;
        background: linear-gradient(90deg, var(--primary), #34d399, var(--secondary));
        background-size: 200% 200%;
        border-radius: 12px;
        transition: width 1s ease-out;
        animation: gradient-shift 3s ease infinite;
    }
    
    /* Scheme Cards */
    .scheme-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border-left: 6px solid var(--primary);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .scheme-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
        border-left-width: 10px;
    }
    
    /* Weather Widget Modern */
    .weather-widget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .weather-widget::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 10s ease-in-out infinite;
    }
    
    /* Voice Assistant Styling */
    .voice-assistant {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 24px;
        padding: 32px;
        margin: 20px 0;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .voice-assistant::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    /* Hide Default Elements */
    #MainMenu, header, footer { 
        visibility: hidden;
    }
    
    .stDeployButton { display: none !important; }
    
    .block-container { 
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 5px;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #059669, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-header {
        font-family: 'Space Grotesk', sans-serif;
        color: #6B7280;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Alert Boxes */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.1));
        border-left: 4px solid var(--primary);
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1));
        border-left: 4px solid var(--accent);
        padding: 16px;
        border-radius: 12px;
        margin: 12px 0;
    }
    
    /* Image Upload Zone */
    .upload-zone {
        border: 3px dashed var(--primary);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        background: rgba(16, 185, 129, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-zone:hover {
        background: rgba(16, 185, 129, 0.1);
        border-color: var(--secondary);
        transform: scale(1.02);
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 3px solid rgba(16, 185, 129, 0.3);
        border-radius: 50%;
        border-top-color: var(--primary);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. ENHANCED DATA & CONSTANTS ---

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
    },
    {
        "name": "Agriculture Infrastructure Fund",
        "desc": "Financing facility for farm gate infrastructure.",
        "link": "https://agriinfra.dac.gov.in/",
        "icon": "🏗️",
        "category": "Infrastructure",
        "eligibility": "Farmers, FPOs, SHGs"
    },
    {
        "name": "Paramparagat Krishi Vikas",
        "desc": "Promoting organic farming with certification.",
        "link": "https://pgsindia-ncof.gov.in/",
        "icon": "🍃",
        "category": "Organic Farming",
        "eligibility": "Farmers groups"
    }
]

CROP_DATABASE = {
    "Rice": {"season": "Kharif", "water": "High", "profit": "Medium", "duration": "120-150 days", "image": "🌾"},
    "Wheat": {"season": "Rabi", "water": "Medium", "profit": "High", "duration": "110-130 days", "image": "🌾"},
    "Sugarcane": {"season": "Annual", "water": "High", "profit": "High", "duration": "300-365 days", "image": "🎋"},
    "Cotton": {"season": "Kharif", "water": "Medium", "profit": "High", "duration": "150-180 days", "image": "🧶"},
    "Maize": {"season": "Kharif/Rabi", "water": "Medium", "profit": "Medium", "duration": "90-100 days", "image": "🌽"},
    "Pulses": {"season": "Rabi", "water": "Low", "profit": "Medium", "duration": "90-120 days", "image": "🫘"},
    "Vegetables": {"season": "All", "water": "High", "profit": "High", "duration": "60-90 days", "image": "🥬"},
    "Fruits": {"season": "Annual", "water": "Medium", "profit": "Very High", "duration": "Varies", "image": "🍎"},
    "Soybean": {"season": "Kharif", "water": "Medium", "profit": "High", "duration": "100-120 days", "image": "🫛"},
    "Groundnut": {"season": "Kharif/Rabi", "water": "Low", "profit": "High", "duration": "110-130 days", "image": "🥜"}
}

DISEASE_DATABASE = {
    "Leaf Rust": {
        "symptoms": "Orange-brown pustules on leaves",
        "organic": ["Neem oil spray", "Garlic extract", "Cow urine spray"],
        "chemical": ["Propiconazole", "Tebuconazole"],
        "crops": ["Wheat", "Barley"],
        "severity": "High"
    },
    "Powdery Mildew": {
        "symptoms": "White powdery patches on leaves",
        "organic": ["Baking soda spray", "Neem oil", "Milk spray"],
        "chemical": ["Sulfur fungicide", "Myclobutanil"],
        "crops": ["Grapes", "Mango", "Wheat"],
        "severity": "Medium"
    },
    "Blast": {
        "symptoms": "Diamond-shaped lesions on leaves",
        "organic": ["Trichoderma", "Neem cake"],
        "chemical": ["Carbendazim", "Mancozeb"],
        "crops": ["Rice"],
        "severity": "High"
    }
}

# --- 5. FIXED & ENHANCED FUNCTIONS ---

def get_ai_response(prompt, context="", image=None):
    """Enhanced AI response using new Google GenAI SDK"""
    try:
        if not GEMINI_AVAILABLE or not genai_client:
            return "⚠️ AI service is not configured. Please add a valid Google API key to secrets."
        
        # Use latest stable model - gemini-2.0-flash is recommended
        model_name = "gemini-2.0-flash"
        
        system_prompt = f"""You are GreenMitra AI Pro, an expert agricultural assistant for Indian farmers.
Context: {context}

Guidelines:
1. Provide practical, actionable advice for Indian farming conditions
2. Include both traditional and modern agricultural methods
3. Mention relevant government schemes when applicable
4. Be concise but comprehensive
5. If discussing pests/diseases, suggest both organic and chemical solutions
6. Consider local climate and soil conditions

User Query: {prompt}

Response:"""
        
        if image:
            # For image analysis
            response = genai_client.models.generate_content(
                model=model_name,
                contents=[system_prompt, image]
            )
        else:
            # Text only
            response = genai_client.models.generate_content(
                model=model_name,
                contents=system_prompt
            )
        
        return response.text if hasattr(response, 'text') else str(response)
    
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return "⚠️ Model error: Please ensure you're using gemini-2.0-flash or newer model. The old gemini-1.5-flash is deprecated."
        elif "API key" in error_msg:
            return "⚠️ Invalid API key. Please check your Google API key in secrets."
        else:
            return f"⚠️ AI Error: {error_msg}. Please try again."

def analyze_crop_disease(image, crop_type="Unknown"):
    """AI-powered crop disease analysis"""
    try:
        if not GEMINI_AVAILABLE:
            return {"error": "AI not available"}
        
        prompt = f"""Analyze this crop image for diseases. Crop type: {crop_type}.
Provide:
1. Disease name (if any)
2. Confidence level (percentage)
3. Symptoms visible
4. Organic treatment options (3-4 methods)
5. Chemical treatment options (if severe)
6. Prevention tips

Format as JSON with keys: disease, confidence, symptoms, organic_treatments, chemical_treatments, prevention, severity"""
        
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        
        # Parse JSON response
        text = response.text
        # Extract JSON if wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text)
    except Exception as e:
        return {
            "disease": "Analysis Error",
            "confidence": 0,
            "symptoms": "Could not analyze image",
            "organic_treatments": ["Please try again with clearer image"],
            "chemical_treatments": [],
            "prevention": ["Regular monitoring"],
            "severity": "Unknown",
            "error": str(e)
        }

def text_to_speech_gtts(text, language='en'):
    """Convert text to speech using gTTS with enhanced error handling"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            # Map language codes properly
            lang_map = {
                'en': 'en', 'hi': 'hi', 'mr': 'mr', 'ta': 'ta',
                'te': 'te', 'kn': 'kn', 'gu': 'gu', 'bn': 'bn',
                'pa': 'pa', 'ml': 'ml', 'ur': 'ur'
            }
            lang = lang_map.get(language, 'en')
            
            tts = gTTS(text=text[:500], lang=lang, slow=False, lang_check=False)  # Limit text length
            tts.save(tmp_file.name)
            
            with open(tmp_file.name, 'rb') as f:
                audio_bytes = f.read()
        
        os.unlink(tmp_file.name)
        return audio_bytes
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

def get_weather_with_forecast(city):
    """Enhanced weather with mock data fallback"""
    if not WEATHER_API_KEY:
        # Return realistic mock data for demo
        return {
            'temp': random.randint(25, 35),
            'condition': random.choice(['Sunny', 'Partly Cloudy', 'Cloudy']),
            'humidity': random.randint(40, 80),
            'wind_speed': random.randint(5, 20),
            'icon': '☀️',
            'forecast': [
                {'day': 'Tomorrow', 'temp': 30, 'icon': '⛅'},
                {'day': 'Day after', 'temp': 29, 'icon': '🌧️'}
            ]
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather_icons = {
                'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 
                'Drizzle': '🌦️', 'Thunderstorm': '⛈️', 'Snow': '❄️',
                'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '😶‍🌫️'
            }
            condition = data['weather'][0]['main']
            
            return {
                'temp': round(data['main']['temp']),
                'condition': condition,
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': weather_icons.get(condition, '🌤️'),
                'forecast': []
            }
        else:
            raise Exception("Weather API error")
    except:
        return {
            'temp': 28, 'condition': 'Sunny', 'humidity': 65,
            'wind_speed': 12, 'icon': '☀️', 'forecast': []
        }

def create_agriculture_dashboard():
    """Enhanced interactive dashboard"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = datetime.datetime.now().month - 1
    
    # Create realistic seasonal data
    seasonal_yield = [20, 22, 25, 35, 55, 75, 85, 80, 60, 45, 30, 25]
    revenue = [y * 1800 for y in seasonal_yield]  # ₹1800 per quintal
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=seasonal_yield,
        name='Yield (Quintal/Ha)',
        line=dict(color='#10B981', width=4),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)',
        hovertemplate='<b>%{x}</b><br>Yield: %{y} Q/Ha<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=months,
        y=revenue,
        name='Revenue (₹)',
        marker_color='#3B82F6',
        opacity=0.6,
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "📈 Annual Agriculture Performance",
            'font': {'size': 24, 'color': '#1f2937', 'family': 'Space Grotesk'},
            'x': 0.5
        },
        xaxis_title="Month",
        yaxis_title="Yield (Quintal/Ha)",
        yaxis2=dict(
            title="Revenue (₹)",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Add vertical line for current month
    fig.add_vline(x=current_month, line_width=2, line_dash="dash", line_color="#F59E0B")
    
    return fig

def create_crop_comparison_chart(selected_crops):
    """Enhanced radar chart for crop comparison"""
    if not selected_crops:
        return None
    
    categories = ['Profit Potential', 'Water Efficiency', 'Market Demand', 'Ease of Cultivation', 'Climate Resilience']
    
    fig = go.Figure()
    
    colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
    
    for i, crop in enumerate(selected_crops[:3]):
        if crop in CROP_DATABASE:
            info = CROP_DATABASE[crop]
            # Generate realistic scores based on crop properties
            profit_score = 10 if info['profit'] == "Very High" else (8 if info['profit'] == "High" else 6)
            water_score = 10 if info['water'] == "Low" else (5 if info['water'] == "High" else 7)
            
            values = [
                profit_score,
                water_score,
                random.randint(7, 10),  # Market demand
                random.randint(6, 9),   # Ease
                random.randint(5, 9)    # Resilience
            ]
            values += values[:1]  # Complete the circle
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=crop,
                line_color=colors[i % len(colors)],
                fillcolor=f'rgba{tuple(list(int(colors[i % len(colors)].lstrip("#")[j:j+2], 16) for j in (0, 2, 4)) + [0.2])}'
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="🌾 Crop Comparison Analysis",
        height=450
    )
    
    return fig

def get_farming_calendar():
    """Get seasonal farming calendar based on current month"""
    month = datetime.datetime.now().month
    
    if month in [6, 7, 8, 9]:  # Kharif
        return {
            "season": "Kharif (Monsoon)",
            "crops": ["Rice", "Cotton", "Soybean", "Maize"],
            "activities": ["Sowing", "Weeding", "Fertilizer application"],
            "color": "#10B981"
        }
    elif month in [10, 11, 12, 1]:  # Rabi
        return {
            "season": "Rabi (Winter)",
            "crops": ["Wheat", "Pulses", "Mustard", "Barley"],
            "activities": ["Sowing", "Irrigation", "Pest control"],
            "color": "#3B82F6"
        }
    else:  # Zaid
        return {
            "season": "Zaid (Summer)",
            "crops": ["Vegetables", "Fruits", "Fodder crops"],
            "activities": ["Harvesting", "Land preparation", "Irrigation management"],
            "color": "#F59E0B"
        }

def play_audio(audio_bytes):
    """Enhanced audio player"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay controls style="width: 100%; margin-top: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# --- 6. SESSION STATE INITIALIZATION ---
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🌾 Welcome to GreenMitra AI Pro! I'm your smart farming assistant. How can I help you today?"}
    ]

if 'audio_queue' not in st.session_state:
    st.session_state.audio_queue = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"

if 'user_location' not in st.session_state:
    st.session_state.user_location = "Kolhapur"

if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = "Rajesh Kumar"

if 'farm_data' not in st.session_state:
    st.session_state.farm_data = {
        "size": 5.0,
        "soil": "Black Soil",
        "irrigation": "Drip",
        "crops": []
    }

# --- 7. MAIN APP ---
def main():
    # --- SIDEBAR WITH ENHANCED UI ---
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1)); border-radius: 20px; margin-bottom: 20px;">
                <div style="font-size: 60px; margin-bottom: 10px; animation: float 3s ease-in-out infinite;">🌾</div>
                <h2 style="color: #059669; margin: 0; font-family: Space Grotesk; font-size: 28px;">GreenMitra</h2>
                <p style="color: #6B7280; font-size: 13px; margin-top: 5px;">Pro Edition • v3.0</p>
            </div>
        """, unsafe_allow_html=True)
        
        # API Status Indicator
        if GEMINI_AVAILABLE:
            st.markdown("""
                <div style="background: rgba(16,185,129,0.1); padding: 10px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(16,185,129,0.3);">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; animation: pulse-glow 2s infinite;"></div>
                        <span style="color: #059669; font-size: 12px; font-weight: 600;">AI Engine Online</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="warning-box">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #F59E0B; font-size: 12px; font-weight: 600;">⚠️ AI Engine Offline</span>
                    </div>
                    <p style="font-size: 11px; margin: 5px 0 0 0; color: #6B7280;">Add GOOGLE_API_KEY to secrets</p>
                </div>
            """, unsafe_allow_html=True)
        
        # User Profile
        st.markdown("### 👨‍🌾 Farmer Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.farmer_name = st.text_input("Name", st.session_state.farmer_name)
        with col2:
            farmer_age = st.number_input("Age", 18, 80, 45, key="age")
        
        farming_exp = st.select_slider("Experience", ["Beginner", "Intermediate", "Expert"])
        
        # Farm Details
        st.markdown("### 🏞️ Farm Details")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.farm_data["size"] = st.number_input("Size (Acres)", 0.1, 1000.0, 5.0)
        with col2:
            st.session_state.farm_data["soil"] = st.selectbox("Soil", ["Black Soil", "Red Soil", "Alluvial", "Laterite", "Sandy"])
        
        st.session_state.farm_data["irrigation"] = st.selectbox("Irrigation", ["Drip", "Sprinkler", "Flood", "Rainfed", "Tube Well"])
        
        # Location with Map
        st.markdown("### 📍 Location")
        st.session_state.user_location = st.text_input("Village/City", st.session_state.user_location)
        
        # Language
        st.markdown("### 🌐 Language")
        st.session_state.selected_language = st.selectbox(
            "Select",
            ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Gujarati", "Bengali", "Punjabi", "Malayalam"],
            index=["English", "Hindi", "Marathi", "Tamil", "Telugu", "Kannada", "Gujarati", "Bengali", "Punjabi", "Malayalam"].index(st.session_state.selected_language)
        )
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 Helpline", use_container_width=True):
                st.success("Dial 1552")
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        # Season Info
        calendar = get_farming_calendar()
        st.markdown(f"""
            <div style="background: {calendar['color']}15; padding: 15px; border-radius: 15px; margin-top: 20px; border-left: 4px solid {calendar['color']};">
                <h4 style="color: {calendar['color']}; margin: 0 0 8px 0; font-size: 14px;">Current Season: {calendar['season']}</h4>
                <p style="font-size: 12px; color: #4B5563; margin: 0;"><strong>Recommended:</strong> {', '.join(calendar['crops'][:3])}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # --- MAIN CONTENT AREA ---
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown("""
            <div style="padding: 10px 0;">
                <h1 class='main-header'>GreenMitra AI Pro</h1>
                <p class='sub-header'>Next-Gen Intelligent Farming Assistant</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Weather Display
    weather_data = get_weather_with_forecast(st.session_state.user_location)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 32px; margin-bottom: 8px;">{weather_data['icon']}</div>
                <div style="font-size: 28px; font-weight: 700; color: #1f2937; margin: 5px 0;">{weather_data['temp']}°C</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">{weather_data['condition']}</div>
                <div style="margin-top: 10px; font-size: 11px; color: #9CA3AF;">
                    💧 {weather_data['humidity']}% | 💨 {weather_data['wind_speed']} km/h
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 32px; margin-bottom: 8px;">🌱</div>
                <div style="font-size: 28px; font-weight: 700; color: #1f2937; margin: 5px 0;">{st.session_state.farm_data['size']}</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Acres</div>
                <div style="margin-top: 10px; font-size: 11px; color: #9CA3AF;">
                    {st.session_state.farm_data['soil']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        projected_revenue = int(st.session_state.farm_data['size'] * 45000)
        st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(52,211,153,0.1));">
                <div style="font-size: 32px; margin-bottom: 8px;">💰</div>
                <div style="font-size: 28px; font-weight: 700; color: #059669; margin: 5px 0;">₹{projected_revenue/1000:.1f}K</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Projected</div>
                <div style="margin-top: 10px; font-size: 11px; color: #10B981; font-weight: 600;">
                    ↑ 12% vs last year
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # --- MAIN TABS ---
    tabs = st.tabs([
        "🤖 **AI Assistant**", 
        "🔬 **Crop Doctor**", 
        "📊 **Analytics**", 
        "🏛️ **Schemes**",
        "🎙️ **Voice**",
        "📈 **Market**",
        "🗺️ **Map**"
    ])
    
    # === TAB 1: AI CHAT ENHANCED ===
    with tabs[0]:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant Pro")
            
            # Chat container with glass effect
            chat_container = st.container(height=450)
            with chat_container:
                for message in st.session_state.messages[-12:]:
                    if message["role"] == "user":
                        st.markdown(f"""
                            <div class="chat-bubble-user">
                                <strong>👤 You</strong><br>{message['content']}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="chat-bubble-assistant">
                                <strong>🌾 GreenMitra</strong><br>{message['content']}
                            </div>
                        """, unsafe_allow_html=True)
            
            # Chat input with suggestion chips
            cols = st.columns([4, 1])
            with cols[0]:
                prompt = st.chat_input("Ask me anything about farming...")
            
            # Suggestion pills
            suggestions = ["Best crop this season?", "Pest control tips", "Market prices", "Irrigation advice"]
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                        prompt = suggestion
            
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.spinner("🌱 Analyzing..."):
                    context = f"""
                    Farmer: {st.session_state.farmer_name}
                    Location: {st.session_state.user_location}
                    Farm Size: {st.session_state.farm_data['size']} acres
                    Soil: {st.session_state.farm_data['soil']}
                    Irrigation: {st.session_state.farm_data['irrigation']}
                    Language: {st.session_state.selected_language}
                    Experience: {farming_exp}
                    """
                    
                    response = get_ai_response(prompt, context)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Auto TTS for latest response
                    if st.session_state.messages[-1]["role"] == "assistant":
                        lang_map = {
                            "English": "en", "Hindi": "hi", "Marathi": "mr",
                            "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
                            "Gujarati": "gu", "Bengali": "bn", "Punjabi": "pa",
                            "Malayalam": "ml"
                        }
                        lang_code = lang_map.get(st.session_state.selected_language, "en")
                        audio_bytes = text_to_speech_gtts(response, lang_code)
                        if audio_bytes:
                            play_audio(audio_bytes)
                    
                    st.rerun()
        
        with col2:
            st.markdown("### 💡 Smart Suggestions")
            
            # Dynamic suggestions based on season
            calendar = get_farming_calendar()
            st.markdown(f"""
                <div class="glass-card" style="background: {calendar['color']}10; border-color: {calendar['color']}40;">
                    <h5 style="color: {calendar['color']}; margin-top: 0;">Season Tips</h5>
                    <p style="font-size: 13px; color: #4B5563;">{calendar['season']}</p>
                    <ul style="font-size: 12px; padding-left: 16px; color: #6B7280;">
                        {' '.join([f'<li>{activity}</li>' for activity in calendar['activities'][:3]])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            # Quick questions
            quick_questions = [
                "Disease identification",
                "Fertilizer calculator",
                "Weather advisory",
                "Organic farming methods"
            ]
            
            for question in quick_questions:
                if st.button(f"❓ {question}", key=f"q_{question}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": question})
                    response = get_ai_response(question, f"Farmer: {st.session_state.farmer_name}")
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
            
            # TTS Demo
            st.markdown("### 🔊 Voice Demo")
            demo_text = st.text_area("Text to speak:", "Welcome to GreenMitra AI Pro", height=80)
            if st.button("🔊 Speak", use_container_width=True):
                audio_bytes = text_to_speech_gtts(demo_text, 'en')
                if audio_bytes:
                    play_audio(audio_bytes)
    
    # === TAB 2: ENHANCED CROP DOCTOR ===
    with tabs[1]:
        st.markdown("### 🔬 AI Crop Health Analysis Pro")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enhanced upload zone
            st.markdown("""
                <div class="upload-zone" id="drop-zone">
                    <div style="font-size: 48px; margin-bottom: 10px;">📸</div>
                    <h4>Upload Crop Image</h4>
                    <p style="color: #6B7280; font-size: 14px;">Drag & drop or click to browse</p>
                </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], key="crop_upload")
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.image(image, caption="Original", use_container_width=True)
                
                with col_img2:
                    # Crop type selection
                    crop_type = st.selectbox("Select Crop Type", list(CROP_DATABASE.keys()), key="crop_type")
                    
                    if st.button("🔍 Analyze with AI", type="primary", use_container_width=True):
                        with st.spinner("🧬 Analyzing image with AI..."):
                            # Convert PIL to bytes for Gemini
                            img_byte_arr = io.BytesIO()
                            image.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            
                            # AI Analysis
                            result = analyze_crop_disease(image, crop_type)
                            
                            if "error" not in result or result.get("disease") != "Analysis Error":
                                st.success(f"✅ Analysis Complete - Confidence: {result.get('confidence', 0)}%")
                                
                                # Display results in glass card
                                severity_color = "#EF4444" if result.get('severity') == "High" else "#F59E0B" if result.get('severity') == "Medium" else "#10B981"
                                
                                st.markdown(f"""
                                    <div class="glass-card" style="border-left: 5px solid {severity_color};">
                                        <h4 style="color: {severity_color}; margin: 0 0 10px 0;">
                                            🦠 {result.get('disease', 'Unknown')}
                                        </h4>
                                        <p style="margin: 5px 0; font-size: 14px;"><strong>Symptoms:</strong> {result.get('symptoms', 'N/A')}</p>
                                        <p style="margin: 5px 0; font-size: 14px;"><strong>Severity:</strong> 
                                            <span style="color: {severity_color}; font-weight: 600;">{result.get('severity', 'Unknown')}</span>
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Treatment tabs
                                treat_tab1, treat_tab2, treat_tab3 = st.tabs(["🌿 Organic", "⚗️ Chemical", "🛡️ Prevention"])
                                
                                with treat_tab1:
                                    for i, treatment in enumerate(result.get('organic_treatments', []), 1):
                                        st.markdown(f"""
                                            <div style="padding: 10px; margin: 8px 0; background: rgba(16,185,129,0.1); border-radius: 10px; border-left: 3px solid #10B981;">
                                                <strong>{i}.</strong> {treatment}
                                            </div>
                                        """, unsafe_allow_html=True)
                                
                                with treat_tab2:
                                    for i, treatment in enumerate(result.get('chemical_treatments', []), 1):
                                        st.markdown(f"""
                                            <div style="padding: 10px; margin: 8px 0; background: rgba(239,68,68,0.1); border-radius: 10px; border-left: 3px solid #EF4444;">
                                                <strong>{i}.</strong> {treatment}
                                            </div>
                                        """, unsafe_allow_html=True)
                                
                                with treat_tab3:
                                    for tip in result.get('prevention', []):
                                        st.info(tip)
                            else:
                                st.error("Could not analyze image. Please try with a clearer photo.")
        
        with col2:
            st.markdown("### 📚 Disease Database")
            
            for disease, info in list(DISEASE_DATABASE.items())[:3]:
                with st.expander(f"{disease}"):
                    st.markdown(f"""
                        <p style="font-size: 13px; color: #6B7280;"><strong>Affects:</strong> {', '.join(info['crops'])}</p>
                        <p style="font-size: 13px; color: #6B7280;"><strong>Symptoms:</strong> {info['symptoms']}</p>
                    """, unsafe_allow_html=True)
            
            # Camera input
            st.markdown("#### 📷 Live Camera")
            camera_file = st.camera_input("Take a picture", key="camera")
            if camera_file:
                st.image(camera_file, caption="Captured", use_column_width=True)
                if st.button("Analyze Photo", key="analyze_cam"):
                    st.info("📸 Image captured! Click 'Analyze with AI' after selecting crop type.")
    
    # === TAB 3: ENHANCED ANALYTICS ===
    with tabs[2]:
        st.markdown("### 📊 Smart Farm Analytics")
        
        # Dashboard
        st.plotly_chart(create_agriculture_dashboard(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌾 AI Crop Recommendations")
            
            # Smart filters
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                water_availability = st.select_slider("Water", ["Low", "Medium", "High"], "Medium")
            with col_f2:
                investment = st.select_slider("Investment", ["Low", "Medium", "High"], "Medium")
            
            if st.button("🤖 Get AI Recommendations", use_container_width=True):
                with st.spinner("Analyzing best crops for your conditions..."):
                    suitable = []
                    for crop, info in CROP_DATABASE.items():
                        water_match = (info['water'] == water_availability or 
                                     (water_availability == "Medium" and info['water'] != "High"))
                        
                        profit_req = "High" if investment == "High" else "Medium"
                        profit_match = info['profit'] in [profit_req, "High", "Very High"]
                        
                        if water_match and profit_match:
                            suitable.append(crop)
                    
                    if suitable:
                        st.markdown("""
                            <div class="success-box">
                                <h5 style="color: #059669; margin: 0 0 10px 0;">🌱 Top Recommendations</h5>
                        """, unsafe_allow_html=True)
                        
                        for crop in suitable[:4]:
                            info = CROP_DATABASE[crop]
                            st.markdown(f"""
                                <div style="display: flex; align-items: center; gap: 10px; padding: 10px; margin: 5px 0; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="font-size: 24px;">{info['image']}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: #1f2937;">{crop}</div>
                                        <div style="font-size: 12px; color: #6B7280;">{info['season']} • {info['duration']}</div>
                                    </div>
                                    <div style="background: {'#10B981' if info['profit'] == 'High' else '#F59E0B'}20; color: {'#059669' if info['profit'] == 'High' else '#D97706'}; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">
                                        {info['profit']} Profit
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Show radar chart
                        fig = create_crop_comparison_chart(suitable[:3])
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 💰 Profit Calculator Pro")
            
            calc_crop = st.selectbox("Select Crop", list(CROP_DATABASE.keys()), key="calc_crop")
            calc_area = st.number_input("Area (Acres)", 0.1, 1000.0, st.session_state.farm_data['size'])
            
            # Smart yield estimation based on crop
            default_yield = {"Rice": 25, "Wheat": 30, "Sugarcane": 400, "Cotton": 15, "Vegetables": 150}.get(calc_crop, 25)
            calc_yield = st.number_input("Expected Yield (Qtl/Acre)", 1.0, 500.0, float(default_yield))
            calc_price = st.number_input("Market Price (₹/Qtl)", 100, 50000, 2000)
            
            if st.button("📊 Calculate Profit", use_container_width=True):
                total_yield = calc_area * calc_yield
                revenue = total_yield * calc_price
                
                # Cost estimation based on crop type
                cost_factors = {
                    "Rice": 0.35, "Wheat": 0.30, "Sugarcane": 0.40,
                    "Cotton": 0.45, "Vegetables": 0.25
                }
                cost_ratio = cost_factors.get(calc_crop, 0.35)
                cost = revenue * cost_ratio
                profit = revenue - cost
                margin = (profit / revenue) * 100 if revenue > 0 else 0
                
                st.markdown(f"""
                    <div class="glass-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(59,130,246,0.1));">
                        <h5 style="color: #1f2937; margin: 0 0 15px 0;">📈 Profit Analysis: {calc_crop}</h5>
                        
                        <div style="display: grid; gap: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #6B7280;">Total Yield:</span>
                                <span style="font-weight: 600; color: #1f2937;">{total_yield:,.1f} Quintals</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #6B7280;">Revenue:</span>
                                <span style="font-weight: 600; color: #3B82F6;">₹{revenue:,.0f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #6B7280;">Est. Cost:</span>
                                <span style="font-weight: 600; color: #F59E0B;">₹{cost:,.0f}</span>
                            </div>
                            <div style="height: 2px; background: linear-gradient(90deg, #10B981, #3B82F6); margin: 8px 0; border-radius: 2px;"></div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #059669; font-weight: 600;">Net Profit:</span>
                                <span style="font-size: 24px; font-weight: 700; color: #059669;">₹{profit:,.0f}</span>
                            </div>
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6B7280; margin-bottom: 5px;">
                                <span>Profit Margin</span>
                                <span>{margin:.1f}%</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {min(margin, 100)}%;"></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 4: GOVERNMENT SCHEMES ENHANCED ===
    with tabs[3]:
        st.markdown("### 🏛️ Government Schemes & Subsidies Hub")
        
        # Search and filter
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            scheme_search = st.text_input("🔍 Search schemes...", placeholder="Type scheme name, benefit, or crop")
        with col_filter:
            category_filter = st.selectbox("Category", ["All", "Income Support", "Insurance", "Loans", "Marketing", "Infrastructure"])
        
        # Filter schemes
        filtered = PERMANENT_SCHEMES
        if scheme_search:
            filtered = [s for s in PERMANENT_SCHEMES if scheme_search.lower() in s['name'].lower() or scheme_search.lower() in s['desc'].lower()]
        if category_filter != "All":
            filtered = [s for s in filtered if s['category'] == category_filter]
        
        # Display in grid
        cols = st.columns(3)
        for i, scheme in enumerate(filtered):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="scheme-card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                            <div style="font-size: 40px; background: linear-gradient(135deg, #10B981, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{scheme['icon']}</div>
                            <div style="background: rgba(16,185,129,0.1); color: #059669; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;">
                                {scheme['category']}
                            </div>
                        </div>
                        <h4 style="color: #1f2937; margin: 0 0 8px 0; font-size: 16px;">{scheme['name']}</h4>
                        <p style="font-size: 13px; color: #6B7280; margin: 0 0 12px 0; line-height: 1.5;">{scheme['desc']}</p>
                        <div style="background: #F3F4F6; padding: 10px; border-radius: 10px; margin-bottom: 12px;">
                            <div style="font-size: 11px; color: #9CA3AF; margin-bottom: 4px;">Eligibility</div>
                            <div style="font-size: 12px; color: #4B5563; font-weight: 500;">{scheme['eligibility']}</div>
                        </div>
                        <a href="{scheme['link']}" target="_blank" style="text-decoration: none;">
                            <div style="background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 10px; border-radius: 12px; text-align: center; font-weight: 600; font-size: 13px; transition: all 0.3s; cursor: pointer; box-shadow: 0 4px 15px rgba(16,185,129,0.3);">
                                Apply Now →
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
        
        # Eligibility checker
        st.markdown("---")
        st.markdown("#### 📋 Smart Eligibility Checker")
        
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            land_own = st.selectbox("Land Type", ["Own Land", "Leased", "Tenant", "Landless"])
        with col_e2:
            income = st.selectbox("Annual Income", ["< ₹1 Lakh", "₹1-2 Lakh", "₹2-5 Lakh", "> ₹5 Lakh"])
        with col_e3:
            farmer_type = st.selectbox("Type", ["Small Farmer", "Marginal", "Large Farmer", "FPO"])
        
        if st.button("🎯 Check My Eligibility", use_container_width=True):
            eligible = []
            if land_own in ["Own Land", "Leased"]:
                eligible.extend(["PM-KISAN", "PMFBY", "Soil Health Card", "e-NAM"])
            if income == "< ₹1 Lakh":
                eligible.extend(["Kisan Credit Card", "PM-KUSUM"])
            
            match_pct = (len(eligible) / len(PERMANENT_SCHEMES)) * 100
            
            st.markdown(f"""
                <div class="success-box">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="color: #059669; margin: 0;">🎉 Good News!</h4>
                            <p style="margin: 5px 0 0 0; font-size: 14px;">You are eligible for <strong>{len(eligible)} schemes</strong></p>
                        </div>
                        <div style="font-size: 32px; font-weight: 700; color: #10B981;">{match_pct:.0f}%</div>
                    </div>
                    <div style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px;">
                        {''.join([f'<span style="background: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; color: #059669; border: 1px solid #10B981;">{s}</span>' for s in eligible[:5]])}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # === TAB 5: VOICE ASSISTANT ENHANCED ===
    with tabs[4]:
        st.markdown("""
            <div class="voice-assistant">
                <div style="position: relative; z-index: 1;">
                    <div style="text-align: center;">
                        <div style="font-size: 60px; margin-bottom: 15px; animation: float 3s ease-in-out infinite;">🎙️</div>
                        <h2 style="color: white; margin: 0; font-family: Space Grotesk;">Voice Assistant</h2>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0;">
                            Speak naturally in your preferred language
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_v1, col_v2 = st.columns([2, 1])
        
        with col_v1:
            st.markdown("### 🎤 Voice Commands")
            
            # Voice language mapping
            voice_langs = {
                "English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta",
                "Telugu": "te", "Kannada": "kn", "Gujarati": "gu", "Bengali": "bn"
            }
            selected_lang_code = voice_langs.get(st.session_state.selected_language, "en")
            
            # Simulated voice input (since streamlit-mic-recorder might not be installed)
            voice_text = st.text_input("📝 Type your voice command:", placeholder="e.g., 'What should I plant this season?'")
            
            if voice_text:
                with st.spinner("🎙️ Processing voice command..."):
                    time.sleep(1)
                    response = get_ai_response(voice_text, f"Voice query from {st.session_state.farmer_name}")
                    
                    st.markdown(f"""
                        <div class="chat-bubble-assistant" style="max-width: 100%;">
                            <strong>🌾 GreenMitra Voice:</strong><br>{response}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Auto play response
                    audio_bytes = text_to_speech_gtts(response, selected_lang_code)
                    if audio_bytes:
                        play_audio(audio_bytes)
            
            # Sample commands
            st.markdown("#### 🎯 Try Saying:")
            samples = [
                "Weather forecast for tomorrow",
                "Best fertilizer for wheat",
                "How to control aphids organically",
                "Current market price for cotton"
            ]
            
            for sample in samples:
                if st.button(f"🎤 {sample}", key=f"voice_{sample}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": f"🎤 {sample}"})
                    response = get_ai_response(sample)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.success("Command processed!")
        
        with col_v2:
            st.markdown("#### ⚙️ Voice Settings")
            
            voice_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1)
            voice_pitch = st.slider("Pitch", 0.5, 2.0, 1.0, 0.1)
            
            st.markdown("#### 📊 Voice History")
            if st.session_state.messages:
                for msg in st.session_state.messages[-3:]:
                    if "🎤" in msg.get("content", ""):
                        st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.5); padding: 8px 12px; border-radius: 10px; margin: 5px 0; font-size: 12px; color: #6B7280;">
                                {msg['content'][:40]}...
                            </div>
                        """, unsafe_allow_html=True)
    
    # === TAB 6: MARKET INSIGHTS ENHANCED ===
    with tabs[5]:
        st.markdown("### 📈 Live Mandi Market Prices")
        
        # Enhanced market data
        market_df = pd.DataFrame({
            'Crop': ['Wheat', 'Rice', 'Cotton', 'Soybean', 'Maize', 'Sugarcane', 'Onion', 'Potato'],
            'Price (₹/Qtl)': [2100, 1850, 6200, 4500, 1950, 350, 2200, 1800],
            'Change (%)': [2.5, -1.2, 3.8, 0.5, -2.1, 1.5, -5.2, 3.2],
            'Demand': ['High', 'High', 'Very High', 'Medium', 'Medium', 'High', 'High', 'Medium'],
            'Arrival (Qtl)': [50000, 75000, 25000, 40000, 60000, 200000, 45000, 80000]
        })
        
        # Color code changes
        market_df['Color'] = market_df['Change (%)'].apply(lambda x: '#10B981' if x > 0 else '#EF4444')
        
        col_m1, col_m2 = st.columns([2, 1])
        
        with col_m1:
            # Interactive chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=market_df['Crop'],
                y=market_df['Price (₹/Qtl)'],
                marker_color=market_df['Color'],
                text=market_df['Change (%)'].apply(lambda x: f"{x:+.1f}%"),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Price: ₹%{y}<br>Change: %{text}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Current Market Prices with Daily Change",
                xaxis_title="",
                yaxis_title="Price (₹/Quintal)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Market table
            st.dataframe(
                market_df[['Crop', 'Price (₹/Qtl)', 'Change (%)', 'Demand']].style.apply(
                    lambda x: ['background: rgba(16,185,129,0.1)' if v > 0 else 'background: rgba(239,68,68,0.1)' 
                              for v in market_df['Change (%)']], subset=['Change (%)']axis=0
                ),
                use_container_width=True,
                hide_index=True
            )
        
        with col_m2:
            st.markdown("#### 🔔 Price Alerts")
            
            alert_crop = st.selectbox("Select Crop", market_df['Crop'].tolist())
            current_p = market_df[market_df['Crop']==alert_crop]['Price (₹/Qtl)'].values[0]
            target_p = st.number_input("Target Price (₹)", 1000, 20000, int(current_p * 1.1))
            
            if st.button("🔔 Set Alert", use_container_width=True):
                st.success(f"✅ Alert set! We'll notify when {alert_crop} reaches ₹{target_p}")
                st.balloons()
            
            st.markdown("---")
            
            st.markdown("#### 💡 AI Trading Tips")
            
            tips = [
                ("📊", "Sell wheat in Jan-Feb for best prices", "High confidence"),
                ("🌾", "Rice prices peak during festivals", "Seasonal"),
                ("💧", "Store cotton in moisture-free areas", "Storage tip"),
                ("📱", "Check e-NAM daily for live rates", "Daily habit")
            ]
            
            for emoji, tip, tag in tips:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 12px; margin: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 20px;">{emoji}</div>
                            <div style="flex: 1;">
                                <div style="font-size: 13px; color: #1f2937; font-weight: 500;">{tip}</div>
                                <div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">{tag}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 7: MAP (NEW) ===
    with tabs[6]:
        st.markdown("### 🗺️ Farm Location & Nearby Services")
        
        col_map1, col_map2 = st.columns([3, 1])
        
        with col_map1:
            # Simple map visualization
            try:
                geolocator = Nominatim(user_agent="greenmitra")
                location = geolocator.geocode(st.session_state.user_location + ", India")
                
                if location:
                    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=12)
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"Your Farm: {st.session_state.user_location}",
                        icon=folium.Icon(color='green', icon='leaf', prefix='fa')
                    ).add_to(m)
                    
                    # Add nearby mandis (mock locations)
                    folium.Marker(
                        [location.latitude + 0.02, location.longitude + 0.02],
                        popup="Nearest APMC Mandi",
                        icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')
                    ).add_to(m)
                    
                    folium.Marker(
                        [location.latitude - 0.015, location.longitude - 0.01],
                        popup="KVK Center",
                        icon=folium.Icon(color='red', icon='university', prefix='fa')
                    ).add_to(m)
                    
                    st_folium(m, width=700, height=500)
                else:
                    # Default to India map
                    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
                    st_folium(m, width=700, height=500)
            except:
                st.info("🗺️ Map feature requires internet connection")
        
        with col_map2:
            st.markdown("#### 📍 Nearby Services")
            
            services = [
                ("🏛️", "APMC Mandi", "12 km"),
                ("🎓", "KVK Center", "8 km"),
                ("🏥", "Veterinary Hospital", "15 km"),
                ("🌾", "Seed Store", "5 km"),
                ("⚙️", "Equipment Rental", "10 km")
            ]
            
            for icon, name, dist in services:
                st.markdown(f"""
                    <div class="glass-card" style="padding: 12px; margin: 8px 0;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 20px;">{icon}</div>
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: #1f2937; font-size: 13px;">{name}</div>
                                <div style="font-size: 11px; color: #6B7280;">{dist} away</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.button("📍 Get Directions", use_container_width=True)
    
    # --- FOOTER ---
    st.markdown("---")
    
    footer_cols = st.columns(4)
    
    with footer_cols[0]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 16px; font-weight: 700; color: #059669; margin: 0;">🌾 GreenMitra AI</p>
                <p style="font-size: 11px; color: #9CA3AF;">Empowering Farmers</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[1]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4B5563; margin: 0;">📞 1800-123-4567</p>
                <p style="font-size: 11px; color: #9CA3AF;">24/7 Helpline</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[2]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4B5563; margin: 0;">🏛️ Ministry of Agri</p>
                <p style="font-size: 11px; color: #9CA3AF;">Govt. Partner</p>
            </div>
        """, unsafe_allow_html=True)
    
    with footer_cols[3]:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 14px; font-weight: 600; color: #4B5563; margin: 0;">© 2025</p>
                <p style="font-size: 11px; color: #9CA3AF;">Version 3.0 Pro</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
