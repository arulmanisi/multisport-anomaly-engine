from fastapi.testclient import TestClient

from cae.api.app import create_app
from cae.utils.storage import ResultStore


def test_health_endpoint() -> None:
    client = TestClient(create_app(store=ResultStore(":memory:")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_score_endpoint_returns_anomaly_scores() -> None:
    client = TestClient(create_app(store=ResultStore(":memory:")))
    payload = {
        "events": [
            {
                "match_id": "MATCH123",
                "over": 10,
                "ball": 2,
                "runs": 8,
                "wickets": 0,
                "phase": "MIDDLE",
                "expected_runs": 3.5,
                "expected_wickets": 0.05,
            },
            {
                "match_id": "MATCH123",
                "over": 10,
                "ball": 3,
                "runs": 4,
                "wickets": 0,
                "phase": "MIDDLE",
                "expected_runs": 4.0,
                "expected_wickets": 0.1,
            },
        ]
    }

    response = client.post("/score", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert len(body["results"]) == 2

    anomaly_result = body["results"][0]
    assert anomaly_result["is_anomaly"] is True
    assert "runs higher than expected" in anomaly_result["reason"]

    non_anomaly_result = body["results"][1]
    assert non_anomaly_result["is_anomaly"] is False
    assert non_anomaly_result["reason"] == "within expected range"


def test_recent_endpoint_returns_persisted_results(tmp_path) -> None:
    store = ResultStore(tmp_path / "cae.db")
    client = TestClient(create_app(store=store))
    payload = {
        "events": [
            {
                "match_id": "MATCH123",
                "over": 1,
                "ball": 1,
                "runs": 7,
                "wickets": 0,
                "phase": "POWERPLAY",
                "expected_runs": 3.0,
                "expected_wickets": 0.05,
            }
        ]
    }

    post_resp = client.post("/score", json=payload)
    assert post_resp.status_code == 200

    recent_resp = client.get("/recent?limit=5")
    assert recent_resp.status_code == 200
    recent_body = recent_resp.json()
    assert "results" in recent_body
    assert len(recent_body["results"]) == 1
    assert recent_body["results"][0]["match_id"] == "MATCH123"
