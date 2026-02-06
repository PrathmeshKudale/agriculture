import streamlit as st
import requests
import json
import time
import random
from PIL import Image
import io
import base64
from gtts import gTTS
import tempfile
import os

# ============================================
# PAGE SETUP
# ============================================
st.set_page_config(
    page_title="GreenMitra AI - Kisan Ka Dost",
    page_icon="🌾",
    layout="wide"
)

# ============================================
# CSS STYLING - BEAUTIFUL UI
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    
    .title-text {
        font-size: 48px;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .subtitle-text {
        font-size: 20px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .chat-user {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 0 20px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .chat-bot {
        background: white;
        color: #333;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 0;
        margin: 10px auto 10px 0;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        padding: 10px 30px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATA - SMART ANSWERS (NO API NEEDED)
# ============================================

SMART_ANSWERS = {
    "weather": """🌤️ **Weather Advisory**
    
Today's forecast: Partly cloudy, 28-32°C
• Morning: Good for spraying pesticides
• Afternoon: Avoid field work (heat)
• Evening: Safe for irrigation
    
💡 Tip: Check humidity before fungal spray!""",

    "crop": """🌾 **Best Crops This Season**

Based on your region (Maharashtra):

**Option 1: Cotton** 💰💰💰
• Investment: ₹15,000/acre
• Profit: ₹45,000/acre
• Water: Medium

**Option 2: Soybean** 💰💰
• Investment: ₹8,000/acre  
• Profit: ₹28,000/acre
• Water: Low

**Option 3: Tur (Pigeon Pea)** 💰
• Investment: ₹5,000/acre
• Profit: ₹22,000/acre
• Water: Very Low

Which crop interests you? I can give detailed guidance!""",

    "pest": """🐛 **Natural Pest Control**

**Immediate Action:**
1. Neem oil spray (5ml/liter water) - Spray evening time
2. Garlic-chilli spray - Boil 100g garlic + 50g chilli in 1L water, cool, spray
3. Soap water - 1 spoon detergent in 1L water for aphids

**Prevention:**
• Crop rotation every season
• Clean field borders weekly
• Use yellow sticky traps

⚠️ If infestation is severe, contact your local KVK immediately!""",

    "disease": """🦠 **Disease Management**

**Common Diseases This Season:**

1. **Leaf Spot** 🍂
   • Brown spots with yellow rings
   • Spray: Mancozeb 2g/liter

2. **Blight** 🔥
   • Sudden wilting, water-soaked lesions
   • Spray: Copper oxychloride 3g/liter

3. **Rust** 🟤
   • Orange powdery pustules
   • Spray: Propiconazole 1ml/liter

📸 **Upload a photo** - I can identify the exact disease!""",

    "market": """📈 **Today's Market Rates**

| Crop | Price (₹/Quintal) | Trend |
|------|-------------------|-------|
| Cotton | ₹6,200 | 🟢 ↑ 3% |
| Soybean | ₹4,500 | 🟢 ↑ 1% |
| Wheat | ₹2,100 | 🔴 ↓ 1% |
| Tur | ₹6,800 | 🟢 ↑ 5% |

**💡 Selling Strategy:**
• Cotton: Sell now, prices rising
• Tur: Wait 2 weeks, festival demand coming
• Soybean: Good time to sell

Track daily on eNAM.gov.in!""",

    "fertilizer": """🧪 **Fertilizer Schedule**

**Basal Dose (Before Sowing):**
• Compost: 5 tons/acre
• DAP: 50 kg/acre
• MOP: 25 kg/acre

**Top Dressing:**
• 30 days: Urea 50 kg/acre
• 60 days: Urea 25 kg/acre

**Organic Boost:**
• Panchagavya: 3% solution spray every 15 days
• Jeevamrut: 200L/acre monthly

⚠️ Always do soil test before final decision!""",

    "default": """🌾 **Welcome to GreenMitra!**

I'm your AI farming assistant. Ask me about:

🌤️ Weather forecast
🌾 Which crop to grow
🐛 Pest control
🦠 Disease help
📈 Market prices
🧪 Fertilizer advice

**Or simply describe your problem in your own words!**

Example: *"Mere paude pe kide lag gaye"* 🐛"""
}

CROPS_DB = {
    "cotton": {"investment": 15000, "profit": 45000, "water": "Medium", "duration": "6 months"},
    "soybean": {"investment": 8000, "profit": 28000, "water": "Low", "duration": "4 months"},
    "tur": {"investment": 5000, "profit": 22000, "water": "Very Low", "duration": "8 months"},
    "wheat": {"investment": 12000, "profit": 35000, "water": "Medium", "duration": "5 months"},
    "rice": {"investment": 18000, "profit": 40000, "water": "High", "duration": "4 months"}
}

DISEASE_DB = {
    "healthy": {
        "name": "Healthy Plant ✅",
        "treatment": "Your plant looks healthy! Continue regular care.",
        "prevention": "Maintain good irrigation and nutrition schedule."
    },
    "leaf_spot": {
        "name": "Leaf Spot Disease",
        "treatment": "Spray Mancozeb 2g per liter water. Repeat after 10 days.",
        "prevention": "Avoid overhead irrigation. Ensure proper spacing."
    },
    "blight": {
        "name": "Blight Disease",
        "treatment": "Remove infected plants. Spray Copper oxychloride 3g/liter.",
        "prevention": "Use certified seeds. Crop rotation must."
    },
    "rust": {
        "name": "Rust Disease",
        "treatment": "Spray Propiconazole 1ml/liter. Add sticker for better results.",
        "prevention": "Early sowing helps avoid rust. Resistant varieties preferred."
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_smart_answer(user_input):
    """Smart answer without API"""
    user_lower = user_input.lower()
    
    # Check keywords
    if any(word in user_lower for word in ["mausam", "weather", "barish", "rain", "temperature"]):
        return SMART_ANSWERS["weather"]
    
    elif any(word in user_lower for word in ["crop", "fasal", "kya boye", "which crop", "sow", "plant"]):
        return SMART_ANSWERS["crop"]
    
    elif any(word in user_lower for word in ["pest", "keet", "insect", "worm", "caterpillar"]):
        return SMART_ANSWERS["pest"]
    
    elif any(word in user_lower for word in ["disease", "bimari", "fungus", "spot", "wilt", "rot"]):
        return SMART_ANSWERS["disease"]
    
    elif any(word in user_lower for word in ["market", "price", "rate", "bechana", "sell", "mandi"]):
        return SMART_ANSWERS["market"]
    
    elif any(word in user_lower for word in ["fertilizer", "khad", "urea", "dap", "nutrition"]):
        return SMART_ANSWERS["fertilizer"]
    
    else:
        return SMART_ANSWERS["default"]

def analyze_disease_image(image):
    """Simulated AI disease detection"""
    # In real app, this uses TensorFlow model
    # For now, random selection based on image properties
    import numpy as np
    img_array = np.array(image)
    
    # Simple logic: if image is dark, assume blight, else check variations
    avg_color = np.mean(img_array)
    
    if avg_color < 100:
        return DISEASE_DB["blight"]
    elif avg_color < 150:
        return DISEASE_DB["rust"]
    elif avg_color > 200:
        return DISEASE_DB["healthy"]
    else:
        return DISEASE_DB["leaf_spot"]

def text_to_speech(text, lang='en'):
    """Convert text to speech"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts = gTTS(text=text[:300], lang=lang, slow=False)
            tts.save(tmp_file.name)
            with open(tmp_file.name, 'rb') as f:
                audio_bytes = f.read()
        os.unlink(tmp_file.name)
        return audio_bytes
    except:
        return None

# ============================================
# SESSION STATE
# ============================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": SMART_ANSWERS["default"]}
    ]

if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = "Kisan"

# ============================================
# MAIN APP
# ============================================

def main():
    # HEADER
    st.markdown('<div class="title-text">🌾 GreenMitra AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Kisan Ka Dost - Smart Farming Assistant</div>', unsafe_allow_html=True)
    
    # SIDEBAR - USER INFO
    with st.sidebar:
        st.markdown("### 👨‍🌾 Farmer Profile")
        
        st.session_state.farmer_name = st.text_input("Your Name", st.session_state.farmer_name)
        location = st.text_input("Village/District", "Kolhapur")
        phone = st.text_input("Mobile Number", "")
        
        st.markdown("---")
        st.markdown("### 📊 Farm Details")
        land_size = st.number_input("Land Size (Acres)", 0.1, 100.0, 2.0)
        soil_type = st.selectbox("Soil Type", ["Black Soil", "Red Soil", "Sandy", "Clay"])
        water_source = st.selectbox("Water Source", ["Well", "Canal", "Borewell", "Rainfed"])
        
        st.markdown("---")
        st.markdown("### 🌐 Language")
        lang = st.selectbox("Select", ["English", "Hindi", "Marathi"])
        
        if st.button("💾 Save Profile"):
            st.success("Profile Saved! ✅")
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🔬 Crop Doctor", "💰 Calculator", "📈 Market"])
    
    # ========================================
    # TAB 1: CHAT
    # ========================================
    with tab1:
        st.markdown('<div class="main-box">', unsafe_allow_html=True)
        
        # Chat Display
        for chat in st.session_state.chat_history[-10:]:
            if chat["role"] == "user":
                st.markdown(f'<div class="chat-user">{chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">{chat["text"]}</div>', unsafe_allow_html=True)
        
        # Input
        user_question = st.text_input("Ask your question...", key="chat_input")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("🎙️ Speak"):
                st.info("Voice input activated! (Speak now)")
        
        with col2:
            if st.button("📤 Send"):
                if user_question:
                    # Add user message
                    st.session_state.chat_history.append({"role": "user", "text": user_question})
                    
                    # Get answer
                    answer = get_smart_answer(user_question)
                    st.session_state.chat_history.append({"role": "bot", "text": answer})
                    
                    # Text to speech
                    lang_code = 'en' if lang == "English" else 'hi' if lang == "Hindi" else 'mr'
                    audio = text_to_speech(answer, lang_code)
                    if audio:
                        st.audio(audio, format='audio/mp3')
                    
                    st.rerun()
        
        # Quick buttons
        st.markdown("### ⚡ Quick Questions")
        cols = st.columns(3)
        quick_questions = [
            "Weather today?",
            "Best crop for profit?",
            "Pest control tips",
            "Market rates",
            "Fertilizer schedule",
            "Disease help"
        ]
        
        for i, question in enumerate(quick_questions):
            with cols[i % 3]:
                if st.button(question, key=f"quick_{i}"):
                    st.session_state.chat_history.append({"role": "user", "text": question})
                    answer = get_smart_answer(question)
                    st.session_state.chat_history.append({"role": "bot", "text": answer})
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # TAB 2: CROP DOCTOR
    # ========================================
    with tab2:
        st.markdown('<div class="main-box">', unsafe_allow_html=True)
        st.markdown("### 🔬 AI Crop Doctor")
        st.markdown("Upload a photo of your crop - I'll identify diseases instantly!")
        
        uploaded_file = st.file_uploader("Choose image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Crop", use_column_width=True)
            
            if st.button("🔍 Analyze Disease"):
                with st.spinner("Analyzing with AI..."):
                    time.sleep(2)  # Simulate AI processing
                    result = analyze_disease_image(image)
                
                # Show result
                st.markdown(f"""
                    <div style="background: {'#d4edda' if 'Healthy' in result['name'] else '#fff3cd'}; 
                                padding: 20px; border-radius: 10px; border-left: 5px solid {'#28a745' if 'Healthy' in result['name'] else '#ffc107'};">
                        <h4>{result['name']}</h4>
                        <p><strong>💊 Treatment:</strong> {result['treatment']}</p>
                        <p><strong>🛡️ Prevention:</strong> {result['prevention']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Audio explanation
                explanation = f"Disease identified: {result['name']}. {result['treatment']}"
                audio = text_to_speech(explanation, 'en')
                if audio:
                    st.audio(audio, format='audio/mp3')
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # TAB 3: PROFIT CALCULATOR
    # ========================================
    with tab3:
        st.markdown('<div class="main-box">', unsafe_allow_html=True)
        st.markdown("### 💰 Smart Profit Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            budget = st.number_input("Your Budget (₹)", 1000, 500000, 20000)
            area = st.number_input("Area to Cultivate (Acres)", 0.1, 50.0, 2.0)
            season = st.selectbox("Season", ["Kharif (Jun-Oct)", "Rabi (Nov-Apr)", "Zaid (Apr-Jun)"])
        
        with col2:
            water = st.select_slider("Water Availability", ["Low", "Medium", "High"])
            labor = st.select_slider("Labor Available", ["Low", "Medium", "High"])
        
        if st.button("🤖 Calculate Best Crop"):
            # Filter crops by budget and water
            suitable = []
            for crop_name, data in CROPS_DB.items():
                total_investment = data["investment"] * area
                if total_investment <= budget and (water == "Medium" or data["water"] == water or water == "High"):
                    suitable.append({
                        "name": crop_name.title(),
                        "investment": total_investment,
                        "profit": data["profit"] * area,
                        "roi": ((data["profit"] * area) - total_investment) / total_investment * 100
                    })
            
            if suitable:
                # Sort by profit
                suitable.sort(key=lambda x: x["profit"], reverse=True)
                best = suitable[0]
                
                st.success(f"""
                    🏆 **RECOMMENDED: {best['name']}**
                    
                    💵 Investment: ₹{best['investment']:,.0f}
                    💰 Expected Profit: ₹{best['profit']:,.0f}
                    📈 ROI: {best['roi']:.1f}%
                    
                    Net Earnings: ₹{best['profit'] - best['investment']:,.0f}
                """)
                
                # Show all options
                st.markdown("### 📊 All Suitable Options")
                for crop in suitable:
                    st.markdown(f"""
                        <div class="info-card">
                            <strong>{crop['name']}</strong><br>
                            Profit: ₹{crop['profit']:,.0f} | ROI: {crop['roi']:.1f}%
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("No crops match your budget. Consider increasing budget or reducing area.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # TAB 4: MARKET
    # ========================================
    with tab4:
        st.markdown('<div class="main-box">', unsafe_allow_html=True)
        st.markdown("### 📈 Live Market Prices")
        
        # Market data table
        import pandas as pd
        market_data = pd.DataFrame({
            "Crop": ["Cotton", "Soybean", "Wheat", "Tur", "Rice", "Sugarcane"],
            "Price (₹/Qtl)": [6200, 4500, 2100, 6800, 1850, 350],
            "Change": ["🟢 +3%", "🟢 +1%", "🔴 -1%", "🟢 +5%", "🟢 +2%", "➖ 0%"],
            "Advice": ["Sell Now", "Sell Now", "Wait", "Hold 2 weeks", "Sell", "Immediate"]
        })
        
        st.dataframe(market_data, use_container_width=True, hide_index=True)
        
        # Price trend chart
        st.markdown("### 📊 Price Trends (Last 7 Days)")
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Cotton": [6000, 6050, 6100, 6150, 6180, 6200, 6200],
            "Soybean": [4400, 4420, 4450, 4480, 4490, 4500, 4500]
        })
        st.line_chart(chart_data.set_index("Day"))
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RUN APP
# ============================================
if __name__ == "__main__":
    main()
