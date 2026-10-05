"""
tune_models.py
==============
Phase 7: Hyperparameter Tuning on Raw Target + Group B
Using 10% Deterministic Building Sample.
"""
import os
import time
import json
import argparse
import pandas as pd
import numpy as np
import gc

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.model_selection import ParameterSampler

from src.models.experiment_config import (
    FEATURES_PATH, FEATURE_GROUP_B, CATEGORICAL_FEATURES,
    TARGET_COL, REPORTS_TABLES_DIR, MODELS_DIR,
    COMPARISON_BUILDING_FRACTION
)
from src.models.split_data import load_and_split_pilot_data
from src.models.preprocessing import get_preprocessor
from src.models.evaluate_models import evaluate_predictions

def get_param_grid(model_name: str):
    if model_name == "DecisionTree":
        return {
            "max_depth": [5, 10, 15, 20, None],
            "min_samples_split": [2, 10, 50],
            "min_samples_leaf": [1, 5, 20],
            "max_features": [None, "sqrt", "log2"]
        }
    elif model_name == "RandomForest":
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [5, 10, 15, 20],
            "min_samples_split": [2, 10, 50],
            "min_samples_leaf": [1, 5, 20],
            "max_features": [None, "sqrt"]
        }
    elif model_name == "XGBoost":
        return {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7, 9],
            "learning_rate": [0.01, 0.05, 0.1],
            "min_child_weight": [1, 5, 10],
            "subsample": [0.7, 0.8, 1.0],
            "colsample_bytree": [0.7, 0.8, 1.0],
            "reg_alpha": [0, 0.1, 1],
            "reg_lambda": [1, 5, 10]
        }
    elif model_name == "LightGBM":
        return {
            "n_estimators": [100, 200, 300],
            "num_leaves": [31, 63, 127],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [5, 7, 9, -1],
            "min_child_samples": [20, 50, 100],
            "subsample": [0.7, 0.8, 1.0],
            "colsample_bytree": [0.7, 0.8, 1.0],
            "reg_alpha": [0, 0.1, 1],
            "reg_lambda": [1, 5, 10]
        }
    elif model_name == "CatBoost":
        return {
            "iterations": [100, 200, 300],
            "depth": [4, 6, 8, 10],
            "learning_rate": [0.01, 0.05, 0.1],
            "l2_leaf_reg": [1, 3, 5, 9],
            "random_strength": [0.1, 1, 5],
            "bagging_temperature": [0, 1, 5]
        }
    else:
        return {}

def get_base_model(model_name: str, random_state: int = 42):
    if model_name == "LinearRegression":
        return LinearRegression(n_jobs=-1)
    elif model_name == "DecisionTree":
        return DecisionTreeRegressor(random_state=random_state)
    elif model_name == "RandomForest":
        return RandomForestRegressor(n_jobs=-1, random_state=random_state)
    elif model_name == "XGBoost":
        return XGBRegressor(n_jobs=-1, random_state=random_state)
    elif model_name == "LightGBM":
        return LGBMRegressor(n_jobs=-1, random_state=random_state)
    elif model_name == "CatBoost":
        return CatBoostRegressor(thread_count=-1, random_seed=random_state, verbose=0)
    else:
        raise ValueError(f"Unknown model_name: {model_name}")

def run_tuning(n_iter=10):
    print("=" * 60)
    print("Phase 7: Hyperparameter Tuning (10% Sample)")
    print(f"Target: raw | Feature Group: GroupB | Trials per model: {n_iter}")
    print("=" * 60)
    
    REPORTS_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    load_cols = list(set(FEATURE_GROUP_B + [TARGET_COL, "building_id", "timestamp"]))
    train_df, val_df, test_df = load_and_split_pilot_data(FEATURES_PATH, fraction=COMPARISON_BUILDING_FRACTION, columns=load_cols)
    
    print("\n[PROTOCOL] December 2016 is protected and untouched.")
    
    y_train = train_df[TARGET_COL]
    y_val = val_df[TARGET_COL]
    
    models_to_test = ["LinearRegression", "DecisionTree", "RandomForest", "XGBoost", "LightGBM", "CatBoost"]
    
    num_cols = [c for c in FEATURE_GROUP_B if c not in CATEGORICAL_FEATURES]
    cat_cols = [c for c in FEATURE_GROUP_B if c in CATEGORICAL_FEATURES]
    
    tuning_results = []
    best_hyperparameters = []
    
    for model_name in models_to_test:
        print(f"\n--- Tuning {model_name} ---")
        
        preprocessor = get_preprocessor(model_name, num_cols, cat_cols)
        X_train_processed = preprocessor.fit(train_df[FEATURE_GROUP_B]).transform(train_df[FEATURE_GROUP_B])
        X_val_processed = preprocessor.transform(val_df[FEATURE_GROUP_B])
        
        fit_kwargs = {}
        if model_name == "CatBoost":
            fit_kwargs["cat_features"] = cat_cols
            
        if model_name == "LinearRegression":
            print("Evaluating Linear Regression (Untuned Baseline)")
            model = get_base_model(model_name)
            t0 = time.time()
            model.fit(X_train_processed, y_train, **fit_kwargs)
            train_time = time.time() - t0
            
            t0_p = time.time()
            pred_val = model.predict(X_val_processed)
            pred_time = time.time() - t0_p
            
            metrics = evaluate_predictions(y_val, pred_val, "raw")
            print(f"MAE: {metrics['MAE']:.2f}, RMSE: {metrics['RMSE']:.2f}, R2: {metrics['R2']:.4f}")
            
            res = {
                "model": model_name,
                "feature_group": "GroupB",
                "target_transform": "raw",
                "best_parameters": "{}",
                "validation_mae": metrics["MAE"],
                "validation_rmse": metrics["RMSE"],
                "validation_r2": metrics["R2"],
                "training_time_seconds": round(train_time, 2),
                "status": "SUCCESS"
            }
            tuning_results.append(res)
            best_hyperparameters.append({"model": model_name, "best_params": "{}"})
        else:
            param_grid = get_param_grid(model_name)
            # Use ParameterSampler to randomly sample n_iter parameters, preserving chronological constraints
            param_list = list(ParameterSampler(param_grid, n_iter=n_iter, random_state=42))
            
            best_rmse = float('inf')
            best_params = None
            best_metrics = None
            best_times = None
            
            for i, params in enumerate(param_list):
                print(f"  Trial {i+1}/{len(param_list)}: {params}")
                model = get_base_model(model_name)
                model.set_params(**params)
                
                try:
                    t0 = time.time()
                    model.fit(X_train_processed, y_train, **fit_kwargs)
                    train_time = time.time() - t0
                    
                    t0_p = time.time()
                    pred_val = model.predict(X_val_processed)
                    pred_time = time.time() - t0_p
                    
                    metrics = evaluate_predictions(y_val, pred_val, "raw")
                    print(f"    -> RMSE: {metrics['RMSE']:.2f} | MAE: {metrics['MAE']:.2f} | R2: {metrics['R2']:.4f}")
                    
                    if metrics["RMSE"] < best_rmse:
                        best_rmse = metrics["RMSE"]
                        best_params = params
                        best_metrics = metrics
                        best_times = (train_time, pred_time)
                except Exception as e:
                    print(f"    -> FAILED: {e}")
            
            print(f"*** Best {model_name} RMSE: {best_rmse:.2f} ***")
            print(f"*** Best Params: {best_params} ***")
            
            if best_params is not None:
                res = {
                    "model": model_name,
                    "feature_group": "GroupB",
                    "target_transform": "raw",
                    "best_parameters": json.dumps(best_params),
                    "validation_mae": best_metrics["MAE"],
                    "validation_rmse": best_metrics["RMSE"],
                    "validation_r2": best_metrics["R2"],
                    "training_time_seconds": round(best_times[0], 2),
                    "status": "SUCCESS"
                }
                tuning_results.append(res)
                best_hyperparameters.append({"model": model_name, "best_params": json.dumps(best_params)})
            else:
                res = {
                    "model": model_name,
                    "feature_group": "GroupB",
                    "target_transform": "raw",
                    "best_parameters": "",
                    "validation_mae": None,
                    "validation_rmse": None,
                    "validation_r2": None,
                    "training_time_seconds": None,
                    "status": "FAILED_ALL_TRIALS"
                }
                tuning_results.append(res)
        
        # Memory cleanup
        del model
        del X_train_processed
        del X_val_processed
        gc.collect()

    # Save results
    res_df = pd.DataFrame(tuning_results)
    res_path = REPORTS_TABLES_DIR / "tuning_results.csv"
    res_df.to_csv(res_path, index=False)
    
    params_df = pd.DataFrame(best_hyperparameters)
    params_path = REPORTS_TABLES_DIR / "best_hyperparameters.csv"
    params_df.to_csv(params_path, index=False)
    
    print(f"\nPhase 7 complete. Results saved to {res_path}")
    print("December 2016 remained untouched.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-iter", type=int, default=10, help="Number of random parameter configurations to test per model.")
    args = parser.parse_args()
    
    run_tuning(n_iter=args.n_iter)
