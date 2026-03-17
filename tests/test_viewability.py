"""Tests for viewability engine."""

import pytest
import pandas as pd
import numpy as np
from analytics.viewability import (
    classify_viewable,
    campaign_viewability_report,
    device_viewability_breakdown,
    publisher_viewability_scorecard,
    viewability_trend,
    viewability_distribution,
)


class TestClassifyViewable:
    def test_video_viewable(self):
        row = pd.Series({"ad_format": "video", "pixels_visible_pct": 0.60, "view_duration_seconds": 3.0})
        assert classify_viewable(row) is True

    def test_video_not_viewable_pixels(self):
        row = pd.Series({"ad_format": "video", "pixels_visible_pct": 0.40, "view_duration_seconds": 3.0})
        assert classify_viewable(row) is False

    def test_video_not_viewable_duration(self):
        row = pd.Series({"ad_format": "video", "pixels_visible_pct": 0.60, "view_duration_seconds": 1.5})
        assert classify_viewable(row) is False

    def test_video_boundary_exact(self):
        row = pd.Series({"ad_format": "video", "pixels_visible_pct": 0.50, "view_duration_seconds": 2.0})
        assert classify_viewable(row) is True

    def test_display_viewable(self):
        row = pd.Series({"ad_format": "display_overlay", "pixels_visible_pct": 0.55, "view_duration_seconds": 1.5})
        assert classify_viewable(row) is True

    def test_display_boundary_exact(self):
        row = pd.Series({"ad_format": "display_overlay", "pixels_visible_pct": 0.50, "view_duration_seconds": 1.0})
        assert classify_viewable(row) is True

    def test_display_not_viewable(self):
        row = pd.Series({"ad_format": "display_overlay", "pixels_visible_pct": 0.49, "view_duration_seconds": 1.0})
        assert classify_viewable(row) is False


class TestReports:
    def test_campaign_report_has_all_campaigns(self, transformed_impressions):
        report = campaign_viewability_report(transformed_impressions)
        n_campaigns = transformed_impressions["campaign_id"].nunique()
        assert len(report) == n_campaigns

    def test_viewable_rate_bounded(self, transformed_impressions):
        report = campaign_viewability_report(transformed_impressions)
        assert report["viewable_rate"].between(0, 1).all()

    def test_device_breakdown_non_empty(self, transformed_impressions):
        breakdown = device_viewability_breakdown(transformed_impressions)
        assert len(breakdown) > 0
        assert "viewable_rate" in breakdown.columns

    def test_publisher_scorecard_ranked(self, transformed_impressions):
        scorecard = publisher_viewability_scorecard(transformed_impressions)
        assert "rank" in scorecard.columns
        assert scorecard["rank"].is_monotonic_increasing

    def test_viewability_distribution_keys(self, transformed_impressions):
        dist = viewability_distribution(transformed_impressions)
        assert "pixel_visibility" in dist
        assert "view_duration" in dist
        assert "overall_viewable_rate" in dist
        assert 0 <= dist["overall_viewable_rate"] <= 1
