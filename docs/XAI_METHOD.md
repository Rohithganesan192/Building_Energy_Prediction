# Explainable AI (XAI) Methodology

## 1. Objective
This document outlines the methodological approach used for implementing Explainable AI (XAI) in the building energy prediction pipeline. The primary objective of the XAI implementation is to interpret the locked final machine learning model, answering:
1. Which features most strongly influence energy consumption predictions?
2. How does each feature influence predictions?
3. What is the relative contribution of historical autoregressive consumption features compared with exogenous/weather features?

## 2. Selection of SHAP
SHapley Additive exPlanations (SHAP) was chosen as the framework for interpretability. 
- **Theoretic Soundness:** SHAP is grounded in cooperative game theory, ensuring that the attribution of the model's output among its input features satisfies properties of local accuracy, missingness, and consistency.
- **Unified Measure:** It provides a unified measure of feature importance that bridges global interpretability and local explanations, allowing consistent analysis at both the dataset level and the individual prediction level.

## 3. Explainer Mechanism: TreeExplainer
Because the final selected model is a `RandomForestRegressor`, we utilize SHAP's `TreeExplainer`. 
- `TreeExplainer` is specifically optimized for tree-based machine learning models. 
- It computes exact SHAP values in polynomial time ($O(TLD^2)$), offering massive computational improvements over the model-agnostic `KernelExplainer`.

## 4. Explanation Sampling Strategy
Generating exact SHAP values for millions of rows is computationally prohibitive and unnecessary for robust global interpretation.
- Global SHAP analysis was performed on a deterministic sample of 1,000 observations from the October-November 2016 validation period to balance explanation stability and computational feasibility.
- **Holdout Protection:** The December 2016 holdout is strictly avoided during global SHAP analysis to maintain its status as an untouched inference benchmark. 

## 5. Global vs. Local Explanations
The methodology divides XAI into two scopes:
- **Global Explanations:** Aggregates SHAP values across the 1,000-row sample to calculate mean absolute SHAP values, establishing a universal feature ranking and generating beeswarm summary plots to visualize general model behavior.
- **Local Explanations:** Explains individual, specific predictions using waterfall plots, showing exactly how the model arrived at a single prediction starting from the expected base value.

## 6. Feature Grouping
To answer the core research question regarding the utility of autoregressive features, individual features are classified into functional groups:
- **Historical Consumption** (Group B autoregressive lags/rolling windows)
- **Weather** (Temperature, Wind, Dew Point, etc.)
- **Temporal** (Sine/Cosine encodings, day, hour)
- **Building** (Metadata, Year Built, Square Feet)
- **Meter** (Identity)

Summing the absolute SHAP contributions of these groups reveals their macroeconomic importance to the model.

## 7. Limitations and Disclaimer
**CRITICAL LIMITATION:** SHAP explains the *contribution of features to the model's prediction*; it does not establish causal relationships between features and physical energy consumption. 
- If `cloud_coverage` has a high SHAP value, it means the model relies heavily on that feature to predict the target, not necessarily that cloud coverage directly causes building energy usage to change (e.g., it could be collinear with a true unmeasured driver).
- Model explanations are strictly bounded by the correlations the algorithm has learned from the training data.

## 8. Reproducibility
The explanation pipeline uses `random_state=42` uniformly across data sampling and explanation functions to guarantee identical XAI artifacts on rerun.
