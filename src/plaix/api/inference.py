"""REST-style inference service design (structure only)."""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel

# TODO: Uncomment when wiring real FastAPI app.
# from fastapi import FastAPI

from plaix.core.model import AnomalyModel
from plaix.sports.cricket.features import CricketFeatureExtractor


class SinglePredictRequest(BaseModel):
    """Request payload for single prediction."""

    payload: dict
    model_path: str | None = None


class SinglePredictResponse(BaseModel):
    """Response payload for single prediction."""

    ups_score: float
    is_anomalous: bool
    explanation: str | None = None


class BatchPredictRequest(BaseModel):
    """Request payload for batch prediction."""

    records: List[dict]
    model_path: str | None = None


class BatchPredictResponse(BaseModel):
    """Response payload for batch prediction."""

    results: List[SinglePredictResponse]


class InferenceService:
    """Inference service that wires feature extraction and model for anomaly scoring."""

    def __init__(self, model_path: str | None = None) -> None:
        self.feature_extractor = self._load_feature_extractor()
        self.model = self._load_model(model_path)

    def _load_feature_extractor(self) -> CricketFeatureExtractor:
        """Construct feature extractor (placeholder)."""
        # TODO: initialize with config/deps if needed.
        return CricketFeatureExtractor()

    def _load_model(self, model_path: str | None) -> AnomalyModel:
        """Load model wrapper and weights (placeholder)."""
        # TODO: choose model_type/config appropriately and load weights from model_path.
        model = AnomalyModel(model_type="placeholder", model_config={}, sport="cricket")
        if model_path:
            # model.load_model(model_path)
            pass
        return model

    def preprocess_input(self, payload: dict) -> Any:
        """Validate and convert raw payload to feature representation."""
        # TODO: run cleaning and feature extraction.
        return payload

    def run_inference(self, features: Any) -> float:
        """Run model inference to obtain UPS Score."""
        # TODO: call model.predict/predict_proba; return UPS score.
        return 0.0

    def format_output(self, ups_score: float) -> SinglePredictResponse:
        """Format model output into response schema."""
        is_anomalous = ups_score > 0.5  # placeholder threshold
        return SinglePredictResponse(
            ups_score=ups_score,
            is_anomalous=is_anomalous,
            explanation=None,  # TODO: add explanation/top features.
        )


# TODO: Uncomment and wire FastAPI when ready.
# app = FastAPI(title="PLAIX Inference Service")
# service = InferenceService()
#
# @app.post("/predict/single", response_model=SinglePredictResponse)
# def predict_single(request: SinglePredictRequest) -> SinglePredictResponse:
#     """
#     Predict UPS Score and anomaly flag for a single payload.
#
#     Expects: JSON payload with match/player context.
#     Returns: UPS Score (numeric) and is_anomalous flag.
#     """
#     features = service.preprocess_input(request.payload)
#     ups_score = service.run_inference(features)
#     return service.format_output(ups_score)
#
# @app.post("/predict/batch", response_model=BatchPredictResponse)
# def predict_batch(request: BatchPredictRequest) -> BatchPredictResponse:
#     """
#     Predict UPS Score and anomaly flag for a batch of payloads.
#
#     Expects: list of JSON records.
#     Returns: list of UPS scores and anomaly flags.
#     """
#     results: List[SinglePredictResponse] = []
#     for record in request.records:
#         features = service.preprocess_input(record)
#         ups_score = service.run_inference(features)
#         results.append(service.format_output(ups_score))
#     return BatchPredictResponse(results=results)
