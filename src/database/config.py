import streamlit as st
import os
from supabase import create_client, Client

try:
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", "https://placeholder.supabase.co"))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", "placeholder_key"))
    supabase: Client = create_client(url, key)
except Exception:
    try:
        supabase: Client = create_client("https://placeholder.supabase.co", "placeholder_key")
    except Exception:
        supabase = None