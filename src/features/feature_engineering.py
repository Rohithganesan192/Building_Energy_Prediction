import pandas as pd
import numpy as np
from pathlib import Path

from src.features.feature_config import (
    PROC_DIR, FEATURES_DIR, META_CLEAN, WEATHER_TRAIN_CLEAN, 
    WEATHER_TEST_CLEAN, METER_MAPPING, LAG_HOURS, ROLLING_WINDOWS
)
from src.features.temporal_features import build_temporal_features
from src.features.historical_features import build_historical_features


def process_weather(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process weather data before joining.
    Sorts chronologically and forward-fills missing values within each site.
    This prevents temporal leakage because ffill only uses past observations.
    """
    weather_df = weather_df.copy()
    weather_df["timestamp"] = pd.to_datetime(weather_df["timestamp"])
    
    # Sort chronologically to ensure ffill is strictly past-to-future
    weather_df = weather_df.sort_values(["site_id", "timestamp"])
    
    # Forward fill continuous weather features within each site
    w_cols = ["air_temperature", "dew_temperature", "sea_level_pressure", 
              "wind_speed", "wind_direction", "cloud_coverage", "precip_depth_1_hr"]
    
    # Group by site and ffill
    weather_df[w_cols] = weather_df.groupby("site_id")[w_cols].ffill()
    
    # Deduplicate to prevent multiplying energy rows on join
    weather_df = weather_df.drop_duplicates(subset=["site_id", "timestamp"])
    
    return weather_df

def build_features_for_sample(energy_df: pd.DataFrame, 
                              meta_df: pd.DataFrame, 
                              weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the full feature engineering pipeline to a DataFrame.
    Assumes energy_df contains all rows for a subset of buildings.
    """
    # 1. Temporal Features
    df = build_temporal_features(energy_df, timestamp_col="timestamp")
    
    # 2. Building Features
    df = df.merge(meta_df, on="building_id", how="left")
    
    # 3. Weather Features
    weather_processed = process_weather(weather_df)
    
    # Ensure site_id exists for weather join
    if "site_id" not in df.columns:
        raise KeyError("site_id is missing from building metadata merge.")
        
    # Join weather. We use left join to preserve energy records.
    df = df.merge(weather_processed, on=["site_id", "timestamp"], how="left")
    
    # 4. Historical Features
    # The historical_features module now handles sorting and group-wise extraction internally.
    df = build_historical_features(df, lags=LAG_HOURS, rolling_windows=ROLLING_WINDOWS)
    
    # 5. Categorical String Mapping
    df["meter_name"] = df["meter"].map(METER_MAPPING)
    
    return df
