# Phase 4 — Exploratory Data Analysis Report

> **Project**: Explainable ML for Building Energy Prediction  
> **Dataset**: ASHRAE Great Energy Predictor III  
> **Phase**: 4 — EDA (read-only; no cleaning, imputation, or modelling performed)  

---

## 1. Dataset Overview

| Attribute | Value |
|---|---|
| Train rows | 20,216,100 |
| Test rows  | 41,697,600 |
| Unique buildings (train) | 1,449 |
| Unique meter types | 4 |
| Unique sites (metadata) | 16 |
| Train timestamp range | 2016-01-01 00:00:00 → 2016-12-31 23:00:00 |
| Metadata rows | 1449 |
| Weather train rows | 139,773 |
| Weather test rows  | 277,243 |

---

## 2. Target Variable Analysis (meter_reading)

> Statistics below are derived from a 2% reproducible sample (seed=42).
> Raw values are used — no log transformation applied.

| Statistic | Value |
|---|---|
| Count (sample) | 404,322 |
| Mean | 2,181.6110 |
| Median | 79.0000 |
| Std | 157,839.9515 |
| Min | 0.0000 |
| Max | 20,026,700.0000 |
| Skewness | 102.5152 |
| p1 | 0.0000 |
| p99 | 5,516.3942 |
| p99.9 | 38,994.9924 |

**Observation**: The target is strongly right-skewed. The mean substantially
exceeds the median, indicating a long right tail driven primarily by Steam
and Chilled Water meter types. Whether a log1p transformation improves
model performance is an experimental question for Phase 6.

---

## 3. Meter Type Analysis

> Counts and statistics are computed exactly via chunked aggregation.
> Medians and percentiles are approximated via 2% sampling.

| Meter | Type | Rows | Mean | Approx Median | Std | Min | Max | Zero % |
|---|---|---|---|---|---|---|---|---|
| 0 | Electricity | 12,060,910 | 170.83 | 54.73 | 380.83 | 0.00 | 79,769.00 | 4.40% |
| 1 | Chilled Water | 4,182,440 | 633.36 | 121.65 | 7,988.21 | 0.00 | 880,374.00 | 15.70% |
| 2 | Steam | 2,708,713 | 13,882.19 | 257.61 | 418,313.43 | 0.00 | 21,904,700.00 | 12.81% |
| 3 | Hot Water | 1,264,037 | 385.87 | 38.10 | 2,508.17 | 0.00 | 160,187.00 | 26.93% |

**Observation**: The four meter types have substantially different distributions.
Steam readings are orders of magnitude larger than electricity readings.
Unified modelling with meter as a feature vs. meter-specific modelling
should be evaluated experimentally in Phase 6.

---

## 4. Building Metadata

| Column | Missing Count | Missing % |
|---|---|---|
| floor_count | 1,094 | 75.50% |
| year_built | 774 | 53.42% |
| building_id | 0 | 0.00% |
| site_id | 0 | 0.00% |
| square_feet | 0 | 0.00% |
| primary_use | 0 | 0.00% |

**Note**: Missing values are preserved. Imputation strategy will be
determined during Feature Engineering (Phase 5).

---

## 5. Weather Variable Missingness

| Column | Missing Count | Missing % |
|---|---|---|
| cloud_coverage | 69,173 | 49.49% |
| precip_depth_1_hr | 56,069 | 40.11% |
| sea_level_pressure | 10,618 | 7.60% |
| wind_direction | 6,268 | 4.48% |
| wind_speed | 304 | 0.22% |
| dew_temperature | 113 | 0.08% |
| air_temperature | 55 | 0.04% |
| site_id | 0 | 0.00% |
| timestamp | 0 | 0.00% |

**Note**: `precip_depth_1_hr` sentinel values (-1) were already converted
to NaN in Phase 3. The missing percentage above reflects both original
NaN values and converted sentinels.

---

## 6. Temporal Analysis

Patterns computed from full training set via chunked aggregation.

| Period | Peak Hour (approx.) |
|---|---|
| Hourly | Hour 15 |
| Day of week | Day 2 (0=Mon) |
| Month | Month 4 |

---

## 7. Outlier Investigation

> Extreme observations are flagged, not removed.

| Meter | Type | p99.9 Threshold | Extreme Count (sample) | Extreme % (sample) |
|---|---|---|---|---|
| 0 | Electricity | 4,934.23 | 247 | 0.1025% |
| 1 | Chilled Water | 15,328.74 | 65 | 0.0778% |
| 2 | Steam | 124,725.89 | 66 | 0.1219% |
| 3 | Hot Water | 40,612.94 | 41 | 0.1599% |

**Observation**: Extreme values are concentrated in Steam (Meter 2)
and Chilled Water (Meter 1). Whether these represent legitimate
high-consumption observations or data anomalies requires further
domain-level investigation. No observations are removed at this stage.

---

## 8. Key EDA Findings

1. **Target skewness**: meter_reading is strongly right-skewed. log1p transformation should be experimentally evaluated.
2. **Meter heterogeneity**: Steam readings are orders of magnitude larger than electricity. Meter type is a critical feature.
3. **Metadata missingness**: floor_count (>75%) and year_built (>50%) are substantially missing; imputation strategy must support all six models.
4. **Weather missingness**: cloud_coverage and precip_depth_1_hr have the highest missingness in weather data.
5. **Temporal patterns**: Consumption varies significantly by hour, weekday, and month, indicating temporal features will be valuable.
6. **Building size**: Larger buildings tend to consume more energy, but the relationship is noisy and non-linear.
7. **Extreme outliers**: Concentrated in Steam meter, Site 0 in particular.

---

## 9. Implications for Feature Engineering (Phase 5)

- Temporal features (hour, day-of-week, month, is_weekend) are clearly supported by EDA.
- `meter` should be included as a model feature; meter-specific modelling should also be experimentally evaluated.
- Weather variables (especially `air_temperature`, `dew_temperature`) show exploratory associations with energy consumption.
- Imputation decisions for `year_built`, `floor_count`, and weather NaNs need to be made in Phase 5.
- Whether to apply log1p to meter_reading is an experimental decision for Phase 6 model training.

---

## 10. Limitations

- Target statistics and visualisations are based on a 2% sample (fixed seed=42). Population statistics may differ slightly.
- Exact global median requires a full pass; approximate medians are reported via sampling.
- Correlation analysis used up to 50,000 sample rows.
- Weather–energy associations are exploratory only; causality is not established.
- Temporal aggregation uses the full training set via chunked accumulation; however, no seasonality decomposition is performed.

---

*Report generated by `src/data/eda.py` — Phase 4, ASHRAE Project.*