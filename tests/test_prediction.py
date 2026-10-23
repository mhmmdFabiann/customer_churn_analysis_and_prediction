"""
Unit & Integration tests for Machine Learning Pipeline and API (Science Track).
Covers domain feature engineering, model inference, input validation, and REST API.
"""

import pytest
import pandas as pd
from fastapi.testclient import TestClient

from src.telco_churn.prediction.pipelines import DomainFeatureEngineer, build_preprocessor
from src.telco_churn.prediction.inference import get_predictor, categorize_risk
from deliverables.prediction.api.app import app

client = TestClient(app)


def test_domain_feature_engineer():
    df = pd.DataFrame([{
        "contract": "Month-to-month",
        "payment_method": "Electronic check",
        "internet_service": "Fiber optic",
        "tech_support": "No",
        "tenure": 10,
        "monthly_charges": 80.0,
        "total_charges": 800.0
    }])

    engineer = DomainFeatureEngineer()
    df_trans = engineer.transform(df)

    assert df_trans["is_month_to_month"].iloc[0] == 1
    assert df_trans["is_electronic_check"].iloc[0] == 1
    assert df_trans["fiber_no_tech_support"].iloc[0] == 1
    assert "monthly_to_total_ratio" in df_trans.columns
    assert df_trans["monthly_to_total_ratio"].iloc[0] == pytest.approx(0.1, 0.01)


def test_risk_categorization():
    assert categorize_risk(0.85) == "High"
    assert categorize_risk(0.45) == "Medium"
    assert categorize_risk(0.15) == "Low"


def test_predictor_loads():
    predictor = get_predictor()
    assert predictor.pipeline is not None


def test_predict_single_output():
    predictor = get_predictor()
    customer = {
        "gender": "Female",
        "senior_citizen": 0,
        "partner": "Yes",
        "dependents": "No",
        "tenure": 2,
        "phone_service": "Yes",
        "multiple_lines": "No",
        "internet_service": "Fiber optic",
        "online_security": "No",
        "online_backup": "No",
        "device_protection": "No",
        "tech_support": "No",
        "streaming_tv": "Yes",
        "streaming_movies": "Yes",
        "contract": "Month-to-month",
        "paperless_billing": "Yes",
        "payment_method": "Electronic check",
        "monthly_charges": 89.5,
        "total_charges": 179.0
    }

    res = predictor.predict_one(customer)
    assert res["churn_prediction"] in ["Yes", "No"]
    assert 0.0 <= res["churn_probability"] <= 1.0
    assert res["risk_level"] in ["Low", "Medium", "High"]
    assert len(res["recommendation"]) > 0


def test_api_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_api_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_predict_endpoint_valid():
    payload = {
        "customer_id": "TEST-1001",
        "gender": "Male",
        "senior_citizen": 0,
        "partner": "No",
        "dependents": "No",
        "tenure": 10,
        "phone_service": "Yes",
        "multiple_lines": "No",
        "internet_service": "DSL",
        "online_security": "Yes",
        "online_backup": "No",
        "device_protection": "Yes",
        "tech_support": "Yes",
        "streaming_tv": "No",
        "streaming_movies": "No",
        "contract": "One year",
        "paperless_billing": "No",
        "payment_method": "Credit card (automatic)",
        "monthly_charges": 55.0,
        "total_charges": 550.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "TEST-1001"
    assert "churn_probability" in data
    assert data["churn_prediction"] in ["Yes", "No"]
    assert data["risk_level"] in ["Low", "Medium", "High"]


def test_api_predict_endpoint_invalid_payload():
    # Missing required fields like monthly_charges and contract
    invalid_payload = {
        "customer_id": "TEST-CORRUPT",
        "gender": "Male"
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422  # Validation error from pydantic
