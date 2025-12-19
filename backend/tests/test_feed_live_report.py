"""Smoke-level backend tests for feed, live, and report endpoints."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_feed_list_and_detail() -> None:
    resp = client.get("/feed/anomalies", params={"limit": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and len(data["items"]) > 0
    item = data["items"][0]
    for key in ["event_id", "player_id", "match_format", "ups_score", "ups_bucket", "headline", "key_drivers"]:
        assert key in item

    detail = client.get(f"/feed/anomaly/{item['event_id']}", params={"tone": "commentator"})
    assert detail.status_code == 200
    d_json = detail.json()
    for key in ["narrative_title", "narrative_summary"]:
        assert key in d_json


def test_live_start_and_step() -> None:
    start = client.post(
        "/live/start",
        json={
            "player_id": "P_TEST",
            "match_format": "T20",
            "scenario": "normal",
            "baseline_mean_runs": 22,
            "baseline_std_runs": 8,
            "overs": 5,
            "tone": "commentator",
            "include_narrative": True,
        },
    )
    assert start.status_code == 200
    s_json = start.json()
    assert "session_id" in s_json and "total_steps" in s_json
    session_id = s_json["session_id"]

    step = client.get(f"/live/step/{session_id}", params={"i": 0, "include_narrative": True, "tone": "commentator"})
    assert step.status_code == 200
    step_json = step.json()
    for key in ["cumulative_runs", "ups_score", "headline", "key_drivers"]:
        assert key in step_json


def test_report_pdf() -> None:
    resp = client.post(
        "/report/anomaly/pdf",
        json={
            "player_id": "P_TEST",
            "match_format": "T20",
            "current_runs": 55,
            "baseline_mean_runs": 22,
            "baseline_std_runs": 8,
            "ups_score": 2.1,
            "ups_bucket": "strong_spike",
            "model_anomaly_probability": 0.6,
            "model_anomaly_label": 1,
        },
    )
    assert resp.status_code == 200
    assert "application/pdf" in resp.headers.get("content-type", "")
    body = resp.content
    assert body.startswith(b"%PDF")
