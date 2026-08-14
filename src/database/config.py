import streamlit as st
import os
import json

import firebase_admin
from firebase_admin import credentials, firestore

db = None
_init_error = None


def _initialize_firebase():
    global db, _init_error

    # Already initialized
    if firebase_admin._apps:
        db = firestore.client()
        return

    try:
        cred_data = None

        # 1) Streamlit secrets (production / Streamlit Cloud)
        try:
            raw = st.secrets.get("FIREBASE_CREDENTIALS")
            if raw:
                cred_data = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception:
            pass

        # 2) Environment variable (CI / Docker)
        if not cred_data:
            env_raw = os.environ.get("FIREBASE_CREDENTIALS")
            if env_raw:
                cred_data = json.loads(env_raw)

        # 3) Local JSON file for development
        if not cred_data:
            local_paths = [
                ".streamlit/firebase-credentials.json",
                "firebase-credentials.json",
            ]
            for path in local_paths:
                if os.path.exists(path):
                    with open(path) as f:
                        cred_data = json.load(f)
                    break

        if cred_data:
            cred = credentials.Certificate(cred_data)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        else:
            _init_error = (
                "FIREBASE_CREDENTIALS not found. "
                "For Streamlit Cloud: add it in App Settings → Secrets as a JSON string. "
                "For local dev: place firebase-credentials.json in .streamlit/."
            )

    except Exception as e:
        _init_error = str(e)
        print("Firebase init error:", e)


_initialize_firebase()