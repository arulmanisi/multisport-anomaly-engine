You are my coding agent.
We are on Day 9 of the Cricket Anomaly Engine MVP.

Goal:
Create a model architecture layer (design only) for anomaly-focused prediction.

Requirements:

1. Create a ModelWrapper (or AnomalyModel) class that:
   - Is initialized with:
       * model_type (e.g., "random_forest", "gradient_boosting", "isolation_forest")
       * model_config (hyperparameters as a dict)
   - Provides methods:
       * fit(X, y)
       * predict(X)
       * predict_proba(X) [where applicable]
       * save_model(path)
       * load_model(path)

2. Make the design anomaly-aware:
   - Primary target: UPS Score (Unexpected Performance Spike).
   - Support for:
       * binary anomaly labels
       * score-based anomaly labels
   - Add docstrings describing how this relates to anomaly detection rather than simple win prediction.

3. Keep it framework-agnostic:
   - Do NOT commit to a specific library (e.g., sklearn, xgboost).
   - Use placeholders / TODOs where actual libraries would go.

4. Add hooks for multi-sport usage:
   - E.g., allow a "task_type" or "sport" field in the config.

5. Do NOT implement full ML logic.
   - Focus on clean abstractions, type hints, and docstrings.
   - Include notes on how to extend with additional model backends later.

Return a single Python module with the model wrapper design only.
