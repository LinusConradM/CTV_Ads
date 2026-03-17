"""Tests for attribution models."""

import pytest
import pandas as pd
import numpy as np
from analytics.attribution import (
    build_conversion_paths,
    last_touch_attribution,
    first_touch_attribution,
    linear_attribution,
    time_decay_attribution,
    attribution_comparison,
)


class TestBuildPaths:
    def test_paths_only_for_converters(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        # Every path should correspond to a user who converted
        converters = transformed_impressions[
            transformed_impressions["converted"] == 1
        ]["user_id_hashed"].unique()
        assert set(paths["user_id_hashed"]).issubset(set(converters))

    def test_path_length_positive(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) > 0:
            assert (paths["path_length"] >= 1).all()


class TestLastTouch:
    def test_total_credit_equals_conversions(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) == 0:
            pytest.skip("No conversion paths")
        result = last_touch_attribution(paths)
        assert abs(result["credit"].sum() - len(paths)) < 1e-6

    def test_all_credit_integer(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) == 0:
            pytest.skip("No conversion paths")
        result = last_touch_attribution(paths)
        # Each conversion gives exactly 1.0 to last touch
        assert (result["credit"] == result["credit"].astype(int)).all()


class TestFirstTouch:
    def test_total_credit_equals_conversions(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) == 0:
            pytest.skip("No conversion paths")
        result = first_touch_attribution(paths)
        assert abs(result["credit"].sum() - len(paths)) < 1e-6


class TestLinear:
    def test_total_credit_equals_conversions(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) == 0:
            pytest.skip("No conversion paths")
        result = linear_attribution(paths)
        assert abs(result["credit"].sum() - len(paths)) < 1e-6

    def test_single_touch_gets_full_credit(self):
        """A path with one touchpoint should give 100% credit."""
        paths = pd.DataFrame([{
            "user_id_hashed": "u_001",
            "path": [{"campaign_id": "camp_A", "timestamp": pd.Timestamp("2024-01-01")}],
            "path_length": 1,
            "conversion_timestamp": pd.Timestamp("2024-01-01"),
        }])
        result = linear_attribution(paths)
        assert result.loc[result["campaign_id"] == "camp_A", "credit"].values[0] == 1.0


class TestTimeDecay:
    def test_total_credit_equals_conversions(self, transformed_impressions):
        paths = build_conversion_paths(transformed_impressions)
        if len(paths) == 0:
            pytest.skip("No conversion paths")
        result = time_decay_attribution(paths)
        assert abs(result["credit"].sum() - len(paths)) < 1e-6

    def test_recent_touch_gets_more_credit(self):
        """More recent touchpoint should get more credit than older one."""
        paths = pd.DataFrame([{
            "user_id_hashed": "u_001",
            "path": [
                {"campaign_id": "camp_old", "timestamp": pd.Timestamp("2024-01-01")},
                {"campaign_id": "camp_new", "timestamp": pd.Timestamp("2024-01-10")},
            ],
            "path_length": 2,
            "conversion_timestamp": pd.Timestamp("2024-01-10"),
        }])
        result = time_decay_attribution(paths, half_life_days=7)
        old_credit = result.loc[result["campaign_id"] == "camp_old", "credit"].values[0]
        new_credit = result.loc[result["campaign_id"] == "camp_new", "credit"].values[0]
        assert new_credit > old_credit


class TestComparison:
    def test_comparison_has_all_models(self, transformed_impressions):
        result = attribution_comparison(transformed_impressions)
        if len(result) == 0:
            pytest.skip("No conversion paths")
        for col in ["last_touch", "first_touch", "linear", "time_decay"]:
            assert col in result.columns
