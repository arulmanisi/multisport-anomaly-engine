You are my coding agent.
We are working on the core anomaly logic for the Cricket Anomaly Engine MVP.

Goal:
Define how UPS Score (Unexpected Performance Spike) is actually computed, and implement a clean, extensible design for it.

Context:
- UPS Score is our primary anomaly label.
- It should represent how much a player or team performance in a given match deviates from their historical baseline.
- We want a design that can later be reused for other sports.

Requirements:

1. Create a module (e.g., ups_scorer.py) that defines:
   - A UPSScorer class responsible for:
       * loading or being initialized with historical stats
       * computing expected performance baseline
       * computing an anomaly score for a new performance

2. Focus on the design of the logic:
   - Define what “baseline” means in code terms:
       * e.g., rolling averages over last N innings or matches
       * per-player metrics like:
           - average runs
           - strike rate
           - wickets per match
           - economy
   - Define what “spike” means:
       * deviation from baseline in standardized form (e.g., z-score)
       * thresholds for turning it into a binary anomaly flag

3. Implement high-level method signatures such as:
   - compute_player_baseline(player_history) -> dict
   - compute_match_performance(current_match_stats) -> dict
   - compute_ups_score(player_baseline, current_performance) -> float
   - is_anomalous(ups_score, threshold) -> bool

4. Include detailed docstrings explaining:
   - The conceptual math (e.g., z-score, normalized deviation)
   - Examples in comments (e.g., player usually scores 25 runs, now scores 70 -> high UPS).

5. Keep implementation partial but meaningful:
   - You can outline simple formulas or pseudocode-like logic.
   - Where actual data structures are unknown, use TODOs and type hints.

6. Make the design sport-extensible:
   - Allow UPSScorer to accept a “sport” or “metric_config” so that:
       * cricket uses runs, strike rate, wickets, economy
       * another sport could plug in its own metrics later.

Return a single Python module with the UPSScorer design, partial implementation of formulas, and clear TODOs for real data integration.
