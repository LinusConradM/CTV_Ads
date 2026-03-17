# CTV Ad Intelligence Platform
### End-to-End Connected TV Advertising Analytics

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![dbt](https://img.shields.io/badge/dbt-1.7+-orange.svg)](https://getdbt.com)

A production-grade CTV and programmatic advertising analytics platform that ingests impression-level ad event data, applies IAB-standard measurement frameworks, and delivers actionable campaign performance insights through an interactive executive dashboard.

Built to demonstrate end-to-end ad tech analytics competency across impression delivery, viewability measurement, audience segmentation, anomaly detection, attribution modeling, and A/B experimentation.

> **Live demo:** [ctv-ad-intelligence.streamlit.app](https://streamlit.app) *(deploy after building)*
> **Portfolio context:** [conradlinusmuhirwe.netlify.app](https://conradlinusmuhirwe.netlify.app)

---

## Table of Contents

- [Why This Project](#why-this-project)
- [Ad Tech Concepts Demonstrated](#ad-tech-concepts-demonstrated)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Dashboard Modules](#dashboard-modules)
- [Technical Implementation](#technical-implementation)
- [Setup & Installation](#setup--installation)
- [Key Findings](#key-findings)
- [Roadmap](#roadmap)

---

## Why This Project

Connected TV (CTV) advertising is one of the fastest-growing segments of digital media. LG Smart TVs alone reach 200M+ households globally. The measurement and analytics challenges in CTV — viewability, frequency capping, cross-screen attribution, and impression quality — are fundamentally different from desktop or mobile advertising.

This platform simulates the core analytics infrastructure that powers ad intelligence teams at companies like LG Ad Solutions, Spotify, Reddit, and Viant/IRIS.TV:

- **Impression pipelines** that process millions of ad events daily
- **IAB-standard viewability** measurement at the campaign level
- **Audience segmentation** using unsupervised ML to identify high-value cohorts
- **Anomaly detection** to flag delivery issues, bot traffic, and pacing problems
- **Attribution modeling** comparing last-touch, linear, and time-decay methodologies
- **A/B experimentation** framework for creative and targeting variant testing

---

## Ad Tech Concepts Demonstrated

| Concept | Implementation | Industry Standard |
|---|---|---|
| Impressions | Event-level ad delivery records | IAB definition |
| Viewability | 50% pixels visible for 2+ seconds | IAB/MRC standard |
| CPM | Cost per 1,000 impressions | Primary pricing unit |
| eCPM | Effective CPM including all fees | Programmatic metric |
| Frequency capping | Max impressions per user per period | Campaign management |
| Reach | Unique devices/users exposed | Audience measurement |
| RTB / Programmatic | Simulated auction clearing prices | Demand-side buying |
| Attribution | Multi-touch conversion credit | Measurement methodology |
| Incrementality | Causal lift from ad exposure | Experimental measurement |
| ACR Data | Automatic Content Recognition signals | CTV-specific targeting |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Impression  │  │  Conversion  │  │   Audience / Device  │  │
│  │  Event Data  │  │  Event Data  │  │     Profile Data     │  │
│  │  (CSV/JSON)  │  │  (CSV/JSON)  │  │      (CSV/JSON)      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         └─────────────────┼──────────────────────┘             │
│                           ▼                                     │
│                   ┌───────────────┐                             │
│                   │  ETL Pipeline │                             │
│                   │  (Python /    │                             │
│                   │   pandas)     │                             │
│                   └───────┬───────┘                             │
└───────────────────────────┼─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE LAYER                         │
│                                                                 │
│         ┌─────────────────────────────────────────┐            │
│         │         DuckDB / Snowflake               │            │
│         │                                         │            │
│         │  ┌────────────┐   ┌─────────────────┐  │            │
│         │  │  Raw Layer │   │  Staging Layer  │  │            │
│         │  │  (Bronze)  │──▶│   (Silver)      │  │            │
│         │  └────────────┘   └────────┬────────┘  │            │
│         │                            ▼            │            │
│         │               ┌────────────────────┐   │            │
│         │               │   Mart Layer       │   │            │
│         │               │   (Gold — dbt)     │   │            │
│         │               └────────────────────┘   │            │
│         └─────────────────────────────────────────┘            │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYER                              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Viewability │  │  Audience   │  │   Anomaly Detection     │ │
│  │ Engine      │  │  Segmenter  │  │   (Isolation Forest)    │ │
│  │ (IAB rules) │  │  (K-Means)  │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Attribution │  │    A/B      │  │   Frequency & Reach     │ │
│  │ Models      │  │ Test Engine │  │   Analytics             │ │
│  │ (MTA, etc.) │  │ (DiD/Stats) │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                                                                 │
│         ┌───────────────────────────────────────┐              │
│         │    Streamlit Executive Dashboard       │              │
│         │                                       │              │
│         │  • Campaign Performance Overview      │              │
│         │  • Viewability & Delivery Health      │              │
│         │  • Audience Segmentation              │              │
│         │  • Anomaly Detection Alerts           │              │
│         │  • Attribution Comparison             │              │
│         │  • A/B Test Results                   │              │
│         │  • Frequency & Reach Curves           │              │
│         └───────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Sources

### Primary Dataset: Criteo Display Advertising Dataset
- **Source:** https://www.kaggle.com/c/criteo-display-ad-challenge/data
- **Size:** 45M+ impression records with click labels
- **Features:** 13 numerical + 26 categorical ad features
- **Use:** Impression pipeline, CTR prediction, anomaly detection

### Secondary Dataset: Avazu CTR Prediction Dataset
- **Source:** https://www.kaggle.com/c/avazu-ctr-prediction/data
- **Size:** 40M impression records
- **Features:** device type, banner position, site category, app category, hour
- **Use:** Frequency analysis, audience segmentation, reach curves

### Synthetic CTV-Specific Data (Generated)
The project includes a `data/generator/ctv_simulator.py` script that synthesizes realistic CTV ad event data including:
- **Device types:** Smart TV (LG, Samsung, Roku, Apple TV, Fire TV)
- **Content categories:** News, Sports, Entertainment, Drama, Kids
- **Ad formats:** 15s, 30s, 60s video; display overlay
- **Viewability signals:** Pixel visibility %, duration watched, completion rate
- **Auction data:** Bid price, clearing price, floor price, auction type
- **Conversion events:** App install, web visit, store visit (simulated)

```python
# Example synthetic record
{
    "impression_id": "imp_a3f9b2c1",
    "timestamp": "2024-03-15T14:32:11Z",
    "device_type": "smart_tv",
    "device_brand": "LG",
    "content_category": "sports",
    "ad_duration_seconds": 30,
    "pixels_visible_pct": 0.87,
    "view_duration_seconds": 28.4,
    "bid_price_cpm": 12.50,
    "clearing_price_cpm": 9.75,
    "user_id_hashed": "u_7f3a9e2b",
    "campaign_id": "camp_001",
    "creative_id": "cr_A",
    "geo_dma": "501",  # New York DMA
    "converted": 0
}
```

### Reference Data
- **IAB Content Taxonomy 3.0:** Content category mapping
- **Nielsen DMA Codes:** Geographic market definitions
- **IAB Viewability Standards:** Measurement benchmarks

---

## Project Structure

```
ctv-ad-intelligence/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   ├── raw/                    # Raw downloaded datasets (gitignored)
│   ├── processed/              # Cleaned, typed, deduplicated
│   ├── marts/                  # Analytics-ready tables
│   └── generator/
│       └── ctv_simulator.py    # Synthetic CTV data generator
│
├── etl/
│   ├── __init__.py
│   ├── ingest.py               # Raw data loading and validation
│   ├── clean.py                # Type normalization, deduplication
│   ├── transform.py            # Feature engineering pipeline
│   └── warehouse.py            # DuckDB / Snowflake connector
│
├── dbt/                        # dbt project (optional Snowflake layer)
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_impressions.sql
│   │   │   ├── stg_conversions.sql
│   │   │   └── stg_audiences.sql
│   │   ├── intermediate/
│   │   │   ├── int_campaign_metrics.sql
│   │   │   └── int_user_frequency.sql
│   │   └── marts/
│   │       ├── mart_campaign_performance.sql
│   │       ├── mart_viewability.sql
│   │       └── mart_attribution.sql
│   └── tests/
│       └── schema.yml
│
├── analytics/
│   ├── __init__.py
│   ├── viewability.py          # IAB viewability measurement engine
│   ├── segmentation.py         # K-Means audience segmentation
│   ├── anomaly_detection.py    # Isolation Forest delivery monitoring
│   ├── attribution.py          # Multi-touch attribution models
│   ├── ab_testing.py           # A/B test design and analysis
│   └── frequency_reach.py      # Frequency distribution & reach curves
│
├── dashboard/
│   ├── app.py                  # Streamlit main application
│   ├── pages/
│   │   ├── 01_campaign_overview.py
│   │   ├── 02_viewability_health.py
│   │   ├── 03_audience_segments.py
│   │   ├── 04_anomaly_alerts.py
│   │   ├── 05_attribution.py
│   │   ├── 06_ab_testing.py
│   │   └── 07_frequency_reach.py
│   └── components/
│       ├── kpi_cards.py
│       ├── charts.py
│       └── filters.py
│
└── tests/
    ├── test_etl.py
    ├── test_viewability.py
    ├── test_attribution.py
    └── test_ab_testing.py
```

---

## Dashboard Modules

### Module 1 — Campaign Performance Overview
**What it shows:** Top-level KPIs across all active campaigns
- Total impressions served, unique reach, average frequency
- CPM trends over time (line chart with anomaly overlays)
- eCPM by device type, content category, and geography
- Delivery pacing vs. booked inventory (over/under delivery alerts)
- CTR and completion rate by creative and placement

**Key metrics defined:**
```
Impressions         = Count of ad events served
Reach               = Count of unique user_id_hashed values
Frequency           = Impressions / Reach
CPM                 = (Total Spend / Impressions) × 1,000
eCPM                = (Total Revenue / Impressions) × 1,000
Completion Rate     = Impressions where view_pct >= 1.0 / Total Impressions
Viewable Rate       = Viewable Impressions / Total Impressions
```

---

### Module 2 — Viewability & Delivery Health
**What it shows:** IAB-standard viewability measurement
- Viewable impression rate by campaign, placement, and device
- Distribution of pixel visibility percentage and view duration
- IAB viewability threshold compliance (50% pixels / 2 seconds for display; 50% pixels / 2 seconds continuous for video)
- Viewability trend over time with statistical control limits
- Below-threshold impressions flagged for publisher review

**Implementation:**
```python
# analytics/viewability.py

IAB_DISPLAY_PIXEL_THRESHOLD = 0.50   # 50% of pixels visible
IAB_DISPLAY_TIME_THRESHOLD  = 1.0    # 1 continuous second
IAB_VIDEO_PIXEL_THRESHOLD   = 0.50   # 50% of pixels visible
IAB_VIDEO_TIME_THRESHOLD    = 2.0    # 2 continuous seconds

def classify_viewable(row):
    if row["ad_format"] == "video":
        return (row["pixels_visible_pct"] >= IAB_VIDEO_PIXEL_THRESHOLD and
                row["view_duration_seconds"] >= IAB_VIDEO_TIME_THRESHOLD)
    return (row["pixels_visible_pct"] >= IAB_DISPLAY_PIXEL_THRESHOLD and
            row["view_duration_seconds"] >= IAB_DISPLAY_TIME_THRESHOLD)
```

---

### Module 3 — Audience Segmentation
**What it shows:** K-Means clustering of advertiser audiences
- Elbow curve for optimal K selection
- Segment profiles: device affinity, content preference, viewing time, engagement
- Reach and CPM efficiency by segment
- Segment overlap visualization (PCA 2D projection)
- Recommended targeting strategies per segment

**Features used for clustering:**
```python
clustering_features = [
    "avg_view_duration_pct",    # Engagement depth
    "avg_daily_sessions",       # Frequency of platform use
    "content_category_entropy", # Content diversity
    "primetime_pct",            # Viewing time pattern
    "device_brand_encoded",     # Device ecosystem
    "geo_dma_encoded",          # Geographic market
    "completion_rate",          # Ad receptivity signal
]
```

---

### Module 4 — Anomaly Detection & Alerts
**What it shows:** Isolation Forest monitoring of delivery health
- Real-time anomaly scoring on impression volume, CPM, and viewability
- Flagged campaigns with anomalous delivery patterns
- Bot traffic indicators (unusually high frequency, zero view duration)
- Inventory quality alerts by publisher/placement
- Time-series control charts with 3-sigma bounds

**Why this matters in production:**
Ad fraud, delivery bugs, and inventory quality issues cost advertisers billions annually. This module demonstrates you understand how to build the monitoring layer that catches these issues before they hit billing.

---

### Module 5 — Attribution Modeling
**What it shows:** Side-by-side comparison of attribution methodologies
- **Last-touch:** 100% credit to final impression before conversion
- **First-touch:** 100% credit to first impression in path
- **Linear:** Equal credit distributed across all touchpoints
- **Time-decay:** Exponentially higher credit for recent touches
- **Data-driven (Shapley):** Game-theoretic credit allocation

**Output:** ROAS (Return on Ad Spend) by channel and campaign under each model, showing how attribution choice materially affects budget allocation recommendations.

```python
# analytics/attribution.py

def shapley_attribution(conversion_paths: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Shapley value attribution for each touchpoint.
    Uses characteristic function based on conversion probability
    with vs without each channel in the path.
    """
    ...
```

---

### Module 6 — A/B Test Framework
**What it shows:** End-to-end experimentation for ad creative and targeting tests
- Power analysis: minimum detectable effect, required sample size
- Test design: randomization unit (user vs. device), stratification
- Results analysis: z-test, t-test, and bootstrap confidence intervals
- CUPED variance reduction using pre-experiment covariates
- Sequential testing with alpha-spending to enable early stopping
- Causal impact estimation using Difference-in-Differences

**Example test:** Creative A vs Creative B on 30-second completion rate
```python
# analytics/ab_testing.py

class ABTestAnalyzer:
    def __init__(self, control: pd.Series, treatment: pd.Series):
        self.control = control
        self.treatment = treatment

    def power_analysis(self, alpha=0.05, power=0.80) -> dict:
        """Compute minimum sample size for desired power."""
        ...

    def cuped_adjustment(self, covariate: pd.Series) -> tuple:
        """Reduce variance using pre-experiment covariate (CUPED)."""
        theta = np.cov(self.treatment, covariate)[0,1] / np.var(covariate)
        adjusted_treatment = self.treatment - theta * (covariate - covariate.mean())
        return adjusted_treatment, theta

    def sequential_test(self, alpha_spending="obrien_fleming") -> dict:
        """Enable early stopping with controlled Type I error."""
        ...
```

---

### Module 7 — Frequency & Reach Curves
**What it shows:** The classic advertising reach-frequency tradeoff
- Reach curve: unique audience reached vs. total impressions served
- Frequency distribution: histogram of impressions per unique user
- Optimal frequency analysis: conversion rate by frequency bucket
- Diminishing returns curve: incremental reach per additional impression
- Frequency cap recommendations by campaign objective

---

## Technical Implementation

### ETL Pipeline

```python
# etl/transform.py — core feature engineering

def engineer_ctv_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw impression events into analytics-ready features.
    Applies IAB taxonomy, computes derived metrics, handles missing values.
    """
    df = df.copy()

    # Viewability features
    df["is_viewable"] = df.apply(classify_viewable, axis=1)
    df["view_completion_pct"] = (
        df["view_duration_seconds"] / df["ad_duration_seconds"]
    ).clip(0, 1)

    # Pricing features
    df["bid_floor_ratio"] = df["clearing_price_cpm"] / df["floor_price_cpm"]
    df["auction_efficiency"] = df["clearing_price_cpm"] / df["bid_price_cpm"]

    # Temporal features
    df["hour_of_day"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
    df["is_primetime"] = df["hour_of_day"].between(19, 22)

    # Frequency features (requires groupby)
    freq = df.groupby(["user_id_hashed", "campaign_id"]).size()
    df = df.merge(
        freq.rename("user_campaign_frequency"),
        on=["user_id_hashed", "campaign_id"]
    )

    return df
```

### dbt Models (Snowflake layer)

```sql
-- dbt/models/marts/mart_campaign_performance.sql

with impressions as (
    select * from {{ ref('stg_impressions') }}
),

conversions as (
    select * from {{ ref('stg_conversions') }}
),

campaign_metrics as (
    select
        campaign_id,
        date_trunc('day', impression_timestamp) as report_date,
        count(*)                                as impressions,
        count(distinct user_id_hashed)          as unique_reach,
        sum(clearing_price_cpm) / 1000.0        as total_spend,
        avg(clearing_price_cpm)                 as avg_cpm,
        sum(case when is_viewable then 1 end)
            / count(*)::float                   as viewability_rate,
        sum(case when view_completion_pct >= 1.0 then 1 end)
            / count(*)::float                   as completion_rate
    from impressions
    group by 1, 2
)

select
    c.*,
    coalesce(conv.conversions, 0)           as conversions,
    coalesce(conv.conversions, 0)
        / nullif(c.impressions, 0) * 1000   as conversion_rate_per_mille,
    c.total_spend
        / nullif(coalesce(conv.conversions, 0), 0) as cost_per_conversion
from campaign_metrics c
left join (
    select campaign_id, report_date, count(*) as conversions
    from conversions
    group by 1, 2
) conv using (campaign_id, report_date)
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Git
- Optional: Snowflake free trial account (for dbt layer)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ConradLinusMuhirwe/ctv-ad-intelligence.git
cd ctv-ad-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic CTV data
python data/generator/ctv_simulator.py --impressions 1000000 --days 90

# Or download Criteo/Avazu datasets from Kaggle
# Place in data/raw/ directory

# Run ETL pipeline
python etl/ingest.py
python etl/clean.py
python etl/transform.py

# Launch dashboard
streamlit run dashboard/app.py
```

### Requirements

```
# requirements.txt
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
plotly>=5.18.0
duckdb>=0.9.0
scipy>=1.11.0
statsmodels>=0.14.0
pytest>=7.4.0
hypothesis>=6.88.0
dbt-core>=1.7.0
dbt-snowflake>=1.7.0  # optional
python-dotenv>=1.0.0
```

### Environment Variables

```bash
# .env.example
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=CTV_ANALYTICS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=MARTS
```

---

## Key Findings

> *(Populate this section as you build and run the analysis — these are example findings to replace with your actual results)*

- **Viewability gap:** Smart TV inventory averaged 84% viewable vs. 61% for mobile — consistent with IAB research showing CTV's viewability advantage over mobile web
- **Frequency sweet spot:** Conversion rate peaked at frequency 3–5 per week; above 8 impressions per week showed negative correlation with conversion probability
- **Segment discovery:** K-Means (k=5) identified a "premium sports viewer" segment representing 18% of reach but 34% of conversions — suggesting significant targeting efficiency gains available
- **Attribution divergence:** Shapley attribution shifted 22% of budget credit from last-touch channels to mid-funnel CTV touchpoints — illustrating the systematic undervaluation of CTV in last-touch models
- **Anomaly flags:** Isolation Forest flagged 3.2% of impressions as anomalous; 60% of flagged records showed zero view duration, consistent with invalid traffic patterns

---

## Roadmap

- [ ] Add Marketing Mix Modeling (MMM) module using PyMC Bayesian framework
- [ ] Integrate real-time streaming simulation using Kafka
- [ ] Add Databricks PySpark version of ETL pipeline
- [ ] Implement multi-touch attribution with Markov chains
- [ ] Add LLM-powered campaign insights using Claude API (natural language Q&A over campaign data)
- [ ] Deploy to Streamlit Cloud with live demo link

---

## Author

**Conrad Linus Muhirwe**
MS Analytics & AI — American University (May 2026)
[conradlinusmuhirwe.netlify.app](https://conradlinusmuhirwe.netlify.app) | [LinkedIn](https://www.linkedin.com/in/Conrad-Linus-m)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
