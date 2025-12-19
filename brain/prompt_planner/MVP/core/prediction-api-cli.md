You are my coding agent.

I now have:
- UPSScorer implemented.
- A synthetic dataset.
- A trained Logistic Regression anomaly model saved as models/ups_logreg.pkl via ModelWrapper.

Goal:
Wire the trained model and UPSScorer into the CLI and REST API so that both surfaces produce real anomaly predictions.

Requirements:

1. CLI (e.g., cli.py):
   - Ensure it:
       * Loads the trained model via ModelWrapper.load_model("models/ups_logreg.pkl").
       * Constructs or receives a history_provider (you can stub this with simple fake history for now, or assume current baseline stats are provided directly in the input).
       * Uses UPSScorer to compute:
            - ups_score
            - ups_bucket
            - ups_anomaly_flag (baseline rule)
       * Builds a feature vector consistent with training-time features.
       * Calls ModelWrapper.predict_proba() or predict() to get model-based anomaly probability or label.
       * Prints a structured output, e.g.:
            UPS Score: X
            UPS Bucket: Y
            Baseline Anomaly Flag: Z
            Model Anomaly Probability: P

   - Support at least predict-single from a small JSON-like input (file or CLI).

2. REST API (FastAPI-style service):
   - In the app startup:
       * Load UPSScorer (with a simple or stub history provider).
       * Load the ModelWrapper and the trained model file.
   - For POST /predict/single:
       * Accept JSON with minimal fields needed (e.g., baseline stats + current_runs + simple context).
       * Use UPSScorer to compute UPS features.
       * Build the same feature vector used in training.
       * Get model probability/label from ModelWrapper.
       * Return a JSON response with:
           {
             "ups_score": ...,
             "ups_bucket": ...,
             "ups_anomaly_flag_baseline": ...,
             "model_anomaly_probability": ...,
             "model_anomaly_label": ...
           }

3. Keep history_provider realistic but simple:
   - For now, you can:
       * Use dummy or inline histories, or
       * Allow the request to carry baseline stats directly and bypass history lookup, with a clear TODO.

4. Update tests for CLI and REST only if necessary to handle the new outputs (but you can keep them mostly structural).

After changes, show me:
- The updated CLI module
- The updated REST API module
- An example of a sample input + sample output for a single prediction.
