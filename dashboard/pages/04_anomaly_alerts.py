"""Page 4 — Anomaly Detection & Alerts."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_pct, format_number
from dashboard.components.charts import histogram, control_chart, bar_chart
from analytics.anomaly_detection import (
    build_anomaly_features,
    fit_isolation_forest,
    flag_anomalies,
    anomaly_summary,
    bot_traffic_indicators,
    control_chart as compute_control_chart,
)

st.header("Anomaly Detection & Alerts")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── Controls ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Anomaly Detection Controls")
contamination = st.sidebar.slider("Contamination Rate", 0.01, 0.10, 0.05, 0.01)

# ── Run Isolation Forest ─────────────────────────────────────────────────
with st.spinner("Running anomaly detection..."):
    features = build_anomaly_features(df)
    scores, model = fit_isolation_forest(features, contamination=contamination)
    df_flagged = flag_anomalies(df, scores, contamination=contamination)
    summary = anomaly_summary(df_flagged)
    df_bot = bot_traffic_indicators(df_flagged)

# ── KPIs ─────────────────────────────────────────────────────────────────
n_anomalies = df_flagged["is_anomaly"].sum()
anomaly_rate = df_flagged["is_anomaly"].mean()
bot_rate = df_bot["bot_indicator"].mean()
flagged_campaigns = df_flagged[df_flagged["is_anomaly"]]["campaign_id"].nunique()

kpi_row([
    {"label": "Anomaly Rate", "value": format_pct(anomaly_rate)},
    {"label": "Anomalies Flagged", "value": format_number(n_anomalies)},
    {"label": "Flagged Campaigns", "value": str(flagged_campaigns)},
    {"label": "Bot Traffic Rate", "value": format_pct(bot_rate)},
])

st.markdown("---")

# ── Anomaly Score Distribution ───────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig = histogram(df_flagged, "anomaly_score", title="Anomaly Score Distribution", nbins=50)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if len(summary) > 0:
        fig = bar_chart(summary, "category", "count", title="Anomaly Categories")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No anomalies categorized.")

# ── Control Charts ───────────────────────────────────────────────────────
st.subheader("Metric Control Charts")

metric = st.selectbox("Select Metric", ["clearing_price_cpm", "pixels_visible_pct", "view_duration_seconds"])
chart_data = compute_control_chart(df_flagged, metric)
if len(chart_data) > 1:
    fig = control_chart(chart_data, "report_date", "value", "ucl", "lcl", "mean_line",
                        title=f"{metric} — Daily Control Chart")
    st.plotly_chart(fig, use_container_width=True)

# ── Anomalous Records Table ──────────────────────────────────────────────
st.subheader("Flagged Anomalous Records")

anomalous = df_flagged[df_flagged["is_anomaly"]].sort_values("anomaly_score")
display_cols = [
    "impression_id", "campaign_id", "device_type", "publisher_id",
    "clearing_price_cpm", "pixels_visible_pct", "view_duration_seconds",
    "user_campaign_frequency", "anomaly_score",
]
st.dataframe(anomalous[display_cols].head(50), use_container_width=True, hide_index=True)
