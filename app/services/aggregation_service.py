from app.schemas.api_models import PredictionRequest, ApplicationResult
from app.services.prediction_service import PredictionService
from app.services.shap_service import ShapService
from app.services.recommendation_service import RecommendationService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AggregationService:
    def __init__(self):
        self.pred_svc = PredictionService()
        self.shap_svc = ShapService()
        self.rec_svc = RecommendationService()
        
    def process_request(self, req: PredictionRequest) -> ApplicationResult:
        """
        Orchestrates the full pipeline: Validation -> Prediction -> Explanation -> Recommendations.
        """
        logger.info("Processing new application request...")
        
        # 1. Prediction (Includes Input Validation & Feature Prep)
        pred_resp, X_processed = self.pred_svc.predict(req)
        
        if pred_resp.status != "success":
            return ApplicationResult(
                status=pred_resp.status,
                warnings=pred_resp.warnings
            )
            
        # 2. Explanation (SHAP)
        expl_resp, feature_contributions = self.shap_svc.explain_prediction(X_processed)
        
        # 3. Energy Drivers
        driver_resp = self.shap_svc.get_drivers(feature_contributions)
        
        # 4. Recommendations
        recs = self.rec_svc.get_recommendations(
            predicted_energy=pred_resp.predicted_energy,
            feature_contributions=feature_contributions
        )
        
        # 5. Assemble Result
        limitations = [
            "SHAP explains model attribution; it does not establish causal relationships.",
            "Recommendations are decision-support suggestions based on model attribution and domain rules; they do not guarantee a specific energy reduction."
        ]
        
        logger.info("Application request processed successfully.")
        return ApplicationResult(
            status="success",
            prediction=pred_resp,
            explanation=expl_resp,
            drivers=driver_resp,
            recommendations=recs,
            warnings=[],
            limitations=limitations
        )
