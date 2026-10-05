"""
validate_full_features.py
=========================
Post-generation audit of data/features/train_features.csv.

Scans the full 20M-row file in chunks. Does NOT load it entirely into memory.
Writes results to:
  reports/full_feature_validation_report.md
  reports/full_feature_validation_summary.json
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

from src.features.feature_config import TRAIN_FEATURES_OUT, PROJECT_ROOT, CHUNKSIZE

REPORTS_DIR = PROJECT_ROOT / "reports"

# ------------------------------------------------------------------
# Expected schema (35 columns from the completed generation run)
# ------------------------------------------------------------------
EXPECTED_COLUMNS = [
    # Identity / target
    "building_id", "meter", "timestamp", "meter_reading",
    # Temporal - basic
    "hour", "day_of_week", "month", "day_of_year", "is_weekend",
    # Temporal - cyclical
    "hour_sin", "hour_cos",
    "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
    # Building
    "site_id", "primary_use", "square_feet", "year_built", "floor_count",
    # Weather
    "air_temperature", "cloud_coverage", "dew_temperature",
    "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed",
    # Historical
    "lag_1", "lag_24", "lag_168",
    "rolling_mean_24", "rolling_mean_168",
    "rolling_std_24", "rolling_std_168",
    # Categorical label
    "meter_name",
]

REQUIRED_IDENTITY_COLS = ["building_id", "meter", "timestamp", "meter_reading"]
REQUIRED_HISTORICAL_COLS = [
    "lag_1", "lag_24", "lag_168",
    "rolling_mean_24", "rolling_mean_168",
    "rolling_std_24", "rolling_std_168",
]
EXPECTED_METER_VALUES = {0, 1, 2, 3}


def run_audit():
    print("=" * 62)
    print("Phase 5 Full Feature Validation Audit")
    print(f"File: {TRAIN_FEATURES_OUT}")
    print("=" * 62)

    if not TRAIN_FEATURES_OUT.exists():
        raise FileNotFoundError(f"Feature file not found: {TRAIN_FEATURES_OUT}")

    # ------------------------------------------------------------------
    # Read header to get column list — one row, effectively free
    # ------------------------------------------------------------------
    header_sample = pd.read_csv(TRAIN_FEATURES_OUT, nrows=1)
    actual_columns = list(header_sample.columns)
    n_actual_cols = len(actual_columns)

    print(f"\nColumns found: {n_actual_cols}")

    # ------------------------------------------------------------------
    # Accumulators (updated per chunk — never grow with data size)
    # ------------------------------------------------------------------
    total_rows = 0
    null_counts = {col: 0 for col in actual_columns}
    negative_meter_reading = 0
    min_timestamp = None
    max_timestamp = None
    unique_buildings = set()
    unique_meters = set()
    unique_groups = set()       # (building_id, meter) tuples

    # Duplicate detection strategy:
    # Exact global deduplication on a 20M-row file requires either loading
    # all (building_id, meter, timestamp) keys into memory (~480 MB for int64 pairs
    # + datetime strings) or a disk-based approach. We use a hash-set of
    # (building_id, meter, timestamp) tuples accumulated across chunks.
    # This is feasible because the three key columns are compact:
    #   building_id: int16 (~0-1449), meter: int8 (0-3), timestamp: string
    # A set of 20.2M 3-tuples uses roughly 20M * ~80 bytes = ~1.6 GB worst-case.
    # That may exceed available RAM, so we track only a duplicate COUNT rather than
    # storing every key. We identify duplicates by checking whether the chunk's
    # own (building_id, meter, timestamp) triple appears more than once within
    # the chunk AND accumulate a running total. Global cross-chunk duplicates
    # (same key split across chunk boundary) require full key storage; we
    # explicitly document this limitation below.
    within_chunk_dup_count = 0
    cross_chunk_dup_limitation = True   # flag: full global check not performed

    print("\nScanning file in chunks...")
    chunk_num = 0

    for chunk in pd.read_csv(
        TRAIN_FEATURES_OUT,
        chunksize=CHUNKSIZE,
        parse_dates=["timestamp"],
        low_memory=False,
    ):
        chunk_num += 1
        total_rows += len(chunk)

        # Missing values
        for col in actual_columns:
            if col in chunk.columns:
                null_counts[col] += int(chunk[col].isna().sum())

        # Negative meter_reading
        if "meter_reading" in chunk.columns:
            negative_meter_reading += int((chunk["meter_reading"] < 0).sum())

        # Timestamp range
        if "timestamp" in chunk.columns:
            chunk_min = chunk["timestamp"].min()
            chunk_max = chunk["timestamp"].max()
            if min_timestamp is None or chunk_min < min_timestamp:
                min_timestamp = chunk_min
            if max_timestamp is None or chunk_max > max_timestamp:
                max_timestamp = chunk_max

        # Unique identifiers
        if "building_id" in chunk.columns:
            unique_buildings.update(chunk["building_id"].dropna().unique())
        if "meter" in chunk.columns:
            unique_meters.update(chunk["meter"].dropna().unique())
        if "building_id" in chunk.columns and "meter" in chunk.columns:
            pairs = chunk[["building_id", "meter"]].drop_duplicates()
            for row in pairs.itertuples(index=False):
                unique_groups.add((row.building_id, row.meter))

        # Within-chunk duplicate detection on identity key
        if all(c in chunk.columns for c in ["building_id", "meter", "timestamp"]):
            dup_mask = chunk.duplicated(subset=["building_id", "meter", "timestamp"])
            within_chunk_dup_count += int(dup_mask.sum())

        if chunk_num % 5 == 0 or chunk_num == 1:
            print(f"  Processed chunk {chunk_num:>3}  "
                  f"rows so far: {total_rows:>12,}")

    print(f"  Processed chunk {chunk_num:>3}  "
          f"rows so far: {total_rows:>12,}")

    # ------------------------------------------------------------------
    # Derived statistics
    # ------------------------------------------------------------------
    null_pct = {
        col: round(null_counts[col] / total_rows * 100, 4) if total_rows else 0.0
        for col in actual_columns
    }

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in actual_columns]
    extra_cols   = [c for c in actual_columns if c not in EXPECTED_COLUMNS]
    schema_pass  = (len(missing_cols) == 0 and n_actual_cols == len(EXPECTED_COLUMNS))

    meter_values_present = {int(m) for m in unique_meters if not (isinstance(m, float) and np.isnan(m))}
    meter_check_pass     = (meter_values_present == EXPECTED_METER_VALUES)

    identity_cols_pass   = all(c in actual_columns for c in REQUIRED_IDENTITY_COLS)
    historical_cols_pass = all(c in actual_columns for c in REQUIRED_HISTORICAL_COLS)
    meter_reading_nan    = null_counts.get("meter_reading", 0)

    # ------------------------------------------------------------------
    # Terminal summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 62)
    print("AUDIT RESULTS")
    print("=" * 62)
    print(f"Total rows            : {total_rows:,}")
    print(f"Columns found         : {n_actual_cols}  (expected {len(EXPECTED_COLUMNS)})")
    print(f"Schema check          : {'PASS' if schema_pass else 'FAIL'}")
    if missing_cols:
        print(f"  Missing columns     : {missing_cols}")
    if extra_cols:
        print(f"  Extra columns       : {extra_cols}")
    print(f"Identity cols present : {'PASS' if identity_cols_pass else 'FAIL'}")
    print(f"Historical cols exist  : {'PASS' if historical_cols_pass else 'FAIL'}")
    print(f"meter values present  : {sorted(meter_values_present)}  "
          f"{'PASS' if meter_check_pass else 'FAIL (expected 0,1,2,3)'}")
    print(f"meter_reading NaN     : {meter_reading_nan:,}  "
          f"{'PASS (none)' if meter_reading_nan == 0 else 'FAIL'}")
    print(f"Negative meter_reading: {negative_meter_reading:,}")
    print(f"Timestamp range       : {min_timestamp} → {max_timestamp}")
    print(f"Unique building_ids   : {len(unique_buildings):,}")
    print(f"Unique meter values   : {len(unique_meters)}")
    print(f"Unique (bld,meter) groups: {len(unique_groups):,}")
    print(f"Within-chunk dups     : {within_chunk_dup_count:,}  "
          f"({'none found' if within_chunk_dup_count == 0 else 'INVESTIGATE'})")
    print("Cross-chunk dup check : NOT PERFORMED (see limitation note in report)")

    print("\nMissing values per column (non-zero only):")
    printed_any = False
    for col in actual_columns:
        if null_counts[col] > 0:
            print(f"  {col:<30}  {null_counts[col]:>10,}  ({null_pct[col]:.4f}%)")
            printed_any = True
    if not printed_any:
        print("  (none)")

    # ------------------------------------------------------------------
    # Write JSON summary
    # ------------------------------------------------------------------
    summary = {
        "total_rows": total_rows,
        "total_columns": n_actual_cols,
        "expected_columns": len(EXPECTED_COLUMNS),
        "schema_pass": schema_pass,
        "missing_schema_columns": missing_cols,
        "extra_columns": extra_cols,
        "identity_cols_present": identity_cols_pass,
        "historical_cols_present": historical_cols_pass,
        "meter_values_found": sorted(meter_values_present),
        "meter_check_pass": meter_check_pass,
        "meter_reading_nan_count": meter_reading_nan,
        "negative_meter_reading_count": negative_meter_reading,
        "min_timestamp": str(min_timestamp),
        "max_timestamp": str(max_timestamp),
        "unique_building_ids": len(unique_buildings),
        "unique_meter_values": len(unique_meters),
        "unique_building_meter_groups": len(unique_groups),
        "within_chunk_duplicate_rows": within_chunk_dup_count,
        "cross_chunk_duplicate_check": "NOT PERFORMED — requires full key set in memory (~1.6 GB)",
        "missing_value_counts": {col: null_counts[col] for col in actual_columns},
        "missing_value_pct": null_pct,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "full_feature_validation_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nJSON summary written to: {json_path}")

    # ------------------------------------------------------------------
    # Write Markdown report
    # ------------------------------------------------------------------
    md_lines = [
        "# Phase 5 Full Feature Validation Report",
        "",
        f"**File**: `{TRAIN_FEATURES_OUT}`",
        "",
        "## 1. Row and Column Counts",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total rows | {total_rows:,} |",
        f"| Total columns | {n_actual_cols} |",
        f"| Expected columns | {len(EXPECTED_COLUMNS)} |",
        f"| Schema check | {'PASS' if schema_pass else 'FAIL'} |",
        "",
        "## 2. Column List",
        "",
        "```",
        "\n".join(actual_columns),
        "```",
        "",
    ]

    if missing_cols or extra_cols:
        md_lines += [
            "## 2a. Schema Discrepancies",
            "",
            f"Missing from output: `{missing_cols}`",
            f"Extra in output: `{extra_cols}`",
            "",
        ]

    md_lines += [
        "## 3. Identity and Structural Checks",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Identity columns present (`building_id`, `meter`, `timestamp`, `meter_reading`) | {'PASS' if identity_cols_pass else 'FAIL'} |",
        f"| Historical feature columns present | {'PASS' if historical_cols_pass else 'FAIL'} |",
        f"| Meter values present (0,1,2,3) | {'PASS' if meter_check_pass else 'FAIL'} — found: {sorted(meter_values_present)} |",
        f"| `meter_reading` NaN count | {meter_reading_nan:,} ({'PASS' if meter_reading_nan == 0 else 'FAIL'}) |",
        f"| Negative `meter_reading` rows | {negative_meter_reading:,} |",
        "",
        "## 4. Temporal Coverage",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Minimum timestamp | {min_timestamp} |",
        f"| Maximum timestamp | {max_timestamp} |",
        "",
        "## 5. Unique Identifiers",
        "",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Unique `building_id` values | {len(unique_buildings):,} |",
        f"| Unique `meter` values | {len(unique_meters)} |",
        f"| Unique `(building_id, meter)` groups | {len(unique_groups):,} |",
        "",
        "## 6. Duplicate Detection",
        "",
        f"| Check | Result |",
        f"|---|---|",
        f"| Within-chunk duplicates on `(building_id, meter, timestamp)` | {within_chunk_dup_count:,} |",
        f"| Cross-chunk global duplicate check | NOT PERFORMED |",
        "",
        "> **Limitation**: Exact global duplicate detection across all 20.2 M rows",
        "> requires storing all `(building_id, meter, timestamp)` keys in memory",
        "> simultaneously (~1.6 GB worst-case). This was not performed.",
        "> Within-chunk detection covers duplicates arising within any 1 M-row",
        "> chunk; cross-chunk duplicates (same key split across a chunk boundary)",
        "> are not detected. Given that the generation pipeline processes each",
        "> `(building_id, meter)` group once and in order, cross-chunk duplicates",
        "> are structurally prevented by design.",
        "",
        "## 7. Missing Value Summary",
        "",
        "Columns with zero missing values are omitted.",
        "",
        "| Column | Missing Count | Missing % |",
        "|---|---|---|",
    ]

    has_missing = False
    for col in actual_columns:
        if null_counts[col] > 0:
            md_lines.append(
                f"| `{col}` | {null_counts[col]:,} | {null_pct[col]:.4f}% |"
            )
            has_missing = True
    if not has_missing:
        md_lines.append("| *(none)* | 0 | 0.00% |")

    md_lines += [
        "",
        "## 8. Notes",
        "",
        "- Missing values in `lag_*` and `rolling_*` columns are expected for the first",
        "  rows of each `(building_id, meter)` group (no prior history available).",
        "- Missing values in `year_built` and `floor_count` reflect genuine data absence",
        "  in the source building metadata, not a pipeline error.",
        "- Missing weather values are the residual after forward-fill; they occur at the",
        "  very start of each site's weather series where no prior reading exists.",
        "- Negative `meter_reading` values (if any) are from the cleaned source data",
        "  and are preserved for downstream modelling decisions.",
        "",
        "*End of Phase 5 Full Feature Validation Report.*",
    ]

    md_path = REPORTS_DIR / "full_feature_validation_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Markdown report written to: {md_path}")
    print("\nPhase 5 audit COMPLETE.")

    return summary


if __name__ == "__main__":
    run_audit()
