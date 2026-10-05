# Phase 5: Feature Engineering Schema and Leakage Audit

## Feature Schema

| Feature Name | Source | Data Type | Transformation | Category | Leakage Risk | Candidate |
|---|---|---|---|---|---|---|
| `building_id` | `train_clean.csv` | int | None | Categorical | None | No (High cardinality) |
| `meter` | `train_clean.csv` | int | None | Categorical | None | Yes |
| `meter_name` | `train_clean.csv` | str | Map (0=Electricity, etc) | Categorical | None | Yes |
| `timestamp` | `train_clean.csv` | datetime | None | Temporal | None | No (Drop before modeling) |
| `meter_reading` | `train_clean.csv` | float | None (Target) | Target | N/A | Target |
| `hour` | `timestamp` | int | dt.hour | Temporal | None | Yes |
| `day_of_week` | `timestamp` | int | dt.dayofweek | Temporal | None | Yes |
| `month` | `timestamp` | int | dt.month | Temporal | None | Yes |
| `day_of_year` | `timestamp` | int | dt.dayofyear | Temporal | None | Yes |
| `is_weekend` | `timestamp` | int | (day >= 5) | Temporal | None | Yes |
| `hour_sin/cos` | `timestamp` | float | Cyclical encoding | Temporal | None | Yes |
| `day_of_week_sin/cos` | `timestamp` | float | Cyclical encoding | Temporal | None | Yes |
| `month_sin/cos` | `timestamp` | float | Cyclical encoding | Temporal | None | Yes |
| `site_id` | `building_metadata` | int | Merge | Building | None | Yes |
| `primary_use` | `building_metadata` | str | Merge | Building | None | Yes |
| `square_feet` | `building_metadata` | float | Merge | Building | None | Yes |
| `year_built` | `building_metadata` | float | Merge | Building | None | Yes |
| `floor_count` | `building_metadata` | float | Merge | Building | None | Yes |
| `air_temperature` | `weather_train` | float | Merge, ffill | Weather | Low (ffill prevents future leak) | Yes |
| `cloud_coverage` | `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `dew_temperature` | `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `precip_depth_1_hr`| `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `sea_level_pressure`| `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `wind_direction` | `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `wind_speed` | `weather_train` | float | Merge, ffill | Weather | Low | Yes |
| `lag_1` | `meter_reading` | float | shift(1) | Historical | High | Yes |
| `lag_24` | `meter_reading` | float | shift(24) | Historical | High | Yes |
| `lag_168` | `meter_reading` | float | shift(168) | Historical | High | Yes |
| `rolling_mean_24` | `meter_reading` | float | shift(1).rolling(24).mean() | Historical | High | Yes |
| `rolling_std_24` | `meter_reading` | float | shift(1).rolling(24).std() | Historical | High | Yes |
| `rolling_mean_168` | `meter_reading` | float | shift(1).rolling(168).mean() | Historical | High | Yes |
| `rolling_std_168` | `meter_reading` | float | shift(1).rolling(168).std() | Historical | High | Yes |


## Leakage Audit

1. **Future target values in lags?**
   - **Audit**: Lag features use pandas `.shift(N)` after sorting by `timestamp`. By shifting by positive integers, `lag_1` strictly corresponds to $t - 1$, preventing future target information from entering current rows.
2. **Rolling windows containing the current target?**
   - **Audit**: A direct `.rolling(N)` includes the current row $t$. To prevent this, the pipeline applies `.shift(1)` to the target *before* computing the rolling mean and std. This ensures the window covers $[t-N, t-1]$, excluding $t$.
3. **Future weather information?**
   - **Audit**: Imputation on continuous weather data relies strictly on `ffill` (forward fill) after sorting chronologically by `site_id` and `timestamp`. No `bfill` (backward fill) or bidirectional interpolation is used, guaranteeing that missing values at time $t$ are populated only from time $\le t$.
4. **Test Target / Future Metadata?**
   - **Audit**: The test target is not present in the training set. Metadata is static and invariant over time (e.g. `year_built`, `square_feet`).
5. **Random Splitting / Time Series Continuity?**
   - **Audit**: The experimental strategy strictly mandates a chronological split of the 2016 training period (e.g. first 9 months train, last 3 months validation) to mimic real-world deployment on the 2017-2018 test data. 
6. **Weather Joins multiplying rows?**
   - **Audit**: Weather data is explicitly deduplicated on `["site_id", "timestamp"]` before merging, preventing cross-product duplication of energy rows.
