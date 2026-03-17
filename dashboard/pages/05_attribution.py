"""Page 5 — Attribution Modeling."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_number
from dashboard.components.charts import bar_chart, PALETTE
from analytics.attribution import (
    build_conversion_paths,
    attribution_comparison,
)

st.header("Attribution Modeling")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── Controls ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Attribution Controls")
half_life = st.sidebar.slider("Time Decay Half-Life (days)", 1, 30, 7)
models_to_show = st.sidebar.multiselect(
    "Models to Compare",
    ["last_touch", "first_touch", "linear", "time_decay"],
    default=["last_touch", "first_touch", "linear", "time_decay"],
)

# ── Compute Attribution ──────────────────────────────────────────────────
with st.spinner("Computing attribution models..."):
    paths = build_conversion_paths(df)
    comparison = attribution_comparison(df, half_life_days=half_life)

if len(comparison) == 0:
    st.warning("No conversion paths found in filtered data.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────
total_conversions = len(paths)
total_spend = comparison["total_spend"].sum() if "total_spend" in comparison.columns else 0

kpi_row([
    {"label": "Total Conversions", "value": format_number(total_conversions)},
    {"label": "Avg Path Length", "value": f"{paths['path_length'].mean():.1f}"},
    {"label": "Campaigns Credited", "value": str(len(comparison))},
    {"label": "Total Spend", "value": f"${total_spend:,.0f}"},
])

st.markdown("---")

# ── Side-by-Side Model Comparison ────────────────────────────────────────
st.subheader("Credit Allocation by Model")

# Melt for grouped bar chart
models = [m for m in models_to_show if m in comparison.columns]
melted = comparison.melt(
    id_vars=["campaign_id"],
    value_vars=models,
    var_name="model",
    value_name="credit",
)

fig = px.bar(
    melted.sort_values("credit", ascending=False),
    x="campaign_id", y="credit", color="model",
    barmode="group", title="Conversion Credit by Campaign & Model",
    color_discrete_sequence=PALETTE,
)
fig.update_layout(template="plotly_white", height=500)
st.plotly_chart(fig, use_container_width=True)

# ── Attribution Divergence ───────────────────────────────────────────────
st.subheader("Attribution Divergence: Last-Touch vs. Linear")

if "last_touch" in comparison.columns and "linear" in comparison.columns:
    comparison["divergence"] = (
        (comparison["last_touch"] - comparison["linear"]) / comparison["linear"].replace(0, 1) * 100
    ).round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig = bar_chart(
            comparison.sort_values("divergence"),
            "campaign_id", "divergence",
            title="Credit Divergence (Last-Touch vs Linear, %)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Show which campaigns are under/over credited by last-touch
        over = comparison[comparison["divergence"] > 10]
        under = comparison[comparison["divergence"] < -10]
        st.markdown(f"**Over-credited by last-touch:** {len(over)} campaigns")
        st.markdown(f"**Under-credited by last-touch:** {len(under)} campaigns")
        st.markdown("---")
        st.markdown(
            "Last-touch attribution systematically over-credits final touchpoints "
            "(typically search/direct) and under-credits mid-funnel CTV exposures."
        )

# ── Comparison Table ─────────────────────────────────────────────────────
st.subheader("Full Attribution Comparison")
st.dataframe(comparison, use_container_width=True, hide_index=True)
