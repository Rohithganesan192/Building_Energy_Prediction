"""
explain_waterfall_only.py
=========================
Generates ONLY the 5 local SHAP waterfall plots to fix the scalar array dimension error.
Bypasses the full global computation.
"""
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

from src.models.experiment_config import (
    FEATURES_PATH, TARGET_COL, 
    REPORTS_FIGURES_DIR, MODELS_DIR,
    COMPARISON_BUILDING_FRACTION
)
from src.models.split_data import load_and_split_pilot_data

def main():
    print("=" * 60)
    print("Generating local SHAP waterfalls (5 observations only)")
    print("=" * 60)
    
    model_path = MODELS_DIR / "final_random_forest_raw_group_b.joblib"
    preprocessor_path = MODELS_DIR / "final_preprocessor.joblib"
    schema_path = MODELS_DIR / "final_feature_schema.json"
    
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    feature_ordering = schema["feature_ordering"]
    load_cols = list(set(feature_ordering + [TARGET_COL, "building_id", "timestamp"]))
    _, val_df, _ = load_and_split_pilot_data(FEATURES_PATH, fraction=COMPARISON_BUILDING_FRACTION, columns=load_cols)
    
    # We sample 1000 to match the EXACT random state shuffle, returning identical observations.
    explanation_df = val_df.sample(n=1000, random_state=42).copy()
    
    # Take ONLY the first 5 rows to skip heavy calculation
    local_sample_df = explanation_df.iloc[:5].copy()
    
    X_sample_raw = local_sample_df[feature_ordering]
    X_sample_processed = preprocessor.transform(X_sample_raw)
    
    try:
        input_features = preprocessor.feature_names_out_
    except AttributeError:
        input_features = schema["numerical_features"] + schema["categorical_features"]
        
    X_sample_processed_df = pd.DataFrame(X_sample_processed, columns=input_features)
    
    # TreeExplainer is exact, so computing on 5 rows yields the same values as computing on 1000 rows.
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample_processed_df)
    
    base = explainer.expected_value
    
    # EXACT CODE CORRECTION:
    # Cast expected_value array to a Python float scalar
    if isinstance(base, (np.ndarray, list)):
        base_scalar = float(base[0])
    else:
        base_scalar = float(base)
        
    for idx in range(5):
        sv = shap_values[idx, :]
        data_vals = X_sample_processed_df.iloc[idx].values
        
        try:
            plt.figure(figsize=(10, 6))
            exp = shap.Explanation(values=sv, base_values=base_scalar, data=data_vals, feature_names=input_features)
            shap.plots.waterfall(exp, show=False)
            plt.tight_layout()
            
            out_file = f"shap_local_obs_{idx}.png"
            plt.savefig(REPORTS_FIGURES_DIR / out_file, dpi=300)
            plt.close()
            print(f"Successfully generated {out_file}")
        except Exception as e:
            print(f"Error generating {out_file}: {e}")

if __name__ == "__main__":
    main()
