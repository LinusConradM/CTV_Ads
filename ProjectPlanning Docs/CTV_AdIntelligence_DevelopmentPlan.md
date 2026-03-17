# CTV Ad Intelligence Platform — Development Plan

**Author:** Conrad Linus Muhirwe
**Created:** March 17, 2026
**Status:** Pre-Development
**Version:** 1.0

---

## 1. Executive Summary

### 1.1 Project Purpose

Build a production-grade CTV advertising analytics platform that demonstrates end-to-end ad tech competency — from impression ingestion through viewability measurement, audience segmentation, anomaly detection, attribution modeling, and A/B experimentation — delivered via an interactive Streamlit executive dashboard.

### 1.2 Success Criteria

| Criteria | Target |
|----------|--------|
| Synthetic data generation | 1M+ realistic CTV impression records |
| ETL pipeline | Ingest, clean, transform, and load into DuckDB with zero data loss |
| Analytics modules | 6 fully functional engines with unit tests passing |
| Dashboard | 7-page Streamlit app deployed to Streamlit Cloud |
| Test coverage | pytest coverage on all analytics modules |
| Documentation | README, architecture doc, and inline docstrings complete |
| Portfolio integration | Live demo URL on resume and portfolio site |

### 1.3 Target Roles

This project directly addresses interview requirements for:
- LG Ad Solutions — Data Analyst / Ad Tech Analytics
- Spotify Ads — Growth / Measurement Analytics
- Reddit Ads — Ad Platform Analytics
- Adobe — Digital Experience Analytics
- IRIS.TV / Viant — CTV Measurement
- Baker Tilly / Judi Health — Data Engineering (dbt/Snowflake layer)

---

## 2. Tech Stack & Dependencies

### 2.1 Core Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.11+ | Primary development language |
| Dashboard | Streamlit | ≥ 1.32.0 | Interactive executive dashboard |
| Local DB | DuckDB | ≥ 0.9.0 | In-process analytical database |
| Cloud DB | Snowflake | — | Enterprise data warehouse (optional) |
| Data Modeling | dbt-core | ≥ 1.7.0 | SQL-based transformation layer |
| Data Processing | pandas | ≥ 2.0.0 | DataFrame operations and ETL |
| Numerical | numpy | ≥ 1.24.0 | Array computations |
| ML | scikit-learn | ≥ 1.3.0 | K-Means, Isolation Forest |
| Statistics | scipy | ≥ 1.11.0 | Statistical tests |
| Time Series | statsmodels | ≥ 0.14.0 | Statistical modeling |
| Visualization | Plotly | ≥ 5.18.0 | Interactive charts |
| Testing | pytest | ≥ 7.4.0 | Unit and integration tests |
| Property Testing | hypothesis | ≥ 6.88.0 | Property-based testing |
| Config | python-dotenv | ≥ 1.0.0 | Environment variable management |

### 2.2 Optional / Phase 4

| Technology | Version | Purpose |
|-----------|---------|---------|
| dbt-snowflake | ≥ 1.7.0 | Snowflake adapter for dbt |
| Snowflake account | Free trial | Cloud data warehouse |

---

## 3. Phase 1 — Foundation (Data Pipeline + DuckDB)

**Goal:** Working data pipeline with clean impression data queryable in DuckDB
**Estimated Duration:** Days 1–2
**Deliverable:** Can run SQL queries against 1M+ impression records locally

### 3.1 Tasks

#### Task 1.1 — Project Scaffolding

| Item | Detail |
|------|--------|
| **Action** | Create full directory structure, virtual environment, requirements.txt, .gitignore, .env.example |
| **Files** | `requirements.txt`, `.gitignore`, `.env.example`, all `__init__.py` files |
| **Acceptance** | `pip install -r requirements.txt` succeeds; directory tree matches README spec |

**Directory structure to create:**
```
data/raw/
data/processed/
data/marts/
data/generator/
etl/
analytics/
dashboard/pages/
dashboard/components/
dbt/models/staging/
dbt/models/intermediate/
dbt/models/marts/
dbt/tests/
tests/
```

**.gitignore must include:**
```
data/raw/
*.db
*.duckdb
.env
__pycache__/
venv/
.venv/
*.egg-info/
```

#### Task 1.2 — Synthetic CTV Data Generator

| Item | Detail |
|------|--------|
| **Action** | Build `data/generator/ctv_simulator.py` that generates realistic CTV impression event data |
| **Inputs** | CLI args: `--impressions` (default 1M), `--days` (default 90), `--seed` (reproducibility) |
| **Output** | CSV file(s) in `data/raw/` with all fields defined in README |
| **Dependencies** | None |
| **Acceptance** | Generates 1M records in < 2 minutes; distributions are realistic (see below) |

**Required fields per record:**
- `impression_id` — unique UUID
- `timestamp` — random within date range, weighted toward primetime (7–10 PM)
- `device_type` — smart_tv, mobile, desktop, tablet (weighted: 45%, 25%, 20%, 10%)
- `device_brand` — LG, Samsung, Roku, Apple TV, Fire TV (for smart_tv); varies for others
- `content_category` — news, sports, entertainment, drama, kids (weighted distribution)
- `ad_duration_seconds` — 15, 30, 60 (weighted: 30%, 50%, 20%)
- `ad_format` — video, display_overlay (weighted: 85%, 15%)
- `pixels_visible_pct` — beta distribution centered ~0.80 for CTV, ~0.60 for mobile
- `view_duration_seconds` — correlated with ad_duration and device_type
- `bid_price_cpm` — log-normal, range $5–$35
- `clearing_price_cpm` — 60–90% of bid price
- `floor_price_cpm` — 40–70% of clearing price
- `user_id_hashed` — ~200K unique users (realistic frequency distribution)
- `campaign_id` — 20 campaigns with varying budgets
- `creative_id` — 2–4 creatives per campaign
- `geo_dma` — top 30 US DMAs (weighted by population)
- `converted` — binary, ~2–5% base rate, higher for engaged viewers
- `conversion_type` — app_install, web_visit, store_visit (when converted=1)
- `publisher_id` — 50 publishers with varying quality
- `placement_id` — 3–5 placements per publisher

**Realistic distribution requirements:**
- Primetime hours (7–10 PM) should have 3x impression volume vs. off-peak
- Smart TV viewability should average ~84%; mobile ~61%
- Frequency distribution should follow power law (most users see 1–3 ads, few see 10+)
- Weekend impression volume ~20% higher than weekdays for entertainment content

#### Task 1.3 — Ingestion Module

| Item | Detail |
|------|--------|
| **Action** | Build `etl/ingest.py` — load raw CSV, validate schema, handle nulls, enforce dtypes |
| **Input** | CSV files from `data/raw/` |
| **Output** | Validated pandas DataFrame |
| **Dependencies** | Task 1.2 |
| **Acceptance** | Loads 1M rows; rejects malformed rows with logging; dtype enforcement passes |

**Validation rules:**
- `impression_id` must be non-null and unique
- `timestamp` must parse to valid datetime
- `pixels_visible_pct` must be in [0.0, 1.0]
- `bid_price_cpm` and `clearing_price_cpm` must be positive
- `clearing_price_cpm` ≤ `bid_price_cpm`
- No null values in required fields (impression_id, timestamp, campaign_id, user_id_hashed)

#### Task 1.4 — Cleaning Module

| Item | Detail |
|------|--------|
| **Action** | Build `etl/clean.py` — deduplicate, normalize timestamps to UTC, encode categoricals |
| **Input** | Validated DataFrame from ingest |
| **Output** | Clean DataFrame ready for transformation |
| **Dependencies** | Task 1.3 |
| **Acceptance** | Zero duplicate impression_ids; timestamps in UTC; consistent category encoding |

**Operations:**
- Deduplicate on `impression_id` (keep first)
- Normalize all timestamps to UTC ISO 8601
- Strip whitespace from string fields
- Standardize device_brand capitalization
- Map geo_dma to human-readable DMA names
- Log cleaning statistics (rows removed, nulls filled)

#### Task 1.5 — Transformation Module

| Item | Detail |
|------|--------|
| **Action** | Build `etl/transform.py` — engineer 15+ analytics features |
| **Input** | Clean DataFrame from clean.py |
| **Output** | Feature-rich DataFrame ready for analytics and DuckDB |
| **Dependencies** | Task 1.4 |
| **Acceptance** | All 15 features computed; no NaN in derived columns |

**Features to engineer:**
1. `is_viewable` — IAB viewability classification (boolean)
2. `view_completion_pct` — view_duration / ad_duration, clipped [0, 1]
3. `bid_floor_ratio` — clearing_price / floor_price
4. `auction_efficiency` — clearing_price / bid_price
5. `hour_of_day` — extracted from timestamp
6. `day_of_week` — extracted from timestamp (0=Monday)
7. `is_primetime` — hour between 19–22 (boolean)
8. `is_weekend` — day_of_week in [5, 6] (boolean)
9. `user_campaign_frequency` — impressions per user per campaign
10. `user_daily_frequency` — impressions per user per day
11. `campaign_daily_impressions` — total impressions per campaign per day
12. `device_viewability_avg` — rolling average viewability by device_type
13. `publisher_quality_score` — average viewability rate per publisher
14. `creative_completion_rate` — average completion rate per creative
15. `dma_cpm_index` — DMA CPM relative to national average

#### Task 1.6 — DuckDB Warehouse Module

| Item | Detail |
|------|--------|
| **Action** | Build `etl/warehouse.py` — create DuckDB database, load transformed data, create indexes |
| **Input** | Transformed DataFrame from transform.py |
| **Output** | DuckDB database file at `data/ctv_analytics.duckdb` |
| **Dependencies** | Task 1.5 |
| **Acceptance** | Can query impression counts, CPM aggregations, viewability rates via SQL |

**Tables to create:**
- `impressions` — main fact table (all columns)
- `campaigns` — dimension table (campaign_id, name, budget, start/end dates)
- `publishers` — dimension table (publisher_id, name, quality_score)
- `dmas` — dimension table (dma_code, dma_name, population)

**Indexes:**
- `impression_id` (unique)
- `campaign_id`
- `timestamp`
- `user_id_hashed`

### 3.2 Phase 1 Milestone Checklist

- [ ] Virtual environment created and dependencies installed
- [ ] Synthetic data generator produces 1M+ records with realistic distributions
- [ ] ETL pipeline runs end-to-end: ingest → clean → transform → DuckDB
- [ ] Can execute SQL queries against DuckDB and get correct aggregations
- [ ] All code committed to GitHub with proper .gitignore
- [ ] No data files in the repository

---

## 4. Phase 2 — Analytics Modules (Days 3–5)

**Goal:** All 6 core analytics engines working with unit tests
**Deliverable:** Can explain every analytical decision in an interview

### 4.1 Tasks

#### Task 2.1 — Viewability Engine

| Item | Detail |
|------|--------|
| **File** | `analytics/viewability.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | IAB-compliant classification; viewable rate by campaign, device, publisher |

**Functions to implement:**
- `classify_viewable(row)` — apply IAB thresholds (video: 50% pixels, 2s; display: 50% pixels, 1s)
- `campaign_viewability_report(df)` — viewable rate, measurable rate by campaign
- `device_viewability_breakdown(df)` — viewability by device_type and device_brand
- `publisher_viewability_scorecard(df)` — rank publishers by viewability rate
- `viewability_trend(df, freq='D')` — daily viewability with 3-sigma control limits
- `viewability_distribution(df)` — histogram of pixel_visible_pct and view_duration

#### Task 2.2 — Audience Segmentation

| Item | Detail |
|------|--------|
| **File** | `analytics/segmentation.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | K-Means clusters with interpretable profiles; elbow curve; PCA visualization |

**Functions to implement:**
- `prepare_clustering_features(df)` — aggregate user-level features (7 features from README)
- `find_optimal_k(features, k_range=(2,10))` — elbow curve + silhouette scores
- `fit_segments(features, k)` — K-Means fitting, return cluster labels and centroids
- `segment_profiles(df, labels)` — descriptive statistics per segment (mean viewability, frequency, content mix)
- `segment_pca_projection(features, labels)` — 2D PCA for visualization
- `segment_value_analysis(df, labels)` — CPM efficiency and conversion rate per segment

#### Task 2.3 — Anomaly Detection

| Item | Detail |
|------|--------|
| **File** | `analytics/anomaly_detection.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | Isolation Forest flags top 5% anomalous records; bot traffic indicators detected |

**Functions to implement:**
- `build_anomaly_features(df)` — features: impression volume, CPM, viewability, frequency, view_duration
- `fit_isolation_forest(features, contamination=0.05)` — train model, return scores
- `flag_anomalies(df, scores, threshold)` — add anomaly flag and score columns
- `anomaly_summary(df)` — count and categorize anomalies (bot traffic, delivery spikes, CPM outliers)
- `bot_traffic_indicators(df)` — flag zero view_duration + high frequency patterns
- `control_chart(df, metric, freq='D')` — time-series with 3-sigma bounds

#### Task 2.4 — Attribution Modeling

| Item | Detail |
|------|--------|
| **File** | `analytics/attribution.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | 5 attribution models produce different credit allocation; ROAS comparison table |

**Functions to implement:**
- `build_conversion_paths(df)` — construct ordered touchpoint sequences per user
- `last_touch_attribution(paths)` — 100% credit to final touchpoint
- `first_touch_attribution(paths)` — 100% credit to first touchpoint
- `linear_attribution(paths)` — equal credit across all touchpoints
- `time_decay_attribution(paths, half_life=7)` — exponential decay from conversion
- `shapley_attribution(paths)` — game-theoretic marginal contribution (if time permits)
- `attribution_comparison(df)` — side-by-side ROAS by channel under each model

#### Task 2.5 — A/B Testing Framework

| Item | Detail |
|------|--------|
| **File** | `analytics/ab_testing.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | Power analysis, z-test, CUPED adjustment, confidence intervals all functional |

**Class: `ABTestAnalyzer`**
- `__init__(control, treatment)` — initialize with two Series
- `power_analysis(alpha=0.05, power=0.80)` — minimum sample size for MDE
- `run_ztest()` — two-proportion z-test with p-value and confidence interval
- `run_ttest()` — Welch's t-test for continuous metrics
- `cuped_adjustment(covariate)` — CUPED variance reduction
- `bootstrap_ci(n_iterations=10000, ci=0.95)` — bootstrap confidence interval
- `sequential_test(alpha_spending='obrien_fleming')` — early stopping boundaries
- `summarize_results()` — formatted results dict with effect size, significance, CI

#### Task 2.6 — Frequency & Reach Analysis

| Item | Detail |
|------|--------|
| **File** | `analytics/frequency_reach.py` |
| **Dependencies** | Phase 1 complete |
| **Acceptance** | Reach curve, frequency histogram, optimal frequency identification |

**Functions to implement:**
- `reach_curve(df, campaign_id=None)` — unique users reached vs. total impressions
- `frequency_distribution(df, campaign_id=None)` — histogram of impressions per user
- `optimal_frequency(df)` — conversion rate by frequency bucket, identify sweet spot
- `diminishing_returns(df)` — incremental reach per additional impression
- `frequency_cap_recommendation(df, objective='conversions')` — recommended cap with rationale

### 4.2 Testing Strategy

#### Unit Tests

| Test File | Covers | Key Tests |
|-----------|--------|-----------|
| `tests/test_etl.py` | ingest, clean, transform | Schema validation, dedup logic, feature computation accuracy |
| `tests/test_viewability.py` | viewability.py | IAB threshold classification (edge cases at exactly 50%/2s) |
| `tests/test_segmentation.py` | segmentation.py | Cluster count matches K; features are normalized |
| `tests/test_anomaly.py` | anomaly_detection.py | Known anomalies are flagged; contamination rate respected |
| `tests/test_attribution.py` | attribution.py | Single-touch path gives 100% credit; linear sums to 1.0 |
| `tests/test_ab_testing.py` | ab_testing.py | Power calc matches statsmodels; identical groups → p > 0.05 |
| `tests/test_frequency.py` | frequency_reach.py | Reach ≤ total users; frequency ≥ 1.0 |

#### Test Data
- Create `tests/fixtures/` with small (1,000 row) deterministic test datasets
- Use `pytest.fixtures` for shared test data
- Use `hypothesis` for property-based testing on viewability classification

### 4.3 Phase 2 Milestone Checklist

- [ ] All 6 analytics modules implemented and importable
- [ ] All unit tests passing (`pytest tests/ -v`)
- [ ] Each module works with DuckDB data from Phase 1
- [ ] Can generate a viewability report, segment users, detect anomalies, compare attribution models, run A/B analysis, and plot reach curves programmatically
- [ ] Code is clean, documented with docstrings, and committed

---

## 5. Phase 3 — Dashboard (Days 6–8)

**Goal:** Deployed Streamlit dashboard with all 7 pages
**Deliverable:** Live demo URL for applications and interviews

### 5.1 Tasks

#### Task 3.1 — Dashboard Core & Navigation

| Item | Detail |
|------|--------|
| **File** | `dashboard/app.py` |
| **Dependencies** | Phase 2 complete |
| **Acceptance** | Streamlit app launches; sidebar navigation works; global filters apply |

**Implementation:**
- Sidebar with page navigation (7 pages)
- Global filters: date range, campaign selector, device type, DMA
- Data loading with `@st.cache_data` for performance
- Consistent page layout template
- Dark/light theme support

#### Task 3.2 — Reusable UI Components

| Item | Detail |
|------|--------|
| **Files** | `dashboard/components/kpi_cards.py`, `charts.py`, `filters.py` |
| **Dependencies** | Task 3.1 |
| **Acceptance** | KPI cards, chart helpers, and filter components are reusable across pages |

**Components:**
- `kpi_cards.py` — metric cards with delta indicators (↑/↓ vs. prior period)
- `charts.py` — Plotly chart wrappers (time series, bar, histogram, scatter, heatmap)
- `filters.py` — date range picker, multi-select for campaigns/devices/DMAs

#### Task 3.3 — Page 1: Campaign Performance Overview

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/01_campaign_overview.py` |
| **KPIs** | Total impressions, unique reach, avg frequency, avg CPM, viewable rate, completion rate |
| **Charts** | CPM trend line, eCPM by device/content/geo (bar), delivery pacing gauge, CTR by creative |

#### Task 3.4 — Page 2: Viewability & Delivery Health

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/02_viewability_health.py` |
| **KPIs** | Viewable rate, measurable rate, avg pixel visibility, avg view duration |
| **Charts** | Viewability by campaign (bar), pixel visibility distribution (histogram), viewability trend with control limits (line), publisher scorecard (table) |

#### Task 3.5 — Page 3: Audience Segmentation

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/03_audience_segments.py` |
| **KPIs** | Number of segments, largest segment size, highest-value segment |
| **Charts** | Elbow curve, PCA scatter (colored by segment), segment radar/profile charts, segment CPM efficiency (bar) |
| **Interactive** | Slider for K selection; re-run clustering on demand |

#### Task 3.6 — Page 4: Anomaly Detection & Alerts

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/04_anomaly_alerts.py` |
| **KPIs** | Anomaly rate, flagged campaigns count, bot traffic % |
| **Charts** | Anomaly score distribution (histogram), control charts for volume/CPM/viewability, anomalous records table with drill-down |
| **Interactive** | Contamination threshold slider; anomaly category filter |

#### Task 3.7 — Page 5: Attribution Modeling

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/05_attribution.py` |
| **KPIs** | Total conversions, ROAS by model, budget reallocation delta |
| **Charts** | Side-by-side bar chart (credit by channel per model), Sankey diagram of conversion paths, ROAS comparison table |
| **Interactive** | Model selector (checkboxes); time-decay half-life slider |

#### Task 3.8 — Page 6: A/B Test Results

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/06_ab_testing.py` |
| **KPIs** | Test status (significant/not), effect size, sample size, statistical power |
| **Charts** | Distribution comparison (overlapping histograms), confidence interval plot, cumulative conversion curve, power curve |
| **Interactive** | Select test (campaign/creative pair); choose metric (completion rate, CTR, viewability) |

#### Task 3.9 — Page 7: Frequency & Reach Curves

| Item | Detail |
|------|--------|
| **File** | `dashboard/pages/07_frequency_reach.py` |
| **KPIs** | Total reach, avg frequency, optimal frequency, recommended cap |
| **Charts** | Reach curve (line), frequency histogram, conversion rate by frequency bucket (bar), diminishing returns curve |
| **Interactive** | Campaign selector; frequency cap simulator |

### 5.2 Dashboard Design Standards

- **Color palette:** Professional blue/gray scheme consistent across all pages
- **Typography:** Clean headers, readable metric labels
- **Responsiveness:** Test at 1280px and 1920px widths
- **Performance:** All pages load in < 3 seconds with cached data
- **Accessibility:** Alt text on charts; color-blind friendly palette

### 5.3 Phase 3 Milestone Checklist

- [ ] `streamlit run dashboard/app.py` launches without errors
- [ ] All 7 pages render with correct data and interactive filters
- [ ] Global filters (date, campaign, device) propagate to all pages
- [ ] KPI cards show accurate metrics with delta indicators
- [ ] Charts are interactive (hover, zoom, filter)
- [ ] Deployed to Streamlit Cloud with live URL
- [ ] Demo URL added to portfolio site and resume

---

## 6. Phase 4 — dbt / Snowflake Layer (Days 9–10, Optional)

**Goal:** dbt project with governed metric definitions running on Snowflake
**Deliverable:** Demonstrates enterprise data modeling competency

### 6.1 Tasks

#### Task 4.1 — Snowflake Setup

| Item | Detail |
|------|--------|
| **Action** | Sign up for Snowflake 30-day free trial; create database, warehouse, schema |
| **Config** | Database: `CTV_ANALYTICS`, Warehouse: `COMPUTE_WH`, Schema: `MARTS` |
| **Acceptance** | Can connect from Python using snowflake-connector |

#### Task 4.2 — Data Loading to Snowflake

| Item | Detail |
|------|--------|
| **Action** | Load processed impression data from DuckDB/CSV into Snowflake staging |
| **Method** | Use `snowflake-connector-python` or `COPY INTO` from staged files |
| **Acceptance** | Row counts match between DuckDB and Snowflake |

#### Task 4.3 — dbt Project Setup

| Item | Detail |
|------|--------|
| **Files** | `dbt/dbt_project.yml`, `dbt/profiles.yml` (gitignored) |
| **Acceptance** | `dbt debug` succeeds; connection to Snowflake confirmed |

#### Task 4.4 — Staging Models

| Item | Detail |
|------|--------|
| **Files** | `dbt/models/staging/stg_impressions.sql`, `stg_conversions.sql`, `stg_audiences.sql` |
| **Action** | Clean column names, cast types, add source freshness tests |

#### Task 4.5 — Intermediate Models

| Item | Detail |
|------|--------|
| **Files** | `dbt/models/intermediate/int_campaign_metrics.sql`, `int_user_frequency.sql` |
| **Action** | Campaign-level daily aggregations; user-level frequency calculations |

#### Task 4.6 — Mart Models

| Item | Detail |
|------|--------|
| **Files** | `dbt/models/marts/mart_campaign_performance.sql`, `mart_viewability.sql`, `mart_attribution.sql` |
| **Action** | Analytics-ready tables matching dashboard requirements |

#### Task 4.7 — dbt Tests & Documentation

| Item | Detail |
|------|--------|
| **File** | `dbt/tests/schema.yml` |
| **Tests** | `not_null` and `unique` on impression_id; `accepted_values` on device_type; `relationships` between fact and dimension tables |
| **Acceptance** | `dbt test` passes with zero failures |

### 6.2 Phase 4 Milestone Checklist

- [ ] Snowflake free trial active with CTV_ANALYTICS database
- [ ] Data loaded and row counts verified
- [ ] `dbt run` executes all models successfully
- [ ] `dbt test` passes all schema tests
- [ ] README updated to document dual DuckDB/Snowflake support

---

## 7. Deployment Plan

### 7.1 Streamlit Cloud Deployment

| Step | Action |
|------|--------|
| 1 | Ensure `requirements.txt` is complete and up-to-date |
| 2 | Add `.streamlit/config.toml` with theme configuration |
| 3 | Connect GitHub repo to Streamlit Cloud (streamlit.io/cloud) |
| 4 | Set main file path to `dashboard/app.py` |
| 5 | Configure secrets in Streamlit Cloud (if Snowflake connection needed) |
| 6 | Deploy and verify all 7 pages render correctly |
| 7 | Set custom subdomain if available |

### 7.2 GitHub Repository

| Item | Action |
|------|--------|
| README | Update with live demo badge, screenshots, and setup instructions |
| License | Add MIT LICENSE file |
| CI | (Optional) Add GitHub Actions for `pytest` on push |
| Releases | Tag v1.0 after Phase 3 deployment |

### 7.3 Portfolio Integration

| Item | Action |
|------|--------|
| Portfolio site | Add project card with description, tech stack, and live demo link |
| Resume | Add project entry using language from Architecture doc Section 6 |
| LinkedIn | Post about the project with 2–3 key findings |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Synthetic data not realistic enough | Medium | High | Validate distributions against IAB industry benchmarks; iterate on simulator |
| Streamlit Cloud performance issues with 1M rows | Medium | Medium | Pre-aggregate data into mart tables; use `@st.cache_data`; sample if needed |
| Snowflake free trial expires before Phase 4 | Low | Low | Phase 4 is optional; DuckDB version is fully functional standalone |
| K-Means produces uninterpretable segments | Medium | Medium | Try multiple K values; validate with silhouette score; name segments based on centroid profiles |
| Attribution paths too sparse for Shapley | Medium | Low | Shapley is stretch goal; 4 other models are sufficient for interviews |
| Streamlit Cloud deployment fails | Low | High | Test locally first; keep dependencies minimal; use `requirements.txt` not `pyproject.toml` |
| Dashboard pages too slow | Medium | Medium | Profile with `st.profiler`; pre-compute expensive analytics; add loading spinners |

---

## 9. Quality Gates & Milestones

### Gate 1 — Foundation Complete (End of Day 2)
- [ ] 1M+ synthetic records generated with realistic distributions
- [ ] ETL pipeline runs end-to-end without errors
- [ ] DuckDB queries return correct aggregations
- [ ] Code committed to GitHub

### Gate 2 — Analytics Complete (End of Day 5)
- [ ] All 6 analytics modules implemented
- [ ] All unit tests passing
- [ ] Can produce viewability report, segments, anomaly flags, attribution comparison, A/B results, and reach curves from code

### Gate 3 — Dashboard Deployed (End of Day 8)
- [ ] 7-page Streamlit dashboard functional
- [ ] Deployed to Streamlit Cloud with live URL
- [ ] All interactive filters working
- [ ] Demo-ready for interviews

### Gate 4 — Enterprise Layer (End of Day 10, Optional)
- [ ] dbt models running on Snowflake
- [ ] All dbt tests passing
- [ ] README documents dual-platform support

---

## 10. Post-Launch Roadmap

These are stretch goals for after the core platform is complete:

| Priority | Feature | Complexity |
|----------|---------|-----------|
| P1 | Marketing Mix Modeling (MMM) with PyMC Bayesian framework | High |
| P2 | LLM-powered campaign insights using Claude API (natural language Q&A) | Medium |
| P3 | Real-time streaming simulation with Kafka | High |
| P4 | PySpark version of ETL pipeline (Databricks) | Medium |
| P5 | Markov chain multi-touch attribution | Medium |
| P6 | GitHub Actions CI/CD pipeline with automated testing | Low |

---

## 11. Development Workflow

### Daily Workflow
1. Pull latest from main
2. Work on current phase tasks in order
3. Write tests alongside implementation (not after)
4. Commit after each completed task with descriptive message
5. Run full test suite before end of day

### Commit Message Convention
```
feat: add viewability engine with IAB-standard classification
fix: correct frequency calculation for multi-campaign users
test: add property-based tests for viewability thresholds
docs: update README with live demo URL
refactor: extract KPI card component for dashboard reuse
```

### Branch Strategy
- `main` — stable, deployable code
- Feature branches optional for complex tasks (e.g., `feature/attribution-models`)

---

*This plan is a living document. Update milestone checkboxes as tasks are completed.*
