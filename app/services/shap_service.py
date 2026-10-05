import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
from app.services.model_service import ModelService
from app.schemas.api_models import ExplanationResponse, DriverResponse
from app.config.settings import GLOBAL_SHAP_PATH
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ShapService:
    def __init__(self):
        self.model_svc = ModelService()
        self.explainer = None
        
        # Load global explanations once
        self.global_importance = []
        try:
            if GLOBAL_SHAP_PATH.exists():
                df = pd.read_csv(GLOBAL_SHAP_PATH)
                # Keep top 5 features for global
                self.global_importance = df.head(5).to_dict(orient="records")
        except Exception as e:
            logger.warning(f"Could not load global SHAP artifacts: {e}")

    def _get_explainer(self):
        if self.explainer is None:
            import shap
            model = self.model_svc.get_model()
            self.explainer = shap.TreeExplainer(model)
        return self.explainer

    def _get_input_features(self):
        preprocessor = self.model_svc.get_preprocessor()
        schema = self.model_svc.get_schema()
        try:
            return preprocessor.feature_names_out_
        except AttributeError:
            return schema.get("numerical_features", []) + schema.get("categorical_features", [])

    def explain_prediction(self, X_processed: Any) -> Tuple[ExplanationResponse, Dict[str, float]]:
        """
        Calculates local SHAP values for a single processed observation.
        Returns the ExplanationResponse schema and a raw dict of feature -> shap_value.
        """
        try:
            explainer = self._get_explainer()
            
            # Ensure it's a 2D array for SHAP
            if len(X_processed.shape) == 1:
                X_processed = X_processed.reshape(1, -1)
                
            input_features = self._get_input_features()
            X_df = pd.DataFrame(X_processed, columns=input_features)
            
            shap_values = explainer.shap_values(X_df)
            
            # Since it's a single prediction, take the first row
            sv = shap_values[0, :]
            
            # Map features to their SHAP values
            feature_contributions = {feat: float(val) for feat, val in zip(input_features, sv)}
            
            # Sort into positive and negative contributors
            pos_contrib = [{"feature": k, "value": v} for k, v in feature_contributions.items() if v > 0]
            neg_contrib = [{"feature": k, "value": v} for k, v in feature_contributions.items() if v < 0]
            
            pos_contrib.sort(key=lambda x: x["value"], reverse=True)
            neg_contrib.sort(key=lambda x: x["value"]) # Sort ascending (most negative first)
            
            resp = ExplanationResponse(
                top_features=self.global_importance,
                positive_contributors=pos_contrib[:5],
                negative_contributors=neg_contrib[:5]
            )
            
            logger.info("SHAP explanation generated.")
            return resp, feature_contributions
            
        except Exception as e:
            logger.error(f"SHAP explanation error: {e}")
            return ExplanationResponse(), {}

    def get_drivers(self, feature_contributions: Dict[str, float]) -> DriverResponse:
        """Categorizes features based on SHAP contributions."""
        historical = ["lag_1", "lag_24", "lag_168", "rolling_mean_24", "rolling_mean_168", "rolling_std_24", "rolling_std_168"]
        temporal = ["hour", "day_of_week", "month", "day_of_year", "is_weekend", "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos", "month_sin", "month_cos"]
        weather = ["air_temperature", "cloud_coverage", "dew_temperature", "precip_depth_1_hr", "sea_level_pressure", "wind_direction", "wind_speed"]
        building = ["site_id", "primary_use", "square_feet", "year_built", "floor_count"]
        meter = ["meter"]
        
        # Helper to sort and filter categorized features by absolute SHAP magnitude > 0.1
        def filter_sort(feat_list):
            valid = [(f, feature_contributions.get(f, 0.0)) for f in feat_list if f in feature_contributions and abs(feature_contributions[f]) > 0.1]
            valid.sort(key=lambda x: abs(x[1]), reverse=True)
            return [x[0] for x in valid]

        return DriverResponse(
            historical=filter_sort(historical),
            temporal=filter_sort(temporal),
            weather=filter_sort(weather),
            building=filter_sort(building),
            meter=filter_sort(meter)
        )
