# dashboard/components/campaign_table.py

import streamlit as st
import pandas as pd
from dashboard.utils.formatters import (
    fmt_inr, fmt_pct, fmt_num
)
from dashboard.utils.chart_theme import TIER_COLORS

def render_campaign_table(campaigns: list):
    """Interactive campaign KPI table."""
    if not campaigns:
        st.info("No campaigns match filters.")
        return

    st.markdown("### 🗂️ Campaign Details")
    df = pd.DataFrame(campaigns)

    # Tier filter
    tiers = ['All'] + sorted(
        df['performance_tier'].dropna().unique().tolist()
    )
    selected = st.selectbox(
        "Filter by Tier", tiers, key="tier_filter"
    )
    if selected != 'All':
        df = df[df['performance_tier'] == selected]

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Campaigns",    len(df))
    m2.metric("Total Spend",  fmt_inr(df['total_spend'].sum()))
    m3.metric("Total Revenue",fmt_inr(df['total_revenue'].sum()))
    avg_roi = df['roi_pct'].mean()
    m4.metric("Avg ROI",      fmt_pct(avg_roi))

    # Display table
    display = df[[
        'campaign_name', 'channel', 'status',
        'total_spend', 'total_revenue',
        'roi_pct', 'roas', 'total_conversions',
        'performance_tier'
    ]].copy()

    display.columns = [
        'Campaign', 'Channel', 'Status',
        'Spend', 'Revenue',
        'ROI %', 'ROAS', 'Conversions', 'Tier'
    ]

    display['Spend']       = display['Spend'].apply(fmt_inr)
    display['Revenue']     = display['Revenue'].apply(fmt_inr)
    display['ROI %']       = display['ROI %'].apply(fmt_pct)
    display['ROAS']        = display['ROAS'].apply(
        lambda x: f"{x:.2f}x" if x else "—"
    )
    display['Conversions'] = display['Conversions'].apply(fmt_num)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    # Export
    csv = display.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Export CSV",
        csv,
        "campaigns.csv",
        "text/csv"
    )