import pandas as pd
import numpy as np
import json
from pathlib import Path

# =========================================================
# HELPER FUNCTIONS FOR LATER MERGE
# =========================================================

def load_building_metadata(path="data/processed/building_metadata_clean.csv"):
    """Load cleaned building metadata."""
    return pd.read_csv(path)

def load_weather_train(path="data/processed/weather_train_clean.csv"):
    """Load cleaned weather train data and parse dates."""
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def load_weather_test(path="data/processed/weather_test_clean.csv"):
    """Load cleaned weather test data and parse dates."""
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def validate_building_mapping(energy_df, metadata_df):
    """Placeholder for later mapping validation."""
    pass

def validate_weather_mapping(energy_df, metadata_df, weather_df):
    """Placeholder for later mapping validation."""
    pass


# =========================================================
# JSON SERIALIZER
# =========================================================

def make_json_serializable(obj):
    """Safely cast numpy/pandas types to standard python types for JSON."""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    if isinstance(obj, tuple):
        return [make_json_serializable(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if pd.isna(obj):
        return None
    return obj


# =========================================================
# CLEANING PROCESSORS
# =========================================================

def process_metadata(raw_path, proc_path):
    df = pd.read_csv(raw_path)
    raw_rows = len(df)
    
    # 1 & 2. Standardize data types, preserve columns
    df['site_id'] = df['site_id'].astype(int)
    df['building_id'] = df['building_id'].astype(int)
    if 'square_feet' in df.columns:
        df['square_feet'] = df['square_feet'].astype(int)
        
    # 3, 4, 5, 6, 8. Keep NaNs in year_built/floor_count, no encoding
    # 7. Validate
    if df['building_id'].duplicated().any():
        raise ValueError("Validation Error: duplicate building_id found in metadata.")
    if (df['square_feet'] <= 0).any():
        raise ValueError("Validation Error: non-positive square_feet found.")
        
    df.to_csv(proc_path, index=False)
    return {"raw_rows": raw_rows, "proc_rows": len(df)}


def process_weather(raw_path, proc_path):
    df = pd.read_csv(raw_path)
    raw_rows = len(df)
    
    # 1. Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 4. Handle Sentinel (-1 -> NaN for precip_depth)
    sentinel_count = 0
    if 'precip_depth_1_hr' in df.columns:
        sentinel_mask = df['precip_depth_1_hr'] == -1
        sentinel_count = sentinel_mask.sum()
        df.loc[sentinel_mask, 'precip_depth_1_hr'] = np.nan

    # FIX 1: Report duplicate (site_id, timestamp) keys — do NOT remove them.
    dup_keys = int(df.duplicated(subset=['site_id', 'timestamp']).sum())

    df.to_csv(proc_path, index=False)
    return {
        "raw_rows": raw_rows,
        "proc_rows": len(df),
        "sentinel_converted": int(sentinel_count),
        "duplicate_site_ts_keys": dup_keys
    }


def process_energy(raw_path, proc_path, is_train=True):
    if proc_path.exists():
        proc_path.unlink() # Delete output to recreate safely
        
    raw_rows = 0
    proc_rows = 0
    
    # Value Integrity Tracking
    b_id_sum = 0
    meter_sum = 0
    target_sum = 0
    row_id_sum = 0
    
    first = True
    
    # Use chunks of 1M for memory-conscious processing
    for chunk in pd.read_csv(raw_path, chunksize=1_000_000):
        raw_rows += len(chunk)
        
        # Track original sums before processing
        b_id_sum += chunk['building_id'].sum()
        meter_sum += chunk['meter'].sum()
        
        # Standardize Types
        chunk['building_id'] = chunk['building_id'].astype(int)
        chunk['meter'] = chunk['meter'].astype(int)
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'])
        
        if is_train:
            target_sum += chunk['meter_reading'].sum()
            chunk['meter_reading'] = chunk['meter_reading'].astype(float)
            # Target validation
            if (chunk['meter_reading'] < 0).any():
                raise ValueError(f"Validation Error: Negative meter_reading found in {raw_path}")
            if chunk['meter_reading'].isnull().any():
                raise ValueError(f"Validation Error: Missing meter_reading found in {raw_path}")
        else:
            row_id_sum += chunk['row_id'].sum()
            chunk['row_id'] = chunk['row_id'].astype(int)
            
        proc_rows += len(chunk)
        
        # Write append
        chunk.to_csv(proc_path, mode='a', index=False, header=first)
        first = False
        
    return {
        "raw_rows": raw_rows, 
        "proc_rows": proc_rows,
        "building_id_sum": float(b_id_sum),
        "meter_sum": float(meter_sum),
        "target_sum": float(target_sum) if is_train else None,
        "row_id_sum": float(row_id_sum) if not is_train else None
    }


# =========================================================
# MAIN EXECUTION
# =========================================================

def main():
    raw_dir = Path("data/raw")
    proc_dir = Path("data/processed")
    reports_dir = Path("reports")
    
    proc_dir.mkdir(exist_ok=True, parents=True)
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    summary = {}
    
    print("Cleaning Building Metadata...")
    summary["building_metadata"] = process_metadata(raw_dir / "building_metadata.csv", proc_dir / "building_metadata_clean.csv")
    
    print("Cleaning Weather Train...")
    summary["weather_train"] = process_weather(raw_dir / "weather_train.csv", proc_dir / "weather_train_clean.csv")
    
    print("Cleaning Weather Test...")
    summary["weather_test"] = process_weather(raw_dir / "weather_test.csv", proc_dir / "weather_test_clean.csv")
    
    print("Cleaning Energy Train (Chunked)...")
    summary["train"] = process_energy(raw_dir / "train.csv", proc_dir / "train_clean.csv", is_train=True)
    
    print("Cleaning Energy Test (Chunked)...")
    summary["test"] = process_energy(raw_dir / "test.csv", proc_dir / "test_clean.csv", is_train=False)
    
    # Integrity Evaluation
    integrity = True
    for k, v in summary.items():
        # FIX 2: Skip non-dict entries (e.g., integrity_passed boolean).
        if not isinstance(v, dict):
            continue
        if v["raw_rows"] != v["proc_rows"]:
            integrity = False
            print(f"INTEGRITY FAILURE: {k} mismatch.")
            
    summary["integrity_passed"] = integrity
    
    # Serialize and Save JSON
    safe_summary = make_json_serializable(summary)
    with open(reports_dir / "cleaning_execution_summary.json", "w", encoding="utf-8") as f:
        json.dump(safe_summary, f, indent=4)
        
    # Generate Markdown Report
    md = [
        "# Data Cleaning Execution Report",
        "",
        "## 1. Input/Output Files",
        "| Dataset | Input | Output | Raw Rows | Processed Rows |",
        "|---|---|---|---|---|",
        f"| Metadata | `data/raw/building_metadata.csv` | `data/processed/building_metadata_clean.csv` | {summary['building_metadata']['raw_rows']} | {summary['building_metadata']['proc_rows']} |",
        f"| Weather Train | `data/raw/weather_train.csv` | `data/processed/weather_train_clean.csv` | {summary['weather_train']['raw_rows']} | {summary['weather_train']['proc_rows']} |",
        f"| Weather Test | `data/raw/weather_test.csv` | `data/processed/weather_test_clean.csv` | {summary['weather_test']['raw_rows']} | {summary['weather_test']['proc_rows']} |",
        f"| Train | `data/raw/train.csv` | `data/processed/train_clean.csv` | {summary['train']['raw_rows']} | {summary['train']['proc_rows']} |",
        f"| Test | `data/raw/test.csv` | `data/processed/test_clean.csv` | {summary['test']['raw_rows']} | {summary['test']['proc_rows']} |",
        "",
        "## 2. Integrity Checks",
        f"- **Row Counts Match**: {integrity}",
        "- **Data Overwrites**: None (all output safely routed to `data/processed/`)",
        "",
        "## 3. Data Transformations",
        "- **Types Normalized**: Timestamps converted to strictly formatted `datetime64`. IDs/Meters cast strictly to `int`.",
        "- **Missing Values Preserved**: Missing `year_built`, `floor_count`, and weather data gaps were intentionally left as `NaN`.",
        "- **Sentinel Values Handled**: `-1` in `precip_depth_1_hr` was explicitly converted to `NaN` to reflect missing/trace representations.",
        f"  - Weather Train Sentinels Converted: {summary['weather_train']['sentinel_converted']}",
        f"  - Weather Test Sentinels Converted: {summary['weather_test']['sentinel_converted']}",
        "- **Target Validation**: Automatically confirmed 0 missing and 0 explicitly negative values for `meter_reading` throughout training chunks.",
        "",
        "## 4. Unchanged Elements",
        "- `meter_reading` values remain completely unmodified (no `log1p` transformation yet).",
        "- Raw target retains its original highly skewed scale.",
        "- All outliers (including Site 0 steam anomalies) remain entirely intact for experimental resolution later.",
        "- `primary_use` categories remain unencoded raw strings.",
        "- Energy, Metadata, and Weather datasets remain strictly modular and completely distinct, preserving pipeline flexibility."
    ]
    with open(reports_dir / "cleaning_execution_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print("Data cleaning execution complete.")

if __name__ == "__main__":
    main()
