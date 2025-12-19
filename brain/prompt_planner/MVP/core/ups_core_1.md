You are my coding agent.

We are implementing the core anomaly logic for the Cricket Anomaly Engine MVP.

Goal:
Implement the UPSScorer so it can compute a UPS (Unexpected Performance Spike) score for a player’s batting innings, based on their recent history in the same format.

Use this design:

- Event: one player batting innings.
- For MVP, UPS is based only on runs_scored.
- History is per-player, per-format (e.g., "T20", "ODI", "TEST").
- Use at most the last N = 10 innings for the baseline.
- Require at least min_history = 5 innings for a player-specific baseline.
- If fewer than min_history innings exist for the player+format:
    * Fallback to team-role baseline (TODO stub for now).
    * If not available, fallback to global-role baseline (TODO stub).
    * If still nothing, use a default baseline: mean_runs = 20.0, std_runs = 15.0, source="default".
- Use exponential decay for recency weighting:
    * index i = 0 for most recent, 1 for previous, ...
    * weight w_i = exp(-lambda * i) with lambda = 0.3 (configurable).
- Compute weighted mean μ and std dev σ over runs_scored.
- Use sigma_eff = max(σ, sigma_min) with sigma_min = 5.0 by default (configurable).
- UPS = clipped positive z-score:
    * z = (current_runs - μ) / sigma_eff
    * z_pos = max(z, 0.0)
    * ups_score = min(z_pos, 5.0)   # so UPS ∈ [0, 5]

- Map UPS to buckets and flag:
    * UPS < 1.0        -> bucket="normal",         flag=0
    * 1.0 ≤ UPS < 2.0  -> bucket="mild_spike",     flag=0
    * 2.0 ≤ UPS < 3.0  -> bucket="strong_spike",   flag=1
    * UPS ≥ 3.0        -> bucket="extreme_spike",  flag=1

Implementation requirements:

1. In the `ups_scorer.py` module (or existing UPSScorer module), implement a `UPSScorer` class:

   - __init__(
        self,
        history_provider,
        window_size: int = 10,
        min_history: int = 5,
        decay_lambda: float = 0.3,
        sigma_min: float = 5.0,
     )

   - A small BaselineStats dataclass or TypedDict, with:
        * mean_runs: float
        * std_runs: float
        * num_innings: int
        * source: str   # "player", "team_role", "global_role", "default"

2. Assume there is a `history_provider` with this interface (protocol):

   - get_player_innings_history(player_id: str, match_format: str) -> list[dict]
     Each dict should include at least:
       * "runs_scored": int or float

   For now, team-role and global-role baselines are not implemented:
   - Create stub methods:
       * get_team_role_baseline(...)
       * get_global_role_baseline(...)
     returning None with TODO docstrings explaining what they will do later.

3. Implement methods on UPSScorer:

   - compute_player_baseline(
         self,
         player_id: str,
         match_format: str
     ) -> BaselineStats

     * Fetch history using history_provider.
     * If >= min_history innings:
         - Take up to last window_size innings.
         - Apply exponential weights.
         - Compute weighted mean and std dev.
         - Return BaselineStats with source="player".
     * Otherwise:
         - Try team/global role baseline (stubbed for now).
         - If still nothing, return defaults:
               mean_runs = 20.0, std_runs = 15.0, num_innings=0, source="default"

   - compute_ups_score(
         self,
         player_id: str,
         match_format: str,
         current_runs: float
     ) -> float

     * Call compute_player_baseline to get μ and σ.
     * Compute z, z_pos, and clipped UPS as above.
     * Return UPS (float in [0, 5]).

   - classify_ups(self, ups_score: float) -> tuple[int, str]
     * Returns (ups_anomaly_flag, bucket_string) using the thresholds above.

   - score_innings(
         self,
         player_id: str,
         match_format: str,
         current_runs: float
     ) -> dict

     * Calls compute_player_baseline + compute_ups_score + classify_ups.
     * Returns a dict:
         {
           "ups_score": float,
           "ups_anomaly_flag": int,
           "ups_bucket": str,
           "baseline_mean_runs": float,
           "baseline_std_runs": float,
           "baseline_source": str,
         }

4. Use Python 3.10+ type hints, add clear docstrings that explain the math in plain language, and leave explicit TODOs where real team/global-role logic would plug in.

After implementing, show me the final UPSScorer class.