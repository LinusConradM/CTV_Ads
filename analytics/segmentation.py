"""
Analytics — Audience Segmentation

K-Means clustering of advertiser audiences using behavioral features.
Produces interpretable segment profiles for targeting optimization.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


CLUSTERING_FEATURES = [
    "avg_view_completion",
    "avg_daily_sessions",
    "content_category_entropy",
    "primetime_pct",
    "completion_rate",
    "avg_cpm_exposure",
    "frequency",
]


def prepare_clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate impression-level data to user-level clustering features."""
    user_agg = df.groupby("user_id_hashed").agg(
        avg_view_completion=("view_completion_pct", "mean"),
        total_impressions=("impression_id", "count"),
        num_days=("report_date", "nunique"),
        primetime_count=("is_primetime", "sum"),
        completion_rate=("view_completion_pct", lambda x: (x >= 0.95).mean()),
        avg_cpm_exposure=("clearing_price_cpm", "mean"),
        converted_any=("converted", "max"),
    ).reset_index()

    user_agg["avg_daily_sessions"] = user_agg["total_impressions"] / user_agg["num_days"].clip(lower=1)
    user_agg["primetime_pct"] = user_agg["primetime_count"] / user_agg["total_impressions"]
    user_agg["frequency"] = user_agg["total_impressions"]

    # Content category entropy (diversity of content consumed)
    content_counts = df.groupby(["user_id_hashed", "content_category"]).size().unstack(fill_value=0)
    content_probs = content_counts.div(content_counts.sum(axis=1), axis=0)
    entropy = -(content_probs * np.log2(content_probs.clip(lower=1e-10))).sum(axis=1)
    entropy.name = "content_category_entropy"
    user_agg = user_agg.merge(entropy, on="user_id_hashed", how="left")
    user_agg["content_category_entropy"] = user_agg["content_category_entropy"].fillna(0)

    return user_agg


def find_optimal_k(features: pd.DataFrame, k_range: tuple = (2, 10)) -> pd.DataFrame:
    """Compute inertia and silhouette scores for range of K values."""
    feature_cols = [c for c in CLUSTERING_FEATURES if c in features.columns]
    X = StandardScaler().fit_transform(features[feature_cols])

    results = []
    for k in range(k_range[0], k_range[1] + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels) if k > 1 else 0
        results.append({
            "k": k,
            "inertia": km.inertia_,
            "silhouette_score": round(sil, 4),
        })

    return pd.DataFrame(results)


def fit_segments(features: pd.DataFrame, k: int) -> tuple[np.ndarray, KMeans, StandardScaler]:
    """Fit K-Means and return labels, model, and scaler."""
    feature_cols = [c for c in CLUSTERING_FEATURES if c in features.columns]
    scaler = StandardScaler()
    X = scaler.fit_transform(features[feature_cols])

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    return labels, km, scaler


def segment_profiles(features: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """Descriptive statistics per segment."""
    df = features.copy()
    df["segment"] = labels

    profile_cols = [c for c in CLUSTERING_FEATURES if c in df.columns]
    profiles = df.groupby("segment")[profile_cols + ["converted_any", "total_impressions"]].agg(["mean", "count"])

    # Flatten multi-level columns
    profiles.columns = ["_".join(col).strip() for col in profiles.columns.values]
    profiles = profiles.reset_index()

    # Add segment size
    segment_sizes = df["segment"].value_counts().rename("segment_size")
    profiles = profiles.merge(segment_sizes, left_on="segment", right_index=True)

    return profiles


def segment_pca_projection(features: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """2D PCA projection for segment visualization."""
    feature_cols = [c for c in CLUSTERING_FEATURES if c in features.columns]
    X = StandardScaler().fit_transform(features[feature_cols])

    pca = PCA(n_components=2)
    coords = pca.fit_transform(X)

    result = pd.DataFrame({
        "pc1": coords[:, 0],
        "pc2": coords[:, 1],
        "segment": labels,
        "user_id_hashed": features["user_id_hashed"].values,
    })

    explained_var = pca.explained_variance_ratio_
    result.attrs["explained_variance"] = explained_var.tolist()

    return result


def segment_value_analysis(features: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """CPM efficiency and conversion rate per segment."""
    df = features.copy()
    df["segment"] = labels

    value = df.groupby("segment").agg(
        users=("user_id_hashed", "count"),
        avg_impressions=("total_impressions", "mean"),
        avg_cpm=("avg_cpm_exposure", "mean"),
        conversion_rate=("converted_any", "mean"),
        avg_completion=("avg_view_completion", "mean"),
    ).round(4).reset_index()

    # Reach share
    total_users = value["users"].sum()
    value["reach_share"] = (value["users"] / total_users).round(4)

    return value
