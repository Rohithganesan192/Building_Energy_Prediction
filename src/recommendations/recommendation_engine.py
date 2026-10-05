"""
recommendation_engine.py
========================
Generates evidence-based operational recommendations by combining SHAP 
attributions with domain rules. Safely fails if data is missing or malformed.
"""
from typing import Dict, List, Any
from src.recommendations.recommendation_rules import RULES

class RecommendationEngine:
    def __init__(self, shap_threshold: float = 1.0):
        """
        Initializes the engine.
        :param shap_threshold: Minimum positive SHAP value to trigger a recommendation.
        """
        self.rules = RULES
        self.shap_threshold = shap_threshold
        
    def generate_recommendations(self, 
                                 predicted_energy: float, 
                                 shap_contributions: Dict[str, float], 
                                 feature_values: Dict[str, Any] = None,
                                 baseline_energy: float = None) -> List[Dict]:
        """
        Generates structured recommendations based on input prediction and SHAP values.
        
        :param predicted_energy: The model's raw predicted energy value.
        :param shap_contributions: Dictionary of feature names to their SHAP values.
        :param feature_values: Optional dictionary of actual feature values.
        :param baseline_energy: Optional reference baseline energy.
        :return: A list of structured recommendation dictionaries.
        """
        recommendations = []
        
        if not shap_contributions or not isinstance(shap_contributions, dict):
            return recommendations
            
        # Filter for positive contributors that exceed the threshold
        actionable_drivers = {
            feat: val for feat, val in shap_contributions.items() 
            if val > self.shap_threshold
        }
        
        if not actionable_drivers:
            return recommendations
            
        # Evaluate rules against top drivers
        for rule in self.rules:
            matched_features = [f for f in rule["primary_feature_triggers"] if f in actionable_drivers]
            if matched_features:
                # Find the strongest triggering feature for context
                top_driver = max(matched_features, key=lambda k: actionable_drivers[k])
                
                priority = "High" if rule["confidence_level"] == "High" else "Medium"
                
                rec = {
                    "priority": priority,
                    "driver": top_driver,
                    "observed_condition": rule["condition"],
                    "recommendation": rule["recommendation"],
                    "reason": rule["reason"],
                    "evidence_type": rule["evidence_type"],
                    "confidence": rule["confidence_level"],
                    "limitation": rule["limitation"]
                }
                recommendations.append(rec)
                
        # Deduplicate and sort by priority if necessary
        return recommendations

def format_recommendations(predicted_energy: float, recommendations: List[Dict]) -> str:
    """Helper to format recommendations into human-readable text."""
    output = f"Predicted energy consumption:\n{predicted_energy:.2f}\n\n"
    
    if not recommendations:
        output += "No specific actionable recommendations generated.\n"
        return output
        
    output += "Energy-efficiency observations:\n"
    for r in recommendations:
        output += f"- {r['recommendation']}\n"
        
    output += "\nImportant limitation:\n"
    output += "These recommendations are decision-support suggestions based on model attribution and domain rules; they do not establish causal relationships or guarantee a specific energy reduction.\n"
    
    return output
