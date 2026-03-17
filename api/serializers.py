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
    """Convert DataFrame to list of dicts with JSON-safe types."""
    records = df.to_dict(orient="records")
    return [
        {k: _convert_value(v) for k, v in record.items()}
        for record in records
    ]


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
