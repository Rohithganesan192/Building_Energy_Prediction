from typing import Dict, List, Any
from src.recommendations.recommendation_engine import RecommendationEngine
from app.utils.logger import get_logger
from app.config.settings import SHAP_RECOMMENDATION_THRESHOLD

logger = get_logger(__name__)

class RecommendationService:
    def __init__(self):
        # Initializing the validated Phase 10 recommendation engine
        self.engine = RecommendationEngine(shap_threshold=SHAP_RECOMMENDATION_THRESHOLD)
        
    def get_recommendations(self, 
                            predicted_energy: float, 
                            feature_contributions: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Receives prediction and SHAP contributions, and returns structural recommendations.
        """
        try:
            recs = self.engine.generate_recommendations(
                predicted_energy=predicted_energy,
                shap_contributions=feature_contributions
            )
            logger.info(f"Generated {len(recs)} recommendations.")
            return recs
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            return []
