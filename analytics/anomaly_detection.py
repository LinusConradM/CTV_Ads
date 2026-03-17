"""
Analytics — Anomaly Detection

Isolation Forest monitoring of delivery health metrics.
Flags bot traffic, delivery spikes, CPM outliers, and viewability anomalies.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


ANOMALY_FEATURES = [
    "clearing_price_cpm",
    "pixels_visible_pct",
    "view_duration_seconds",
    "user_campaign_frequency",
    "view_completion_pct",
]


def build_anomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare feature matrix for anomaly detection."""
    features = df[ANOMALY_FEATURES].copy()
    features = features.fillna(0)
    return features


def fit_isolation_forest(
    features: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> tuple[np.ndarray, IsolationForest]:
    """Train Isolation Forest and return anomaly scores."""
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=100,
        n_jobs=-1,
    )
    model.fit(X)
    scores = model.decision_function(X)  # Lower = more anomalous

    return scores, model


def flag_anomalies(
    df: pd.DataFrame,
    scores: np.ndarray,
    contamination: float = 0.05,
) -> pd.DataFrame:
    """Add anomaly flag and score columns to DataFrame."""
    df = df.copy()
    df["anomaly_score"] = scores
    threshold = np.percentile(scores, contamination * 100)
    df["is_anomaly"] = df["anomaly_score"] <= threshold
    return df


def anomaly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Categorize and summarize detected anomalies."""
    anomalies = df[df["is_anomaly"]].copy()

    if len(anomalies) == 0:
        return pd.DataFrame(columns=["category", "count", "pct_of_anomalies"])

    categories = []

    # Bot traffic: zero view duration + high frequency
    bot_mask = (anomalies["view_duration_seconds"] == 0) & (anomalies["user_campaign_frequency"] > 5)
    categories.append(("bot_traffic", bot_mask.sum()))

    # CPM outliers: extremely high or low
    cpm_high = anomalies["clearing_price_cpm"] > anomalies["clearing_price_cpm"].quantile(0.95)
    cpm_low = anomalies["clearing_price_cpm"] < anomalies["clearing_price_cpm"].quantile(0.05)
    categories.append(("cpm_outlier", (cpm_high | cpm_low).sum()))

    # Low viewability: very low pixel visibility
    low_view = anomalies["pixels_visible_pct"] < 0.2
    categories.append(("low_viewability", low_view.sum()))

    # High frequency: suspicious repeat exposure
    high_freq = anomalies["user_campaign_frequency"] > 10
    categories.append(("high_frequency", high_freq.sum()))

    summary = pd.DataFrame(categories, columns=["category", "count"])
    summary["pct_of_anomalies"] = (summary["count"] / len(anomalies) * 100).round(1)

    return summary


def bot_traffic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Flag impressions with bot-like behavior patterns."""
    df = df.copy()
    df["bot_indicator"] = (
        (df["view_duration_seconds"] == 0) &
        (df["user_campaign_frequency"] > 5)
    )
    return df


def control_chart(df: pd.DataFrame, metric: str, freq: str = "D") -> pd.DataFrame:
    """Time-series control chart with 3-sigma bounds for a given metric."""
    daily = df.groupby("report_date")[metric].agg(["mean", "count"]).reset_index()
    daily.columns = ["report_date", "value", "n"]

    overall_mean = daily["value"].mean()
    overall_std = daily["value"].std()

    daily["mean_line"] = overall_mean
    daily["ucl"] = overall_mean + 3 * overall_std
    daily["lcl"] = max(overall_mean - 3 * overall_std, 0)
    daily["out_of_control"] = ~daily["value"].between(daily["lcl"], daily["ucl"])

    return daily
