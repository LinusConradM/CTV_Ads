"""Tests for frequency & reach analysis."""

import pytest
import pandas as pd
from analytics.frequency_reach import (
    reach_curve,
    frequency_distribution,
    optimal_frequency,
    diminishing_returns,
    frequency_cap_recommendation,
)


class TestReachCurve:
    def test_reach_monotonic(self, transformed_impressions):
        curve = reach_curve(transformed_impressions)
        assert curve["unique_reach"].is_monotonic_increasing

    def test_reach_bounded_by_total_users(self, transformed_impressions):
        curve = reach_curve(transformed_impressions)
        total_users = transformed_impressions["user_id_hashed"].nunique()
        assert curve["unique_reach"].max() <= total_users

    def test_campaign_filter(self, transformed_impressions):
        campaign = transformed_impressions["campaign_id"].iloc[0]
        curve = reach_curve(transformed_impressions, campaign_id=campaign)
        assert len(curve) > 0


class TestFrequencyDistribution:
    def test_distribution_non_empty(self, transformed_impressions):
        dist = frequency_distribution(transformed_impressions)
        assert len(dist) > 0
        assert "user_count" in dist.columns

    def test_user_count_matches(self, transformed_impressions):
        dist = frequency_distribution(transformed_impressions)
        total_users = transformed_impressions["user_id_hashed"].nunique()
        assert dist["user_count"].sum() == total_users


class TestOptimalFrequency:
    def test_has_conversion_rate(self, transformed_impressions):
        result = optimal_frequency(transformed_impressions)
        assert "conversion_rate" in result.columns
        assert result["conversion_rate"].between(0, 1).all()


class TestDiminishingReturns:
    def test_impressions_monotonic(self, transformed_impressions):
        dr = diminishing_returns(transformed_impressions)
        assert dr["impressions"].is_monotonic_increasing

    def test_cumulative_reach_monotonic(self, transformed_impressions):
        dr = diminishing_returns(transformed_impressions)
        assert dr["cumulative_reach"].is_monotonic_increasing


class TestFrequencyCapRecommendation:
    def test_conversions_objective(self, transformed_impressions):
        rec = frequency_cap_recommendation(transformed_impressions, objective="conversions")
        assert "recommended_cap" in rec
        assert rec["recommended_cap"] is not None
        assert rec["recommended_cap"] > 0

    def test_reach_objective(self, transformed_impressions):
        rec = frequency_cap_recommendation(transformed_impressions, objective="reach")
        assert "recommended_cap" in rec
        assert rec["recommended_cap"] > 0
