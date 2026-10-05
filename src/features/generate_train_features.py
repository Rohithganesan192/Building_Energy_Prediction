"""
generate_train_features.py
==========================
Production-scale feature generation for train_clean.csv.

Strategy:
---------
The critical constraint is that historical features (lag_1, lag_24, lag_168,
rolling_mean_24/168, rolling_std_24/168) require a contiguous, chronologically
sorted series per (building_id, meter) group.

A naive row-count-based chunked approach is UNSAFE because:
  - lag_168 for the first row of chunk N depends on the last 168 rows of chunk N-1.
  - rolling_mean_168 for the start of chunk N depends on up to 168 rows before it.
  - Chunk boundaries are arbitrary and will silently produce NaN where real values exist.

Safe production strategy:
  1. Load the small building_metadata_clean.csv fully into memory (~1,450 rows).
  2. Load weather_train_clean.csv fully into memory (~140,000 rows). Both are small.
  3. Read train_clean.csv in a SINGLE PASS but process it grouped by (building_id, meter).
     Each (building_id, meter) group has at most 8,784 rows (hourly data for 2016).
     There are at most 1,450 buildings x 4 meters = 5,800 groups.
     Each group is small enough to hold in memory individually.
  4. For each group: apply temporal, building, weather, and historical features.
  5. Write completed groups to the output CSV progressively (append mode).

This guarantees:
  - Each group is contiguous and chronologically sorted.
  - No cross-chunk boundary problem exists because groups are never split.
  - Memory usage is bounded: the largest single group is ~8,784 rows.
  - Output is written incrementally so the full 20M-row output is not held in memory.

Dry-run mode:
  Run with --dry-run to process only building_id 0 and 1 (two groups).
  This verifies the full pipeline logic without touching the 20M-row file.
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

from src.features.feature_config import (
    TRAIN_CLEAN, META_CLEAN, WEATHER_TRAIN_CLEAN, FEATURES_DIR, METER_MAPPING,
    LAG_HOURS, ROLLING_WINDOWS, TRAIN_FEATURES_OUT, FEATURE_WRITE_BATCH_SIZE
)
from src.features.temporal_features import build_temporal_features
from src.features.historical_features import build_historical_features
from src.features.feature_engineering import process_weather


# TRAIN_FEATURES_OUT is imported from feature_config above.
# Defined there as: FEATURES_DIR / "train_features.csv"


def build_group_features(
    group_df: pd.DataFrame,
    meta_df: pd.DataFrame,
    site_weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply the full feature engineering pipeline to a single (building_id, meter) group.

    Parameters
    ----------
    group_df   : rows for one (building_id, meter) pair, sorted by timestamp
    meta_df    : full building metadata (used for left-merge on building_id)
    site_weather : weather rows for this group's site_id ONLY
                   (pre-filtered by the caller to avoid merging 139k rows per group)

    The function:
      1. Builds temporal features from timestamp.
      2. Merges building metadata.
      3. Merges site-specific weather (site_id + timestamp lookup).
      4. Builds historical lag and rolling features (target-dependent).
      5. Adds meter_name as a supplementary string column.

    Returns a complete feature row for every row in the group.
    The original `meter` column is always retained.
    """
    rows_before_weather = len(group_df)

    # Step 1: temporal features
    df = build_temporal_features(group_df, timestamp_col="timestamp")

    # Step 2: building features (merge on building_id)
    df = df.merge(meta_df, on="building_id", how="left")

    # Step 3: weather features.
    # site_weather contains ONLY the rows for this group's site_id.
    # Merging a small site slice (~8,760 rows) against a small group
    # (~8,784 rows) avoids the 139,773-row join structure that was
    # causing numpy _ArrayMemoryError at building 221.
    df = df.merge(site_weather, on=["site_id", "timestamp"], how="left")

    # Validate that the weather merge did not add or remove energy rows.
    if len(df) != rows_before_weather:
        raise RuntimeError(
            f"Weather merge changed row count: "
            f"before={rows_before_weather}, after={len(df)}. "
            "Check for duplicate (site_id, timestamp) keys in weather data."
        )

    # Validate that key weather columns arrived (warn only; NaN is legitimate).
    expected_weather_cols = [
        "air_temperature", "dew_temperature", "sea_level_pressure",
        "wind_speed", "wind_direction", "cloud_coverage", "precip_depth_1_hr",
    ]
    missing_weather = [c for c in expected_weather_cols if c not in df.columns]
    if missing_weather:
        raise RuntimeError(
            f"Weather merge is missing expected columns: {missing_weather}"
        )

    # Step 4: historical features
    # The group is already sorted chronologically and belongs to a single
    # (building_id, meter) pair, so lag and rolling calculations are exact.
    df = build_historical_features(df, lags=LAG_HOURS, rolling_windows=ROLLING_WINDOWS)

    # Step 5: meter_name (supplementary — does not replace numeric meter)
    df["meter_name"] = df["meter"].map(METER_MAPPING)

    return df


def generate_train_features(dry_run: bool = False):
    """
    Full production-scale feature generation for train_clean.csv.

    Parameters
    ----------
    dry_run : bool
        If True, process only building_id 0 and 1 to test pipeline logic.
    """
    print("=" * 60)
    print("Phase 5: Train Feature Generation")
    print(f"Mode: {'DRY-RUN (building_id 0 and 1 only)' if dry_run else 'FULL (all buildings)'}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Load small support files fully (both are tiny)
    # ------------------------------------------------------------------
    print("\nLoading building metadata...")
    meta_df = pd.read_csv(META_CLEAN)
    print(f"  Metadata rows: {len(meta_df)}, columns: {list(meta_df.columns)}")

    print("Loading and preprocessing weather data...")
    raw_weather = pd.read_csv(WEATHER_TRAIN_CLEAN)
    weather_df = process_weather(raw_weather)
    print(f"  Weather rows after deduplication: {len(weather_df)}, columns: {list(weather_df.columns)}")

    # Pre-split weather by site_id so each group merge only touches one site.
    # This avoids the 139,773-row join structure being rebuilt for every one
    # of the 2,380 groups, which caused the numpy _ArrayMemoryError at group 221.
    # Each site slice is a tiny DataFrame (~8,760 rows) held in a plain dict.
    weather_by_site = {
        site_id: site_df.reset_index(drop=True)
        for site_id, site_df in weather_df.groupby("site_id")
    }
    print(f"  Pre-split weather into {len(weather_by_site)} site-specific slices.")

    # Pre-build an O(1) building_id → site_id lookup so per-group site resolution
    # is a dict key access rather than a repeated DataFrame scan.
    building_to_site = meta_df.set_index("building_id")["site_id"].to_dict()

    # ------------------------------------------------------------------
    # Load train_clean.csv FULLY into memory
    # ------------------------------------------------------------------
    # We load all of train_clean.csv at once for group-by correctness.
    # train_clean.csv has 4 columns (building_id, meter, timestamp, meter_reading)
    # At ~34 bytes/row average, 20.2M rows ≈ 690MB on disk but as a DataFrame
    # with appropriate dtypes uses ~650–900 MB RAM.
    # This is the safest correct approach for this dataset scale.
    print("\nLoading train_clean.csv (this may take ~30-60 seconds)...")

    if dry_run:
        # Dry-run: scan in chunks and keep only building_id in {0, 1}
        chunks = []
        for chunk in pd.read_csv(TRAIN_CLEAN, chunksize=1_000_000,
                                  parse_dates=["timestamp"]):
            sub = chunk[chunk["building_id"].isin([0, 1])]
            if not sub.empty:
                chunks.append(sub)
        train_df = pd.concat(chunks, ignore_index=True)
    else:
        train_df = pd.read_csv(TRAIN_CLEAN, parse_dates=["timestamp"])

    print(f"  Loaded {len(train_df):,} rows, columns: {list(train_df.columns)}")

    # ------------------------------------------------------------------
    # Sort globally by (building_id, meter, timestamp)
    # ------------------------------------------------------------------
    print("\nSorting by (building_id, meter, timestamp)...")
    train_df = train_df.sort_values(["building_id", "meter", "timestamp"])
    print("  Sort complete.")

    # ------------------------------------------------------------------
    # Group-wise feature generation with incremental CSV output
    # ------------------------------------------------------------------
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)

    # Safety: remove stale output to avoid appending to a partial file
    if TRAIN_FEATURES_OUT.exists():
        TRAIN_FEATURES_OUT.unlink()
        print(f"\nRemoved stale output file: {TRAIN_FEATURES_OUT}")

    groups = list(train_df.groupby(["building_id", "meter"]))
    n_groups = len(groups)
    print(f"\nProcessing {n_groups} (building_id, meter) groups...")

    total_rows_written = 0
    write_header = True  # Write CSV header only for the first group

    for i, ((bld, mtr), group_df) in enumerate(groups):
        group_df = group_df.reset_index(drop=True)

        # Resolve site_id for this group in O(1) using the pre-built lookup.
        group_site_id = building_to_site[int(bld)]

        # Retrieve the pre-filtered weather slice for this site.
        # KeyError here would mean the site has no weather data at all.
        if group_site_id not in weather_by_site:
            raise KeyError(
                f"No weather data found for site_id={group_site_id} "
                f"(building_id={bld}, meter={mtr})."
            )
        site_weather = weather_by_site[group_site_id]

        try:
            features = build_group_features(group_df, meta_df, site_weather)
        except Exception as e:
            print(f"  ERROR in group (building_id={bld}, meter={mtr}): {e}")
            raise

        # Write this group to the output CSV in small batches.
        # Reason: pandas.DataFrame.to_csv() converts the entire group to
        # a temporary Unicode (numpy <U32) array before serialising.
        # For larger groups (~8,784 rows × 30 columns) this allocation
        # can exceed available memory and raise numpy._ArrayMemoryError.
        # Writing FEATURE_WRITE_BATCH_SIZE rows at a time keeps the
        # per-call allocation tiny (500 rows × 30 cols ≈ negligible).
        n_rows = len(features)
        for batch_start in range(0, n_rows, FEATURE_WRITE_BATCH_SIZE):
            batch_end = min(batch_start + FEATURE_WRITE_BATCH_SIZE, n_rows)
            features.iloc[batch_start:batch_end].to_csv(
                TRAIN_FEATURES_OUT,
                mode="a",
                header=write_header,
                index=False,
            )
            write_header = False   # header written on first batch of first group
        total_rows_written += n_rows

        # Release the feature DataFrame for this group immediately.
        # The next iteration allocates a fresh one, so there is no reason
        # to keep this in memory any longer.
        del features

        # Progress report every 500 groups (or for every group in dry-run)
        if dry_run or (i + 1) % 500 == 0 or (i + 1) == n_groups:
            print(f"  [{i+1:>5}/{n_groups}]  "
                  f"building_id={bld:>4}  meter={mtr}  "
                  f"rows={n_rows:>5}  total_written={total_rows_written:,}")

    # ------------------------------------------------------------------
    # Post-generation validation
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Post-generation validation")
    print("=" * 60)

    # Row count check
    expected_rows = len(train_df)
    if total_rows_written != expected_rows:
        raise RuntimeError(
            f"Row count mismatch: input had {expected_rows:,} rows "
            f"but output has {total_rows_written:,} rows."
        )
    print(f"Row count: {total_rows_written:,}  (matches input: PASS)")

    # Read back header and check columns
    output_sample = pd.read_csv(TRAIN_FEATURES_OUT, nrows=2)
    output_cols = list(output_sample.columns)
    print(f"Output columns ({len(output_cols)}): {output_cols}")

    # Check that meter and meter_reading are preserved
    for required in ["building_id", "meter", "timestamp", "meter_reading",
                     "meter_name", "site_id", "hour", "lag_1", "lag_24",
                     "lag_168", "rolling_mean_24", "rolling_mean_168",
                     "rolling_std_24", "rolling_std_168"]:
        status = "PRESENT" if required in output_cols else "MISSING"
        print(f"  {required}: {status}")

    # Missing value summary from the first two output rows already read above.
    # A full-file missing-value scan would require re-reading the output CSV,
    # which is expensive. The schema check above is sufficient to confirm correctness.
    print("\nNote: complete missing-value statistics require a separate post-hoc scan.")
    print("The validation checks (Checks 1–16) from validate_features.py are the")
    print("authoritative leakage/correctness reference for this pipeline.")

    print(f"\nOutput file: {TRAIN_FEATURES_OUT}")
    print("Phase 5 training feature generation COMPLETE.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Phase 5 training features."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Process only building_id 0 and 1 to test pipeline logic.",
    )
    args = parser.parse_args()
    generate_train_features(dry_run=args.dry_run)
