"""API — Campaign Performance Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters, cache_key, get_or_compute
from api.serializers import df_to_records

router = APIRouter(tags=["campaigns"])


@router.get("/campaigns")
def get_campaigns(
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Campaign performance metrics, trends, and breakdowns."""
    key = cache_key("campaigns", start_date=start_date, end_date=end_date,
                    campaigns=campaigns, device_types=device_types)

    def compute():
        df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)
        return _compute_campaigns(df)

    return get_or_compute(key, compute)


def _compute_campaigns(df):
    if len(df) == 0:
        return {"kpis": {}, "performance_table": [], "cpm_trend": [], "device_breakdown": [], "category_breakdown": [], "top_dmas": []}

    # KPIs
    unique_reach = int(df["user_id_hashed"].nunique())
    total_imps = len(df)
    kpis = {
        "total_impressions": total_imps,
        "unique_reach": unique_reach,
        "avg_frequency": round(total_imps / max(unique_reach, 1), 2),
        "avg_cpm": round(float(df["clearing_price_cpm"].mean()), 2),
        "viewable_rate": round(float(df["is_viewable"].mean()), 4),
        "completion_rate": round(float((df["view_completion_pct"] >= 0.95).mean()), 4),
    }

    # Daily CPM trend
    cpm_trend = df.groupby("report_date").agg(
        avg_cpm=("clearing_price_cpm", "mean"),
        impressions=("impression_id", "count"),
    ).reset_index().sort_values("report_date")

    # Device breakdown
    device_breakdown = df.groupby("device_type").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
        viewable_rate=("is_viewable", "mean"),
    ).reset_index().sort_values("impressions", ascending=False)

    # Content category breakdown
    category_breakdown = df.groupby("content_category").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
    ).reset_index().sort_values("avg_cpm", ascending=False)

    # Top DMAs
    top_dmas = df.groupby("dma_name").agg(
        impressions=("impression_id", "count"),
        avg_cpm=("clearing_price_cpm", "mean"),
    ).reset_index().sort_values("impressions", ascending=False).head(10)

    # Campaign performance table
    perf = df.groupby("campaign_id").agg(
        impressions=("impression_id", "count"),
        unique_reach=("user_id_hashed", "nunique"),
        avg_cpm=("clearing_price_cpm", "mean"),
        viewable_rate=("is_viewable", "mean"),
        completion_rate=("view_completion_pct", lambda x: (x >= 0.95).mean()),
        conversion_rate=("converted", "mean"),
        total_spend=("clearing_price_cpm", lambda x: x.sum() / 1000),
    ).reset_index()
    perf["frequency"] = (perf["impressions"] / perf["unique_reach"].clip(lower=1)).round(2)
    perf = perf.sort_values("impressions", ascending=False)

    return {
        "kpis": kpis,
        "performance_table": df_to_records(perf),
        "cpm_trend": df_to_records(cpm_trend),
        "device_breakdown": df_to_records(device_breakdown),
        "category_breakdown": df_to_records(category_breakdown),
        "top_dmas": df_to_records(top_dmas),
    }
