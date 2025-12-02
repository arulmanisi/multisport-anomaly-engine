from fastapi.testclient import TestClient

from plaix.api.main import app


def test_score_endpoint_happy_path() -> None:
    client = TestClient(app)
    payload = [
        {
            "match_id": "M1",
            "over": 1,
            "ball": 1,
            "runs": 6,
            "wickets": 0,
            "expected_runs": 3.0,
            "expected_wickets": 0.1,
        },
        {
            "match_id": "M1",
            "over": 1,
            "ball": 2,
            "runs": 2,
            "wickets": 0,
            "expected_runs": 3.0,
            "expected_wickets": 0.1,
        },
    ]

    response = client.post("/score", json=payload)

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["is_anomaly"] is True
    assert results[1]["is_anomaly"] is False


def test_score_endpoint_empty_list_returns_empty() -> None:
    client = TestClient(app)

    response = client.post("/score", json=[])

    assert response.status_code == 200
    assert response.json() == []
