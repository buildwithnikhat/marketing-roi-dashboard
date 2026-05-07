# dashboard/components/channel_charts.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.chart_theme import (
    apply_theme, COLORS, CHANNEL_COLORS
)
from dashboard.utils.formatters import fmt_inr, fmt_pct

def render_channel_charts(channel_data: list):
    """Modern channel comparison with gradient bars."""
    if not channel_data:
        st.info("No channel data.")
        return

    df = pd.DataFrame(channel_data)
    df = df.sort_values('roi_pct', ascending=True)

    st.markdown("""
    <div style="font-family:'Inter',sans-serif;font-size:22px;
                font-weight:700;color:#FFFFFF;margin:24px 0 16px;">
        📡 Channel Performance
    </div>
    """, unsafe_allow_html=True)

    # ── Horizontal gradient bar chart ─────────────────
    colors = [
        CHANNEL_COLORS.get(ch, '#635BFF')
        for ch in df['channel']
    ]

    fig = go.Figure(go.Bar(
        x=df['roi_pct'],
        y=df['channel'],
        orientation='h',
        marker=dict(
            color=colors,
            opacity=0.9,
            line=dict(width=0)
        ),
        text=[f"  {v:.1f}%" for v in df['roi_pct'].fillna(0)],
        textposition='outside',
        textfont=dict(color='#FFFFFF', size=13, family='Inter'),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "ROI: %{x:.1f}%<extra></extra>"
        )
    ))

    fig.add_vline(
        x=0, line_dash="dot",
        line_color='rgba(255,77,79,0.6)',
        line_width=1.5
    )

    fig.update_layout(
        title=dict(
            text="🏆 ROI by Channel — Best to Worst",
            font=dict(size=16, color='#FFFFFF', family='Inter')
        ),
        showlegend=False,
        xaxis_title="ROI %",
    )
    apply_theme(fig, height=380)
    st.plotly_chart(fig, use_container_width=True)

    # ── Bottom row: Donut + Table ─────────────────────
    c1, c2 = st.columns(2)

    with c1:
        df_sorted = df.sort_values('total_spend', ascending=False)
        fig2 = go.Figure(go.Pie(
            labels=df_sorted['channel'],
            values=df_sorted['total_spend'],
            hole=0.6,
            marker=dict(
                colors=[
                    CHANNEL_COLORS.get(ch, '#635BFF')
                    for ch in df_sorted['channel']
                ],
                line=dict(color='#0A2540', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(color='#FFFFFF', size=11),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Spend: ₹%{value:,.0f}<br>"
                "%{percent}<extra></extra>"
            )
        ))

        fig2.update_layout(
            title=dict(
                text="💰 Budget Allocation",
                font=dict(size=16, color='#FFFFFF',
                          family='Inter')
            ),
            annotations=[dict(
                text='Spend<br>Share',
                x=0.5, y=0.5,
                font=dict(size=14, color='#FFFFFF',
                          family='Inter'),
                showarrow=False
            )]
        )
        apply_theme(fig2, height=380)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("""
        <div style="font-family:'Inter',sans-serif;
                    font-size:15px;font-weight:600;
                    color:#FFFFFF;margin-bottom:12px;">
            📋 Channel Summary
        </div>
        """, unsafe_allow_html=True)

        df_table = df.sort_values(
            'roi_pct', ascending=False
        )[[
            'channel', 'total_spend',
            'total_revenue', 'roi_pct', 'roas'
        ]].copy()

        df_table.columns = [
            'Channel', 'Spend', 'Revenue', 'ROI %', 'ROAS'
        ]
        df_table['Spend']   = df_table['Spend'].apply(fmt_inr)
        df_table['Revenue'] = df_table['Revenue'].apply(fmt_inr)
        df_table['ROI %']   = df_table['ROI %'].apply(fmt_pct)
        df_table['ROAS']    = df_table['ROAS'].apply(
            lambda x: f"{x:.2f}x" if x else "—"
        )

        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            height=320
        )