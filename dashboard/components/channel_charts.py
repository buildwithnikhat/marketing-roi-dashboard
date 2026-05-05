# dashboard/components/channel_charts.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.chart_theme import (
    apply_theme, COLORS, CHANNEL_COLORS
)
from dashboard.utils.formatters import fmt_inr, fmt_pct

def render_channel_charts(channel_data: list):
    """Channel ROI bar chart + budget donut."""
    if not channel_data:
        st.info("No channel data.")
        return

    df = pd.DataFrame(channel_data)
    df = df.sort_values('roi_pct', ascending=False)

    st.markdown("### 📡 Channel Performance")

    # ── ROI Bar Chart ─────────────────────────────────
    colors = [
        COLORS['success'] if r >= 100 else
        COLORS['warning'] if r >= 0   else
        COLORS['danger']
        for r in df['roi_pct'].fillna(0)
    ]

    fig = go.Figure(go.Bar(
        x=df['roi_pct'],
        y=df['channel'],
        orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df['roi_pct'].fillna(0)],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>"
            "ROI: %{x:.1f}%<extra></extra>"
        )
    ))

    fig.add_vline(
        x=0, line_dash="dot",
        line_color=COLORS['danger'], opacity=0.5
    )

    fig.update_layout(
        title="ROI by Channel",
        showlegend=False
    )
    apply_theme(fig, height=350)
    st.plotly_chart(fig, use_container_width=True)

    # ── Two charts side by side ───────────────────────
    c1, c2 = st.columns(2)

    # Spend share donut
    with c1:
        fig2 = go.Figure(go.Pie(
            labels=df['channel'],
            values=df['total_spend'],
            hole=0.55,
            marker_colors=[
                CHANNEL_COLORS.get(ch, COLORS['neutral'])
                for ch in df['channel']
            ],
            textinfo='label+percent',
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Spend: ₹%{value:,.0f}<br>"
                "%{percent}<extra></extra>"
            )
        ))
        fig2.update_layout(title="Budget Allocation")
        apply_theme(fig2, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    # Channel summary table
    with c2:
        st.markdown("**Channel KPI Summary**")
        display = df[[
            'channel', 'total_spend', 'total_revenue',
            'roi_pct', 'roas'
        ]].copy()
        display.columns = [
            'Channel', 'Spend', 'Revenue', 'ROI %', 'ROAS'
        ]
        display['Spend']   = display['Spend'].apply(fmt_inr)
        display['Revenue'] = display['Revenue'].apply(fmt_inr)
        display['ROI %']   = display['ROI %'].apply(fmt_pct)
        display['ROAS']    = display['ROAS'].apply(
            lambda x: f"{x:.2f}x" if x else "—"
        )
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )