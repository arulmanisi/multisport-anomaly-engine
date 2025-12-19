You are my coding agent.
We are on Day 10 of the Cricket Anomaly Engine MVP.

Goal:
Create a TrainingEngine design that wires together:
- DataPipeline
- ModelWrapper
for anomaly-focused training and evaluation.

Requirements:

1. Define a TrainingEngine class with:
   - __init__(self, data_pipeline, model_wrapper, config)
   - run_training():
       * calls pipeline to get train/validation data
       * fits the model on train data
   - run_evaluation():
       * runs predictions on validation data
       * computes anomaly-relevant metrics (design only)
   - log_metrics():
       * placeholder for logging to console or external system.

2. Anomaly-aware evaluation design:
   - In docstrings or comments, mention:
       * precision and recall for anomalous cases
       * PR-AUC for anomaly detection
       * recall at fixed false positive rate
   - Only describe; do NOT implement the metrics.

3. Show input/output shapes at a high level:
   - e.g., X_train, y_train for UPS Score.
   - Flexibility for multiple labels later.

4. Keep everything library-agnostic and implementation-light:
   - Type hints
   - Docstrings
   - TODO comments

Return one Python module with TrainingEngine and related structures.
