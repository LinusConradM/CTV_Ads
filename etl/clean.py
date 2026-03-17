"""
ETL — Cleaning Module

Deduplicates records, normalizes timestamps, standardizes string fields,
and maps DMA codes to human-readable names.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

DMA_NAMES = {
    "501": "New York", "803": "Los Angeles", "602": "Chicago",
    "504": "Philadelphia", "511": "Washington DC", "525": "Houston",
    "506": "Boston", "623": "Dallas-Ft. Worth", "524": "Atlanta",
    "753": "Phoenix", "807": "San Francisco", "819": "Seattle",
    "539": "Tampa", "505": "Detroit", "527": "Indianapolis",
    "528": "Miami", "613": "Minneapolis", "641": "San Antonio",
    "510": "Cleveland", "561": "Jacksonville",
    "512": "Baltimore", "820": "Portland OR", "751": "Denver",
    "534": "Orlando", "662": "Abilene-Sweetwater", "617": "Milwaukee",
    "659": "Nashville", "618": "Charlotte", "648": "Champaign",
    "532": "Albany-Schenectady",
}


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate impression_ids, keeping first occurrence."""
    n_before = len(df)
    df = df.drop_duplicates(subset="impression_id", keep="first")
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        logger.info(f"Removed {n_dropped:,} duplicate impression_ids")
    return df


def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure timestamps are UTC-aware datetime."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def standardize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and standardize capitalization on key fields."""
    df = df.copy()
    string_cols = ["device_type", "content_category", "ad_format"]
    for col in string_cols:
        df[col] = df[col].str.strip().str.lower()

    # Device brand: title case
    df["device_brand"] = df["device_brand"].str.strip().str.title()
    return df


def map_dma_names(df: pd.DataFrame) -> pd.DataFrame:
    """Add human-readable DMA name column."""
    df = df.copy()
    df["geo_dma"] = df["geo_dma"].astype(str)
    df["dma_name"] = df["geo_dma"].map(DMA_NAMES).fillna("Unknown")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Run full cleaning pipeline."""
    n_before = len(df)
    logger.info(f"Cleaning {n_before:,} rows")

    df = deduplicate(df)
    df = normalize_timestamps(df)
    df = standardize_strings(df)
    df = map_dma_names(df)

    df = df.reset_index(drop=True)
    logger.info(f"Cleaning complete: {len(df):,} rows retained")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from etl.ingest import ingest
    from pathlib import Path

    raw_path = Path(__file__).parent.parent / "data" / "raw" / "impressions.csv"
    df = ingest(raw_path)
    df = clean(df)
    print(f"Cleaned: {len(df):,} rows")
    print(df[["timestamp", "device_type", "device_brand", "dma_name"]].head())
