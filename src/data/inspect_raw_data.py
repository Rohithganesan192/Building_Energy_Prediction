import pandas as pd
import numpy as np
import json
import sys
import math
from pathlib import Path

def check_environment():
    env_info = {
        "python_version": sys.version.split(" ")[0],
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "imports": {}
    }
    
    libraries = ["sklearn", "xgboost", "lightgbm", "catboost", "shap"]
    for lib in libraries:
        try:
            __import__(lib)
            env_info["imports"][lib] = "Success"
        except ImportError:
            env_info["imports"][lib] = "Failed"
            
    return env_info

def get_basic_info(df, file_size):
    example_values = {}
    if not df.empty:
        for c in df.columns:
            valid_val = df[c].dropna()
            example_values[c] = str(valid_val.iloc[0]) if len(valid_val) > 0 else None

    return {
        "file_size_mb": file_size,
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {c: str(d) for c, d in df.dtypes.items()},
        "example_values": example_values,
        "missing_counts": df.isnull().sum().to_dict(),
        "missing_percentages": (df.isnull().sum() / len(df) * 100).to_dict() if len(df) > 0 else {}
    }

def inspect_metadata(path):
    df = pd.read_csv(path)
    info = get_basic_info(df, path.stat().st_size / (1024*1024))
    
    info["unique_site_ids"] = df['site_id'].nunique() if 'site_id' in df else 0
    info["unique_building_ids"] = df['building_id'].nunique() if 'building_id' in df else 0
    info["primary_use_categories"] = df['primary_use'].nunique() if 'primary_use' in df else 0
    info["primary_uses"] = df['primary_use'].unique().tolist() if 'primary_use' in df else []
    
    info["min_year_built"] = float(df['year_built'].min()) if 'year_built' in df else None
    info["max_year_built"] = float(df['year_built'].max()) if 'year_built' in df else None
    
    info["min_square_feet"] = float(df['square_feet'].min()) if 'square_feet' in df else None
    info["max_square_feet"] = float(df['square_feet'].max()) if 'square_feet' in df else None
    
    info["min_floor_count"] = float(df['floor_count'].min()) if 'floor_count' in df else None
    info["max_floor_count"] = float(df['floor_count'].max()) if 'floor_count' in df else None
    
    meta_bids = set(df['building_id'].unique()) if 'building_id' in df else set()
    bids_to_sites = dict(zip(df['building_id'], df['site_id'])) if 'building_id' in df and 'site_id' in df else {}
    
    return info, meta_bids, bids_to_sites

def inspect_weather(path):
    df = pd.read_csv(path)
    info = get_basic_info(df, path.stat().st_size / (1024*1024))
    
    info["unique_site_ids"] = df['site_id'].nunique() if 'site_id' in df else 0
    info["min_timestamp"] = df['timestamp'].min() if 'timestamp' in df else None
    info["max_timestamp"] = df['timestamp'].max() if 'timestamp' in df else None
    info["weather_variables"] = [c for c in df.columns if c not in ['site_id', 'timestamp']]
    
    stats = {}
    for col in info["weather_variables"]:
        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            stats[col] = {
                "min": float(desc.get("min", 0)),
                "max": float(desc.get("max", 0)),
                "mean": float(desc.get("mean", 0))
            }
    info["numerical_statistics"] = stats
    
    weather_sites = set(df['site_id'].unique()) if 'site_id' in df else set()
    return info, weather_sites

def inspect_large_csv(path, is_train=False):
    num_rows = 0
    missing = {}
    unique_bids = set()
    unique_meters = set()
    unique_ts = set()
    cols = []
    dtypes = {}
    example_values = {}
    
    target_count = 0
    target_sum = 0
    target_sq_sum = 0
    target_min = float('inf')
    target_max = float('-inf')
    sample_median = []
    
    chunk_duplicate_counts = []
    first = True
    
    for chunk in pd.read_csv(path, chunksize=2_000_000):
        if first:
            cols = list(chunk.columns)
            dtypes = {c: str(d) for c, d in chunk.dtypes.items()}
            missing = {c: 0 for c in cols}
            if not chunk.empty:
                for c in cols:
                    valid_val = chunk[c].dropna()
                    example_values[c] = str(valid_val.iloc[0]) if len(valid_val) > 0 else None
            first = False
            
        num_rows += len(chunk)
        for c in cols:
            missing[c] += int(chunk[c].isnull().sum())
            
        if 'building_id' in chunk.columns:
            unique_bids.update(chunk['building_id'].unique())
        if 'meter' in chunk.columns:
            unique_meters.update(chunk['meter'].unique())
        if 'timestamp' in chunk.columns:
            unique_ts.update(chunk['timestamp'].unique())
            
        # Check intra-chunk duplicates
        chunk_duplicate_counts.append(int(chunk.duplicated().sum()))
            
        if is_train and 'meter_reading' in chunk.columns:
            v = chunk['meter_reading'].dropna()
            if len(v) > 0:
                target_count += len(v)
                target_sum += float(v.sum())
                target_sq_sum += float((v ** 2).sum())
                target_min = min(target_min, float(v.min()))
                target_max = max(target_max, float(v.max()))
                sz = min(len(v), 5000)
                sample_median.extend(v.sample(sz).tolist())
                
    info = {
        "file_size_mb": path.stat().st_size / (1024*1024),
        "num_rows": num_rows,
        "num_columns": len(cols),
        "column_names": cols,
        "dtypes": dtypes,
        "example_values": example_values,
        "missing_counts": missing,
        "missing_percentages": {k: (v/num_rows)*100 for k,v in missing.items()} if num_rows else {},
        "unique_building_ids_count": len(unique_bids),
        "unique_meters": len(unique_meters),
        "chunk_duplicates_sum": sum(chunk_duplicate_counts),
        "has_target_column": 'meter_reading' in cols
    }
    
    if unique_ts:
        sorted_ts = sorted(list(unique_ts))
        info["min_timestamp"] = sorted_ts[0]
        info["max_timestamp"] = sorted_ts[-1]
    else:
        info["min_timestamp"] = None
        info["max_timestamp"] = None
        
    if is_train and target_count > 0:
        mean = target_sum / target_count
        var = (target_sq_sum / target_count) - (mean ** 2)
        std = math.sqrt(var) if var > 0 else 0
        med = float(np.median(sample_median)) if sample_median else None
        info["target_stats"] = {
            "name": "meter_reading",
            "count": target_count,
            "missing_count": missing.get("meter_reading", 0),
            "min": target_min,
            "max": target_max,
            "mean": mean,
            "approximate_median_from_sample": med,
            "std": std
        }
        
    return info, unique_bids

def inspect_submission(path):
    df_head = pd.read_csv(path, nrows=5)
    cols = list(df_head.columns)
    
    num_rows = 0
    missing = {c: 0 for c in cols}
    first = True
    dtypes = {}
    
    for chunk in pd.read_csv(path, chunksize=5_000_000):
        if first:
            dtypes = {c: str(d) for c, d in chunk.dtypes.items()}
            first = False
        num_rows += len(chunk)
        for c in cols:
            missing[c] += int(chunk[c].isnull().sum())
            
    example_values = {}
    if not df_head.empty:
        for c in cols:
            example_values[c] = str(df_head[c].iloc[0])

    return {
        "file_size_mb": path.stat().st_size / (1024*1024),
        "num_rows": num_rows,
        "num_columns": len(cols),
        "column_names": cols,
        "dtypes": dtypes,
        "example_values": example_values,
        "missing_counts": missing,
        "missing_percentages": {k: (v/num_rows)*100 for k,v in missing.items()} if num_rows else {},
        "first_five_rows": df_head.to_dict(orient='records'),
        "identifier_column": cols[0] if cols else None
    }

def check_relationships(train_bids, test_bids, meta_bids, bids_to_sites, wtrain_sites, wtest_sites):
    train_missing_meta = len(train_bids - meta_bids)
    test_missing_meta = len(test_bids - meta_bids)
    
    train_sites = {bids_to_sites[b] for b in train_bids if b in bids_to_sites}
    test_sites = {bids_to_sites[b] for b in test_bids if b in bids_to_sites}
    
    unmatched_wtrain = list(train_sites - wtrain_sites)
    unmatched_wtest = list(test_sites - wtest_sites)
    
    return {
        "train_buildings_missing_from_metadata": train_missing_meta,
        "test_buildings_missing_from_metadata": test_missing_meta,
        "train_sites_missing_from_weather": len(unmatched_wtrain),
        "test_sites_missing_from_weather": len(unmatched_wtest),
        "unmatched_wtrain_sites": unmatched_wtrain,
        "unmatched_wtest_sites": unmatched_wtest
    }

def generate_markdown(env, data, out_path):
    md = [
        "# ASHRAE Raw Data Profile",
        "",
        "## FACTS COMPUTED FROM DATA",
        ""
    ]
    
    md.extend([
        "### 1. Environment Details",
        f"- Python: {env['python_version']}",
        f"- Pandas: {env['pandas_version']}",
        f"- Numpy: {env['numpy_version']}",
        "- Imports:"
    ])
    for lib, status in env['imports'].items():
        md.append(f"  - {lib}: {status}")
    md.append("")
        
    md.extend([
        "### 2. Dataset Files Summary",
        "| File | Size (MB) | Rows | Columns |",
        "|---|---|---|---|"
    ])
    files_to_report = [
        ("train.csv", "train"),
        ("test.csv", "test"),
        ("building_metadata.csv", "metadata"),
        ("weather_train.csv", "weather_train"),
        ("weather_test.csv", "weather_test"),
        ("sample_submission.csv", "submission")
    ]
    for fname, k in files_to_report:
        if k in data:
            md.append(f"| {fname} | {data[k]['file_size_mb']:.2f} | {data[k]['num_rows']} | {data[k]['num_columns']} |")
            
    md.extend(["", "### 3. Train Data"])
    if 'train' in data:
        t = data['train']
        md.append(f"- **Rows**: {t['num_rows']}")
        md.append(f"- **Columns**: {t['num_columns']}")
        md.append(f"- **Temporal Coverage**: {t['min_timestamp']} to {t['max_timestamp']}")
        md.append(f"- **Unique Buildings**: {t['unique_building_ids_count']}")
        md.append(f"- **Unique Meters**: {t['unique_meters']}")
        md.append(f"- **Intra-chunk Duplicates**: {t['chunk_duplicates_sum']}")
        if "target_stats" in t:
            ts = t["target_stats"]
            md.append("- **Target Name**: meter_reading")
            md.append(f"- **Target Stats**: Count={ts['count']}, Min={ts['min']:.2f}, Max={ts['max']:.2f}, Mean={ts['mean']:.2f}, Approx Median={ts['approximate_median_from_sample']:.2f}, Std={ts['std']:.2f}")
            
    md.extend(["", "### 4. Test Data"])
    if 'test' in data:
        t = data['test']
        md.append(f"- **Rows**: {t['num_rows']}")
        md.append(f"- **Columns**: {t['num_columns']}")
        md.append(f"- **Temporal Coverage**: {t['min_timestamp']} to {t['max_timestamp']}")
        md.append(f"- **Unique Buildings**: {t['unique_building_ids_count']}")
        md.append(f"- **Unique Meters**: {t['unique_meters']}")
        md.append(f"- **Intra-chunk Duplicates**: {t['chunk_duplicates_sum']}")
        md.append(f"- **Has Target Column?**: {t['has_target_column']}")
        
    md.extend(["", "### 5. Building Metadata"])
    if 'metadata' in data:
        m = data['metadata']
        md.append(f"- **Rows**: {m['num_rows']}")
        md.append(f"- **Unique Sites**: {m['unique_site_ids']}")
        md.append(f"- **Unique Buildings**: {m['unique_building_ids']}")
        md.append(f"- **Primary Uses**: {m['primary_use_categories']} categories")
        md.append(f"- **Year Built Range**: {m['min_year_built']} to {m['max_year_built']}")
        md.append(f"- **Square Feet Range**: {m['min_square_feet']} to {m['max_square_feet']}")
        md.append(f"- **Floor Count Range**: {m['min_floor_count']} to {m['max_floor_count']}")
        
    md.extend(["", "### 6. Weather Coverage"])
    for k, name in [("weather_train", "Weather Train"), ("weather_test", "Weather Test")]:
        if k in data:
            w = data[k]
            md.append(f"#### {name}")
            md.append(f"- **Rows**: {w['num_rows']}")
            md.append(f"- **Unique Sites**: {w['unique_site_ids']}")
            md.append(f"- **Temporal Coverage**: {w['min_timestamp']} to {w['max_timestamp']}")
            
    md.extend(["", "### 7. Sample Submission"])
    if 'submission' in data:
        s = data['submission']
        md.append(f"- **Rows**: {s['num_rows']}")
        md.append(f"- **Columns**: {s['num_columns']}")
        md.append(f"- **Identifier Column**: {s['identifier_column']}")
        md.append(f"- **First Row Example**: {json.dumps(s['first_five_rows'][0])}")
        
    md.extend(["", "### 8. Dataset Relationships"])
    if 'relationships' in data:
        r = data['relationships']
        md.append(f"- Train buildings missing from metadata: {r['train_buildings_missing_from_metadata']}")
        md.append(f"- Test buildings missing from metadata: {r['test_buildings_missing_from_metadata']}")
        md.append(f"- Train site_ids lacking weather_train coverage: {r['train_sites_missing_from_weather']}")
        md.append(f"- Test site_ids lacking weather_test coverage: {r['test_sites_missing_from_weather']}")
        if r['unmatched_wtrain_sites']:
            md.append(f"- Unmatched weather_train site_ids: {r['unmatched_wtrain_sites']}")
        if r['unmatched_wtest_sites']:
            md.append(f"- Unmatched weather_test site_ids: {r['unmatched_wtest_sites']}")

    md.extend(["", "### 9. Missing-Value Summary"])
    for fname, k in files_to_report:
        if k in data and 'missing_percentages' in data[k]:
            missing_cols = {col: pct for col, pct in data[k]['missing_percentages'].items() if pct > 0}
            if missing_cols:
                md.append(f"**{fname}**:")
                for col, pct in missing_cols.items():
                    md.append(f"- {col}: {pct:.2f}% missing")
            else:
                md.append(f"**{fname}**: No missing values.")
        md.append("")
            
    md.extend([
        "",
        "## LIMITATIONS OF THE INSPECTION",
        "- **Duplicate Detection**: A complete global duplicate check across all rows in train.csv and test.csv was not performed due to extreme memory constraints. Only duplicates within individual 2-million-row chunks were counted.",
        "- **Median Calculation**: True median for `meter_reading` in train.csv cannot be computed precisely in chunks without excessive memory overhead. The reported median is an `approximate_median_from_sample` derived from random chunk subsamples.",
        "- **Schema/Example Generation**: Example values are selected solely from the first available valid row in a given column."
    ])
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

def main():
    base_dir = Path("data/raw")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    env_info = check_environment()
    print(f"Python: {env_info['python_version']}, pandas: {env_info['pandas_version']}")
    
    print("Inspecting metadata...")
    metadata, meta_bids, bids_to_sites = inspect_metadata(base_dir / "building_metadata.csv")
    
    print("Inspecting weather train...")
    weather_train, wtrain_sites = inspect_weather(base_dir / "weather_train.csv")
    
    print("Inspecting weather test...")
    weather_test, wtest_sites = inspect_weather(base_dir / "weather_test.csv")
    
    print("Inspecting submission...")
    submission = inspect_submission(base_dir / "sample_submission.csv")
    
    print("Inspecting train (chunked)...")
    train, train_bids = inspect_large_csv(base_dir / "train.csv", is_train=True)
    
    print("Inspecting test (chunked)...")
    test, test_bids = inspect_large_csv(base_dir / "test.csv", is_train=False)
    
    print("Evaluating relationships...")
    rels = check_relationships(train_bids, test_bids, meta_bids, bids_to_sites, wtrain_sites, wtest_sites)
    
    all_data = {
        "metadata": metadata,
        "weather_train": weather_train,
        "weather_test": weather_test,
        "submission": submission,
        "train": train,
        "test": test,
        "relationships": rels,
        "environment": env_info
    }
    
    print("Saving json...")
    with open(reports_dir / "raw_data_profile.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
        
    print("Saving markdown...")
    generate_markdown(env_info, all_data, reports_dir / "raw_data_profile.md")
    print("Inspection script finished successfully.")

if __name__ == "__main__":
    main()
