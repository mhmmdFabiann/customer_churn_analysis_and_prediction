"""
Aggregation and segmentation utilities for cohort analysis and risk heatmaps.
"""

from typing import List, Optional
import pandas as pd


def build_tenure_cohorts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups customers into tenure cohorts and calculates cohort-specific retention KPIs.
    """
    df_out = df.copy()
    bins = [-1, 12, 24, 48, 72]
    labels = ["01. 0-12 Bulan (Baru)", "02. 13-24 Bulan", "03. 25-48 Bulan", "04. 49-72 Bulan (Loyal)"]
    df_out["tenure_cohort"] = pd.cut(df_out["tenure"], bins=bins, labels=labels)

    cohort_summary = df_out.groupby("tenure_cohort", observed=False).agg(
        total_customers=("churn", "count"),
        churned_customers=("churn", lambda s: (s == "Yes").sum()),
        churn_rate_pct=("churn", lambda s: round((s == "Yes").mean() * 100, 2)),
        avg_monthly_charges=("monthly_charges", lambda s: round(s.mean(), 2))
    ).reset_index()

    return cohort_summary


def build_risk_matrix(df: pd.DataFrame, row_col: str = "tenure", col_col: str = "contract") -> pd.DataFrame:
    """
    Builds risk percentage matrix across two dimensions.
    """
    df_out = df.copy()
    if row_col == "tenure":
        bins = [-1, 12, 24, 48, 72]
        labels = ["0-12 Bulan", "13-24 Bulan", "25-48 Bulan", "49-72 Bulan"]
        df_out["tenure_group"] = pd.cut(df_out["tenure"], bins=bins, labels=labels)
        row_dim = "tenure_group"
    else:
        row_dim = row_col

    matrix = df_out.pivot_table(
        index=row_dim,
        columns=col_col,
        values="churn",
        aggfunc=lambda s: round((s == "Yes").mean() * 100, 1),
        observed=False
    )
    return matrix
