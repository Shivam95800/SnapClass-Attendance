import streamlit as st


def footer_home():
    github_url = "https://github.com/Shivam95800"

    st.markdown(f"""
        <div style="margin-top: 3rem; display: flex; gap: 6px; justify-content: center; align-items: center; opacity: 0.9;">
            <p style="font-weight: 500; font-size: 0.9rem; color: #E0E7FF; margin: 0;">Created with ❤️ by</p>
            <a href="{github_url}" target="_blank" style="color: #FFFFFF; font-weight: 700; text-decoration: underline; text-underline-offset: 3px; font-size: 0.9rem;">Shivam Soni</a>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    github_url = "https://github.com/Shivam95800"

    st.markdown(f"""
        <div style="margin-top: 3rem; display: flex; gap: 6px; justify-content: center; align-items: center; opacity: 0.85;">
            <p style="font-weight: 500; font-size: 0.88rem; color: #64748B; margin: 0;">Created with ❤️ by</p>
            <a href="{github_url}" target="_blank" style="color: #5865F2; font-weight: 700; text-decoration: underline; text-underline-offset: 3px; font-size: 0.88rem;">Shivam Soni</a>
        </div>
    """, unsafe_allow_html=True)
