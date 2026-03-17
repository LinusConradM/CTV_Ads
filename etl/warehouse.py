"""
ETL — Warehouse Module

Loads transformed impression data into DuckDB, creates dimension tables
and indexes for fast analytical queries.
"""

import logging
from pathlib import Path

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "ctv_analytics.duckdb"


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection, creating the database if needed."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def create_tables(con: duckdb.DuckDBPyConnection) -> None:
    """Create schema tables if they don't exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS impressions (
            impression_id VARCHAR PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE,
            device_type VARCHAR,
            device_brand VARCHAR,
            content_category VARCHAR,
            ad_duration_seconds INTEGER,
            ad_format VARCHAR,
            pixels_visible_pct DOUBLE,
            view_duration_seconds DOUBLE,
            bid_price_cpm DOUBLE,
            clearing_price_cpm DOUBLE,
            floor_price_cpm DOUBLE,
            user_id_hashed VARCHAR,
            campaign_id VARCHAR,
            creative_id VARCHAR,
            geo_dma VARCHAR,
            dma_name VARCHAR,
            publisher_id VARCHAR,
            placement_id VARCHAR,
            converted INTEGER,
            conversion_type VARCHAR,
            is_viewable BOOLEAN,
            view_completion_pct DOUBLE,
            bid_floor_ratio DOUBLE,
            auction_efficiency DOUBLE,
            hour_of_day INTEGER,
            day_of_week INTEGER,
            is_primetime BOOLEAN,
            is_weekend BOOLEAN,
            report_date DATE,
            user_campaign_frequency INTEGER,
            user_daily_frequency INTEGER,
            campaign_daily_impressions INTEGER,
            device_viewability_avg DOUBLE,
            publisher_quality_score DOUBLE,
            creative_completion_rate DOUBLE,
            dma_cpm_index DOUBLE
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id VARCHAR PRIMARY KEY,
            total_impressions BIGINT,
            total_spend DOUBLE,
            avg_cpm DOUBLE,
            unique_reach BIGINT,
            viewable_rate DOUBLE,
            conversion_rate DOUBLE
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS publishers (
            publisher_id VARCHAR PRIMARY KEY,
            total_impressions BIGINT,
            quality_score DOUBLE,
            avg_viewability DOUBLE,
            num_placements INTEGER
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS dmas (
            geo_dma VARCHAR PRIMARY KEY,
            dma_name VARCHAR,
            total_impressions BIGINT,
            avg_cpm DOUBLE,
            cpm_index DOUBLE
        )
    """)


def load_impressions(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    """Load transformed impression data into DuckDB."""
    df = df.copy()
    # Replace string 'nan' with proper None for nullable columns
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].replace({"nan": None, "None": None})
        df[col] = df[col].where(df[col].notna(), None)

    # Clear existing data
    con.execute("DELETE FROM impressions")

    # Reorder columns to match table schema
    table_cols = [col[0] for col in con.execute("DESCRIBE impressions").fetchall()]
    df = df[table_cols]

    # Insert from DataFrame
    con.execute("INSERT INTO impressions SELECT * FROM df")

    count = con.execute("SELECT COUNT(*) FROM impressions").fetchone()[0]
    logger.info(f"Loaded {count:,} impressions into DuckDB")
    return count


def build_dimension_tables(con: duckdb.DuckDBPyConnection) -> None:
    """Populate dimension tables from impressions fact table."""
    con.execute("DELETE FROM campaigns")
    con.execute("""
        INSERT INTO campaigns
        SELECT
            campaign_id,
            COUNT(*) as total_impressions,
            SUM(clearing_price_cpm) / 1000.0 as total_spend,
            AVG(clearing_price_cpm) as avg_cpm,
            COUNT(DISTINCT user_id_hashed) as unique_reach,
            AVG(CASE WHEN is_viewable THEN 1.0 ELSE 0.0 END) as viewable_rate,
            AVG(converted) as conversion_rate
        FROM impressions
        GROUP BY campaign_id
    """)

    con.execute("DELETE FROM publishers")
    con.execute("""
        INSERT INTO publishers
        SELECT
            publisher_id,
            COUNT(*) as total_impressions,
            AVG(publisher_quality_score) as quality_score,
            AVG(pixels_visible_pct) as avg_viewability,
            COUNT(DISTINCT placement_id) as num_placements
        FROM impressions
        GROUP BY publisher_id
    """)

    con.execute("DELETE FROM dmas")
    con.execute("""
        INSERT INTO dmas
        SELECT
            geo_dma,
            MAX(dma_name) as dma_name,
            COUNT(*) as total_impressions,
            AVG(clearing_price_cpm) as avg_cpm,
            AVG(dma_cpm_index) as cpm_index
        FROM impressions
        GROUP BY geo_dma
    """)

    logger.info("Dimension tables built")


def create_indexes(con: duckdb.DuckDBPyConnection) -> None:
    """Create indexes for common query patterns."""
    # DuckDB auto-indexes PRIMARY KEY, but we add extras for common filters
    con.execute("CREATE INDEX IF NOT EXISTS idx_campaign ON impressions(campaign_id)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON impressions(timestamp)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_user ON impressions(user_id_hashed)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_report_date ON impressions(report_date)")
    logger.info("Indexes created")


def load_warehouse(df: pd.DataFrame, db_path: str | Path = DEFAULT_DB_PATH) -> duckdb.DuckDBPyConnection:
    """Full warehouse loading pipeline."""
    con = get_connection(db_path)
    create_tables(con)
    load_impressions(con, df)
    build_dimension_tables(con)
    create_indexes(con)
    return con


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from pathlib import Path
    from etl.ingest import ingest
    from etl.clean import clean
    from etl.transform import transform

    raw_path = Path(__file__).parent.parent / "data" / "raw" / "impressions.csv"
    df = ingest(raw_path)
    df = clean(df)
    df = transform(df)

    con = load_warehouse(df)

    # Verify
    print("\n--- Warehouse Verification ---")
    print(con.execute("SELECT COUNT(*) as rows FROM impressions").fetchdf())
    print(con.execute("SELECT campaign_id, total_impressions, viewable_rate FROM campaigns LIMIT 5").fetchdf())
    print(con.execute("SELECT device_type, AVG(pixels_visible_pct) as avg_viewability FROM impressions GROUP BY device_type").fetchdf())
    con.close()
