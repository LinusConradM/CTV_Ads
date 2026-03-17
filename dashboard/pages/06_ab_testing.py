"""Page 6 — A/B Test Results."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.components.kpi_cards import kpi_row, format_pct
from dashboard.components.charts import PALETTE
from analytics.ab_testing import ABTestAnalyzer

st.header("A/B Test Framework")

if "filtered_df" not in st.session_state:
    st.warning("Please load data from the main page first.")
    st.stop()

df = st.session_state["filtered_df"]

# ── Test Configuration ───────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("A/B Test Configuration")

# Select campaign for testing
campaigns = sorted(df["campaign_id"].unique())
test_campaign = st.sidebar.selectbox("Campaign", campaigns)

# Select metric
metric = st.sidebar.selectbox("Metric", ["view_completion_pct", "converted", "pixels_visible_pct"])

# Get creatives for this campaign
campaign_df = df[df["campaign_id"] == test_campaign]
creatives = sorted(campaign_df["creative_id"].unique())

if len(creatives) < 2:
    st.warning(f"Campaign {test_campaign} has only {len(creatives)} creative(s). Need at least 2 for A/B testing.")
    st.stop()

control_creative = st.sidebar.selectbox("Control (A)", creatives, index=0)
treatment_creative = st.sidebar.selectbox("Treatment (B)", [c for c in creatives if c != control_creative], index=0)

# ── Run Test ─────────────────────────────────────────────────────────────
control = campaign_df[campaign_df["creative_id"] == control_creative][metric]
treatment = campaign_df[campaign_df["creative_id"] == treatment_creative][metric]

if len(control) < 10 or len(treatment) < 10:
    st.warning("Insufficient sample size for meaningful testing.")
    st.stop()

analyzer = ABTestAnalyzer(control, treatment)

# ── KPIs ─────────────────────────────────────────────────────────────────
ttest = analyzer.run_ttest()
power = analyzer.power_analysis()

kpi_row([
    {"label": "Control Mean", "value": f"{ttest['control_mean']:.4f}"},
    {"label": "Treatment Mean", "value": f"{ttest['treatment_mean']:.4f}"},
    {"label": "Effect Size", "value": f"{ttest['effect_size']:.4f}"},
    {"label": "P-Value", "value": f"{ttest['p_value']:.4f}"},
    {"label": "Significant", "value": "Yes" if ttest["significant"] else "No"},
    {"label": "Powered", "value": "Yes" if power["is_sufficiently_powered"] else "No"},
])

st.markdown("---")

# ── Distribution Comparison ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution Comparison")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=control, name=f"Control ({control_creative})",
                               opacity=0.7, marker_color=PALETTE[0], nbinsx=40))
    fig.add_trace(go.Histogram(x=treatment, name=f"Treatment ({treatment_creative})",
                               opacity=0.7, marker_color=PALETTE[1], nbinsx=40))
    fig.update_layout(barmode="overlay", template="plotly_white", height=400,
                      title=f"{metric} Distribution: {control_creative} vs {treatment_creative}")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Confidence Interval")
    ci_lower, ci_upper = ttest["ci_95"]
    effect = ttest["effect_size"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[ci_lower, effect, ci_upper], y=[0, 0, 0],
        mode="markers+lines",
        marker=dict(size=[8, 14, 8], color=[PALETTE[2], PALETTE[0], PALETTE[2]]),
        line=dict(color=PALETTE[0], width=3),
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        template="plotly_white", height=400,
        title="95% Confidence Interval for Effect Size",
        xaxis_title="Effect Size",
        yaxis=dict(visible=False),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Power Analysis ───────────────────────────────────────────────────────
st.subheader("Power Analysis")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    | Parameter | Value |
    |-----------|-------|
    | Min Sample Size (per group) | **{power['min_sample_size_per_group']:,}** |
    | Current Control N | {power['current_n_control']:,} |
    | Current Treatment N | {power['current_n_treatment']:,} |
    | MDE | {power['mde']:.6f} |
    | Alpha | {power['alpha']} |
    | Power | {power['power']} |
    | Sufficiently Powered | **{'Yes' if power['is_sufficiently_powered'] else 'No'}** |
    """)

with col2:
    # Bootstrap CI
    bootstrap = analyzer.bootstrap_ci(n_iterations=5000)
    st.markdown(f"""
    **Bootstrap Confidence Interval**

    | Parameter | Value |
    |-----------|-------|
    | Mean Difference | {bootstrap['mean_diff']:.6f} |
    | 95% CI Lower | {bootstrap['ci_lower']:.6f} |
    | 95% CI Upper | {bootstrap['ci_upper']:.6f} |
    | Significant | **{'Yes' if bootstrap['significant'] else 'No'}** |
    """)

# ── Sequential Testing ───────────────────────────────────────────────────
st.subheader("Sequential Test (Early Stopping)")
seq = analyzer.sequential_test(n_looks=5)

seq_df = pd.DataFrame(seq["looks"])
if len(seq_df) > 0:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=seq_df["look"], y=seq_df["z_stat"].abs(),
                             mode="lines+markers", name="|Z-stat|", line=dict(color=PALETTE[0])))
    fig.add_trace(go.Scatter(x=seq_df["look"], y=seq_df["z_boundary"],
                             mode="lines", name="Boundary", line=dict(color=PALETTE[2], dash="dash")))
    fig.update_layout(template="plotly_white", title="Sequential Test Boundaries",
                      xaxis_title="Look", yaxis_title="Z-statistic", height=400)
    st.plotly_chart(fig, use_container_width=True)

    if seq["early_stop"]:
        st.success("Early stopping triggered — effect detected before final look.")
    else:
        st.info("No early stopping — full sample needed for conclusion.")
