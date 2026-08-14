import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    header_home()
    style_background_home()
    style_base_layout()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1E1B4B; margin-bottom: 8px;'>I'm a Student</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #475569; font-size: 0.95rem; margin-bottom: 20px;'>Check your attendance records, join courses via QR, or log in with FaceID.</p>", unsafe_allow_html=True)
        c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
        with c_img2:
            st.image("https://i.ibb.co/844D9Lrt/mascot-student.png", width=120)
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button('Enter Student Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width='stretch'):
            st.session_state['login_type'] = 'student'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1E1B4B; margin-bottom: 8px;'>I'm a Teacher</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #475569; font-size: 0.95rem; margin-bottom: 20px;'>Manage your courses, share join links, and take multi-face or voice attendance.</p>", unsafe_allow_html=True)
        c_img1, c_img2, c_img3 = st.columns([1, 2, 1])
        with c_img2:
            st.image("https://i.ibb.co/CsmQQV6X/mascot-prof.png", width=135)
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button('Enter Teacher Portal', type='primary', icon=':material/arrow_outward:', icon_position='right', width='stretch'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    footer_home()