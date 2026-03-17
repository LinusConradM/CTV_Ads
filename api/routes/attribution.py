"""API — Attribution Modeling Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters, cache_key, get_or_compute
from api.serializers import df_to_records

from analytics.attribution import attribution_comparison, build_conversion_paths

router = APIRouter(tags=["attribution"])

MAX_ROWS = 200_000  # Sample for row-by-row attribution path building


@router.get("/attribution")
def get_attribution(
    half_life_days: float = 7.0,
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Multi-touch attribution comparison across models."""
    key = cache_key("attribution", half_life_days=half_life_days,
                    start_date=start_date, end_date=end_date,
                    campaigns=campaigns, device_types=device_types)

    def compute():
        df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)
        return _compute_attribution(df, half_life_days)

    return get_or_compute(key, compute)


def _compute_attribution(df, half_life_days):
    if len(df) == 0:
        return {"kpis": {}, "comparison": [], "path_stats": {}}

    # Sample for expensive path building
    df_sampled = df.sample(n=min(MAX_ROWS, len(df)), random_state=42) if len(df) > MAX_ROWS else df

    # Build conversion paths for stats
    paths = build_conversion_paths(df_sampled)

    # Full attribution comparison (uses sampled data)
    comparison = attribution_comparison(df_sampled, half_life_days=half_life_days)

    # KPIs from full dataset for accuracy
    total_conversions = int(df["converted"].sum())
    avg_path_length = round(float(paths["path_length"].mean()), 2) if len(paths) > 0 else 0
    campaigns_credited = int(comparison["campaign_id"].nunique()) if len(comparison) > 0 else 0
    total_spend = round(float(df["clearing_price_cpm"].sum() / 1000), 2)

    kpis = {
        "total_conversions": total_conversions,
        "avg_path_length": avg_path_length,
        "campaigns_credited": campaigns_credited,
        "total_spend": total_spend,
    }

    return {
        "kpis": kpis,
        "comparison": df_to_records(comparison),
        "path_stats": {
            "total_paths": len(paths),
            "avg_path_length": avg_path_length,
            "max_path_length": int(paths["path_length"].max()) if len(paths) > 0 else 0,
        },
    }
