"""Tests for ETL modules: ingest, clean, transform."""

import pytest
import pandas as pd
import numpy as np


class TestIngest:
    def test_validate_schema_passes(self, sample_impressions):
        from etl.ingest import validate_schema
        result = validate_schema(sample_impressions)
        assert len(result) == len(sample_impressions)

    def test_validate_schema_fails_missing_col(self, sample_impressions):
        from etl.ingest import validate_schema
        df = sample_impressions.drop(columns=["impression_id"])
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_schema(df)

    def test_validate_values_drops_invalid_pixels(self, sample_impressions):
        from etl.ingest import enforce_dtypes, validate_values
        df = sample_impressions.copy()
        df.loc[0, "pixels_visible_pct"] = 1.5  # Invalid
        df.loc[1, "pixels_visible_pct"] = -0.1  # Invalid
        df = enforce_dtypes(df)
        result = validate_values(df)
        assert 0 not in result.index or result.loc[0, "pixels_visible_pct"] <= 1.0

    def test_validate_values_drops_null_required(self, sample_impressions):
        from etl.ingest import enforce_dtypes, validate_values
        df = sample_impressions.copy()
        df.loc[0, "impression_id"] = None
        df = enforce_dtypes(df)
        result = validate_values(df)
        assert len(result) < len(df)


class TestClean:
    def test_deduplicate(self, sample_impressions):
        from etl.clean import deduplicate
        df = pd.concat([sample_impressions, sample_impressions.head(5)])
        result = deduplicate(df)
        assert len(result) == len(sample_impressions)
        assert result["impression_id"].is_unique

    def test_normalize_timestamps(self, sample_impressions):
        from etl.clean import normalize_timestamps
        result = normalize_timestamps(sample_impressions)
        assert result["timestamp"].dt.tz is not None

    def test_standardize_strings(self, sample_impressions):
        from etl.clean import standardize_strings
        df = sample_impressions.copy()
        df.loc[0, "device_type"] = "  Smart_TV  "
        result = standardize_strings(df)
        assert result.loc[0, "device_type"] == "smart_tv"

    def test_map_dma_names(self, sample_impressions):
        from etl.clean import map_dma_names
        result = map_dma_names(sample_impressions)
        assert "dma_name" in result.columns
        assert result.loc[result["geo_dma"] == "501", "dma_name"].iloc[0] == "New York"


class TestTransform:
    def test_viewability_classification(self, transformed_impressions):
        df = transformed_impressions
        assert "is_viewable" in df.columns
        assert df["is_viewable"].dtype == bool

    def test_viewable_video_threshold(self):
        """Video: 50% pixels, 2 seconds."""
        from etl.transform import classify_viewable
        row = pd.Series({
            "ad_format": "video",
            "pixels_visible_pct": 0.50,
            "view_duration_seconds": 2.0,
        })
        assert classify_viewable(row) is True

        row["pixels_visible_pct"] = 0.49
        assert classify_viewable(row) is False

        row["pixels_visible_pct"] = 0.50
        row["view_duration_seconds"] = 1.9
        assert classify_viewable(row) is False

    def test_viewable_display_threshold(self):
        """Display: 50% pixels, 1 second."""
        from etl.transform import classify_viewable
        row = pd.Series({
            "ad_format": "display_overlay",
            "pixels_visible_pct": 0.50,
            "view_duration_seconds": 1.0,
        })
        assert classify_viewable(row) is True

        row["view_duration_seconds"] = 0.9
        assert classify_viewable(row) is False

    def test_completion_pct_bounded(self, transformed_impressions):
        df = transformed_impressions
        assert df["view_completion_pct"].between(0, 1).all()

    def test_temporal_features(self, transformed_impressions):
        df = transformed_impressions
        assert df["hour_of_day"].between(0, 23).all()
        assert df["day_of_week"].between(0, 6).all()
        assert df["is_primetime"].dtype == bool
        assert df["is_weekend"].dtype == bool

    def test_frequency_features_positive(self, transformed_impressions):
        df = transformed_impressions
        assert (df["user_campaign_frequency"] >= 1).all()
        assert (df["user_daily_frequency"] >= 1).all()

    def test_all_features_present(self, transformed_impressions):
        expected = [
            "is_viewable", "view_completion_pct", "bid_floor_ratio",
            "auction_efficiency", "hour_of_day", "day_of_week",
            "is_primetime", "is_weekend", "user_campaign_frequency",
            "user_daily_frequency", "campaign_daily_impressions",
            "device_viewability_avg", "publisher_quality_score",
            "creative_completion_rate", "dma_cpm_index",
        ]
        for col in expected:
            assert col in transformed_impressions.columns, f"Missing: {col}"
