You are my coding agent.
We are building a Cricket Anomaly Engine MVP.

Goal:
Design a tiny REST-style inference service for anomaly scoring, using the existing ModelWrapper / TrainingEngine concepts.

Context:
- We have:
  * FeatureExtractor (design)
  * LabelCreator with anomaly labels (UPS Score, etc.)
  * DataPipeline, ModelWrapper, TrainingEngine designs
- We want a minimal REST API to expose inference/prediction.

Requirements:

1. Use a lightweight Python web framework (you can assume FastAPI for the structure, but keep real imports minimal and mark as TODO if needed).

2. Define endpoints such as:
   - POST /predict/single
       * Input: JSON with match/player context
       * Output: UPS Score and anomaly flags
   - POST /predict/batch
       * Input: list of JSON records
       * Output: list of scores / anomaly indicators

3. Design an InferenceService or similar class that:
   - On startup:
       * Loads or constructs FeatureExtractor
       * Loads ModelWrapper and model weights from a path
   - Exposes methods used by the API handlers:
       * preprocess_input()
       * run_inference()
       * format_output()

4. Focus on API and structure:
   - Use Pydantic-style request/response models (even if only as placeholders with TODOs).
   - Add docstrings to each endpoint explaining:
       * what it expects
       * what it returns
       * how it relates to UPS Score anomaly detection.

5. Keep the service anomaly-centric:
   - Primary output should revolve around:
       * UPS Score (numeric)
       * is_anomalous flag
       * optional explanation placeholders (e.g., “top contributing features” TODO)

6. Avoid full implementation:
   - Do not actually code ML logic.
   - Use placeholders and TODO comments for:
       * real model loading
       * feature extraction
       * prediction logic

Return one Python module that represents a small REST API service, ready to be filled in later.
