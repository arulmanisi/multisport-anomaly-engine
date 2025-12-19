You are my coding assistant for a project called **PLAIX** (plaix.ai).

## Product context

PLAIX is an AI-driven sports intelligence platform.  
MVP focus: **cricket anomaly detection** – an engine that ingests structured cricket events and flags unusual / anomalous behavior (sudden slowdowns, wicket clusters, abnormal overs, etc.) with simple, interpretable logic.

Long-term, PLAIX will support:
- Multiple sports
- Real-time dashboards
- LLM-based explanations

Right now, we are building only the **backend MVP**:
- Core anomaly scoring engine
- Simple baselines
- HTTP API
- Basic tests

## Tech stack

Use:

- Python 3.10+
- FastAPI for the HTTP API
- Pydantic for request/response models
- pandas & numpy for data handling
- pytest for tests
- (Streamlit or similar for a simple dashboard will come later, not today)

## Repository structure

If the repo is empty or incomplete, you should create / extend it into something like:

- README.md
- requirements.txt
- src/
  - plaix/
    - __init__.py
    - config.py
    - utils/
      - logger.py
    - data/
      - __init__.py
      - loader.py
      - baselines.py
    - models/
      - __init__.py
      - anomaly_scorer.py
    - api/
      - __init__.py
      - main.py
- tests/
  - test_health.py
  - test_anomaly_scorer.py
- docs/
  - design.md
  - mvp_plan.md  (high-level checklist for the MVP)

## Design constraints

- Code must be modular and clean.
- Use type hints everywhere.
- Add concise docstrings for public functions and classes.
- Don’t introduce heavy ML libraries yet; start with simple statistical logic (e.g., z-score style).
- We want something that’s easy to extend later with more advanced detectors and an LLM explanation layer.

## Day 1 goal

For **Day 1**, I want you to:

1. **Scaffold the project** (if not already done):
   - Create the `src/plaix/` package with the submodules listed above.
   - Add `requirements.txt` with at least: fastapi, uvicorn[standard], pydantic, pandas, numpy, pytest.
   - Add a minimal `README.md` that explains:
     - What PLAIX is (1–2 paragraphs, cricket anomaly MVP).
     - How to install dependencies.
     - How to run the API.

2. **Implement a minimal FastAPI app**:
   - In `src/plaix/api/main.py`, create a FastAPI app with:
     - `GET /health` → returns `{ "status": "ok", "service": "plaix" }`
   - Add a basic `uvicorn` command example to the README for running the service.

3. **Set up basic logging**:
   - In `src/plaix/utils/logger.py`, implement a `get_logger(name: str) -> logging.Logger` helper with a simple, consistent format.

4. **Set up a placeholder anomaly scorer**:
   - In `src/plaix/models/anomaly_scorer.py`, define:
     - A Pydantic model `AnomalyRequest` with minimal fields:
       - match_id: str
       - over: int
       - ball: int
       - runs: float
       - wickets: float
     - A Pydantic model `AnomalyResponse` with:
       - match_id, over, ball
       - anomaly_score: float
       - is_anomaly: bool
       - reason: str
     - A function `score_event(event: AnomalyRequest) -> AnomalyResponse` that:
       - For now, uses a trivial rule:
         - If runs >= 6 or wickets >= 1 → mark as anomalous with a simple reason.
         - Otherwise, non-anomalous.
       - This is just a placeholder; we will replace it with a proper baseline/z-score logic later.

5. **Wire the scorer to the API**:
   - In `src/plaix/api/main.py`, add:
     - A `POST /score` endpoint that accepts a batch of `AnomalyRequest` objects and returns a list of `AnomalyResponse` objects.
   - Keep models and logic in `plaix.models.anomaly_scorer`; the API layer should just orchestrate.

6. **Add basic tests**:
   - In `tests/test_health.py`, add a test using FastAPI’s `TestClient` to check that `/health` returns status=ok.
   - In `tests/test_anomaly_scorer.py`, add at least one test:
     - A clearly non-anomalous event.
     - A clearly anomalous event (e.g., a 6 or a wicket).
     - Assert `is_anomaly` and `reason` behave as expected.

## How I want you to work

- First, scan the current repo and summarize what already exists.
- Then propose a short plan (3–5 bullet points) for the edits you’re about to make to achieve the Day 1 goal.
- After that, generate the concrete file contents or diffs needed.
- Keep changes incremental and consistent with the structure above.

Start now by:
1. Describing what files you see and what’s missing for the Day 1 goal.
2. Then implement the required files and code step by step.
