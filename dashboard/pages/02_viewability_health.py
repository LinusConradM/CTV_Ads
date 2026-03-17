"""Page 2 — Viewability & Delivery Health."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_pct
from dashboard.components.charts import bar_chart, histogram, control_chart
from analytics.viewability import (
    campaign_viewability_report,
    device_viewability_breakdown,
    publisher_viewability_scorecard,
    viewability_trend,
    viewability_distribution,
)

st.header("Viewability & Delivery Health")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]
dist = viewability_distribution(df)

# ── KPIs ─────────────────────────────────────────────────────────────────
kpi_row([
    {"label": "Viewable Rate", "value": format_pct(dist["overall_viewable_rate"])},
    {"label": "Video Viewable", "value": format_pct(dist["video_viewable_rate"])},
    {"label": "Display Viewable", "value": format_pct(dist.get("display_viewable_rate", 0))},
    {"label": "Avg Pixel Visibility", "value": format_pct(dist["pixel_visibility"]["mean"])},
    {"label": "Avg View Duration", "value": f"{dist['view_duration']['mean']:.1f}s"},
])

st.markdown("---")

# ── Viewability by Campaign ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    report = campaign_viewability_report(df)
    fig = bar_chart(report.head(15), "campaign_id", "viewable_rate",
                    title="Viewable Rate by Campaign")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    breakdown = device_viewability_breakdown(df)
    device_avg = breakdown.groupby("device_type").agg(
        viewable_rate=("viewable_rate", "mean"),
        impressions=("impressions", "sum"),
    ).reset_index().sort_values("viewable_rate", ascending=False)
    fig = bar_chart(device_avg, "device_type", "viewable_rate",
                    title="Viewable Rate by Device Type")
    st.plotly_chart(fig, use_container_width=True)

# ── Pixel Visibility Distribution ────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig = histogram(df, "pixels_visible_pct", title="Pixel Visibility Distribution", nbins=40)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = histogram(df, "view_duration_seconds", title="View Duration Distribution", nbins=40)
    st.plotly_chart(fig, use_container_width=True)

# ── Viewability Trend with Control Limits ────────────────────────────────
st.subheader("Viewability Trend (Statistical Control Chart)")
trend = viewability_trend(df)
if len(trend) > 1:
    fig = control_chart(trend, "report_date", "viewable_rate", "ucl", "lcl", "mean_line",
                        title="Daily Viewability Rate with 3-Sigma Control Limits")
    st.plotly_chart(fig, use_container_width=True)

    out_of_control = trend[trend["out_of_control"]]
    if len(out_of_control) > 0:
        st.warning(f"{len(out_of_control)} day(s) out of control limits")

# ── Publisher Scorecard ──────────────────────────────────────────────────
st.subheader("Publisher Viewability Scorecard")
scorecard = publisher_viewability_scorecard(df)
st.dataframe(scorecard.head(20), use_container_width=True, hide_index=True)
