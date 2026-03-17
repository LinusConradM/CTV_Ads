"""API — Frequency & Reach Analysis Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import df_to_records, dict_to_safe

from analytics.frequency_reach import (
    reach_curve,
    frequency_distribution,
    optimal_frequency,
    diminishing_returns,
    frequency_cap_recommendation,
)

router = APIRouter(tags=["frequency"])

MAX_ROWS_FOR_CURVE = 100_000  # Sample for row-by-row operations


@router.get("/frequency")
def get_frequency(
    campaign_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Frequency & reach analysis with cap recommendations."""
    df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)

    if len(df) == 0:
        return {"kpis": {}, "reach_curve": [], "frequency_distribution": [], "optimal_frequency": [], "diminishing_returns": [], "cap_recommendation": {}}

    # Sample for expensive row-by-row operations
    df_sampled = df.sample(n=min(MAX_ROWS_FOR_CURVE, len(df)), random_state=42) if len(df) > MAX_ROWS_FOR_CURVE else df

    # Reach curve (uses row-by-row iteration — use sampled data)
    rc = reach_curve(df_sampled, campaign_id=campaign_id)

    # Frequency distribution (groupby — fast on full data)
    fd = frequency_distribution(df, campaign_id=campaign_id)

    # Optimal frequency (groupby — fast on full data)
    opt = optimal_frequency(df)

    # Diminishing returns (row-by-row — use sampled data)
    dr = diminishing_returns(df_sampled)

    # Cap recommendations (groupby — fast on full data)
    cap_conv = frequency_cap_recommendation(df, objective="conversions")
    cap_reach = frequency_cap_recommendation(df, objective="reach")

    # KPIs (groupby — fast)
    user_freq = df.groupby("user_id_hashed").size()
    kpis = {
        "total_reach": int(user_freq.count()),
        "avg_frequency": round(float(user_freq.mean()), 2),
        "median_frequency": round(float(user_freq.median()), 1),
        "max_frequency": int(user_freq.max()),
        "recommended_cap_conv": cap_conv.get("recommended_cap"),
        "recommended_cap_reach": cap_reach.get("recommended_cap"),
    }

    return {
        "kpis": kpis,
        "reach_curve": df_to_records(rc),
        "frequency_distribution": df_to_records(fd),
        "optimal_frequency": df_to_records(opt),
        "diminishing_returns": df_to_records(dr),
        "cap_recommendation": {
            "conversions": dict_to_safe(cap_conv),
            "reach": dict_to_safe(cap_reach),
        },
    }
