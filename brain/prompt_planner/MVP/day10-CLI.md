You are my coding agent.
We are building a Cricket Anomaly Engine MVP.

Goal:
Design and implement a tiny CLI interface for running inference using the existing TrainingEngine / ModelWrapper stack.

Context:
- We already have (design-level) modules:
  * DataPipeline
  * ModelWrapper (anomaly-aware, UPS Score)
  * TrainingEngine
- Assume a trained model artifact is available on disk (e.g., model.pkl or similar), even if we only mock the loading.

Requirements:

1. Create a small CLI tool (e.g., cli.py) that supports commands like:
   - predict-single: run anomaly scoring for a single match or player input
   - predict-batch: run anomaly scoring for a batch file (e.g., JSON/CSV)

2. The CLI should:
   - Parse arguments (e.g., using argparse or similar)
   - Load or construct:
       * FeatureExtractor
       * LabelCreator (if needed for derived info)
       * ModelWrapper (and load model from path)
   - Accept input as:
       * JSON string or JSON file path
       * For batch mode: path to structured data

3. Focus on structure and interface:
   - Provide function and class signatures
   - Add docstrings and TODOs
   - Minimal or mock implementation for:
       * model loading
       * feature extraction
       * prediction

4. Make it anomaly-focused:
   - Primary output: UPS Score (Unexpected Performance Spike)
   - The CLI output should clearly print:
       * UPS Score
       * Any anomaly flags (e.g., is_anomalous = True/False)

5. Keep it simple and production-lean:
   - No heavy error handling needed, just the skeleton
   - Use clean separation:
       * main()
       * helper functions for loading model, parsing input, running inference

Return a complete Python module for the CLI, focusing on structure and flow with TODO comments where real logic goes.
