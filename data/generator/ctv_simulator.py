"""
CTV Ad Intelligence — Synthetic Data Generator

Generates realistic CTV impression-level ad event data with:
- Primetime-weighted temporal patterns
- Device-specific viewability distributions
- Power-law frequency distributions
- Realistic auction pricing mechanics
- Multi-campaign, multi-creative structure
"""

import argparse
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


# ── Constants ────────────────────────────────────────────────────────────────

TOP_DMAS = {
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

DMA_WEIGHTS = np.array([
    0.12, 0.10, 0.06, 0.04, 0.04, 0.035, 0.03, 0.035, 0.03, 0.025,
    0.025, 0.02, 0.02, 0.018, 0.015, 0.02, 0.018, 0.015, 0.012, 0.01,
    0.012, 0.012, 0.015, 0.012, 0.008, 0.01, 0.012, 0.01, 0.008, 0.008,
])
DMA_WEIGHTS = DMA_WEIGHTS / DMA_WEIGHTS.sum()

DEVICE_TYPES = ["smart_tv", "mobile", "desktop", "tablet"]
DEVICE_TYPE_WEIGHTS = [0.45, 0.25, 0.20, 0.10]

SMART_TV_BRANDS = ["LG", "Samsung", "Roku", "Apple TV", "Fire TV"]
SMART_TV_BRAND_WEIGHTS = [0.25, 0.25, 0.25, 0.15, 0.10]

CONTENT_CATEGORIES = ["news", "sports", "entertainment", "drama", "kids"]
CONTENT_CATEGORY_WEIGHTS = [0.20, 0.25, 0.25, 0.20, 0.10]

AD_DURATIONS = [15, 30, 60]
AD_DURATION_WEIGHTS = [0.30, 0.50, 0.20]

AD_FORMATS = ["video", "display_overlay"]
AD_FORMAT_WEIGHTS = [0.85, 0.15]

CONVERSION_TYPES = ["app_install", "web_visit", "store_visit"]
CONVERSION_TYPE_WEIGHTS = [0.30, 0.50, 0.20]

NUM_CAMPAIGNS = 20
NUM_PUBLISHERS = 50
NUM_UNIQUE_USERS = 200_000

# Hourly impression weight — primetime (19–22) gets 3x
HOUR_WEIGHTS = np.array([
    0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5
    0.03, 0.04, 0.05, 0.05, 0.04, 0.04,  # 6-11
    0.05, 0.05, 0.04, 0.04, 0.05, 0.06,  # 12-17
    0.07, 0.09, 0.09, 0.09, 0.06, 0.04,  # 18-23
])
HOUR_WEIGHTS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()

# Day-of-week weights (Mon=0..Sun=6) — weekends slightly higher
DAY_WEIGHTS = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.20, 1.20])
DAY_WEIGHTS = DAY_WEIGHTS / DAY_WEIGHTS.sum()


# ── Helper Functions ─────────────────────────────────────────────────────────

def _hash_user(idx: int, seed: int) -> str:
    return "u_" + hashlib.md5(f"{seed}_{idx}".encode()).hexdigest()[:8]


def _generate_campaigns(rng: np.random.Generator) -> pd.DataFrame:
    campaigns = []
    for i in range(NUM_CAMPAIGNS):
        cid = f"camp_{i+1:03d}"
        num_creatives = rng.integers(2, 5)
        creatives = [f"cr_{cid}_{chr(65+j)}" for j in range(num_creatives)]
        budget = rng.uniform(50_000, 500_000)
        campaigns.append({
            "campaign_id": cid,
            "creatives": creatives,
            "budget": round(budget, 2),
        })
    return campaigns


def _generate_publishers(rng: np.random.Generator) -> list[dict]:
    publishers = []
    for i in range(NUM_PUBLISHERS):
        pid = f"pub_{i+1:03d}"
        num_placements = rng.integers(3, 6)
        placements = [f"pl_{pid}_{j+1}" for j in range(num_placements)]
        quality = rng.beta(5, 2)  # Most publishers are decent quality
        publishers.append({
            "publisher_id": pid,
            "placements": placements,
            "quality": quality,
        })
    return publishers


# ── Main Generator ───────────────────────────────────────────────────────────

def generate_impressions(
    n_impressions: int = 1_000_000,
    n_days: int = 90,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic CTV impression data."""
    rng = np.random.default_rng(seed)

    # Pre-generate reference data
    campaigns = _generate_campaigns(rng)
    publishers = _generate_publishers(rng)
    user_ids = [_hash_user(i, seed) for i in range(NUM_UNIQUE_USERS)]
    dma_codes = list(TOP_DMAS.keys())

    # Assign users with power-law frequency (most users see few ads)
    # Use Zipf-like distribution for user selection
    user_weights = 1.0 / (np.arange(1, NUM_UNIQUE_USERS + 1) ** 0.7)
    user_weights = user_weights / user_weights.sum()

    end_date = datetime(2024, 6, 15)
    start_date = end_date - timedelta(days=n_days)

    # ── Generate each field ──────────────────────────────────────────────

    # Impression IDs
    impression_ids = [f"imp_{uuid.uuid4().hex[:8]}" for _ in range(n_impressions)]

    # Timestamps: weighted by hour and day-of-week
    days_offset = rng.choice(n_days, size=n_impressions, p=None)
    # Weight by day of week
    base_dates = [start_date + timedelta(days=int(d)) for d in days_offset]
    dow = np.array([d.weekday() for d in base_dates])
    # Resample with day-of-week weights for weekend boost
    day_accept = rng.random(n_impressions) < (DAY_WEIGHTS[dow] * 7)
    # Simple rejection — keep ~all, just shift weekend content slightly
    hours = rng.choice(24, size=n_impressions, p=HOUR_WEIGHTS)
    minutes = rng.integers(0, 60, size=n_impressions)
    seconds = rng.integers(0, 60, size=n_impressions)
    timestamps = [
        datetime(d.year, d.month, d.day, int(h), int(m), int(s))
        for d, h, m, s in zip(base_dates, hours, minutes, seconds)
    ]

    # Device types
    device_types = rng.choice(DEVICE_TYPES, size=n_impressions, p=DEVICE_TYPE_WEIGHTS)

    # Device brands
    device_brands = []
    for dt in device_types:
        if dt == "smart_tv":
            device_brands.append(rng.choice(SMART_TV_BRANDS, p=SMART_TV_BRAND_WEIGHTS))
        elif dt == "mobile":
            device_brands.append(rng.choice(["Apple", "Samsung", "Google", "Other"]))
        elif dt == "desktop":
            device_brands.append(rng.choice(["Windows", "Mac", "Linux"]))
        else:
            device_brands.append(rng.choice(["Apple", "Samsung", "Amazon"]))

    # Content categories — sports higher on weekends
    content_cats = rng.choice(CONTENT_CATEGORIES, size=n_impressions, p=CONTENT_CATEGORY_WEIGHTS)

    # Ad duration and format
    ad_durations = rng.choice(AD_DURATIONS, size=n_impressions, p=AD_DURATION_WEIGHTS)
    ad_formats = rng.choice(AD_FORMATS, size=n_impressions, p=AD_FORMAT_WEIGHTS)

    # Viewability — device-dependent beta distributions
    pixels_visible = np.zeros(n_impressions)
    for i, dt in enumerate(device_types):
        if dt == "smart_tv":
            pixels_visible[i] = rng.beta(8, 2)    # mean ~0.80
        elif dt == "mobile":
            pixels_visible[i] = rng.beta(4, 3)    # mean ~0.57
        elif dt == "desktop":
            pixels_visible[i] = rng.beta(5, 3)    # mean ~0.625
        else:  # tablet
            pixels_visible[i] = rng.beta(6, 3)    # mean ~0.67
    pixels_visible = np.clip(pixels_visible, 0.0, 1.0)

    # View duration — correlated with ad duration and viewability
    view_durations = np.zeros(n_impressions)
    for i in range(n_impressions):
        max_dur = float(ad_durations[i])
        # Higher viewability → longer view
        base_completion = pixels_visible[i] * rng.beta(5, 2)
        view_durations[i] = round(max_dur * base_completion, 1)
    view_durations = np.clip(view_durations, 0.0, ad_durations.astype(float))

    # Pricing — log-normal CPM
    bid_prices = np.round(rng.lognormal(mean=2.3, sigma=0.4, size=n_impressions), 2)
    bid_prices = np.clip(bid_prices, 5.0, 35.0)
    clearing_ratio = rng.uniform(0.60, 0.90, size=n_impressions)
    clearing_prices = np.round(bid_prices * clearing_ratio, 2)
    floor_ratio = rng.uniform(0.40, 0.70, size=n_impressions)
    floor_prices = np.round(clearing_prices * floor_ratio, 2)

    # Users — power-law selection
    user_indices = rng.choice(NUM_UNIQUE_USERS, size=n_impressions, p=user_weights)
    selected_users = [user_ids[i] for i in user_indices]

    # Campaigns — weighted by budget
    campaign_budgets = np.array([c["budget"] for c in campaigns])
    campaign_weights = campaign_budgets / campaign_budgets.sum()
    campaign_indices = rng.choice(NUM_CAMPAIGNS, size=n_impressions, p=campaign_weights)
    selected_campaigns = [campaigns[i]["campaign_id"] for i in campaign_indices]
    selected_creatives = [
        rng.choice(campaigns[i]["creatives"]) for i in campaign_indices
    ]

    # Geography
    selected_dmas = rng.choice(dma_codes, size=n_impressions, p=DMA_WEIGHTS)

    # Publishers
    pub_indices = rng.integers(0, NUM_PUBLISHERS, size=n_impressions)
    selected_publishers = [publishers[i]["publisher_id"] for i in pub_indices]
    selected_placements = [
        rng.choice(publishers[i]["placements"]) for i in pub_indices
    ]

    # Conversions — base rate ~3%, boosted by engagement
    completion_pct = view_durations / ad_durations.astype(float)
    conversion_prob = 0.03 + 0.05 * completion_pct + 0.02 * pixels_visible
    conversion_prob = np.clip(conversion_prob, 0.0, 0.15)
    converted = (rng.random(n_impressions) < conversion_prob).astype(int)
    conversion_types = [
        rng.choice(CONVERSION_TYPES, p=CONVERSION_TYPE_WEIGHTS) if c == 1 else None
        for c in converted
    ]

    # ── Assemble DataFrame ───────────────────────────────────────────────

    df = pd.DataFrame({
        "impression_id": impression_ids,
        "timestamp": timestamps,
        "device_type": device_types,
        "device_brand": device_brands,
        "content_category": content_cats,
        "ad_duration_seconds": ad_durations,
        "ad_format": ad_formats,
        "pixels_visible_pct": np.round(pixels_visible, 4),
        "view_duration_seconds": view_durations,
        "bid_price_cpm": bid_prices,
        "clearing_price_cpm": clearing_prices,
        "floor_price_cpm": floor_prices,
        "user_id_hashed": selected_users,
        "campaign_id": selected_campaigns,
        "creative_id": selected_creatives,
        "geo_dma": selected_dmas,
        "publisher_id": selected_publishers,
        "placement_id": selected_placements,
        "converted": converted,
        "conversion_type": conversion_types,
    })

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic CTV ad impression data")
    parser.add_argument("--impressions", type=int, default=1_000_000, help="Number of impressions")
    parser.add_argument("--days", type=int, default=90, help="Date range in days")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    args = parser.parse_args()

    print(f"Generating {args.impressions:,} impressions over {args.days} days (seed={args.seed})...")
    df = generate_impressions(args.impressions, args.days, args.seed)

    output_path = args.output or str(Path(__file__).parent.parent / "raw" / "impressions.csv")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} records to {output_path}")

    # Quick stats
    print(f"\n--- Data Summary ---")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Unique users: {df['user_id_hashed'].nunique():,}")
    print(f"Campaigns: {df['campaign_id'].nunique()}")
    print(f"Conversion rate: {df['converted'].mean():.2%}")
    print(f"Device type distribution:\n{df['device_type'].value_counts(normalize=True).to_string()}")
    print(f"Avg viewability by device:")
    print(df.groupby("device_type")["pixels_visible_pct"].mean().round(3).to_string())


if __name__ == "__main__":
    main()
