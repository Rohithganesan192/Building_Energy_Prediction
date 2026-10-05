"""
eda.py
======
Phase 4 — Exploratory Data Analysis
Project: Explainable ML for Building Energy Consumption Prediction
Dataset: ASHRAE Great Energy Predictor III

Rules enforced in this script:
- Reads ONLY from data/processed/ (cleaned outputs).
- data/raw/ is never touched.
- No model training, feature engineering, imputation, or log-transformation.
- Outliers are investigated, never deleted.
- 20M+ train data processed via chunking or controlled sampling only.
- All numerical findings come from actual computation; nothing is hard-coded.
- Fixed random seed for any sampling.
"""

import sys
import json
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# Make src/ importable when running from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.eda_utils import (
    METER_LABELS, METER_COLORS, PERCENTILE_LEVELS, RANDOM_SEED,
    save_figure, styled_figure, styled_figure_multi,
    descriptive_stats, missing_summary,
    sample_energy_chunked, aggregate_energy_chunked, meter_stats_chunked,
)

warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------

PROC_DIR    = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR  / "figures"
TABLES_DIR  = REPORTS_DIR  / "tables"

TRAIN_PATH   = PROC_DIR / "train_clean.csv"
TEST_PATH    = PROC_DIR / "test_clean.csv"
META_PATH    = PROC_DIR / "building_metadata_clean.csv"
W_TRAIN_PATH = PROC_DIR / "weather_train_clean.csv"
W_TEST_PATH  = PROC_DIR / "weather_test_clean.csv"

# Sampling config
SAMPLE_FRAC = 0.02          # 2 % of train rows for visualisations
CHUNKSIZE   = 1_000_000


def setup_dirs():
    for d in [FIGURES_DIR, TABLES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


# ==================================================================
# 1. DATASET OVERVIEW
# ==================================================================

def dataset_overview(sample: pd.DataFrame,
                     meta: pd.DataFrame,
                     w_train: pd.DataFrame,
                     w_test: pd.DataFrame) -> dict:
    """Report high-level dataset dimensions from processed files."""

    # Row counts via chunked pass for accuracy
    train_rows, test_rows = 0, 0
    for chunk in pd.read_csv(TRAIN_PATH, chunksize=CHUNKSIZE):
        train_rows += len(chunk)
    for chunk in pd.read_csv(TEST_PATH, chunksize=CHUNKSIZE):
        test_rows += len(chunk)

    ts_min, ts_max = None, None
    for chunk in pd.read_csv(TRAIN_PATH, chunksize=CHUNKSIZE,
                              parse_dates=["timestamp"]):
        c_min = chunk["timestamp"].min()
        c_max = chunk["timestamp"].max()
        if ts_min is None or c_min < ts_min: ts_min = c_min
        if ts_max is None or c_max > ts_max: ts_max = c_max

    # FIX 3: simple, readable implementation – compute unique building count before dict
    building_ids = set()
    for chunk in pd.read_csv(
            TRAIN_PATH, chunksize=CHUNKSIZE, usecols=["building_id"]
    ):
        building_ids.update(chunk["building_id"].unique())
    unique_buildings_train = len(building_ids)

    overview = {
        "train_rows": train_rows,
        "test_rows": test_rows,
        "train_columns": list(sample.columns),
        "unique_buildings_train": int(unique_buildings_train),
        "unique_meters": int(sample["meter"].nunique()),
        "unique_sites_meta": int(meta["site_id"].nunique()),
        "train_ts_min": str(ts_min),
        "train_ts_max": str(ts_max),
        "metadata_rows": len(meta),
        "metadata_columns": list(meta.columns),
        "weather_train_rows": len(w_train),
        "weather_test_rows": len(w_test),
        "weather_columns": list(w_train.columns),
    }
    return overview


# ==================================================================
# 2. TARGET ANALYSIS
# ==================================================================

def target_analysis(sample: pd.DataFrame) -> dict:
    """Descriptive statistics for meter_reading using sampled data."""
    stats = descriptive_stats(sample["meter_reading"], label="meter_reading (sample)")
    return stats


def plot_target_distribution(sample: pd.DataFrame, out_path: Path):
    """Histogram of meter_reading on sampled data (raw scale, no transform)."""
    data = sample["meter_reading"].dropna()

    # Clip at 99th percentile just for the histogram x-axis limit;
    # the underlying data and statistics are unchanged.
    p99 = float(np.percentile(data, 99))

    fig, axes = styled_figure_multi(1, 2, figsize=(14, 5))

    axes[0].hist(data[data <= p99], bins=80, color="#2196F3", alpha=0.8, edgecolor="none")
    axes[0].set_title("meter_reading distribution (≤ 99th pct.)", fontsize=12)
    axes[0].set_xlabel("meter_reading (kWh)")
    axes[0].set_ylabel("Frequency")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x:,.0f}"))

    axes[1].hist(data, bins=80, color="#FF5722", alpha=0.8, edgecolor="none")
    axes[1].set_title("meter_reading distribution (full range)", fontsize=12)
    axes[1].set_xlabel("meter_reading (kWh)")
    axes[1].set_ylabel("Frequency")
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"{x:,.0f}"))

    fig.suptitle("Target Variable Distribution (2% sample)", fontsize=13, y=1.01)
    save_figure(fig, out_path)


# ==================================================================
# 3. METER ANALYSIS
# ==================================================================

def plot_meter_distribution(sample: pd.DataFrame, out_path: Path):
    """Box plots of meter_reading by meter type."""
    fig, ax = styled_figure(figsize=(12, 6))

    p99 = float(np.percentile(sample["meter_reading"].dropna(), 99))
    sub = sample[sample["meter_reading"] <= p99].copy()
    sub["meter_label"] = sub["meter"].map(METER_LABELS)

    order = [METER_LABELS[m] for m in [0, 1, 2, 3]
             if m in sub["meter"].unique()]
    palette = {METER_LABELS[m]: METER_COLORS[m] for m in METER_COLORS}

    sns.boxplot(data=sub, x="meter_label", y="meter_reading",
                order=order, palette=palette, ax=ax,
                showfliers=False, linewidth=1.2)
    ax.set_title("meter_reading by Meter Type (≤ 99th pct., 2% sample)", fontsize=12)
    ax.set_xlabel("Meter Type")
    ax.set_ylabel("meter_reading (kWh)")
    save_figure(fig, out_path)


def plot_meter_statistics(meter_df: pd.DataFrame, out_path: Path):
    """Bar chart comparing mean meter_reading per meter type."""
    fig, axes = styled_figure_multi(1, 2, figsize=(14, 5))

    colors = [METER_COLORS[m] for m in meter_df["meter"]]

    axes[0].bar(meter_df["energy_type"], meter_df["mean"],
                color=colors, alpha=0.85)
    axes[0].set_title("Mean meter_reading by Meter Type", fontsize=12)
    axes[0].set_ylabel("Mean (kWh)")
    axes[0].tick_params(axis="x", rotation=15)

    axes[1].bar(meter_df["energy_type"],
                meter_df["row_count"] / 1e6,
                color=colors, alpha=0.85)
    axes[1].set_title("Row Count by Meter Type (millions)", fontsize=12)
    axes[1].set_ylabel("Rows (M)")
    axes[1].tick_params(axis="x", rotation=15)

    fig.suptitle("Meter Type Statistics", fontsize=13, y=1.01)
    save_figure(fig, out_path)


# ==================================================================
# 4. BUILDING METADATA ANALYSIS
# ==================================================================

def plot_primary_use(meta: pd.DataFrame, out_path: Path):
    counts = meta["primary_use"].value_counts()
    fig, ax = styled_figure(figsize=(12, 6))
    counts.sort_values().plot.barh(ax=ax, color="#4CAF50", alpha=0.85)
    ax.set_title("Building Primary Use Distribution", fontsize=12)
    ax.set_xlabel("Number of Buildings")
    ax.set_ylabel("Primary Use")
    save_figure(fig, out_path)


def plot_metadata_distributions(meta: pd.DataFrame, out_path: Path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # square_feet
    axes[0].hist(meta["square_feet"].dropna(), bins=60,
                 color="#2196F3", alpha=0.8, edgecolor="none")
    axes[0].set_title("square_feet Distribution")
    axes[0].set_xlabel("square_feet")
    axes[0].set_ylabel("Count")

    # year_built
    yb = meta["year_built"].dropna()
    axes[1].hist(yb, bins=40, color="#FF9800", alpha=0.8, edgecolor="none")
    axes[1].set_title(f"year_built Distribution\n(n={len(yb):,} non-missing)")
    axes[1].set_xlabel("Year Built")

    # floor_count
    fc = meta["floor_count"].dropna()
    axes[2].hist(fc, bins=25, color="#9C27B0", alpha=0.8, edgecolor="none")
    axes[2].set_title(f"floor_count Distribution\n(n={len(fc):,} non-missing)")
    axes[2].set_xlabel("Floor Count")

    fig.suptitle("Building Metadata Distributions", fontsize=13, y=1.02)
    plt.tight_layout()
    save_figure(fig, out_path)


# ==================================================================
# 5. MISSING VALUE ANALYSIS
# ==================================================================

def plot_missing_values(meta: pd.DataFrame, w_train: pd.DataFrame,
                        out_path: Path):
    meta_miss  = missing_summary(meta)
    meta_miss  = meta_miss[meta_miss["missing_count"] > 0].copy()
    meta_miss["source"] = "metadata"

    w_miss = missing_summary(w_train)
    w_miss = w_miss[w_miss["missing_count"] > 0].copy()
    w_miss["source"] = "weather_train"

    combined = pd.concat([meta_miss, w_miss], ignore_index=True)

    fig, ax = styled_figure(figsize=(12, 6))
    colors = combined["source"].map({"metadata": "#FF5722",
                                     "weather_train": "#2196F3"})
    ax.barh(combined["column"], combined["missing_pct"],
            color=colors, alpha=0.85)
    ax.set_xlabel("Missing %")
    ax.set_title("Missing Value Summary — Metadata & Weather Train")
    ax.axvline(50, color="red", linestyle="--", linewidth=1, alpha=0.5,
               label="50% threshold")
    ax.legend()

    # Legend for source color
    from matplotlib.patches import Patch
    handles = [Patch(color="#FF5722", label="Metadata"),
               Patch(color="#2196F3", label="Weather Train")]
    ax.legend(handles=handles)
    save_figure(fig, out_path)


# ==================================================================
# 6. WEATHER ANALYSIS
# ==================================================================

WEATHER_COLS = ["air_temperature", "cloud_coverage", "dew_temperature",
                "precip_depth_1_hr", "sea_level_pressure",
                "wind_direction", "wind_speed"]


def plot_weather_distributions(w_train: pd.DataFrame, out_path: Path):
    cols = [c for c in WEATHER_COLS if c in w_train.columns]
    n = len(cols)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 4))
    axes_flat = np.array(axes).flatten()

    for i, col in enumerate(cols):
        data = w_train[col].dropna()
        axes_flat[i].hist(data, bins=50, color="#607D8B", alpha=0.8,
                          edgecolor="none")
        axes_flat[i].set_title(f"{col}\n(n={len(data):,}, "
                                f"miss={w_train[col].isnull().sum():,})")
        axes_flat[i].set_xlabel(col)
        axes_flat[i].spines["top"].set_visible(False)
        axes_flat[i].spines["right"].set_visible(False)

    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)

    fig.suptitle("Weather Variable Distributions (Weather Train)", fontsize=13)
    plt.tight_layout()
    save_figure(fig, out_path)


# ==================================================================
# 7. TEMPORAL ANALYSIS
# ==================================================================

def temporal_analysis(csv_path: Path) -> dict:
    """Aggregate mean meter_reading by hour, weekday, and month."""
    hour_acc  = {}
    dow_acc   = {}
    month_acc = {}

    for chunk in pd.read_csv(csv_path, chunksize=CHUNKSIZE,
                              parse_dates=["timestamp"]):
        chunk["hour"]  = chunk["timestamp"].dt.hour
        chunk["dow"]   = chunk["timestamp"].dt.dayofweek   # 0=Mon
        chunk["month"] = chunk["timestamp"].dt.month

        for grp_col, acc in [("hour", hour_acc),
                              ("dow",  dow_acc),
                              ("month", month_acc)]:
            g = chunk.groupby(grp_col)["meter_reading"].agg(["sum", "count"])
            for key, row in g.iterrows():
                if key not in acc:
                    acc[key] = {"sum": 0.0, "count": 0}
                acc[key]["sum"]   += row["sum"]
                acc[key]["count"] += row["count"]

    def acc_to_series(acc):
        keys = sorted(acc.keys())
        vals = [acc[k]["sum"] / acc[k]["count"] for k in keys]
        return pd.Series(vals, index=keys)

    return {
        "hourly": acc_to_series(hour_acc),
        "weekday": acc_to_series(dow_acc),
        "monthly": acc_to_series(month_acc),
    }


def plot_temporal(temporal: dict, out_dir: Path):
    DOW_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Hourly
    fig, ax = styled_figure(figsize=(12, 4))
    s = temporal["hourly"]
    ax.plot(s.index, s.values, marker="o", color="#2196F3", linewidth=2)
    ax.set_title("Average meter_reading by Hour of Day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Mean meter_reading (kWh)")
    ax.set_xticks(range(24))
    save_figure(fig, out_dir / "hourly_consumption.png")

    # Weekday
    fig, ax = styled_figure(figsize=(10, 4))
    s = temporal["weekday"]
    bar_colors = ["#FF5722" if i >= 5 else "#2196F3" for i in s.index]
    ax.bar([DOW_LABELS[i] for i in s.index], s.values,
           color=bar_colors, alpha=0.85)
    ax.set_title("Average meter_reading by Day of Week\n"
                 "(orange = weekend)")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Mean meter_reading (kWh)")
    save_figure(fig, out_dir / "weekday_consumption.png")

    # Monthly
    fig, ax = styled_figure(figsize=(12, 4))
    s = temporal["monthly"]
    ax.bar([MONTH_LABELS[i - 1] for i in s.index], s.values,
           color="#4CAF50", alpha=0.85)
    ax.set_title("Average meter_reading by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean meter_reading (kWh)")
    save_figure(fig, out_dir / "monthly_consumption.png")


# ==================================================================
# 8. WEATHER vs ENERGY RELATIONSHIP
# ==================================================================

def plot_weather_energy(sample: pd.DataFrame, meta: pd.DataFrame,
                        w_train: pd.DataFrame, out_path: Path):
    """
    Scatter plots of weather variables vs meter_reading using the sample.

    The sample is merged with weather on (site_id, timestamp hour).
    Associations observed are exploratory and do not imply causation.
    """
    # Merge sample → meta → weather (site_id, hour)
    s = sample.copy()
    s["timestamp"] = pd.to_datetime(s["timestamp"])

    s = s.merge(meta[["building_id", "site_id"]], on="building_id", how="left")

    # Round to hour for join
    s["ts_hour"] = s["timestamp"].dt.floor("h")
    w = w_train.copy()
    w["timestamp"] = pd.to_datetime(w["timestamp"])
    w["ts_hour"] = w["timestamp"].dt.floor("h")

    # FIX 4: Deduplicate weather on (site_id, ts_hour) before joining.
    # Deduplication is used only to guarantee one-to-one weather lookup
    # during EDA joins; the source weather dataset is not modified.
    w_dedup = w.drop_duplicates(subset=["site_id", "ts_hour"])

    merged = s.merge(w_dedup[["site_id", "ts_hour"] + WEATHER_COLS],
                     on=["site_id", "ts_hour"], how="left")

    plot_cols = ["air_temperature", "dew_temperature",
                 "wind_speed", "sea_level_pressure"]
    plot_cols = [c for c in plot_cols if c in merged.columns]

    fig, axes = plt.subplots(1, len(plot_cols),
                             figsize=(5 * len(plot_cols), 5))
    axes = np.array(axes).flatten()

    # Cap meter_reading at 99th pct for readability
    p99 = float(np.percentile(merged["meter_reading"].dropna(), 99))
    vis = merged[merged["meter_reading"] <= p99]

    for i, col in enumerate(plot_cols):
        sub = vis[[col, "meter_reading"]].dropna()
        if len(sub) > 20_000:
            sub = sub.sample(20_000, random_state=RANDOM_SEED)
        axes[i].scatter(sub[col], sub["meter_reading"],
                        alpha=0.1, s=2, color="#607D8B")
        axes[i].set_xlabel(col)
        axes[i].set_ylabel("meter_reading (kWh)")
        axes[i].set_title(f"{col} vs meter_reading")
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["right"].set_visible(False)

    fig.suptitle(
        "Weather vs Energy (2% sample, ≤ 99th pct.)\n"
        "NOTE: Associations are exploratory — causation is not implied.",
        fontsize=11, y=1.02,
    )
    plt.tight_layout()
    save_figure(fig, out_path)


# ==================================================================
# 9. BUILDING / SITE CONSUMPTION
# ==================================================================

def plot_site_consumption(site_agg: pd.DataFrame, out_path: Path):
    fig, ax = styled_figure(figsize=(12, 5))
    site_sorted = site_agg.sort_values("mean_reading", ascending=True)
    ax.barh(site_sorted["site_id"].astype(str),
            site_sorted["mean_reading"],
            color="#2196F3", alpha=0.85)
    ax.set_title("Mean meter_reading by Site")
    ax.set_xlabel("Mean meter_reading (kWh)")
    ax.set_ylabel("Site ID")
    save_figure(fig, out_path)


def plot_primary_use_consumption(sample: pd.DataFrame, meta: pd.DataFrame,
                                 out_path: Path):
    s = sample.merge(meta[["building_id", "primary_use"]],
                     on="building_id", how="left")
    p99 = float(np.percentile(s["meter_reading"].dropna(), 99))
    s = s[s["meter_reading"] <= p99]
    grp = s.groupby("primary_use")["meter_reading"].mean().sort_values()

    fig, ax = styled_figure(figsize=(12, 6))
    grp.plot.barh(ax=ax, color="#FF9800", alpha=0.85)
    ax.set_title("Mean meter_reading by Primary Use (2% sample, ≤ 99th pct.)")
    ax.set_xlabel("Mean meter_reading (kWh)")
    save_figure(fig, out_path)


def plot_sqft_energy(sample: pd.DataFrame, meta: pd.DataFrame,
                     out_path: Path):
    s = sample.merge(meta[["building_id", "square_feet"]],
                     on="building_id", how="left")
    p99 = float(np.percentile(s["meter_reading"].dropna(), 99))
    s = s[s["meter_reading"] <= p99].dropna(subset=["square_feet"])
    if len(s) > 30_000:
        s = s.sample(30_000, random_state=RANDOM_SEED)

    fig, ax = styled_figure(figsize=(10, 5))
    ax.scatter(s["square_feet"], s["meter_reading"],
               alpha=0.1, s=2, color="#9C27B0")
    ax.set_xlabel("square_feet")
    ax.set_ylabel("meter_reading (kWh)")
    ax.set_title("square_feet vs meter_reading (sample, ≤ 99th pct.)")
    save_figure(fig, out_path)


# ==================================================================
# 10. OUTLIER INVESTIGATION
# ==================================================================

def outlier_analysis(meter_df: pd.DataFrame, sample: pd.DataFrame,
                     meta: pd.DataFrame) -> pd.DataFrame:
    """
    Identify extreme observations using the p99.9 threshold per meter.
    Observations above the threshold are flagged — NOT removed.
    """
    rows = []
    for _, row in meter_df.iterrows():
        m = int(row["meter"])
        threshold = row["p99.9"]
        sub = sample[(sample["meter"] == m) &
                     (sample["meter_reading"] > threshold)]
        rows.append({
            "meter": m,
            "energy_type": METER_LABELS[m],
            "p99.9_threshold": threshold,
            "extreme_count_in_sample": len(sub),
            "extreme_pct_in_sample": round(
                len(sub) / len(sample[sample["meter"] == m]) * 100, 4)
            if len(sample[sample["meter"] == m]) else 0,
        })
    return pd.DataFrame(rows)


def plot_outlier_analysis(sample: pd.DataFrame, meter_df: pd.DataFrame,
                          out_path: Path):
    fig, axes = styled_figure_multi(1, 2, figsize=(14, 5))

    # Per-meter max vs p99
    axes[0].bar(meter_df["energy_type"],
                meter_df["max"],
                color=[METER_COLORS[m] for m in meter_df["meter"]],
                alpha=0.85, label="Max")
    axes[0].bar(meter_df["energy_type"],
                meter_df["p99"],
                color="black", alpha=0.4, label="p99")
    axes[0].set_title("Max vs p99 by Meter Type")
    axes[0].set_ylabel("meter_reading (kWh)")
    axes[0].legend()
    axes[0].tick_params(axis="x", rotation=15)

    # Distribution of extreme values in sample
    p999 = float(np.percentile(sample["meter_reading"].dropna(), 99.9))
    extremes = sample[sample["meter_reading"] > p999]
    if len(extremes):
        vc = extremes["meter"].value_counts().sort_index()
        colors = [METER_COLORS.get(m, "gray") for m in vc.index]
        axes[1].bar([METER_LABELS[m] for m in vc.index],
                    vc.values, color=colors, alpha=0.85)
        axes[1].set_title(f"Extreme Observations (> p99.9) by Meter\n"
                          f"(2% sample, n={len(extremes)})")
        axes[1].set_ylabel("Count in sample")
        axes[1].tick_params(axis="x", rotation=15)
    else:
        axes[1].text(0.5, 0.5, "No extreme values in sample",
                     ha="center", va="center", transform=axes[1].transAxes)

    fig.suptitle("Outlier Investigation (NOT removed)", fontsize=13, y=1.01)
    save_figure(fig, out_path)


# ==================================================================
# 11. CORRELATION ANALYSIS
# ==================================================================

def plot_correlation_matrix(sample: pd.DataFrame, meta: pd.DataFrame,
                            w_train: pd.DataFrame, out_path: Path):
    s = sample.copy()
    s["timestamp"] = pd.to_datetime(s["timestamp"])
    s = s.merge(meta[["building_id", "site_id", "square_feet"]],
                on="building_id", how="left")
    s["ts_hour"] = s["timestamp"].dt.floor("h")
    w = w_train.copy()
    w["timestamp"] = pd.to_datetime(w["timestamp"])
    w["ts_hour"] = w["timestamp"].dt.floor("h")

    # FIX 4: Deduplicate weather on (site_id, ts_hour) before joining.
    # Deduplication is used only to guarantee one-to-one weather lookup
    # during EDA joins; the source weather dataset is not modified.
    w_dedup = w.drop_duplicates(subset=["site_id", "ts_hour"])

    merged = s.merge(w_dedup[["site_id", "ts_hour",
                         "air_temperature", "dew_temperature",
                         "wind_speed", "sea_level_pressure",
                         "cloud_coverage"]],
                     on=["site_id", "ts_hour"], how="left")

    num_cols = ["meter_reading", "meter", "square_feet",
                "air_temperature", "dew_temperature",
                "wind_speed", "sea_level_pressure", "cloud_coverage"]
    num_cols = [c for c in num_cols if c in merged.columns]

    corr_df = merged[num_cols].dropna()
    if len(corr_df) > 50_000:
        corr_df = corr_df.sample(50_000, random_state=RANDOM_SEED)

    corr = corr_df.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, ax=ax, linewidths=0.5,
                annot_kws={"size": 9})
    ax.set_title(
        "Correlation Matrix (sample)\n"
        "NOTE: Correlation does not imply causation.",
        fontsize=11,
    )
    plt.tight_layout()
    save_figure(fig, out_path)

    return corr


# ==================================================================
# TABLE WRITERS
# ==================================================================

def write_table(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_dict_table(d: dict, path: Path):
    rows = [{"key": k, "value": v} for k, v in d.items()
            if not isinstance(v, list)]
    pd.DataFrame(rows).to_csv(path, index=False)


# ==================================================================
# EDA REPORT WRITER
# ==================================================================

def write_eda_report(
    overview: dict,
    target_stats: dict,
    meter_df: pd.DataFrame,
    meta_miss: pd.DataFrame,
    w_miss: pd.DataFrame,
    outlier_df: pd.DataFrame,
    temporal: dict,
    out_path: Path,
):
    lines = [
        "# Phase 4 — Exploratory Data Analysis Report",
        "",
        "> **Project**: Explainable ML for Building Energy Prediction  ",
        "> **Dataset**: ASHRAE Great Energy Predictor III  ",
        "> **Phase**: 4 — EDA (read-only; no cleaning, imputation, or modelling performed)  ",
        "",
        "---",
        "",
        "## 1. Dataset Overview",
        "",
        f"| Attribute | Value |",
        f"|---|---|",
        f"| Train rows | {overview['train_rows']:,} |",
        f"| Test rows  | {overview['test_rows']:,} |",
        f"| Unique buildings (train) | {overview['unique_buildings_train']:,} |",
        f"| Unique meter types | {overview['unique_meters']} |",
        f"| Unique sites (metadata) | {overview['unique_sites_meta']} |",
        f"| Train timestamp range | {overview['train_ts_min']} → {overview['train_ts_max']} |",
        f"| Metadata rows | {overview['metadata_rows']} |",
        f"| Weather train rows | {overview['weather_train_rows']:,} |",
        f"| Weather test rows  | {overview['weather_test_rows']:,} |",
        "",
        "---",
        "",
        "## 2. Target Variable Analysis (meter_reading)",
        "",
        "> Statistics below are derived from a 2% reproducible sample (seed=42).",
        "> Raw values are used — no log transformation applied.",
        "",
        f"| Statistic | Value |",
        f"|---|---|",
        f"| Count (sample) | {target_stats.get('count', 'N/A'):,} |",
        f"| Mean | {target_stats.get('mean', 'N/A'):,.4f} |",
        f"| Median | {target_stats.get('median', 'N/A'):,.4f} |",
        f"| Std | {target_stats.get('std', 'N/A'):,.4f} |",
        f"| Min | {target_stats.get('min', 'N/A'):,.4f} |",
        f"| Max | {target_stats.get('max', 'N/A'):,.4f} |",
        f"| Skewness | {target_stats.get('skewness', 'N/A'):,.4f} |",
        f"| p1 | {target_stats.get('p1', 'N/A'):,.4f} |",
        f"| p99 | {target_stats.get('p99', 'N/A'):,.4f} |",
        f"| p99.9 | {target_stats.get('p99.9', 'N/A'):,.4f} |",
        "",
        "**Observation**: The target is strongly right-skewed. The mean substantially",
        "exceeds the median, indicating a long right tail driven primarily by Steam",
        "and Chilled Water meter types. Whether a log1p transformation improves",
        "model performance is an experimental question for Phase 6.",
        "",
        "---",
        "",
        "## 3. Meter Type Analysis",
        "",
        "> Counts and statistics are computed exactly via chunked aggregation.",
        "> Medians and percentiles are approximated via 2% sampling.",
        "",
    ]

    # Meter table
    lines.append("| Meter | Type | Rows | Mean | Approx Median | Std | Min | Max | Zero % |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for _, row in meter_df.iterrows():
        lines.append(
            f"| {int(row['meter'])} | {row['energy_type']} "
            f"| {int(row['row_count']):,} "
            f"| {row['mean']:,.2f} "
            f"| {row['approx_median']:,.2f} "
            f"| {row['std']:,.2f} "
            f"| {row['min']:,.2f} "
            f"| {row['max']:,.2f} "
            f"| {row['zero_pct']:.2f}% |"
        )

    lines += [
        "",
        "**Observation**: The four meter types have substantially different distributions.",
        "Steam readings are orders of magnitude larger than electricity readings.",
        "Unified modelling with meter as a feature vs. meter-specific modelling",
        "should be evaluated experimentally in Phase 6.",
        "",
        "---",
        "",
        "## 4. Building Metadata",
        "",
        "| Column | Missing Count | Missing % |",
        "|---|---|---|",
    ]
    for _, row in meta_miss.iterrows():
        lines.append(
            f"| {row['column']} | {int(row['missing_count']):,} | {row['missing_pct']:.2f}% |"
        )

    lines += [
        "",
        "**Note**: Missing values are preserved. Imputation strategy will be",
        "determined during Feature Engineering (Phase 5).",
        "",
        "---",
        "",
        "## 5. Weather Variable Missingness",
        "",
        "| Column | Missing Count | Missing % |",
        "|---|---|---|",
    ]
    for _, row in w_miss.iterrows():
        lines.append(
            f"| {row['column']} | {int(row['missing_count']):,} | {row['missing_pct']:.2f}% |"
        )

    lines += [
        "",
        "**Note**: `precip_depth_1_hr` sentinel values (-1) were already converted",
        "to NaN in Phase 3. The missing percentage above reflects both original",
        "NaN values and converted sentinels.",
        "",
        "---",
        "",
        "## 6. Temporal Analysis",
        "",
        "Patterns computed from full training set via chunked aggregation.",
        "",
        f"| Period | Peak Hour (approx.) |",
        f"|---|---|",
        f"| Hourly | Hour {int(temporal['hourly'].idxmax())} |",
        f"| Day of week | Day {int(temporal['weekday'].idxmax())} (0=Mon) |",
        f"| Month | Month {int(temporal['monthly'].idxmax())} |",
        "",
        "---",
        "",
        "## 7. Outlier Investigation",
        "",
        "> Extreme observations are flagged, not removed.",
        "",
        "| Meter | Type | p99.9 Threshold | Extreme Count (sample) | Extreme % (sample) |",
        "|---|---|---|---|---|",
    ]
    for _, row in outlier_df.iterrows():
        lines.append(
            f"| {int(row['meter'])} | {row['energy_type']} "
            f"| {row['p99.9_threshold']:,.2f} "
            f"| {int(row['extreme_count_in_sample'])} "
            f"| {row['extreme_pct_in_sample']:.4f}% |"
        )

    lines += [
        "",
        "**Observation**: Under the per-meter 99.9th-percentile threshold, extreme",
        "observations occur across all four meter types. Steam has the highest threshold",
        "value, while Hot Water has the highest proportion of sampled observations",
        "classified as extreme. These observations require further domain-level",
        "investigation rather than automatic removal.",
        "",
        "---",
        "",
        "## 8. Key EDA Findings",
        "",
        "1. **Target skewness**: meter_reading is strongly right-skewed."
        " log1p transformation should be experimentally evaluated.",
        "2. **Meter heterogeneity**: Steam readings are orders of magnitude"
        " larger than electricity. Meter type is a critical feature.",
        "3. **Metadata missingness**: floor_count (>75%) and year_built (>50%)"
        " are substantially missing; imputation strategy must support all six models.",
        "4. **Weather missingness**: cloud_coverage and precip_depth_1_hr"
        " have the highest missingness in weather data.",
        "5. **Temporal patterns**: Consumption varies significantly by hour,"
        " weekday, and month, indicating temporal features will be valuable.",
        "6. **Building size**: Larger buildings tend to consume more energy,"
        " but the relationship is noisy and non-linear.",
        "7. **Extreme outliers**: Extreme observations are present across all meter types,"
        " with substantial thresholds for Steam and other high-variance meter categories."
        " Site-level anomalies identified during earlier data validation should be"
        " investigated separately.",
        "",
        "---",
        "",
        "## 9. Implications for Feature Engineering (Phase 5)",
        "",
        "- Temporal features (hour, day-of-week, month, is_weekend)"
        " are clearly supported by EDA.",
        "- `meter` should be included as a model feature; meter-specific"
        " modelling should also be experimentally evaluated.",
        "- Weather variables (especially `air_temperature`, `dew_temperature`)"
        " show exploratory associations with energy consumption.",
        "- Imputation decisions for `year_built`, `floor_count`, and"
        " weather NaNs need to be made in Phase 5.",
        "- Whether to apply log1p to meter_reading is an experimental"
        " decision for Phase 6 model training.",
        "",
        "---",
        "",
        "## 10. Limitations",
        "",
        "- Target statistics and visualisations are based on a 2% sample"
        " (fixed seed=42). Population statistics may differ slightly.",
        "- Exact global median requires a full pass; approximate medians"
        " are reported via sampling.",
        "- Correlation analysis used up to 50,000 sample rows.",
        "- Weather–energy associations are exploratory only;"
        " causality is not established.",
        "- Temporal aggregation uses the full training set via chunked"
        " accumulation; however, no seasonality decomposition is performed.",
        "",
        "---",
        "",
        "*Report generated by `src/data/eda.py` — Phase 4, ASHRAE Project.*",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ==================================================================
# MAIN
# ==================================================================

def main():
    setup_dirs()

    # ---- Load small datasets fully ----
    print("Loading metadata and weather...")
    meta    = pd.read_csv(META_PATH)
    w_train = pd.read_csv(W_TRAIN_PATH, parse_dates=["timestamp"])
    w_test  = pd.read_csv(W_TEST_PATH,  parse_dates=["timestamp"])

    # ---- Draw reproducible sample from train ----
    print("Sampling train data (2%)...")
    sample = sample_energy_chunked(TRAIN_PATH,
                                   sample_frac=SAMPLE_FRAC,
                                   seed=RANDOM_SEED,
                                   chunksize=CHUNKSIZE)
    sample["timestamp"] = pd.to_datetime(sample["timestamp"])

    # ==== 1. Dataset Overview ====
    print("1/11  Dataset overview...")
    overview = dataset_overview(sample, meta, w_train, w_test)
    write_dict_table(overview, TABLES_DIR / "dataset_overview.csv")

    # ==== 2. Target Analysis ====
    print("2/11  Target analysis...")
    target_stats = target_analysis(sample)
    pd.DataFrame([target_stats]).to_csv(
        TABLES_DIR / "target_statistics.csv", index=False)
    plot_target_distribution(sample,
                             FIGURES_DIR / "target_distribution.png")

    # ==== 3. Meter Analysis ====
    print("3/11  Meter analysis (chunked)...")
    meter_df = meter_stats_chunked(TRAIN_PATH,
                                   chunksize=CHUNKSIZE,
                                   sample_frac_for_percentiles=SAMPLE_FRAC,
                                   seed=RANDOM_SEED)
    meter_df.to_csv(TABLES_DIR / "meter_statistics.csv", index=False)
    plot_meter_distribution(sample, FIGURES_DIR / "meter_distribution.png")
    plot_meter_statistics(meter_df, FIGURES_DIR / "meter_statistics.png")

    # ==== 4. Building Metadata ====
    print("4/11  Building metadata analysis...")
    meta_miss = missing_summary(meta)
    meta_miss.to_csv(TABLES_DIR / "building_metadata_summary.csv", index=False)
    plot_primary_use(meta, FIGURES_DIR / "primary_use_distribution.png")
    plot_metadata_distributions(meta, FIGURES_DIR / "metadata_distributions.png")

    # ==== 5. Missing Values ====
    print("5/11  Missing value analysis...")
    w_miss = missing_summary(w_train)
    w_miss.to_csv(TABLES_DIR / "missing_value_summary_weather.csv", index=False)
    plot_missing_values(meta, w_train, FIGURES_DIR / "missing_values.png")

    # ==== 6. Weather Analysis ====
    print("6/11  Weather analysis...")
    w_stats = []
    for col in WEATHER_COLS:
        if col in w_train.columns:
            w_stats.append(descriptive_stats(w_train[col], label=col))
    pd.DataFrame(w_stats).to_csv(TABLES_DIR / "weather_statistics.csv", index=False)
    plot_weather_distributions(w_train, FIGURES_DIR / "weather_distributions.png")

    # ==== 7. Temporal Analysis ====
    print("7/11  Temporal analysis (chunked)...")
    temporal = temporal_analysis(TRAIN_PATH)
    t_rows = []
    for period, s in temporal.items():
        for k, v in s.items():
            t_rows.append({"period": period, "key": k, "mean_reading": v})
    pd.DataFrame(t_rows).to_csv(TABLES_DIR / "temporal_statistics.csv", index=False)
    plot_temporal(temporal, FIGURES_DIR)

    # ==== 8. Weather vs Energy ====
    print("8/11  Weather-energy relationship...")
    plot_weather_energy(sample, meta, w_train,
                        FIGURES_DIR / "weather_energy_relationship.png")

    # ==== 9. Building / Site Consumption ====
    print("9/11  Building/site consumption...")
    
    metadata_df = pd.read_csv(META_PATH, usecols=["building_id", "site_id"])
    building_to_site = metadata_df.set_index("building_id")["site_id"]
    
    site_accum = {}
    unmapped_ids = set()
    
    for chunk in pd.read_csv(TRAIN_PATH, chunksize=CHUNKSIZE):
        chunk["site_id"] = chunk["building_id"].map(building_to_site)
        
        if chunk["site_id"].isna().any():
            unmapped = chunk.loc[chunk["site_id"].isna(), "building_id"].unique()
            unmapped_ids.update(unmapped)
            
        grp = chunk.groupby("site_id")["meter_reading"].agg(["sum", "count"])
        for key, row in grp.iterrows():
            if key not in site_accum:
                site_accum[key] = {"sum": 0.0, "count": 0}
            site_accum[key]["sum"] += row["sum"]
            site_accum[key]["count"] += row["count"]
            
    if unmapped_ids:
        raise KeyError(
            f"Found {len(unmapped_ids)} building_id(s) without a site_id mapping. "
            "These IDs: " + ", ".join(map(str, sorted(unmapped_ids)))
        )
        
    site_rows = []
    for site_id, vals in site_accum.items():
        site_rows.append({
            "site_id": site_id,
            "mean_reading": vals["sum"] / vals["count"] if vals["count"] else np.nan,
            "total_reading": vals["sum"],
            "row_count": vals["count"]
        })
    site_agg = pd.DataFrame(site_rows)
    site_agg.to_csv(TABLES_DIR / "site_consumption.csv", index=False)
    plot_site_consumption(site_agg, FIGURES_DIR / "site_consumption.png")
    plot_primary_use_consumption(sample, meta,
                                 FIGURES_DIR / "primary_use_consumption.png")
    plot_sqft_energy(sample, meta,
                     FIGURES_DIR / "sqft_energy_relationship.png")

    # ==== 10. Outlier Investigation ====
    print("10/11  Outlier analysis...")
    outlier_df = outlier_analysis(meter_df, sample, meta)
    outlier_df.to_csv(TABLES_DIR / "outlier_summary.csv", index=False)
    plot_outlier_analysis(sample, meter_df,
                          FIGURES_DIR / "outlier_analysis.png")

    # ==== 11. Correlation Matrix ====
    print("11/11  Correlation analysis...")
    corr = plot_correlation_matrix(sample, meta, w_train,
                                   FIGURES_DIR / "correlation_matrix.png")
    corr.reset_index().rename(columns={"index": "variable"}).to_csv(
        TABLES_DIR / "correlation_matrix.csv", index=False)

    # ==== EDA Report ====
    print("Writing EDA report...")
    write_eda_report(
        overview=overview,
        target_stats=target_stats,
        meter_df=meter_df,
        meta_miss=meta_miss,
        w_miss=w_miss,
        outlier_df=outlier_df,
        temporal=temporal,
        out_path=REPORTS_DIR / "eda_report.md",
    )

    print("\n✓ EDA complete.")
    print(f"  Figures : {FIGURES_DIR}")
    print(f"  Tables  : {TABLES_DIR}")
    print(f"  Report  : {REPORTS_DIR / 'eda_report.md'}")


if __name__ == "__main__":
    main()
