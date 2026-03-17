"""API — Audience Segmentation Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import df_to_records

from analytics.segmentation import (
    prepare_clustering_features,
    find_optimal_k,
    fit_segments,
    segment_pca_projection,
    segment_value_analysis,
)

router = APIRouter(tags=["segmentation"])

MAX_USERS_FOR_CLUSTERING = 5_000  # Sample users for K-Means performance


@router.get("/segmentation")
def get_segmentation(
    k: int = 4,
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = Query(None),
    device_types: list[str] | None = Query(None),
):
    """Audience segmentation with K-Means clustering."""
    df = apply_filters(get_full_df(), start_date, end_date, campaigns, device_types)

    if len(df) == 0:
        return {"kpis": {}, "elbow_curve": [], "pca_projection": [], "value_analysis": []}

    # Sample impressions to limit user-level feature computation
    # Keep enough to represent user behavior well
    unique_users = df["user_id_hashed"].unique()
    if len(unique_users) > MAX_USERS_FOR_CLUSTERING:
        import numpy as np
        rng = np.random.default_rng(42)
        sampled_users = rng.choice(unique_users, size=MAX_USERS_FOR_CLUSTERING, replace=False)
        df_sampled = df[df["user_id_hashed"].isin(sampled_users)]
    else:
        df_sampled = df

    # Prepare user-level features (on sampled users)
    features = prepare_clustering_features(df_sampled)

    # Elbow curve data (K=2..8)
    elbow = find_optimal_k(features, k_range=(2, 8))

    # Fit segments with chosen K
    labels, model, scaler = fit_segments(features, k)

    # PCA projection (further sample for frontend rendering)
    pca_df = segment_pca_projection(features, labels)
    if len(pca_df) > 5000:
        pca_df = pca_df.sample(5000, random_state=42)

    # Value analysis
    value = segment_value_analysis(features, labels)

    # KPIs
    total_unique_users = len(unique_users)
    kpis = {
        "num_segments": k,
        "total_users": total_unique_users,
        "largest_segment_size": int(value["users"].max()),
        "best_conversion_rate": round(float(value["conversion_rate"].max()), 4),
    }

    return {
        "kpis": kpis,
        "elbow_curve": df_to_records(elbow),
        "pca_projection": df_to_records(pca_df),
        "value_analysis": df_to_records(value),
    }
