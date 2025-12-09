# Multisport AI Engine (PLAIX)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

Open-source engine to detect unusual patterns in sports matches. PLAIX is a multi-sport anomaly and intelligence platform; it currently ships a cricket scorer and a football placeholder, with a structure to add more sports easily.

## Quick Start
- Install dependencies (Python 3.10+):
  ```bash
  pip install -r requirements.txt
  ```
- Generate synthetic UPS data:
  ```bash
  python backend/scripts/generate_synthetic_ups_data.py
  ```
- Train the UPS model (logistic regression):
  ```bash
  PYTHONPATH=backend/src python backend/scripts/train_ups_model.py
  ```
- Run end-to-end demo (UPS scoring + model inference):
  ```bash
  PYTHONPATH=backend/src python backend/scripts/run_end_to_end_demo.py
  ```

## PLAIX MVP (Day 1)
- Backend MVP for cricket anomaly detection (placeholder rule-based scoring).
- FastAPI service with `/health` and `/score` using `plaix` models.
- Pydantic models for inputs/outputs; pytest tests for health and scoring.

## Features
- Pydantic schemas for structured cricket events and anomaly outputs.
- Simple, interpretable z-score anomaly detector (runs/wickets vs expected).
- FastAPI service with `/health` and `/score` endpoints.
- Baseline helpers for per-phase aggregates (mean/median).
- Tests covering scoring logic and API responses.

## Quickstart
Requirements: Python 3.10+, `pip`, and virtualenv recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the API
```bash
uvicorn cae.api.app:app --reload

# PLAIX MVP app
uvicorn plaix.api.main:app --reload
```
- Health: `GET http://localhost:8000/health`
- Cricket-only (legacy): `POST http://localhost:8000/score`
- Multi-sport: `POST http://localhost:8000/plaix/score`
- Recent scores: `GET http://localhost:8000/recent`
- UI: open `http://localhost:8000/ui/` for a simple end-to-end prototype.

### Sample payloads
- Request example: `samples/score_request.json`
- Response example: `samples/score_response.json`

### Persistence
- Anomaly results are stored in a local SQLite database at `data/cae.db` (created on first run).
- `GET /recent` returns the latest scored events; the UI has a “Load recent” button wired to it.

## PLAIX Day 2 workflow
- Load events CSV: `plaix.data.loader.load_events_csv`
- Compute baselines and attach expected values: `plaix.data.baselines.compute_phase_baselines` and `attach_baselines`
- Score events via API or directly with `plaix.models.anomaly_scorer.score_events`
- Example script: `python examples/run_sample.py`

## Data Flow (CSV → Baselines → Scoring)
```python
from plaix.data.loader import load_events_csv
from plaix.data.baselines import compute_phase_baselines, attach_baselines
from plaix.models.anomaly_scorer import prepare_requests_from_df, score_events
from plaix.pipeline.events_pipeline import prepare_events_for_scoring

df = load_events_csv("path/to/events.csv")
baselines = compute_phase_baselines(df)
df_expected = attach_baselines(df, baselines)
requests = prepare_requests_from_df(df_expected)
results = score_events(requests)
anomalies = [r for r in results if r.is_anomaly]

# Or use the pipeline helper:
requests = prepare_events_for_scoring("data/plaix_sample_events.csv")
results = score_events(requests)
```
Sample CSV: `data/plaix_sample_events.csv`

## PLAIX Baselines Pipeline (Day 5)
1) Load CSV: `df = load_events_csv("data/plaix_sample_events.csv")`
2) Compute baselines: `baselines = compute_phase_baselines(df)`
3) Attach: `df_expected = attach_baselines(df, baselines)`
4) Build requests: `requests = prepare_requests_from_df(df_expected)`
5) Score: `results = score_events(requests)`
6) Handle missing expected values by running baseline attachment first; scorer will raise if they are absent.

## Multi-sport architecture
- `plaix.core`: sport-agnostic request/response models and a registry to dispatch by `sport`.
- `plaix.sports.cricket`: cricket event models and scoring logic (rule-based placeholder).
- `plaix.sports.football`: placeholder scorer returning non-anomalous results.
- API: `POST /plaix/score` expects `{"sport": "<sport>", "events": [...]}` and routes to the correct scorer. Unknown sports return HTTP 400.

### Add a new sport
1) Create `plaix/sports/<sport>/` with scorer that accepts `List[dict]` and returns `List[dict]`.
2) Define sport-specific schemas and baseline logic as needed.
3) Register the handler in `plaix.api.main` (via the core registry).
4) Add tests covering dispatch and sport-specific scoring.

## Running the Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Running the Streamlit UI
Set the API URL (defaults to http://localhost:8000/predict/single) and launch:
```bash
PLAIX_API_URL=http://localhost:8000/predict/single streamlit run ui/demo_streamlit/demo_ui.py
```
The UI will call the Plaix.ai backend and display UPS score, bucket, baseline flag, and model outputs.

## Architecture Overview
```mermaid
flowchart LR
    A[Raw Input (match/innings)] --> B[FeatureExtractor]
    B --> C[UPSScorer<br/>(baseline + UPS)]
    C --> D[Feature Vector<br/>(UPS + context)]
    D --> E[ModelWrapper<br/>(Logistic Regression)]
    E --> F[Anomaly Prediction<br/>(probability + label)]
    F --> G[CLI / REST Response]
```

## Feature extraction (cricket design)
- Core abstractions: `plaix.core.features.FeatureExtractor`, `FeatureExtractionInput`, `FeatureExtractionOutput`.
- Cricket structure: `plaix.sports.cricket.features.CricketFeatureExtractor` with buckets:
  - Match context features
  - Team-level features
  - Player-level features
  - Venue/weather features
- Placeholder methods (no implementation yet): `get_team_strength`, `get_player_form`, `compute_recent_performance_index`, `compute_venue_advantage`.

## Label creation (Day 7 design)
- Core: `plaix.core.labels.LabelRegistry`, `LabelRequest`, `LabelResponse`.
- Cricket labels via `plaix.sports.cricket.labels.LabelCreator`:
  - Baseline labels: `winner`, `run_margin` (future), `first_innings_score` (future)
  - Anomaly labels: `ups_score`, `bowling_spell_anomaly`, `batting_collapse_indicator`, `momentum_shift_score`, `contextual_upset_indicator`, `outlier_event_tag`
- Registry supports `register_label` and `get_label_output`; placeholder methods only, ready for future implementation.

## Data pipeline (Day 8 design)
- `plaix.core.pipeline.DataPipeline`: orchestrates loading, cleaning, feature extraction, label generation, dataset assembly, and train/validation split.
- Dependencies injected: data_loader, cleaner, feature_extractor (sport-specific), label_creator (sport-specific).
- Methods are structure/docstring/TODO only; anomaly-focused labels (e.g., UPS Score) called out for future logic.

## Model layer (Day 9 design)
- `plaix.core.model.AnomalyModel`: framework-agnostic wrapper with hooks for model_type/model_config and optional sport.
- Methods: `fit`, `predict`, `predict_proba`, `save_model`, `load_model` (all TODOs).
- Focused on anomaly labels (UPS Score and related anomaly tasks); no backend tied yet.

## Training engine (Day 10 design)
- `plaix.core.training.TrainingEngine`: wires DataPipeline and AnomalyModel for training/evaluation.
- Methods (design only): `run_training` (pipeline + fit), `run_evaluation` (predict + anomaly metrics like precision/recall, PR-AUC, recall@FPR), `log_metrics`.
- Shapes: expects X/y for anomaly labels (UPS Score, etc.), extensible to multi-label anomaly targets.

## CLI (Day 10 - CLI design)
- `src/plaix/cli.py`: tiny inference CLI skeleton.
- Commands:
  - `predict-single --input <json_or_path> --model <path>`
  - `predict-batch --input <path> --model <path>`
- Structure only: parses args, mocks model load, placeholder feature extraction, outputs UPS Score/is_anomalous placeholders.

## REST inference (Day 10 - REST design)
- `plaix.api.inference`: design-only FastAPI-style service.
- Endpoints (commented placeholders):
  - `POST /predict/single` → UPS Score + is_anomalous
  - `POST /predict/batch` → list of scores/flags
- `InferenceService` wires feature extractor and model loading (placeholders) with preprocess/run_inference/format_output hooks.

## Core anomaly logic (UPS Score design)
- `plaix.core.ups_scorer.UPSScorer`: computes UPS (Unexpected Performance Spike) from historical baselines and current performance.
- Methods: `compute_player_baseline`, `compute_match_performance`, `compute_ups_score`, `is_anomalous`, `score_player`.
- Uses z-score style deviation across runs/strike rate/wickets/economy (placeholders/assumptions); configurable per sport via metric_config.

## CLI Usage
Single prediction with precomputed baseline stats:
```bash
PYTHONPATH=backend/src python -m plaix.cli predict-single \
  --input '{"player_id":"P1","match_format":"T20","baseline_mean_runs":22,"baseline_std_runs":8,"current_runs":40,"venue_flatness":0.6,"opposition_strength":0.5,"batting_position":4}' \
  --model backend/models/ups_logreg.pkl
```
Sample output:
```
{
  "ups_score": 2.25,
  "ups_bucket": "strong_spike",
  "ups_anomaly_flag_baseline": 1,
  "model_anomaly_probability": 0.98,
  "model_anomaly_label": 1
}
```

## REST API Usage
Example (FastAPI-style inference service) `POST /predict/single`:
```bash
curl -X POST http://localhost:8000/predict/single \
  -H "Content-Type: application/json" \
  -d '{
        "payload": {
          "player_id": "P1",
          "match_format": "T20",
          "baseline_mean_runs": 22,
          "baseline_std_runs": 8,
          "current_runs": 40,
          "venue_flatness": 0.6,
          "opposition_strength": 0.5,
          "batting_position": 4
        }
      }'
```
Sample response:
```json
{
  "ups_score": 2.25,
  "ups_bucket": "strong_spike",
  "ups_anomaly_flag_baseline": 1,
  "model_anomaly_probability": 0.98,
  "model_anomaly_label": 1,
  "explanation": null
}
```

## Disclaimer

This project is fully open-source and uses only publicly available, synthetic,
or self-generated data. No enterprise, confidential, or proprietary data from
any employer (past or present) has been used in developing this project.

Example request:
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
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
      }'
```

Example response:
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

## Project layout
- `src/cae/` — library code
  - `api/app.py` — FastAPI app factory and routes
  - `data/schemas.py` — Pydantic models for requests/responses
  - `data/baseline.py` — simple per-phase baseline calculators
  - `models/anomaly.py` — z-score anomaly scorer
- `tests/` — unit and API tests
- `docs/design.md` — source-of-truth design document
- `docs/roadmap.md` — roadmap notes
- `brain/` — working prompts/design scratch space

## Development
- Run tests: `pytest`
- Lint/format: use your preferred tools (e.g., Ruff/Black); no config yet in repo.
- Update `docs/design.md` when changing APIs or detection logic; keep it the source of truth.

## Assumptions & next steps
- Baseline expectations (`expected_runs`, `expected_wickets`) are provided by the caller; extend `data/baseline.py` to compute richer baselines as data becomes available.
- Default detector parameters: `run_std=1.5`, `wicket_std=0.25`, `threshold=2.0`. Tune with real data.
- Future work: richer context features, multiple detectors, LLM explanations, CI/tooling.

## License
MIT (see repository if license file is added).
