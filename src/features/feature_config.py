import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROC_DIR = PROJECT_ROOT / "data" / "processed"
FEATURES_DIR = PROJECT_ROOT / "data" / "features"

TRAIN_CLEAN = PROC_DIR / "train_clean.csv"
TEST_CLEAN = PROC_DIR / "test_clean.csv"
META_CLEAN = PROC_DIR / "building_metadata_clean.csv"
WEATHER_TRAIN_CLEAN = PROC_DIR / "weather_train_clean.csv"
WEATHER_TEST_CLEAN = PROC_DIR / "weather_test_clean.csv"

# Output paths
SAMPLE_OUT = FEATURES_DIR / "train_features_sample.csv"
TRAIN_FEATURES_OUT = FEATURES_DIR / "train_features.csv"

# Columns
METADATA_COLS = ["site_id", "building_id", "primary_use", "square_feet", "year_built", "floor_count"]
WEATHER_COLS = ["site_id", "timestamp", "air_temperature", "cloud_coverage", "dew_temperature", 
                "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed"]

# Meter mapping
METER_MAPPING = {
    0: "Electricity",
    1: "ChilledWater",
    2: "Steam",
    3: "HotWater"
}

# Historical feature parameters
LAG_HOURS = [1, 24, 168]
ROLLING_WINDOWS = [24, 168]  # hours

# How many feature rows to serialize to CSV in one call.
# Keeping this small prevents pandas from allocating a large intermediate
# Unicode buffer for the entire group at once, which caused the
# numpy._ArrayMemoryError seen at group write time.
FEATURE_WRITE_BATCH_SIZE = 500

CHUNKSIZE = 1_000_000
