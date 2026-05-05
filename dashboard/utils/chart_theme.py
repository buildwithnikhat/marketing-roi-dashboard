# dashboard/utils/chart_theme.py
import plotly.graph_objects as go

# Brand colors — used consistently across ALL charts
COLORS = {
    'primary': '#7F77DD',
    'success': '#1D9E75',
    'warning': '#EF9F27',
    'danger':  '#D85A30',
    'neutral': '#888780',
}

# One color per channel — consistent across all charts
CHANNEL_COLORS = {
    'Google Search':  '#4285F4',
    'Google Display': '#34A853',
    'Meta Feed':      '#1877F2',
    'Meta Stories':   '#E1306C',
    'Email':          '#EA4335',
    'SMS':            '#FF6D00',
    'YouTube':        '#FF0000',
}

TIER_COLORS = {
    'Excellent':   '#1D9E75',
    'Good':        '#7F77DD',
    'Break-even':  '#EF9F27',
    'Loss-making': '#D85A30',
}

def apply_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply consistent theme to any Plotly chart."""
    fig.update_layout(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="sans-serif", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
        ),
        xaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)'),
    )
    return fig