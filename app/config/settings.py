import os
from pathlib import Path

# Base Project Root
PROJECT_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Model Artifact Paths
MODELS_DIR = PROJECT_ROOT / "models"
FINAL_MODEL_PATH = MODELS_DIR / "final_random_forest_raw_group_b.joblib"
PREPROCESSOR_PATH = MODELS_DIR / "final_preprocessor.joblib"
SCHEMA_PATH = MODELS_DIR / "final_feature_schema.json"

# SHAP Artifact Paths
REPORTS_TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
GLOBAL_SHAP_PATH = REPORTS_TABLES_DIR / "shap_global_importance.csv"

# Minimum positive SHAP threshold for recommendations
SHAP_RECOMMENDATION_THRESHOLD = 1.0
