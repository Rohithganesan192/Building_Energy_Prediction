"""
evaluate_models.py
==================
Centralized model evaluation metrics.
Handles inverse transformations for log1p targets.
"""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_predictions(y_true_raw, y_pred, target_transform: str):
    """
    Evaluates predictions consistently.
    
    Parameters
    ----------
    y_true_raw : array-like
        The true target values on the original scale (meter_reading).
    y_pred : array-like
        The model predictions. If the model was trained on log1p, these
        predictions are in log scale and will be inverse-transformed here.
    target_transform : str
        "raw" or "log1p". Defines how y_pred should be handled before scoring.
        
    Returns
    -------
    dict
        MAE, RMSE, and R2 calculated on the ORIGINAL target scale.
    """
    
    if target_transform == "log1p":
        # Inverse transform: expm1 undoes log1p
        # Clip to prevent overflow/underflow if model goes wild
        y_pred_clipped = np.clip(y_pred, a_min=-1, a_max=20) 
        y_pred_raw = np.expm1(y_pred_clipped)
    elif target_transform == "raw":
        y_pred_raw = y_pred
    else:
        raise ValueError(f"Unknown target_transform: {target_transform}")
        
    # Prevent negative predictions on the raw scale (energy cannot be < 0)
    # However, source data might have minor negatives, so we clip at min of y_true
    y_pred_raw = np.maximum(y_pred_raw, y_true_raw.min())
    
    mae = mean_absolute_error(y_true_raw, y_pred_raw)
    rmse = np.sqrt(mean_squared_error(y_true_raw, y_pred_raw))
    r2 = r2_score(y_true_raw, y_pred_raw)
    
    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }
