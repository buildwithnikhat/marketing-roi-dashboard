# dashboard/app.py

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Page config — MUST be first ──────────────────────
st.set_page_config(
    page_title="Marketing ROI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────
st.markdown("""
<style>
[data-testid="metric-container"] {
    background: rgba(127,119,221,0.05);
    border: 1px solid rgba(127,119,221,0.2);
    border-radius: 10px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

from dashboard.components.kpi_cards     import render_kpi_cards
from dashboard.components.trend_charts  import render_trend_charts
from dashboard.components.channel_charts import render_channel_charts
from dashboard.components.campaign_table import render_campaign_table
from dashboard.api_client import (
    fetch_summary, fetch_channels,
    fetch_campaigns, fetch_trends, fetch_anomalies
)

# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════

with st.sidebar:
    st.title("📊 Filters")
    st.divider()

    channels = [
        "All", "Google Search", "Google Display",
        "Meta Feed", "Meta Stories",
        "Email", "SMS", "YouTube"
    ]
    sel_channel = st.selectbox("📡 Channel", channels)
    channel_param = None if sel_channel == "All" else sel_channel

    statuses = ["All", "Active", "Paused", "Completed"]
    sel_status = st.selectbox("🔄 Status", statuses)
    status_param = None if sel_status == "All" else sel_status

    min_roi = st.slider("Min ROI %", -100, 500, 0, 10)
    min_roi_param = min_roi if min_roi > 0 else None

    trend_weeks = st.slider("📅 Trend Weeks", 4, 52, 12)

    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════

st.title("📊 Marketing ROI Dashboard")
st.caption(
    "Real-time campaign performance · "
    "KPI monitoring · AI-powered insights"
)
st.divider()

# ══════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📡 Channels",
    "🗂️ Campaigns",
    "🤖 AI Insights",
])

# ── TAB 1: Overview ───────────────────────────────────
with tab1:
    with st.spinner("Loading KPIs..."):
        summary  = fetch_summary()
        trend    = fetch_trends(weeks=trend_weeks)
        anomalies = fetch_anomalies()

    render_kpi_cards(summary)
    st.divider()
    render_trend_charts(trend)

    # Anomalies
    if anomalies:
        st.divider()
        st.markdown("### 🚨 Anomalies Detected")
        import pandas as pd
        adf = pd.DataFrame(anomalies)
        st.dataframe(adf, use_container_width=True,
                     hide_index=True)
    else:
        st.success("✅ No anomalies detected.")

# ── TAB 2: Channels ───────────────────────────────────
with tab2:
    with st.spinner("Loading channel data..."):
        channels_data = fetch_channels()
    render_channel_charts(channels_data)

# ── TAB 3: Campaigns ──────────────────────────────────
with tab3:
    with st.spinner("Loading campaigns..."):
        campaigns = fetch_campaigns(
            channel=channel_param,
            status=status_param,
            min_roi=min_roi_param
        )
    if channel_param or status_param or min_roi_param:
        filters = []
        if channel_param: filters.append(f"Channel: {channel_param}")
        if status_param:  filters.append(f"Status: {status_param}")
        if min_roi_param: filters.append(f"Min ROI: {min_roi_param}%")
        st.info(f"🔍 Filters: {' · '.join(filters)}")

    render_campaign_table(campaigns)

# ── Footer ────────────────────────────────────────────
st.divider()
st.caption(
    "Built by Nikhat Shaikh · "
    "Python · FastAPI · PostgreSQL · Streamlit"
)
# ── TAB 4: AI Insights ────────────────────────────────
with tab4:
    st.markdown("### 🤖 AI Marketing Analyst")
    st.caption(
        "Ask any question about your campaigns "
        "in plain English. AI reads your real data."
    )

    # Suggested questions
    st.markdown("**💡 Try these:**")
    col1, col2, col3 = st.columns(3)
    suggestions = [
        "Which channel has the best ROI?",
        "Which campaign made the most profit?",
        "What is the cost per lead for Email?",
        "Which campaigns are loss-making?",
        "What is our best performing product?",
        "Compare Email vs SMS performance",
    ]
    for i, q in enumerate(suggestions):
        with [col1, col2, col3][i % 3]:
            if st.button(q, key=f"q_{i}",
                         use_container_width=True):
                st.session_state['ai_question'] = q

    st.divider()

    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    for msg in st.session_state['chat_history']:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if msg.get('sql'):
                with st.expander("📋 SQL used"):
                    st.code(msg['sql'], language='sql')

    # Input
    default_q = st.session_state.pop('ai_question', '')
    question  = st.chat_input(
        "Ask about your marketing data..."
    ) or default_q

    if question:
        # Show user message
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state['chat_history'].append({
            'role': 'user', 'content': question
        })

        # Get AI answer
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                import requests as req
                try:
                    resp = req.post(
                        "http://localhost:8000/api/v1/kpis/ai/query",
                        json={"question": question},
                        timeout=30
                    )
                    data = resp.json().get('data', {})
                    answer  = data.get('answer',
                                       'Could not get answer.')
                    sql_used = data.get('sql_used')
                    st.markdown(answer)
                    if sql_used:
                        with st.expander("📋 SQL used"):
                            st.code(sql_used, language='sql')
                    st.session_state['chat_history'].append({
                        'role':    'assistant',
                        'content': answer,
                        'sql':     sql_used
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state['chat_history']:
        if st.button("🗑️ Clear chat"):
            st.session_state['chat_history'] = []
            st.rerun()