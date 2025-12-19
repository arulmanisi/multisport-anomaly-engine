You are my coding agent.

Goal:
Add a Makefile target `make smoke-test` that runs a deterministic backend smoke test locally.
Also add a bash script that performs the curl-based checks and validates responses.

Constraints:
- Do not require Streamlit for smoke-test (backend only).
- Use localhost:8000.
- Script should start the backend if it is not already running, run tests, then stop it.
- Safe shutdown: only kill the process the script started.

Deliverables:
- Makefile (project root)
- scripts/smoke_test_backend.sh
- scripts/helpers.sh (optional helper functions)
- Update README with "make smoke-test" usage (short section)

Implementation details:

1) Create scripts/smoke_test_backend.sh (macOS/Linux bash)
- Shebang: #!/usr/bin/env bash
- set -euo pipefail
- Determine repo root (script directory / git root)
- Activate venv if present (venv/bin/activate)
- Export env defaults:
    export LLM_PROVIDER=${LLM_PROVIDER:-dummy}
    export PLAIX_BASE_URL=${PLAIX_BASE_URL:-http://localhost:8000}

2) Start backend (if not already running)
- Check if PLAIX_BASE_URL/docs responds (curl --fail).
- If not running:
    - Start uvicorn in background (no reload) with a configurable app path.
    - Write PID to /tmp/plaix_backend.pid (or repo .tmp/backend.pid).
    - Wait up to 20 seconds for /docs to respond.

NOTE: We may not know the exact uvicorn module path. Implement a fallback approach:
- Read env var BACKEND_APP (default "backend.app.main:app" OR "app.main:app" depending on your repo).
- Use:
    BACKEND_APP=${BACKEND_APP:-app.main:app}
- Run:
    (cd backend && uvicorn "$BACKEND_APP" --host 127.0.0.1 --port 8000 > ../backend_smoke.log 2>&1 &)

If your app path is different, user can set BACKEND_APP in shell:
    BACKEND_APP="app.main:app" make smoke-test

3) Smoke tests (curl checks)
Implement each check and fail with clear messages:

A) GET /feed/anomalies?limit=5
- Expect HTTP 200 and JSON with items array length > 0
- Validate required fields exist using python -c snippet (no jq dependency), e.g.:
    python - <<'PY'
    import json,sys
    data=json.load(sys.stdin)
    assert "items" in data and len(data["items"])>0
    item=data["items"][0]
    for k in ["event_id","player_id","match_format","ups_score","ups_bucket","headline","key_drivers"]:
        assert k in item
    print("OK: feed list")
    PY

B) GET /feed/anomaly/{event_id}?tone=commentator
- Grab event_id from the first response and call detail endpoint
- Validate narrative_title and narrative_summary exist (may be empty if dummy, but keys should exist)

C) POST /live/start
- Post JSON body and validate session_id and total_steps
- Capture session_id

D) GET /live/step/{session_id}?i=0&include_narrative=true&tone=commentator
- Validate keys: cumulative_runs, ups_score, headline, etc.

E) POST /report/anomaly/pdf
- Post a minimal body (like in your earlier smoke test)
- Validate response Content-Type is application/pdf
- Validate first 4 bytes of output are "%PDF"
- Save to /tmp/test_report.pdf

4) Cleanup
- If script started uvicorn, kill that PID and remove pid file.

5) Create Makefile targets
Add Makefile in repo root with targets:
- help (default)
- run-backend
- stop-backend (optional)
- smoke-test (calls scripts/smoke_test_backend.sh)

Example:
smoke-test:
    bash scripts/smoke_test_backend.sh

6) Mark scripts executable
- chmod +x scripts/smoke_test_backend.sh

7) README update
Add a short section:
- How to run: make smoke-test
- How to set BACKEND_APP if needed

After implementing, show me:
- Makefile
- scripts/smoke_test_backend.sh
- README section
