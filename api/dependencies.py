"""
API — Shared Dependencies

Data loading, DuckDB connection management, filter application, and response caching.
"""

import hashlib
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Callable

import duckdb
import pandas as pd
from fastapi import Query

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "ctv_analytics.duckdb"
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "impressions.csv"

# Module-level cache for the full DataFrame
_df_cache: pd.DataFrame | None = None

# Module-level cache for computed API responses (data is static per session)
_result_cache: dict[str, Any] = {}


def cache_key(route: str, **params) -> str:
    """Create a hashable cache key from route name and parameters."""
    key_data = {"route": route}
    for k, v in sorted(params.items()):
        if v is None:
            key_data[k] = None
        elif isinstance(v, list):
            key_data[k] = tuple(v)
        elif isinstance(v, date):
            key_data[k] = v.isoformat()
        else:
            key_data[k] = v
    return hashlib.md5(json.dumps(key_data, default=str).encode()).hexdigest()


def get_or_compute(key: str, compute_fn: Callable) -> Any:
    """Return cached result or compute and cache it."""
    if key not in _result_cache:
        logger.info(f"Cache miss for {key[:12]}..., computing...")
        _result_cache[key] = compute_fn()
    else:
        logger.info(f"Cache hit for {key[:12]}...")
    return _result_cache[key]


def _load_from_duckdb() -> pd.DataFrame:
    """Load impressions from DuckDB warehouse."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM impressions").fetchdf()
    con.close()
    return df


def _load_from_csv() -> pd.DataFrame:
    """Fallback: load from CSV and run ETL pipeline."""
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))
    from etl.ingest import ingest
    from etl.clean import clean
    from etl.transform import transform

    df = ingest(CSV_PATH)
    df = clean(df)
    df = transform(df)
    return df


def get_full_df() -> pd.DataFrame:
    """Get the full impressions DataFrame, loading once and caching."""
    global _df_cache
    if _df_cache is None:
        if DB_PATH.exists():
            logger.info("Loading data from DuckDB...")
            _df_cache = _load_from_duckdb()
        elif CSV_PATH.exists():
            logger.info("DuckDB not found, loading from CSV pipeline...")
            _df_cache = _load_from_csv()
        else:
            raise FileNotFoundError(
                f"No data source found. Expected DuckDB at {DB_PATH} or CSV at {CSV_PATH}. "
                "Run: python data/generator/ctv_simulator.py"
            )
        # Ensure report_date is a date type
        if "report_date" in _df_cache.columns:
            _df_cache["report_date"] = pd.to_datetime(_df_cache["report_date"]).dt.date
        logger.info(f"Loaded {len(_df_cache):,} impressions")
    return _df_cache


def apply_filters(
    df: pd.DataFrame,
    start_date: date | None = None,
    end_date: date | None = None,
    campaigns: list[str] | None = None,
    device_types: list[str] | None = None,
) -> pd.DataFrame:
    """Apply date range, campaign, and device filters."""
    mask = pd.Series(True, index=df.index)

    if start_date:
        mask &= df["report_date"] >= start_date
    if end_date:
        mask &= df["report_date"] <= end_date
    if campaigns:
        mask &= df["campaign_id"].isin(campaigns)
    if device_types:
        mask &= df["device_type"].isin(device_types)

    return df[mask]
