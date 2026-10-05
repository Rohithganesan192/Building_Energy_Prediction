from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class PredictionRequest:
    features: Dict[str, Any]

@dataclass
class PredictionResponse:
    status: str
    predicted_energy: Optional[float] = None
    unit: str = "kWh (or equivalent meter reading unit)"
    model_name: str = "RandomForestRegressor"
    feature_group: str = "Group B (Historical)"
    warnings: List[str] = field(default_factory=list)

@dataclass
class ExplanationResponse:
    top_features: List[Dict[str, Any]] = field(default_factory=list)
    positive_contributors: List[Dict[str, Any]] = field(default_factory=list)
    negative_contributors: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DriverResponse:
    historical: List[str] = field(default_factory=list)
    temporal: List[str] = field(default_factory=list)
    weather: List[str] = field(default_factory=list)
    building: List[str] = field(default_factory=list)
    meter: List[str] = field(default_factory=list)

@dataclass
class ApplicationResult:
    status: str
    prediction: Optional[PredictionResponse] = None
    explanation: Optional[ExplanationResponse] = None
    drivers: Optional[DriverResponse] = None
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
