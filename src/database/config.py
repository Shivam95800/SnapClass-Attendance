import streamlit as st
import os
import json

import firebase_admin
from firebase_admin import credentials, firestore

db = None
_init_error = None


def _find_credentials():
    """Ultra-resilient credential loader that checks all possible secret names and formats."""
    # 1. Check Streamlit Secrets
    try:
        if hasattr(st, "secrets") and st.secrets:
            # Direct key names
            candidate_keys = [
                "FIREBASE_CREDENTIALS",
                "FIREBASE_CREDENTIAL",
                "firebase_credentials",
                "firebase_credential",
                "Firebase credential",
                "Firebase credentials",
                "firebase",
                "FIREBASE",
                "credentials",
            ]
            for key in candidate_keys:
                if key in st.secrets:
                    val = st.secrets[key]
                    if isinstance(val, str):
                        try:
                            return json.loads(val.strip())
                        except Exception:
                            try:
                                return json.loads(val.replace("'", '"'))
                            except Exception:
                                pass
                    elif hasattr(val, "to_dict") or isinstance(val, dict):
                        return dict(val)

            # Check if secrets was entered as root-level TOML keys
            if "project_id" in st.secrets and ("private_key" in st.secrets or "client_email" in st.secrets):
                return dict(st.secrets)
            
            # Check any nested section in st.secrets
            for sec_key in st.secrets.keys():
                sec_val = st.secrets[sec_key]
                if (hasattr(sec_val, "to_dict") or isinstance(sec_val, dict)) and "project_id" in sec_val:
                    return dict(sec_val)
    except Exception as e:
        print("Secrets parse notice:", e)

    # 2. Check Environment Variables
    for env_key in ["FIREBASE_CREDENTIALS", "FIREBASE_CREDENTIAL", "GOOGLE_APPLICATION_CREDENTIALS_JSON"]:
        env_raw = os.environ.get(env_key)
        if env_raw:
            try:
                return json.loads(env_raw.strip())
            except Exception:
                pass

    # 3. Check Local JSON Files
    local_paths = [
        ".streamlit/firebase-credentials.json",
        "firebase-credentials.json",
        ".streamlit/serviceAccountKey.json",
        "serviceAccountKey.json",
    ]
    for path in local_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    return None


def get_db():
    """Lazy initialize and return the Firestore client."""
    global db, _init_error

    if db is not None:
        return db

    if firebase_admin._apps:
        try:
            db = firestore.client()
            return db
        except Exception:
            pass

    try:
        cred_data = _find_credentials()

        if cred_data and isinstance(cred_data, dict) and "project_id" in cred_data:
            # Fix escaped newlines in private key if stringified
            if "private_key" in cred_data and isinstance(cred_data["private_key"], str):
                cred_data["private_key"] = cred_data["private_key"].replace("\\n", "\n")

            cred = credentials.Certificate(cred_data)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            _init_error = None
            return db
        else:
            _init_error = (
                "FIREBASE_CREDENTIALS not found in Streamlit Secrets. "
                "Please add FIREBASE_CREDENTIALS = '''{...}''' in App Settings → Secrets."
            )

    except Exception as e:
        _init_error = f"Firebase initialization error: {str(e)}"
        print("Firebase init error:", e)

    return None


# Initialize on import
get_db()