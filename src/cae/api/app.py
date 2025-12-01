"""FastAPI application exposing anomaly scoring endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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

    ui_dir = Path(__file__).resolve().parent.parent.parent.parent / "ui"
    if ui_dir.exists():
        app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    return app


app = create_app()
