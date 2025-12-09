"""FastAPI application for PLAIX with multi-sport dispatch."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from plaix.config import settings
from plaix.core.models import ScoreRequest, ScoreResponse
from plaix.core.registry import registry
from plaix.sports.cricket.scorer import score_events_from_dicts as score_cricket
from plaix.sports.football.scorer import score_events_from_dicts as score_football

app = FastAPI(title="PLAIX", version="0.2.0")

# Register available sports.
registry.register("cricket", score_cricket)
registry.register("football", score_football)


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
