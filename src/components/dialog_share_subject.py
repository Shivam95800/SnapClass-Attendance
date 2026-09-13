import streamlit as st
import segno
import io
import socket
from src.database.db import create_session


def _get_network_ip():
    """Detect local LAN IP so phones on the same Wi-Fi can open the app."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


@st.dialog("Share Class QR & Link")
def share_subject_dialog(subject_name, subject_code, subject_id=None):
    lan_ip = _get_network_ip()

    # Detect current host if running on Streamlit Cloud or custom server
    detected_host = ""
    if hasattr(st, "context") and hasattr(st.context, "headers") and st.context.headers:
        detected_host = (
            st.context.headers.get("x-forwarded-host")
            or st.context.headers.get("host")
            or ""
        )

    is_on_cloud = bool(detected_host and ("streamlit.app" in detected_host or "localhost" not in detected_host and "127.0.0.1" not in detected_host))
    default_cloud_url = f"https://{detected_host}" if is_on_cloud else "https://snapclass-attendance-gcel.streamlit.app"

    # Network destination selection for QR Code
    url_mode_options = [
        f"☁️ Cloud Deployment ({default_cloud_url})",
        f"📱 Mobile on Local Wi-Fi (http://{lan_ip}:8501)",
        "💻 Localhost (http://localhost:8501)",
        "✏️ Custom URL...",
    ]

    # Default to Cloud if deployed, otherwise Wi-Fi for local testing
    default_idx = 0 if is_on_cloud else 1
    selected_mode = st.selectbox("QR Code Target Network", options=url_mode_options, index=default_idx)

    if selected_mode.startswith("☁️ Cloud Deployment"):
        base_url = default_cloud_url
    elif selected_mode.startswith("📱 Mobile on Local Wi-Fi"):
        base_url = f"http://{lan_ip}:8501"
    elif selected_mode.startswith("💻 Localhost"):
        base_url = "http://localhost:8501"
    else:
        custom_input = st.text_input(
            "Enter Deployed App Domain or URL",
            value=default_cloud_url,
            help="Enter your app's live URL (e.g. https://snapclass-attendance-gcel.streamlit.app)"
        ).strip()
        if custom_input.startswith("http://") or custom_input.startswith("https://"):
            base_url = custom_input.rstrip("/")
        else:
            base_url = f"https://{custom_input.rstrip('/')}"

    col_ttl, col_stat = st.columns([2, 1], vertical_alignment="bottom")
    with col_ttl:
        ttl_options = {"15 Minutes": 15, "30 Minutes": 30, "60 Minutes": 60, "24 Hours": 1440}
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
        join_url = f"{base_url}/?join-code={subject_code}&session={session_id}"
    else:
        join_url = f"{base_url}/?join-code={subject_code}"

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)

    st.markdown(
        f"<div style='background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 10px 14px; margin: 8px 0 16px 0;'>"
        f"<span style='color: #15803D; font-weight: 700; font-size: 0.85rem;'>⏳ Security TTL Active:</span> "
        f"<span style='color: #166534; font-size: 0.85rem;'>Valid for {ttl_minutes} minutes. Session Code: <code style='background: #DCFCE7; font-weight: 700;'>{session_id or 'GENERAL'}</code></span>"
        f"</div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Join Link')
        st.code(join_url, language="text")
        st.caption(f"Course Code: **{subject_code}**")
        st.info('Scan QR or copy link above to self-enroll.')

        if st.button("🔄 Generate Fresh QR Code", type="tertiary", width="stretch"):
            if subject_id:
                st.session_state[session_key] = create_session(subject_id, ttl_minutes)
                st.rerun()

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption=f'QR Code ({ttl_minutes}m Expiry)')

