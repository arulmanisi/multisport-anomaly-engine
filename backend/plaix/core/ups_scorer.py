"""UPS (Unexpected Performance Spike) scorer for player batting innings."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Protocol


class HistoryProvider(Protocol):
    """Protocol for retrieving player history."""

    def get_player_innings_history(self, player_id: str, match_format: str) -> Iterable[Dict[str, Any]]:
        """
        Return recent innings for player_id and match_format.
        Expected most recent first. Each item should include:
            - runs_scored: int/float
            - timestamp or sequence (optional)
        """


@dataclass
class BaselineStats:
    """Baseline statistics for UPS computation."""

    mean_runs: float
    std_runs: float
    num_innings: int
    source: str


class UPSScorer:
    """
    Compute UPS Score for a single batting innings.

    Assumptions (encoded in logic and docstrings):
    - Event: one player batting innings.
    - UPS for MVP uses only `runs_scored`.
    - History is per-player, per-format (e.g., T20/ODI/TEST).
    - Baseline uses up to last N innings (window_size), minimum min_history.
    - Recency weighting: w_i = exp(-lambda * i), i=0 most recent.
    - Baseline mean/std computed with exponential weights; sigma_min guards tiny std.
    - UPS = clipped positive z-score: z = (runs - μ) / sigma_eff; UPS = min(max(z, 0), 5).
    - Buckets:
        * UPS < 1.0          -> normal (flag 0)
        * 1.0 ≤ UPS < 2.0    -> mild_spike (flag 0)
        * 2.0 ≤ UPS < 3.0    -> strong_spike (flag 1)
        * UPS ≥ 3.0          -> extreme_spike (flag 1)
    """

    def __init__(
        self,
        history_provider: HistoryProvider,
        *,
        window_size: int = 10,
        min_history: int = 5,
        decay_lambda: float = 0.3,
        sigma_min: float = 5.0,
    ) -> None:
        self.history_provider = history_provider
        self.window_size = window_size
        self.min_history = min_history
        self.decay_lambda = decay_lambda
        self.sigma_min = sigma_min

    def get_team_role_baseline(self, player_id: str, match_format: str) -> Optional[BaselineStats]:
        """
        Fetch team-role baseline when player history is insufficient (MVP fallback).

        Notes:
            - Placeholder implementation returns a simple heuristic baseline.
            - Replace with real team/role aggregates when data is available.
        """
        return BaselineStats(mean_runs=25.0, std_runs=max(self.sigma_min, 10.0), num_innings=0, source="team_role_fallback")

    def get_global_role_baseline(self, match_format: str) -> Optional[BaselineStats]:
        """
        Fetch global-role baseline when player/team baselines are unavailable (MVP fallback).

        Notes:
            - Placeholder implementation uses conservative global defaults.
            - Replace with format-specific aggregates when available.
        """
        return BaselineStats(mean_runs=22.0, std_runs=max(self.sigma_min, 12.0), num_innings=0, source="global_fallback")

    def _compute_weighted_stats(self, values: Iterable[float]) -> tuple[float, float, int]:
        """Compute exponential-weighted mean and std for a sequence of values."""
        values_list = list(values)
        weights = [math.exp(-self.decay_lambda * i) for i in range(len(values_list))]
        weight_sum = sum(weights)
        if weight_sum == 0:
            return 0.0, 0.0, 0
        mean = sum(v * w for v, w in zip(values_list, weights)) / weight_sum
        variance = sum(w * (v - mean) ** 2 for v, w in zip(values_list, weights)) / weight_sum
        std = math.sqrt(variance)
        return mean, std, len(values_list)

    def compute_player_baseline(self, player_id: str, match_format: str) -> BaselineStats:
        """
        Compute player-specific baseline for runs_scored with recency weighting.

        - Uses up to `window_size` most recent innings from history_provider.
        - Requires >= min_history innings; otherwise falls back to team/global/default baselines.
        - Default baseline: mean_runs=20, std_runs=15, source="default".
        """
        history = list(self.history_provider.get_player_innings_history(player_id, match_format))
        if history:
            history = history[: self.window_size]
        if len(history) >= self.min_history:
            runs = [float(item.get("runs_scored", 0.0)) for item in history]
            mean_runs, std_runs, n = self._compute_weighted_stats(runs)
            sigma_eff = max(std_runs, self.sigma_min)
            return BaselineStats(mean_runs=mean_runs, std_runs=sigma_eff, num_innings=n, source="player")

        # TODO: attempt team-role or global-role baselines.
        team_baseline = self.get_team_role_baseline(player_id, match_format)
        if team_baseline:
            return team_baseline
        global_baseline = self.get_global_role_baseline(match_format)
        if global_baseline:
            return global_baseline

        return BaselineStats(mean_runs=20.0, std_runs=15.0, num_innings=0, source="default")

    def compute_ups_score(self, player_id: str, match_format: str, current_runs: float) -> float:
        """
        Compute UPS score for a single innings.

        z = (current_runs - μ) / sigma_eff
        UPS = min(max(z, 0), 5)
        """
        baseline = self.compute_player_baseline(player_id, match_format)
        z = (current_runs - baseline.mean_runs) / baseline.std_runs if baseline.std_runs > 0 else 0.0
        z_pos = max(z, 0.0)
        ups = min(z_pos, 5.0)
        return ups

    def classify_ups(self, ups_score: float) -> tuple[int, str]:
        """
        Map UPS score to anomaly flag and bucket.

        Returns:
            (flag, bucket) where flag ∈ {0,1} and bucket ∈ {normal, mild_spike, strong_spike, extreme_spike}
        """
        if ups_score < 1.0:
            return 0, "normal"
        if ups_score < 2.0:
            return 0, "mild_spike"
        if ups_score < 3.0:
            return 1, "strong_spike"
        return 1, "extreme_spike"

    def score_innings(self, player_id: str, match_format: str, current_runs: float) -> Dict[str, Any]:
        """
        End-to-end UPS computation for an innings.

        Returns dict with UPS score, anomaly flag, bucket, and baseline stats.
        """
        baseline = self.compute_player_baseline(player_id, match_format)
        ups_score = self.compute_ups_score(player_id, match_format, current_runs)
        flag, bucket = self.classify_ups(ups_score)
        return {
            "ups_score": ups_score,
            "ups_anomaly_flag": flag,
            "ups_bucket": bucket,
            "baseline_mean_runs": baseline.mean_runs,
            "baseline_std_runs": baseline.std_runs,
            "baseline_source": baseline.source,
        }
