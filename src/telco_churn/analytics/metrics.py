"""
Mathematical calculations for Business KPIs and Financial Retention Metrics.
Tested to be robust against empty inputs and division by zero.
"""

from typing import Union, Dict, Any
import pandas as pd
import numpy as np


def calculate_churn_rate(df: pd.DataFrame, churn_col: str = "churn") -> float:
    """Calculates churn rate as a percentage (0.0 to 100.0)."""
    if len(df) == 0:
        return 0.0
    churn_count = (df[churn_col] == "Yes").sum()
    return round(float(churn_count / len(df) * 100), 2)


def calculate_mrr_loss(df: pd.DataFrame, churn_col: str = "churn", revenue_col: str = "monthly_charges") -> Dict[str, float]:
    """
    Calculates total monthly revenue, lost MRR, and lost revenue percentage.
    """
    if len(df) == 0:
        return {"total_mrr": 0.0, "lost_mrr": 0.0, "pct_lost": 0.0}

    total_mrr = float(df[revenue_col].sum())
    churned_mask = df[churn_col] == "Yes"
    lost_mrr = float(df.loc[churned_mask, revenue_col].sum())
    pct_lost = (lost_mrr / total_mrr * 100) if total_mrr > 0 else 0.0

    return {
        "total_mrr": round(total_mrr, 2),
        "lost_mrr": round(lost_mrr, 2),
        "pct_lost": round(pct_lost, 2)
    }


def calculate_arpu(df: pd.DataFrame, revenue_col: str = "monthly_charges") -> float:
    """Calculates Average Revenue Per User (ARPU)."""
    if len(df) == 0:
        return 0.0
    return round(float(df[revenue_col].mean()), 2)
