"""
FastAPI REST API Service for Telco Churn Prediction.
Deliverables / Production API Entrypoint.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.telco_churn.prediction.inference import get_predictor

app = FastAPI(
    title="Telco Customer Churn Prediction Service",
    description="Full-Cycle ML Service providing real-time churn probability scoring and retention recommendations.",
    version="1.0.0"
)


class CustomerFeatures(BaseModel):
    customer_id: Optional[str] = Field(default="CUST_DEMO", description="Unique Customer Identifier")
    gender: str = Field(..., description="Customer gender ('Male' or 'Female')")
    senior_citizen: int = Field(..., ge=0, le=1, description="1 if senior citizen, 0 otherwise")
    partner: str = Field(..., description="'Yes' or 'No'")
    dependents: str = Field(..., description="'Yes' or 'No'")
    tenure: int = Field(..., ge=0, le=120, description="Months customer has stayed with company")
    phone_service: str = Field(..., description="'Yes' or 'No'")
    multiple_lines: str = Field(..., description="'Yes', 'No', or 'No phone service'")
    internet_service: str = Field(..., description="'DSL', 'Fiber optic', or 'No'")
    online_security: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    online_backup: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    device_protection: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    tech_support: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    streaming_tv: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    streaming_movies: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    contract: str = Field(..., description="'Month-to-month', 'One year', or 'Two year'")
    paperless_billing: str = Field(..., description="'Yes' or 'No'")
    payment_method: str = Field(..., description="'Electronic check', 'Mailed check', 'Bank transfer (automatic)', or 'Credit card (automatic)'")
    monthly_charges: float = Field(..., ge=0.0, description="Monthly charges in USD")
    total_charges: float = Field(..., ge=0.0, description="Cumulative charges in USD")

    model_config = {
        "json_schema_extra": {
            "example": {
                "customer_id": "7590-VHVEG",
                "gender": "Female",
                "senior_citizen": 0,
                "partner": "Yes",
                "dependents": "No",
                "tenure": 1,
                "phone_service": "No",
                "multiple_lines": "No phone service",
                "internet_service": "DSL",
                "online_security": "No",
                "online_backup": "Yes",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "No",
                "streaming_movies": "No",
                "contract": "Month-to-month",
                "paperless_billing": "Yes",
                "payment_method": "Electronic check",
                "monthly_charges": 29.85,
                "total_charges": 29.85
            }
        }
    }


class PredictionResponse(BaseModel):
    customer_id: str
    churn_prediction: str
    churn_probability: float
    risk_level: str
    recommendation: str
    timestamp: str


@app.get("/", tags=["Info"])
def root():
    return {
        "service": "Telco Customer Churn Prediction API",
        "track": "Science (Full-Cycle Project)",
        "model": "XGBoost Classifier (Tuned)",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/health", tags=["Health"])
def health_check():
    try:
        predictor = get_predictor()
        return {
            "status": "healthy",
            "model_loaded": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model unavailable: {str(e)}"
        )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_single(customer: CustomerFeatures):
    try:
        predictor = get_predictor()
        input_dict = customer.model_dump()
        cust_id = input_dict.pop("customer_id", "UNKNOWN")
        res = predictor.predict_one(input_dict)
        return {
            "customer_id": cust_id,
            "churn_prediction": res["churn_prediction"],
            "churn_probability": res["churn_probability"],
            "risk_level": res["risk_level"],
            "recommendation": res["recommendation"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict/batch", response_model=List[PredictionResponse], tags=["Prediction"])
def predict_batch_endpoint(customers: List[CustomerFeatures]):
    try:
        predictor = get_predictor()
        input_list = [c.model_dump() for c in customers]
        batch_results = predictor.predict_batch(input_list)
        ts = datetime.now().isoformat()
        return [
            {
                "customer_id": r["customer_id"],
                "churn_prediction": r["churn_prediction"],
                "churn_probability": r["churn_probability"],
                "risk_level": r["risk_level"],
                "recommendation": r["recommendation"],
                "timestamp": ts
            }
            for r in batch_results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction error: {str(e)}"
        )
