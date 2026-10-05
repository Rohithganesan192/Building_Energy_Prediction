# Data Validation Report

### 1. Timestamp Validation
- All timestamps in energy and weather datasets are valid and parse successfully as `datetime64`.
- All timestamps are perfectly hourly (`minute == 0` and `second == 0`).
- No invalid timestamp formats discovered.

### 2. Key Validation
- `train` and `test` `building_id` values map 100% perfectly to `building_metadata`.
- `building_metadata` `site_id` maps 100% perfectly to `weather` `site_id`.
- There are no missing or broken relationships between the datasets.

### 3. Meter Analysis
| Meter | Energy Type | Rows | Buildings | Min | Max | Mean | Approx Median | Zero % |
|---|---|---|---|---|---|---|---|---|
| 0 | electricity | ~12.0M | 1413 | 0.0 | 79.9K | 170.8 | 62.8 | ~5% |
| 1 | chilledwater | ~4.1M | 498 | 0.0 | 8.8M | 633.3 | 120.4 | ~20% |
| 2 | steam | ~2.7M | 324 | 0.0 | 21.9M | 13882.1 | 258.9 | ~7% |
| 3 | hotwater | ~1.2M | 145 | 0.0 | 3.9M | 385.8 | 39.6 | ~15% |

*(Note: Medians are approximated via sampling due to chunked data constraints).*

### 4. Target Validation
- **Missing values**: 0 in `train.csv`.
- **Negative values**: 0 (Energy cannot be negative).
- **Extreme values**: Steam (meter 2) has high maximums compared to others. Site 0 steam contains extreme values requiring further investigation. The observations will not be removed without evidence.
- The target is highly right-skewed.

### 5. Building Metadata Validation
- `year_built`: Range 1900 to 2017. 53.4% missing. No illogical future years.
- `floor_count`: Range 1 to 26. 75.5% missing. 
- `square_feet`: Range 283 to 875,000. 0% missing. No zero/negative areas.
- `primary_use`: 16 distinct string categories. Clean.

### 6. Weather Validation
- `precip_depth_1_hr`: Contains `-1`. `-1` is a sentinel/missing-value representation in the ASHRAE weather data and requires explicit preprocessing treatment.
- Missingness is very high for `cloud_coverage` (~50%) and `precip_depth_1_hr` (~35%).
- `air_temperature` ranges from -28.9 to 48.3 °C (valid and expected bounds).

### 7. Missing-Value Analysis
- **Energy Data**: 0% missing.
- **Metadata**: High missingness for `floor_count`, `year_built`.
- **Weather Data**: Moderate missingness for `sea_level_pressure`, `wind_direction`. Low missingness for `air_temperature`.

### 8. Duplicate-Key Analysis
- No duplicate keys were detected within the examined chunks. A complete global duplicate-key check was not performed because of memory constraints.

### 9. Outlier Analysis
- Site 0 steam readings are heavily clustered at immense values.
- High percentile (99.9%) of `meter_reading` jumps drastically compared to the 99% percentile, confirming severe right-tail skew.

### 10. Initial Cleaning Decisions
Please review `data_cleaning_decisions.md` for the explicit proposed treatments per variable.

### 11. Limitations
- A complete global duplicate-key check was not performed because of memory constraints. Only examined chunks were evaluated.
- Medians are approximated via sampling.

---

### IMPORTANT RESEARCH DECISIONS

1. **Is the target valid for regression?**
   Yes, the target is purely numeric, non-negative, and continuous.
2. **Are all four meter types represented?**
   Yes. Electricity is the most common (present in almost all buildings).
3. **Are the meter types distributed similarly or very differently?**
   They are vastly different. Steam has means in the tens of thousands, while electricity is in the hundreds.
4. **Does meter type appear necessary as a model feature?**
   The four meter types have substantially different distributions. Unified modeling with meter type as a feature and meter-specific modeling should be evaluated experimentally.
5. **Is target transformation worth experimentally testing?**
   The strong right-skew of meter_reading provides justification for experimentally comparing the raw target with a log1p-transformed target. MAE, RMSE and R² will be reported according to the finalized target/evaluation strategy. If target transformation is used, predictions will be transformed back to the original energy-consumption scale before practical metric comparison.
6. **Which columns have missing values?**
   `year_built`, `floor_count`, and nearly all weather variables except `timestamp` and `site_id`.
7. **Which missing-value treatments need to be tested later?**
   Treatments must support a fair comparison across all six planned models (e.g., converting -1 to NaN for precip_depth_1_hr, evaluating interpolation, dropping vs. imputing floor_count and year_built).
8. **Are there suspicious values requiring further investigation?**
   Site 0 steam contains extreme values requiring further investigation. The observations will not be removed without evidence.
9. **Are the dataset relationships safe for later merging?**
   Yes, keys map perfectly.
10. **Are there any findings that could cause data leakage?**
   None observed directly from keys, though temporal ordering must be respected in cross-validation.
