import pandas as pd
from typing import Tuple, Dict, Any, List
from app.services.model_service import ModelService
from app.schemas.api_models import PredictionRequest, PredictionResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PredictionService:
    def __init__(self):
        self.model_svc = ModelService()
        self.expected_features = self.model_svc.get_feature_ordering()
        self.numerical_features = self.model_svc.get_schema().get("numerical_features", [])
        self.categorical_features = self.model_svc.get_schema().get("categorical_features", [])
        
    def validate_input(self, req: PredictionRequest) -> Tuple[bool, str, List[str]]:
        """
        Validates input structure.
        MODE A: Historical features available -> Success.
        MODE B: Missing -> Insufficient history.
        """
        features = req.features
        missing_features = [f for f in self.expected_features if f not in features]
        
        if missing_features:
            historical_missing = any("lag" in f or "rolling" in f for f in missing_features)
            if historical_missing:
                logger.warning("Input validation failed: insufficient_history")
                return False, "insufficient_history", missing_features
            else:
                logger.warning(f"Input validation failed: missing_features {missing_features}")
                return False, "missing_features", missing_features
                
        # Validate data types
        for num_feat in self.numerical_features:
            if num_feat in features:
                try:
                    float(features[num_feat])
                except (ValueError, TypeError):
                    return False, "invalid_numerical_input", [num_feat]
                    
        return True, "valid", []

    def prepare_features(self, req: PredictionRequest) -> pd.DataFrame:
        """Converts dict to DataFrame in the exact expected order."""
        # Convert dictionary to single-row dataframe
        df = pd.DataFrame([req.features])
        # Reorder to match model's expected feature ordering
        return df[self.expected_features]

    def predict(self, req: PredictionRequest) -> Tuple[PredictionResponse, Any]:
        """
        Validates, prepares, transforms, and predicts.
        Returns the response schema and the processed feature array (for SHAP).
        """
        is_valid, status_msg, bad_fields = self.validate_input(req)
        
        if not is_valid:
            return PredictionResponse(
                status=status_msg, 
                warnings=[f"Failed fields: {bad_fields}"]
            ), None
            
        try:
            # 1. Prepare raw dataframe
            X_raw = self.prepare_features(req)
            
            # 2. Transform using existing sklearn preprocessor
            preprocessor = self.model_svc.get_preprocessor()
            X_processed = preprocessor.transform(X_raw)
            
            # 3. Predict
            model = self.model_svc.get_model()
            prediction = model.predict(X_processed)[0]
            
            logger.info("Prediction successfully generated.")
            return PredictionResponse(
                status="success",
                predicted_energy=float(prediction)
            ), X_processed
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return PredictionResponse(
                status="prediction_error",
                warnings=[str(e)]
            ), None
