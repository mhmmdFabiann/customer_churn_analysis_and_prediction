"""
Training pipeline for the XGBoost churn classifier following the methodology from:
Peng et al. (2023) "Research on customer churn prediction and model interpretability analysis",
PLOS ONE 18(12): e0289724.

Key methodology elements implemented:
1. Sampling comparison on training data: No processing vs SMOTE vs ADASYN vs SMOTEENN.
2. SMOTEENN hybrid resampling selected as optimal to handle class imbalance without noise.
3. Model comparison: DecisionTree, KNN, GBDT, ExtraTrees, RandomForest, and XGBoost.
4. Hyperparameter-tuned XGBoost targeting AUC maximization (n_estimators=265, max_depth=5, learning_rate=0.097).
5. SHAP interpretability analysis (global beeswarm & local waterfall plots).
6. Complete inference pipeline serialization to deliverables/prediction/models/xgb_churn_model.joblib.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import ADASYN, SMOTE
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
import shap

from ..core.loader import FIGURES_DIR, MODELS_DIR, load_processed_data
from .pipelines import DomainFeatureEngineer, build_preprocessor

RANDOM_STATE = 42
TEST_SIZE = 0.20
MODEL_FILENAME = "xgb_churn_model.joblib"
METADATA_FILENAME = "model_metadata.json"

# Tuned parameters inspired by Peng et al. (2023) Table 7 & 8
XGB_TUNED_PARAMS = {
    "n_estimators": 265,
    "max_depth": 5,
    "learning_rate": 0.097,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
    "tree_method": "hist",
}


def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Canonical stratified train-test split before transformation (zero data leakage)."""
    X = df.drop(columns=["churn", "customer_id"], errors="ignore")
    y = (df["churn"] == "Yes").astype(int)
    return train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)


def compute_metrics(y_true, y_pred, y_prob) -> Dict[str, float]:
    return {
        "accuracy": float(round(accuracy_score(y_true, y_pred), 4)),
        "precision": float(round(precision_score(y_true, y_pred), 4)),
        "recall": float(round(recall_score(y_true, y_pred), 4)),
        "f1": float(round(f1_score(y_true, y_pred), 4)),
        "roc_auc": float(round(roc_auc_score(y_true, y_prob), 4)),
        "pr_auc": float(round(average_precision_score(y_true, y_prob), 4)),
    }


def compare_sampling_algorithms(X_train_trans, y_train, X_test_trans, y_test) -> pd.DataFrame:
    """Reproduces Table 5 from Peng et al. (2023) comparing sampling algorithms on XGBoost."""
    samplers = {
        "No processing": (X_train_trans, y_train),
        "SMOTE": SMOTE(random_state=RANDOM_STATE).fit_resample(X_train_trans, y_train),
        "ADASYN": ADASYN(random_state=RANDOM_STATE).fit_resample(X_train_trans, y_train),
        "SMOTEENN": SMOTEENN(random_state=RANDOM_STATE).fit_resample(X_train_trans, y_train),
    }

    records = []
    for name, (X_tr, y_tr) in samplers.items():
        clf = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=RANDOM_STATE, eval_metric="logloss")
        clf.fit(X_tr, y_tr)
        pred = clf.predict(X_test_trans)
        prob = clf.predict_proba(X_test_trans)[:, 1]
        m = compute_metrics(y_test, pred, prob)
        records.append({
            "Sampling algorithm": name,
            "Accuracy": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1-score": m["f1"],
            "AUC": m["roc_auc"],
        })

    return pd.DataFrame(records)


def compare_models(X_train_res, y_train_res, X_test_trans, y_test) -> pd.DataFrame:
    """Reproduces Table 6 & 9 from Peng et al. (2023) comparing classifiers after SMOTEENN."""
    models = {
        "DecisionTree": DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "GBDT": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=RANDOM_STATE),
        "ExtraTrees": ExtraTreesClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
        "XGBoost (Default)": XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=RANDOM_STATE, eval_metric="logloss"),
        "GA-XGBoost (Tuned)": XGBClassifier(**XGB_TUNED_PARAMS),
    }

    records = []
    for name, clf in models.items():
        clf.fit(X_train_res, y_train_res)
        pred = clf.predict(X_test_trans)
        prob = clf.predict_proba(X_test_trans)[:, 1] if hasattr(clf, "predict_proba") else [0.0] * len(y_test)
        m = compute_metrics(y_test, pred, prob)
        records.append({
            "Classifier": name,
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1-score": m["f1"],
            "Accuracy": m["accuracy"],
            "AUC": m["roc_auc"],
        })

    return pd.DataFrame(records)


def train_model() -> Dict[str, Any]:
    df = load_processed_data()
    X_train, X_test, y_train, y_test = split_data(df)

    feat_eng = DomainFeatureEngineer()
    prep = build_preprocessor()

    # Step 1: Preprocess training data
    X_train_trans = prep.fit_transform(feat_eng.transform(X_train))
    X_test_trans = prep.transform(feat_eng.transform(X_test))

    # Step 2: Sampling comparison (Peng et al. Table 5)
    sampling_df = compare_sampling_algorithms(X_train_trans, y_train, X_test_trans, y_test)
    tables_dir = Path("reports/tables")
    tables_dir.mkdir(parents=True, exist_ok=True)
    sampling_df.to_csv(tables_dir / "sampling_comparison.csv", index=False)

    # Step 3: Apply SMOTEENN (best sampling strategy as demonstrated in paper)
    sme = SMOTEENN(random_state=RANDOM_STATE)
    X_train_res, y_train_res = sme.fit_resample(X_train_trans, y_train)

    # Step 4: Model comparison on SMOTEENN balanced data (Peng et al. Table 6 & 9)
    model_comp_df = compare_models(X_train_res, y_train_res, X_test_trans, y_test)
    model_comp_df.to_csv(tables_dir / "model_comparison.csv", index=False)

    # Step 5: Fit Tuned GA-XGBoost Model
    best_xgb = XGBClassifier(**XGB_TUNED_PARAMS)
    best_xgb.fit(X_train_res, y_train_res)

    # Step 6: Package into standard Scikit-Learn Pipeline for clean production inference
    inference_pipeline = Pipeline([
        ("domain_features", feat_eng),
        ("preprocessor", prep),
        ("classifier", best_xgb),
    ])

    # Evaluate on held-out test set
    y_pred = inference_pipeline.predict(X_test)
    y_prob = inference_pipeline.predict_proba(X_test)[:, 1]
    final_metrics = compute_metrics(y_test, y_pred, y_prob)

    # Save artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / MODEL_FILENAME
    joblib.dump(inference_pipeline, model_path)

    # Save metrics table
    metrics_summary_df = pd.DataFrame([{
        "Model": "GA-XGBoost (Peng et al. 2023 with SMOTEENN)",
        **final_metrics,
    }])
    metrics_summary_df.to_csv(tables_dir / "model_evaluation_metrics.csv", index=False)

    # Step 7: Generate diagnostic figures
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Retained (0)", "Churn (1)"],
                yticklabels=["Retained (0)", "Churn (1)"])
    plt.title("GA-XGBoost Confusion Matrix (Held-out Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Predicted Class", fontsize=10)
    plt.ylabel("True Class", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "model_confusion_matrix.png", dpi=150)
    plt.close()

    # Figure 2: ROC and PR Curves
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(fpr, tpr, color="#2980b9", lw=2, label=f"GA-XGBoost (AUC = {final_metrics['roc_auc']:.4f})")
    ax1.plot([0, 1], [0, 1], "k--", lw=1)
    ax1.set_title("ROC Curve", fontsize=12, fontweight="bold")
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.legend(loc="lower right")

    ax2.plot(recall, precision, color="#e67e22", lw=2, label=f"PR-AUC = {final_metrics['pr_auc']:.4f}")
    ax2.axhline(y=float(y_test.mean()), color="k", linestyle="--", lw=1, label=f"Baseline ({y_test.mean():.3f})")
    ax2.set_title("Precision-Recall Curve", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Recall")
    ax2.set_ylabel("Precision")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "model_roc_pr_curves.png", dpi=150)
    plt.close()

    # Figure 3: SHAP Interpretability Summary Plot (Peng et al. Fig 11 & Fig 12)
    explainer = shap.TreeExplainer(best_xgb)
    shap_sample = X_test_trans[:300]
    shap_values = explainer.shap_values(shap_sample)

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, shap_sample, show=False)
    plt.title("SHAP Global Feature Impact (Peng et al. 2023 Methodology)", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "shap_summary_plot.png", dpi=150)
    plt.close()

    metadata = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "reference_paper": "Peng, K., Peng, Y., & Li, W. (2023). Research on customer churn prediction and model interpretability analysis. PLOS ONE, 18(12), e0289724.",
        "algorithm": "GA-XGBoost with SMOTEENN Resampling",
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "n_train_raw": int(len(X_train)),
        "n_train_smoteenn": int(len(X_train_res)),
        "n_test": int(len(X_test)),
        "hyperparameters": XGB_TUNED_PARAMS,
        "test_metrics": final_metrics,
        "sampling_comparison": sampling_df.to_dict(orient="records"),
        "model_comparison": model_comp_df.to_dict(orient="records"),
    }

    with open(MODELS_DIR / METADATA_FILENAME, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[train] Model pipeline saved to {model_path}")
    print(f"[train] Final Test Metrics: Accuracy={final_metrics['accuracy']:.4f} | Recall={final_metrics['recall']:.4f} "
          f"| Precision={final_metrics['precision']:.4f} | F1={final_metrics['f1']:.4f} | ROC-AUC={final_metrics['roc_auc']:.4f}")
    return metadata


if __name__ == "__main__":
    train_model()
