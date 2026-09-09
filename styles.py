import streamlit as st

def apply_custom_css():
    """Injects Mobile Suit Gundam: Iron-Blooded Orphans (Tekkadan / Barbatos UI) CSS theme into Streamlit."""
    st.markdown("""
        <style>
        /* Import Industrial & Military Monospace Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');

        /* Global Canvas - Industrial Hangar Metallic Theme */
        html, body, [class*="css"] {
            font-family: 'Share Tech Mono', monospace;
            background-color: #0b0c0e;
            color: #d1d5db;
        }

        .stApp {
            background: radial-gradient(circle at 50% 20%, #171a21 0%, #0b0c0e 80%);
            background-attachment: fixed;
        }

        /* Titles & Headings - Alaya-Vijnana System HUD Style */
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            color: #f3f4f6 !important;
            text-shadow: 0 0 10px rgba(0, 255, 170, 0.3);
        }

        /* Sidebar - Tekkadan Mobile Suit Chassis Cockpit Style */
        section[data-testid="stSidebar"] {
            background-color: #111318 !important;
            border-right: 2px solid #b91c1c !important;
            box-shadow: 5px 0 15px rgba(0,0,0,0.8);
        }

        /* Metric Cards - Angular Armor Plating with Red Accent Chamfers */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #181b22 0%, #0f1115 100%);
            border: 1px solid #374151;
            border-left: 4px solid #b91c1c;
            border-radius: 0px !important;
            clip-path: polygon(0 0, 95% 0, 100% 15%, 100% 100%, 0 100%);
            padding: 16px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        }

        div[data-testid="stMetricValue"] {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #10b981 !important; /* Alaya-Vijnana Emerald Glow */
            text-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }

        /* Primary Execution Button - Tekkadan Crimson & Gold Hazard */
        .stButton>button {
            width: 100%;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 0.9rem !important;
            letter-spacing: 1.5px !important;
            background: linear-gradient(90deg, #991b1b 0%, #dc2626 100%) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border: 1px solid #f59e0b !important;
            border-radius: 0px !important;
            clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
            padding: 0.7rem 1rem !important;
            transition: all 0.2s ease-in-out !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }

        .stButton>button:hover {
            background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%) !important;
            box-shadow: 0 0 15px rgba(220, 38, 38, 0.6) !important;
            color: #ffffff !important;
            transform: scale(1.01);
        }

        /* Inputs - Gunmetal Armor Box */
        .stTextInput>div>div>input {
            font-family: 'Share Tech Mono', monospace !important;
            background-color: #181b22 !important;
            color: #f3f4f6 !important;
            border: 1px solid #4b5563 !important;
            border-radius: 0px !important;
            border-left: 3px solid #f59e0b !important;
        }

        .stTextInput>div>div>input:focus {
            border-color: #10b981 !important;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3) !important;
        }

        /* Tabs - Tactical Combat Module Switcher */
        button[data-baseweb="tab"] {
            font-family: 'Orbitron', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: #9ca3af !important;
            border-radius: 0px !important;
            background: #111318;
            border: 1px solid #1f2937;
            margin-right: 4px;
        }

        button[aria-selected="true"] {
            color: #10b981 !important;
            background: #1f2937 !important;
            border-bottom: 3px solid #10b981 !important;
            text-shadow: 0 0 6px rgba(16, 185, 129, 0.4);
        }

        /* Custom Scrollbar - Iron-Blooded Metal Track */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0b0c0e;
        }
        ::-webkit-scrollbar-thumb {
            background: #b91c1c;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #ef4444;
        }
        </style>
    """, unsafe_allow_html=True)