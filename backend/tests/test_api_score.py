from fastapi.testclient import TestClient

from plaix.api.main import app


def _cricket_payload():
    return {
        "sport": "cricket",
        "events": [
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
        ],
    }


def test_plaix_score_endpoint_happy_path_cricket() -> None:
    client = TestClient(app)

    response = client.post("/plaix/score", json=_cricket_payload())

    assert response.status_code == 200
    results = response.json()["results"]
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["is_anomaly"] is True
    assert results[1]["is_anomaly"] is False


def test_plaix_score_endpoint_empty_events() -> None:
    client = TestClient(app)
    payload = {"sport": "cricket", "events": []}

    response = client.post("/plaix/score", json=payload)

    assert response.status_code == 200
    assert response.json()["results"] == []


def test_plaix_score_unsupported_sport() -> None:
    client = TestClient(app)
    payload = {"sport": "unknown", "events": []}

    response = client.post("/plaix/score", json=payload)

    assert response.status_code == 400
    assert "Unsupported sport" in response.json()["detail"]


def test_plaix_score_football_stub() -> None:
    client = TestClient(app)
    payload = {"sport": "football", "events": [{"event_id": 1}]}

    response = client.post("/plaix/score", json=payload)

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["sport"] == "football"
    assert results[0]["is_anomaly"] is False
