"""UPS (Unexpected Performance Spike) scorer design for anomaly detection."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import math


class UPSScorer:
    """Compute UPS Scores to quantify unexpected performance spikes."""

    def __init__(self, sport: str = "cricket", metric_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scorer.

        Args:
            sport: sport identifier; defaults to cricket, but structure allows others later.
            metric_config: optional configuration of metrics to consider (weights, thresholds).
        """
        self.sport = sport
        self.metric_config = metric_config or {}
        # TODO: load historical baselines from persistence or inject as dependency.

    def compute_player_baseline(self, player_history: Iterable[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute baseline statistics for a player.

        For cricket, baseline can include:
            - avg_runs: rolling average runs per innings
            - strike_rate: average strike rate
            - wickets_per_match: average wickets
            - economy: average runs conceded per over
        Args:
            player_history: iterable of match/innings stats dicts.
        Returns:
            Dict of baseline metrics.
        """
        # TODO: replace with real aggregation over history.
        return {
            "avg_runs": 25.0,
            "strike_rate": 120.0,
            "wickets_per_match": 0.8,
            "economy": 7.5,
        }

    def compute_match_performance(self, current_match_stats: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract performance metrics from current match stats.

        For cricket, expect keys like:
            - runs_scored
            - balls_faced
            - wickets_taken
            - overs_bowled
            - runs_conceded
        Returns:
            Dict of performance metrics to compare against baseline.
        """
        # TODO: normalize and validate current_match_stats schema.
        runs = float(current_match_stats.get("runs_scored", 0.0))
        balls = float(current_match_stats.get("balls_faced", 1.0))
        wickets = float(current_match_stats.get("wickets_taken", 0.0))
        overs = float(current_match_stats.get("overs_bowled", 1.0))
        runs_conceded = float(current_match_stats.get("runs_conceded", 0.0))
        strike_rate = (runs / balls) * 100 if balls > 0 else 0.0
        economy = (runs_conceded / overs) if overs > 0 else 0.0
        return {
            "runs": runs,
            "strike_rate": strike_rate,
            "wickets": wickets,
            "economy": economy,
        }

    def _z_score(self, value: float, mean: float, std: float) -> float:
        """Compute z-score with guard for zero std."""
        if std <= 0:
            return 0.0
        return (value - mean) / std

    def compute_ups_score(self, baseline: Dict[str, float], performance: Dict[str, float]) -> float:
        """
        Compute UPS score as a normalized deviation from baseline.

        Concept (example):
            - Compute per-metric z-scores for deviations (e.g., runs vs avg_runs, strike_rate vs baseline)
            - Combine via weighted sum or Euclidean norm to form UPS Score.
        Example:
            player avg_runs=25, current runs=70 → z_runs high -> contributes to UPS.
        Returns:
            UPS score (float); higher indicates more unexpected spike.
        """
        # Placeholder stds; TODO: derive from historical variance.
        std_runs = baseline.get("std_runs", 10.0)
        std_sr = baseline.get("std_strike_rate", 15.0)
        std_wkts = baseline.get("std_wickets", 0.8)
        std_eco = baseline.get("std_economy", 1.5)

        z_runs = self._z_score(performance.get("runs", 0.0), baseline.get("avg_runs", 0.0), std_runs)
        z_sr = self._z_score(performance.get("strike_rate", 0.0), baseline.get("strike_rate", 0.0), std_sr)
        z_wkts = self._z_score(performance.get("wickets", 0.0), baseline.get("wickets_per_match", 0.0), std_wkts)
        # For economy, lower is better; invert deviation
        eco_dev = baseline.get("economy", 0.0) - performance.get("economy", 0.0)
        z_eco = eco_dev / std_eco if std_eco > 0 else 0.0

        # Combine deviations; TODO: apply metric weights from metric_config.
        ups_score = math.sqrt(z_runs**2 + z_sr**2 + z_wkts**2 + z_eco**2)
        return ups_score

    def is_anomalous(self, ups_score: float, threshold: float = 2.0) -> bool:
        """
        Convert UPS score to binary anomaly flag.

        Args:
            ups_score: computed UPS score.
            threshold: z-score-like cutoff (default 2.0).
        Returns:
            True if anomalous, else False.
        """
        return ups_score >= threshold

    def score_player(self, player_history: Iterable[Dict[str, Any]], current_match_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        End-to-end UPS computation for a player.

        Args:
            player_history: historical records used to compute baseline.
            current_match_stats: stats for the current match/innings.
        Returns:
            Dict with ups_score and is_anomalous flag.
        """
        baseline = self.compute_player_baseline(player_history)
        performance = self.compute_match_performance(current_match_stats)
        ups_score = self.compute_ups_score(baseline, performance)
        return {
            "ups_score": ups_score,
            "is_anomalous": self.is_anomalous(ups_score, threshold=self.metric_config.get("threshold", 2.0)),
        }


# Notes for extension:
# - Allow sport-specific metric sets via metric_config (e.g., football could use xG, shots, saves).
# - Persist baselines per player/team; consider time decay/recency weighting.
# - Calibrate thresholds per role or format (e.g., T20 vs ODI).
