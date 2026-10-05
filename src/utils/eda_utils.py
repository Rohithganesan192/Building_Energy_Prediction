"""
eda_utils.py
============
Reusable utility functions for the ASHRAE EDA phase.

These functions are deliberately kept stateless and side-effect-free
so they can be imported and tested independently.

Rules:
- No modification of raw data.
- No model training.
- No feature engineering.
- No imputation of missing values.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # Non-interactive backend; safe for script execution.
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path


# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------

METER_LABELS = {
    0: "Electricity",
    1: "Chilled Water",
    2: "Steam",
    3: "Hot Water",
}

METER_COLORS = {
    0: "#2196F3",   # blue
    1: "#4CAF50",   # green
    2: "#FF5722",   # deep orange
    3: "#9C27B0",   # purple
}

PERCENTILE_LEVELS = [1, 5, 25, 50, 75, 95, 99, 99.9]

RANDOM_SEED = 42


# ------------------------------------------------------------------
# FIGURE HELPERS
# ------------------------------------------------------------------

def save_figure(fig: plt.Figure, path: Path, dpi: int = 150) -> None:
    """Save a matplotlib figure and close it immediately to free memory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def styled_figure(figsize=(10, 5)) -> tuple:
    """Return a (fig, ax) pair with consistent styling."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax


def styled_figure_multi(nrows=1, ncols=2, figsize=(14, 5)) -> tuple:
    """Return a (fig, axes) pair for multi-panel figures."""
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    for ax in np.array(axes).flatten():
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    return fig, axes


# ------------------------------------------------------------------
# DESCRIPTIVE STATISTICS
# ------------------------------------------------------------------

def descriptive_stats(series: pd.Series, label: str = "") -> dict:
    """
    Compute robust descriptive statistics for a numeric series.

    Parameters
    ----------
    series : pd.Series  (must be numeric, NaN-safe)
    label  : str        (optional human-readable label for the result dict)

    Returns
    -------
    dict with count, mean, median, std, min, max, skewness, and percentiles.
    """
    clean = series.dropna()
    if len(clean) == 0:
        return {"label": label, "count": 0}

    pct = {f"p{p}": float(np.percentile(clean, p)) for p in PERCENTILE_LEVELS}

    result = {
        "label": label,
        "count": int(len(clean)),
        "missing": int(series.isnull().sum()),
        "missing_pct": round(float(series.isnull().sum() / len(series) * 100), 4),
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "std": float(clean.std()),
        "min": float(clean.min()),
        "max": float(clean.max()),
        "skewness": float(clean.skew()),
        **pct,
    }
    return result


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a missing-value summary table for every column in df.

    Returns a DataFrame with columns: column, missing_count, missing_pct.
    """
    total = len(df)
    miss = df.isnull().sum()
    pct  = (miss / total * 100).round(4)
    result = pd.DataFrame({
        "column": miss.index,
        "missing_count": miss.values,
        "missing_pct": pct.values,
    })
    return result.sort_values("missing_pct", ascending=False).reset_index(drop=True)


# ------------------------------------------------------------------
# CHUNKED ENERGY HELPERS
# ------------------------------------------------------------------

def sample_energy_chunked(
    csv_path: Path,
    sample_frac: float = 0.01,
    seed: int = RANDOM_SEED,
    chunksize: int = 1_000_000,
) -> pd.DataFrame:
    """
    Draw a reproducible fractional sample from a large energy CSV
    without loading the entire file into memory.

    Parameters
    ----------
    csv_path    : Path  to train_clean.csv or test_clean.csv
    sample_frac : float fraction of each chunk to keep (default 1%)
    seed        : int   random seed for reproducibility
    chunksize   : int   rows per chunk

    Returns
    -------
    pd.DataFrame  (sample of the full file)
    """
    rng = np.random.default_rng(seed)
    frames = []
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        n = max(1, int(len(chunk) * sample_frac))
        idx = rng.choice(len(chunk), size=n, replace=False)
        # FIX 1: .copy() releases the reference to the full 1M-row chunk
        # so the GC can free it before the next chunk is read.
        frames.append(chunk.iloc[idx].copy())
    return pd.concat(frames, ignore_index=True)


def aggregate_energy_chunked(
    csv_path: Path,
    group_cols: list,
    agg_col: str = "meter_reading",
    chunksize: int = 1_000_000,
) -> pd.DataFrame:
    """
    Aggregate a large energy CSV by group columns without loading it fully.

    Returns a DataFrame with group keys and sum/count columns,
    which is then reduced to mean externally.
    """
    accum = {}
    for chunk in pd.read_csv(csv_path, chunksize=chunksize,
                              parse_dates=["timestamp"]):
        grp = chunk.groupby(group_cols)[agg_col].agg(["sum", "count"])
        for key, row in grp.iterrows():
            key_t = key if isinstance(key, tuple) else (key,)
            if key_t not in accum:
                accum[key_t] = {"sum": 0.0, "count": 0}
            accum[key_t]["sum"]   += row["sum"]
            accum[key_t]["count"] += row["count"]

    rows = []
    for key_t, vals in accum.items():
        row_dict = dict(zip(group_cols, key_t))
        row_dict["mean_reading"] = vals["sum"] / vals["count"] if vals["count"] else np.nan
        row_dict["total_reading"] = vals["sum"]
        row_dict["row_count"] = vals["count"]
        rows.append(row_dict)
    return pd.DataFrame(rows)


def meter_stats_chunked(
    csv_path: Path,
    chunksize: int = 1_000_000,
    sample_frac_for_percentiles: float = 0.02,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Compute per-meter descriptive statistics from a large energy CSV.

    Exact: count, sum, sum-of-squares, min, max, zeros, negatives.
    Approximate (via sampling): median, skewness, percentiles.

    Returns a DataFrame indexed by meter (0-3).
    """
    import math
    # FIX 2: Hard cap on stored samples per meter to bound memory use
    # regardless of sample_frac_for_percentiles setting.
    MAX_SAMPLES = 100_000

    stats = {m: {"count": 0, "sum": 0.0, "sq_sum": 0.0,
                 "min": float("inf"), "max": float("-inf"),
                 "zeros": 0, "negatives": 0, "samples": []}
             for m in [0, 1, 2, 3]}

    rng = np.random.default_rng(seed)

    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        for m in [0, 1, 2, 3]:
            sub = chunk[chunk["meter"] == m]["meter_reading"].dropna()
            if len(sub) == 0:
                continue
            s = stats[m]
            s["count"]     += len(sub)
            s["sum"]       += float(sub.sum())
            s["sq_sum"]    += float((sub ** 2).sum())
            s["min"]        = min(s["min"], float(sub.min()))
            s["max"]        = max(s["max"], float(sub.max()))
            s["zeros"]     += int((sub == 0).sum())
            s["negatives"] += int((sub < 0).sum())
            # Only collect more samples if cap not yet reached.
            remaining_capacity = MAX_SAMPLES - len(s["samples"])
            if remaining_capacity > 0:
                n_sample = min(
                    max(1, int(len(sub) * sample_frac_for_percentiles)),
                    remaining_capacity,
                )
                idx = rng.choice(len(sub), size=n_sample, replace=False)
                s["samples"].extend(sub.iloc[idx].tolist())

    rows = []
    for m in [0, 1, 2, 3]:
        s = stats[m]
        if s["count"] == 0:
            continue
        mean = s["sum"] / s["count"]
        var  = max(0.0, (s["sq_sum"] / s["count"]) - mean ** 2)
        std  = math.sqrt(var)
        samp = np.array(s["samples"])
        pcts = {f"p{p}": float(np.percentile(samp, p)) for p in PERCENTILE_LEVELS}
        rows.append({
            "meter": m,
            "energy_type": METER_LABELS[m],
            "row_count": s["count"],
            "mean": round(mean, 4),
            "approx_median": round(float(np.median(samp)), 4),
            "std": round(std, 4),
            "min": s["min"],
            "max": s["max"],
            "zero_count": s["zeros"],
            "zero_pct": round(s["zeros"] / s["count"] * 100, 4),
            "negative_count": s["negatives"],
            **pcts,
        })
    return pd.DataFrame(rows)
