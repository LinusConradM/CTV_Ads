"""Dashboard — Plotly chart wrappers."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLORS = {
    "primary": "#2E75B6",
    "secondary": "#4ECDC4",
    "accent": "#FF6B6B",
    "warning": "#FFE66D",
    "gray": "#95A5A6",
    "dark": "#2C3E50",
}

PALETTE = ["#2E75B6", "#4ECDC4", "#FF6B6B", "#FFE66D", "#95A5A6", "#E74C3C", "#3498DB", "#2ECC71"]


def line_chart(df, x, y, title="", color=None, labels=None):
    fig = px.line(df, x=x, y=y, title=title, color=color, labels=labels, color_discrete_sequence=PALETTE)
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def bar_chart(df, x, y, title="", color=None, labels=None, orientation="v"):
    fig = px.bar(df, x=x, y=y, title=title, color=color, labels=labels,
                 orientation=orientation, color_discrete_sequence=PALETTE, barmode="group")
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def histogram(df, x, title="", nbins=30, color=None):
    fig = px.histogram(df, x=x, title=title, nbins=nbins, color=color, color_discrete_sequence=PALETTE)
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def scatter_chart(df, x, y, title="", color=None, size=None, labels=None):
    fig = px.scatter(df, x=x, y=y, title=title, color=color, size=size, labels=labels,
                     color_discrete_sequence=PALETTE)
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def control_chart(df, date_col, value_col, ucl_col, lcl_col, mean_col, title=""):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[date_col], y=df[value_col], mode="lines+markers",
                             name="Value", line=dict(color=COLORS["primary"])))
    fig.add_trace(go.Scatter(x=df[date_col], y=df[ucl_col], mode="lines",
                             name="UCL", line=dict(color=COLORS["accent"], dash="dash")))
    fig.add_trace(go.Scatter(x=df[date_col], y=df[lcl_col], mode="lines",
                             name="LCL", line=dict(color=COLORS["accent"], dash="dash")))
    fig.add_trace(go.Scatter(x=df[date_col], y=df[mean_col], mode="lines",
                             name="Mean", line=dict(color=COLORS["gray"], dash="dot")))
    fig.update_layout(template="plotly_white", title=title, height=400,
                      margin=dict(l=20, r=20, t=40, b=20))
    return fig


def pie_chart(df, names, values, title=""):
    fig = px.pie(df, names=names, values=values, title=title, color_discrete_sequence=PALETTE)
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def heatmap(df, x, y, z, title=""):
    fig = px.density_heatmap(df, x=x, y=y, z=z, title=title, color_continuous_scale="Blues")
    fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=40, b=20))
    return fig
