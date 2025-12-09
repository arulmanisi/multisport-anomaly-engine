from cae.data.schemas import EventInput
from cae.models.anomaly import score_event


def test_score_event_detects_anomaly_and_reason() -> None:
    event = EventInput(
        match_id="M1",
        over=1,
        ball=1,
        runs=8,
        wickets=1,
        phase="POWERPLAY",
        expected_runs=3.0,
        expected_wickets=0.1,
    )

    result = score_event(event)

    assert result.is_anomaly is True
    assert result.anomaly_score > 2
    assert "runs higher than expected" in result.reason
    assert "more wickets than expected" in result.reason


def test_score_event_within_expected_range() -> None:
    event = EventInput(
        match_id="M1",
        over=1,
        ball=1,
        runs=3,
        wickets=0,
        phase="POWERPLAY",
        expected_runs=3.0,
        expected_wickets=0.0,
    )

    result = score_event(event)

    assert result.is_anomaly is False
    assert result.anomaly_score < 2
    assert result.reason == "within expected range"
