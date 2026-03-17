"""Page 1 — Campaign Performance Overview."""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_number, format_pct, format_currency
from dashboard.components.charts import line_chart, bar_chart, PALETTE

st.header("Campaign Performance Overview")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── KPIs ─────────────────────────────────────────────────────────────────
kpi_row([
    {"label": "Total Impressions", "value": format_number(len(df))},
    {"label": "Unique Reach", "value": format_number(df["user_id_hashed"].nunique())},
    {"label": "Avg Frequency", "value": f"{len(df) / max(df['user_id_hashed'].nunique(), 1):.1f}"},
    {"label": "Avg CPM", "value": format_currency(df["clearing_price_cpm"].mean())},
    {"label": "Viewable Rate", "value": format_pct(df["is_viewable"].mean())},
    {"label": "Completion Rate", "value": format_pct((df["view_completion_pct"] >= 0.95).mean())},
])

st.markdown("---")

# ── CPM Trend Over Time ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    daily_cpm = df.groupby("report_date").agg(
        avg_cpm=("clearing_price_cpm", "mean"),
        impressions=("impression_id", "count"),
    ).reset_index()
    fig = line_chart(daily_cpm, "report_date", "avg_cpm", title="Average CPM Over Time")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # eCPM by Device Type
    device_cpm = df.groupby("device_type").agg(
        avg_cpm=("clearing_price_cpm", "mean"),
        impressions=("impression_id", "count"),
    ).reset_index().sort_values("avg_cpm", ascending=False)
    fig = bar_chart(device_cpm, "device_type", "avg_cpm", title="Avg CPM by Device Type")
    st.plotly_chart(fig, use_container_width=True)

# ── Campaign Performance Table ───────────────────────────────────────────
st.subheader("Campaign Performance")

camp_perf = df.groupby("campaign_id").agg(
    impressions=("impression_id", "count"),
    unique_reach=("user_id_hashed", "nunique"),
    avg_cpm=("clearing_price_cpm", "mean"),
    viewable_rate=("is_viewable", "mean"),
    completion_rate=("view_completion_pct", lambda x: (x >= 0.95).mean()),
    conversion_rate=("converted", "mean"),
    total_spend=("clearing_price_cpm", lambda x: x.sum() / 1000),
).round(4).reset_index()
camp_perf["frequency"] = (camp_perf["impressions"] / camp_perf["unique_reach"]).round(1)
camp_perf = camp_perf.sort_values("impressions", ascending=False)

st.dataframe(camp_perf, use_container_width=True, hide_index=True)

# ── CTR by Creative and Content Category ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    content_perf = df.groupby("content_category").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
    ).reset_index()
    fig = bar_chart(content_perf, "content_category", "avg_cpm", title="CPM by Content Category")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Delivery by DMA
    dma_perf = df.groupby("dma_name").agg(
        impressions=("impression_id", "count"),
    ).reset_index().sort_values("impressions", ascending=False).head(10)
    fig = bar_chart(dma_perf, "dma_name", "impressions", title="Top 10 DMAs by Impressions")
    st.plotly_chart(fig, use_container_width=True)
