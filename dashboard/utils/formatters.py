# dashboard/utils/formatters.py

def fmt_inr(value) -> str:
    """Format as Indian currency — lakhs and crores."""
    if value is None:
        return "—"
    try:
        v = float(value)
        if v >= 1_00_00_000:
            return f"₹{v/1_00_00_000:.2f}Cr"
        elif v >= 1_00_000:
            return f"₹{v/1_00_000:.2f}L"
        elif v >= 1_000:
            return f"₹{v:,.0f}"
        else:
            return f"₹{v:.2f}"
    except:
        return "—"

def fmt_pct(value, decimals=1) -> str:
    """Format as percentage."""
    if value is None:
        return "—"
    try:
        return f"{float(value):.{decimals}f}%"
    except:
        return "—"

def fmt_x(value) -> str:
    """Format as multiplier e.g. 3.18x"""
    if value is None:
        return "—"
    try:
        return f"{float(value):.2f}x"
    except:
        return "—"

def fmt_num(value) -> str:
    """Format large numbers with commas."""
    if value is None:
        return "—"
    try:
        return f"{int(value):,}"
    except:
        return "—"