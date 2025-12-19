You are my coding agent.

Goal:
Restructure this project into a "backend" and "ui" layout suitable for a future plaix.ai deployment, without breaking anything.

Tasks:

1) Create a backend/ directory and move engine code
- Create a directory: backend/
- Move the existing application code (FastAPI app, anomaly engine modules, UPSScorer, pipelines, TrainingEngine, ModelWrapper, etc.) into backend/.
  For example, if the current app entrypoint is at:
    app.py
  or
    src/api.py
  or
    main.py
  move those into a sensible structure like:
    backend/app/main.py
- Move scripts and models into backend where appropriate:
    scripts/  -> backend/scripts/
    models/   -> backend/models/
    tests/    -> backend/tests/
- Update any imports in the moved files so they use the new package paths under backend.
  For example:
    from xxx import yyy
  might become:
    from backend.app.xxx import yyy
  or similar, depending on the existing structure.

2) Create a ui/demo_streamlit/ directory and move the Streamlit UI
- Create directory: ui/demo_streamlit/
- Move the demo_ui.py file into ui/demo_streamlit/demo_ui.py
- Ensure any relative imports (if any) are updated to reflect the new project layout.

3) Keep run commands clear
- Ensure that the FastAPI app can still be started from the repo root with a command like:
    uvicorn backend.app.main:app --reload --port 8000
  (Adjust the module path to match the new layout.)
- Do NOT change functionality, only structure and imports.

4) After refactoring, please show:
- The new directory tree for:
    backend/
    ui/demo_streamlit/
- The updated FastAPI entrypoint path (module:app)
- Any changes to imports that were required.

Be careful to keep the project running end-to-end after this restructure.
