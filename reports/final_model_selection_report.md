# Phase 8: Final Model Selection Report

## 1. Candidate Selection
Based on the Phase 7 validation results (October-November), the tuned `RandomForestRegressor` was explicitly selected over all competitors. It achieved the highest validation performance across all primary and secondary metrics without succumbing to the variance/explosion problems seen in log-transformed targets.

## 2. Candidate Comparison
- **Tuned Random Forest (Selected)**: Val RMSE = 262.07, Val MAE = 38.97, Val R² = 0.9614
- **Untuned Linear Regression**: Val RMSE = 275.54, Val MAE = 43.69, Val R² = 0.9573

## 3. Selected Hyperparameters
```json
{
  "n_estimators": 200,
  "min_samples_split": 2,
  "min_samples_leaf": 20,
  "max_features": null,
  "max_depth": 20
}
```

## 4. Methodological Integrity
The December 2016 holdout was completely excluded from this selection process. The candidate was locked based strictly on Validation (Oct-Nov) performance.
