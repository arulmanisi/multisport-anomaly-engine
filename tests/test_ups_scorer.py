from typing import Any, Dict, Iterable

from plaix.core.ups_scorer import HistoryProvider, UPSScorer


class StubHistoryProvider:
    def __init__(self, history: Iterable[Dict[str, Any]]):
        self._history = list(history)

    def get_player_innings_history(self, player_id: str, match_format: str):
        return self._history


def test_ups_scorer_anomalous_spike() -> None:
    # history mean ~25 runs; current 70 should yield high UPS
    history = [{"runs_scored": 20}, {"runs_scored": 25}, {"runs_scored": 30}, {"runs_scored": 25}, {"runs_scored": 26}]
    provider = StubHistoryProvider(history)
    scorer = UPSScorer(provider, sigma_min=5.0)

    ups_score = scorer.compute_ups_score("p1", "T20", current_runs=70)
    flag, bucket = scorer.classify_ups(ups_score)

    assert ups_score > 0
    assert flag == 1
    assert bucket in {"strong_spike", "extreme_spike"}


def test_ups_scorer_non_anomalous() -> None:
    history = [{"runs_scored": 25}, {"runs_scored": 24}, {"runs_scored": 26}, {"runs_scored": 25}, {"runs_scored": 25}]
    provider = StubHistoryProvider(history)
    scorer = UPSScorer(provider, sigma_min=5.0)

    ups_score = scorer.compute_ups_score("p1", "T20", current_runs=25)
    flag, bucket = scorer.classify_ups(ups_score)

    assert ups_score >= 0
    assert flag == 0
    assert bucket in {"normal", "mild_spike"}


def test_score_innings_returns_baseline_fields() -> None:
    history = [{"runs_scored": 20}, {"runs_scored": 21}, {"runs_scored": 22}, {"runs_scored": 23}, {"runs_scored": 24}]
    provider = StubHistoryProvider(history)
    scorer = UPSScorer(provider)

    result = scorer.score_innings("p1", "T20", current_runs=30)

    assert "ups_score" in result
    assert "ups_anomaly_flag" in result
    assert "ups_bucket" in result
    assert "baseline_mean_runs" in result
    assert "baseline_std_runs" in result
    assert "baseline_source" in result
