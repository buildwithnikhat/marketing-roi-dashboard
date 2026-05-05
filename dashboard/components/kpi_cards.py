# dashboard/components/kpi_cards.py

import streamlit as st
from dashboard.utils.formatters import (
    fmt_inr, fmt_pct, fmt_x, fmt_num
)

def render_kpi_cards(summary: dict):
    """Renders the top KPI header cards."""
    if not summary:
        st.warning("No data available.")
        return

    st.markdown("### 📊 Portfolio Overview")

    # Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="🎯 Overall ROI",
            value=fmt_pct(summary.get('roi_pct')),
            help="(Revenue - Spend) / Spend × 100"
        )
    with c2:
        st.metric(
            label="📈 ROAS",
            value=fmt_x(summary.get('roas')),
            help="Revenue per ₹1 spent"
        )
    with c3:
        st.metric(
            label="🧲 Cost Per Lead",
            value=fmt_inr(summary.get('cpl')),
            help="Spend / Total Leads"
        )
    with c4:
        st.metric(
            label="🛒 Conversions",
            value=fmt_num(summary.get('total_conversions')),
            help="Total purchases"
        )

    # Row 2
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric(
            label="💰 Total Spend",
            value=fmt_inr(summary.get('total_spend'))
        )
    with c6:
        st.metric(
            label="💵 Total Revenue",
            value=fmt_inr(summary.get('total_revenue'))
        )
    with c7:
        profit = (summary.get('gross_profit') or 0)
        st.metric(
            label="💹 Gross Profit",
            value=fmt_inr(profit),
            delta="Profitable" if profit > 0 else "Loss",
            delta_color="normal" if profit > 0 else "inverse"
        )
    with c8:
        st.metric(
            label="🎯 Total Leads",
            value=fmt_num(summary.get('total_leads'))
        )