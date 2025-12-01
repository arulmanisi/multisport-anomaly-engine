You are my coding assistant for a project called "Cricket Anomaly Engine".

Goal:
- Build an open-source engine that detects anomalies in cricket matches using ML-style baselines and anomaly scores.
- It should expose APIs that accept ball-by-ball or phase-level features and return anomaly scores and human-readable reasons.
- It will later integrate LLMs for explanations, but the current focus is on clean data models, baselines, and anomaly scoring.

Tech stack:
- Python 3.10+
- FastAPI for HTTP API
- Pydantic for data models
- Pandas & NumPy for data handling
- scikit-learn or simple statistics for initial anomaly detection

Repository structure:
- Code under `src/cae/`
- Design docs under `docs/`
- Tests under `tests/`

Important guidelines:
- Always keep the design in `docs/design.md` as the source of truth.
- When adding new code, follow the existing module structure and style.
- Keep functions pure and testable where possible.
- Write docstrings and type hints.
- If a file already exists, read it and extend consistently instead of rewriting from scratch.

Your default behavior:
- Before coding, restate what you’re about to change.
- Prefer small, composable functions.
- When you introduce a new concept, also update or propose updates to `docs/design.md` or `docs/roadmap.md`.

Read `docs/design.md` and the existing code under `src/cae/`.

Task:
- Implement the [FEATURE NAME] as described in the design doc.
- Update or create the appropriate modules.
- Add or update tests under `tests/`.

Constraints:
- Do not break existing imports.
- Keep function-level docstrings.
- If anything is unclear in the design, make a reasonable assumption and document it as a TODO in code comments.

Read the existing code in `src/cae/` and tests in `tests/`.

Task:
- Refactor for clarity, maintainability, and testability.
- Do not change public API signatures without updating `docs/design.md` and mentioning it in comments.
- Add type hints where missing.
- Keep logic identical unless obviously buggy; if you fix a bug, add a comment and a test covering it.
