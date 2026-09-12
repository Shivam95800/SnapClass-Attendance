import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    header_home()
    style_background_home()
    style_base_layout()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="text-align: center;">
                <h2 style="text-align: center; color: #0F172A; margin: 0 0 8px 0; font-size: 1.65rem;">I'm a Student</h2>
                <p style="text-align: center; color: #64748B; font-size: 0.95rem; margin-bottom: 24px; min-height: 48px; line-height: 1.4;">
                    Check your attendance records, join courses via QR, or log in with FaceID.
                </p>
                <div style="display: flex; justify-content: center; align-items: center; height: 140px; margin-bottom: 24px;">
                    <img src="https://i.ibb.co/844D9Lrt/mascot-student.png" style="height: 120px; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.08));" />
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button('Enter Student Portal →', type='primary', width='stretch', key='home_student_btn'):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <h2 style="text-align: center; color: #0F172A; margin: 0 0 8px 0; font-size: 1.65rem;">I'm a Teacher</h2>
                <p style="text-align: center; color: #64748B; font-size: 0.95rem; margin-bottom: 24px; min-height: 48px; line-height: 1.4;">
                    Manage your courses, share join links, and take multi-face or voice attendance.
                </p>
                <div style="display: flex; justify-content: center; align-items: center; height: 140px; margin-bottom: 24px;">
                    <img src="https://i.ibb.co/CsmQQV6X/mascot-prof.png" style="height: 130px; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.08));" />
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button('Enter Teacher Portal →', type='primary', width='stretch', key='home_teacher_btn'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    guide_col1, guide_col2, guide_col3 = st.columns([1, 2, 1])
    with guide_col2:
        if st.button("✨ Open SnapClass AI Guide & Assistant", type="secondary", width="stretch", key="home_ai_guide_btn"):
            from src.components.dialog_ai_guide import ai_guide_dialog
            ai_guide_dialog(role="general")

    footer_home()