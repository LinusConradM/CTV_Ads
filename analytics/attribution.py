"""
Analytics — Attribution Modeling

Multi-touch attribution models comparing credit allocation methodologies:
last-touch, first-touch, linear, time-decay, and Shapley value.
"""

import pandas as pd
import numpy as np
from itertools import combinations


def build_conversion_paths(df: pd.DataFrame) -> pd.DataFrame:
    """Construct ordered touchpoint sequences per converting user.

    Returns a DataFrame with columns:
    - user_id_hashed: user identifier
    - path: list of (campaign_id, timestamp) tuples ordered chronologically
    - conversion_timestamp: timestamp of conversion event
    """
    # Only users who converted at least once
    converters = df[df["converted"] == 1]["user_id_hashed"].unique()
    user_impressions = df[df["user_id_hashed"].isin(converters)].copy()
    user_impressions = user_impressions.sort_values(["user_id_hashed", "timestamp"])

    paths = []
    for user_id, group in user_impressions.groupby("user_id_hashed"):
        touchpoints = group[["campaign_id", "timestamp", "creative_id", "device_type"]].to_dict("records")
        conversion_rows = group[group["converted"] == 1]
        if len(conversion_rows) > 0:
            conv_ts = conversion_rows["timestamp"].iloc[-1]
            # Only touchpoints before or at conversion
            path = [t for t in touchpoints if t["timestamp"] <= conv_ts]
            if path:
                paths.append({
                    "user_id_hashed": user_id,
                    "path": path,
                    "path_length": len(path),
                    "conversion_timestamp": conv_ts,
                })

    return pd.DataFrame(paths)


def last_touch_attribution(paths: pd.DataFrame) -> pd.DataFrame:
    """100% credit to final touchpoint before conversion."""
    credits = []
    for _, row in paths.iterrows():
        last = row["path"][-1]
        credits.append({
            "campaign_id": last["campaign_id"],
            "credit": 1.0,
        })

    return pd.DataFrame(credits).groupby("campaign_id")["credit"].sum().reset_index()


def first_touch_attribution(paths: pd.DataFrame) -> pd.DataFrame:
    """100% credit to first touchpoint in path."""
    credits = []
    for _, row in paths.iterrows():
        first = row["path"][0]
        credits.append({
            "campaign_id": first["campaign_id"],
            "credit": 1.0,
        })

    return pd.DataFrame(credits).groupby("campaign_id")["credit"].sum().reset_index()


def linear_attribution(paths: pd.DataFrame) -> pd.DataFrame:
    """Equal credit distributed across all touchpoints."""
    credits = []
    for _, row in paths.iterrows():
        n = len(row["path"])
        for touch in row["path"]:
            credits.append({
                "campaign_id": touch["campaign_id"],
                "credit": 1.0 / n,
            })

    return pd.DataFrame(credits).groupby("campaign_id")["credit"].sum().reset_index()


def time_decay_attribution(paths: pd.DataFrame, half_life_days: float = 7.0) -> pd.DataFrame:
    """Exponentially higher credit for touchpoints closer to conversion."""
    credits = []
    for _, row in paths.iterrows():
        conv_ts = row["conversion_timestamp"]
        weights = []
        for touch in row["path"]:
            days_before = (conv_ts - touch["timestamp"]).total_seconds() / 86400
            weight = 2 ** (-days_before / half_life_days)
            weights.append(weight)

        total_weight = sum(weights)
        for touch, w in zip(row["path"], weights):
            credits.append({
                "campaign_id": touch["campaign_id"],
                "credit": w / total_weight if total_weight > 0 else 0,
            })

    return pd.DataFrame(credits).groupby("campaign_id")["credit"].sum().reset_index()


def shapley_attribution(paths: pd.DataFrame, max_path_length: int = 8) -> pd.DataFrame:
    """Game-theoretic Shapley value attribution.

    For efficiency, limits to paths of max_path_length or fewer unique campaigns.
    Longer paths fall back to linear attribution.
    """
    credits = []

    for _, row in paths.iterrows():
        unique_campaigns = list(set(t["campaign_id"] for t in row["path"]))

        if len(unique_campaigns) > max_path_length:
            # Fall back to linear for very long paths
            n = len(row["path"])
            for touch in row["path"]:
                credits.append({"campaign_id": touch["campaign_id"], "credit": 1.0 / n})
            continue

        n = len(unique_campaigns)
        if n == 1:
            credits.append({"campaign_id": unique_campaigns[0], "credit": 1.0})
            continue

        # Compute Shapley values
        for campaign in unique_campaigns:
            shapley_value = 0
            others = [c for c in unique_campaigns if c != campaign]

            for size in range(0, n):
                for subset in combinations(others, size):
                    subset_set = set(subset)
                    # Value with campaign
                    with_campaign = len(subset_set | {campaign}) / n
                    # Value without campaign
                    without_campaign = len(subset_set) / n if subset_set else 0

                    # Weighting factor
                    weight = (
                        np.math.factorial(size) * np.math.factorial(n - size - 1)
                        / np.math.factorial(n)
                    )
                    shapley_value += weight * (with_campaign - without_campaign)

            credits.append({"campaign_id": campaign, "credit": shapley_value})

    return pd.DataFrame(credits).groupby("campaign_id")["credit"].sum().reset_index()


def attribution_comparison(df: pd.DataFrame, half_life_days: float = 7.0) -> pd.DataFrame:
    """Side-by-side comparison of all attribution models."""
    paths = build_conversion_paths(df)

    if len(paths) == 0:
        return pd.DataFrame(columns=["campaign_id"])

    last = last_touch_attribution(paths).rename(columns={"credit": "last_touch"})
    first = first_touch_attribution(paths).rename(columns={"credit": "first_touch"})
    linear = linear_attribution(paths).rename(columns={"credit": "linear"})
    decay = time_decay_attribution(paths, half_life_days).rename(columns={"credit": "time_decay"})

    comparison = last.merge(first, on="campaign_id", how="outer")
    comparison = comparison.merge(linear, on="campaign_id", how="outer")
    comparison = comparison.merge(decay, on="campaign_id", how="outer")
    comparison = comparison.fillna(0)

    # Add spend data for ROAS calculation
    spend = df.groupby("campaign_id")["clearing_price_cpm"].sum().reset_index()
    spend.columns = ["campaign_id", "total_spend_cpm"]
    spend["total_spend"] = spend["total_spend_cpm"] / 1000
    comparison = comparison.merge(spend[["campaign_id", "total_spend"]], on="campaign_id", how="left")

    return comparison.sort_values("last_touch", ascending=False).reset_index(drop=True)
