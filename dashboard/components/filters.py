"""Dashboard — Reusable filter components."""

import streamlit as st
import pandas as pd


def date_range_filter(df: pd.DataFrame, key_prefix: str = "") -> tuple:
    """Date range picker returning (start_date, end_date)."""
    min_date = df["report_date"].min()
    max_date = df["report_date"].max()

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key=f"{key_prefix}start")
    with col2:
        end = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key=f"{key_prefix}end")

    return start, end


def campaign_filter(df: pd.DataFrame, key: str = "campaign_filter") -> list:
    """Multi-select campaign filter."""
    campaigns = sorted(df["campaign_id"].unique())
    selected = st.multiselect("Campaigns", campaigns, default=campaigns, key=key)
    return selected if selected else campaigns


def device_filter(df: pd.DataFrame, key: str = "device_filter") -> list:
    """Multi-select device type filter."""
    devices = sorted(df["device_type"].unique())
    selected = st.multiselect("Device Types", devices, default=devices, key=key)
    return selected if selected else devices


def apply_filters(df: pd.DataFrame, start_date, end_date, campaigns: list, devices: list) -> pd.DataFrame:
    """Apply all filters to DataFrame."""
    mask = (
        (df["report_date"] >= pd.Timestamp(start_date).date()) &
        (df["report_date"] <= pd.Timestamp(end_date).date()) &
        (df["campaign_id"].isin(campaigns)) &
        (df["device_type"].isin(devices))
    )
    return df[mask]
