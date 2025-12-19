You are my coding agent.

Now that UPSScorer is implemented, I want to generate a small synthetic dataset for training a simple anomaly model.

Goal:
Create a Python script that generates a synthetic UPS training dataset and saves it as a CSV (e.g., data/synthetic_ups_dataset.csv).

Requirements:

1. Create a script, e.g., scripts/generate_synthetic_ups_data.py

2. The script should:
   - Import numpy and pandas.
   - Simulate synthetic players and innings without any external data.

3. Dataset schema (each row represents one innings):

   - player_id: str
   - match_format: str           # e.g., "T20"
   - baseline_mean_runs: float
   - baseline_std_runs: float
   - current_runs: float
   - ups_score: float            # approximated via simple formula inside script
   - ups_anomaly_flag: int       # 0 or 1
   - ups_bucket: str
   - optional simple context fields:
       * venue_flatness: float   # 0–1 (flatter pitch => more runs)
       * opposition_strength: float  # 0–1
       * batting_position: int   # 1–7

4. Synthetic generation logic (simple and self-contained):

   - For, say, 100–200 rows:
       * Sample baseline_mean_runs from something like N(22, 8) but clipped to [5, 60].
       * Sample baseline_std_runs from [5, 20].
       * Generate current_runs like:
            current_runs = baseline_mean_runs + epsilon
         where epsilon is:
            - mostly modest (e.g., N(0, baseline_std_runs))
            - occasionally large positive spikes to simulate anomalies.
       * Approximate UPS as:
            ups_score = max(0, (current_runs - baseline_mean_runs) / max(baseline_std_runs, 5.0))
            and clip to [0, 5].
       * Derive ups_bucket and ups_anomaly_flag from the same thresholds as UPSScorer.

5. Save the dataset to data/synthetic_ups_dataset.csv with a header row.

6. The script should be runnable as:
   python scripts/generate_synthetic_ups_data.py

After implementation, show me the script and a preview (head) of the generated DataFrame.
