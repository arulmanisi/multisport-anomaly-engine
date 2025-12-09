from cae.data.simulator import events_to_dataframe, simulate_match_events
from cae.models.predictor import score_dataframe


def test_simulator_generates_expected_count_and_fields() -> None:
    events = simulate_match_events(overs=4, balls_per_over=6, anomaly_rate=0.0, seed=123)

    assert len(events) == 24
    assert all(event.match_id == "SIM-1" for event in events)
    assert all(event.over >= 1 for event in events)
    assert all(event.ball >= 1 for event in events)
    assert all(event.expected_runs >= 0 for event in events)
    assert all(event.expected_wickets >= 0 for event in events)
    assert set(event.phase for event in events) == {"POWERPLAY"}


def test_simulation_and_prediction_pipeline_detects_anomalies() -> None:
    events = simulate_match_events(overs=2, balls_per_over=6, anomaly_rate=1.0, seed=7)
    df = events_to_dataframe(events)

    results = score_dataframe(df)

    assert len(results) == len(events)
    assert any(result.is_anomaly for result in results)
