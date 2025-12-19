You are the PLAIX coding assistant. Continue building the MVP exactly according to the architecture in README and the design intent in src/plaix/.

Today’s goal (Day 5): 
Implement baseline computation utilities and integrate them cleanly into the PLAIX scoring workflow.

Tasks for Day 5:
1. In src/plaix/data/, create two modules:
   - loader.py
   - baselines.py

2. Implement loader.py with:
   - load_events_csv(path: str | Path) -> pd.DataFrame
   - Validate expected columns: match_id, over, ball, runs, wickets, phase
   - Clean column types (int for over/ball, float/int for runs/wickets, string for phase)
   - Return a DataFrame ready for baseline computation.

3. Implement baselines.py with:
   - compute_phase_baselines(df: pd.DataFrame) -> pd.DataFrame
       * Group by phase
       * Compute mean expected_runs and expected_wickets per ball
       * Return a DataFrame: phase, expected_runs, expected_wickets
   - attach_baselines(df: pd.DataFrame, baselines: pd.DataFrame) -> pd.DataFrame
       * Left-join on 'phase'
       * Ensure expected_runs / expected_wickets columns exist for all rows
       * Raise descriptive errors if any phases in df lack baselines.

4. Add a new test file: tests/test_baselines.py
   - Load a small synthetic DataFrame inline (no need for CSV yet).
   - Test baseline computation correctness.
   - Test attach_baselines merges correctly.
   - Test failure modes (missing phase values).

5. Integrate baselines into scoring:
   - In anomaly_scorer, add optional support where events missing expected_runs/expected_wickets trigger a ValueError with guidance: “Run baseline attachment first.”
   - Do NOT compute baselines inside the scorer—keep it separate by design.

6. Update README:
   - Add a section “PLAIX Baselines Pipeline (Day 5)” explaining:
     * How to load CSV
     * How to compute baselines
     * How to attach them before scoring.

7. Ensure code is modular, documented, and type-hinted.

After completing these tasks:
- Output the diffs for modified files.
- Then propose the next set of improvements for Day 6 based on the MVP roadmap.
