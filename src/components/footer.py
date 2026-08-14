import streamlit as st


def footer_home():
    github_url = "https://github.com/Shivam95800"

    st.markdown(f"""
        <div style="margin-top: 3.5rem; display: flex; gap: 8px; justify-content: center; align-items: center;">
            <span style="font-weight: 500; font-size: 0.9rem; color: #C7D2FE;">Created with ❤️ by</span>
            <a href="{github_url}" target="_blank" style="color: #FFFFFF; font-weight: 700; text-decoration: none; background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); padding: 3px 10px; border-radius: 9999px; font-size: 0.88rem; transition: background 0.2s ease;">Shivam Soni ↗</a>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    github_url = "https://github.com/Shivam95800"

    st.markdown(f"""
        <div style="margin-top: 3.5rem; display: flex; gap: 8px; justify-content: center; align-items: center;">
            <span style="font-weight: 500; font-size: 0.88rem; color: #64748B;">Created with ❤️ by</span>
            <a href="{github_url}" target="_blank" style="color: #4F46E5; font-weight: 700; text-decoration: none; background: #EEF2FF; border: 1px solid #C7D2FE; padding: 3px 10px; border-radius: 9999px; font-size: 0.85rem; transition: background 0.2s ease;">Shivam Soni ↗</a>
        </div>
    """, unsafe_allow_html=True)
