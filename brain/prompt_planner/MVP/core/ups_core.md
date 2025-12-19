You are my coding agent.

I already have a UPSScorer skeleton in this project for the Cricket Anomaly Engine MVP.  
Now I want to implement the core baseline and UPS logic in a clear, well-documented way.

Goal:
Implement UPSScorer so that it can compute a per-player batting UPS score for one innings, based on recent history in the same format.

Please do the following, updating the existing UPSScorer module (or creating it if needed):

--------------------------------------------------
1) Design assumptions (encode these into docstrings)
--------------------------------------------------
- Event: one player batting innings.
- For MVP, UPS is defined only on "runs_scored".
- History is per-player, per-format (e.g., "T20", "ODI", "TEST").
- Use at most the last N = 10 innings for the baseline.
- Require at least min_history = 5 innings for a player-specific baseline.
- If fewer than min_history innings exist for the player+format:
    - Fallback to team-role baseline (if available).
    - Otherwise fallback to global-role baseline (if available).
    - Otherwise use a format-specific default baseline (e.g., μ=20, σ=15 for T20).
- Use exponential decay weights for recency:
    - index i = 0 for most recent, 1 for previous, etc.
    - weight w_i = exp(-lambda * i) with lambda = 0.3 (configurable).
- Compute a weighted mean μ and std dev σ over runs_scored.
- Use sigma_eff = max(σ, sigma_min) to avoid division by tiny sigma.
    - Use sigma_min = 5.0 by default (configurable).

- UPS is defined as a clipped positive z-score:
    - z = (current_runs - μ) / sigma_eff
    - z_pos = max(z, 0.0)
    - ups_score = min(z_pos, 5.0)   # So UPS ∈ [0, 5]

- Map UPS to anomaly buckets:
    - UPS < 1.0          -> "normal", ups_anomaly_flag = 0
    - 1.0 ≤ UPS < 2.0    -> "mild_spike", ups_anomaly_flag = 0
    - 2.0 ≤ UPS < 3.0    -> "strong_spike", ups_anomaly_flag = 1
    - UPS ≥ 3.0          -> "extreme_spike", ups_anomaly_flag = 1

--------------------------------------------------
2) Implement UPSScorer class
--------------------------------------------------
- The class should be initialized with a configuration object or kwargs for:
    - N (window_size)
    - min_history
    - lambda (decay)
    - sigma_min
- It should depend on an injected "history_provider" that can return batting histories.

Define a simple protocol / interface for history_provider:
- get_player_innings_history(player_id: str, match_format: str) -> list[dict]
  where each dict contains at least:
    - "runs_scored": int
    - "timestamp" or "sequence" (optional, but you can assume list is sorted most recent first)

For now, you can assume team-role and global-role baselines are not implemented:
- Leave TODOs and provide methods:
    - get_team_role_baseline(...)
    - get_global_role_baseline(...)
  that currently just return None, with docstrings explaining their intended behavior.

--------------------------------------------------
3) Methods to implement
--------------------------------------------------
Implement the following methods with type hints and rich docstrings:

- compute_player_baseline(player_id: str, match_format: str) -> BaselineStats:
    - Fetch history from history_provider.
    - If enough innings (>= min_history):
        * Use up to the last N innings.
        * Apply exponential weights.
        * Return mean_runs, std_runs, num_innings, source="player".
    - Else:
        * Try team-role and global-role baselines (for now they can be TODOs or defaults).
        * If nothing else, return a default baseline:
              mean_runs = 20.0, std_runs = 15.0, source="default"
          (you can vary defaults per format if you want, but keep it simple).

- compute_ups_score(
      player_id: str,
      match_format: str,
      current_runs: float
  ) -> float:
    - Call compute_player_baseline to get μ and σ.
    - Compute z, z_pos, and clipped UPS as described above.
    - Return the UPS score (float in [0, 5]).

- classify_ups(ups_score: float) -> tuple[bool, str]:
    - Return (ups_anomaly_flag, bucket_string) according to the thresholds:
        * normal / mild_spike / strong_spike / extreme_spike

- score_innings(
      player_id: str,
      match_format: str,
      current_runs: float
  ) -> dict:
    - Convenience wrapper that:
        * computes UPS
        * classifies it
        * returns a dict with:
            {
              "ups_score": float,
              "ups_anomaly_flag": int,
              "ups_bucket": str,
              "baseline_mean_runs": float,
              "baseline_std_runs": float,
              "baseline_source": str,
            }

--------------------------------------------------
4) Implementation style
--------------------------------------------------
- Use Python 3.10+ type hints.
- Consider using a small dataclass or TypedDict for BaselineStats.
- Add docstrings that explain the math in plain English.
- Keep the code self-contained and testable.
- Leave clear TODOs where real data / team-role baselines would need to be plugged in.

After making these changes, show me the updated UPSScorer module.
