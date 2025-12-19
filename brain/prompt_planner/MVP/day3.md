You are the coding assistant for the PLAIX MVP build.

**Context (Completed Work):**
- Project structure scaffolded under src/plaix/
- FastAPI app created with /health and /score endpoints
- Placeholder anomaly scoring implemented (rule-based)
- Models: AnomalyRequest, AnomalyResponse
- Tests: test_health.py and test_anomaly_scorer.py (both passing)
- README includes basic setup instructions

**Goal for Day 3 MVP:**
Implement the **baseline computation pipeline** and the **CSV → baseline → scoring data flow utilities**, preparing the ground for the anomaly engine and dashboard.

---

### ✔️ Day 3 Tasks (Implement all)

1. **Create plaix/data/loader.py**
   - Implement load_events_csv(path: str|Path) -> pd.DataFrame
   - Validate required columns: match_id, over, ball, runs, wickets, phase
   - Add minimal cleaning (strip column names, enforce dtypes)

2. **Create plaix/data/baselines.py**
   - Implement compute_phase_baselines(df) -> pd.DataFrame
     * Group by "phase"
     * Compute expected_runs (mean of runs)
     * Compute expected_wickets (mean of wickets)
   - Implement attach_baselines(df, baselines_df)
     * Merge on "phase"
     * Output df must include expected_runs and expected_wickets

3. **Integrate baseline utilities with scoring**
   - Add a helper in plaix/models/anomaly_scorer.py:
       prepare_requests_from_df(df) -> List[AnomalyRequest]
   - If expected_runs or expected_wickets are missing, scorer should gracefully fallback or raise clear errors.

4. **Add tests**
   - tests/test_baselines.py
       * Create a small synthetic DataFrame inline
       * Test compute_phase_baselines() returns proper values
       * Test attach_baselines() attaches expected columns
   - tests/test_loader.py
       * Write a temporary CSV file
       * Test load_events_csv loads and cleans properly

5. **Update README**
   - Add "Data Flow (CSV → Baselines → Scoring)" section
   - Add short code sample using loader + baselines + scorer

---

### ✔️ Requirements / Style
- Use pandas for data handling
- Add type hints, clear docstrings, and internal validation
- Prefer pure functions and deterministic behavior
- All new modules must have __init__.py
- Ensure tests pass: `PYTHONPATH=src pytest -q`
- Do not modify existing score_event logic unless needed for integration

---

### ✔️ Deliverables for Day 3
- src/plaix/data/loader.py
- src/plaix/data/baselines.py
- Updated anomaly_scorer with prepare helper
- tests/test_baselines.py
- tests/test_loader.py
- README updated

Respond with:
1) Summary of what you plan to generate,
2) The code changes in patch/diff style,
3) The updated files.
