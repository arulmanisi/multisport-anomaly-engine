from typing import Any, Dict, Iterable

from plaix.core.ups_scorer import UPSScorer


class FakeHistoryProvider:
    """Returns fixed history for testing."""

    def __init__(self):
        self.data = {
            ("P1", "T20"): [
                {"runs_scored": 20},
                {"runs_scored": 22},
                {"runs_scored": 25},
                {"runs_scored": 18},
                {"runs_scored": 30},
                {"runs_scored": 24},
                {"runs_scored": 21},
                {"runs_scored": 19},
                {"runs_scored": 23},
                {"runs_scored": 26},
            ]
        }

    def get_player_innings_history(self, player_id: str, match_format: str) -> Iterable[Dict[str, Any]]:
        return self.data.get((player_id, match_format), [])


def _scorer() -> UPSScorer:
    return UPSScorer(FakeHistoryProvider())


def test_compute_player_baseline_structure() -> None:
    scorer = _scorer()
    baseline = scorer.compute_player_baseline("P1", "T20")

    assert isinstance(baseline.mean_runs, float)
    assert isinstance(baseline.std_runs, float)
    assert isinstance(baseline.num_innings, int)
    assert isinstance(baseline.source, str)


def test_ups_score_increases_with_large_deviation() -> None:
    scorer = _scorer()
    ups_near = scorer.compute_ups_score("P1", "T20", current_runs=25)
    ups_far = scorer.compute_ups_score("P1", "T20", current_runs=60)

    assert 0 <= ups_near <= 5
    assert 0 <= ups_far <= 5
    assert ups_far > ups_near


def test_classify_ups_thresholds() -> None:
    scorer = _scorer()
    assert scorer.classify_ups(0.5) == (0, "normal")
    assert scorer.classify_ups(1.5) == (0, "mild_spike")
    assert scorer.classify_ups(2.5) == (1, "strong_spike")
    assert scorer.classify_ups(3.5) == (1, "extreme_spike")


def test_score_innings_integration() -> None:
    scorer = _scorer()
    result = scorer.score_innings("P1", "T20", current_runs=60)

    expected_keys = {
        "ups_score",
        "ups_anomaly_flag",
        "ups_bucket",
        "baseline_mean_runs",
        "baseline_std_runs",
        "baseline_source",
    }
    assert expected_keys.issubset(result.keys())
    assert result["ups_score"] > 0
    assert result["ups_anomaly_flag"] in {0, 1}
