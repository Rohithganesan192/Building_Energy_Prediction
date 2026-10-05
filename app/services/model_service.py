import json
import joblib
from app.config.settings import FINAL_MODEL_PATH, PREPROCESSOR_PATH, SCHEMA_PATH
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ModelService:
    """
    Centralized model-loading mechanism.
    Singleton pattern ensures the 200-tree RF and preprocessor are loaded only once per session.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._load_artifacts()
        return cls._instance

    def _load_artifacts(self):
        try:
            logger.info("Loading model artifacts...")
            self.model = joblib.load(FINAL_MODEL_PATH)
            self.preprocessor = joblib.load(PREPROCESSOR_PATH)
            
            with open(SCHEMA_PATH, "r") as f:
                self.schema = json.load(f)
                
            self.feature_ordering = self.schema["feature_ordering"]
            logger.info("Model artifacts loaded successfully.")
        except FileNotFoundError as e:
            logger.error(f"Missing model artifact: {e}")
            raise RuntimeError(f"Application cannot start. Missing artifact: {e}")
        except Exception as e:
            logger.error(f"Error loading model artifacts: {e}")
            raise RuntimeError(f"Application cannot start due to artifact error: {e}")

    def get_model(self):
        return self.model
        
    def get_preprocessor(self):
        return self.preprocessor
        
    def get_schema(self):
        return self.schema
        
    def get_feature_ordering(self):
        return self.feature_ordering
