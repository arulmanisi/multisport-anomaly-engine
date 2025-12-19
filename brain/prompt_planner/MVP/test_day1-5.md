You are my coding assistant for the "PLAIX" project.

Goal:
- Write and/or improve pytest-based tests that cover everything implemented in the PLAIX MVP from Day 1–5.

Context:
- Code lives under src/plaix/.
- Tests live under tests/.
- We already have:
  - A FastAPI app (PLAIX service) with at least /health and /score endpoints.
  - An anomaly scoring module with AnomalyRequest/AnomalyResponse and score_event/score_events implementations (initially rule-based, now possibly evolved).
  - Basic tests: tests/test_health.py and tests/test_anomaly_scorer.py (or similar), which verify health and a couple of anomaly vs non-anomaly cases.
- By Day 5, we’ve added more functionality (e.g., additional models, data utilities, config modules, etc.). Your job is to inspect the codebase and write tests that give us broad, meaningful coverage for everything implemented so far, without overfitting to implementation details.

Tasks:

1. Scan the repo
   - Read src/plaix/ and tests/ to understand:
     - What public functions, classes, and endpoints exist.
     - What is already tested.
   - Do NOT delete any existing tests; extend and complement them.

2. Design a test plan
   - Identify each module / public surface that should have tests, for example (adapt this to the actual codebase):
     - plaix.api.main: /health and /score endpoints
     - plaix.models.anomaly_scorer: score_event, score_events, Pydantic models
     - plaix.config: any configuration objects / factories
     - plaix.utils.logger: logger creation
     - Any data/loader/baseline utilities implemented by Day 5
   - For each module, decide what behavior needs to be verified (not private details).

3. Implement or improve tests module-by-module
   - Create or update test files under tests/, following a clear naming pattern, e.g.:
     - tests/test_health.py              → health and basic service metadata
     - tests/test_api_score.py           → /score endpoint behavior
     - tests/test_anomaly_scorer.py      → anomaly scoring logic
     - tests/test_config.py              → config defaults and overrides (if applicable)
     - tests/test_utils_logger.py        → logger behavior (singleton-ish, formatting)
     - tests/test_data_*.py              → any loader/baseline helpers if they exist
   - Use pytest style tests (functions, not unittest classes), unless something in the repo already uses a different style.

4. Concrete testing expectations
   For each test area, implement tests similar to the following (adapt to actual code):

   - Health endpoint:
     - Assert status code 200.
     - Assert JSON includes status="ok" and service name is "plaix" (or whatever is defined).
   
   - /score endpoint:
     - Happy path: valid batch of events returns 200 and a list of results with expected fields.
     - Edge cases:
       - Empty events list → decide expected behavior and assert it.
       - Invalid payload → assert 422 or appropriate validation error.
       - Single event vs multiple events.

   - Anomaly scorer:
     - Normal event → anomaly_score >= 0 and is_anomaly == False in a clearly normal scenario.
     - Clearly anomalous event (e.g., extreme runs/wickets) → is_anomaly == True and reason is non-empty and meaningful.
     - Verify that the Pydantic models validate input correctly and reject invalid data (e.g., missing required fields, wrong types).
     - If there is any config-driven threshold, test behavior just below and just above the threshold.

   - Config module:
     - Verify default config values (thresholds, std devs, etc.).
     - If there is any helper like get_default_config(), assert it returns the expected type and values.

   - Logger utils:
     - Call get_logger() multiple times with the same name and ensure it doesn’t add duplicate handlers.
     - Optionally assert log level or format if feasible without brittle string matching.

   - Data utilities (if present by Day 5):
     - Loader:
       - Given a small CSV from a temp file, ensure DataFrame columns match expectations.
       - Handle missing or extra columns gracefully if that’s part of the design.
     - Baselines:
       - Given a small synthetic DataFrame, ensure baseline computation returns expected averages.
       - Ensure attaching baselines adds the correct columns and preserves row count.

5. Code quality for tests
   - Use clear test names (test_[what_is_verified]()).
   - Avoid magic numbers when possible; if constants are used in the code, reference them via imports when it makes sense.
   - Keep tests deterministic (no randomness without seeding).
   - Prefer small, focused tests over one giant scenario, but it’s OK to add one or two end-to-end style tests (e.g., via FastAPI TestClient) that go from request payload → HTTP call → response validation.

6. Run and fix
   - After adding or updating tests, ensure:
     - `PYTHONPATH=src pytest` passes.
   - If something fails due to ambiguous behavior in the implementation, adjust the tests or suggest minimal code changes (but do not rewrite core logic unless it’s clearly buggy).

7. Output
   - Show me the new or updated test files with full code blocks.
   - Briefly summarize:
     - Which modules are now covered.
     - Any gaps that still exist, if any (e.g., “X function is tricky to test due to Y; here’s how we could refactor later”).

Start by summarizing what you found in src/plaix/ and tests/ (high-level only), then proceed to propose the new tests you will create, and finally write the concrete test code.
