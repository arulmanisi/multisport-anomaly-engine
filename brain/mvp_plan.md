# Cricket Anomaly Engine – MVP Plan (3 Months)

This document defines the concrete plan to complete the MVP of the Cricket Anomaly Engine (CAE)
in ~3 months. It is written so that an AI coding assistant (e.g., Codex) can read and execute
on the tasks.

## 0. MVP Scope (Success Criteria)

The MVP is **done** when all of the following are true:

1. **Core anomaly engine**
   - Z-score–based anomaly scoring for cricket events (ball-level).
   - Uses expected runs/wickets and configurable std devs + threshold.
   - Returns anomaly_score, is_anomaly, and a human-readable reason.

2. **Baseline utilities**
   - Load event CSVs into pandas DataFrame.
   - Compute simple phase-level baselines (POWERPLAY, MIDDLE, DEATH, etc.).
   - Attach baselines (expected_runs, expected_wickets) to event rows.

3. **HTTP API (FastAPI)**
   - `/health` endpoint.
   - `/score` endpoint that takes a batch of events and returns anomalies.

4. **MVP dashboard (simple but usable)**
   - Upload a CSV with events.
   - Run anomaly scoring.
   - Show a table of events with anomaly flags.
   - Show a basic plot of anomaly_score over overs/balls.
   - Can be Streamlit or a simple web UI; Streamlit is acceptable for MVP.

5. **LLM narrative stub**
   - A module that takes anomaly outputs and generates a **placeholder** narrative.
   - For the MVP, this can be:
     - Rule-based text templates, OR
     - A simple call to an LLM API with a clear interface and a TODO for API key handling.
   - This module is **optional to call** from the dashboard but should exist and be demoable.

6. **Docs & examples**
   - `README.md` explains how to:
     - Install dependencies.
     - Run the API.
     - Run the dashboard.
     - Try a sample CSV.
   - `docs/design.md` and `docs/roadmap.md` reflect the actual implementation.
   - At least one example CSV + script/notebook showing end-to-end usage.

7. **Basic tests**
   - A few pytest tests:
     - Anomaly scoring sanity.
     - Baseline computation sanity.
     - API `/health` and `/score` work in a basic scenario.

If all of the above ship with clean code, the MVP is successful.

---

## 1. High-Level Timeline (12 Weeks)

- **Weeks 1–2**: Solidify repo skeleton, anomaly engine, basic tests.
- **Weeks 3–4**: Baseline computation & CSV pipeline.
- **Weeks 5–6**: API polish + better anomaly explanations + examples.
- **Weeks 7–9**: MVP dashboard (upload CSV → anomalies + plots).
- **Weeks 10–11**: LLM narrative stub, polish docs, sample flows.
- **Week 12**: Stabilization, refactor, harden tests, small UX tweaks.

This is flexible; the point is to have a clear progression.

---

## 2. Master Prompt for Codex (Use at the Start of Each Session)

Paste this into Codex whenever you open a new session:

```text
You are my coding assistant for the "Cricket Anomaly Engine (CAE)" project.

Goal:
- Complete the MVP defined in docs/mvp_plan.md.
- Follow the high-level design in docs/design.md.
- Keep code modular, tested, and easy to extend.

Tech stack:
- Python 3.10+
- FastAPI for HTTP API
- Pydantic for schemas
- Pandas & NumPy for data operations
- pytest for tests
- Streamlit (or similar) for MVP dashboard

Repo structure:
- Code in src/cae/
- Docs in docs/
- Tests in tests/
- Examples / sample data in examples/ or data/

Instructions:
- Before coding, read the relevant sections of docs/design.md and docs/mvp_plan.md.
- Respect existing module structure and public APIs unless explicitly updating the design.
- Use type hints and docstrings.
- When adding or changing behavior, update docs/design.md or docs/mvp_plan.md if needed.
- Keep changes incremental and self-contained; where possible, also add / update tests.

Now acknowledge that you understand the project structure and MVP scope
by summarizing what you see in docs/design.md and docs/mvp_plan.md,
then propose the next small set of tasks you will perform.
