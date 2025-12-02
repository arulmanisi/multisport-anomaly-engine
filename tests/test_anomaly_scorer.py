import pandas as pd
import pytest

from plaix.models.anomaly_scorer import AnomalyRequest, prepare_requests_from_df, score_event


def test_non_anomalous_event() -> None:
    event = AnomalyRequest(
        match_id="M1",
        over=1,
        ball=1,
        runs=3,
        wickets=0,
        expected_runs=3.0,
        expected_wickets=0.1,
    )
    result = score_event(event)
    assert result.is_anomaly is False
    assert result.reason == "within expected range"


def test_anomalous_event_boundary() -> None:
    event = AnomalyRequest(
        match_id="M1",
        over=1,
        ball=2,
        runs=6,
        wickets=0,
        expected_runs=3.0,
        expected_wickets=0.1,
    )
    result = score_event(event)
    assert result.is_anomaly is True
    assert "runs >=" in result.reason


def test_anomalous_event_wicket() -> None:
    event = AnomalyRequest(
        match_id="M1",
        over=1,
        ball=3,
        runs=0,
        wickets=1,
        expected_runs=3.0,
        expected_wickets=0.1,
    )
    result = score_event(event)
    assert result.is_anomaly is True
    assert "wickets >=" in result.reason


def test_prepare_requests_from_df() -> None:
    df = pd.DataFrame(
        {
            "match_id": ["M1"],
            "over": [1],
            "ball": [1],
            "runs": [4],
            "wickets": [0],
            "expected_runs": [3.0],
            "expected_wickets": [0.1],
        }
    )
    requests = prepare_requests_from_df(df)
    assert len(requests) == 1
    assert requests[0].match_id == "M1"


def test_score_event_missing_expected_raises() -> None:
    event = AnomalyRequest(match_id="M1", over=1, ball=1, runs=4, wickets=0)
    with pytest.raises(ValueError):
        score_event(event)
