from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import os
import json
import pathlib

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.schemas.api_models import PredictionRequest as InternalPredictionRequest
from app.services.prediction_service import PredictionService
from app.services.model_service import ModelService
from app.services.shap_service import ShapService
from app.services.recommendation_service import RecommendationService
from app.services.aggregation_service import AggregationService

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

_buildings_cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload model artifacts on startup to avoid cold starts
    ModelService()
    PredictionService()
    yield

app = FastAPI(title="Building Energy Intelligence API", lifespan=lifespan)

# Restrict CORS to local Vite development ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class APIPredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(..., description="Dictionary of features matching the exact schema requirements.")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/model-info")
def model_info():
    model_svc = ModelService()
    return {
        "model_name": "Random Forest",
        "feature_group": "Group B",
        "target": "meter_reading (raw)",
        "xai_method": "SHAP (TreeExplainer)",
        "status": "ready",
        "expected_features": model_svc.get_feature_ordering(),
        "categorical_features": model_svc.get_schema().get("categorical_features", []),
        "numerical_features": model_svc.get_schema().get("numerical_features", [])
    }

@app.post("/api/predict")
def predict(req: APIPredictionRequest):
    pred_service = PredictionService()
    internal_req = InternalPredictionRequest(features=req.features)
    
    response, shap_processed = pred_service.predict(internal_req)
    return response

@app.post("/api/explain")
def explain(req: APIPredictionRequest):
    pred_service = PredictionService()
    internal_req = InternalPredictionRequest(features=req.features)
    
    pred_resp, X_processed = pred_service.predict(internal_req)
    if pred_resp.status != "success":
        return {"prediction": pred_resp, "explanation": None}
        
    shap_service = ShapService()
    expl_resp, feature_contributions = shap_service.explain_prediction(X_processed)
    
    return {"prediction": pred_resp, "explanation": expl_resp, "contributions": feature_contributions}

@app.get("/api/energy-drivers")
def energy_drivers():
    shap_service = ShapService()
    return {
        "global_importance": shap_service.global_importance,
        "groups": [
            {"name": "Historical", "pct": 95.14},
            {"name": "Temporal", "pct": 2.31},
            {"name": "Weather", "pct": 1.22},
            {"name": "Building", "pct": 0.84},
            {"name": "Meter", "pct": 0.46}
        ]
    }

@app.post("/api/recommendations")
def recommendations(req: APIPredictionRequest):
    agg_service = AggregationService()
    internal_req = InternalPredictionRequest(features=req.features)
    result = agg_service.process_request(internal_req)
    return result

@app.get("/api/buildings")
def get_buildings():
    global _buildings_cache
    if _buildings_cache is None:
        csv_path = os.path.join(DATA_DIR, "raw", "building_metadata.csv")
        if os.path.exists(csv_path):
            import numpy as np
            df = pd.read_csv(csv_path).replace({np.nan: None})
            _buildings_cache = df.to_dict(orient="records")
        else:
            _buildings_cache = []
    return {"buildings": _buildings_cache}

@app.get("/api/reports")
def get_reports():
    return {
        "Experimental Results": [
            {"title": "10% Comparison Report", "file": "10pct_comparison_report.md", "type": "markdown", "desc": "Detailed comparison of 6 models on 10% sample."},
            {"title": "Final Model Selection Report", "file": "final_model_selection_report.md", "type": "markdown", "desc": "Rationale and metrics for selecting Random Forest."},
            {"title": "Final Holdout Evaluation Report", "file": "final_holdout_evaluation_report.md", "type": "markdown", "desc": "Performance on the December 2016 protected holdout."},
            {"title": "SHAP Analysis Report", "file": "shap_analysis_report.md", "type": "markdown", "desc": "Global and local XAI insights."}
        ],
        "Data / Validation": [
            {"title": "Raw Data Profile", "file": "raw_data_profile.md", "type": "markdown", "desc": "Initial profiling of ASHRAE dataset."},
            {"title": "Data Validation Report", "file": "data_validation_report.md", "type": "markdown", "desc": "Data consistency and anomaly checks."},
            {"title": "Data Cleaning Decisions", "file": "data_cleaning_decisions.md", "type": "markdown", "desc": "Imputation and outlier handling rules."},
            {"title": "Feature Engineering Design", "file": "feature_engineering_design.md", "type": "markdown", "desc": "Lag and rolling feature calculations."}
        ],
        "Application / Architecture": [
            {"title": "Application Architecture", "file": "APPLICATION_ARCHITECTURE.md", "type": "markdown", "desc": "System design and backend APIs."},
            {"title": "Recommendation Engine", "file": "RECOMMENDATION_ENGINE.md", "type": "markdown", "desc": "Decision-support mapping rules."},
            {"title": "XAI Method", "file": "XAI_METHOD.md", "type": "markdown", "desc": "Implementation of SHAP TreeExplainer."}
        ],
        "Tables": [
            {"title": "Comparison 10pct Results", "file": "comparison_10pct_results.csv", "type": "csv", "desc": "Raw results from 10% deterministic sample."},
            {"title": "Tuning Results", "file": "tuning_results.csv", "type": "csv", "desc": "Hyperparameter optimization output."},
            {"title": "Final Holdout Results", "file": "final_holdout_results.csv", "type": "csv", "desc": "Metrics on protected December holdout."},
            {"title": "SHAP Global Importance", "file": "shap_global_importance.csv", "type": "csv", "desc": "Feature importance aggregated across holdout."},
            {"title": "SHAP Group Importance", "file": "shap_group_importance.csv", "type": "csv", "desc": "Grouped feature importance."},
            {"title": "Energy Driver Analysis", "file": "energy_driver_analysis.csv", "type": "csv", "desc": "Detailed temporal and weather feature attribution."}
        ]
    }

@app.get("/api/report-content")
def get_report_content(file: str):
    base_dir = pathlib.Path(__file__).parent.parent
    possible_paths = [
        base_dir / "reports" / file,
        base_dir / "reports" / "tables" / file,
        base_dir / "docs" / file,
        base_dir / file
    ]
    
    for p in possible_paths:
        if p.exists() and p.is_file():
            return FileResponse(path=p, filename=file)
    
    raise HTTPException(status_code=404, detail="File not found")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(req: LoginRequest):
    # Ensure credentials are required and not hardcoded if missing in env
    valid_username = os.environ.get("APP_ADMIN_USERNAME")
    valid_password = os.environ.get("APP_ADMIN_PASSWORD")
    
    if not valid_username or not valid_password:
        raise HTTPException(status_code=500, detail="Server missing admin credentials configuration.")
        
    if req.username == valid_username and req.password == valid_password:
        return {"token": "demo-admin-token-xyz"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# SPA Routing: Serve static files from app/ui/dist
UI_DIST = os.path.join(os.path.dirname(__file__), "ui", "dist")

if os.path.isdir(UI_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(UI_DIST, "assets")), name="assets")

    @app.exception_handler(404)
    async def not_found_spa_handler(request: Request, exc: HTTPException):
        # Allow API calls to fail normally
        if request.url.path.startswith(("/api/", "/docs", "/openapi.json")):
            return HTMLResponse(content="Not Found", status_code=404)
        
        index_file = os.path.join(UI_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return HTMLResponse(content="Frontend build not found.", status_code=404)
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith(("api/", "docs", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not Found")
            
        file_path = os.path.join(UI_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        index_file = os.path.join(UI_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return HTMLResponse(content="Frontend build not found.", status_code=404)



