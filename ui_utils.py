import streamlit as st
from contextlib import contextmanager

def apply_legendary_styles():
    """Injects advanced CSS for a legendary UI experience."""
    
    # Determine theme from session state (default to Dark if not set, or handle both)
    # Note: main.py sets st.session_state.theme.
    theme = st.session_state.get("theme", "Dark")
    is_dark = theme == "Dark"
    
    if is_dark:
        bg_gradient = "radial-gradient(circle at 50% 50%, #1a1a2e 0%, #16213e 50%, #0f3460 100%)"
        text_color = "#ffffff"
        card_bg = "rgba(255, 255, 255, 0.05)"
        card_border = "rgba(255, 255, 255, 0.1)"
        input_bg = "rgba(0, 0, 0, 0.3)"
        input_text = "white"
        metric_bg = "rgba(255, 255, 255, 0.03)"
        sidebar_bg = "#0a0a0a"
    else:
        # Light mode legendary styles
        bg_gradient = "radial-gradient(circle at 50% 50%, #ffffff 0%, #f0f2f6 50%, #e0e7ff 100%)"
        text_color = "#000000"
        card_bg = "rgba(255, 255, 255, 0.6)"
        card_border = "rgba(0, 0, 0, 0.1)"
        input_bg = "rgba(255, 255, 255, 0.8)"
        input_text = "black"
        metric_bg = "rgba(255, 255, 255, 0.5)"
        sidebar_bg = "#f8f9fa"

    st.markdown(f"""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;500;700&family=Inter:wght@300;400;600&display=swap');

        :root {{
            --primary-gradient: linear-gradient(135deg, #00f260 0%, #0575e6 100%);
            --secondary-gradient: linear-gradient(135deg, #FF0099 0%, #493240 100%);
            --glass-bg: {card_bg};
            --glass-border: {card_border};
            --neon-blue: #00f3ff;
            --neon-purple: #bc13fe;
            --neon-green: #0aff00;
            --text-color: {text_color};
            --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        }}

        /* Global Resets & Typography */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text-color) !important;
        }}
        
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: var(--text-color);
        }}
        
        h1, h2, h3 {{
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        /* Animated Background Gradient */
        .stApp {{
            background: {bg_gradient};
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }}

        @keyframes gradientBG {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        /* Legendary Header */
        .main-header {{
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 4rem !important;
            font-weight: 900 !important;
            text-align: center;
            text-shadow: 0 0 20px rgba(0, 242, 96, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
            margin-bottom: 0 !important;
        }}

        @keyframes glow {{
            from {{ text-shadow: 0 0 10px rgba(0, 242, 96, 0.5); }}
            to {{ text-shadow: 0 0 30px rgba(5, 117, 230, 0.8), 0 0 10px rgba(0, 242, 96, 0.5); }}
        }}

        .sub-header {{
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.5rem !important;
            color: var(--text-color) !important;
            text-align: center;
            margin-bottom: 3rem !important;
            letter-spacing: 4px;
            opacity: 0.8;
        }}

        /* Glassmorphism Cards */
        .legendary-card {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: var(--card-shadow);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }}

        .legendary-card:hover {{
            transform: translateY(-5px) scale(1.01);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
            border-color: var(--neon-blue);
        }}

        /* Metric Styling */
        div[data-testid="stMetric"] {{
            background: {metric_bg};
            border-radius: 15px;
            padding: 15px;
            border: 1px solid var(--glass-border);
            transition: all 0.3s ease;
        }}

        div[data-testid="stMetric"]:hover {{
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            border-color: var(--neon-blue);
        }}

        div[data-testid="stMetricLabel"] {{
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            color: var(--text-color);
            opacity: 0.7;
        }}

        div[data-testid="stMetricValue"] {{
            font-family: 'Orbitron', sans-serif;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(90deg, #00f260, #0575e6);
            color: white !important;
            border: none;
            border-radius: 50px;
            padding: 0.6rem 2rem;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 242, 96, 0.4);
        }}

        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(5, 117, 230, 0.6);
            background: linear-gradient(90deg, #0575e6, #00f260);
            color: white !important;
        }}

        /* Inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select {{
            background: {input_bg} !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 10px !important;
            color: {input_text} !important;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }}

        .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {{
            border-color: var(--neon-blue) !important;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
        }}
        
        /* Input Labels */
        .stTextInput label, .stNumberInput label, .stSelectbox label {{
            color: var(--text-color) !important;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: {sidebar_bg};
            border-right: 1px solid var(--glass-border);
        }}
        
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] span {{
            color: var(--text-color) !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent;
            border-bottom: 1px solid var(--glass-border);
        }}

        .stTabs [data-baseweb="tab"] {{
            color: var(--text-color);
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            opacity: 0.7;
        }}

        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: var(--neon-blue);
            border-bottom-color: var(--neon-blue);
            opacity: 1;
        }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: {sidebar_bg};
        }}

        ::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
        
        /* Status Indicators */
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 10px currentColor;
        }}
        
        .status-active {{ background-color: var(--neon-green); color: var(--neon-green); }}
        .status-warning {{ background-color: #ffaa00; color: #ffaa00; }}
        .status-error {{ background-color: #ff0055; color: #ff0055; }}

        </style>
    """, unsafe_allow_html=True)

def render_legendary_header():
    st.markdown('<h1 class="main-header">FOREVER FIT</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">EVOLVE • TRANSCEND • CONQUER</p>', unsafe_allow_html=True)

@contextmanager
def card_container(key=None):
    """Context manager that wraps content in a glassmorphism card."""
    st.markdown('<div class="legendary-card">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

def render_status_badge(status, label):
    color_class = "status-active" if status else "status-warning"
    st.markdown(f"""
        <div style="display: flex; align-items: center; background: rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
            <span class="status-indicator {color_class}"></span>
            <span style="font-family: 'Rajdhani'; font-weight: 600; color: white;">{label}</span>
        </div>
    """, unsafe_allow_html=True)