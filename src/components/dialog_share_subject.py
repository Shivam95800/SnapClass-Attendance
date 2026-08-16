import streamlit as st
import segno
import io
from src.database.db import create_session


@st.dialog("Share Class QR & Link")
def share_subject_dialog(subject_name, subject_code, subject_id=None):
    app_domain = "snapclass-main.streamlit.app"

    ttl_options = {"15 Minutes": 15, "30 Minutes": 30, "60 Minutes": 60}
    selected_ttl_label = st.selectbox(
        "Session Expiry Window (TTL)",
        options=list(ttl_options.keys()),
        index=0,
        help="QR code and link will automatically expire after this duration to prevent proxy attendance."
    )
    ttl_minutes = ttl_options[selected_ttl_label]

    session_key = f"active_session_{subject_code}"
    # Generate or retrieve session
    if session_key not in st.session_state or st.session_state[session_key].get("ttl_minutes") != ttl_minutes:
        if subject_id:
            st.session_state[session_key] = create_session(subject_id, ttl_minutes)
        else:
            st.session_state[session_key] = {}

    session_data = st.session_state.get(session_key, {})
    session_id = session_data.get("session_id", "")

    if session_id:
        join_url = f"https://{app_domain}/?join-code={subject_code}&session={session_id}"
    else:
        join_url = f"https://{app_domain}/?join-code={subject_code}"

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)

    st.markdown(
        f"<div style='background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 10px 14px; margin: 8px 0 16px 0;'>"
        f"<span style='color: #15803D; font-weight: 700; font-size: 0.85rem;'>⏳ Security TTL Active:</span> "
        f"<span style='color: #166534; font-size: 0.85rem;'>Valid for {ttl_minutes} minutes from creation. Session Code: <code style='background: #DCFCE7; font-weight: 700;'>{session_id or 'GENERAL'}</code></span>"
        f"</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info('Share this link with students in class.')

        if st.button("🔄 Generate Fresh QR Code", type="tertiary", width="stretch"):
            if subject_id:
                st.session_state[session_key] = create_session(subject_id, ttl_minutes)
                st.rerun()

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption=f'QR Code ({ttl_minutes}m Expiry)')
