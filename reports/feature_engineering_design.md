# Phase 5: Feature Engineering Design

## Design Philosophy
This pipeline generates candidate features across Temporal, Building, Weather, and Historical domains. The objective is to produce a consistent and reproducible dataset that supports a fair comparison of models ranging from Linear Regression to Gradient Boosting Trees (LightGBM, XGBoost, CatBoost).

## Historical Feature Strategy
To provide meaningful time-series signals without introducing temporal leakage:
- **Lags**: Lag features (1h, 24h, 168h) are implemented directly by shifting the target variable backward in time for each specific `building_id` and `meter`.
- **Rolling Statistics**: Rolling mean and rolling standard deviation over 24h and 168h windows are calculated. 
- **Leakage Prevention**: To strictly avoid allowing the target at time $t$ to influence the rolling window for time $t$, the target series is shifted by 1 hour *before* applying the pandas `.rolling()` operation.
- **Train/Validation vs. Inference**: These historical features can be directly calculated for the 2016 training and validation sets where `meter_reading` is natively observed. However, the official 2017-2018 test set does not contain `meter_reading`. Therefore, using these lag features for future inference will require either historical data feeds or recursive prediction.
- **Implementation Constraint**: Since historical feature calculation requires sorting by `building_id`, `meter`, and `timestamp`, applying this logic across 20M rows requires careful group-wise processing. The current implementation leverages `groupby.apply()` for sample testing.

## Missing-Value Strategy
- **Building Metadata**: `year_built` and `floor_count` suffer from heavy missingness. In this phase, they are left as native `NaN`. Tree-based models (LightGBM, XGBoost) handle `NaN` splits inherently. Model-specific pipelines (e.g. median imputation for Linear Regression) will handle imputation in Phase 6.
- **Weather Data**: Missing weather entries are handled using a chronological forward fill (`ffill`) within each `site_id`, which never uses future observations (unlike `bfill`). Because weather changes continuously, the most recent past observation is a safe, non-leaking estimator for the current condition. This is marked as the initial candidate strategy to be evaluated experimentally later; it is not claimed to be universally optimal.

## Categorical Representation Strategy
- **Meter**: The original numeric `meter` (0 = Electricity, 1 = Chilled Water, 2 = Steam, 3 = Hot Water) is retained as a candidate canonical feature. A descriptive string column `meter_name` is also created for readability, but does not replace `meter`. 
- **Primary Use & Site ID**: These are preserved as unencoded strings/integers. 
- **Encoding Action**: Final categorical encoding (e.g., One-Hot Encoding for Linear Regression, native categorical passing for LightGBM/CatBoost) is deferred to the model-specific preprocessing pipelines in Phase 6 to ensure fair comparisons.

## Temporal Split Strategy
Due to the time-series nature of building energy consumption:
- Standard random k-fold or train-test splitting is invalid and causes temporal leakage.
- The 2016 training set will be chronologically divided. A standard approach will be to assign the first 9-10 months for training and the remaining 2-3 months for validation. 
- The official 2017-2018 test set remains untouched for final evaluation.

## Unresolved Design Decisions (Phase 6)
- **Target Transformation**: Whether to apply `log1p` to the right-skewed `meter_reading` remains an experimental decision.
- **Meter-Specific vs. Unified Models**: Whether to train a single large model with `meter` as a feature or four independent models per meter type.
- **Handling Extreme Outliers**: Whether extreme outliers identified in Phase 4 (e.g. Site 0 Steam) should be truncated or modeled as-is.

*End of Phase 5 Design Document*
