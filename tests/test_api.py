import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.model_service import ModelService

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_model_info():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "Random Forest"
    assert data["feature_group"] == "Group B"
    assert "expected_features" in data
    assert isinstance(data["expected_features"], list)
    assert "lag_1" in data["expected_features"]

def test_predict_malformed_json():
    # Sending missing 'features' key
    response = client.post("/api/predict", json={"wrong_key": {}})
    assert response.status_code == 422 # Pydantic validation error

def test_predict_missing_historical_features():
    # Valid model features expect lags and rolling features.
    # We will provide an empty feature dict to see if it triggers insufficient_history
    req_data = {"features": {}}
    response = client.post("/api/predict", json=req_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "insufficient_history"
    assert "warnings" in data

def test_predict_success(monkeypatch):
    # To test success without needing a real prediction run that might be slow or require exact types,
    # we can mock the prediction service or provide a fully valid feature dict.
    # Since we just want to ensure it calls the service and returns properly:
    from app.services.prediction_service import PredictionService
    from app.schemas.api_models import PredictionResponse

    def mock_predict(self, req):
        return PredictionResponse(status="success", predicted_energy=123.4), None

    monkeypatch.setattr(PredictionService, "predict", mock_predict)

    # We provide a valid schema request
    req_data = {"features": {"dummy": "data"}}
    response = client.post("/api/predict", json=req_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_energy"] == 123.4
