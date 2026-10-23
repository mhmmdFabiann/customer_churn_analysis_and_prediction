"""
Unit tests for data cleaning and column standardization (Shared Core).
Ensures consistency and validity of basic data preparation.
"""

import pandas as pd
from src.telco_churn.core.cleaner import clean_column_names, clean_telco_data


def test_clean_column_names():
    df = pd.DataFrame(columns=["customerID", "SeniorCitizen", "MonthlyCharges", "TotalCharges"])
    df_cleaned = clean_column_names(df)
    assert list(df_cleaned.columns) == ["customer_id", "senior_citizen", "monthly_charges", "total_charges"]


def test_clean_telco_data_whitespace_handling():
    df = pd.DataFrame([{
        "customerID": "TEST-01",
        "tenure": 0,
        "MonthlyCharges": 25.5,
        "TotalCharges": "   "  # whitespace string
    }])

    df_cleaned = clean_telco_data(df)
    assert df_cleaned["total_charges"].dtype == "float64"
    assert df_cleaned["total_charges"].iloc[0] == 0.0
    assert df_cleaned.isna().sum().sum() == 0


def test_clean_telco_data_preserves_valid_values():
    df = pd.DataFrame([{
        "customerID": "TEST-02",
        "tenure": 12,
        "MonthlyCharges": 70.35,
        "TotalCharges": "844.20"
    }])

    df_cleaned = clean_telco_data(df)
    assert df_cleaned["total_charges"].iloc[0] == 844.20
    assert df_cleaned["monthly_charges"].iloc[0] == 70.35
