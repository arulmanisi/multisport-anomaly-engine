"""FastAPI application exposing anomaly scoring endpoints."""

from __future__ import annotations

from fastapi import FastAPI

from cae.data.schemas import BatchScoreRequest, BatchScoreResponse
from cae.models.anomaly import score_events


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Cricket Anomaly Engine", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/score", response_model=BatchScoreResponse)
    def score(request: BatchScoreRequest) -> BatchScoreResponse:
        results = score_events(request.events)
        return BatchScoreResponse(results=results)

    return app


app = create_app()
