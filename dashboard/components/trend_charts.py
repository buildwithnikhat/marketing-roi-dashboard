# dashboard/components/trend_charts.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.chart_theme import apply_theme, COLORS

def render_trend_charts(trend_data: list):
    """ROI trend line + Spend vs Revenue bar chart."""
    if not trend_data:
        st.info("No trend data available.")
        return

    df = pd.DataFrame(trend_data)
    df['week_start'] = pd.to_datetime(df['week_start'])

    st.markdown("### 📈 Performance Trends")
    col_left, col_right = st.columns(2)

    # ── LEFT: ROI Trend ───────────────────────────────
    with col_left:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['week_start'],
            y=df['roi_pct'],
            mode='lines+markers',
            name='Weekly ROI %',
            line=dict(color=COLORS['primary'], width=2.5),
            marker=dict(size=6),
            hovertemplate=(
                "<b>Week of %{x|%b %d}</b><br>"
                "ROI: %{y:.1f}%<extra></extra>"
            )
        ))

        # Rolling 4-week average
        if len(df) >= 4:
            df['roi_ma'] = df['roi_pct'].rolling(4).mean()
            fig.add_trace(go.Scatter(
                x=df['week_start'],
                y=df['roi_ma'],
                mode='lines',
                name='4-week avg',
                line=dict(
                    color=COLORS['success'],
                    width=1.5,
                    dash='dash'
                )
            ))

        # Zero line
        fig.add_hline(
            y=0,
            line_dash="dot",
            line_color=COLORS['danger'],
            opacity=0.5
        )

        fig.update_layout(title="Weekly ROI Trend %")
        apply_theme(fig, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # ── RIGHT: Spend vs Revenue ───────────────────────
    with col_right:
        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=df['week_start'],
            y=df['weekly_spend'],
            name='Spend',
            marker_color=COLORS['warning'],
            hovertemplate="Spend: ₹%{y:,.0f}<extra></extra>"
        ))

        fig2.add_trace(go.Bar(
            x=df['week_start'],
            y=df['weekly_revenue'],
            name='Revenue',
            marker_color=COLORS['success'],
            hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>"
        ))

        fig2.update_layout(
            title="Weekly Spend vs Revenue",
            barmode='group'
        )
        apply_theme(fig2, height=350)
        st.plotly_chart(fig2, use_container_width=True)