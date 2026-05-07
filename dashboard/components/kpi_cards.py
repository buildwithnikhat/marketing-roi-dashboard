# dashboard/components/kpi_cards.py

import streamlit as st
from dashboard.utils.formatters import fmt_inr, fmt_pct, fmt_x, fmt_num

def render_kpi_cards(summary: dict):
    if not summary:
        st.warning("No data available.")
        return

    st.markdown("""
    <style>
    [data-testid="metric-container"] {
        background: linear-gradient(135deg,
            rgba(99,91,255,0.12) 0%,
            rgba(0,199,230,0.05) 100%) !important;
        border: 1px solid rgba(99,91,255,0.35) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #635BFF, #00C7E6);
        border-radius: 16px 16px 0 0;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #8792A2 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 12px !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    roi    = summary.get('roi_pct', 0) or 0
    roas   = summary.get('roas', 0) or 0
    cpl    = summary.get('cpl', 0) or 0
    convs  = summary.get('total_conversions', 0) or 0
    spend  = summary.get('total_spend', 0) or 0
    rev    = summary.get('total_revenue', 0) or 0
    profit = summary.get('gross_profit', 0) or 0
    leads  = summary.get('total_leads', 0) or 0

    st.markdown("""
    <div style="font-family:'Inter',sans-serif;
                font-size:13px;font-weight:600;
                color:#8792A2;text-transform:uppercase;
                letter-spacing:1.5px;margin-bottom:16px;">
        📊 Portfolio Overview
    </div>
    """, unsafe_allow_html=True)

    # Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "🎯 Overall ROI",
            fmt_pct(roi),
            delta="Profitable ↑" if roi > 0 else "Loss ↓",
            delta_color="normal" if roi > 0 else "inverse"
        )
    with c2:
        st.metric(
            "📈 ROAS",
            fmt_x(roas),
            delta=f"{roas:.1f}x return" if roas else None
        )
    with c3:
        st.metric(
            "🧲 Cost Per Lead",
            fmt_inr(cpl),
            delta="Per lead generated",
            delta_color="off"
        )
    with c4:
        st.metric(
            "🛒 Conversions",
            fmt_num(convs),
            delta="Total purchases",
            delta_color="off"
        )

    st.markdown("<div style='height:12px'></div>",
                unsafe_allow_html=True)

    # Row 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric(
            "💰 Total Spend",
            fmt_inr(spend),
            delta="All campaigns",
            delta_color="off"
        )
    with c6:
        st.metric(
            "💵 Total Revenue",
            fmt_inr(rev),
            delta="Attributed revenue",
            delta_color="off"
        )
    with c7:
        st.metric(
            "💹 Gross Profit",
            fmt_inr(profit),
            delta="Profitable ↑" if profit > 0 else "Loss ↓",
            delta_color="normal" if profit > 0 else "inverse"
        )
    with c8:
        st.metric(
            "🎯 Total Leads",
            fmt_num(leads),
            delta="Leads generated",
            delta_color="off"
        )