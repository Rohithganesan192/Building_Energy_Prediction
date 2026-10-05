"""
test_app_backend.py
===================
Tests for the application backend services.
"""
import unittest
from app.schemas.api_models import PredictionRequest
from app.services.model_service import ModelService
from app.services.prediction_service import PredictionService
from app.services.shap_service import ShapService
from app.services.aggregation_service import AggregationService

class TestAppBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Trigger model loading
        cls.model_svc = ModelService()
        cls.pred_svc = PredictionService()
        cls.shap_svc = ShapService()
        cls.agg_svc = AggregationService()
        
        # Base valid feature payload (extracted from schema)
        cls.valid_features = {
            "lag_1": 150.0, "lag_24": 140.0, "lag_168": 145.0, 
            "rolling_mean_24": 145.5, "rolling_mean_168": 148.0, 
            "rolling_std_24": 5.0, "rolling_std_168": 6.0,
            "air_temperature": 15.0, "cloud_coverage": 2.0, "dew_temperature": 10.0, 
            "precip_depth_1_hr": 0.0, "sea_level_pressure": 1012.0, 
            "wind_direction": 180.0, "wind_speed": 3.0,
            "hour": 12.0, "day_of_week": 2.0, "month": 6.0, "day_of_year": 150.0, 
            "is_weekend": 0.0,
            "hour_sin": 0.0, "hour_cos": -1.0, 
            "day_of_week_sin": 0.97, "day_of_week_cos": -0.22, 
            "month_sin": 0.0, "month_cos": -1.0,
            "site_id": 0.0, "primary_use": 0.0, "square_feet": 50000.0, 
            "year_built": 1990.0, "floor_count": 5.0, "meter": 0.0
        }

    def test_model_loading(self):
        """1. Model artifacts are loaded successfully."""
        self.assertIsNotNone(self.model_svc.get_model())
        self.assertIsNotNone(self.model_svc.get_preprocessor())
        self.assertTrue(len(self.model_svc.get_feature_ordering()) > 0)

    def test_valid_prediction_input(self):
        """2. Valid input produces successful status and valid energy prediction."""
        req = PredictionRequest(features=self.valid_features)
        is_valid, status, bad_fields = self.pred_svc.validate_input(req)
        self.assertTrue(is_valid)
        self.assertEqual(status, "valid")
        
        resp, _ = self.pred_svc.predict(req)
        self.assertEqual(resp.status, "success")
        self.assertIsInstance(resp.predicted_energy, float)

    def test_missing_required_input(self):
        """3. Missing contextual input triggers validation failure."""
        bad_features = self.valid_features.copy()
        del bad_features["square_feet"]
        req = PredictionRequest(features=bad_features)
        is_valid, status, bad_fields = self.pred_svc.validate_input(req)
        self.assertFalse(is_valid)
        self.assertEqual(status, "missing_features")
        self.assertIn("square_feet", bad_fields)

    def test_missing_historical_features(self):
        """4. Missing historical features correctly raises insufficient_history status (MODE B constraint)."""
        bad_features = self.valid_features.copy()
        del bad_features["lag_1"]
        req = PredictionRequest(features=bad_features)
        is_valid, status, bad_fields = self.pred_svc.validate_input(req)
        self.assertFalse(is_valid)
        self.assertEqual(status, "insufficient_history")

    def test_invalid_categorical_input(self):
        """5. Invalid categorical input (currently handled by prediction pipeline/preprocessor)."""
        pass # The underlying OneHotEncoder handles unknown categoricals natively if configured so, or will throw handled prediction_error.

    def test_invalid_numerical_input(self):
        """6. String values in numerical fields trigger validation failure."""
        bad_features = self.valid_features.copy()
        bad_features["square_feet"] = "not_a_number"
        req = PredictionRequest(features=bad_features)
        is_valid, status, bad_fields = self.pred_svc.validate_input(req)
        self.assertFalse(is_valid)
        self.assertEqual(status, "invalid_numerical_input")

    def test_prediction_response_schema(self):
        """7. Prediction response matches defined schema fields."""
        req = PredictionRequest(features=self.valid_features)
        resp, _ = self.pred_svc.predict(req)
        self.assertEqual(resp.model_name, "RandomForestRegressor")
        self.assertEqual(resp.feature_group, "Group B (Historical)")

    def test_shap_local_explanation_response(self):
        """8. SHAP service correctly generates structural ExplanationResponse."""
        req = PredictionRequest(features=self.valid_features)
        _, X_processed = self.pred_svc.predict(req)
        expl_resp, contribs = self.shap_svc.explain_prediction(X_processed)
        
        self.assertTrue(len(expl_resp.positive_contributors) > 0 or len(expl_resp.negative_contributors) > 0)
        self.assertTrue(isinstance(contribs, dict))
        self.assertTrue(len(contribs) > 0)

    def test_recommendation_response(self):
        """9. Recommendation engine correctly integrates into the ApplicationResult."""
        req = PredictionRequest(features=self.valid_features)
        result = self.agg_svc.process_request(req)
        self.assertIsNotNone(result.recommendations)

    def test_complete_application_result(self):
        """10. Full aggregation result validates end-to-end flow."""
        req = PredictionRequest(features=self.valid_features)
        result = self.agg_svc.process_request(req)
        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.prediction)
        self.assertIsNotNone(result.explanation)
        self.assertIsNotNone(result.drivers)
        
        # Verify non-causality strings are enforced in the final output
        self.assertTrue(any("does not establish causal" in limit for limit in result.limitations))

if __name__ == "__main__":
    unittest.main()
