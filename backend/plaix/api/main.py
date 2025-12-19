"""FastAPI application for PLAIX with multi-sport dispatch."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from plaix.config import settings
from plaix.core.models import ScoreRequest, ScoreResponse
from plaix.core.registry import registry
from plaix.api.inference import (
    BatchPredictResponse,
    InferenceService,
    NarrateRequest,
    NarrateResponse,
    RecentSummaryRequest,
    SinglePredictRequest,
    SinglePredictResponse,
)
from plaix.services import anomaly_feed, live_match, report_export
import pandas as pd
from plaix.sports.cricket.scorer import score_events_from_dicts as score_cricket
from plaix.sports.football.scorer import score_events_from_dicts as score_football

app = FastAPI(title="PLAIX", version="0.2.0")

# Register available sports.
registry.register("cricket", score_cricket)
registry.register("football", score_football)
inference_service = InferenceService(model_path="models/ups_logreg.pkl")
feed_df = anomaly_feed.load_feed_dataset()


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": settings.service_name}


@app.get("/internal/metrics")
def internal_metrics() -> dict[str, int]:
    """Expose basic service metrics."""
    return {
        "active_sports": len(registry._handlers),
        "feed_items_loaded": len(feed_df) if feed_df is not None else 0,
    }


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
    tone = request.tone or "analyst"
    return inference_service.run_inference(request.payload, tone=tone)


@app.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(request: list[SinglePredictRequest]) -> BatchPredictResponse:
    """Inference endpoint for a batch of payloads."""
    results = [inference_service.run_inference(item.payload, tone=item.tone or "analyst") for item in request]
    return BatchPredictResponse(results=results)


@app.post("/player/recent/summary")
def player_recent_summary(request: RecentSummaryRequest) -> dict:
    """Return recent innings plus narrative summary (demo-friendly)."""
    if request.n <= 0:
        raise HTTPException(status_code=400, detail="n must be positive")
    return inference_service.summarize_recent_events(request.player_id, request.match_format, request.n, tone=request.tone or "analyst")


@app.post("/narrate/anomaly", response_model=NarrateResponse)
def narrate_anomaly(request: NarrateRequest) -> NarrateResponse:
    """Generate a narrative for a precomputed anomaly row (no scoring)."""
    return inference_service.narrate_only(request)


@app.get("/feed/anomalies")
def feed_anomalies(format: str = "ALL", min_ups: float = 0.0, min_prob: float = 0.0, limit: int = 25, sort: str = "combined"):
    """List anomalies for feed consumption."""
    items = anomaly_feed.list_feed_items(
        feed_df,
        match_format=format,
        min_ups=min_ups,
        min_prob=min_prob,
        limit=limit,
        sort=sort,
    )
    return {"items": items}


@app.get("/feed/anomaly/{event_id}")
def feed_anomaly_detail(event_id: str, tone: str = "commentator"):
    """Return anomaly detail with narrative for a given event id."""
    row = anomaly_feed.get_event_detail(feed_df, event_id)
    narrative = anomaly_feed.narrate_event(row, tone=tone)
    response = row.to_dict()
    response["event_id"] = event_id
    response.update(narrative)
    response["headline"] = anomaly_feed._build_headline(row)  # type: ignore[attr-defined]
    response["key_drivers"] = anomaly_feed._build_key_drivers(row)  # type: ignore[attr-defined]
    return response


@app.post("/live/start")
def live_start(payload: dict):
    """Start a live simulation session."""
    return live_match.start_session(payload)


@app.get("/live/step/{session_id}")
def live_step(session_id: str, i: int = 0, include_narrative: bool = False, tone: str = "commentator"):
    """Return a scored step for a live session."""
    return live_match.get_step(session_id, i, include_narrative=include_narrative, tone=tone)


@app.post("/live/stop/{session_id}")
def live_stop(session_id: str):
    """Stop and clear a live session."""
    return live_match.stop_session(session_id)


@app.post("/report/anomaly/pdf")
def report_anomaly_pdf(payload: dict):
    """Generate a PDF anomaly report."""
    return report_export.build_pdf_response(payload)
