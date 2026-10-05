"""
experiment_config.py
====================
Configuration for Phase 6 modeling experiments.
Defines features, target transformations, splits, and subsampling strategy.
"""
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "features" / "train_features.csv"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
REPORTS_FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

# ------------------------------------------------------------------
# Feature Groups
# ------------------------------------------------------------------
FEATURE_GROUP_A = [
    # Temporal
    "hour", "day_of_week", "month", "day_of_year", "is_weekend",
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos",
    "month_sin", "month_cos",
    # Building
    "site_id", "primary_use", "square_feet", "year_built", "floor_count",
    # Weather
    "air_temperature", "cloud_coverage", "dew_temperature",
    "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed",
    # Meter identity (categorical)
    "meter", 
    # meter_name is supplementary and perfectly correlated with meter; 
    # we use the canonical numeric meter for modeling.
]

# Feature Group B: Exogenous + Target-dependent Historical
# INFERENCE LIMITATION WARNING:
# Historical features are constructed from previously observed meter_reading values.
# For the 2016 experimental holdout, this represents a one-step-ahead/rolling 
# operational forecasting setting where previous consumption observations are available.
# It does NOT represent a scenario where all December predictions are generated 
# without observing any December consumption.
# The official ASHRAE 2017-2018 test file contains no meter_reading, so the 
# existing Group B features cannot be directly generated from that file.
# This is an inference/deployment constraint, not a feature-engineering failure.
FEATURE_GROUP_B = FEATURE_GROUP_A + [
    "lag_1", "lag_24", "lag_168",
    "rolling_mean_24", "rolling_mean_168",
    "rolling_std_24", "rolling_std_168"
]

CATEGORICAL_FEATURES = ["meter", "primary_use", "site_id"]

# ------------------------------------------------------------------
# Targets & Transformations
# ------------------------------------------------------------------
TARGET_COL = "meter_reading"
TARGET_TRANSFORMS = ["raw", "log1p"]

# ------------------------------------------------------------------
# Chronological Splits (2016 Training Data Only)
# ------------------------------------------------------------------
# Note: The December 2016 split is an "experimental chronological holdout"
# used to simulate future performance. It is NOT the official ASHRAE test set.
SPLIT_TRAIN_END = "2016-09-30"
SPLIT_VAL_START = "2016-10-01"
SPLIT_VAL_END   = "2016-11-30"
SPLIT_TEST_START= "2016-12-01"

# ------------------------------------------------------------------
# Pilot / Subsampling Configuration
# ------------------------------------------------------------------
# To perform rapid pilot experiments on this 20M row dataset without random 
# time-slicing, we sample complete buildings deterministically.
PILOT_BUILDING_FRACTION = 0.01
COMPARISON_BUILDING_FRACTION = 0.10

# We use a fixed seed for hashing so the exact same buildings are selected every time.
PILOT_SEED = 42

TOTAL_BUILDINGS_KNOWN = 1449 # From Phase 5 audit
