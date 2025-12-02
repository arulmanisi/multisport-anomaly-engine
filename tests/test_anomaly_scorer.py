from plaix.models.anomaly_scorer import AnomalyRequest, score_event


def test_non_anomalous_event() -> None:
    event = AnomalyRequest(match_id="M1", over=1, ball=1, runs=3, wickets=0)
    result = score_event(event)
    assert result.is_anomaly is False
    assert result.reason == "within expected range"


def test_anomalous_event_boundary() -> None:
    event = AnomalyRequest(match_id="M1", over=1, ball=2, runs=6, wickets=0)
    result = score_event(event)
    assert result.is_anomaly is True
    assert "runs >=" in result.reason


def test_anomalous_event_wicket() -> None:
    event = AnomalyRequest(match_id="M1", over=1, ball=3, runs=0, wickets=1)
    result = score_event(event)
    assert result.is_anomaly is True
    assert "wickets >=" in result.reason
