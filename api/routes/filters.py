"""API — Filter Options Endpoint"""

from fastapi import APIRouter
from api.dependencies import get_full_df, cache_key, get_or_compute
from api.serializers import _convert_value

router = APIRouter(tags=["filters"])


@router.get("/filters")
def get_filter_options():
    """Return available filter values for the frontend."""
    key = cache_key("filters")

    def compute():
        return _compute_filters()

    return get_or_compute(key, compute)


def _compute_filters():
    df = get_full_df()

    campaigns = sorted(df["campaign_id"].unique().tolist())
    device_types = sorted(df["device_type"].unique().tolist())
    creative_ids = sorted(df["creative_id"].unique().tolist())

    min_date = _convert_value(df["report_date"].min())
    max_date = _convert_value(df["report_date"].max())

    # Creative IDs per campaign (for A/B testing page)
    campaign_creatives = (
        df.groupby("campaign_id")["creative_id"]
        .apply(lambda x: sorted(x.unique().tolist()))
        .to_dict()
    )

    return {
        "campaigns": campaigns,
        "device_types": device_types,
        "creative_ids": creative_ids,
        "date_range": {"min": min_date, "max": max_date},
        "campaign_creatives": campaign_creatives,
    }
