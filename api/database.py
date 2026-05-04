# api/database.py

import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from api.config import get_settings
import time

settings = get_settings()

# ── Connection Pool ───────────────────────────────────
# Creates 5 connections upfront — reuses them
# Much faster than creating new connection per request
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Test connection before using
)

def run_query(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Execute SQL and return DataFrame.
    All KPI queries go through this function.
    """
    with engine.connect() as conn:
        result = pd.read_sql(
            text(sql),
            conn,
            params=params or {}
        )
    return result

def safe_float(value) -> float:
    """
    Convert to float safely.
    Handles NaN, None, numpy types.
    JSON cannot serialize NaN — must convert to None.
    """
    import math
    import numpy as np

    if value is None:
        return None
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 2)
    except (TypeError, ValueError):
        return None

def df_to_records(df: pd.DataFrame) -> list:
    """
    Convert DataFrame to list of JSON-safe dicts.
    Handles all numpy/pandas types automatically.
    """
    import numpy as np

    records = []
    for _, row in df.iterrows():
        clean_row = {}
        for col, val in row.items():
            if pd.isna(val) if not isinstance(
                val, (list, dict)
            ) else False:
                clean_row[col] = None
            elif isinstance(val, (np.integer,)):
                clean_row[col] = int(val)
            elif isinstance(val, (np.floating,)):
                clean_row[col] = safe_float(val)
            elif isinstance(val, pd.Timestamp):
                clean_row[col] = str(val.date())
            else:
                clean_row[col] = val
        records.append(clean_row)
    return records