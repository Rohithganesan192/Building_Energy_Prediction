# Phase 10: Energy Driver Analysis

## 1. Top SHAP Drivers
The final tuned RandomForestRegressor heavily relies on the following features (based on mean absolute SHAP values):
1. `lag_1` (373.60)
2. `lag_24` (61.42)
3. `rolling_mean_24` (23.17)
4. `lag_168` (8.59)
5. `hour_cos` (4.14)
6. `dew_temperature` (3.63)

## 2. Historical vs Contextual Drivers
- **Historical Drivers (95.1% contribution)**: Features like `lag_1` and `rolling_mean_24` dominate the model's prediction process. They serve as observational proxies for the building's current persistent energy load.
- **Contextual Drivers (<5% contribution)**: Temporal variables (`hour_cos`), weather variables (`dew_temperature`), and static building metadata (`square_feet`) act as minor modifiers to the strong autoregressive baseline established by the historical drivers.

## 3. Controllability Classification
Drivers were classified to determine how they can be addressed operationally:
- **Historical State**: Observational proxies indicating elevated baseline demand. (Indirectly Actionable via general operational review).
- **Contextual/non-controllable (Temporal/Weather)**: Identifies time-of-day or thermal patterns. (Actionable via scheduling or HVAC setpoint reviews).
- **Identification/context only (Building/Meter)**: Static properties that cannot be altered. (Not directly actionable).

## 4. Actionable vs Non-Actionable Drivers
- **Actionable**: Features that map to an operational review, such as reviewing HVAC runtime against the hour of the day (`hour_cos`), identifying abnormal weekend operation (`is_weekend`), or reviewing mechanical response to weather (`dew_temperature`).
- **Non-Actionable**: Static building features like `square_feet` or geographic location (`site_id`) are non-actionable for daily operations.

## 5. Recommendation Framework
The newly developed recommendation engine (`src/recommendations/recommendation_engine.py`) explicitly decouples predictive attribution from causality. It translates mathematical SHAP values into structured domain rules (`recommendation_rules.py`). 
For example, if `hour_cos` significantly drives up a prediction, the engine does not suggest "altering the hour"; it suggests "reviewing HVAC and lighting schedules to ensure they align with actual occupancy."

## 6. Limitations
- **No Causal Guarantee**: The recommendation engine has not been validated as a causal energy-saving intervention system. Recommendations are decision-support suggestions, not automated control actions.
- **No Fabricated Savings**: The framework intentionally avoids hard-coding arbitrary energy-saving percentages (e.g., "this action saves 5%"). SHAP cannot mathematically guarantee intervention savings.
