You are the coding assistant for the PLAIX MVP.

Goal for Day 4:
Implement baseline computation + CSV pipeline utilities so that real-world data can flow
from input → baselines → anomaly requests → scoring.

Tasks:
1. Create plaix/data/loader.py with load_events_csv().
2. Create plaix/data/baselines.py with compute_phase_baselines() and attach_baselines().
3. Add data/sample_events.csv with varied phases.
4. Create plaix/pipeline/events_pipeline.py with prepare_events_for_scoring().
5. Add tests in tests/test_baselines.py to cover the baseline flow end-to-end.
6. Update README with a section about baselines.
7. Use type hints, docstrings, and clean code.
8. After coding, summarize changes and highlight next-day suggestions.

Read the existing code in src/plaix and make changes accordingly.
Proceed.
