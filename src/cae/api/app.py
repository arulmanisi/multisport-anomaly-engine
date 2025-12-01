"""FastAPI application exposing anomaly scoring endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

from cae.data.schemas import BatchScoreRequest, BatchScoreResponse
from cae.models.anomaly import score_events
from cae.models.pipeline import score_and_persist
from cae.utils.storage import ResultStore


def create_app(store: ResultStore | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Cricket Anomaly Engine", version="0.1.0")
    if store is None:
        data_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"
        store = ResultStore(data_dir / "cae.db")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/score", response_model=BatchScoreResponse)
    def score(request: BatchScoreRequest) -> BatchScoreResponse:
        results = score_and_persist(request.events, store=store)
        return BatchScoreResponse(results=results)

    @app.get("/recent", response_model=BatchScoreResponse)
    def recent(limit: int = Query(20, ge=1, le=200)) -> BatchScoreResponse:
        """Fetch recent scored events from persistence."""
        results = store.fetch_recent(limit=limit) if store else []
        return BatchScoreResponse(results=results)

    ui_dir = Path(__file__).resolve().parent.parent.parent.parent / "ui"
    if ui_dir.exists():
        app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    return app


app = create_app()
