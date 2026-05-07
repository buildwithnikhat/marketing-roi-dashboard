import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Marketing ROI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp { background: #0F1117 !important; }

section[data-testid="stSidebar"] {
    background: #161B27 !important;
    border-right: 1px solid #1E2A3A !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: #8892A4 !important;
}
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMetricDelta"] {
    font-size: 12px !important;
}
[data-testid="metric-container"] {
    background: #1A2035 !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 12px !important;
    padding: 20px !important;
    transition: border-color 0.2s !important;
}
[data-testid="metric-container"]:hover {
    border-color: #3B4FCC !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #161B27 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid #1E2A3A !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: #8892A4 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #3B4FCC !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: linear-gradient(135deg,#3B4FCC,#2D3A9E) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.3px !important;
    padding: 10px 18px !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stSelectbox > div > div {
    background: #1A2035 !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-size: 13px !important;
}
.stSelectbox label {
    color: #8892A4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

.stSlider label {
    color: #8892A4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
.stSlider [data-baseweb="slider"] div {
    background: #3B4FCC !important;
}

.stDataFrame {
    border: 1px solid #1E2A3A !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

.stChatInput > div {
    background: #1A2035 !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 10px !important;
}

.element-container .stMarkdown h3 {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}

hr { border-color: #1E2A3A !important; }
#MainMenu, footer, header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

from dashboard.api_client import (
    fetch_summary, fetch_channels,
    fetch_campaigns, fetch_trends, fetch_anomalies
)
from dashboard.utils.formatters import (
    fmt_inr, fmt_pct, fmt_x, fmt_num
)
from dashboard.components.trend_charts   import render_trend_charts
from dashboard.components.channel_charts import render_channel_charts
from dashboard.components.campaign_table import render_campaign_table

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:4px 0 20px'>
        <div style='font-size:18px;font-weight:700;
                    color:#FFFFFF;letter-spacing:-0.3px'>
            📊 ROI Dashboard
        </div>
        <div style='font-size:12px;color:#8892A4;
                    margin-top:4px'>by Nikhat Shaikh</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    channels     = ["All","Google Search","Google Display",
                    "Meta Feed","Meta Stories","Email","SMS","YouTube"]
    sel_channel  = st.selectbox("Channel", channels)
    channel_param = None if sel_channel=="All" else sel_channel

    statuses     = ["All","Active","Paused","Completed"]
    sel_status   = st.selectbox("Status", statuses)
    status_param = None if sel_status=="All" else sel_status

    min_roi      = st.slider("Min ROI %", -100, 500, 0, 10)
    min_roi_param = min_roi if min_roi > 0 else None

    trend_weeks  = st.slider("Trend Window", 4, 52, 12)

    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style='margin-top:16px;padding:12px;
                background:#1A2035;
                border:1px solid #1E2A3A;
                border-radius:10px'>
        <div style='font-size:10px;font-weight:600;
                    text-transform:uppercase;
                    letter-spacing:1px;
                    color:#8892A4;
                    margin-bottom:8px'>System Status</div>
        <div style='font-size:12px;color:#22C55E;
                    display:flex;align-items:center;
                    gap:6px;margin-bottom:4px'>
            <div style='width:6px;height:6px;
                        border-radius:50%;
                        background:#22C55E'></div>
            API Connected
        </div>
        <div style='font-size:12px;color:#22C55E;
                    display:flex;align-items:center;
                    gap:6px'>
            <div style='width:6px;height:6px;
                        border-radius:50%;
                        background:#22C55E'></div>
            Database Active
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════
st.markdown("""
<div style='padding:8px 0 20px'>
    <div style='font-size:28px;font-weight:700;
                color:#FFFFFF;letter-spacing:-0.5px'>
        Marketing ROI Dashboard
    </div>
    <div style='font-size:13px;color:#8892A4;margin-top:6px'>
        Real-time campaign intelligence &nbsp;·&nbsp;
        KPI monitoring &nbsp;·&nbsp;
        AI-powered insights &nbsp;·&nbsp;
        Built by <span style="color:#3B4FCC;
                              font-weight:600">
            Nikhat Shaikh</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TABS
# ══════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "  📊  Overview  ",
    "  📡  Channels  ",
    "  🗂️  Campaigns  ",
    "  🤖  AI Insights  ",
])

# ─────────────── TAB 1: OVERVIEW ──────────────────────
with tab1:
    with st.spinner(""):
        summary   = fetch_summary()
        trend     = fetch_trends(weeks=trend_weeks)
        anomalies = fetch_anomalies()

    if summary:
        # Section label
        st.markdown("""
        <div style='font-size:11px;font-weight:600;
                    text-transform:uppercase;
                    letter-spacing:1.5px;
                    color:#8892A4;
                    margin-bottom:14px'>
            Portfolio Overview
        </div>
        """, unsafe_allow_html=True)

        roi    = summary.get('roi_pct', 0) or 0
        roas   = summary.get('roas', 0) or 0
        cpl    = summary.get('cpl', 0) or 0
        convs  = summary.get('total_conversions', 0) or 0
        spend  = summary.get('total_spend', 0) or 0
        rev    = summary.get('total_revenue', 0) or 0
        profit = summary.get('gross_profit', 0) or 0
        leads  = summary.get('total_leads', 0) or 0

        # Row 1 — Primary KPIs
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.metric("🎯  Overall ROI", fmt_pct(roi),
                delta="↑ Profitable" if roi>0 else "↓ Loss",
                delta_color="normal" if roi>0 else "inverse")
        with c2:
            st.metric("📈  ROAS", fmt_x(roas),
                delta=f"{roas:.2f}x revenue/spend",
                delta_color="off")
        with c3:
            st.metric("🧲  Cost Per Lead", fmt_inr(cpl),
                delta="per lead generated",
                delta_color="off")
        with c4:
            st.metric("🛒  Conversions", fmt_num(convs),
                delta="total purchases",
                delta_color="off")

        st.markdown("<div style='height:10px'></div>",
                    unsafe_allow_html=True)

        # Row 2 — Financial KPIs
        c5,c6,c7,c8 = st.columns(4)
        with c5:
            st.metric("💰  Total Spend", fmt_inr(spend),
                delta="all campaigns", delta_color="off")
        with c6:
            st.metric("💵  Total Revenue", fmt_inr(rev),
                delta="attributed revenue", delta_color="off")
        with c7:
            st.metric("💹  Gross Profit", fmt_inr(profit),
                delta="↑ Profitable" if profit>0 else "↓ Loss",
                delta_color="normal" if profit>0 else "inverse")
        with c8:
            st.metric("🎯  Total Leads", fmt_num(leads),
                delta="leads generated", delta_color="off")

    st.divider()
    render_trend_charts(trend)

    if anomalies:
        st.divider()
        st.markdown("""
        <div style='font-size:15px;font-weight:600;
                    color:#FFFFFF;margin-bottom:12px'>
            🚨 Statistical Anomalies Detected
        </div>
        """, unsafe_allow_html=True)
        import pandas as pd
        st.dataframe(
            pd.DataFrame(anomalies),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No anomalies detected in current data.")

# ─────────────── TAB 2: CHANNELS ──────────────────────
with tab2:
    with st.spinner(""):
        channels_data = fetch_channels()
    render_channel_charts(channels_data)

# ─────────────── TAB 3: CAMPAIGNS ─────────────────────
with tab3:
    with st.spinner(""):
        campaigns = fetch_campaigns(
            channel=channel_param,
            status=status_param,
            min_roi=min_roi_param
        )

    if channel_param or status_param or min_roi_param:
        filters = []
        if channel_param:
            filters.append(f"Channel: **{channel_param}**")
        if status_param:
            filters.append(f"Status: **{status_param}**")
        if min_roi_param:
            filters.append(f"Min ROI: **{min_roi_param}%**")
        st.info(f"🔍 Active filters — {' · '.join(filters)}")

    render_campaign_table(campaigns)

# ─────────────── TAB 4: AI INSIGHTS ───────────────────
with tab4:
    st.markdown("""
    <div style='margin-bottom:20px'>
        <div style='font-size:20px;font-weight:700;
                    color:#FFFFFF;margin-bottom:6px'>
            🤖 AI Marketing Analyst
        </div>
        <div style='font-size:13px;color:#8892A4'>
            Ask any question about your campaigns
            in plain English.
            The AI reads your real PostgreSQL data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    suggestions = [
        "Which channel has the best ROI?",
        "Which campaign made the most profit?",
        "What is the cost per lead for Email?",
        "Which campaigns are loss-making?",
        "What is our best performing product?",
        "Compare Email vs SMS performance",
    ]

    st.markdown("""
    <div style='font-size:11px;font-weight:600;
                text-transform:uppercase;
                letter-spacing:1px;
                color:#8892A4;
                margin-bottom:10px'>
        💡 Suggested Questions
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for i, q in enumerate(suggestions):
        with [col1, col2, col3][i % 3]:
            if st.button(q, key=f"q_{i}",
                         use_container_width=True):
                st.session_state['ai_question'] = q

    st.divider()

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    for msg in st.session_state['chat_history']:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if msg.get('sql'):
                with st.expander("📋 View SQL query"):
                    st.code(msg['sql'], language='sql')

    default_q = st.session_state.pop('ai_question', '')
    question  = st.chat_input(
        "Ask about your marketing data..."
    ) or default_q

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state['chat_history'].append({
            'role': 'user', 'content': question
        })
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                import requests as req
                try:
                    resp = req.post(
                        "http://localhost:8000"
                        "/api/v1/kpis/ai/query",
                        json={"question": question},
                        timeout=30
                    )
                    data     = resp.json().get('data', {})
                    answer   = data.get('answer', 'No answer.')
                    sql_used = data.get('sql_used')
                    st.markdown(answer)
                    if sql_used:
                        with st.expander("📋 View SQL query"):
                            st.code(sql_used, language='sql')
                    st.session_state['chat_history'].append({
                        'role':    'assistant',
                        'content': answer,
                        'sql':     sql_used
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.get('chat_history'):
        if st.button("🗑️ Clear conversation"):
            st.session_state['chat_history'] = []
            st.rerun()

# ─────────────── FOOTER ───────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;
            color:#8892A4;
            font-size:12px;
            padding:8px 0'>
    Built by
    <span style='color:#3B4FCC;font-weight:600'>
        Nikhat Shaikh
    </span>
    &nbsp;·&nbsp;
    Python &nbsp;·&nbsp; FastAPI &nbsp;·&nbsp;
    PostgreSQL &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp;
</div>
""", unsafe_allow_html=True)