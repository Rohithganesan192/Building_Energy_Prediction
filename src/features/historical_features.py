import pandas as pd
import numpy as np

def build_historical_features(df: pd.DataFrame, 
                              target_col: str = "meter_reading",
                              lags: list = [1, 24, 168],
                              rolling_windows: list = [24, 168]) -> pd.DataFrame:
    """
    Build historical lag and rolling features.
    Handles grouping and sorting internally to prevent temporal leakage,
    avoiding pandas groupby.apply() column-dropping bugs.
    
    DEPENDENCY WARNING: 
    This function is target-dependent. It assumes the target column 
    (`meter_reading`) exists. It can be executed directly on the 2016 
    training and validation data where consumption is natively observed. 
    However, the official ASHRAE 2017-2018 test dataset legitimately 
    has no `meter_reading`. Therefore, these historical features cannot 
    be directly calculated for official test inference without previously 
    observed consumption data feeds or an iterative recursive prediction strategy.
    """
    df = df.copy()
    
    # 1. Sort strictly chronologically within each group
    df = df.sort_values(["building_id", "meter", "timestamp"])
    
    # 2. Lag features (grouped)
    grp = df.groupby(["building_id", "meter"])[target_col]
    
    for lag in lags:
        df[f"lag_{lag}"] = grp.shift(lag)
        
    # 3. Rolling features (shift by 1 to exclude current row, preventing leakage)
    shifted_target = grp.shift(1)
    shifted_grp = shifted_target.groupby([df["building_id"], df["meter"]])
    
    for window in rolling_windows:
        # min_periods=1 ensures mean/std computation even if window is incomplete
        roll = shifted_grp.rolling(window=window, min_periods=1)
        
        # groupby.rolling returns a MultiIndex (building_id, meter, original_index)
        # Drop the group levels to align exactly with df's original index
        df[f"rolling_mean_{window}"] = roll.mean().reset_index(level=[0, 1], drop=True)
        df[f"rolling_std_{window}"] = roll.std().reset_index(level=[0, 1], drop=True)
        
    return df
