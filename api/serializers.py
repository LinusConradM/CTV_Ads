"""
API — Serialization Utilities

Handles DataFrame → JSON conversion with proper type handling for
numpy types, NaN values, and date objects.
"""

import math
from datetime import date, datetime

import numpy as np
import pandas as pd


def _convert_value(v):
    """Convert a single value to JSON-safe Python type."""
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        if np.isnan(v) or np.isinf(v):
            return None
        return float(v)
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    return v


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts with JSON-safe types.

    Uses column-level vectorized conversion instead of per-cell iteration.
    """
    df = df.copy()
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_bool_dtype(dtype):
            df[col] = df[col].astype(object).where(df[col].notna(), None)
        elif pd.api.types.is_integer_dtype(dtype):
            df[col] = df[col].astype(object).where(df[col].notna(), None)
        elif pd.api.types.is_float_dtype(dtype):
            mask = df[col].notna() & ~np.isinf(df[col])
            df[col] = df[col].where(mask, None)
            # Convert remaining numpy floats to Python floats
            df.loc[mask, col] = df.loc[mask, col].astype(float)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            df[col] = df[col].astype(str).where(df[col].notna(), None)
        elif dtype == object:
            # Handle mixed object columns (may contain numpy types)
            df[col] = df[col].where(df[col].notna(), None)
    return df.to_dict(orient="records")


def dict_to_safe(d: dict) -> dict:
    """Recursively convert dict values to JSON-safe types."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = dict_to_safe(v)
        elif isinstance(v, (list, tuple)):
            result[k] = [_convert_value(item) if not isinstance(item, dict) else dict_to_safe(item) for item in v]
        else:
            result[k] = _convert_value(v)
    return result
