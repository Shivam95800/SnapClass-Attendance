import streamlit as st
from src.database.db import create_subject, get_subject_by_code


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="e.g. CS002")
    sub_name = st.text_input("Subject Name", placeholder="e.g. Internet Of Things")
    sub_section = st.text_input("Section", placeholder="e.g. CS DS A")

    if st.button("Create Subject Now", type='primary', width='stretch'):
        sub_code_clean = sub_id.strip().upper() if sub_id else ""
        sub_name_clean = sub_name.strip() if sub_name else ""
        sub_section_clean = sub_section.strip() if sub_section else ""

        if sub_code_clean and sub_name_clean and sub_section_clean:
            existing = get_subject_by_code(sub_code_clean)
            if existing:
                st.error(f"⚠️ Subject code **'{sub_code_clean}'** is already taken by *{existing.get('name')}*. Please use a unique subject code (e.g. CS003).")
                return

            try:
                create_subject(sub_code_clean, sub_name_clean, sub_section_clean, teacher_id)
                st.toast("Subject Created Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill all the fields")
