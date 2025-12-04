from plaix.core.ups_scorer import UPSScorer


def test_ups_scorer_anomalous_spike() -> None:
    scorer = UPSScorer(metric_config={"threshold": 1.0})
    baseline = {"avg_runs": 25.0, "strike_rate": 120.0, "wickets_per_match": 0.5, "economy": 7.5}
    performance = {"runs": 70.0, "strike_rate": 150.0, "wickets": 2.0, "economy": 6.0}

    ups_score = scorer.compute_ups_score(baseline, performance)

    assert ups_score > 0
    assert scorer.is_anomalous(ups_score, threshold=1.0) is True


def test_ups_scorer_non_anomalous() -> None:
    scorer = UPSScorer(metric_config={"threshold": 5.0})
    baseline = {"avg_runs": 25.0, "strike_rate": 120.0, "wickets_per_match": 0.5, "economy": 7.5}
    performance = {"runs": 25.0, "strike_rate": 120.0, "wickets": 0.5, "economy": 7.5}

    ups_score = scorer.compute_ups_score(baseline, performance)

    assert scorer.is_anomalous(ups_score, threshold=5.0) is False
