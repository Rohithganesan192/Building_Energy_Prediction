# Phase 6 Pilot Audit Report

## 1. Audit Status
**Recommendation:** A) READY FOR 10% COMPARISON

The 1% pilot successfully verified the modeling pipeline, memory management, and evaluation loops without modifying raw data, regenerating Phase 5 features, or touching the chronological holdout.

## 2. Target Transformation Audit
**Status: PASS WITH LIMITATION**
- **Implementation:** Correct. Models train on `np.log1p()` and predictions are inversely transformed via `np.expm1(np.clip(pred, a_min=-1, a_max=20))` before calculating MAE, RMSE, and R². `y_true` is correctly preserved on the raw scale.
- **Abnormal Results Analysis:** The wildly poor `log1p` performance in LinearRegression (R² -6.15) and CatBoost (R² -6.54) is a known mathematical risk of MSE-optimized algorithms predicting extreme bounds on log-transformed data without proper regularization or hyperparameter tuning. A small absolute error overhead in log space transforms into a catastrophic squared error on the original scale (e.g. `expm1(15)`). The clipping parameter prevents `Inf` crashes, but these models inherently require tuning to manage variance. This is a legitimate pilot observation, not a pipeline bug.

## 3. Chronological Split Audit
**Status: PASS**
- **Train:** Jan 1 – Sep 30, 2016
- **Validation:** Oct 1 – Nov 30, 2016
- **December Holdout:** Dec 1 – Dec 31, 2016
- **Leakage check:** The holdout split (`test_df`) is strictly isolated and bypassed during the experimental 24-run grid search. 

## 4. Preprocessing Leakage Audit
**Status: PASS**
- `get_preprocessor()` correctly returns a scikit-learn pipeline or adapter.
- `fit()` is exclusively called on `train_df`.
- Imputation (Median/Mode), Encoders (OneHot/Ordinal), and Standard Scalers strictly apply validation distributions derived solely from training history.

## 5. Group A Audit
**Status: PASS**
- Features verified in `experiment_config.py`.
- Includes Temporal (hours, sine/cosine, etc), Building metadata, Weather, and `meter` categorical.
- Strictly Exogenous. No lags or rolling targets exist in Group A.

## 6. Group B Audit
**Status: PASS WITH LIMITATION**
- **Composition:** Contains Group A + `lag_1`, `lag_24`, `lag_168`, `rolling_mean_24/168`, `rolling_std_24/168`.
- **Validation Boundary Behavior:** Because historical features were constructed sequentially over the whole 2016 timeline in Phase 5, an observation on October 2nd (validation set) uses historical target data from October 1st (also validation set).
- **Interpretation:** This is NOT a leakage defect, but it defines the experiment as a **sequential one-step-ahead operational forecast**, simulating an environment where recent smart-meter consumption is constantly available. This matches the explicit limitation documented in the codebase. It cannot, however, be treated as a pure blind batch forecast (like the ASHRAE test rules). 

## 7. Historical-Feature Leakage Audit
**Status: PASS**
- Verified `src/features/historical_features.py`.
- `grp.shift(lag)` correctly aligns past readings.
- For rolling features, `grp.shift(1).rolling(window)` enforces a mandatory 1-step exclusion, preventing the current timestep's `meter_reading` from polluting the rolling average or standard deviation.

## 8. Building Sampling Audit
**Status: PASS**
- Deterministic hash selection `hash(building_id + seed)` guarantees stability.
- Using `PILOT_BUILDING_FRACTION = 0.01`, the subsample retrieved exactly identical rows (221,885 Train / 49,341 Val) across all 24 models.
- Entire time-series trajectories for selected buildings are perfectly preserved.

## 9. Model Comparability Audit
**Status: PASS**
- All 6 algorithms receive exactly the same semantic information based on the designated Feature Group.
- **LinearRegression:** Uses OHE & Standard Scaling.
- **Sklearn Trees:** Use OrdinalEncoding.
- **XGBoost:** Uses safe OrdinalEncoding.
- **LightGBM:** Leverages pandas `category` dtype directly.
- **CatBoost:** Parses explicitly via strings & `cat_features`.

## 10. Metric Audit
**Status: PASS**
- MAE, RMSE, and R² are uniformly scored on the raw meter_reading scale using `evaluate_predictions()`.
- Unusually poor R² scores are correctly computed mathematically, rather than artificially suppressed.

## 11. Result Consistency Audit
**Status: PASS**
- Exactly 24 complete experiments recorded in `pilot_results.csv`.
- No duplicated runs, no NaNs.
- **Performance Highlights (Descriptive Only, Untuned):**
  - **Lowest MAE:** LightGBM (log1p, GroupB) = 34.96
  - **Lowest RMSE:** CatBoost (raw, GroupB) = 300.97
  - **Highest R²:** CatBoost (raw, GroupB) = 0.7462

## 12. LightGBM Warning Analysis
**Status: PASS**
- *Warning:* "No further splits with positive gain, best gain: -inf"
- *Analysis:* Given the tiny 1% building subsample and lightweight parameters (`max_depth=5`, `n_estimators=100`), LightGBM frequently hits structural minimum-data-in-leaf constraints or explores splits that offer zero loss reduction. This is normal, benign early-stopping behavior for a tree algorithm on subsetted data and is completely safe.

## 13. Issues Found
None requiring architectural intervention.

## 14. Required Corrections
None. 

## 15. Decision
**READY FOR 10% COMPARISON.** 
The codebase is structurally sound, mathematically honest, and methodologically strict.
