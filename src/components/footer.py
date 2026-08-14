import streamlit as st


def footer_home():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"

    st.markdown(f"""
        <div style="margin-top: 3rem; display: flex; gap: 8px; justify-content: center; align-items: center; opacity: 0.85;">
            <p style="font-weight: 500; font-size: 0.88rem; color: #E0E7FF; margin: 0;">Created with ❤️ by</p>
            <img src='{logo_url}' style='max-height: 22px;' />
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"

    st.markdown(f"""
        <div style="margin-top: 3rem; display: flex; gap: 8px; justify-content: center; align-items: center; opacity: 0.75;">
            <p style="font-weight: 500; font-size: 0.85rem; color: #64748B; margin: 0;">Created with ❤️ by</p>
            <img src='{logo_url}' style='max-height: 20px;' />
        </div>
    """, unsafe_allow_html=True)
