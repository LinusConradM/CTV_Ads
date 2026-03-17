"""API — Overview / Dashboard Home Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import df_to_records, _convert_value

router = APIRouter(tags=["overview"])


@router.get("/overview")
def get_overview(
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Dashboard home KPIs and daily trend."""
    df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)

    total_impressions = len(df)
    unique_reach = int(df["user_id_hashed"].nunique())
    avg_frequency = round(total_impressions / max(unique_reach, 1), 2)
    avg_cpm = round(float(df["clearing_price_cpm"].mean()), 2) if len(df) > 0 else 0
    viewable_rate = round(float(df["is_viewable"].mean()), 4) if len(df) > 0 else 0
    conversion_rate = round(float(df["converted"].mean()), 4) if len(df) > 0 else 0

    # Daily trend for sparklines
    daily = df.groupby("report_date").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
        viewable_rate=("is_viewable", "mean"),
        conversions=("converted", "sum"),
    ).reset_index()
    daily = daily.sort_values("report_date")

    # Top campaigns summary
    campaign_summary = df.groupby("campaign_id").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
        viewable_rate=("is_viewable", "mean"),
        conversion_rate=("converted", "mean"),
        unique_reach=("user_id_hashed", "nunique"),
    ).reset_index().sort_values("impressions", ascending=False).head(10)

    return {
        "kpis": {
            "total_impressions": total_impressions,
            "unique_reach": unique_reach,
            "avg_frequency": avg_frequency,
            "avg_cpm": avg_cpm,
            "viewable_rate": viewable_rate,
            "conversion_rate": conversion_rate,
        },
        "daily_trend": df_to_records(daily),
        "campaign_summary": df_to_records(campaign_summary),
    }
