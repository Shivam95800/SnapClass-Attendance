import streamlit as st


def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 25px; margin-top: 15px;">
            <img src='{logo_url}' style='height: 90px; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2)); margin-bottom: 10px;' />
            <h1 style='text-align: center; color: #FFFFFF; font-size: 2.75rem; margin: 0; letter-spacing: -0.03em;'>SNAP<br/>CLASS</h1>
            <p style='color: #C7D2FE; font-size: 1rem; margin-top: 6px; font-weight: 500;'>AI-Powered Smart Attendance System</p>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <img src='{logo_url}' style='height: 52px; filter: drop-shadow(0 4px 6px rgba(88, 101, 242, 0.2));' />
            <div>
                <h2 style='text-align: left; color: #5865F2; font-size: 1.45rem; font-weight: 800; line-height: 1; margin: 0; letter-spacing: -0.02em;'>SNAPCLASS</h2>
                <span style='font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;'>AI Attendance Hub</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
