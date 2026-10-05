"""
test_recommendation_integration.py
==================================
Integration tests verifying the recommendation engine works with actual Phase 9 SHAP outputs.
"""
import unittest
import pandas as pd
from pathlib import Path
from src.recommendations.recommendation_engine import RecommendationEngine
from src.models.experiment_config import PROJECT_ROOT

class TestRecommendationIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RecommendationEngine(shap_threshold=1.0)
        cls.local_shap_path = PROJECT_ROOT / "reports" / "tables" / "shap_local_explanations.csv"
        cls.global_shap_path = PROJECT_ROOT / "reports" / "tables" / "shap_global_importance.csv"
        
        # We need these files to exist for integration tests to proceed
        if not cls.local_shap_path.exists() or not cls.global_shap_path.exists():
            raise FileNotFoundError("Phase 9 SHAP CSV outputs not found.")
            
        cls.local_df = pd.read_csv(cls.local_shap_path)
        cls.global_df = pd.read_csv(cls.global_shap_path)

    def _parse_shap_string(self, shap_str: str) -> dict:
        """Helper to parse 'feature_name (+value) | feature_name2 (+value2)' back to a dict"""
        shap_dict = {}
        if not isinstance(shap_str, str):
            return shap_dict
            
        parts = shap_str.split(" | ")
        for part in parts:
            if " (" in part and ")" in part:
                feat, val_str = part.rsplit(" (", 1)
                val_str = val_str.replace(")", "").replace("+", "")
                try:
                    shap_dict[feat.strip()] = float(val_str)
                except ValueError:
                    pass
        return shap_dict

    def test_actual_local_explanation_integration(self):
        """Test integrating a real local explanation into the engine."""
        # Find observation 1 which has strong positive lag_1 (+855.39) based on Phase 9 output
        obs = self.local_df.iloc[1]
        predicted_energy = float(obs["predicted_value"])
        pos_str = obs["top_positive_features"]
        
        shap_dict = self._parse_shap_string(pos_str)
        
        recs = self.engine.generate_recommendations(predicted_energy, shap_dict)
        
        # Verify the historical engine handles lag_1 properly
        self.assertTrue(len(recs) > 0)
        drivers = [r["driver"] for r in recs]
        self.assertIn("lag_1", drivers)
        
        # Verify non-causality string is preserved
        historical_rec = next(r for r in recs if r["driver"] == "lag_1")
        self.assertEqual(historical_rec["evidence_type"], "Observational State / Autoregressive")
        self.assertIn("Recent energy consumption remains elevated", historical_rec["recommendation"])

    def test_actual_temporal_driver_integration(self):
        """Test integrating a real local explanation that triggers temporal rules."""
        # Find observation 0 which has hour_cos (+3.85) based on Phase 9 output
        obs = self.local_df.iloc[0]
        predicted_energy = float(obs["predicted_value"])
        pos_str = obs["top_positive_features"]
        
        shap_dict = self._parse_shap_string(pos_str)
        
        recs = self.engine.generate_recommendations(predicted_energy, shap_dict)
        
        # hour_cos is > threshold (1.0), should trigger temporal rule
        self.assertTrue(len(recs) > 0)
        drivers = [r["driver"] for r in recs]
        self.assertIn("hour_cos", drivers)
        
        temporal_rec = next(r for r in recs if r["driver"] == "hour_cos")
        self.assertIn("time-of-day", temporal_rec["observed_condition"])
        self.assertEqual(temporal_rec["limitation"], "Time cannot be controlled. This highlights potential scheduling misalignments, not mechanical faults.")

    def test_global_historical_safe_handling(self):
        """Verify the global importance table highlights drivers correctly without causal mapping."""
        # Get top global driver
        top_driver = self.global_df.iloc[0]["feature"]
        mean_abs = self.global_df.iloc[0]["mean_abs_shap"]
        
        # Pass a mock dict representing the top global driver
        recs = self.engine.generate_recommendations(100.0, {top_driver: mean_abs})
        
        if top_driver in ["lag_1", "lag_24", "rolling_mean_24"]:
            rec = recs[0]
            self.assertEqual(rec["evidence_type"], "Observational State / Autoregressive")
            self.assertIn("investigation rather than an exact causal intervention", rec["limitation"])
            self.assertNotIn("cause", rec["recommendation"].lower())

    def test_unsupported_no_actionable_case(self):
        """Verify engine safely handles features with no mapped rules (e.g., meter identity)."""
        # Meter is often highly ranked but non-actionable
        recs = self.engine.generate_recommendations(100.0, {"meter": 2.12})
        self.assertEqual(len(recs), 0) # No rule should trigger just for 'meter'

    def test_output_schema_validation(self):
        """Verify the generated schema strictly adheres to the requested format."""
        obs = self.local_df.iloc[1]
        shap_dict = self._parse_shap_string(obs["top_positive_features"])
        recs = self.engine.generate_recommendations(float(obs["predicted_value"]), shap_dict)
        
        expected_keys = {
            "priority", "driver", "observed_condition", "recommendation", 
            "reason", "evidence_type", "confidence", "limitation"
        }
        
        for r in recs:
            self.assertEqual(set(r.keys()), expected_keys)
            self.assertNotIn("savings", str(r).lower()) # Ensure no fabricated percentages

if __name__ == "__main__":
    unittest.main()
