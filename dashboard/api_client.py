# dashboard/api_client.py

import requests
import streamlit as st
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

def _get(endpoint: str, params: dict = None):
    """Make GET request to FastAPI."""
    try:
        response = requests.get(
            f"{API_BASE}{endpoint}",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            return data.get('data')
        else:
            st.error(f"API error: {data.get('error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Is FastAPI running on port 8000?")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Each function cached for 5 minutes
@st.cache_data(ttl=300)
def fetch_summary():
    return _get("/kpis/summary")

@st.cache_data(ttl=300)
def fetch_channels():
    return _get("/kpis/channels") or []

@st.cache_data(ttl=300)
def fetch_campaigns(channel=None, status=None, min_roi=None):
    params = {}
    if channel: params['channel'] = channel
    if status:  params['status']  = status
    if min_roi: params['min_roi'] = min_roi
    return _get("/kpis/campaigns", params) or []

@st.cache_data(ttl=300)
def fetch_trends(weeks=12):
    return _get("/kpis/trends", {'weeks': weeks}) or []

@st.cache_data(ttl=300)
def fetch_anomalies():
    return _get("/kpis/anomalies") or []