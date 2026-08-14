import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np
from datetime import datetime
import pandas as pd
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog
import time


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    # Top Navbar Row
    nav_c1, nav_c2 = st.columns([3, 2], vertical_alignment='center')
    with nav_c1:
        header_dashboard()
    with nav_c2:
        btn_c1, btn_c2 = st.columns([2, 1], vertical_alignment='center')
        with btn_c1:
            st.markdown(f"<div style='text-align: right; color: #0F172A; font-weight: 600; font-size: 0.95rem;'>Hi, {teacher_data['name']} 👋</div>", unsafe_allow_html=True)
        with btn_c2:
            if st.button("Logout", type='tertiary', key='teacher_logout_btn', icon=":material/logout:"):
                st.session_state['is_logged_in'] = False
                if 'teacher_data' in st.session_state:
                    del st.session_state.teacher_data
                st.rerun()

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    # Linear-inspired Segmented Pill Navigation
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab_col1, tab_col2, tab_col3 = st.columns(3)

    with tab_col1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('📸 Take Attendance', type=type1, width='stretch'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab_col2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('📚 Manage Subjects', type=type2, width='stretch'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab_col3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('📊 Attendance Records', type=type3, width='stretch'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info('✨ You haven\'t created any subjects yet. Switch to the **Manage Subjects** tab to create one.')
        return

    subject_options = {f"{s['name']} ({s['subject_code']}) - Sec {s['section']}": s['subject_id'] for s in subjects}

    # Subject selection card
    with st.container(border=True):
        st.markdown("<h3 style='margin-top: 0;'>1. Select Course &amp; Upload Photos</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1], vertical_alignment='bottom')

        with col1:
            selected_subject_label = st.selectbox('Course', options=list(subject_options.keys()), label_visibility='collapsed')

        with col2:
            if st.button('Add Photos', type='primary', icon=':material/add_a_photo:', width='stretch'):
                add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    # Gallery preview if photos exist
    if st.session_state.attendance_images:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"<h4>Classroom Snapshots ({len(st.session_state.attendance_images)})</h4>", unsafe_allow_html=True)
        gallery_cols = st.columns(min(4, len(st.session_state.attendance_images)))

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % len(gallery_cols)]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')

    has_photos = bool(st.session_state.attendance_images)
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Action Toolbar
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear Photos', width='stretch', type='tertiary', icon=':material/delete_sweep:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', width='stretch', type='primary', icon=':material/face:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course yet.')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Voice Attendance', type='secondary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']

    header_c1, header_c2 = st.columns([3, 1], vertical_alignment='center')
    with header_c1:
        st.markdown("<h2 style='margin: 0;'>Your Courses &amp; Sections</h2>", unsafe_allow_html=True)
    with header_c2:
        if st.button('＋ Create Subject', type='primary', width='stretch'):
            create_subject_dialog(teacher_id)

    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        cols = st.columns(2)
        for i, sub in enumerate(subjects):
            stats = [
                ("👥", "Students", sub.get('total_students', 0)),
                ("📅", "Classes Held", sub.get('total_classes', 0)),
            ]

            def make_share_btn(current_sub=sub):
                def share_btn():
                    if st.button(f"Share Code & QR", key=f"share_{current_sub['subject_code']}_{current_sub['subject_id']}", icon=":material/qr_code_2:", width='stretch', type='tertiary'):
                        share_subject_dialog(current_sub['name'], current_sub['subject_code'])
                return share_btn

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=stats,
                    footer_callback=make_share_btn(sub)
                )
    else:
        st.info("No subjects found. Click **＋ Create Subject** above to create your first class!")


def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.markdown("<h2 style='margin: 0 0 1rem 0;'>Attendance History</h2>", unsafe_allow_html=True)

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info("No attendance records found yet. Take attendance to see logs here.")
        return

    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count')
        ).reset_index()
    )

    summary['Attendance Rate'] = (
        "✅ " + summary['Present_Count'].astype(str) + " / "
        + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = (
        summary.sort_values(by='ts_group', ascending=False)
        [['Time', 'Subject', 'Subject Code', 'Attendance Rate']]
    )

    st.dataframe(display_df, width='stretch', hide_index=True)


def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type='tertiary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; margin: 0 0 1rem 0; color: #0F172A;'>Teacher Portal Login</h2>", unsafe_allow_html=True)

        with st.form("teacher_login_form"):
            teacher_username = st.text_input("Username", placeholder='e.g. ananyaroy')
            teacher_pass = st.text_input("Password", type='password', placeholder="Enter your password")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            btnc1, btnc2 = st.columns(2)

            with btnc1:
                submitted = st.form_submit_button('Login', use_container_width=True, type='primary')
            with btnc2:
                go_register = st.form_submit_button('Create Account', use_container_width=True)

        if submitted:
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back!", icon="👋")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid username or password.")

        if go_register:
            st.session_state.teacher_login_type = 'register'
            st.rerun()

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username is already taken."
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Account created successfully! Please log in."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("← Back to Home", type='tertiary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h2 style='text-align: center; margin: 0 0 1rem 0; color: #0F172A;'>Register Teacher Profile</h2>", unsafe_allow_html=True)

        with st.form("teacher_register_form"):
            teacher_name = st.text_input("Full Name", placeholder='e.g. Dr. Ananya Roy')
            teacher_username = st.text_input("Username", placeholder='e.g. ananyaroy')
            teacher_pass = st.text_input("Password", type='password', placeholder="Choose a strong password")
            teacher_pass_confirm = st.text_input("Confirm Password", type='password', placeholder="Re-enter your password")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            btnc1, btnc2 = st.columns(2)

            with btnc1:
                submitted = st.form_submit_button('Register Account', use_container_width=True, type='primary')
            with btnc2:
                go_login = st.form_submit_button('Login Instead', use_container_width=True)

        if submitted:
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(1.5)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

        if go_login:
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()