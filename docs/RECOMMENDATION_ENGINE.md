# Recommendation Engine Methodology

## 1. Purpose
The recommendation engine serves as a decision-support layer bridging raw machine-learning predictions with actionable building management strategies. It translates complex model explanations into clear, human-readable operational advice.

## 2. Relationship between Prediction and Recommendation
Predictions establish *what* energy load is anticipated. The recommendation engine explores *why* that load is anticipated by inspecting the model's internal feature attributions, then evaluates if those attributions map to a logical operational review.

## 3. SHAP Role
The engine relies on exact SHAP (SHapley Additive exPlanations) values to identify which features most heavily drove a specific prediction upward. SHAP provides the mathematical attribution required to trigger specific domain rules.

## 4. Driver Classification
Features are categorized by their functional domain:
- **Historical**: Lagged consumption and rolling statistics (`lag_1`, `rolling_mean_24`)
- **Temporal**: Time-of-day, day-of-week, seasonality (`hour_cos`, `is_weekend`)
- **Weather**: External loads (`air_temperature`, `dew_temperature`)
- **Building/Meter**: Static identifiers (`square_feet`, `primary_use`)

## 5. Controllability Classification
Features are further categorized by their controllability:
- **Indirectly actionable**: Historical consumption indicates a persistent operational state that can be reviewed, but the feature itself is a proxy.
- **Actionable via scheduling**: Temporal features highlight recurring patterns that can be addressed by modifying HVAC/lighting schedules.
- **Actionable via HVAC review**: Weather features highlight external loads; setpoint strategies can be reviewed in response.
- **Not directly actionable / Contextual**: Static building features cannot be altered.

## 6. Recommendation Rules
Rules are structured mappings linking a `driver_type`, a set of `primary_feature_triggers`, and a `condition` (e.g., strong positive SHAP) to a specific `recommendation`. The engine evaluates real-time SHAP output against these rules to generate contextual advice.

## 7. Evidence Requirements
A recommendation is only generated if:
1. The SHAP attribution for a defined feature strongly exceeds a positive threshold (indicating it is driving the prediction upward).
2. The feature maps to a defined rule supported by building-domain logic.

## 8. Limitations
- **No Causal Guarantee**: Modifying an operational schedule based on a recommendation may not yield a proportional reduction in actual energy usage.
- **Context Missing**: The model does not know if a building is legitimately occupied during an "unusual" hour (e.g., a special event); recommendations require human review.

## 9. Non-causal Interpretation
> **CRITICAL DISCLAIMER**: SHAP identifies features that contribute to model predictions. It does not establish that changing a feature will cause a corresponding change in energy consumption.

## 10. Testing Strategy
The recommendation engine logic is validated via automated unit tests (`tests/test_recommendation_engine.py`) to ensure it handles valid SHAP inputs, ignores malformed or missing inputs without crashing, respects threshold triggers, and outputs properly formatted warnings without hallucinating arbitrary rules.
