"""
train_models.py
===============
Model factory and pilot orchestration for Phase 6.
"""
import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# Model Imports
import time
import gc

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from src.models.experiment_config import (
    FEATURES_PATH, FEATURE_GROUP_A, FEATURE_GROUP_B, CATEGORICAL_FEATURES,
    TARGET_COL, TARGET_TRANSFORMS, REPORTS_TABLES_DIR, MODELS_DIR,
    PILOT_BUILDING_FRACTION, COMPARISON_BUILDING_FRACTION
)
from src.models.split_data import load_and_split_pilot_data
from src.models.preprocessing import get_preprocessor
from src.models.evaluate_models import evaluate_predictions

def get_model(model_name: str, random_state: int = 42):
    """
    Returns an instantiated, un-tuned model.
    """
    if model_name == "LinearRegression":
        return LinearRegression(n_jobs=-1)
    elif model_name == "DecisionTree":
        return DecisionTreeRegressor(random_state=random_state)
    elif model_name == "RandomForest":
        # Keep n_estimators small for pilot tests
        return RandomForestRegressor(n_estimators=10, max_depth=5, n_jobs=-1, random_state=random_state)
    elif model_name == "XGBoost":
        # We are using safe OrdinalEncoding via XGBoostPreprocessor, so native categorical is not needed
        return XGBRegressor(n_estimators=100, max_depth=5, n_jobs=-1, random_state=random_state)
    elif model_name == "LightGBM":
        return LGBMRegressor(n_estimators=100, max_depth=5, n_jobs=-1, random_state=random_state)
    elif model_name == "CatBoost":
        # Verbose=0 to prevent enormous logs. CatBoost handles strings natively.
        return CatBoostRegressor(iterations=100, depth=5, thread_count=-1, random_seed=random_state, verbose=0)
    else:
        raise ValueError(f"Unknown model_name: {model_name}")

def run_pilot(fraction_type: str = "pilot"):
    print("=" * 60)
    if fraction_type == "10pct":
        print("Phase 6: 10% Comparison Model Training (Untuned)")
        fraction = COMPARISON_BUILDING_FRACTION
        out_filename = "comparison_10pct_results.csv"
    else:
        print("Phase 6: Pilot Model Training")
        fraction = PILOT_BUILDING_FRACTION
        out_filename = "pilot_results.csv"
    print("=" * 60)
    
    # 1. Ensure output directories exist
    REPORTS_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Load and split pilot data
    # We only need the features from Group B (which includes Group A) and target
    load_cols = list(set(FEATURE_GROUP_B + [TARGET_COL, "building_id", "timestamp"]))
    train_df, val_df, test_df = load_and_split_pilot_data(FEATURES_PATH, fraction=fraction, columns=load_cols)
    
    # 3. Define the experiment grid
    models_to_test = ["LinearRegression", "DecisionTree", "RandomForest", "XGBoost", "LightGBM", "CatBoost"]
    feature_groups = {"GroupA": FEATURE_GROUP_A, "GroupB": FEATURE_GROUP_B}
    target_transforms = TARGET_TRANSFORMS
    
    results = []
    
    # 4. Explicitly protect December holdout
    print("\n[PROTOCOL] December 2016 is reserved as an untouched chronological")
    print("[PROTOCOL] holdout for final evaluation after model and feature")
    print("[PROTOCOL] configuration selection. It will NOT be used here.")
    
    # Run a small grid
    for transform in target_transforms:
        
        # Prepare targets
        if transform == "log1p":
            y_train = np.log1p(train_df[TARGET_COL])
        else:
            y_train = train_df[TARGET_COL]
            
        y_val_raw = val_df[TARGET_COL] # Evaluate function needs the raw true target
        # test_df is strictly protected and ignored during this selection loop
        
        for f_group_name, f_group_cols in feature_groups.items():
            
            num_cols = [c for c in f_group_cols if c not in CATEGORICAL_FEATURES]
            cat_cols = [c for c in f_group_cols if c in CATEGORICAL_FEATURES]
            
            for model_name in models_to_test:
                print(f"\n--- Training: {model_name} | {f_group_name} | Target: {transform} ---")
                
                # Preprocess
                preprocessor = get_preprocessor(model_name, num_cols, cat_cols)
                
                # Fit preprocessor on train only
                X_train_processed = preprocessor.fit(train_df[f_group_cols]).transform(train_df[f_group_cols])
                X_val_processed = preprocessor.transform(val_df[f_group_cols])
                # test_df preprocessor transform intentionally omitted to save memory
                
                # Instantiate model
                model = get_model(model_name)
                
                # Special fit kwargs for native categorical support
                fit_kwargs = {}
                if model_name == "CatBoost":
                    fit_kwargs["cat_features"] = cat_cols
                
                # Train
                print("Fitting model...")
                t0_train = time.time()
                try:
                    model.fit(X_train_processed, y_train, **fit_kwargs)
                    train_time = time.time() - t0_train
                    
                    # Predict
                    print("Evaluating...")
                    t0_pred = time.time()
                    pred_val = model.predict(X_val_processed)
                    pred_time = time.time() - t0_pred
                    
                    # Evaluate on original scale
                    metrics_val = evaluate_predictions(y_val_raw, pred_val, transform)
                    
                    print(f"Validation MAE: {metrics_val['MAE']:.2f} | RMSE: {metrics_val['RMSE']:.2f} | R2: {metrics_val['R2']:.4f}")
                    status = "SUCCESS"
                    
                    results.append({
                        "model": model_name,
                        "target_transform": transform,
                        "feature_group": f_group_name,
                        "train_rows": len(train_df),
                        "validation_rows": len(val_df),
                        "training_time": round(train_time, 2),
                        "prediction_time": round(pred_time, 2),
                        "val_mae": metrics_val['MAE'],
                        "val_rmse": metrics_val['RMSE'],
                        "val_r2": metrics_val['R2'],
                        "status": status,
                    })
                    
                except Exception as e:
                    print(f"FAILED: {e}")
                    results.append({
                        "model": model_name,
                        "target_transform": transform,
                        "feature_group": f_group_name,
                        "train_rows": len(train_df),
                        "validation_rows": len(val_df),
                        "training_time": None,
                        "prediction_time": None,
                        "val_mae": None,
                        "val_rmse": None,
                        "val_r2": None,
                        "status": f"ERROR: {e}",
                    })
                    
                # Clean up memory immediately
                del model
                del X_train_processed
                del X_val_processed
                gc.collect()
                
    # Save results
    results_df = pd.DataFrame(results)
    results_path = REPORTS_TABLES_DIR / out_filename
    results_df.to_csv(results_path, index=False)
    print(f"\nExperiment complete! Results saved to {results_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-pilot", action="store_true", help="Run the deterministic 1% pilot grid")
    parser.add_argument("--run-10pct", action="store_true", help="Run the 10% comparison experiment")
    args = parser.parse_args()
    
    if args.run_10pct:
        run_pilot(fraction_type="10pct")
    elif args.run_pilot:
        run_pilot(fraction_type="pilot")
    else:
        print("Use --run-pilot or --run-10pct to execute the pipeline.")
