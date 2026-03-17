"""API — Anomaly Detection & Alerts Endpoint"""

from datetime import date
import numpy as np
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import df_to_records

from analytics.anomaly_detection import (
    build_anomaly_features,
    fit_isolation_forest,
    flag_anomalies,
    anomaly_summary,
    bot_traffic_indicators,
    control_chart,
)

router = APIRouter(tags=["anomalies"])

MAX_ROWS_FOR_IFOREST = 200_000


@router.get("/anomalies")
def get_anomalies(
    contamination: float = 0.05,
    metric: str = "clearing_price_cpm",
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Anomaly detection results, control charts, and flagged records."""
    df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)

    if len(df) == 0:
        return {"kpis": {}, "summary": [], "control_chart": [], "flagged_records": [], "score_distribution": []}

    # Sample for Isolation Forest (O(n) but with large constant)
    if len(df) > MAX_ROWS_FOR_IFOREST:
        df_sample = df.sample(n=MAX_ROWS_FOR_IFOREST, random_state=42)
    else:
        df_sample = df

    # Fit isolation forest on sample
    features = build_anomaly_features(df_sample)
    scores, model = fit_isolation_forest(features, contamination=contamination)

    # Flag anomalies
    flagged_df = flag_anomalies(df_sample, scores, contamination)

    # Summary by category
    summary = anomaly_summary(flagged_df)

    # Bot traffic (fast vectorized op on full data)
    bot_df = bot_traffic_indicators(df)
    bot_rate = float(bot_df["bot_indicator"].mean())

    # Control chart for selected metric (groupby — fast on full data)
    ctrl = control_chart(df, metric)

    # KPIs
    anomaly_count = int(flagged_df["is_anomaly"].sum())
    # Scale to full dataset
    scale_factor = len(df) / len(df_sample) if len(df_sample) > 0 else 1
    kpis = {
        "anomaly_rate": round(anomaly_count / len(flagged_df) * 100, 2),
        "anomalies_flagged": int(anomaly_count * scale_factor),
        "flagged_campaigns": int(flagged_df[flagged_df["is_anomaly"]]["campaign_id"].nunique()) if anomaly_count > 0 else 0,
        "bot_traffic_rate": round(bot_rate * 100, 2),
    }

    # Score distribution (binned for histogram)
    hist_counts, hist_edges = np.histogram(scores, bins=50)
    score_distribution = [
        {"bin_start": round(float(hist_edges[i]), 4), "bin_end": round(float(hist_edges[i+1]), 4), "count": int(hist_counts[i])}
        for i in range(len(hist_counts))
    ]

    # Top flagged records (limit to 50)
    flagged_records = flagged_df[flagged_df["is_anomaly"]].nsmallest(50, "anomaly_score")[
        ["impression_id", "campaign_id", "device_type", "clearing_price_cpm",
         "pixels_visible_pct", "view_duration_seconds", "user_campaign_frequency",
         "anomaly_score"]
    ]

    return {
        "kpis": kpis,
        "summary": df_to_records(summary),
        "control_chart": df_to_records(ctrl),
        "flagged_records": df_to_records(flagged_records),
        "score_distribution": score_distribution,
    }
