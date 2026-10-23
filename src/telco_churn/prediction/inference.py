"""
Production inference for the churn model, including the prescriptive loop
(scoring the customer base so the analytics/dashboard track can prioritise retention).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import pandas as pd

from ..core.loader import MODELS_DIR, PROCESSED_DIR, load_processed_data

DEFAULT_MODEL_PATH = MODELS_DIR / "xgb_churn_model.joblib"
DECISION_THRESHOLD = 0.50
HIGH_RISK_THRESHOLD = 0.60
MEDIUM_RISK_THRESHOLD = 0.35


def categorize_risk(prob: float) -> str:
    if prob >= HIGH_RISK_THRESHOLD:
        return "High"
    if prob >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


def generate_recommendation(customer: Dict[str, Any], risk: str) -> str:
    """Rule-based retention actions derived from the Analytics track findings."""
    if risk == "Low":
        return "Pelanggan loyal. Pertahankan pengalaman layanan prima."

    recs: List[str] = []
    if risk == "High":
        recs.append("Prioritas intervensi tim retensi.")
        if customer.get("contract") == "Month-to-month":
            recs.append("Tawarkan diskon untuk migrasi ke kontrak 1 tahun.")
        if customer.get("internet_service") == "Fiber optic" and customer.get("tech_support") == "No":
            recs.append("Sediakan complimentary Tech Support & Online Security.")
        if customer.get("payment_method") == "Electronic check":
            recs.append("Tawarkan reward untuk beralih ke Auto-pay.")
        if len(recs) == 1:
            recs.append("Hubungi pelanggan secara proaktif untuk mendiagnosis kepuasan layanan.")
    else:
        recs.append("Pelanggan dalam pengawasan retensi.")
        if customer.get("contract") == "Month-to-month":
            recs.append("Kirimkan penawaran paket bundling tahunan.")
    return " ".join(recs)


class ChurnPredictor:
    """Wraps the trained pipeline (feature engineering + preprocessing + XGBoost)."""

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        if not path.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {path}. Run `python -m src.telco_churn.prediction.train` first."
            )
        self.model_path = path
        self.pipeline = joblib.load(path)

    def predict_proba(self, df: pd.DataFrame) -> pd.Series:
        features = df.drop(columns=["churn", "customer_id"], errors="ignore")
        return pd.Series(self.pipeline.predict_proba(features)[:, 1], index=df.index)

    def predict_one(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        prob = float(self.predict_proba(pd.DataFrame([customer_data])).iloc[0])
        risk = categorize_risk(prob)
        return {
            "churn_prediction": "Yes" if prob >= DECISION_THRESHOLD else "No",
            "churn_probability": round(prob, 4),
            "risk_level": risk,
            "recommendation": generate_recommendation(customer_data, risk),
        }

    def predict_batch(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        probs = self.predict_proba(pd.DataFrame(customers))
        results = []
        for i, row in enumerate(customers):
            prob = float(probs.iloc[i])
            risk = categorize_risk(prob)
            results.append({
                "customer_id": row.get("customer_id") or f"CUST_{i + 1:04d}",
                "churn_prediction": "Yes" if prob >= DECISION_THRESHOLD else "No",
                "churn_probability": round(prob, 4),
                "risk_level": risk,
                "recommendation": generate_recommendation(row, risk),
            })
        return results


_default_predictor: Optional[ChurnPredictor] = None


def get_predictor() -> ChurnPredictor:
    global _default_predictor
    if _default_predictor is None:
        _default_predictor = ChurnPredictor()
    return _default_predictor


def predict_churn(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    return get_predictor().predict_one(customer_data)


def score_customers(df: Optional[pd.DataFrame] = None, only_active: bool = True) -> pd.DataFrame:
    """
    Prescriptive loop: adds `churn_risk_score` and `risk_level` to the customer base
    so the BI dashboard can sort retention priorities.
    """
    data = load_processed_data() if df is None else df.copy()
    if only_active and "churn" in data.columns:
        data = data[data["churn"] == "No"].copy()
    data["churn_risk_score"] = get_predictor().predict_proba(data).round(4)
    data["risk_level"] = data["churn_risk_score"].apply(categorize_risk)
    return data.sort_values("churn_risk_score", ascending=False)


if __name__ == "__main__":
    scored = score_customers()
    out = PROCESSED_DIR / "customer_risk_scores.csv"
    scored.to_csv(out, index=False)
    print(f"[inference] Scored {len(scored):,} active customers -> {out}")
    print(scored["risk_level"].value_counts().to_string())
