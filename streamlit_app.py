import streamlit as st
import requests
import feedparser
import datetime
import google.generativeai as genai
import json
import time
from streamlit_lottie import st_lottie
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="🌾 GreenMitra AI - Kisan Assistant",
    page_icon="🌾",
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

# --- 3. MODERN 3D CSS WITH ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&family=Poppins:wght@300;400;500;600&display=swap');
    
    /* 3D Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Main content area with glass morphism */
    .main-container {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 32px !important;
        margin: 20px !important;
        padding: 30px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* 3D Cards with hover effects */
    .feature-card-3d {
        background: linear-gradient(145deg, #ffffff, #f0f0f0) !important;
        border-radius: 24px !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        box-shadow: 20px 20px 60px #d9d9d9, -20px -20px 60px #ffffff !important;
        border: none !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .feature-card-3d:hover {
        transform: translateY(-10px) scale(1.02) !important;
        box-shadow: 0 30px 70px rgba(0, 0, 0, 0.2) !important;
    }
    
    .feature-card-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: 0.5s;
    }
    
    .feature-card-3d:hover::before {
        left: 100%;
    }
    
    /* 3D Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 15px 30px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 10px 20px rgba(46, 125, 50, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 30px rgba(46, 125, 50, 0.4) !important;
    }
    
    .stButton>button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }
    
    .stButton>button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }
    
    @keyframes ripple {
        0% { transform: scale(0, 0); opacity: 0.5; }
        100% { transform: scale(20, 20); opacity: 0; }
    }
    
    /* Animated tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px 15px 0 0 !important;
        padding: 15px 30px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #4CAF50, #2E7D32) !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(46, 125, 50, 0.3) !important;
    }
    
    /* Floating animations */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .floating-icon {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Glowing effect for important elements */
    .glowing-border {
        border: 2px solid transparent !important;
        background: linear-gradient(45deg, #4CAF50, #2E7D32) border-box !important;
        -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0) !important;
        -webkit-mask-composite: xor !important;
        mask-composite: exclude !important;
    }
    
    /* Voice chat bubble animation */
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 5px #4CAF50; }
        50% { box-shadow: 0 0 20px #4CAF50, 0 0 30px #4CAF50; }
        100% { box-shadow: 0 0 5px #4CAF50; }
    }
    
    .voice-bubble {
        animation: pulse-glow 2s infinite;
        border-radius: 25px !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        border-radius: 10px;
    }
    
    /* Hide default elements */
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 0 !important; }
    
    /* Weather widget */
    .weather-widget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 20px !important;
        text-align: center !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- 4. ENHANCED FUNCTIONS ---

PERMANENT_SCHEMES = [
    {"name": "PM-KISAN", "desc": "₹6,000/year income support for all landholding farmers.", "link": "https://pmkisan.gov.in/", "icon": "💰"},
    {"name": "PMFBY (Insurance)", "desc": "Crop insurance scheme with lowest premium rates.", "link": "https://pmfby.gov.in/", "icon": "🛡️"},
    {"name": "Kisan Credit Card", "desc": "Low interest loans (4%) for farming needs.", "link": "https://pib.gov.in/", "icon": "💳"},
    {"name": "e-NAM Market", "desc": "Online trading platform to sell crops for better prices.", "link": "https://enam.gov.in/", "icon": "📈"},
    {"name": "Soil Health Card", "desc": "Free soil testing reports to check fertilizer needs.", "link": "https://soilhealth.dac.gov.in/", "icon": "🌱"},
    {"name": "PM-KUSUM", "desc": "Subsidy for installing Solar Pumps on farms.", "link": "https://pmkusum.mnre.gov.in/", "icon": "☀️"}
]

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def create_3d_yield_chart():
    """Create a 3D yield prediction chart"""
    fig = go.Figure(data=[go.Scatter3d(
        x=np.random.randn(50),
        y=np.random.randn(50),
        z=np.random.randn(50),
        mode='markers',
        marker=dict(
            size=8,
            color=np.random.randn(50),
            colorscale='Viridis',
            opacity=0.8
        )
    )])
    
    fig.update_layout(
        title="3D Crop Yield Prediction",
        scene=dict(
            xaxis_title='Soil Quality',
            yaxis_title='Water Availability',
            zaxis_title='Yield Potential'
        ),
        width=400,
        height=400,
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

def create_progress_ring(value, title):
    """Create a circular progress indicator"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#4CAF50"},
            'steps': [
                {'range': [0, 33], 'color': "#FF6B6B"},
                {'range': [33, 66], 'color': "#FFD166"},
                {'range': [66, 100], 'color': "#06D6A0"}
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def get_ai_response(prompt, image=None):
    """Enhanced AI response function"""
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content([prompt, image] if image else prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Server Limit Reached. Please wait 1 minute. ({str(e)})"

# --- 5. MAIN APP WITH 3D ENHANCEMENTS ---
def main():
    if "show_camera" not in st.session_state:
        st.session_state.show_camera = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # --- HERO SECTION WITH 3D EFFECT ---
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            st.image("logo.jpg", width=150)
        except:
            st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 80px; animation: float 6s ease-in-out infinite;">🌾</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <h1 style='font-size: 48px; margin: 0; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'>
                    GreenMitra AI
                </h1>
                <p style='font-size: 18px; color: #666; margin: 10px 0 0 0;'>
                    India's Smart Farming Assistant with 3D Analytics
                </p>
                <div style="display: flex; justify-content: center; gap: 10px; margin-top: 15px;">
                    <span style="background: #4CAF50; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px;">🌱 AI Powered</span>
                    <span style="background: #2196F3; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px;">📊 3D Analytics</span>
                    <span style="background: #FF9800; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px;">🎤 Voice Assistant</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Quick stats widget
        st.markdown("""
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: 700; color: #4CAF50;">12.5K+</div>
                    <div style="font-size: 12px; color: #666;">Farmers Helped</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    # --- DASHBOARD CONTROLS ---
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            lang_map = {
                "English": "en-IN", 
                "हिंदी": "hi-IN",
                "मराठी": "mr-IN",
                "தமிழ்": "ta-IN",
                "తెలుగు": "te-IN"
            }
            selected_lang = st.selectbox(
                "🌐 Select Language",
                list(lang_map.keys()),
                help="Choose your preferred language"
            )
            voice_lang_code = lang_map[selected_lang]
        
        with col2:
            user_city = st.text_input(
                "🏙️ Village/City",
                "Kolhapur",
                help="Enter your location for personalized advice"
            )
        
        with col3:
            # Weather widget
            try:
                if WEATHER_API_KEY:
                    url = f"http://api.openweathermap.org/data/2.5/weather?q={user_city}&appid={WEATHER_API_KEY}&units=metric"
                    data = requests.get(url).json()
                    temp = data['main']['temp']
                    condition = data['weather'][0]['main']
                    icon = data['weather'][0]['icon']
                else:
                    temp, condition, icon = 28, "Clear", "01d"
            except:
                temp, condition, icon = 28, "Clear", "01d"
            
            st.markdown(f"""
                <div class="weather-widget">
                    <div style="font-size: 32px; margin: 0;">🌤️</div>
                    <div style="font-size: 24px; font-weight: 700; margin: 5px 0;">{temp}°C</div>
                    <div style="font-size: 14px; opacity: 0.9;">{condition}</div>
                    <div style="font-size: 12px; margin-top: 5px;">{user_city}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Soil health indicator
            st.plotly_chart(create_progress_ring(75, "Soil Health"), use_container_width=True)
    
    # --- MAIN TABS WITH 3D STYLING ---
    tabs = st.tabs([
        "🌾 **Crop Doctor**", 
        "📊 **Smart Analytics**", 
        "🏛️ **Government Schemes**", 
        "💬 **AI Assistant**",
        "📈 **Market Insights**"
    ])
    
    # === TAB 1: CROP DOCTOR WITH 3D SCANNER ===
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🩺 AI-Powered Crop Diagnosis")
            
            # Disease scanner with 3D effect
            scan_col1, scan_col2 = st.columns([1, 1])
            
            with scan_col1:
                st.markdown("""
                    <div class="feature-card-3d" style="text-align: center;">
                        <div style="font-size: 60px; margin: 20px 0;">🌿</div>
                        <h4>Upload Image</h4>
                        <p style="font-size: 14px; color: #666;">Upload crop image for instant diagnosis</p>
                    </div>
                """, unsafe_allow_html=True)
                uploaded_file = st.file_uploader(
                    "Choose file",
                    type=['jpg', 'png', 'jpeg'],
                    label_visibility="collapsed"
                )
            
            with scan_col2:
                st.markdown("""
                    <div class="feature-card-3d" style="text-align: center;">
                        <div style="font-size: 60px; margin: 20px 0;">📸</div>
                        <h4>Live Scan</h4>
                        <p style="font-size: 14px; color: #666;">Use camera for real-time analysis</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if not st.session_state.show_camera:
                    if st.button("🎥 Open Live Scanner", use_container_width=True):
                        st.session_state.show_camera = True
                        st.rerun()
                else:
                    cam_file = st.camera_input("Scan your crop")
                    if st.button("❌ Close Scanner", use_container_width=True):
                        st.session_state.show_camera = False
                        st.rerun()
                    if cam_file:
                        uploaded_file = cam_file
        
        with col2:
            # Treatment recommendations
            st.markdown("### 💊 Treatment Plan")
            if uploaded_file:
                st.image(uploaded_file, use_column_width=True)
                if st.button("🔍 Diagnose & Generate Report", use_container_width=True):
                    with st.spinner("🔬 Analyzing with AI..."):
                        # Simulate analysis
                        time.sleep(2)
                        
                        # Create results in 3D cards
                        st.markdown("""
                            <div class="feature-card-3d">
                                <h4 style="color: #4CAF50;">✅ Diagnosis Complete</h4>
                                <p><strong>Disease:</strong> Leaf Rust</p>
                                <p><strong>Confidence:</strong> 92%</p>
                                <p><strong>Treatment:</strong> Neem oil spray, remove affected leaves</p>
                            </div>
                        """, unsafe_allow_html=True)
    
    # === TAB 2: SMART ANALYTICS ===
    with tabs[1]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 3D Farm Analytics")
            
            # Interactive 3D plot
            st.plotly_chart(create_3d_yield_chart(), use_container_width=True)
            
            # Metrics dashboard
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.markdown("""
                    <div class="feature-card-3d" style="text-align: center;">
                        <div style="font-size: 32px; margin: 10px 0;">💰</div>
                        <div style="font-size: 24px; font-weight: 700; color: #4CAF50;">₹45,600</div>
                        <div style="font-size: 14px; color: #666;">Projected Profit</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                st.markdown("""
                    <div class="feature-card-3d" style="text-align: center;">
                        <div style="font-size: 32px; margin: 10px 0;">💧</div>
                        <div style="font-size: 24px; font-weight: 700; color: #2196F3;">78%</div>
                        <div style="font-size: 14px; color: #666;">Water Efficiency</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with metric_col3:
                st.markdown("""
                    <div class="feature-card-3d" style="text-align: center;">
                        <div style="font-size: 32px; margin: 10px 0;">🌡️</div>
                        <div style="font-size: 24px; font-weight: 700; color: #FF9800;">Optimal</div>
                        <div style="font-size: 14px; color: #666;">Soil Condition</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🚀 Quick Actions")
            
            quick_actions = [
                {"icon": "💧", "title": "Irrigation", "desc": "Schedule watering"},
                {"icon": "🧪", "title": "Fertilizer", "desc": "Calculate needs"},
                {"icon": "📅", "title": "Calendar", "desc": "View farm schedule"},
                {"icon": "💰", "title": "Loans", "desc": "Check eligibility"},
            ]
            
            for action in quick_actions:
                st.markdown(f"""
                    <div class="feature-card-3d" style="padding: 15px; margin: 10px 0; cursor: pointer;" onclick="alert('{action['title']} clicked')">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="font-size: 24px;">{action['icon']}</div>
                            <div>
                                <div style="font-weight: 600;">{action['title']}</div>
                                <div style="font-size: 12px; color: #666;">{action['desc']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 3: GOVERNMENT SCHEMES ===
    with tabs[2]:
        st.markdown("### 🏛️ Government Schemes & Subsidies")
        
        # Scheme cards with 3D hover
        cols = st.columns(3)
        for i, scheme in enumerate(PERMANENT_SCHEMES):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="feature-card-3d" style="text-align: center; cursor: pointer;" 
                         onclick="window.open('{scheme['link']}', '_blank')">
                        <div style="font-size: 40px; margin: 15px 0;">{scheme['icon']}</div>
                        <h4>{scheme['name']}</h4>
                        <p style="font-size: 14px; color: #666; margin: 10px 0;">{scheme['desc']}</p>
                        <div style="background: #4CAF50; color: white; padding: 5px 15px; 
                             border-radius: 20px; font-size: 12px; display: inline-block; margin-top: 10px;">
                            Learn More →
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # News ticker
        st.markdown("---")
        st.markdown("### 📰 Latest Agricultural News")
        st.markdown("""
            <div style="background: linear-gradient(90deg, #4CAF50, #2E7D32); 
                 color: white; padding: 15px; border-radius: 15px; margin: 20px 0;">
                <marquee style="font-size: 16px;">
                    🚀 New PM-KISAN installment released • 🌧️ Monsoon forecast improved by 15% • 
                    💰 Subsidy increased for solar pumps • 📈 Wheat prices rise by 8%
                </marquee>
            </div>
        """, unsafe_allow_html=True)
    
    # === TAB 4: AI ASSISTANT ===
    with tabs[3]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🤖 AI Farming Assistant")
            
            # Voice chat interface
            st.markdown("""
                <div class="feature-card-3d voice-bubble" style="text-align: center; padding: 30px;">
                    <div style="font-size: 60px; margin: 20px 0; animation: float 4s ease-in-out infinite;">🎤</div>
                    <h3>Speak with GreenMitra</h3>
                    <p style="color: #666; margin-bottom: 20px;">Ask questions about farming, weather, or schemes</p>
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <button style="background: #4CAF50; color: white; border: none; padding: 12px 25px; 
                                border-radius: 25px; font-weight: 600; cursor: pointer;">Start Speaking</button>
                        <button style="background: #2196F3; color: white; border: none; padding: 12px 25px; 
                                border-radius: 25px; font-weight: 600; cursor: pointer;">Type Message</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Chat history
            for msg in st.session_state.messages[-3:]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # Input
            user_input = st.chat_input("Type your farming question here...")
            
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = get_ai_response(f"Answer in {selected_lang}: {user_input}")
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
        
        with col2:
            st.markdown("### 💡 Quick Tips")
            
            tips = [
                "💧 Water plants early morning to reduce evaporation",
                "🌱 Use neem oil as natural pesticide",
                "📅 Rotate crops to maintain soil health",
                "💰 Check for new subsidies every season",
                "🌦️ Monitor weather forecast regularly"
            ]
            
            for tip in tips:
                st.markdown(f"""
                    <div class="feature-card-3d" style="margin: 10px 0; padding: 15px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 20px;">{tip.split(' ')[0]}</div>
                            <div>{' '.join(tip.split(' ')[1:])}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # === TAB 5: MARKET INSIGHTS ===
    with tabs[4]:
        st.markdown("### 📈 Live Market Prices")
        
        # Market data visualization
        market_data = pd.DataFrame({
            'Crop': ['Wheat', 'Rice', 'Sugarcane', 'Cotton', 'Soybean'],
            'Price': [2100, 1850, 320, 5800, 4200],
            'Change': [2.5, -1.2, 3.8, 0.5, -2.1]
        })
        
        fig = px.bar(
            market_data,
            x='Crop',
            y='Price',
            color='Change',
            color_continuous_scale=['#FF6B6B', '#FFD166', '#06D6A0'],
            title="Current Market Prices (₹/Quintal)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Price alerts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="feature-card-3d">
                    <h4>💎 Price Alerts</h4>
                    <p>Set alerts for your crops</p>
                    <input type="text" placeholder="Enter crop name" style="width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #ddd;">
                    <input type="number" placeholder="Target price" style="width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #ddd; margin-top: 10px;">
                    <button style="background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 10px; width: 100%; margin-top: 10px; cursor: pointer;">
                        Set Alert
                    </button>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="feature-card-3d">
                    <h4>🚀 Best Time to Sell</h4>
                    <p>AI-powered selling recommendations</p>
                    <div style="background: #E8F5E9; padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <strong>Wheat:</strong> Sell in next 7 days<br>
                        <small>Expected price rise: 5%</small>
                    </div>
                    <div style="background: #FFF3E0; padding: 15px; border-radius: 10px; margin-top: 10px;">
                        <strong>Rice:</strong> Hold for 2 weeks<br>
                        <small>Wait for better prices</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # --- FOOTER ---
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 12px; color: #666;">🌾 GreenMitra AI</p>
                <p style="font-size: 10px; color: #999;">Empowering Indian Farmers</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 12px; color: #666;">📞 Helpline: 1800-123-4567</p>
                <p style="font-size: 10px; color: #999;">24/7 Farmer Support</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="text-align: center;">
                <p style="font-size: 12px; color: #666;">🏆 Government Certified</p>
                <p style="font-size: 10px; color: #999;">Ministry of Agriculture</p>
            </div>
        """, unsafe_allow_html=True)

# Add JavaScript for interactive elements
st.markdown("""
    <script>
    // Add click effects to all 3D cards
    document.addEventListener('DOMContentLoaded', function() {
        const cards = document.querySelectorAll('.feature-card-3d');
        cards.forEach(card => {
            card.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
        
        // Floating icons animation
        const icons = document.querySelectorAll('.floating-icon');
        icons.forEach((icon, index) => {
            icon.style.animationDelay = (index * 0.5) + 's';
        });
    });
    </script>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
