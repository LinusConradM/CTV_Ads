"""Shared pytest fixtures for CTV Ad Intelligence tests."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_impressions():
    """Small deterministic impression dataset for testing."""
    rng = np.random.default_rng(42)
    n = 1000

    timestamps = pd.date_range("2024-03-01", periods=n, freq="5min", tz="UTC")

    df = pd.DataFrame({
        "impression_id": [f"imp_{i:04d}" for i in range(n)],
        "timestamp": timestamps,
        "device_type": rng.choice(["smart_tv", "mobile", "desktop", "tablet"], n, p=[0.45, 0.25, 0.2, 0.1]),
        "device_brand": rng.choice(["LG", "Samsung", "Apple", "Roku"], n),
        "content_category": rng.choice(["news", "sports", "entertainment", "drama", "kids"], n),
        "ad_duration_seconds": rng.choice([15, 30, 60], n, p=[0.3, 0.5, 0.2]),
        "ad_format": rng.choice(["video", "display_overlay"], n, p=[0.85, 0.15]),
        "pixels_visible_pct": rng.beta(6, 2, n).round(4),
        "view_duration_seconds": rng.uniform(0, 30, n).round(1),
        "bid_price_cpm": rng.uniform(5, 35, n).round(2),
        "clearing_price_cpm": rng.uniform(3, 25, n).round(2),
        "floor_price_cpm": rng.uniform(1, 15, n).round(2),
        "user_id_hashed": [f"u_{rng.integers(0, 200):04d}" for _ in range(n)],
        "campaign_id": rng.choice([f"camp_{i:03d}" for i in range(1, 6)], n),
        "creative_id": rng.choice(["cr_A", "cr_B", "cr_C"], n),
        "geo_dma": rng.choice(["501", "803", "602"], n),
        "publisher_id": rng.choice([f"pub_{i:03d}" for i in range(1, 6)], n),
        "placement_id": rng.choice(["pl_1", "pl_2", "pl_3"], n),
        "converted": rng.choice([0, 1], n, p=[0.93, 0.07]),
        "conversion_type": [None] * n,
    })

    # Set conversion_type for converted rows
    converted_mask = df["converted"] == 1
    df.loc[converted_mask, "conversion_type"] = rng.choice(
        ["app_install", "web_visit", "store_visit"],
        converted_mask.sum()
    )

    return df


@pytest.fixture
def transformed_impressions(sample_impressions):
    """Sample impressions with all transform features applied."""
    from etl.transform import transform
    from etl.clean import clean
    df = clean(sample_impressions)
    return transform(df)
