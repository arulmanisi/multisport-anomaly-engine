You are my coding agent.

I have just updated the UPSScorer implementation to compute UPS as a clipped positive z-score
based on recent player history, using the design we discussed.

Now I want to update or create pytest tests in test_ups_scorer.py so they validate the new semantics.

Please do the following:

1. Open or create tests/file: test_ups_scorer.py

2. Create a simple FakeHistoryProvider class inside the tests that:
   - For a given player_id and format, returns a fixed list of innings.
   - Example for player "P1", format "T20":
       runs: [20, 22, 25, 18, 30, 24, 21, 19, 23, 26]
     (consistent around ~22-24, with modest variance)

3. Write tests that cover:

   - test_compute_player_baseline_structure():
       * Instantiate UPSScorer with FakeHistoryProvider.
       * Call compute_player_baseline("P1", "T20").
       * Assert that mean_runs, std_runs, num_innings, and source are present and of correct types.

   - test_ups_score_increases_with_large_deviation():
       * Use same baseline.
       * Compute UPS for:
           current_runs = 25 (near baseline)
           current_runs = 60 (way above baseline)
       * Assert that UPS(60) > UPS(25), and UPS values are within [0, 5].

   - test_classify_ups_thresholds():
       * Manually call classify_ups() with UPS values like:
           0.5, 1.5, 2.5, 3.5
       * Assert correct buckets:
           0.5 -> "normal", flag=0
           1.5 -> "mild_spike", flag=0
           2.5 -> "strong_spike", flag=1
           3.5 -> "extreme_spike", flag=1

   - test_score_innings_integration():
       * Call score_innings("P1", "T20", current_runs=60).
       * Assert the result dict has expected keys:
           "ups_score", "ups_anomaly_flag", "ups_bucket",
           "baseline_mean_runs", "baseline_std_runs", "baseline_source".
       * Assert ups_score > 0 and ups_anomaly_flag in {0, 1}.

4. Keep tests deterministic:
   - Do not use randomness.
   - Do not rely on real data or external IO.

5. Use pytest style (simple functions).

After implementing/updating tests, show me the contents of test_ups_scorer.py.
