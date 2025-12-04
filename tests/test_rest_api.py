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


def build_app(service: InferenceService) -> FastAPI:
    app = FastAPI()

    @app.post("/predict/single", response_model=SinglePredictResponse)
    def predict_single(req: SinglePredictRequest) -> SinglePredictResponse:
        features = service.preprocess_input(req.payload)
        ups_score = service.run_inference(features)
        return service.format_output(ups_score)

    @app.post("/predict/batch", response_model=BatchPredictResponse)
    def predict_batch(req: BatchPredictRequest) -> BatchPredictResponse:
        results: List[SinglePredictResponse] = []
        for record in req.records:
            features = service.preprocess_input(record)
            ups_score = service.run_inference(features)
            results.append(service.format_output(ups_score))
        return BatchPredictResponse(results=results)

    return app


def test_rest_single_prediction(monkeypatch) -> None:
    service = InferenceService()
    monkeypatch.setattr(service, "run_inference", lambda features: 0.7)
    app = build_app(service)
    client = TestClient(app)

    resp = client.post("/predict/single", json={"payload": {"runs": 10}})

    assert resp.status_code == 200
    data = resp.json()
    assert "ups_score" in data
    assert "is_anomalous" in data


def test_rest_batch_prediction(monkeypatch) -> None:
    service = InferenceService()
    monkeypatch.setattr(service, "run_inference", lambda features: 0.3)
    app = build_app(service)
    client = TestClient(app)

    resp = client.post("/predict/batch", json={"records": [{"runs": 1}, {"runs": 2}]})

    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) == 2
