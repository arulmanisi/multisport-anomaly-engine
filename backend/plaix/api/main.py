"""FastAPI application for PLAIX with multi-sport dispatch."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from plaix.config import settings
from plaix.core.models import ScoreRequest, ScoreResponse
from plaix.core.registry import registry
from plaix.api.inference import (
    BatchPredictResponse,
    InferenceService,
    SinglePredictRequest,
    SinglePredictResponse,
)
from plaix.sports.cricket.scorer import score_events_from_dicts as score_cricket
from plaix.sports.football.scorer import score_events_from_dicts as score_football

app = FastAPI(title="PLAIX", version="0.2.0")

# Register available sports.
registry.register("cricket", score_cricket)
registry.register("football", score_football)
inference_service = InferenceService(model_path="models/ups_logreg.pkl")


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": settings.service_name}


@app.post("/score", response_model=list[dict])
def score(batch: list[dict]) -> list[dict]:
    """Backward-compatible scoring without sport dispatch (assumes cricket)."""
    return score_cricket(batch)


@app.post("/plaix/score", response_model=ScoreResponse)
def plaix_score(request: ScoreRequest) -> ScoreResponse:
    """Generic multi-sport scoring endpoint for PLAIX."""
    try:
        handler = registry.get(request.sport)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    results = handler(request.events)
    return ScoreResponse(results=results)


@app.post("/predict/single", response_model=SinglePredictResponse)
def predict_single(request: SinglePredictRequest) -> SinglePredictResponse:
    """Inference endpoint returning UPS + model anomaly output for a single payload."""
    return inference_service.run_inference(request.payload)


@app.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(request: list[SinglePredictRequest]) -> BatchPredictResponse:
    """Inference endpoint for a batch of payloads."""
    results = [inference_service.run_inference(item.payload) for item in request]
    return BatchPredictResponse(results=results)
