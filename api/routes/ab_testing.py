"""API — A/B Testing Endpoint"""

from datetime import date
from fastapi import APIRouter, Query
from api.dependencies import get_full_df, apply_filters
from api.serializers import dict_to_safe

from analytics.ab_testing import ABTestAnalyzer

router = APIRouter(tags=["ab_testing"])


@router.get("/ab-testing")
def get_ab_testing(
    campaign_id: str = Query(..., description="Campaign to test"),
    metric: str = Query("view_completion_pct", description="Metric to compare"),
    control_creative: str = Query(..., description="Control creative ID"),
    treatment_creative: str = Query(..., description="Treatment creative ID"),
    start_date: date | None = None,
    end_date: date | None = None,
):
    """A/B test analysis between two creatives within a campaign."""
    df = apply_filters(get_full_df(), start_date, end_date, [campaign_id], None)

    if len(df) == 0:
        return {"error": "No data for this campaign"}

    control_data = df[df["creative_id"] == control_creative][metric]
    treatment_data = df[df["creative_id"] == treatment_creative][metric]

    if len(control_data) == 0 or len(treatment_data) == 0:
        return {"error": "Insufficient data for one or both creatives"}

    analyzer = ABTestAnalyzer(control_data, treatment_data)

    # Run all tests
    ttest = analyzer.run_ttest()
    power = analyzer.power_analysis()
    bootstrap = analyzer.bootstrap_ci(n_iterations=5000)
    sequential = analyzer.sequential_test()

    # KPIs
    kpis = {
        "control_mean": ttest["control_mean"],
        "treatment_mean": ttest["treatment_mean"],
        "effect_size": ttest["effect_size"],
        "p_value": ttest["p_value"],
        "significant": ttest["significant"],
        "is_powered": power["is_sufficiently_powered"],
    }

    # Distribution data for histogram overlay
    import numpy as np
    ctrl_hist, ctrl_edges = np.histogram(control_data.values, bins=30)
    treat_hist, treat_edges = np.histogram(treatment_data.values, bins=30)

    control_dist = [
        {"bin_start": round(float(ctrl_edges[i]), 4), "bin_end": round(float(ctrl_edges[i+1]), 4), "count": int(ctrl_hist[i])}
        for i in range(len(ctrl_hist))
    ]
    treatment_dist = [
        {"bin_start": round(float(treat_edges[i]), 4), "bin_end": round(float(treat_edges[i+1]), 4), "count": int(treat_hist[i])}
        for i in range(len(treat_hist))
    ]

    return {
        "kpis": dict_to_safe(kpis),
        "ttest": dict_to_safe(ttest),
        "power_analysis": dict_to_safe(power),
        "bootstrap": dict_to_safe(bootstrap),
        "sequential_test": dict_to_safe(sequential),
        "control_distribution": control_dist,
        "treatment_distribution": treatment_dist,
    }
