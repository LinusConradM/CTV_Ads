"""API — Viewability & Delivery Health Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import df_to_records, dict_to_safe

from analytics.viewability import (
    campaign_viewability_report,
    device_viewability_breakdown,
    publisher_viewability_scorecard,
    viewability_trend,
    viewability_distribution,
)

router = APIRouter(tags=["viewability"])


@router.get("/viewability")
def get_viewability(
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Viewability metrics, distributions, trends, and publisher scorecard."""
    df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)

    if len(df) == 0:
        return {"kpis": {}, "campaign_report": [], "device_breakdown": [], "publisher_scorecard": [], "trend": [], "distribution": {}}

    # Distribution stats (dict)
    dist = viewability_distribution(df)

    # KPIs from distribution
    kpis = {
        "viewable_rate": dist["overall_viewable_rate"],
        "video_viewable_rate": dist["video_viewable_rate"],
        "display_viewable_rate": dist["display_viewable_rate"],
        "avg_pixel_visibility": dist["pixel_visibility"]["mean"],
        "avg_view_duration": dist["view_duration"]["mean"],
    }

    # Campaign viewability report
    camp_report = campaign_viewability_report(df)

    # Device breakdown
    device_bkdn = device_viewability_breakdown(df)

    # Publisher scorecard
    pub_scorecard = publisher_viewability_scorecard(df)

    # Viewability trend with control limits
    trend = viewability_trend(df)

    return {
        "kpis": dict_to_safe(kpis),
        "distribution": dict_to_safe(dist),
        "campaign_report": df_to_records(camp_report),
        "device_breakdown": df_to_records(device_bkdn),
        "publisher_scorecard": df_to_records(pub_scorecard),
        "trend": df_to_records(trend),
    }
