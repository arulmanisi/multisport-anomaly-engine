"""CLI skeleton for anomaly inference (design-level only)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from plaix.core.model import AnomalyModel
from plaix.core.ups_scorer import BaselineStats, UPSScorer
from plaix.sports.cricket.features import CricketFeatureExtractor


class DummyHistoryProvider:
    """Simple history provider that returns empty history (baseline provided via input)."""

    def get_player_innings_history(self, player_id: str, match_format: str):
        return []


def load_model(model_path: Path) -> AnomalyModel:
    """Load a trained model artifact."""
    model = AnomalyModel(model_type="logistic_regression", model_config={}, sport="cricket")
    model.load_model(str(model_path))
    return model


def parse_json_input(input_arg: str) -> Dict[str, Any]:
    """Parse JSON input from string or file path."""
    candidate = Path(input_arg)
    if candidate.exists():
        return json.loads(candidate.read_text())
    return json.loads(input_arg)


def build_feature_extractor() -> CricketFeatureExtractor:
    """Construct a cricket feature extractor (placeholder)."""
    # TODO: inject real dependencies/config into the extractor.
    return CricketFeatureExtractor()


def build_ups_scorer() -> UPSScorer:
    """Construct UPS scorer with dummy history provider."""
    return UPSScorer(DummyHistoryProvider())


def extract_features_from_payload(payload: Dict[str, Any]) -> Dict[str, float]:
    """Build feature vector consistent with training."""
    return {
        "baseline_mean_runs": float(payload["baseline_mean_runs"]),
        "baseline_std_runs": float(payload["baseline_std_runs"]),
        "current_runs": float(payload["current_runs"]),
        "venue_flatness": float(payload.get("venue_flatness", 0.5)),
        "opposition_strength": float(payload.get("opposition_strength", 0.5)),
        "batting_position": int(payload.get("batting_position", 4)),
    }


def run_predict_single(args: argparse.Namespace) -> None:
    """Run anomaly scoring for a single payload."""
    payload = parse_json_input(args.input)
    model = load_model(Path(args.model))
    ups_scorer = build_ups_scorer()

    # Use provided baseline stats if present; otherwise use UPS scorer to compute baseline.
    if "baseline_mean_runs" not in payload or "baseline_std_runs" not in payload:
        # TODO: call ups_scorer.compute_player_baseline with real history.
        baseline = BaselineStats(mean_runs=20.0, std_runs=15.0, num_innings=0, source="default")
        payload["baseline_mean_runs"] = baseline.mean_runs
        payload["baseline_std_runs"] = baseline.std_runs

    ups_score = ups_scorer.compute_ups_score(
        payload.get("player_id", "unknown"),
        payload.get("match_format", "T20"),
        current_runs=float(payload["current_runs"]),
    )
    flag, bucket = ups_scorer.classify_ups(ups_score)

    features = extract_features_from_payload(payload)
    model_proba = model.predict_proba([[features[c] for c in features]])[0][1]
    model_label = int(model.predict([[features[c] for c in features]])[0])

    output = {
        "ups_score": ups_score,
        "ups_bucket": bucket,
        "ups_anomaly_flag_baseline": flag,
        "model_anomaly_probability": float(model_proba),
        "model_anomaly_label": model_label,
    }
    print(json.dumps(output, indent=2))


def run_predict_batch(args: argparse.Namespace) -> None:
    """Run anomaly scoring for a batch file."""
    batch_path = Path(args.input)
    payloads = json.loads(batch_path.read_text())
    model = load_model(Path(args.model))
    ups_scorer = build_ups_scorer()

    results: List[Dict[str, Any]] = []
    for payload in payloads:
        if "baseline_mean_runs" not in payload or "baseline_std_runs" not in payload:
            baseline = BaselineStats(mean_runs=20.0, std_runs=15.0, num_innings=0, source="default")
            payload["baseline_mean_runs"] = baseline.mean_runs
            payload["baseline_std_runs"] = baseline.std_runs

        ups_score = ups_scorer.compute_ups_score(
            payload.get("player_id", "unknown"),
            payload.get("match_format", "T20"),
            current_runs=float(payload["current_runs"]),
        )
        flag, bucket = ups_scorer.classify_ups(ups_score)
        features = extract_features_from_payload(payload)
        model_proba = model.predict_proba([[features[c] for c in features]])[0][1]
        model_label = int(model.predict([[features[c] for c in features]])[0])

        results.append(
            {
                "ups_score": ups_score,
                "ups_bucket": bucket,
                "ups_anomaly_flag_baseline": flag,
                "model_anomaly_probability": float(model_proba),
                "model_anomaly_label": model_label,
            }
        )

    print(json.dumps({"results": results}, indent=2))


def get_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI."""
    parser = argparse.ArgumentParser(description="PLAIX anomaly inference CLI (design skeleton)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("predict-single", help="Predict anomaly for a single JSON payload")
    single.add_argument("--input", required=True, help="JSON string or path to JSON file")
    single.add_argument("--model", required=True, help="Path to trained model artifact")
    single.set_defaults(func=run_predict_single)

    batch = subparsers.add_parser("predict-batch", help="Predict anomalies for a batch file")
    batch.add_argument("--input", required=True, help="Path to batch file (JSON/CSV placeholder)")
    batch.add_argument("--model", required=True, help="Path to trained model artifact")
    batch.set_defaults(func=run_predict_batch)

    return parser


def main(argv: List[str] | None = None) -> None:
    """CLI entrypoint."""
    parser = get_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
