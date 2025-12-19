You are my coding agent.

Now I want a simple end-to-end smoke script to prove the full MVP pipeline works.

Goal:
Create a script that:
1) Generates synthetic data (or assumes it already exists),
2) Trains the model (or detects existing model),
3) Runs one sample prediction through the UPSScorer + ModelWrapper,
4) Prints the final anomaly output.

Requirements:

1. Create a script, e.g., scripts/run_end_to_end_demo.py

2. The script should:
   - Option 1: Call the existing scripts programmatically:
       * generate_synthetic_ups_data.main()
       * train_ups_model.main()
   - Or Option 2: Assume data/model exists and just proceed.

   - Construct a sample input representing one innings, e.g.:
       player_id = "P_DEMO"
       match_format = "T20"
       baseline_mean_runs = 22.0
       baseline_std_runs = 8.0
       current_runs = 60.0
       venue_flatness = 0.7
       opposition_strength = 0.6
       batting_position = 3

   - Use UPSScorer to compute:
       * ups_score
       * ups_bucket
       * ups_anomaly_flag_baseline

   - Build the same feature vector used during training and call:
       * ModelWrapper.load_model(model_path)
       * model.predict_proba(features) or model.predict(features)

   - Print a final, human-readable summary, for example:

       Player: P_DEMO (T20)
       Baseline mean runs: ...
       Current runs: ...
       UPS Score: ...
       UPS Bucket: ...
       Baseline anomaly flag: ...
       Model anomaly probability: ...
       Model anomaly label: ...

3. Keep the script simple and robust enough to run with:
   python scripts/run_end_to_end_demo.py

After creating the script, show me its contents and a sample output from running it.
