from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from plaix.api.inference import (
    BatchPredictRequest,
    BatchPredictResponse,
    InferenceService,
    SinglePredictRequest,
    SinglePredictResponse,
)


class DummyModel:
    def predict_proba(self, X):
        return [[0.3, 0.7] for _ in X]

    def predict(self, X):
        return [1 for _ in X]


def build_app(service: InferenceService) -> FastAPI:
    app = FastAPI()

    @app.post("/predict/single", response_model=SinglePredictResponse)
    def predict_single(req: SinglePredictRequest) -> SinglePredictResponse:
        return service.run_inference(req.payload)

    @app.post("/predict/batch", response_model=BatchPredictResponse)
    def predict_batch(req: BatchPredictRequest) -> BatchPredictResponse:
        results: List[SinglePredictResponse] = [service.run_inference(rec) for rec in req.records]
        return BatchPredictResponse(results=results)

    return app


def test_rest_single_prediction(monkeypatch) -> None:
    service = InferenceService()
    service.model = DummyModel()
    app = build_app(service)
    client = TestClient(app)

    resp = client.post(
        "/predict/single",
        json={
            "payload": {
                "player_id": "P1",
                "match_format": "T20",
                "current_runs": 35,
                "baseline_mean_runs": 22,
                "baseline_std_runs": 10,
            }
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "ups_score" in data
    assert "ups_bucket" in data
    assert "model_anomaly_probability" in data


def test_rest_batch_prediction(monkeypatch) -> None:
    service = InferenceService()
    service.model = DummyModel()
    app = build_app(service)
    client = TestClient(app)

    resp = client.post(
        "/predict/batch",
        json={
            "records": [
                {
                    "player_id": "P1",
                    "match_format": "T20",
                    "current_runs": 20,
                    "baseline_mean_runs": 22,
                    "baseline_std_runs": 10,
                },
                {
                    "player_id": "P2",
                    "match_format": "T20",
                    "current_runs": 45,
                    "baseline_mean_runs": 22,
                    "baseline_std_runs": 10,
                },
            ]
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) == 2
