You are the coding assistant for the PLAIX MVP.
Your job is to read the existing repository and continue building the MVP according to the design plan.

✅ Project Summary

PLAIX is a multi-sport AI anomaly detection engine.
The MVP includes:

A baseline rule-based anomaly scorer

A FastAPI /score endpoint

Pydantic models

Tests for basic scoring and health

A clean Python package: src/plaix/

You should extend functionality while keeping:

Code modular

Functions pure when possible

Models expressive

Tests updated for every new behavior

Documentation consistent

🔧 Current Components (already completed)

src/plaix/api/main.py → FastAPI app with /health and /score

src/plaix/models/anomaly_scorer.py → placeholder scorer

src/plaix/config.py → placeholder config

src/plaix/utils/logger.py → basic logger

Tests for health and scoring

Requirements updated

README updated

Scaffolding complete

🎯 Your Tasks (Next Steps for MVP)
1. Create the CSV Loading + Baseline Framework

Add new modules under src/plaix/data/:

loader.py

Function: load_events_csv(path) -> pd.DataFrame

Validate columns: match_id, over, ball, runs, wickets, phase

baselines.py

Function: compute_phase_baselines(df) -> pd.DataFrame

Group by phase

Compute mean runs/wickets

Function: attach_baselines(df, baselines) -> pd.DataFrame

Update scorer to optionally use expected_runs / expected_wickets if available.

Add tests:

tests/test_loader.py

tests/test_baselines.py

2. Improve the Anomaly Scorer

Enhance the placeholder rule-based scorer:

Add configurable thresholds via plaix.config

Add anomaly_score range documentation

Return richer anomaly metadata (e.g., “reason” strings)

Add tests updating expected behavior.

3. Add an Examples Directory

Create:

examples/run_sample.py

Which:

Loads a sample CSV

Attaches baselines

Converts to AnomalyRequest

Calls score_events()

Prints anomalies

4. Update README with the new workflow