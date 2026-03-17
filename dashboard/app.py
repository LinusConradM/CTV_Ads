"""
CTV Ad Intelligence Platform — Executive Dashboard

Main Streamlit application with sidebar navigation and global data loading.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.ingest import ingest
from etl.clean import clean
from etl.transform import transform

st.set_page_config(
    page_title="CTV Ad Intelligence",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600)
def load_data():
    """Load and transform impression data."""
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "impressions.csv"
    if not raw_path.exists():
        st.error(f"Data file not found: {raw_path}")
        st.info("Run: `python data/generator/ctv_simulator.py` to generate data.")
        st.stop()

    df = ingest(raw_path)
    df = clean(df)
    df = transform(df)
    return df


def main():
    st.sidebar.title("CTV Ad Intelligence")
    st.sidebar.markdown("---")

    # Load data
    with st.spinner("Loading impression data..."):
        df = load_data()

    # Global filters in sidebar
    st.sidebar.header("Filters")

    # Date range
    min_date = df["report_date"].min()
    max_date = df["report_date"].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Campaign filter
    campaigns = sorted(df["campaign_id"].unique())
    selected_campaigns = st.sidebar.multiselect("Campaigns", campaigns, default=campaigns)
    if not selected_campaigns:
        selected_campaigns = campaigns

    # Device filter
    devices = sorted(df["device_type"].unique())
    selected_devices = st.sidebar.multiselect("Device Types", devices, default=devices)
    if not selected_devices:
        selected_devices = devices

    # Apply filters
    mask = (
        (df["report_date"] >= start_date) &
        (df["report_date"] <= end_date) &
        (df["campaign_id"].isin(selected_campaigns)) &
        (df["device_type"].isin(selected_devices))
    )
    filtered_df = df[mask]

    # Store in session state for pages
    st.session_state["df"] = df
    st.session_state["filtered_df"] = filtered_df

    # Sidebar stats
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Total records: {len(filtered_df):,} / {len(df):,}")
    st.sidebar.caption(f"Date range: {start_date} to {end_date}")

    # Main content
    st.title("CTV Ad Intelligence Platform")
    st.markdown("### Connected TV Advertising Analytics Dashboard")
    st.markdown("---")

    # Quick overview KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Impressions", f"{len(filtered_df):,}")
    with col2:
        st.metric("Unique Reach", f"{filtered_df['user_id_hashed'].nunique():,}")
    with col3:
        avg_freq = len(filtered_df) / max(filtered_df['user_id_hashed'].nunique(), 1)
        st.metric("Avg Frequency", f"{avg_freq:.1f}")
    with col4:
        st.metric("Avg CPM", f"${filtered_df['clearing_price_cpm'].mean():.2f}")
    with col5:
        st.metric("Viewable Rate", f"{filtered_df['is_viewable'].mean():.1%}")
    with col6:
        st.metric("Conv Rate", f"{filtered_df['converted'].mean():.2%}")

    st.markdown("---")
    st.info("Navigate to specific analytics modules using the sidebar pages.")


if __name__ == "__main__":
    main()
