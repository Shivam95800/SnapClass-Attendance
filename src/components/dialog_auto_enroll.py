import streamlit as st
from src.database.db import (
    get_subject_by_code,
    check_student_enrolled,
    enroll_student_to_subject,
)
import time


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data['student_id']

    subject = get_subject_by_code(subject_code.strip())
    if not subject:
        st.error('Subject code not found!')
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
        return

    if check_student_enrolled(student_id, subject['subject_id']):
        st.info("You're already enrolled in this course!")
        if st.button('Got it!'):
            st.query_params.clear()
            st.rerun()
        return

    sub_name = subject['name']
    st.markdown(f"Would you like to enroll in **{sub_name}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('No thanks'):
            st.query_params.clear()
            st.rerun()
    with col2:
        if st.button('Yes, Enroll Now', type='primary', width='stretch'):
            enroll_student_to_subject(student_id, subject['subject_id'])
            st.success('Joined course successfully!')
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
