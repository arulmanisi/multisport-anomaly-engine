# Cricket Anomaly Engine

Open-source engine to detect unusual patterns in cricket matches. It consumes structured ball-by-ball/phase data, scores deviations from baselines, and exposes a FastAPI endpoint for scoring.

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
- Score: `POST http://localhost:8000/score`
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
