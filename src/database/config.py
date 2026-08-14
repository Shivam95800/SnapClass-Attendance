import streamlit as st
import os
import re
from supabase import create_client, Client


def _get_secrets():
    """Safely read Supabase credentials from Streamlit secrets or environment."""
    url = None
    key = None

    try:
        url = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key") or st.secrets.get("SUPABASE_ANON_KEY")
    except Exception:
        pass

    if not url:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("supabase_url")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

    return url, key


def _clean_url(url: str) -> str:
    """Strip trailing slashes and any REST path that shouldn't be in the base URL."""
    if not url:
        return url
    # Remove trailing slashes
    url = url.rstrip("/")
    # Remove common mistakenly appended paths
    for suffix in ["/rest/v1", "/auth/v1", "/storage/v1", "/realtime/v1"]:
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url


_url, _key = _get_secrets()
_url = _clean_url(_url) if _url else None

_init_error = None
supabase: Client = None

if _url and _key:
    try:
        supabase = create_client(_url, _key)
    except Exception as e:
        _init_error = str(e)
else:
    _init_error = (
        f"Missing Supabase credentials. "
        f"URL={'SET' if _url else 'MISSING'}, "
        f"KEY={'SET' if _key else 'MISSING'}. "
        f"Go to Streamlit Cloud → App Settings → Secrets and add SUPABASE_URL and SUPABASE_KEY."
    )