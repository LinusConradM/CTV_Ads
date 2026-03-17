"""Dashboard — KPI card components."""

import streamlit as st


def kpi_row(metrics: list[dict]):
    """Display a row of KPI metric cards.

    Args:
        metrics: list of dicts with keys: label, value, delta (optional), delta_color (optional)
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            delta = m.get("delta")
            delta_color = m.get("delta_color", "normal")
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=delta,
                delta_color=delta_color,
            )


def format_number(n: float, decimals: int = 0) -> str:
    """Format large numbers with K/M suffix."""
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.{decimals}f}M"
    elif abs(n) >= 1_000:
        return f"{n/1_000:.{decimals}f}K"
    return f"{n:.{decimals}f}"


def format_pct(n: float, decimals: int = 1) -> str:
    """Format as percentage string."""
    return f"{n * 100:.{decimals}f}%"


def format_currency(n: float, decimals: int = 2) -> str:
    """Format as USD currency."""
    return f"${n:,.{decimals}f}"
