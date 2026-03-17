"""Page 3 — Audience Segmentation."""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_number
from dashboard.components.charts import scatter_chart, bar_chart, line_chart, PALETTE
from analytics.segmentation import (
    prepare_clustering_features,
    find_optimal_k,
    fit_segments,
    segment_profiles,
    segment_pca_projection,
    segment_value_analysis,
)

st.header("Audience Segmentation")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── Prepare features ─────────────────────────────────────────────────────
with st.spinner("Preparing user-level features..."):
    features = prepare_clustering_features(df)

st.sidebar.markdown("---")
st.sidebar.subheader("Segmentation Controls")
k = st.sidebar.slider("Number of Segments (K)", min_value=2, max_value=8, value=4)

# ── Elbow Curve ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Optimal K Selection")
    k_results = find_optimal_k(features, (2, 8))
    fig = line_chart(k_results, "k", "inertia", title="Elbow Curve (Inertia)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = line_chart(k_results, "k", "silhouette_score", title="Silhouette Score by K")
    st.plotly_chart(fig, use_container_width=True)

# ── Fit Segments ─────────────────────────────────────────────────────────
with st.spinner(f"Fitting K-Means with K={k}..."):
    labels, km, scaler = fit_segments(features, k)

# ── KPIs ─────────────────────────────────────────────────────────────────
value_analysis = segment_value_analysis(features, labels)
best_segment = value_analysis.loc[value_analysis["conversion_rate"].idxmax()]

kpi_row([
    {"label": "Segments", "value": str(k)},
    {"label": "Total Users", "value": format_number(len(features))},
    {"label": "Largest Segment", "value": format_number(value_analysis["users"].max())},
    {"label": "Best Segment Conv Rate", "value": f"{best_segment['conversion_rate']:.1%}"},
])

st.markdown("---")

# ── PCA Scatter Plot ─────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Segment Visualization (PCA)")
    pca_df = segment_pca_projection(features, labels)
    pca_df["segment"] = pca_df["segment"].astype(str)
    fig = px.scatter(pca_df, x="pc1", y="pc2", color="segment",
                     title="2D PCA Projection of User Segments",
                     color_discrete_sequence=PALETTE, opacity=0.5)
    fig.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Segment Value Analysis")
    value_analysis["segment"] = value_analysis["segment"].astype(str)
    fig = bar_chart(value_analysis, "segment", "conversion_rate", title="Conversion Rate by Segment")
    st.plotly_chart(fig, use_container_width=True)

# ── Segment Profiles ─────────────────────────────────────────────────────
st.subheader("Segment Profiles")

col1, col2 = st.columns(2)
with col1:
    fig = bar_chart(value_analysis, "segment", "avg_impressions", title="Avg Impressions per User by Segment")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = bar_chart(value_analysis, "segment", "avg_cpm", title="Avg CPM Exposure by Segment")
    st.plotly_chart(fig, use_container_width=True)

# ── Detail Table ─────────────────────────────────────────────────────────
st.subheader("Segment Detail")
st.dataframe(value_analysis, use_container_width=True, hide_index=True)
