# Phase 9: SHAP Explainable AI Analysis Report

## 1. Objective
To interpret the structural behavior of the finalized model, evaluate relative feature group impacts (especially autoregressive vs. exogenous drivers), and validate local prediction mechanics.

## 2. Final Model Evaluated
- **Algorithm**: RandomForestRegressor
- **Target**: `meter_reading` (Raw)
- **Features**: Group B

## 3. Explanation Dataset & Methodology
- **Sample**: 1,000 deterministically sampled rows from the October-November 2016 Validation period.
- **Holdout Protection**: December 2016 was strictly excluded from this global explanation dataset.
- **Methodology**: Exact SHAP attribution calculated via `shap.TreeExplainer`.

## 4. SHAP Reconstruction Validation
- Dimensionality matched exactly: `True`
- Maximum base + sum(shap) deviation from actual prediction: `8.89e-10` (Numerically identical within floating point tolerance).

## 5. Global Feature Importance
The top 5 features driving model predictions globally are:
    1. `lag_1` (Mean Abs SHAP: 373.60)
    2. `lag_24` (Mean Abs SHAP: 61.42)
    3. `rolling_mean_24` (Mean Abs SHAP: 23.18)
    4. `lag_168` (Mean Abs SHAP: 8.59)
    5. `hour_cos` (Mean Abs SHAP: 4.14)

## 6. Feature-Group Contribution
Aggregated absolute SHAP values reveal the macroeconomic importance of each functional group:
- **Historical**: 95.1% (Sum: 472.69)
- **Temporal**: 2.3% (Sum: 11.51)
- **Weather**: 1.2% (Sum: 6.10)
- **Building**: 0.8% (Sum: 4.18)
- **Meter**: 0.5% (Sum: 2.31)

## 7. Dependence Analysis Insights
Based on the generated `shap_dependence_<feature>.png` plots, the relationships generally show:
- **lag_1** exhibits a strong, near-linear positive relationship, confirming the model heavily leverages the immediate past consumption as a stateful anchor.
- **rolling_mean_24** contributes significantly, mapping multi-hour load thresholds.

## 8. Limitations and Disclaimers
> **CRITICAL**: SHAP explains the *contribution of features to the model prediction*; it does **not** establish causal relationships between features and actual physical energy consumption.
The dominance of historical autoregressive features simply means the model learned to rely on past consumption telemetry over weather data; it does not mean past consumption physically causes future consumption. True exogenous causal drivers (weather, building physics) are largely absorbed by the autoregressive state.
