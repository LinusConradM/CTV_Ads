# CTV Ad Intelligence Platform

## Project Overview
End-to-end CTV and programmatic advertising analytics platform that ingests impression-level ad event data, applies IAB-standard measurement frameworks, and delivers campaign performance insights through a Streamlit dashboard.

## Tech Stack
- **Language:** Python 3.11+
- **Dashboard:** Streamlit 1.32+
- **Database:** DuckDB (local), Snowflake (cloud, optional)
- **Data Modeling:** dbt-core 1.7+
- **ML/Analytics:** scikit-learn, scipy, statsmodels
- **Visualization:** Plotly 5.18+
- **Testing:** pytest, hypothesis

## Project Structure
```
ctv-ad-intelligence/
├── data/
│   ├── raw/                  # Raw datasets (gitignored)
│   ├── processed/            # Cleaned data
│   ├── marts/                # Analytics-ready tables
│   └── generator/
│       └── ctv_simulator.py  # Synthetic CTV data generator
├── etl/
│   ├── ingest.py             # Raw data loading and validation
│   ├── clean.py              # Deduplication, type normalization
│   ├── transform.py          # Feature engineering
│   └── warehouse.py          # DuckDB / Snowflake connector
├── dbt/                      # dbt models (staging → intermediate → marts)
├── analytics/
│   ├── viewability.py        # IAB viewability measurement
│   ├── segmentation.py       # K-Means audience segmentation
│   ├── anomaly_detection.py  # Isolation Forest monitoring
│   ├── attribution.py        # Multi-touch attribution models
│   ├── ab_testing.py         # A/B test design and analysis
│   └── frequency_reach.py    # Frequency distribution & reach curves
├── dashboard/
│   ├── app.py                # Streamlit main app
│   ├── pages/                # 7 dashboard pages
│   └── components/           # Reusable UI components
├── tests/
├── skills/
└── ProjectPlanning Docs/
```

## Build Phases
1. **Foundation** — Data pipeline + DuckDB (ctv_simulator, ETL, warehouse)
2. **Analytics Modules** — Viewability, segmentation, anomaly detection, attribution, A/B testing
3. **Dashboard** — 7 Streamlit pages with KPI cards and filters
4. **dbt/Snowflake** — Staging → intermediate → mart models (optional)

## Key Standards
- **Viewability:** IAB MRC standard — 50% pixels visible, 2s for video, 1s for display
- **Pricing:** CPM (cost per 1,000 impressions) as primary unit
- **Attribution:** Support last-touch, first-touch, linear, time-decay, and Shapley
- **Anomaly Detection:** Isolation Forest (unsupervised, continuous scoring)
- **Segmentation:** K-Means with elbow curve for optimal K selection

## Conventions
- Use `data/raw/` for downloaded datasets — always gitignored
- Use DuckDB for local development, Snowflake for cloud layer
- All analytics modules should have corresponding pytest tests
- Feature engineering happens in `etl/transform.py`, not in analytics modules
- Dashboard pages follow `0X_page_name.py` naming convention
