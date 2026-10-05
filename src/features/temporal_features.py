import pandas as pd
import numpy as np

def build_temporal_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    """
    Extract temporal features from a timestamp column.
    Includes basic components (hour, day of week, month, etc.)
    and cyclical encodings (sin/cos) for fair comparison across
    tree-based and linear models.
    """
    df = df.copy()
    
    # Ensure datetime type
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    dt = df[timestamp_col].dt
    
    # Basic components
    df["hour"] = dt.hour
    df["day_of_week"] = dt.dayofweek
    df["month"] = dt.month
    df["day_of_year"] = dt.dayofyear
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(np.int8)
    
    # Cyclical encodings
    # Hour: 0-23
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    
    # Day of week: 0-6
    df["day_of_week_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
    df["day_of_week_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
    
    # Month: 1-12
    df["month_sin"] = np.sin(2 * np.pi * (df["month"] - 1) / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * (df["month"] - 1) / 12.0)
    
    return df
