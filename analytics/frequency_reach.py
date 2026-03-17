"""
Analytics — Frequency & Reach Analysis

Classic advertising reach-frequency tradeoff analysis:
- Reach curves (unique audience vs. impressions served)
- Frequency distribution
- Optimal frequency identification
- Diminishing returns analysis
- Frequency cap recommendations
"""

import pandas as pd
import numpy as np


def reach_curve(df: pd.DataFrame, campaign_id: str = None) -> pd.DataFrame:
    """Compute reach curve: unique users reached vs. total impressions served.

    Samples impression delivery chronologically and tracks cumulative unique reach.
    """
    data = df.copy()
    if campaign_id:
        data = data[data["campaign_id"] == campaign_id]

    data = data.sort_values("timestamp")

    # Sample at intervals for efficiency
    n = len(data)
    sample_points = np.unique(np.linspace(0, n - 1, min(200, n), dtype=int))

    seen_users = set()
    curve = []
    for i, (_, row) in enumerate(data.iterrows()):
        seen_users.add(row["user_id_hashed"])
        if i in sample_points:
            curve.append({
                "impressions_served": i + 1,
                "unique_reach": len(seen_users),
            })

    result = pd.DataFrame(curve)
    if len(result) > 0:
        result["reach_pct"] = result["unique_reach"] / df["user_id_hashed"].nunique()
    return result


def frequency_distribution(df: pd.DataFrame, campaign_id: str = None) -> pd.DataFrame:
    """Histogram of impressions per unique user."""
    data = df.copy()
    if campaign_id:
        data = data[data["campaign_id"] == campaign_id]

    freq = data.groupby("user_id_hashed").size().rename("frequency")

    # Bucket into frequency groups
    bins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 50, float("inf")]
    labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11-15", "16-20", "20+"]
    freq_bucketed = pd.cut(freq, bins=[0] + bins, labels=labels + ["50+"], right=True)

    dist = freq_bucketed.value_counts().sort_index().reset_index()
    dist.columns = ["frequency_bucket", "user_count"]
    dist["pct_of_users"] = (dist["user_count"] / dist["user_count"].sum() * 100).round(2)

    return dist


def optimal_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """Conversion rate by frequency bucket to identify sweet spot."""
    user_freq = df.groupby("user_id_hashed").agg(
        frequency=("impression_id", "count"),
        converted=("converted", "max"),
    ).reset_index()

    # Create frequency buckets
    bins = [0, 1, 2, 3, 4, 5, 8, 10, 15, 20, float("inf")]
    labels = ["1", "2", "3", "4", "5", "6-8", "9-10", "11-15", "16-20", "20+"]
    user_freq["freq_bucket"] = pd.cut(user_freq["frequency"], bins=bins, labels=labels)

    result = user_freq.groupby("freq_bucket", observed=True).agg(
        users=("user_id_hashed", "count"),
        conversions=("converted", "sum"),
    ).reset_index()
    result["conversion_rate"] = (result["conversions"] / result["users"]).round(4)

    # Identify sweet spot (highest conversion rate bucket)
    if len(result) > 0:
        best_idx = result["conversion_rate"].idxmax()
        result["is_optimal"] = result.index == best_idx

    return result


def diminishing_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Incremental reach per additional impression."""
    data = df.sort_values("timestamp")

    # Compute cumulative reach at checkpoints
    n = len(data)
    checkpoints = np.unique(np.linspace(0, n - 1, min(100, n), dtype=int))

    seen = set()
    points = []
    prev_reach = 0
    prev_imp = 0

    for i, (_, row) in enumerate(data.iterrows()):
        seen.add(row["user_id_hashed"])
        if i in checkpoints:
            current_reach = len(seen)
            impressions = i + 1
            incremental_reach = current_reach - prev_reach
            incremental_imps = impressions - prev_imp

            points.append({
                "impressions": impressions,
                "cumulative_reach": current_reach,
                "incremental_reach": incremental_reach,
                "incremental_impressions": incremental_imps,
                "marginal_reach_rate": (
                    incremental_reach / incremental_imps if incremental_imps > 0 else 0
                ),
            })
            prev_reach = current_reach
            prev_imp = impressions

    return pd.DataFrame(points)


def frequency_cap_recommendation(
    df: pd.DataFrame,
    objective: str = "conversions",
) -> dict:
    """Recommend frequency cap based on objective.

    Args:
        objective: "conversions" (maximize conversion rate) or
                   "reach" (maximize unique reach)
    """
    opt_freq = optimal_frequency(df)

    if objective == "conversions":
        # Find the frequency bucket with highest conversion rate
        if len(opt_freq) == 0:
            return {"recommended_cap": None, "reason": "Insufficient data"}

        best = opt_freq.loc[opt_freq["conversion_rate"].idxmax()]
        # Parse the upper bound of the optimal bucket
        bucket_label = str(best["freq_bucket"])
        if "+" in bucket_label:
            cap = 20
        elif "-" in bucket_label:
            cap = int(bucket_label.split("-")[1])
        else:
            cap = int(bucket_label)

        return {
            "recommended_cap": cap,
            "optimal_bucket": bucket_label,
            "conversion_rate_at_optimal": round(best["conversion_rate"], 4),
            "objective": objective,
            "reason": f"Conversion rate peaks at frequency {bucket_label} "
                      f"({best['conversion_rate']:.1%}). Capping at {cap} "
                      f"prevents over-exposure while maximizing conversions.",
        }

    else:  # reach
        user_freq = df.groupby("user_id_hashed").size()
        total_imps = len(df)
        total_users = len(user_freq)

        # Simulate different caps
        results = []
        for cap in [3, 5, 8, 10, 15]:
            wasted_imps = (user_freq - cap).clip(lower=0).sum()
            efficiency = 1 - (wasted_imps / total_imps)
            results.append({"cap": cap, "efficiency": efficiency})

        results = pd.DataFrame(results)
        # Pick cap where efficiency > 90%
        good_caps = results[results["efficiency"] > 0.90]
        recommended = good_caps["cap"].min() if len(good_caps) > 0 else 10

        return {
            "recommended_cap": int(recommended),
            "objective": objective,
            "total_users": total_users,
            "avg_frequency": round(user_freq.mean(), 1),
            "reason": f"A cap of {int(recommended)} impressions per user maintains "
                      f">90% impression efficiency while maximizing reach.",
        }
