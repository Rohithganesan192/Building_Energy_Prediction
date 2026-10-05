import pandas as pd
import numpy as np
import json
import math
from pathlib import Path

def validate_metadata(path):
    df = pd.read_csv(path)
    
    # Missing
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    # Validation
    stats = {}
    for col in ['year_built', 'floor_count', 'square_feet']:
        if col in df:
            valid_vals = df[col].dropna()
            stats[col] = {
                "min": float(valid_vals.min()) if len(valid_vals) else None,
                "max": float(valid_vals.max()) if len(valid_vals) else None,
                "mean": float(valid_vals.mean()) if len(valid_vals) else None,
                "missing": int(missing[col]),
                "missing_pct": float(missing_pct[col]),
                "zeros": int((valid_vals == 0).sum()),
                "negatives": int((valid_vals < 0).sum())
            }
            
            # Percentiles for outliers
            if len(valid_vals):
                pcts = [1, 5, 25, 50, 75, 95, 99, 99.9]
                stats[col]["percentiles"] = {f"p{p}": float(np.percentile(valid_vals, p)) for p in pcts}

    # Duplicates
    dup_keys = int(df.duplicated(subset=['building_id']).sum())
    
    return {
        "rows": len(df),
        "primary_uses": df['primary_use'].nunique() if 'primary_use' in df else 0,
        "stats": stats,
        "duplicate_building_ids": dup_keys
    }

def validate_weather(path):
    df = pd.read_csv(path)
    
    # Timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ts_min = df['timestamp'].min()
    ts_max = df['timestamp'].max()
    hourly = (df['timestamp'].dt.minute == 0).all() and (df['timestamp'].dt.second == 0).all()
    
    # Duplicates
    dup_keys = int(df.duplicated(subset=['site_id', 'timestamp']).sum())
    
    # Stats
    vars_to_check = ['air_temperature', 'cloud_coverage', 'dew_temperature', 'precip_depth_1_hr', 'sea_level_pressure', 'wind_direction', 'wind_speed']
    stats = {}
    
    for col in vars_to_check:
        if col in df:
            valid = df[col].dropna()
            stats[col] = {
                "missing": int(df[col].isnull().sum()),
                "missing_pct": float(df[col].isnull().sum() / len(df) * 100),
                "min": float(valid.min()) if len(valid) else None,
                "max": float(valid.max()) if len(valid) else None,
                "mean": float(valid.mean()) if len(valid) else None,
                "std": float(valid.std()) if len(valid) else None,
                "zeros": int((valid == 0).sum()),
                "negatives": int((valid < 0).sum())
            }
            if len(valid):
                pcts = [1, 5, 25, 50, 75, 95, 99, 99.9]
                stats[col]["percentiles"] = {f"p{p}": float(np.percentile(valid, p)) for p in pcts}
                
    return {
        "min_ts": ts_min.strftime("%Y-%m-%d %H:%M:%S"),
        "max_ts": ts_max.strftime("%Y-%m-%d %H:%M:%S"),
        "is_hourly": hourly,
        "duplicate_keys": dup_keys,
        "stats": stats
    }

def validate_train(path):
    meter_stats = {0: {}, 1: {}, 2: {}, 3: {}}
    for m in meter_stats:
        meter_stats[m] = {
            "count": 0, "sum": 0, "sq_sum": 0,
            "min": float('inf'), "max": float('-inf'),
            "zeros": 0, "negatives": 0, "buildings": set(),
            "samples": []
        }
        
    total_rows = 0
    missing_target = 0
    min_ts, max_ts = None, None
    is_hourly = True
    
    # For global duplicates, we'll try to store hashes of (b, m, t) if RAM permits.
    # To be memory safe, we will just count intra-chunk duplicates and clearly report the limitation.
    chunk_dups = 0

    first = True
    for chunk in pd.read_csv(path, chunksize=2_000_000):
        total_rows += len(chunk)
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'])
        
        c_min = chunk['timestamp'].min()
        c_max = chunk['timestamp'].max()
        if min_ts is None or c_min < min_ts: min_ts = c_min
        if max_ts is None or c_max > max_ts: max_ts = c_max
        
        if not ((chunk['timestamp'].dt.minute == 0).all() and (chunk['timestamp'].dt.second == 0).all()):
            is_hourly = False
            
        chunk_dups += chunk.duplicated(subset=['building_id', 'meter', 'timestamp']).sum()
        
        missing_target += chunk['meter_reading'].isnull().sum()
        
        for m in [0, 1, 2, 3]:
            m_df = chunk[(chunk['meter'] == m) & (chunk['meter_reading'].notnull())]
            if len(m_df) == 0: continue
            
            v = m_df['meter_reading']
            b = m_df['building_id'].unique()
            
            meter_stats[m]["count"] += len(v)
            meter_stats[m]["sum"] += float(v.sum())
            meter_stats[m]["sq_sum"] += float((v**2).sum())
            meter_stats[m]["min"] = min(meter_stats[m]["min"], float(v.min()))
            meter_stats[m]["max"] = max(meter_stats[m]["max"], float(v.max()))
            meter_stats[m]["zeros"] += int((v == 0).sum())
            meter_stats[m]["negatives"] += int((v < 0).sum())
            meter_stats[m]["buildings"].update(b)
            
            sz = min(len(v), 5000)
            meter_stats[m]["samples"].extend(v.sample(sz).tolist())
            
    final_stats = {}
    for m in [0, 1, 2, 3]:
        s = meter_stats[m]
        if s["count"] == 0: continue
        
        mean = s["sum"] / s["count"]
        var = (s["sq_sum"] / s["count"]) - (mean**2)
        std = math.sqrt(var) if var > 0 else 0
        approx_median = float(np.median(s["samples"])) if s["samples"] else 0
        
        pcts = [1, 5, 25, 50, 75, 95, 99, 99.9]
        perc_dict = {f"p{p}": float(np.percentile(s["samples"], p)) for p in pcts} if s["samples"] else {}
        
        final_stats[m] = {
            "rows": s["count"],
            "pct_of_total": (s["count"] / total_rows) * 100,
            "buildings": len(s["buildings"]),
            "min": s["min"],
            "max": s["max"],
            "mean": mean,
            "approx_median": approx_median,
            "std": std,
            "zero_pct": (s["zeros"] / s["count"]) * 100,
            "non_zero": s["count"] - s["zeros"],
            "negatives": s["negatives"],
            "percentiles": perc_dict
        }
        
    return {
        "total_rows": total_rows,
        "min_ts": min_ts.strftime("%Y-%m-%d %H:%M:%S") if min_ts else None,
        "max_ts": max_ts.strftime("%Y-%m-%d %H:%M:%S") if max_ts else None,
        "is_hourly": is_hourly,
        "chunk_duplicates": int(chunk_dups),
        "missing_target": int(missing_target),
        "meter_analysis": final_stats
    }

def make_json_serializable(obj):
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

def main():
    base = Path("data/raw")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    print("Validating Building Metadata...")
    meta = validate_metadata(base / "building_metadata.csv")
    
    print("Validating Weather Train...")
    wtrain = validate_weather(base / "weather_train.csv")
    
    print("Validating Train...")
    train = validate_train(base / "train.csv")
    
    out = {
        "metadata": meta,
        "weather_train": wtrain,
        "train": train
    }
    
    out_safe = make_json_serializable(out)
    
    with open(reports_dir / "data_validation_summary.json", "w") as f:
        json.dump(out_safe, f, indent=4)
        
    print("Validation and cleaning analysis script complete.")

if __name__ == "__main__":
    main()
