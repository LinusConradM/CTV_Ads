"""Page 7 — Frequency & Reach Curves."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_number
from dashboard.components.charts import line_chart, bar_chart
from analytics.frequency_reach import (
    reach_curve,
    frequency_distribution,
    optimal_frequency,
    diminishing_returns,
    frequency_cap_recommendation,
)

st.header("Frequency & Reach Analysis")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── Controls ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Frequency & Reach Controls")
campaigns = ["All"] + sorted(df["campaign_id"].unique())
selected_campaign = st.sidebar.selectbox("Campaign", campaigns)
campaign_id = None if selected_campaign == "All" else selected_campaign

# ── Compute Metrics ──────────────────────────────────────────────────────
campaign_df = df if campaign_id is None else df[df["campaign_id"] == campaign_id]
user_freq = campaign_df.groupby("user_id_hashed").size()

# ── KPIs ─────────────────────────────────────────────────────────────────
rec_conv = frequency_cap_recommendation(campaign_df, objective="conversions")
rec_reach = frequency_cap_recommendation(campaign_df, objective="reach")

kpi_row([
    {"label": "Total Reach", "value": format_number(user_freq.nunique())},
    {"label": "Avg Frequency", "value": f"{user_freq.mean():.1f}"},
    {"label": "Median Frequency", "value": f"{user_freq.median():.0f}"},
    {"label": "Max Frequency", "value": str(user_freq.max())},
    {"label": "Recommended Cap (Conv)", "value": str(rec_conv.get("recommended_cap", "N/A"))},
])

st.markdown("---")

# ── Reach Curve ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Reach Curve")
    rc = reach_curve(campaign_df, campaign_id=campaign_id)
    if len(rc) > 0:
        fig = line_chart(rc, "impressions_served", "unique_reach",
                         title="Unique Reach vs. Impressions Served")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Frequency Distribution")
    fd = frequency_distribution(campaign_df, campaign_id=campaign_id)
    fig = bar_chart(fd, "frequency_bucket", "user_count",
                    title="Users by Impression Frequency")
    st.plotly_chart(fig, use_container_width=True)

# ── Optimal Frequency ────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Conversion Rate by Frequency")
    opt = optimal_frequency(campaign_df)
    fig = bar_chart(opt, "freq_bucket", "conversion_rate",
                    title="Conversion Rate by Frequency Bucket")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Diminishing Returns")
    dr = diminishing_returns(campaign_df)
    if len(dr) > 0:
        fig = line_chart(dr, "impressions", "marginal_reach_rate",
                         title="Marginal Reach Rate (Diminishing Returns)")
        st.plotly_chart(fig, use_container_width=True)

# ── Frequency Cap Recommendations ────────────────────────────────────────
st.subheader("Frequency Cap Recommendations")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Conversions Objective**")
    st.markdown(f"- Recommended Cap: **{rec_conv.get('recommended_cap', 'N/A')}**")
    st.markdown(f"- {rec_conv.get('reason', '')}")

with col2:
    st.markdown("**Reach Objective**")
    st.markdown(f"- Recommended Cap: **{rec_reach.get('recommended_cap', 'N/A')}**")
    st.markdown(f"- {rec_reach.get('reason', '')}")
