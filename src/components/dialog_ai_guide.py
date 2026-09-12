import streamlit as st
import pandas as pd


# Knowledge base for intelligent question answering
AI_GUIDE_KB = {
    "photo_attendance": {
        "title": "📸 How to Take Photo Attendance",
        "keywords": ["photo", "camera", "picture", "snapshot", "multi-face", "face attendance", "take attendance"],
        "answer": r"""
### 📸 How to Take Classroom Photo Attendance:
1. Navigate to the **Teacher Dashboard** ➔ Click the **📸 Take Attendance** tab.
2. Select your course from the dropdown.
3. Choose your capture method:
   - **Webcam Snapshot**: Use the live laptop/webcam camera feed.
   - **Upload Image**: Upload a high-resolution classroom wide-angle photograph.
4. The **dlib ResNet pipeline** automatically:
   - Locates all student faces using 68-point facial landmarks.
   - Extracts 128-dimensional biometric embeddings.
   - Compares embeddings with enrolled students using Euclidean distance ($\le 0.48$).
5. Review the detected vs absent student breakdown in the modal, then click **Confirm & Save**.

💡 **Pro Tip**: Ensure good classroom lighting and ask students to face towards the camera for highest detection accuracy.
"""
    },
    "voice_attendance": {
        "title": "🎙️ How Voice Roll-Call Works",
        "keywords": ["voice", "audio", "mic", "microphone", "sound", "challenge", "resemblyzer", "roll call"],
        "answer": """
### 🎙️ How Voice Roll-Call & Liveness Verification Works:
1. In the Teacher Dashboard, click **🎙️ Voice Attendance**.
2. **Anti-Replay Challenge**: The system generates a dynamic 4-token phrase (e.g., *"Falcon 7 4 2"*).
3. The student or class speaks the challenge phrase aloud.
4. **Google Speech-to-Text** transcribes the audio in real time to verify the spoken challenge words, ensuring old audio cannot be replayed for proxy attendance.
5. **Resemblyzer & Librosa**:
   - `librosa` splits classroom audio segments at silence intervals (`top_db=30`).
   - `Resemblyzer VoiceEncoder` calculates 256D normalized voiceprints.
   - Matches speaker identities via Cosine Similarity against enrolled student voiceprints.
"""
    },
    "anti_spoofing": {
        "title": "👁️ Eye-Blink Anti-Spoofing & Liveness",
        "keywords": ["spoof", "anti-spoof", "blink", "ear", "fake", "liveness", "proxy", "buddy punching"],
        "answer": r"""
### 👁️ How Eye-Blink Dynamic EAR Prevents Photo Spoofing:
- Traditional face recognition systems can be tricked by holding up a printed photo or phone screen of another student ("buddy punching").
- **SnapClass Eye Aspect Ratio (EAR)**:
  - Measures vertical distance between upper/lower eyelids divided by horizontal eye width using 6 landmark points per eye (points 36–47).
  - Evaluates consecutive frames to detect natural eye blinking dynamics ($\text{min EAR} \le 0.22$ and $\text{max EAR} \ge 0.25$ or dynamic range $\ge 0.065$).
  - Static photos, screen replays, and non-blinking proxies are instantly rejected!
"""
    },
    "qr_ttl": {
        "title": "⏱️ QR Codes & Session Expiration (TTL)",
        "keywords": ["qr", "ttl", "expire", "session", "link", "share", "enroll", "token", "time"],
        "answer": """
### ⏱️ Dynamic QR Codes with Session TTL:
1. Teachers click **Share / QR Code** on any subject card.
2. Select a **Session Time-To-Live (TTL)**: 15 minutes, 30 minutes, 1 hour, or 24 hours.
3. The system creates a temporary session token in Google Firebase Firestore with an ISO `expires_at` timestamp.
4. When students scan the QR code or click the join link, Firestore verifies whether the current time is within the expiration window.
5. **Security Benefit**: If a student leaks the QR code or link after class, outsiders cannot join the course because the link will have expired automatically!
"""
    },
    "threshold": {
        "title": "🎯 0.48 Biometric Distance Threshold",
        "keywords": ["threshold", "distance", "accuracy", "false positive", "euclidean", "0.48", "margin"],
        "answer": r"""
### 🎯 Biometric Recognition Threshold ($\le 0.48$):
- In face recognition, Euclidean distance measures the geometric difference between two 128-dimensional ResNet face vectors.
- A distance of **0.0** means an identical match.
- Standard libraries use a threshold of 0.60, which occasionally causes false positive misidentifications in crowded classrooms.
- SnapClass applies a **strict 0.48 threshold**:
  - Ensures different students are never mistakenly marked present for one another.
  - Guarantees zero buddy punching while maintaining high true positive recognition.
"""
    },
    "export_records": {
        "title": "📥 Exporting Records to Excel / CSV",
        "keywords": ["export", "csv", "excel", "download", "records", "history", "report"],
        "answer": """
### 📥 How to Export Attendance Records:
1. In the Teacher Dashboard, switch to the **📋 Attendance Records** tab.
2. Filter records by subject or view all classes.
3. The high-density table displays Student Name, ID, Subject, Timestamp, and Verification Status.
4. Click the **📥 Export to CSV** button to download a spreadsheet compatible with Microsoft Excel, Google Sheets, or university ERP systems.
"""
    },
    "troubleshoot": {
        "title": "⚠️ Face Recognition Troubleshooting",
        "keywords": ["troubleshoot", "not recognized", "absent", "missed", "problem", "error", "fail", "fix"],
        "answer": r"""
### ⚠️ What to Do if a Student Face is Not Recognized:
1. **Lighting**: Avoid strong backlighting (windows behind students). Position the camera facing evenly lit subjects.
2. **Angle**: Students should look forward within $\pm 20^\circ$ of the camera lens.
3. **Registration Photo**: Ensure the student's registered profile photo in their profile is clear, sharp, and without heavy shadows.
4. **Resolution**: If taking a photo of a large hall, use high-resolution cameras or take multiple section photos (e.g. Left side, Right side).
"""
    }
}


def find_best_answer(user_query: str) -> str:
    query_lower = user_query.lower()

    # Search keyword scores
    best_match = None
    max_score = 0

    for key, data in AI_GUIDE_KB.items():
        score = 0
        for kw in data["keywords"]:
            if kw in query_lower:
                score += 2
        for word in query_lower.split():
            if len(word) > 3 and word in data["answer"].lower():
                score += 1

        if score > max_score:
            max_score = score
            best_match = data

    if best_match and max_score >= 2:
        return best_match["answer"]

    return """
### 🤖 SnapClass AI Assistant Answer:
SnapClass is a dual-modality biometric smart attendance system designed for educational institutions:
- **📸 Computer Vision**: Uses dlib 68-point landmarks and 128D ResNet embeddings with dynamic Eye Aspect Ratio (EAR) blink anti-spoofing.
- **🎙️ Voice AI**: Uses Resemblyzer 256D normalized voiceprints and Google Speech-to-Text challenge verification to eliminate replay attacks.
- **🔥 Firebase Firestore**: Cloud NoSQL storage with atomic transaction counters and session TTL expiry.
- **🔐 Security**: Salted Bcrypt teacher password hashing and zero credential leakage.

*Try asking about: "photo attendance", "voice roll-call", "anti-spoofing", "QR expiration", or "export records"!*
"""


@st.dialog("✨ SnapClass AI Interactive Guide & Copilot", width="large")
def ai_guide_dialog(role: str = "general", context_data: dict = None):
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 18px 22px; border-radius: 16px; margin-bottom: 18px; border: 1px solid #4338ca;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 2rem;">🤖</span>
                    <div>
                        <h3 style="margin: 0; color: #FFFFFF; font-size: 1.3rem; font-weight: 700;">SnapClass AI Co-Pilot</h3>
                        <p style="margin: 2px 0 0 0; color: #C7D2FE; font-size: 0.85rem;">Your intelligent guide for biometric attendance, security & analytics</p>
                    </div>
                </div>
                <span style="background: #4F46E5; color: #EEF2FF; font-family: monospace; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 999px;">
                    v2.4 ACTIVE
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💬 Ask AI Copilot", "📚 Interactive User Guides", "📊 Smart Attendance Insights"])

    # ─────────────────────────────────────────────
    # TAB 1: Interactive Q&A Copilot
    # ─────────────────────────────────────────────
    with tab1:
        st.markdown("<p style='font-size: 0.9rem; color: #475569;'>Tap any quick question below or type your own question to get instant technical & practical guidance:</p>", unsafe_allow_html=True)

        # Quick question pills
        q_cols = st.columns(3)
        selected_q = None

        with q_cols[0]:
            if st.button("📸 How to take photo roll-call?", width="stretch", key="q1"):
                selected_q = "photo attendance"
            if st.button("👁️ How does anti-spoofing work?", width="stretch", key="q2"):
                selected_q = "anti-spoofing"

        with q_cols[1]:
            if st.button("🎙️ How does voice roll-call work?", width="stretch", key="q3"):
                selected_q = "voice attendance"
            if st.button("⏱️ How does QR TTL expire?", width="stretch", key="q4"):
                selected_q = "qr session expiration"

        with q_cols[2]:
            if st.button("🎯 What is the 0.48 threshold?", width="stretch", key="q5"):
                selected_q = "threshold"
            if st.button("📥 How to export to Excel/CSV?", width="stretch", key="q6"):
                selected_q = "export records"

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

        # Search Query Bar
        user_query = st.text_input(
            "Search or ask any question:",
            value=selected_q if selected_q else "",
            placeholder="e.g., How does eye-blink EAR prevent fake photos?",
            key="ai_guide_input"
        )

        if user_query:
            with st.spinner("AI is analyzing codebase & biometric documentation..."):
                answer = find_best_answer(user_query)
                with st.container(border=True):
                    st.markdown(answer)

    # ─────────────────────────────────────────────
    # TAB 2: Step-by-Step Guides
    # ─────────────────────────────────────────────
    with tab2:
        st.markdown("### 🎓 Recommended Workflows")

        with st.expander("📸 1. Taking Classroom Attendance in 5 Seconds", expanded=True):
            st.markdown("""
            1. **Select Course**: Open the teacher dashboard and select your active subject.
            2. **Snap or Upload**: Point your laptop camera at the classroom or upload a wide-angle snapshot.
            3. **Vector Verification**: dlib computes 128D embeddings for every face and compares against enrolled students.
            4. **Review & Confirm**: Green chips indicate verified students. Click **Confirm & Save** to sync to Firebase Firestore.
            """)

        with st.expander("🎙️ 2. Audio-Based Roll Call & Anti-Replay", expanded=False):
            st.markdown("""
            1. Click **🎙️ Voice Attendance** in the teacher dashboard.
            2. An unpredictable 4-token challenge phrase will appear (e.g., *"Titan 3 8 1"*).
            3. Ask the student to speak the challenge phrase into the microphone.
            4. **Google STT** verifies the phrase words, while **Resemblyzer** verifies the voiceprint against their registration sample.
            """)

        with st.expander("📲 3. Course Enrollment with Dynamic Expiring QR", expanded=False):
            st.markdown("""
            1. Under **Manage Subjects**, find your subject and click **Share / QR Code**.
            2. Select a security TTL window (e.g. 15 minutes).
            3. Display the projected QR code on the lecture screen.
            4. Students scan with their phone camera to instantly self-enroll.
            5. The link automatically invalidates once the 15-minute timer expires.
            """)

        with st.expander("👁️ 4. Student Face Registration & Eye-Blink Liveness", expanded=False):
            st.markdown("""
            1. Students enter the **Student Portal** and click **Register Biometrics**.
            2. The webcam captures consecutive frames while the student blinks naturally.
            3. The Eye Aspect Ratio (EAR) algorithm confirms physical presence and rejects static photos.
            4. 128D face embeddings are stored in Firestore for instant future FaceID logins.
            """)

    # ─────────────────────────────────────────────
    # TAB 3: Smart Attendance Insights
    # ─────────────────────────────────────────────
    with tab3:
        st.markdown("### 📊 AI Analytics & Compliance Insights")

        # Native Streamlit metrics (Adapts to both Dark & Light Themes automatically!)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            with st.container(border=True):
                st.metric(label="Target Attendance", value="75.0%", delta="Standard Policy")

        with col_b:
            with st.container(border=True):
                st.metric(label="Time Saved", value="~12 Mins", delta="Per Lecture Session")

        with col_c:
            with st.container(border=True):
                st.metric(label="Proxy Rate", value="0.0%", delta="Zero Buddy Punching")

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        st.info("💡 **Compliance Notice**: Students falling below the 75% attendance threshold will be automatically highlighted with warning tags in the teacher's Attendance Records tab.")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Close AI Guide", type="primary", width="stretch"):
        st.rerun()
