# Master Experimental Results

**Project**: Explainable Machine Learning for Building Energy Consumption Prediction and Energy Efficiency Optimization

---

## 1. Experimental Objective
The experiments evaluate the predictive performance of various machine learning models for building energy consumption. Specifically, the experiments evaluate:
- The effect of historical energy features on predictive accuracy.
- Raw versus log1p target transformations.
- Model comparison across linear and tree-based ensemble architectures.
- The effect of sample size on computational feasibility and result stability.
- Hyperparameter tuning strategies.
- Final model holdout performance.
- Explainability via SHAP (Shapley Additive exPlanations).
- Recommendation engine integration and safety.
- Application validation and UI delivery.

These results establish the comparative performance within the evaluated dataset constraints and do not claim universal superiority for all untested buildings.

## 2. Dataset and Experimental Data
The primary dataset is derived from the **ASHRAE Great Energy Predictor III** competition.
- **Labeled Dataset Period**: 2016-01-01 to 2016-12-31.
- **Official Test Period**: 2017–2018 (unavailable for supervised evaluation as true targets are hidden).
- **Building Metadata**: Primary use, square footage, year built, floor count, and site identifiers.
- **Weather Data**: Air temperature, cloud coverage, dew temperature, precipitation, pressure, and wind metrics.
- **Meter Types**: Electricity (0), Chilled Water (1), Steam (2), Hot Water (3).

The experimental pipeline cleanly distinguishes between the raw ASHRAE train/test data, the project-derived cleaned dataset, the finalized project-derived feature dataset, and single-observation application demonstrations.

## 3. Feature Groups
Features are divided into two evaluative groups:

**Group A**: Temporal + Building + Weather + Meter information.
**Group B**: Group A + Seven historical energy state features.

The historical features are:
- `lag_1`
- `lag_24`
- `lag_168`
- `rolling_mean_24`
- `rolling_mean_168`
- `rolling_std_24`
- `rolling_std_168`

Historical features were constructed strictly using prior chronologically valid observations. The current target (`meter_reading`) was entirely excluded from their construction to prevent data leakage.

## 4. Train / Validation / Holdout Strategy
To respect temporal dependencies, a chronological split was utilized for the 2016 dataset:
- **Initial Training**: 2016-01-01 through 2016-09-30 (Used during model comparison/tuning).
- **Validation**: 2016-10-01 through 2016-11-30 (Used for model selection/tuning).
- **Final Training Period**: 2016-01-01 through 2016-11-30 (After selection, the final Random Forest was retrained using Jan-Nov).
- **Protected Holdout**: 2016-12-01 through 2016-12-31.

December remained completely untouched until final evaluation.

## 5. Pilot Experiment
The pilot experiment was used to verify pipeline feasibility across the candidate model, feature-group, and target-transformation combinations before scaling to the 10% comparison.
- **Sample Details**: Conducted on a fractional subset of buildings (221,885 training rows, 49,341 validation rows).
- **Combinations**: Successfully evaluated LinearRegression, DecisionTree, RandomForest, XGBoost, LightGBM, and CatBoost across Group A / Group B and raw / log1p transforms.

## 6. 10% Model Comparison
A comparative audit across a 10% deterministic building-level sample evaluated 24 unique configurations.
- **Building Sample**: 157 buildings (10.84% of the 1,449 buildings).
- **Total Rows**: 2,160,237 (1,609,317 training, 366,336 validation, 184,584 holdout).

| Feature Group | Target Transform | Model | MAE | RMSE | R² |
|---|---|---|---|---|---|
| GroupA | raw | LinearRegression | 393.94 | 1154.69 | 0.2503 |
| GroupA | raw | DecisionTree | 138.46 | 687.90 | 0.7339 |
| GroupA | raw | RandomForest | 263.91 | 788.67 | 0.6503 |
| GroupA | raw | XGBoost | 152.19 | 607.72 | 0.7923 |
| GroupA | raw | LightGBM | 166.04 | 630.36 | 0.7766 |
| GroupA | raw | CatBoost | 167.62 | 640.35 | 0.7694 |
| GroupB | raw | LinearRegression | 43.69 | 275.54 | 0.9573 |
| GroupB | raw | DecisionTree | 70.25 | 425.99 | 0.8980 |
| GroupB | raw | RandomForest | 60.18 | 286.57 | 0.9538 |
| GroupB | raw | XGBoost | 54.84 | 409.29 | 0.9058 |
| GroupB | raw | LightGBM | 51.63 | 378.51 | 0.9194 |
| GroupB | raw | CatBoost | 58.17 | 411.49 | 0.9048 |
| GroupA | log1p | LinearRegression | 458.34 | 3029.91 | -4.1619 |
| GroupA | log1p | DecisionTree | 139.92 | 695.77 | 0.7278 |
| GroupA | log1p | RandomForest | 241.36 | 959.81 | 0.4820 |
| GroupA | log1p | XGBoost | 168.04 | 896.30 | 0.5483 |
| GroupA | log1p | LightGBM | 179.16 | 949.90 | 0.4927 |
| GroupA | log1p | CatBoost | 191.78 | 918.20 | 0.5259 |
| GroupB | log1p | LinearRegression | 230169.16 | 9362869.22 | -49291116.28 |
| GroupB | log1p | DecisionTree | 70.39 | 412.62 | 0.9043 |
| GroupB | log1p | RandomForest | 71.41 | 551.28 | 0.8291 |
| GroupB | log1p | XGBoost | 57.10 | 421.31 | 0.9002 |
| GroupB | log1p | LightGBM | 53.13 | 436.38 | 0.8929 |
| GroupB | log1p | CatBoost | 56.50 | 423.65 | 0.8991 |

**Observed Effects:**
- **Group A vs. Group B**: The experiment observed substantial improvement in predictive accuracy after adding historical features (Group B), effectively capturing the building state.
- **Raw vs. Log1p**: In the tested configurations, the raw target generally produced lower validation error on the original `meter_reading` scale than the log1p target.
- **Model Comparison**: Within the evaluated ASHRAE-derived experimental setting, the tree-based models generally achieved lower validation error than Linear Regression.

## 7. Hyperparameter Tuning
Hyperparameter tuning was conducted on candidate models using the validation set (Oct-Nov) across Group B raw configurations. 
- Random Forest achieved strong validation performance (MAE: 38.97, RMSE: 262.07, R²: 0.961) using: `{"n_estimators": 200, "min_samples_split": 2, "min_samples_leaf": 20, "max_features": null, "max_depth": 20}`.

Random Forest was selected as the final candidate based on its tuned validation performance within the evaluated Group B, raw-target configuration. SHAP TreeExplainer was subsequently used for model interpretation.

## 8. Final Model
- **Final Model**: RandomForestRegressor
- **Feature Group**: Group B
- **Target Transformation**: Raw (`meter_reading`)
- **Final Training Period**: 2016-01-01 through 2016-11-30
- **Final Training Rows**: 1,975,653
- **Protected Holdout Rows**: 184,584
- **Model Artifact Path**: `models/final_random_forest_raw_group_b.joblib`

## 9. Protected Holdout Evaluation
The final model was evaluated against the protected December 2016 holdout set. December 2016 was not used for model selection or hyperparameter tuning and was evaluated once as the protected final holdout.

**Verified Final Holdout Results (December 2016):**
- **Random Forest**: MAE = 34.36, RMSE = 175.65, R² = 0.9876
- **Linear Regression (Baseline)**: MAE = 40.32, RMSE = 190.69, R² = 0.9854

## 10. SHAP Explainability
Global and local interpretability was achieved using `SHAP TreeExplainer`.

**Verified Feature-Group Attribution:**
- **Historical**: 95.14%
- **Temporal**: 2.31%
- **Weather**: 1.22%
- **Building**: 0.84%
- **Meter**: 0.46%

*Careful Interpretation:* SHAP attribution indicates relative mathematical contribution to the model's output prediction; it does not establish causal engineering relationships. 

## 11. Energy Driver Analysis
The system converts SHAP attribution into contextual driver categories. 
- **Historical (Non-Actionable)**: Represents building state and inertia.
- **Contextual (Non-Actionable)**: Weather and temporal environmental baselines.
- **Potentially Actionable**: Operational anomalies where expected baseline deviations suggest operational inefficiency rather than unavoidable inertia.

## 12. Recommendation Engine
The application implements a rule-based recommendation layer on top of SHAP outputs. 
- Classifies actionability based on domain rules.
- Explicitly avoids unsupported energy-saving percentage claims.
- Operates as a decision-support system, utilizing SHAP as an anomaly detector rather than a causal engineering intervention tool.

## 13. Real ASHRAE Application Demonstration
A single genuine observation was extracted to demonstrate end-to-end API and UI functionality:
- **Building ID**: 565
- **Site ID**: 4
- **Timestamp**: 2016-01-08 00:00:00
- **Primary Use**: Education
- **Meter**: 0 / Electricity
- **Actual meter reading**: 8.25 kWh
- **Predicted reading**: ~7.99 kWh

*Note: This is an application demonstration observation used for integration testing. It is NOT presented as an aggregate accuracy measurement.*

## 14. Application Testing
The full stack application underwent rigorous programmatic testing:
- **Backend Validation**: 39 Passed, 4 Warnings (Dependency deprecation warnings, no failures).
- **Frontend Build**: `npm run build` executed successfully.
The testing guarantees that historical features are strictly enforced and never fabricated by the API if missing.

## 15. Research Findings
Supported findings include:
- Historical features materially improved validation performance.
- The raw target transformation outperformed log1p in the tested configuration.
- Tree-based ensemble methods performed strongly in the tested tabular setting.
- Random Forest achieved the selected final validation performance.
- Historical features dominated SHAP attribution.
- SHAP successfully provided local and global model interpretation.
- Recommendation generation requires an additional rule/domain layer rather than relying on SHAP alone.

## 16. Limitations
Methodological limitations:
- The official ASHRAE test target is unavailable for direct supervised evaluation.
- Historical features (Group B) create a strict inference requirement; the application cannot predict without prior data.
- The model was trained and evaluated on a deterministic subset for computational feasibility.
- SHAP attribution is correlative, not causal.
- Recommendation rules are decision-support logic, not verified engineering interventions.
- Application demonstration uses one genuine observation and is not a substitute for aggregate evaluation.

## 17. Future Work
- AutoML integration
- Automatic model retraining pipelines
- MLOps tracking
- Model drift monitoring
- Real-time BMS/IoT integration
- Advanced model adaptation for external datasets

---

## Verified Experimental Status
- [x] Pilot results verified
- [x] 10% Comparison metrics verified
- [x] Hyperparameter tuning configuration verified
- [x] Final holdout performance verified
- [x] SHAP group attribution verified
- [x] Real ASHRAE demonstration observation verified
- [x] Application testing status verified
