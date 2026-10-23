"""
Data loading utilities with project-root-relative paths (no hardcoded local paths).
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

# src/telco_churn/core/loader.py -> parents[3] is the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "deliverables" / "prediction" / "models"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

RAW_FILENAME = "Telco-Customer-Churn.csv"
PROCESSED_FILENAME = "telco_churn_clean.csv"


def get_project_root() -> Path:
    """Returns the absolute path to the project root directory."""
    return PROJECT_ROOT


def load_raw_data(path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Loads the original, read-only dataset from data/raw/."""
    target = Path(path) if path else RAW_DIR / RAW_FILENAME
    if not target.exists():
        raise FileNotFoundError(f"Raw data not found: {target}")
    return pd.read_csv(target)


def load_processed_data(path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Loads the cleaned dataset (single source of truth) from data/processed/."""
    target = Path(path) if path else PROCESSED_DIR / PROCESSED_FILENAME
    if not target.exists():
        raise FileNotFoundError(
            f"Processed data not found: {target}. Run `python -m src.telco_churn.core.cleaner` first."
        )
    return pd.read_csv(target)
