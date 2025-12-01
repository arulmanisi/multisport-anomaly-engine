# Roadmap
Living roadmap; update as priorities change.

## Near term (0-4 weeks)
- Finalize input/output schemas in `docs/design.md`; lock Pydantic models.
- Gather a small sample dataset (ball-by-ball CSV) and stub baseline expectations (`expected_runs`, `expected_wickets`).
- Implement/verify baseline calculators for per-phase averages; document assumptions.
- Harden z-score detector defaults with smoke tests on sample data; add API contract tests.
- Ship FastAPI service with `/health` and `/score`, containerize, and add a minimal CLI wrapper.
- Set up CI (lint + pytest) and basic publishing workflow (package metadata).

## Mid term (1-3 months)
- Enrich baselines with contextual features (venue, teams, bowler type); evaluate per-context thresholds.
- Add additional detectors (rolling-window time-series, simple clustering) behind a common interface.
- Introduce persistence for baselines and scored outputs (e.g., SQLite/Postgres) and retrieval APIs.
- Expand API surface (batch scoring file upload, metadata endpoints) and tighten validation/error handling.
- Add observability: structured logging, request metrics, and detector performance dashboards.
- Build feedback hooks for labeling anomalies (API + CLI), feeding an evaluation loop.

## Long term
- Integrate LLM-based explanation layer using structured anomaly outputs.
- Support streaming ingestion (Kafka/Kinesis) and backpressure-aware scoring.
- Optimize performance and cost (vectorized scoring, caching, parallelization).
- Produce SDK examples and integrations (dashboards, alerting tools, notebooks) for common user journeys.
