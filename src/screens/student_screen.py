import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier, check_liveness
from src.pipelines.voice_pipeline import get_voice_embedding, generate_voice_challenge, transcribe_and_verify_phrase
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
        guide_c, btn_c1, btn_c2 = st.columns([1.2, 1.8, 1], vertical_alignment='center')
        with guide_c:
            if st.button("✨ AI Guide", type='secondary', key='student_ai_guide_btn'):
                from src.components.dialog_ai_guide import ai_guide_dialog
                ai_guide_dialog(role="student")
        with btn_c1:
            st.markdown(f"<div style='text-align: right; color: #0F172A; font-weight: 600; font-size: 0.95rem;'>Hi, {student_data['name']} 👋</div>", unsafe_allow_html=True)
        with btn_c2:
            if st.button("🚪 Logout", type='tertiary', key='student_logout_btn'):
                st.session_state.clear()
                st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    header_col1, header_col2, header_col3 = st.columns([2, 1, 1], vertical_alignment='center')
    with header_col1:
        st.markdown("<h2 style='margin: 0;'>Enrolled Courses</h2>", unsafe_allow_html=True)
    with header_col2:
        if st.button('＋ Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()
    with header_col3:
        if st.button('👤 Switch / New Student', type='secondary', width='stretch'):
            st.session_state.clear()
            st.session_state['login_type'] = 'student'
            st.rerun()

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
                    if st.button("🗑️ Unenroll Course", key=f"unenroll_{current_sid}", type='tertiary', width='stretch'):
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

    if "student_data" in st.session_state and st.session_state.get('is_logged_in', False):
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
        pending_join_code = st.query_params.get('join-code')
        if pending_join_code:
            st.info(f"📲 **Course Enrollment in Progress**: You are joining course `{pending_join_code}`. Complete your FaceID login or profile registration below to finish enrolling!")

        st.markdown("<h2 style='text-align: center; margin: 0 0 0.5rem 0; color: #0F172A;'>Student FaceID Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 1.5rem;'>Position your face in the center of the camera. Anti-spoofing requires a 2-shot liveness check (Eyes Open + Blink).</p>", unsafe_allow_html=True)

        if "liveness_frames" not in st.session_state:
            st.session_state.liveness_frames = []

        direct_register = st.toggle("➕ Register new student profile manually", value=False)
        show_registration = direct_register

        # Guided Step Indicator
        num_captured = len(st.session_state.liveness_frames)
        if num_captured == 0:
            st.info("📸 **Step 1 of 2**: Look straight into the camera with **eyes open** and take a snapshot.")
            photo_source = st.camera_input("Step 1: Face Scan (Eyes Open)", key="face_cam_step1")
            if photo_source:
                st.session_state.liveness_frames.append(Image.open(photo_source))
                st.rerun()

        elif num_captured == 1:
            st.info("👁️ **Step 2 of 2 (Anti-Spoofing)**: Now **blink or close your eyes** and take a 2nd snapshot to verify live presence.")
            photo_source = st.camera_input("Step 2: Blink Verification", key="face_cam_step2")

            c_retry1, c_retry2 = st.columns([3, 1])
            with c_retry2:
                if st.button("🔄 Retake Step 1", type="tertiary"):
                    st.session_state.liveness_frames = []
                    st.rerun()

            if photo_source:
                st.session_state.liveness_frames.append(Image.open(photo_source))
                st.rerun()

        else:
            # 2 frames captured: Run Liveness Anti-Spoofing & Attendance prediction
            frame_open = np.array(st.session_state.liveness_frames[0].convert('RGB'))
            frame_blink = np.array(st.session_state.liveness_frames[1].convert('RGB'))

            with st.spinner('AI is performing anti-spoofing liveness & biometric analysis...'):
                is_live = check_liveness([frame_open, frame_blink])

                if not is_live:
                    st.error("⚠️ **Liveness Verification Failed**: No natural eye blink detected across the frames. Holding up a static photo or video replay is prohibited. Please retry with a live camera.")
                    if st.button("🔄 Retry Liveness Verification", type="primary"):
                        st.session_state.liveness_frames = []
                        st.rerun()
                else:
                    detected, all_ids, num_faces = predict_attendance(frame_open)

                    if num_faces == 0:
                        st.warning('No face detected in the primary frame. Please ensure good lighting and face the camera directly.')
                        if st.button("🔄 Try Again"):
                            st.session_state.liveness_frames = []
                            st.rerun()
                    elif num_faces > 1:
                        st.warning('Multiple faces detected. Please ensure only one person is in frame.')
                        if st.button("🔄 Try Again"):
                            st.session_state.liveness_frames = []
                            st.rerun()
                    else:
                        if detected:
                            student_id = list(detected.keys())[0]
                            all_students = get_all_students()
                            student = next((s for s in all_students if s['student_id'] == student_id), None)

                            if student:
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = student
                                st.session_state.liveness_frames = []
                                st.toast(f"Welcome back, {student['name']}! (Liveness Verified ✅)", icon="👋")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.info('Face liveness verified ✅, but profile is not recognized in our database. Register below!')
                            show_registration = True

        if show_registration:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0F172A;'>Register New Student Profile</h3>", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder='e.g. Akash Sharma')

            direct_cam = None
            if not st.session_state.get('liveness_frames'):
                st.markdown("<h4 style='margin-top: 1rem; color: #0F172A;'>Face Photo</h4>", unsafe_allow_html=True)
                direct_cam = st.camera_input("Take Profile Photo", key="direct_reg_photo")

            st.markdown("<h4 style='margin-top: 1rem; color: #0F172A;'>Voice Biometric Enrollment (Optional)</h4>", unsafe_allow_html=True)
            st.caption("Anti-replay protection: Speak the dynamic security phrase below to enroll your voiceprint.")

            if "voice_enroll_challenge" not in st.session_state or not st.session_state.voice_enroll_challenge:
                st.session_state.voice_enroll_challenge = generate_voice_challenge()

            challenge = st.session_state.voice_enroll_challenge
            st.markdown(
                f"<div style='background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 10px; padding: 12px 16px; margin: 10px 0 14px 0;'>"
                f"<span style='font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #4F46E5; letter-spacing: 0.05em;'>Dynamic Security Phrase</span>"
                f"<div style='font-family: monospace; font-size: 1.35rem; font-weight: 800; color: #1E1B4B; margin-top: 4px;'>\"{challenge}\"</div>"
                f"</div>",
                unsafe_allow_html=True
            )

            audio_data = None
            try:
                audio_data = st.audio_input(f'Speak "{challenge}" into microphone')
            except Exception:
                st.error('Microphone access failed.')

            if st.button('Complete Registration', type='primary', width='stretch'):
                if new_name:
                    with st.spinner('Validating liveness & generating biometric embeddings...'):
                        if st.session_state.get('liveness_frames'):
                            reg_img = np.array(st.session_state.liveness_frames[0].convert('RGB'))
                        elif direct_cam:
                            reg_img = np.array(Image.open(direct_cam).convert('RGB'))
                        else:
                            reg_img = None

                        if reg_img is None:
                            st.error('No face photo available. Please take a photo with the camera above.')
                        else:
                            encodings = get_face_embeddings(reg_img)
                            if encodings:
                                face_emb = encodings[0].tolist()
                                voice_emb = None
                                voice_valid = True

                                if audio_data:
                                    audio_bytes = audio_data.read()
                                    is_phrase_match, heard_text = transcribe_and_verify_phrase(audio_bytes, challenge)
                                    if not is_phrase_match:
                                        voice_valid = False
                                        st.error(f"⚠️ **Voice Challenge Mismatch**: Heard *\"{heard_text}\"*, but expected *\"{challenge}\"*. Please speak the exact phrase shown to prevent replay attacks.")
                                    else:
                                        voice_emb = get_voice_embedding(audio_bytes)

                                if voice_valid:
                                    response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                                    if response_data:
                                        train_classifier()
                                        st.session_state.is_logged_in = True
                                        st.session_state.user_role = 'student'
                                        st.session_state.student_data = response_data[0]
                                        st.session_state.liveness_frames = []
                                        st.session_state.voice_enroll_challenge = None
                                        st.toast(f"Profile created! Welcome, {new_name}!", icon="🎉")
                                        time.sleep(1)
                                        st.rerun()
                            else:
                                st.error('Could not capture facial features clearly for registration. Please try again.')
                else:
                    st.warning('Please enter your name.')

    footer_dashboard()