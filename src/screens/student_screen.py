import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    # Top Navbar Row
    nav_c1, nav_c2 = st.columns([3, 2], vertical_alignment='center')
    with nav_c1:
        header_dashboard()
    with nav_c2:
        btn_c1, btn_c2 = st.columns([2, 1], vertical_alignment='center')
        with btn_c1:
            st.markdown(f"<div style='text-align: right; color: #0F172A; font-weight: 600; font-size: 0.95rem;'>Hi, {student_data['name']} 👋</div>", unsafe_allow_html=True)
        with btn_c2:
            if st.button("Logout", type='tertiary', key='student_logout_btn', icon=":material/logout:"):
                st.session_state['is_logged_in'] = False
                if 'student_data' in st.session_state:
                    del st.session_state.student_data
                st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    header_col1, header_col2 = st.columns([3, 1], vertical_alignment='center')
    with header_col1:
        st.markdown("<h2 style='margin: 0;'>Enrolled Courses</h2>", unsafe_allow_html=True)
    with header_col2:
        if st.button('＋ Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    with st.spinner('Loading enrolled courses...'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if subjects:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']
            stats = stats_map.get(sid, {"total": 0, "attended": 0})
            attendance_pct = (stats['attended'] / stats['total'] * 100) if stats['total'] > 0 else 100.0

            def make_unenroll_btn(current_sub=sub, current_sid=sid):
                def unenroll_button():
                    if st.button("Unenroll Course", key=f"unenroll_{current_sid}", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                        unenroll_student_to_subject(student_id, current_sid)
                        sub_name = current_sub['name']
                        st.toast(f"Unenrolled from {sub_name} successfully!")
                        time.sleep(0.5)
                        st.rerun()
                return unenroll_button

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        ('📅', 'Total Classes', stats['total']),
                        ('✅', 'Attended', stats['attended']),
                        ('📈', 'Attendance', f"{attendance_pct:.1f}%"),
                    ],
                    footer_callback=make_unenroll_btn(sub, sid)
                )
    else:
        st.info("You are not enrolled in any courses yet. Click **＋ Enroll in Subject** above or scan a class QR code.")

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type='tertiary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; margin: 0 0 0.5rem 0; color: #0F172A;'>Student FaceID Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 1.5rem;'>Position your face in the center of the camera to verify your identity.</p>", unsafe_allow_html=True)

        show_registration = False
        photo_source = st.camera_input("Face Scan", label_visibility="collapsed")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner('AI is scanning your facial features...'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('No face detected. Please ensure good lighting and face the camera directly.')
                elif num_faces > 1:
                    st.warning('Multiple faces detected. Please ensure only one person is in frame.')
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s['student_id'] == student_id), None)

                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.toast(f"Welcome back, {student['name']}!", icon="👋")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.info('Face not recognized in our database. Register your profile below to get started!')
                        show_registration = True

        if show_registration:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0F172A;'>Register New Student Profile</h3>", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder='e.g. Akash Sharma')

            st.markdown("<h4 style='margin-top: 1rem; color: #0F172A;'>Voice Biometric Enrollment (Optional)</h4>", unsafe_allow_html=True)
            st.caption("Record a short voice sample for voice roll-calls.")

            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like "I am present, my name is Akash"')
            except Exception:
                st.error('Microphone access failed.')

            if st.button('Complete Registration', type='primary', width='stretch'):
                if new_name:
                    with st.spinner('Generating biometric embeddings and creating account...'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Profile created! Welcome, {new_name}!", icon="🎉")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Could not capture facial features clearly for registration. Please try again.')
                else:
                    st.warning('Please enter your name.')

    footer_dashboard()