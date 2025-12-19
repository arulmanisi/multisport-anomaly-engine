#!/usr/bin/env python
"""Run a quick benchmark on the synthetic UPS dataset."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

# Ensure plaix modules are importable
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = BACKEND_ROOT / "src"
# Add both backend root and src (depending on layout)
for candidate in (BACKEND_ROOT, SRC_PATH):
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from plaix.core.model import AnomalyModel  # noqa: E402


DATA_PATH = BACKEND_ROOT / "data" / "synthetic_ups_dataset.csv"
MODEL_PATH = BACKEND_ROOT / "models" / "ups_logreg.pkl"
METRICS_PATH = BACKEND_ROOT / "data" / "benchmark_metrics.json"

FEATURE_COLUMNS = [
    "baseline_mean_runs",
    "baseline_std_runs",
    "current_runs",
    "venue_flatness",
    "opposition_strength",
    "batting_position",
]
LABEL_COLUMN = "ups_anomaly_flag"


def ensure_dataset() -> None:
    """Generate synthetic dataset if missing."""
    if DATA_PATH.exists():
        return
    generator = Path(__file__).resolve().parent / "generate_synthetic_ups_data.py"
    print(f"Dataset not found at {DATA_PATH}. Generating via {generator} ...")
    subprocess.run([sys.executable, str(generator)], check=True)


def compute_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Train/val split, fit logistic regression, compute metrics."""
    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = AnomalyModel(model_type="logistic_regression", model_config={"max_iter": 200})
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    metrics = {
        "accuracy": float(accuracy_score(y_val, y_pred)),
        "precision": float(precision_score(y_val, y_pred, zero_division=0)),
        "recall": float(recall_score(y_val, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_val, y_proba)),
        "n_train": int(len(X_train)),
        "n_val": int(len(X_val)),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))

    return metrics


def main() -> None:
    ensure_dataset()
    df = pd.read_csv(DATA_PATH)
    metrics = compute_metrics(df)

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print("Benchmark metrics (synthetic dataset):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
