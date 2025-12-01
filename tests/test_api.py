from fastapi.testclient import TestClient

from cae.api.app import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_score_endpoint_returns_anomaly_scores() -> None:
    client = TestClient(create_app())
    payload = {
        "events": [
            {
                "match_id": "MATCH123",
                "over": 10,
                "ball": 2,
                "runs": 6,
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
