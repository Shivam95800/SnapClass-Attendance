import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%) !important;
                background-attachment: fixed !important;
            }

            /* Home Portal Cards */
            .stApp [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                background: #FFFFFF !important;
                padding: 2.75rem 2.25rem !important;
                border-radius: 1.75rem !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
                box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.35) !important;
                transition: transform 0.25s ease, box-shadow 0.25s ease !important;
            }

            .stApp [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 25px 50px -12px rgba(88, 101, 242, 0.4) !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%) !important;
                background-attachment: fixed !important;
            }

            /* Container cards */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 1.25rem !important;
                border: 1px solid rgba(226, 232, 240, 0.9) !important;
                background: rgba(255, 255, 255, 0.9) !important;
                backdrop-filter: blur(12px) !important;
                box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04) !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

            /* Hide Top Bar of streamlit */
            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 1050px !important;
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0.5rem !important;
                letter-spacing: -0.02em;
            }

            h2 {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 700 !important;
                font-size: 1.75rem !important;
                line-height: 1.2 !important;
                margin-bottom: 0.5rem !important;
                color: #0F172A !important;
                letter-spacing: -0.01em;
            }

            h3 {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                font-size: 1.35rem !important;
                color: #1E293B !important;
            }

            h4, p, span, label {
                font-family: 'Inter', sans-serif !important;
            }

            /* Buttons - Linear style */
            button {
                border-radius: 0.875rem !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                padding: 10px 20px !important;
                border: 1px solid transparent !important;
                transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            }

            button[kind="primary"] {
                background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%) !important;
                color: white !important;
                box-shadow: 0 4px 14px 0 rgba(88, 101, 242, 0.35) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }

            button[kind="primary"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px 0 rgba(88, 101, 242, 0.5) !important;
                background: linear-gradient(135deg, #6975f5 0%, #5865F2 100%) !important;
            }

            button[kind="secondary"] {
                background: linear-gradient(135deg, #EB459E 0%, #D83A8F 100%) !important;
                color: white !important;
                box-shadow: 0 4px 14px 0 rgba(235, 69, 158, 0.35) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }

            button[kind="secondary"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px 0 rgba(235, 69, 158, 0.5) !important;
            }

            button[kind="tertiary"] {
                background: #FFFFFF !important;
                color: #334155 !important;
                border: 1px solid #CBD5E1 !important;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
            }

            button[kind="tertiary"]:hover {
                transform: translateY(-2px) !important;
                background: #F1F5F9 !important;
                color: #0F172A !important;
                border-color: #94A3B8 !important;
            }

            /* Inputs & Selectbox */
            div[data-baseweb="input"], div[data-baseweb="select"] {
                border-radius: 0.75rem !important;
            }

            /* Dialog Styling */
            div[data-testid="stDialog"] {
                border-radius: 1.5rem !important;
            }

            /* Dataframe styling */
            div[data-testid="stDataFrame"] {
                border-radius: 1rem !important;
                overflow: hidden !important;
                border: 1px solid #E2E8F0 !important;
            }
        </style>
    """, unsafe_allow_html=True)