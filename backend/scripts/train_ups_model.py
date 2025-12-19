"""Train a simple UPS anomaly model (logistic regression) on synthetic data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from plaix.core.model import AnomalyModel

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_ups_dataset.csv"
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "ups_logreg.pkl"

FEATURE_COLUMNS = [
    "baseline_mean_runs",
    "baseline_std_runs",
    "current_runs",
    "venue_flatness",
    "opposition_strength",
    "batting_position",
]
LABEL_COLUMN = "ups_anomaly_flag"


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = AnomalyModel(model_type="logistic_regression", model_config={"max_iter": 200})
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    acc = accuracy_score(y_val, y_pred)
    prec = precision_score(y_val, y_pred, zero_division=0)
    rec = recall_score(y_val, y_pred, zero_division=0)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))

    print(f"Validation accuracy: {acc:.3f}")
    print(f"Validation precision: {prec:.3f}")
    print(f"Validation recall: {rec:.3f}")
    print(f"Saved model to {MODEL_PATH}")

    # Save metrics
    metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
    }
    metrics_path = MODEL_PATH.parent / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    # Save metadata
    meta = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "logistic_regression",
        "config": {"max_iter": 200},
        "data_source": str(DATA_PATH.name),
    }
    meta_path = MODEL_PATH.parent / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {meta_path}")


if __name__ == "__main__":
    main()
