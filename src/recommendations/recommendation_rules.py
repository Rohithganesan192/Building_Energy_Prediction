"""
recommendation_rules.py
=======================
Structured rules for generating evidence-based operational recommendations.
Rules strictly observe the non-causal nature of SHAP attributions.
"""

# Define the master set of rules
RULES = [
    {
        "rule_id": "REC_HIST_01",
        "driver_type": "Historical",
        "primary_feature_triggers": ["rolling_mean_24", "lag_1", "lag_24"],
        "condition": "SHAP contribution for historical consumption is strongly positive, indicating elevated baseline demand.",
        "recommendation": "Recent energy consumption remains elevated relative to historical operating patterns. Review operating schedules and major controllable loads.",
        "reason": "The model detects a persistent high-consumption state continuing into the current prediction.",
        "evidence_type": "Observational State / Autoregressive",
        "confidence_level": "High",
        "limitation": "Historical features are observational proxies; this recommends investigation rather than an exact causal intervention."
    },
    {
        "rule_id": "REC_TEMP_01",
        "driver_type": "Temporal",
        "primary_feature_triggers": ["hour_cos", "hour_sin", "hour"],
        "condition": "SHAP contribution for time-of-day features is strongly positive during expected low-occupancy periods.",
        "recommendation": "A recurring time-of-day contribution is elevating demand. Review HVAC and lighting schedules to ensure they align with actual occupancy.",
        "reason": "The model expects higher consumption based strictly on the current hour of the day.",
        "evidence_type": "Temporal Pattern",
        "confidence_level": "Medium",
        "limitation": "Time cannot be controlled. This highlights potential scheduling misalignments, not mechanical faults."
    },
    {
        "rule_id": "REC_TEMP_02",
        "driver_type": "Temporal",
        "primary_feature_triggers": ["day_of_week", "day_of_week_cos", "day_of_week_sin", "is_weekend"],
        "condition": "SHAP contribution for day-of-week features is strongly positive, especially if it falls on a weekend.",
        "recommendation": "A weekly recurring pattern is elevating demand. Investigate unnecessary operation during non-working days or weekends.",
        "reason": "The model expects higher consumption based on the day of the week.",
        "evidence_type": "Weekly Schedule Pattern",
        "confidence_level": "Medium",
        "limitation": "Relies on standard operating assumptions which may not apply to specialized facilities."
    },
    {
        "rule_id": "REC_WTHR_01",
        "driver_type": "Weather",
        "primary_feature_triggers": ["dew_temperature", "air_temperature"],
        "condition": "SHAP contribution for external temperature/humidity is strongly positive.",
        "recommendation": "External thermal/humidity loads are actively driving up consumption. Review whether HVAC operating schedules and setpoints are appropriate for the prevailing weather conditions.",
        "reason": "The model has learned that the current weather state significantly increases demand.",
        "evidence_type": "Contextual External Load",
        "confidence_level": "Medium",
        "limitation": "Weather is uncontrollable. The recommendation suggests reviewing mechanical response strategies, not specific temperature setpoints."
    },
    {
        "rule_id": "REC_BLDG_01",
        "driver_type": "Building",
        "primary_feature_triggers": ["square_feet", "year_built"],
        "condition": "Building characteristics strongly drive the baseline predicted value.",
        "recommendation": "This building's physical characteristics heavily influence its high baseline footprint. Consider for long-term structural efficiency audits.",
        "reason": "Static metadata sets a high expected baseline relative to the portfolio.",
        "evidence_type": "Static Context",
        "confidence_level": "Low",
        "limitation": "Not addressable through daily operational changes; requires capital intervention."
    }
]

def get_rules_by_driver(driver_type: str) -> list:
    """Returns all rules matching a specific driver type."""
    return [r for r in RULES if r["driver_type"] == driver_type]
