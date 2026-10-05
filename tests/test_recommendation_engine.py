"""
test_recommendation_engine.py
=============================
Tests for the recommendation engine logic.
"""
import unittest
from src.recommendations.recommendation_engine import RecommendationEngine, format_recommendations

class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        # Use a low threshold for easy testing
        self.engine = RecommendationEngine(shap_threshold=1.0)
        
    def test_valid_shap_input(self):
        shap_vals = {"hour_cos": 4.5, "lag_1": -5.0}
        recs = self.engine.generate_recommendations(100.0, shap_vals)
        self.assertTrue(len(recs) > 0)
        self.assertEqual(recs[0]["driver"], "hour_cos")
        
    def test_missing_shap_input(self):
        recs = self.engine.generate_recommendations(100.0, None)
        self.assertEqual(len(recs), 0)
        
        recs2 = self.engine.generate_recommendations(100.0, {})
        self.assertEqual(len(recs2), 0)
        
    def test_no_actionable_driver(self):
        # Drivers exist, but don't meet positive threshold
        shap_vals = {"lag_1": 0.5, "hour_cos": -2.0}
        recs = self.engine.generate_recommendations(100.0, shap_vals)
        self.assertEqual(len(recs), 0)
        
    def test_high_historical_consumption_state(self):
        shap_vals = {"lag_1": 300.0, "rolling_mean_24": 50.0}
        recs = self.engine.generate_recommendations(1500.0, shap_vals)
        self.assertTrue(any(r["driver"] in ["lag_1", "rolling_mean_24"] for r in recs))
        self.assertTrue(any("Recent energy consumption remains elevated" in r["recommendation"] for r in recs))
        
    def test_temporal_pattern(self):
        shap_vals = {"day_of_week": 2.5}
        recs = self.engine.generate_recommendations(200.0, shap_vals)
        self.assertTrue(any("weekly recurring pattern" in r["recommendation"] for r in recs))
        
    def test_multiple_simultaneous_drivers(self):
        shap_vals = {"lag_1": 150.0, "air_temperature": 5.0}
        recs = self.engine.generate_recommendations(1000.0, shap_vals)
        drivers = [r["driver"] for r in recs]
        self.assertIn("lag_1", drivers)
        self.assertIn("air_temperature", drivers)
        self.assertTrue(len(recs) >= 2)
        
    def test_empty_recommendation_result(self):
        shap_vals = {"unknown_feature_xyz": 10.0}
        recs = self.engine.generate_recommendations(100.0, shap_vals)
        self.assertEqual(len(recs), 0)
        
    def test_malformed_feature_input(self):
        recs = self.engine.generate_recommendations(100.0, ["list", "instead", "of", "dict"])
        self.assertEqual(len(recs), 0)
        
    def test_formatting(self):
        shap_vals = {"lag_1": 150.0}
        recs = self.engine.generate_recommendations(500.0, shap_vals)
        formatted = format_recommendations(500.0, recs)
        self.assertIn("Predicted energy consumption:", formatted)
        self.assertIn("Recent energy consumption remains elevated", formatted)
        self.assertIn("These recommendations are decision-support suggestions", formatted)

if __name__ == "__main__":
    unittest.main()
