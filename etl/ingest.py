"""
ETL — Ingestion Module

Loads raw CSV impression data, validates schema, enforces dtypes,
and rejects malformed rows with logging.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "impression_id", "timestamp", "device_type", "device_brand",
    "content_category", "ad_duration_seconds", "ad_format",
    "pixels_visible_pct", "view_duration_seconds",
    "bid_price_cpm", "clearing_price_cpm", "floor_price_cpm",
    "user_id_hashed", "campaign_id", "creative_id",
    "geo_dma", "publisher_id", "placement_id",
    "converted", "conversion_type",
]

NON_NULL_COLUMNS = [
    "impression_id", "timestamp", "device_type", "campaign_id",
    "user_id_hashed", "ad_format", "ad_duration_seconds",
]

DTYPE_MAP = {
    "impression_id": str,
    "device_type": str,
    "device_brand": str,
    "content_category": str,
    "ad_duration_seconds": int,
    "ad_format": str,
    "pixels_visible_pct": float,
    "view_duration_seconds": float,
    "bid_price_cpm": float,
    "clearing_price_cpm": float,
    "floor_price_cpm": float,
    "user_id_hashed": str,
    "campaign_id": str,
    "creative_id": str,
    "geo_dma": str,
    "publisher_id": str,
    "placement_id": str,
    "converted": int,
    "conversion_type": str,
}


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Check that all required columns are present."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def enforce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to expected dtypes."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for col, dtype in DTYPE_MAP.items():
        if col in df.columns:
            if dtype == str:
                df[col] = df[col].astype(str)
            elif dtype == float:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif dtype == int:
                df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def validate_values(df: pd.DataFrame) -> pd.DataFrame:
    """Apply value-level validation rules. Drop invalid rows with logging."""
    n_before = len(df)

    # Drop rows with null required fields
    df = df.dropna(subset=NON_NULL_COLUMNS)

    # pixels_visible_pct must be in [0, 1]
    mask = df["pixels_visible_pct"].between(0.0, 1.0)
    df = df[mask]

    # Prices must be positive
    for col in ["bid_price_cpm", "clearing_price_cpm"]:
        df = df[df[col] > 0]

    # clearing_price <= bid_price
    df = df[df["clearing_price_cpm"] <= df["bid_price_cpm"]]

    # Timestamp must not be NaT
    df = df[df["timestamp"].notna()]

    n_dropped = n_before - len(df)
    if n_dropped > 0:
        logger.warning(f"Dropped {n_dropped:,} invalid rows during validation")

    return df.reset_index(drop=True)


def ingest(filepath: str | Path) -> pd.DataFrame:
    """Load, validate, and return a raw impression DataFrame."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    logger.info(f"Loading data from {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    logger.info(f"Loaded {len(df):,} rows")

    df = validate_schema(df)
    df = enforce_dtypes(df)
    df = validate_values(df)

    logger.info(f"Ingestion complete: {len(df):,} valid rows")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "impressions.csv"
    df = ingest(raw_path)
    print(f"Ingested {len(df):,} rows")
    print(df.dtypes)
