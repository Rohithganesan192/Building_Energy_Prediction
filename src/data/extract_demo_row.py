import pandas as pd
import json
from pathlib import Path
import math

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "features" / "train_features.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"

REQUIRED_FEATURES = [
    "site_id", "primary_use", "square_feet", "year_built", "floor_count", "meter",
    "hour", "day_of_week", "month", "day_of_year", "is_weekend",
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos", "month_sin", "month_cos",
    "air_temperature", "cloud_coverage", "dew_temperature", "precip_depth_1_hr",
    "sea_level_pressure", "wind_direction", "wind_speed",
    "lag_1", "lag_24", "lag_168",
    "rolling_mean_24", "rolling_mean_168", "rolling_std_24", "rolling_std_168",
    "meter_reading"
]

def format_value(val):
    if pd.isna(val):
        return "N/A"
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return f"{val:.4f}"
    return str(val)

def extract_demo_row():
    chunk_size = 50000
    valid_row = None
    
    print(f"Reading {FEATURES_PATH} in chunks...")
    try:
        for chunk in pd.read_csv(FEATURES_PATH, chunksize=chunk_size):
            # Check if all required features exist in the file
            missing_cols = [col for col in REQUIRED_FEATURES if col not in chunk.columns]
            if missing_cols:
                print(f"Error: Missing columns in dataset: {missing_cols}")
                return False

            # Drop rows where any of the required features are null
            valid_chunk = chunk.dropna(subset=REQUIRED_FEATURES)
            
            if not valid_chunk.empty:
                # Get the first valid row
                valid_row = valid_chunk.iloc[0].to_dict()
                break
                
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return False
        
    if valid_row is None:
        print("No complete row found with all required features.")
        return False
        
    print("Found valid demonstration row.")
    
    # Clean up row for JSON serialization (convert numpy types)
    clean_row = {}
    for k, v in valid_row.items():
        if pd.isna(v):
            clean_row[k] = None
        elif isinstance(v, (int, float, str, bool)):
            clean_row[k] = v
        elif hasattr(v, 'item'):
            clean_row[k] = v.item()
        else:
            clean_row[k] = str(v)
            
    # Save to JSON
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "demo_real_row.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(clean_row, f, indent=4)
        
    print(f"Saved JSON to {json_path}")
    
    # Generate Markdown
    md_path = REPORTS_DIR / "demo_real_row.md"
    
    timestamp = clean_row.get("timestamp", "N/A")
    building_id = clean_row.get("building_id", "N/A")
    meter_name = "N/A"
    meter = clean_row.get("meter")
    if meter == 0: meter_name = "Electricity"
    elif meter == 1: meter_name = "Chilled Water"
    elif meter == 2: meter_name = "Steam"
    elif meter == 3: meter_name = "Hot Water"

    md_content = f"""# Genuine Demonstration Observation

> This row is an actual observation from the ASHRAE-derived project feature dataset and is intended for application demonstration/testing.

## Identification
- **Timestamp**: {timestamp}
- **Building ID**: {building_id}
- **Site ID**: {format_value(clean_row.get('site_id'))}
- **Primary Use**: {clean_row.get('primary_use')}
- **Meter**: {meter} ({meter_name})

## Building Characteristics
- **Square Feet**: {format_value(clean_row.get('square_feet'))}
- **Year Built**: {format_value(clean_row.get('year_built'))}
- **Floor Count**: {format_value(clean_row.get('floor_count'))}

## Actual Target
- **Meter Reading**: {format_value(clean_row.get('meter_reading'))}

## Historical Energy State (Group B Features)
- **Lag 1**: {format_value(clean_row.get('lag_1'))}
- **Lag 24**: {format_value(clean_row.get('lag_24'))}
- **Lag 168**: {format_value(clean_row.get('lag_168'))}
- **Rolling Mean 24**: {format_value(clean_row.get('rolling_mean_24'))}
- **Rolling Mean 168**: {format_value(clean_row.get('rolling_mean_168'))}
- **Rolling Std 24**: {format_value(clean_row.get('rolling_std_24'))}
- **Rolling Std 168**: {format_value(clean_row.get('rolling_std_168'))}

## Weather Conditions
- **Air Temperature**: {format_value(clean_row.get('air_temperature'))}
- **Cloud Coverage**: {format_value(clean_row.get('cloud_coverage'))}
- **Dew Temperature**: {format_value(clean_row.get('dew_temperature'))}
- **Precipitation (1 hr)**: {format_value(clean_row.get('precip_depth_1_hr'))}
- **Sea Level Pressure**: {format_value(clean_row.get('sea_level_pressure'))}
- **Wind Direction**: {format_value(clean_row.get('wind_direction'))}
- **Wind Speed**: {format_value(clean_row.get('wind_speed'))}

## Temporal Features
- **Hour**: {format_value(clean_row.get('hour'))} (sin: {format_value(clean_row.get('hour_sin'))}, cos: {format_value(clean_row.get('hour_cos'))})
- **Day of Week**: {format_value(clean_row.get('day_of_week'))} (sin: {format_value(clean_row.get('day_of_week_sin'))}, cos: {format_value(clean_row.get('day_of_week_cos'))})
- **Month**: {format_value(clean_row.get('month'))} (sin: {format_value(clean_row.get('month_sin'))}, cos: {format_value(clean_row.get('month_cos'))})
- **Day of Year**: {format_value(clean_row.get('day_of_year'))}
- **Is Weekend**: {format_value(clean_row.get('is_weekend'))}
"""
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Saved Markdown report to {md_path}")
    return True

if __name__ == "__main__":
    extract_demo_row()
