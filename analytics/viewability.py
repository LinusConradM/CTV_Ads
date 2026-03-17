"""
Analytics — Viewability Engine

IAB/MRC-standard viewability measurement for CTV and display advertising.
- Video: 50% pixels visible for 2+ continuous seconds
- Display: 50% pixels visible for 1+ continuous second
"""

import pandas as pd
import numpy as np

IAB_DISPLAY_PIXEL_THRESHOLD = 0.50
IAB_DISPLAY_TIME_THRESHOLD = 1.0
IAB_VIDEO_PIXEL_THRESHOLD = 0.50
IAB_VIDEO_TIME_THRESHOLD = 2.0


def classify_viewable(row: pd.Series) -> bool:
    """Classify a single impression as viewable per IAB/MRC standard."""
    if row["ad_format"] == "video":
        return (row["pixels_visible_pct"] >= IAB_VIDEO_PIXEL_THRESHOLD and
                row["view_duration_seconds"] >= IAB_VIDEO_TIME_THRESHOLD)
    return (row["pixels_visible_pct"] >= IAB_DISPLAY_PIXEL_THRESHOLD and
            row["view_duration_seconds"] >= IAB_DISPLAY_TIME_THRESHOLD)


def campaign_viewability_report(df: pd.DataFrame) -> pd.DataFrame:
    """Compute viewability metrics by campaign."""
    report = df.groupby("campaign_id").agg(
        total_impressions=("impression_id", "count"),
        viewable_impressions=("is_viewable", "sum"),
        avg_pixel_visibility=("pixels_visible_pct", "mean"),
        avg_view_duration=("view_duration_seconds", "mean"),
        avg_completion_pct=("view_completion_pct", "mean"),
    ).reset_index()

    report["viewable_rate"] = (
        report["viewable_impressions"] / report["total_impressions"]
    ).round(4)

    return report.sort_values("viewable_rate", ascending=False).reset_index(drop=True)


def device_viewability_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Viewability metrics by device type and brand."""
    breakdown = df.groupby(["device_type", "device_brand"]).agg(
        impressions=("impression_id", "count"),
        viewable_rate=("is_viewable", "mean"),
        avg_pixel_visibility=("pixels_visible_pct", "mean"),
        avg_view_duration=("view_duration_seconds", "mean"),
    ).round(4).reset_index()

    return breakdown.sort_values("viewable_rate", ascending=False).reset_index(drop=True)


def publisher_viewability_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """Rank publishers by viewability rate."""
    scorecard = df.groupby("publisher_id").agg(
        impressions=("impression_id", "count"),
        viewable_rate=("is_viewable", "mean"),
        avg_pixel_visibility=("pixels_visible_pct", "mean"),
        avg_cpm=("clearing_price_cpm", "mean"),
    ).round(4).reset_index()

    scorecard["rank"] = scorecard["viewable_rate"].rank(ascending=False, method="min").astype(int)
    return scorecard.sort_values("rank").reset_index(drop=True)


def viewability_trend(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Daily viewability trend with statistical control limits (3-sigma)."""
    daily = df.groupby("report_date").agg(
        impressions=("impression_id", "count"),
        viewable_rate=("is_viewable", "mean"),
        avg_pixel_visibility=("pixels_visible_pct", "mean"),
    ).reset_index()

    mean_rate = daily["viewable_rate"].mean()
    std_rate = daily["viewable_rate"].std()
    daily["ucl"] = mean_rate + 3 * std_rate  # Upper control limit
    daily["lcl"] = max(mean_rate - 3 * std_rate, 0)  # Lower control limit
    daily["mean_line"] = mean_rate
    daily["out_of_control"] = ~daily["viewable_rate"].between(daily["lcl"], daily["ucl"])

    return daily


def viewability_distribution(df: pd.DataFrame) -> dict:
    """Summary statistics for viewability distribution analysis."""
    return {
        "pixel_visibility": {
            "mean": df["pixels_visible_pct"].mean(),
            "median": df["pixels_visible_pct"].median(),
            "std": df["pixels_visible_pct"].std(),
            "p25": df["pixels_visible_pct"].quantile(0.25),
            "p75": df["pixels_visible_pct"].quantile(0.75),
        },
        "view_duration": {
            "mean": df["view_duration_seconds"].mean(),
            "median": df["view_duration_seconds"].median(),
            "std": df["view_duration_seconds"].std(),
            "p25": df["view_duration_seconds"].quantile(0.25),
            "p75": df["view_duration_seconds"].quantile(0.75),
        },
        "overall_viewable_rate": df["is_viewable"].mean(),
        "video_viewable_rate": df.loc[df["ad_format"] == "video", "is_viewable"].mean(),
        "display_viewable_rate": df.loc[df["ad_format"] == "display_overlay", "is_viewable"].mean(),
    }
