"""
Foundational data cleaner (shared by the Analytics and Science tracks).

Cleaning is performed exactly once here; every notebook and module reads the
result from data/processed/ instead of re-implementing cleaning logic.
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from .loader import PROCESSED_DIR, PROCESSED_FILENAME, load_raw_data


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names to snake_case (e.g. 'customerID' -> 'customer_id')."""
    df_clean = df.copy()
    df_clean.columns = (
        df_clean.columns
        .str.strip()
        .str.replace(r"([a-z0-9])([A-Z])", r"\1_\2", regex=True)
        .str.replace(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", regex=True)
        .str.replace(r"[\s\-]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
        .str.lower()
    )
    return df_clean


def clean_telco_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw Telco Churn DataFrame:
    1. Standardizes column names to snake_case.
    2. Converts whitespace-only `total_charges` to 0.0. In the source data these
       rows all have tenure == 0 (no billing cycle completed yet), so 0.0 is the
       business-correct value rather than a mean/median imputation.
    """
    df_clean = clean_column_names(df)

    if "total_charges" in df_clean.columns and df_clean["total_charges"].dtype == "object":
        df_clean["total_charges"] = (
            pd.to_numeric(df_clean["total_charges"].str.strip(), errors="coerce").fillna(0.0)
        )

    return df_clean


def save_processed_data(df: pd.DataFrame, path: Optional[Union[str, Path]] = None) -> Path:
    """Saves the cleaned DataFrame to data/processed/."""
    target = Path(path) if path else PROCESSED_DIR / PROCESSED_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target, index=False)
    return target


if __name__ == "__main__":
    clean = clean_telco_data(load_raw_data())
    out = save_processed_data(clean)
    print(f"[cleaner] {len(clean):,} rows x {clean.shape[1]} cols | nulls={int(clean.isna().sum().sum())} "
          f"| duplicate IDs={int(clean['customer_id'].duplicated().sum())} -> {out}")
