# Cricket Anomaly Engine – Design Document

## 1. Overview

The Cricket Anomaly Engine (CAE) is an open-source system that detects unusual or unexpected patterns in cricket matches.
It consumes structured ball-by-ball or phase-level data, learns baselines for "normal" behavior, and produces anomaly
scores and human-readable explanations.

Examples of anomalies:
- Sudden batting slowdown or acceleration compared to expected run rates.
- Unusual clusters of wickets in a short span.
- Bowling spells that deviate strongly from a bowler's historical economy/strike metrics.
- Sharp shifts in momentum or win probability.

The system is designed to be:
- **Modular**: clear separation between data ingestion, baselines, models, and APIs.
- **Extensible**: easy to plug in new anomaly detectors and LLM-based explanation modules.
- **Production-minded**: clean configs, logging, testability, and clear API boundaries.

LLM integration is planned as a separate layer that consumes structured anomaly outputs and returns natural language
explanations. The initial versions will focus on deterministic, interpretable anomaly detection logic.

---

## 2. Goals and Non-Goals

### 2.1 Goals

- Provide a Python library and HTTP API to:
  - Ingest cricket match events in a structured format.
  - Compute baselines for expected behavior (e.g., expected runs/wickets per phase).
  - Score events or sequences with anomaly scores and labels.
- Offer clear, documented data schemas for:
  - Input events.
  - Anomaly outputs.
- Provide a minimal, working reference anomaly detector using simple statistics / classical ML.
- Provide a skeleton for future:
  - Historical training pipelines.
  - Multiple detectors (e.g., time-series, clustering).
  - LLM-based explanation and commentary.

### 2.2 Non-Goals (Initial Version)

- Building a fully accurate, production-grade predictive cricket model.
- Scraping and maintaining large external datasets.
- Real-time streaming integration (Kafka, Kinesis, etc.) in v0.1.
- Full web UI dashboards (beyond simple examples, if any).

---

## 3. Use Cases

1. **Developer / Analyst**:
   - Loads a historical dataset.
   - Computes baselines for a tournament, venue, or player.
   - Runs anomaly detection over a match to find unusual overs/phases.

2. **Live Analytics Prototype**:
   - Receives ball-by-ball events via an API.
   - Returns anomaly scores and explanations that can be visualized in a separate UI.

3. **LLM Explanation Layer (Future)**:
   - Takes anomaly outputs and match context.
   - Generates human-readable commentary:
     - "The run rate in overs 7–10 is significantly lower than expected given wickets in hand."

---

## 4. High-Level Architecture

Layers:

1. **Data Layer (`cae.data`)**
   - Input schemas and loaders (e.g., from CSV).
   - Baseline computation utilities (e.g., expected runs, wickets by phase/venue).

2. **Model Layer (`cae.models`)**
   - Core anomaly scoring logic.
   - Simple statistical detector (initial).
   - Future extension for ML-based detectors.

3. **API Layer (`cae.api`)**
   - FastAPI application exposing health and anomaly scoring endpoints.
   - Accepts JSON payloads defined via Pydantic models.

4. **Utils Layer (`cae.utils`)**
   - Logging.
   - Config handling.

5. **Docs/Tests**
   - `docs/` for design, roadmap, prompts.
   - `tests/` for basic sanity and regression tests.

---

## 5. Data Model

### 5.1 Input Event Schema

At minimum, the engine needs:

- `match_id`: string
- `over`: integer (1-based)
- `ball`: integer (1–6 for standard deliveries)
- `runs`: runs scored on this ball (including extras)
- `wickets`: wickets that fell on this ball (0/1 typically)
- `phase`: e.g., "POWERPLAY", "MIDDLE", "DEATH"
- `expected_runs`: expected runs for this ball/phase given baselines
- `expected_wickets`: expected wickets for this ball/phase given baselines

This can be extended later with:
- `venue`, `team`, `batsman`, `bowler`, `required_run_rate`, etc.

The first implementation will assume `expected_runs` and `expected_wickets` are already present, possibly computed offline
or via a placeholder baseline.

### 5.2 Anomaly Output Schema

For each event, the anomaly detector returns:

- `match_id`
- `over`
- `ball`
- `anomaly_score`: float (e.g., distance from baseline)
- `is_anomaly`: boolean
- `reason`: short human-readable explanation string

---

## 6. Baseline Computation (Initial Approach)

Baseline computation is separated into its own module to allow evolution:

- For v0.1:
  - Assume baselines can be constants or simple aggregates:
    - Average runs per ball in a given phase.
    - Average wickets per ball in a given phase.
  - Provide helper functions to compute these from a pandas DataFrame.

- Later:
  - Condition baselines on:
    - Venue.
    - Batting team, bowling team.
    - Bowler type (pace, spin).
    - Batter role (anchor, finisher).
  - Use grouping and feature engineering.

---

## 7. Anomaly Detection Logic (Initial Version)

The initial detector will be simple, interpretable, and easy to test:

- Compute differences:
  - `run_diff = runs - expected_runs`
  - `wicket_diff = wickets - expected_wickets`
- Use fixed or empirically estimated standard deviations for runs/wickets.
- Compute z-scores:
  - `z_run = run_diff / run_std`
  - `z_wicket = wicket_diff / wicket_std`
- Combine into a single anomaly score:
  - `score = sqrt(z_run^2 + z_wicket^2)`
- Mark anomaly if `score >= threshold` (e.g., 2.0).
- Default parameters in the reference implementation:
  - `run_std = 1.5`
  - `wicket_std = 0.25`
  - `threshold = 2.0`
- Generate a simple explanation string based on which components are large:
  - "runs much higher than expected"
  - "more wickets than expected"
  - etc.

This provides:
- A clear starting point.
- A consistent API for swapping in more complex detectors later.

---

## 8. API Design

### 8.1 Health Endpoint

- `GET /health`
- Response: `{ "status": "ok" }`

### 8.2 Scoring Endpoint

- `POST /score`
- Request:
  - JSON body containing a batch of events.
- Response:
  - JSON with a list of anomaly outputs for each event.

Example (simplified):

Request:
```json
{
  "events": [
    {
      "match_id": "MATCH123",
      "over": 10,
      "ball": 2,
      "runs": 6,
      "wickets": 0,
      "phase": "MIDDLE",
      "expected_runs": 3.5,
      "expected_wickets": 0.05
    }
  ]
}

```

Response:
```json
{
  "results": [
    {
      "match_id": "MATCH123",
      "over": 10,
      "ball": 2,
      "anomaly_score": 4.3,
      "is_anomaly": true,
      "reason": "runs higher than expected"
    }
  ]
}
```
