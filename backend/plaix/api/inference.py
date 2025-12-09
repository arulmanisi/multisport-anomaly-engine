"""REST-style inference service design (structure only)."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

# TODO: Uncomment when wiring real FastAPI app.
# from fastapi import FastAPI

from plaix.core.model import AnomalyModel
from plaix.core.ups_scorer import BaselineStats, UPSScorer
from plaix.sports.cricket.features import CricketFeatureExtractor


class SinglePredictRequest(BaseModel):
    """Request payload for single prediction."""

    payload: dict
    model_path: str | None = None


class SinglePredictResponse(BaseModel):
    """Response payload for single prediction."""

    ups_score: float
    ups_bucket: str
    ups_anomaly_flag_baseline: int
    model_anomaly_probability: float
    model_anomaly_label: int
    explanation: str | None = None


class BatchPredictRequest(BaseModel):
    """Request payload for batch prediction."""

    records: List[dict]
    model_path: str | None = None


class BatchPredictResponse(BaseModel):
    """Response payload for batch prediction."""

    results: List[SinglePredictResponse]


class DummyHistoryProvider:
    """Simple history provider stub."""

    def get_player_innings_history(self, player_id: str, match_format: str):
        return []


def extract_features(payload: Dict[str, Any]) -> Dict[str, float]:
    """Build feature vector consistent with training."""
    return {
        "baseline_mean_runs": float(payload["baseline_mean_runs"]),
        "baseline_std_runs": float(payload["baseline_std_runs"]),
        "current_runs": float(payload["current_runs"]),
        "venue_flatness": float(payload.get("venue_flatness", 0.5)),
        "opposition_strength": float(payload.get("opposition_strength", 0.5)),
        "batting_position": int(payload.get("batting_position", 4)),
    }


class InferenceService:
    """Inference service that wires UPS scoring and model inference."""

    def __init__(self, model_path: str | None = None) -> None:
        self.feature_extractor = self._load_feature_extractor()
        self.ups_scorer = UPSScorer(DummyHistoryProvider())
        self.model = self._load_model(model_path)

    def _load_feature_extractor(self) -> CricketFeatureExtractor:
        """Construct feature extractor (placeholder)."""
        return CricketFeatureExtractor()

    def _load_model(self, model_path: str | None) -> AnomalyModel:
        """Load model wrapper and weights."""
        model = AnomalyModel(model_type="logistic_regression", model_config={}, sport="cricket")
        if model_path:
            model.load_model(model_path)
        return model

    def preprocess_input(self, payload: dict) -> Dict[str, float]:
        """Validate and convert raw payload to feature representation."""
        if "baseline_mean_runs" not in payload or "baseline_std_runs" not in payload:
            baseline = BaselineStats(mean_runs=20.0, std_runs=15.0, num_innings=0, source="default")
            payload["baseline_mean_runs"] = baseline.mean_runs
            payload["baseline_std_runs"] = baseline.std_runs
        return extract_features(payload)

    def run_inference(self, payload: dict) -> SinglePredictResponse:
        """Run UPS scoring + model inference for a single record."""
        ups_score = self.ups_scorer.compute_ups_score(
            payload.get("player_id", "unknown"),
            payload.get("match_format", "T20"),
            current_runs=float(payload["current_runs"]),
        )
        flag, bucket = self.ups_scorer.classify_ups(ups_score)
        features = self.preprocess_input(payload)
        proba = float(self.model.predict_proba([[features[c] for c in features]])[0][1])
        label = int(self.model.predict([[features[c] for c in features]])[0])
        return SinglePredictResponse(
            ups_score=ups_score,
            ups_bucket=bucket,
            ups_anomaly_flag_baseline=flag,
            model_anomaly_probability=proba,
            model_anomaly_label=label,
            explanation=None,
        )


# TODO: Uncomment and wire FastAPI when ready.
# app = FastAPI(title="PLAIX Inference Service")
# service = InferenceService(model_path="models/ups_logreg.pkl")
#
# @app.post("/predict/single", response_model=SinglePredictResponse)
# def predict_single(request: SinglePredictRequest) -> SinglePredictResponse:
#     """
#     Predict UPS score and anomaly probability for a single payload.
#     """
#     return service.run_inference(request.payload)
#
# @app.post("/predict/batch", response_model=BatchPredictResponse)
# def predict_batch(request: BatchPredictRequest) -> BatchPredictResponse:
#     """
#     Predict UPS score and anomaly probability for a batch of payloads.
#     """
#     results: List[SinglePredictResponse] = [service.run_inference(rec) for rec in request.records]
#     return BatchPredictResponse(results=results)
