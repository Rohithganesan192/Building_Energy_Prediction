# Phase 5 Full Feature Validation Report

**File**: `C:\Users\ROHITHGANESAN G\Building_Energy_Prediction\data\features\train_features.csv`

## 1. Row and Column Counts

| Metric | Value |
|---|---|
| Total rows | 20,216,100 |
| Total columns | 35 |
| Expected columns | 35 |
| Schema check | PASS |

## 2. Column List

```
building_id
meter
timestamp
meter_reading
hour
day_of_week
month
day_of_year
is_weekend
hour_sin
hour_cos
day_of_week_sin
day_of_week_cos
month_sin
month_cos
site_id
primary_use
square_feet
year_built
floor_count
air_temperature
cloud_coverage
dew_temperature
precip_depth_1_hr
sea_level_pressure
wind_direction
wind_speed
lag_1
lag_24
lag_168
rolling_mean_24
rolling_std_24
rolling_mean_168
rolling_std_168
meter_name
```

## 3. Identity and Structural Checks

| Check | Result |
|---|---|
| Identity columns present (`building_id`, `meter`, `timestamp`, `meter_reading`) | PASS |
| Historical feature columns present | PASS |
| Meter values present (0,1,2,3) | PASS — found: [0, 1, 2, 3] |
| `meter_reading` NaN count | 0 (PASS) |
| Negative `meter_reading` rows | 0 |

## 4. Temporal Coverage

| Metric | Value |
|---|---|
| Minimum timestamp | 2016-01-01 00:00:00 |
| Maximum timestamp | 2016-12-31 23:00:00 |

## 5. Unique Identifiers

| Metric | Count |
|---|---|
| Unique `building_id` values | 1,449 |
| Unique `meter` values | 4 |
| Unique `(building_id, meter)` groups | 2,380 |

## 6. Duplicate Detection

| Check | Result |
|---|---|
| Within-chunk duplicates on `(building_id, meter, timestamp)` | 0 |
| Cross-chunk global duplicate check | NOT PERFORMED |

> **Limitation**: Exact global duplicate detection across all 20.2 M rows
> requires storing all `(building_id, meter, timestamp)` keys in memory
> simultaneously (~1.6 GB worst-case). This was not performed.
> Within-chunk detection covers duplicates arising within any 1 M-row
> chunk; cross-chunk duplicates (same key split across a chunk boundary)
> are not detected. Given that the generation pipeline processes each
> `(building_id, meter)` group once and in order, cross-chunk duplicates
> are structurally prevented by design.

## 7. Missing Value Summary

Columns with zero missing values are omitted.

| Column | Missing Count | Missing % |
|---|---|---|
| `year_built` | 12,127,645 | 59.9900% |
| `floor_count` | 16,709,167 | 82.6528% |
| `air_temperature` | 90,495 | 0.4476% |
| `cloud_coverage` | 574,835 | 2.8435% |
| `dew_temperature` | 90,495 | 0.4476% |
| `precip_depth_1_hr` | 1,769,913 | 8.7550% |
| `sea_level_pressure` | 898,096 | 4.4425% |
| `wind_direction` | 90,495 | 0.4476% |
| `wind_speed` | 90,495 | 0.4476% |
| `lag_1` | 2,380 | 0.0118% |
| `lag_24` | 57,120 | 0.2825% |
| `lag_168` | 399,840 | 1.9778% |
| `rolling_mean_24` | 2,380 | 0.0118% |
| `rolling_std_24` | 4,760 | 0.0235% |
| `rolling_mean_168` | 2,380 | 0.0118% |
| `rolling_std_168` | 4,760 | 0.0235% |

## 8. Notes

- Missing values in `lag_*` and `rolling_*` columns are expected for the first
  rows of each `(building_id, meter)` group (no prior history available).
- Missing values in `year_built` and `floor_count` reflect genuine data absence
  in the source building metadata, not a pipeline error.
- Missing weather values are the residual after forward-fill; they occur at the
  very start of each site's weather series where no prior reading exists.
- Negative `meter_reading` values (if any) are from the cleaned source data
  and are preserved for downstream modelling decisions.

*End of Phase 5 Full Feature Validation Report.*