"""FastAPI application for PLAIX MVP."""

from __future__ import annotations

from fastapi import FastAPI

from plaix.config import settings
from plaix.models.anomaly_scorer import AnomalyRequest, AnomalyResponse, score_events

app = FastAPI(title="PLAIX", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": settings.service_name}


@app.post("/score")
def score(batch: list[AnomalyRequest]) -> list[AnomalyResponse]:
    """Score a batch of events."""
    return score_events(batch)
