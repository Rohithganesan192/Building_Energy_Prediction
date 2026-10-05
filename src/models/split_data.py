"""
split_data.py
=============
Provides modular functions for deterministically subsampling buildings
and applying chronological splits to the time-series data.
"""
import pandas as pd
import hashlib

from src.models.experiment_config import (
    SPLIT_TRAIN_END, SPLIT_VAL_START, SPLIT_VAL_END, SPLIT_TEST_START,
    PILOT_BUILDING_FRACTION, PILOT_SEED, TOTAL_BUILDINGS_KNOWN
)

def is_selected_building(building_id: int, fraction: float = PILOT_BUILDING_FRACTION, seed: int = PILOT_SEED) -> bool:
    """
    Deterministic building selector based on MD5 hashing.
    Ensures that regardless of chunk boundaries, a building is consistently
    selected or rejected across the entire dataset, maintaining the complete
    time series for chosen buildings.
    """
    # Create a stable string from building_id + seed
    val = f"{building_id}_{seed}".encode("utf-8")
    hash_hex = hashlib.md5(val).hexdigest()
    # Use first 8 characters to get a uniform int, modulo 10000 for percentage
    hash_int = int(hash_hex[:8], 16)
    return (hash_int % 10000) / 10000.0 < fraction

def chronological_split(df: pd.DataFrame):
    """
    Splits the 2016 DataFrame chronologically.
    Train: Jan 1 - Sep 30
    Validation: Oct 1 - Nov 30
    Experimental Test: Dec 1 - Dec 31
    
    WARNING: The experimental test split (Dec 2016) is NOT the official ASHRAE test set.
    """
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
    train_mask = df["timestamp"] <= pd.to_datetime(SPLIT_TRAIN_END + " 23:59:59")
    val_mask = (df["timestamp"] >= pd.to_datetime(SPLIT_VAL_START)) & (df["timestamp"] <= pd.to_datetime(SPLIT_VAL_END + " 23:59:59"))
    test_mask = df["timestamp"] >= pd.to_datetime(SPLIT_TEST_START)
    
    return df[train_mask].copy(), df[val_mask].copy(), df[test_mask].copy()

def load_and_split_pilot_data(filepath: str, fraction: float = PILOT_BUILDING_FRACTION, columns: list = None):
    """
    Loads data in chunks, applying the deterministic building filter and
    collecting the pilot dataset, then splits it chronologically.
    """
    print(f"Loading pilot data (fraction={fraction*100:.0f}%) from {filepath}...")
    
    chunks = []
    chunk_iter = pd.read_csv(filepath, chunksize=1_000_000, usecols=columns)
    
    for i, chunk in enumerate(chunk_iter):
        # Filter rows by checking if building_id is selected
        mask = chunk["building_id"].apply(lambda x: is_selected_building(x, fraction=fraction))
        pilot_chunk = chunk[mask]
        
        if not pilot_chunk.empty:
            chunks.append(pilot_chunk)
            
    if not chunks:
        raise ValueError("No buildings were selected by the deterministic filter. Increase fraction or change seed.")
        
    pilot_df = pd.concat(chunks, ignore_index=True)
    
    selected_buildings = pilot_df["building_id"].nunique()
    total_selected_rows = len(pilot_df)
    
    print("\n--- Subsample Statistics ---")
    print(f"Total buildings (known) : {TOTAL_BUILDINGS_KNOWN}")
    print(f"Selected buildings      : {selected_buildings}")
    print(f"Percentage of buildings : {(selected_buildings / TOTAL_BUILDINGS_KNOWN) * 100:.2f}%")
    print(f"Total rows selected     : {total_selected_rows:,}")
    
    print("\nApplying chronological splits...")
    train_df, val_df, test_df = chronological_split(pilot_df)
    
    print(f"Train rows (Jan-Sep)    : {len(train_df):,}")
    print(f"Val rows (Oct-Nov)      : {len(val_df):,}")
    print(f"Holdout rows (Dec)      : {len(test_df):,}")
    
    # Verify no overlap
    assert train_df["timestamp"].max() < val_df["timestamp"].min(), "Train and Validation timestamps overlap!"
    assert val_df["timestamp"].max() < test_df["timestamp"].min(), "Validation and Test timestamps overlap!"
    
    return train_df, val_df, test_df
