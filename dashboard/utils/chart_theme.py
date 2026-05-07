# dashboard/utils/chart_theme.py

import plotly.graph_objects as go

# ── Stripe-inspired color palette ────────────────────
COLORS = {
    'primary':   '#635BFF',   # Stripe purple
    'secondary': '#0A2540',   # Deep navy
    'success':   '#00D924',   # Bright green
    'warning':   '#FF9F43',   # Warm orange
    'danger':    '#FF4D4F',   # Red
    'info':      '#00C7E6',   # Cyan
    'pink':      '#FF6B9D',   # Pink accent
    'neutral':   '#8792A2',   # Gray
    'white':     '#FFFFFF',
}

# Gradient pairs for each channel
CHANNEL_COLORS = {
    'Google Search':  '#4285F4',
    'Google Display': '#34A853',
    'Meta Feed':      '#1877F2',
    'Meta Stories':   '#E1306C',
    'Email':          '#635BFF',
    'SMS':            '#FF9F43',
    'YouTube':        '#FF0000',
}

TIER_COLORS = {
    'Excellent':   '#00D924',
    'Good':        '#635BFF',
    'Break-even':  '#FF9F43',
    'Loss-making': '#FF4D4F',
}

# Gradient colorscale for charts
GRADIENT_SCALE = [
    [0.0,  '#635BFF'],
    [0.25, '#00C7E6'],
    [0.5,  '#00D924'],
    [0.75, '#FF9F43'],
    [1.0,  '#FF6B9D'],
]

def apply_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Apply modern Stripe-style theme."""
    fig.update_layout(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="'Inter', 'Segoe UI', sans-serif",
            size=12,
            color='#FFFFFF'
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(color='#FFFFFF', size=11)
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#8792A2'),
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#8792A2'),
            showgrid=True,
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor='#0A2540',
            bordercolor='#635BFF',
            font=dict(color='#FFFFFF', size=12)
        ),
    )
    return fig