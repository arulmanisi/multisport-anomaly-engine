# Technology Overview

This document summarizes the tech stack and component responsibilities for the Cricket Anomaly Engine.

## Stack
- Language: Python 3.10+
- API: FastAPI (+ Starlette)
- Data modeling: Pydantic v2
- Numerics: NumPy
- Dataframes: pandas
- HTTP server: Uvicorn
- Testing: Pytest

## Components
- `src/cae/api/app.py`
  - FastAPI app factory, routes for `/health` and `/score`.
  - Uses Pydantic request/response models for validation.
- `src/cae/data/schemas.py`
  - Pydantic models for input events, batch requests, and anomaly outputs.
- `src/cae/data/baseline.py`
  - Helpers to compute simple per-phase expected runs/wickets from dataframes.
- `src/cae/data/simulator.py`
  - Synthetic data generator for demos/tests; produces `EventInput` objects and dataframe helper.
- `src/cae/models/anomaly.py`
  - Z-score anomaly detector; configurable std devs and thresholds; human-readable reasons.
- `src/cae/models/predictor.py`
  - Bridges dataframes and scoring, validating required columns and returning results (objects or dataframe).
- `src/cae/models/pipeline.py`
  - End-to-end scoring helper that also persists results when a store is provided.
- `src/cae/utils/storage.py`
  - SQLite-backed persistence for anomaly results; fetches recent scores.
- `tests/`
  - Unit tests for scoring logic, API responses, and simulation/prediction pipeline.

## Why a z-score detector?
- Interpretability: z-scores show how many standard deviations an observation is from its expected value, which is easy to reason about and explain.
- Simplicity: minimal parameters (`run_std`, `wicket_std`, `threshold`) and no training loop; works immediately with provided baselines.
- Composability: runs/wickets are independent components; combining their z-scores via Euclidean norm yields a single score while preserving signal from each dimension.
- Baseline-friendly: pairs naturally with simple expected values (per-phase averages) and can be tightened later with context-specific std devs without changing the interface.
- Testability: deterministic math with clear thresholds makes for straightforward unit and API contract tests.

## Data Flow
1) Ingestion: API receives `BatchScoreRequest` with event payloads (or dataframes via predictor helper).
2) Validation: Pydantic ensures schema correctness and non-empty fields.
3) Scoring: `score_events` computes z-scores vs expected baselines and flags anomalies.
4) Response: Results returned as `BatchScoreResponse` or dataframe; reasoning strings describe deviations.

## Development Notes
- Set `PYTHONPATH=src` (or install as a package) when running tests or scripts.
- Run API locally: `uvicorn cae.api.app:app --reload`
- Run tests: `pytest`
- Defaults for detector: `run_std=1.5`, `wicket_std=0.25`, `threshold=2.0` (tune with data).

## Future Extensions
- Additional detectors (time-series, clustering) behind a common interface.
- Contextual baselines (venue, teams, bowler type) with persistence.
- Observability (metrics/logging) and CI/CD automation.
- LLM explanation layer consuming structured anomaly outputs.
