"""
Scikit-learn Pipeline construction: Domain Feature Engineering + ColumnTransformer.
Ensures zero data leakage by fitting solely on training data.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin


class DomainFeatureEngineer(BaseEstimator, TransformerMixin):
    """Generates high-signal domain features identified during exploratory analysis."""

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X.copy()

        if "contract" in X_out.columns:
            X_out["is_month_to_month"] = (X_out["contract"] == "Month-to-month").astype(int)

        if "payment_method" in X_out.columns:
            X_out["is_electronic_check"] = (X_out["payment_method"] == "Electronic check").astype(int)

        if "internet_service" in X_out.columns and "tech_support" in X_out.columns:
            X_out["fiber_no_tech_support"] = (
                (X_out["internet_service"] == "Fiber optic") & (X_out["tech_support"] == "No")
            ).astype(int)

        if "monthly_charges" in X_out.columns and "total_charges" in X_out.columns:
            X_out["monthly_to_total_ratio"] = np.where(
                X_out["total_charges"] > 0,
                X_out["monthly_charges"] / (X_out["total_charges"] + 1e-5),
                1.0
            )

        return X_out


def get_feature_columns() -> Tuple[List[str], List[str]]:
    numeric_features = [
        "tenure",
        "monthly_charges",
        "total_charges",
        "is_month_to_month",
        "is_electronic_check",
        "fiber_no_tech_support",
        "monthly_to_total_ratio"
    ]

    categorical_features = [
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "contract",
        "paperless_billing",
        "payment_method"
    ]

    return numeric_features, categorical_features


def build_preprocessor() -> ColumnTransformer:
    numeric_features, categorical_features = get_feature_columns()

    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ],
        remainder="drop"
    )

    return preprocessor


def create_full_pipeline(model: BaseEstimator) -> Pipeline:
    preprocessor = build_preprocessor()
    pipeline = Pipeline(steps=[
        ("engineer", DomainFeatureEngineer()),
        ("preprocessor", preprocessor),
        ("classifier", model)
    ])
    return pipeline
