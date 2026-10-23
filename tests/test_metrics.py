"""
Unit tests for Business KPI metrics and cohort calculations (Analytics Track).
Ensures robustness against empty inputs and division by zero.
"""

import pandas as pd
import pytest
from src.telco_churn.analytics.metrics import calculate_churn_rate, calculate_mrr_loss, calculate_arpu
from src.telco_churn.analytics.aggregations import build_tenure_cohorts, build_risk_matrix


def test_calculate_churn_rate():
    df = pd.DataFrame({
        "churn": ["Yes", "No", "No", "No"]
    })
    rate = calculate_churn_rate(df)
    assert rate == 25.0


def test_calculate_churn_rate_empty():
    df = pd.DataFrame(columns=["churn"])
    rate = calculate_churn_rate(df)
    assert rate == 0.0


def test_calculate_mrr_loss():
    df = pd.DataFrame({
        "churn": ["Yes", "No", "Yes"],
        "monthly_charges": [50.0, 100.0, 50.0]
    })
    res = calculate_mrr_loss(df)
    assert res["total_mrr"] == 200.0
    assert res["lost_mrr"] == 100.0
    assert res["pct_lost"] == 50.0


def test_calculate_mrr_loss_empty():
    df = pd.DataFrame(columns=["churn", "monthly_charges"])
    res = calculate_mrr_loss(df)
    assert res["total_mrr"] == 0.0
    assert res["lost_mrr"] == 0.0
    assert res["pct_lost"] == 0.0


def test_calculate_arpu():
    df = pd.DataFrame({
        "monthly_charges": [60.0, 80.0, 100.0]
    })
    arpu = calculate_arpu(df)
    assert arpu == 80.0


def test_calculate_arpu_empty():
    df = pd.DataFrame(columns=["monthly_charges"])
    arpu = calculate_arpu(df)
    assert arpu == 0.0


def test_build_tenure_cohorts():
    df = pd.DataFrame({
        "tenure": [5, 15, 30, 60],
        "churn": ["Yes", "No", "Yes", "No"],
        "monthly_charges": [50.0, 60.0, 70.0, 80.0]
    })
    cohorts = build_tenure_cohorts(df)
    assert len(cohorts) == 4
    assert "churn_rate_pct" in cohorts.columns


def test_build_risk_matrix():
    df = pd.DataFrame({
        "tenure": [5, 15, 30, 60],
        "contract": ["Month-to-month", "One year", "Two year", "Month-to-month"],
        "churn": ["Yes", "No", "No", "Yes"]
    })
    matrix = build_risk_matrix(df)
    assert not matrix.empty
    assert "Month-to-month" in matrix.columns
    assert matrix.loc["0-12 Bulan", "Month-to-month"] == 100.0
