# dashboard/components/trend_charts.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.chart_theme import apply_theme, COLORS

def render_trend_charts(trend_data: list):
    """Modern gradient trend charts."""
    if not trend_data:
        st.info("No trend data available.")
        return

    df = pd.DataFrame(trend_data)
    df['week_start'] = pd.to_datetime(df['week_start'])

    st.markdown("""
    <div style="font-family:'Inter',sans-serif;font-size:22px;
                font-weight:700;color:#FFFFFF;margin:24px 0 16px;">
        📈 Performance Trends
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # ── ROI Trend with gradient fill ──────────────────
    with col_left:
        fig = go.Figure()

        # Gradient fill under line
        fig.add_trace(go.Scatter(
            x=df['week_start'],
            y=df['roi_pct'],
            fill='tozeroy',
            fillcolor='rgba(99,91,255,0.15)',
            line=dict(color='#635BFF', width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Main ROI line
        fig.add_trace(go.Scatter(
            x=df['week_start'],
            y=df['roi_pct'],
            mode='lines+markers',
            name='Weekly ROI %',
            line=dict(
                color='#635BFF',
                width=3,
                shape='spline'   # Smooth curve!
            ),
            marker=dict(
                size=8,
                color='#635BFF',
                line=dict(color='#FFFFFF', width=2)
            ),
            hovertemplate=(
                "<b>%{x|%b %d}</b><br>"
                "ROI: <b>%{y:.1f}%</b><extra></extra>"
            )
        ))

        # Rolling average
        if len(df) >= 4:
            df['roi_ma'] = df['roi_pct'].rolling(4).mean()
            fig.add_trace(go.Scatter(
                x=df['week_start'],
                y=df['roi_ma'],
                mode='lines',
                name='4-week avg',
                line=dict(
                    color='#00C7E6',
                    width=2,
                    dash='dot'
                ),
                hovertemplate="Avg: %{y:.1f}%<extra></extra>"
            ))

        fig.add_hline(
            y=0, line_dash="dot",
            line_color='rgba(255,77,79,0.5)',
            line_width=1
        )

        fig.update_layout(
            title=dict(
                text="📊 Weekly ROI Trend",
                font=dict(size=16, color='#FFFFFF',
                          family='Inter')
            )
        )
        apply_theme(fig, height=380)
        st.plotly_chart(fig, use_container_width=True)

    # ── Spend vs Revenue Gradient Bars ────────────────
    with col_right:
        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=df['week_start'],
            y=df['weekly_spend'],
            name='Spend',
            marker=dict(
                color='#FF9F43',
                opacity=0.9,
                line=dict(width=0)
            ),
            hovertemplate="Spend: ₹%{y:,.0f}<extra></extra>"
        ))

        fig2.add_trace(go.Bar(
            x=df['week_start'],
            y=df['weekly_revenue'],
            name='Revenue',
            marker=dict(
                color='#00D924',
                opacity=0.9,
                line=dict(width=0)
            ),
            hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>"
        ))

        fig2.update_layout(
            title=dict(
                text="💰 Spend vs Revenue",
                font=dict(size=16, color='#FFFFFF',
                          family='Inter')
            ),
            barmode='group',
            bargap=0.3,
            bargroupgap=0.05
        )
        apply_theme(fig2, height=380)
        st.plotly_chart(fig2, use_container_width=True)