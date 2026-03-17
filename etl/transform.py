"""
ETL — Transformation Module

Engineers 15+ analytics features from cleaned impression data.
All feature engineering is centralized here — analytics modules
consume the transformed output.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# IAB Viewability Thresholds
IAB_DISPLAY_PIXEL_THRESHOLD = 0.50
IAB_DISPLAY_TIME_THRESHOLD = 1.0
IAB_VIDEO_PIXEL_THRESHOLD = 0.50
IAB_VIDEO_TIME_THRESHOLD = 2.0


def classify_viewable(row: pd.Series) -> bool:
    """Apply IAB/MRC viewability standard."""
    if row["ad_format"] == "video":
        return (row["pixels_visible_pct"] >= IAB_VIDEO_PIXEL_THRESHOLD and
                row["view_duration_seconds"] >= IAB_VIDEO_TIME_THRESHOLD)
    return (row["pixels_visible_pct"] >= IAB_DISPLAY_PIXEL_THRESHOLD and
            row["view_duration_seconds"] >= IAB_DISPLAY_TIME_THRESHOLD)


def add_viewability_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add viewability classification and completion percentage."""
    df["is_viewable"] = df.apply(classify_viewable, axis=1)
    df["view_completion_pct"] = (
        df["view_duration_seconds"] / df["ad_duration_seconds"]
    ).clip(0, 1)
    return df


def add_pricing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add auction pricing derived metrics."""
    df["bid_floor_ratio"] = (
        df["clearing_price_cpm"] / df["floor_price_cpm"].replace(0, np.nan)
    ).round(4)
    df["auction_efficiency"] = (
        df["clearing_price_cpm"] / df["bid_price_cpm"].replace(0, np.nan)
    ).round(4)
    return df


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract time-based features from timestamp."""
    ts = df["timestamp"]
    df["hour_of_day"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek
    df["is_primetime"] = df["hour_of_day"].between(19, 22)
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    df["report_date"] = ts.dt.date
    return df


def add_frequency_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute frequency metrics per user and campaign."""
    # User-campaign frequency
    freq = df.groupby(["user_id_hashed", "campaign_id"]).size().rename("user_campaign_frequency")
    df = df.merge(freq, on=["user_id_hashed", "campaign_id"], how="left")

    # User daily frequency
    daily_freq = df.groupby(["user_id_hashed", "report_date"]).size().rename("user_daily_frequency")
    df = df.merge(daily_freq, on=["user_id_hashed", "report_date"], how="left")

    # Campaign daily impressions
    camp_daily = df.groupby(["campaign_id", "report_date"]).size().rename("campaign_daily_impressions")
    df = df.merge(camp_daily, on=["campaign_id", "report_date"], how="left")

    return df


def add_quality_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute device, publisher, and creative quality scores."""
    # Device viewability average
    device_view = df.groupby("device_type")["pixels_visible_pct"].mean().rename("device_viewability_avg")
    df = df.merge(device_view, on="device_type", how="left")

    # Publisher quality score
    pub_quality = df.groupby("publisher_id")["is_viewable"].mean().rename("publisher_quality_score")
    df = df.merge(pub_quality, on="publisher_id", how="left")

    # Creative completion rate
    creative_comp = df.groupby("creative_id")["view_completion_pct"].mean().rename("creative_completion_rate")
    df = df.merge(creative_comp, on="creative_id", how="left")

    # DMA CPM index (relative to national average)
    national_avg_cpm = df["clearing_price_cpm"].mean()
    dma_cpm = df.groupby("geo_dma")["clearing_price_cpm"].mean().rename("dma_avg_cpm")
    dma_cpm_index = (dma_cpm / national_avg_cpm).rename("dma_cpm_index")
    df = df.merge(dma_cpm_index, on="geo_dma", how="left")

    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Run full transformation pipeline."""
    logger.info(f"Transforming {len(df):,} rows")

    df = df.copy()
    df = add_viewability_features(df)
    df = add_pricing_features(df)
    df = add_temporal_features(df)
    df = add_frequency_features(df)
    df = add_quality_features(df)

    logger.info(f"Transformation complete: {len(df.columns)} columns")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from pathlib import Path
    from etl.ingest import ingest
    from etl.clean import clean

    raw_path = Path(__file__).parent.parent / "data" / "raw" / "impressions.csv"
    df = ingest(raw_path)
    df = clean(df)
    df = transform(df)
    print(f"Transformed: {len(df):,} rows, {len(df.columns)} columns")
    print(f"\nNew columns: {sorted(set(df.columns) - set(['impression_id','timestamp','device_type','device_brand','content_category','ad_duration_seconds','ad_format','pixels_visible_pct','view_duration_seconds','bid_price_cpm','clearing_price_cpm','floor_price_cpm','user_id_hashed','campaign_id','creative_id','geo_dma','publisher_id','placement_id','converted','conversion_type']))}")
