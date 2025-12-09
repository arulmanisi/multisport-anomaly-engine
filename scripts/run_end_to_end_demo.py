"""End-to-end smoke demo: generate data, train model, run a sample prediction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure local imports work
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
sys.path.append(str(REPO_ROOT / "src"))
sys.path.append(str(REPO_ROOT))

from plaix.core.model import AnomalyModel
from plaix.core.ups_scorer import BaselineStats, UPSScorer
import scripts.generate_synthetic_ups_data as generate_synthetic_ups_data
import scripts.train_ups_model as train_ups_model

DATA_PATH = REPO_ROOT / "data" / "synthetic_ups_dataset.csv"
MODEL_PATH = REPO_ROOT / "models" / "ups_logreg.pkl"


class DummyHistoryProvider:
    """History provider stub to satisfy UPSScorer dependency."""

    def get_player_innings_history(self, player_id: str, match_format: str):
        return []


def ensure_data_and_model() -> None:
    """Generate synthetic data and train model if missing."""
    if not DATA_PATH.exists():
        generate_synthetic_ups_data.main()
    if not MODEL_PATH.exists():
        train_ups_model.main()


def main() -> None:
    ensure_data_and_model()

    # Sample innings payload
    payload = {
        "player_id": "P_DEMO",
        "match_format": "T20",
        "baseline_mean_runs": 22.0,
        "baseline_std_runs": 8.0,
        "current_runs": 60.0,
        "venue_flatness": 0.7,
        "opposition_strength": 0.6,
        "batting_position": 3,
    }

    # UPS scoring
    ups_scorer = UPSScorer(DummyHistoryProvider(), sigma_min=5.0)
    baseline = BaselineStats(
        mean_runs=payload["baseline_mean_runs"],
        std_runs=max(payload["baseline_std_runs"], ups_scorer.sigma_min),
        num_innings=0,
        source="provided",
    )
    ups_score = ups_scorer.compute_ups_score(
        payload["player_id"], payload["match_format"], current_runs=float(payload["current_runs"])
    )
    flag, bucket = ups_scorer.classify_ups(ups_score)

    # Model inference
    model = AnomalyModel(model_type="logistic_regression", model_config={}, sport="cricket")
    model.load_model(str(MODEL_PATH))
    feature_vec = [
        payload["baseline_mean_runs"],
        payload["baseline_std_runs"],
        payload["current_runs"],
        payload["venue_flatness"],
        payload["opposition_strength"],
        payload["batting_position"],
    ]
    model_proba = float(model.predict_proba([feature_vec])[0][1])
    model_label = int(model.predict([feature_vec])[0])

    summary = {
        "player_id": payload["player_id"],
        "match_format": payload["match_format"],
        "baseline_mean_runs": baseline.mean_runs,
        "baseline_std_runs": baseline.std_runs,
        "current_runs": payload["current_runs"],
        "ups_score": ups_score,
        "ups_bucket": bucket,
        "ups_anomaly_flag_baseline": flag,
        "model_anomaly_probability": model_proba,
        "model_anomaly_label": model_label,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
