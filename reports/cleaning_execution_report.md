# Data Cleaning Execution Report

## 1. Input/Output Files
| Dataset | Input | Output | Raw Rows | Processed Rows |
|---|---|---|---|---|
| Metadata | `data/raw/building_metadata.csv` | `data/processed/building_metadata_clean.csv` | 1449 | 1449 |
| Weather Train | `data/raw/weather_train.csv` | `data/processed/weather_train_clean.csv` | 139773 | 139773 |
| Weather Test | `data/raw/weather_test.csv` | `data/processed/weather_test_clean.csv` | 277243 | 277243 |
| Train | `data/raw/train.csv` | `data/processed/train_clean.csv` | 20216100 | 20216100 |
| Test | `data/raw/test.csv` | `data/processed/test_clean.csv` | 41697600 | 41697600 |

## 2. Integrity Checks
- **Row Counts Match**: True
- **Data Overwrites**: None (all output safely routed to `data/processed/`)

## 3. Data Transformations
- **Types Normalized**: Timestamps converted to strictly formatted `datetime64`. IDs/Meters cast strictly to `int`.
- **Missing Values Preserved**: Missing `year_built`, `floor_count`, and weather data gaps were intentionally left as `NaN`.
- **Sentinel Values Handled**: `-1` in `precip_depth_1_hr` was explicitly converted to `NaN` to reflect missing/trace representations.
  - Weather Train Sentinels Converted: 5780
  - Weather Test Sentinels Converted: 12271
- **Target Validation**: Automatically confirmed 0 missing and 0 explicitly negative values for `meter_reading` throughout training chunks.

## 4. Unchanged Elements
- `meter_reading` values remain completely unmodified (no `log1p` transformation yet).
- Raw target retains its original highly skewed scale.
- All outliers (including Site 0 steam anomalies) remain entirely intact for experimental resolution later.
- `primary_use` categories remain unencoded raw strings.
- Energy, Metadata, and Weather datasets remain strictly modular and completely distinct, preserving pipeline flexibility.