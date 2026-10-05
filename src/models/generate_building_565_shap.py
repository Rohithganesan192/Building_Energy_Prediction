import os
import sys

# Inject project root into python path so we can import src from anywhere
sys.path.append(r"c:\Users\ROHITHGANESAN G\Building_Energy_Prediction")

import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import shap

from src.models.experiment_config import (
    FEATURES_PATH, CATEGORICAL_FEATURES, TARGET_COL, 
    REPORTS_FIGURES_DIR, MODELS_DIR, PROJECT_ROOT
)

def main():
    model_path = MODELS_DIR / "final_random_forest_raw_group_b.joblib"
    preprocessor_path = MODELS_DIR / "final_preprocessor.joblib"
    schema_path = MODELS_DIR / "final_feature_schema.json"
    
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    feature_ordering = schema["feature_ordering"]
    
    # Load Building 565 observation directly from demo JSON
    demo_json_path = PROJECT_ROOT / "reports" / "demo_real_row.json"
    with open(demo_json_path, "r") as f:
        obs_data = json.load(f)
        
    # Create DataFrame with the exact feature ordering
    found_row = pd.DataFrame([obs_data])
    
    y_actual = found_row[TARGET_COL].values[0]
    print(f"Actual value: {y_actual}")
    
    X_raw = found_row[feature_ordering]
    X_processed = preprocessor.transform(X_raw)
    
    try:
        input_features = preprocessor.feature_names_out_
    except AttributeError:
        num_cols = schema["numerical_features"]
        cat_cols = schema["categorical_features"]
        input_features = num_cols + cat_cols
        
    X_processed_df = pd.DataFrame(X_processed, columns=input_features)
    
    pred = model.predict(X_processed_df)[0]
    print(f"Predicted value: {pred}")
    
    # Calculate SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_processed_df)[0]
    base_value = explainer.expected_value
    if isinstance(base_value, (np.ndarray, list)):
        base_value = float(base_value[0])
    
    print(f"Base value: {base_value}")
    
    # Map feature names to human-readable names
    name_map = {
        'lag_1': 'Previous-hour consumption',
        'lag_24': 'Previous-day same-hour consumption',
        'rolling_mean_24': '24-hour historical average',
        'lag_168': 'Previous-week same-hour consumption',
        'square_feet': 'Building floor area',
        'hour_cos': 'Hour-cycle representation',
    }
    mapped_features = [name_map.get(f, f) for f in input_features]
    
    exp = shap.Explanation(
        values=shap_values,
        base_values=base_value,
        data=X_processed_df.iloc[0].values,
        feature_names=mapped_features
    )
    
    plt.style.use('grayscale')
    fig = plt.figure(figsize=(10, 6), facecolor='white')
    ax = fig.gca()
    
    shap.plots.waterfall(exp, show=False)
    
    # Try to change colors to grayscale
    for child in ax.get_children():
        if isinstance(child, plt.Rectangle):
            color = child.get_facecolor()
            # color is an RGBA tuple
            if color[0] > 0.5 and color[2] < 0.5: # Reddish
                child.set_facecolor('0.3')
                child.set_edgecolor('black')
            elif color[2] > 0.5 and color[0] < 0.5: # Blueish
                child.set_facecolor('0.7')
                child.set_edgecolor('black')
        elif isinstance(child, plt.Text):
            try:
                child.set_color('black')
            except:
                pass

    plt.title("Local SHAP Explanation for the Building 565 Application Demonstration", fontsize=12)
    plt.tight_layout()
    plt.savefig(REPORTS_FIGURES_DIR / "shap_local_building_565.png", dpi=300, facecolor='white')
    plt.close()

if __name__ == "__main__":
    main()
