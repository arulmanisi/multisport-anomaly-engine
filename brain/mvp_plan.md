# MVP Plan

Scope: deliver a minimal, working anomaly scoring service with a demo UI and persistence.

## Goals
- Ingest ball-by-ball/phase events via HTTP.
- Score anomalies using simple z-scores against provided baselines.
- Store recent results and expose them via API/UI.
- Provide sample payloads and docs for quick adoption.

## Deliverables
- FastAPI service with `/health`, `/score`, and `/recent`.
- Pydantic models for inputs/outputs; z-score detector wired end-to-end.
- SQLite persistence for scored results.
- Demo UI served from `/ui/` to submit payloads and view recent scores.
- Sample request/response JSON; README + tech overview.
- Tests for scoring, persistence, and API contracts.

## Constraints
- Keep logic deterministic; no external data fetches.
- Python 3.10+, use current stack (FastAPI, Pydantic v2, pandas/NumPy).
- Avoid breaking public APIs without updating docs.

## Milestones
- M1: Core scoring path
  - Finalize schemas; implement z-score detector; add unit tests.
- M2: API & docs
  - Expose `/score` and `/health`; update README/docs with usage and samples.
- M3: Persistence & UI
  - Add SQLite-backed storage and `/recent`; wire UI to `/score` and `/recent`.
- M4: Polish
  - CI/tests green; add linting config; refine docs; containerization (optional).

## Risks / Open Questions
- Baseline quality: currently caller-provided; may need richer baseline computation.
- Threshold tuning: defaults may be too lax/strict; add config surface if needed.
- Data shape: extending schemas (venue/teams) could require versioning; document changes.

## Next Steps
- Add configuration for detector params (env or settings file).
- Add containerization and simple deployment script.
- Expand baselines (phase+venue/team) and include example datasets.
