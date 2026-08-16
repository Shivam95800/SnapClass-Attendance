import streamlit as st
from src.database.db import (
    get_subject_by_code,
    check_student_enrolled,
    enroll_student_to_subject,
    verify_session,
)
import time


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code, session_token=None):
    student_id = st.session_state.student_data['student_id']

    # 1. Verify session TTL if a session token was embedded
    if session_token:
        is_valid, msg, _ = verify_session(session_token)
        if not is_valid:
            st.error(f"⚠️ **Session Expired or Invalid**: {msg}")
            if st.button('Dismiss', width='stretch'):
                st.query_params.clear()
                st.rerun()
            return

    # 2. Find subject
    subject = get_subject_by_code(subject_code.strip())
    if not subject:
        st.error('Subject code not found!')
        if st.button('Close', width='stretch'):
            st.query_params.clear()
            st.rerun()
        return

    # 3. Check existing enrollment
    if check_student_enrolled(student_id, subject['subject_id']):
        st.info(f"You are already enrolled in **{subject['name']}** ({subject['subject_code']})!")
        if st.button('Got it!', width='stretch'):
            st.query_params.clear()
            st.rerun()
        return

    sub_name = subject['name']
    st.markdown(f"Would you like to enroll in **{sub_name}** (`{subject['subject_code']}`)?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('No thanks', width='stretch'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Yes, Enroll Now', type='primary', width='stretch'):
            enroll_student_to_subject(student_id, subject['subject_id'])
            st.success('Joined course successfully!')
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
