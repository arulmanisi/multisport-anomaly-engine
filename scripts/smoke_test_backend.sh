#!/usr/bin/env bash
set -euo pipefail

# Backend smoke test runner (backend-only).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

# Pick python interpreter
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  else
    echo "No python interpreter found; set PYTHON_BIN." >&2
    exit 127
  fi
fi

export LLM_PROVIDER="${LLM_PROVIDER:-dummy}"
export PLAIX_BASE_URL="${PLAIX_BASE_URL:-http://127.0.0.1:8000}"
PID_FILE="/tmp/plaix_backend.pid"
STARTED_BACKEND=0

BACKEND_APP="${BACKEND_APP:-app.main:app}"

cleanup() {
  if [ "$STARTED_BACKEND" -eq 1 ] && [ -f "$PID_FILE" ]; then
    kill "$(cat "$PID_FILE")" >/dev/null 2>&1 || true
    rm -f "$PID_FILE"
  fi
}
trap cleanup EXIT

wait_for_backend() {
  local tries=0
  until curl -fsS "${PLAIX_BASE_URL}/docs" >/dev/null 2>&1; do
    tries=$((tries + 1))
    if [ $tries -ge 20 ]; then
      echo "Backend did not become ready at ${PLAIX_BASE_URL}" >&2
      exit 1
    fi
    sleep 1
  done
}

if ! curl -fsS "${PLAIX_BASE_URL}/docs" >/dev/null 2>&1; then
  echo "Starting backend for smoke test..."
  (cd backend && uvicorn "${BACKEND_APP}" --host 127.0.0.1 --port 8000 > ../backend_smoke.log 2>&1 & echo $! > "$PID_FILE")
  STARTED_BACKEND=1
  wait_for_backend
else
  echo "Backend already running at ${PLAIX_BASE_URL}"
fi

echo "Running smoke checks..."

# A) feed list
FEED_TMP="$(mktemp)"
FEED_STATUS=$(curl -s -o "$FEED_TMP" -w "%{http_code}" "${PLAIX_BASE_URL}/feed/anomalies?limit=5")
if [ "$FEED_STATUS" != "200" ]; then
  echo "Feed list returned HTTP $FEED_STATUS" >&2
  head -c 500 "$FEED_TMP" >&2 || true
  exit 1
fi
FEED_JSON="$(cat "$FEED_TMP")"
"${PYTHON_BIN}" - <<PY
import json, sys
raw = """$FEED_JSON"""
if not raw.strip():
    print("Empty response from /feed/anomalies", file=sys.stderr)
    sys.exit(1)
try:
    data=json.loads(raw)
except Exception as exc:
    print(f"Failed to parse /feed/anomalies JSON: {exc}", file=sys.stderr)
    print(raw[:500], file=sys.stderr)
    sys.exit(1)
assert "items" in data and len(data["items"])>0, "feed items missing"
item=data["items"][0]
for k in ["event_id","player_id","match_format","ups_score","ups_bucket","headline","key_drivers"]:
    assert k in item, f"missing {k}"
print("OK: feed list")
print(item["event_id"])
PY

EVENT_ID="$("${PYTHON_BIN}" - <<PY
import json, sys
raw = """$FEED_JSON"""
if not raw.strip():
    print("Empty feed JSON in EVENT_ID parse", file=sys.stderr)
    sys.exit(1)
data=json.loads(raw)
print(data["items"][0]["event_id"])
PY
)"

# B) feed detail
DETAIL_JSON="$(curl -fsS "${PLAIX_BASE_URL}/feed/anomaly/${EVENT_ID}?tone=commentator")"
"${PYTHON_BIN}" - <<PY
import json, sys
raw = """$DETAIL_JSON"""
if not raw.strip():
    print("Empty response from feed detail", file=sys.stderr)
    sys.exit(1)
data=json.loads(raw)
assert "narrative_title" in data and "narrative_summary" in data, "narrative fields missing"
print("OK: feed detail")
PY

# C) live start
LIVE_TMP="$(mktemp)"
LIVE_STATUS=$(curl -s -o "$LIVE_TMP" -w "%{http_code}" -X POST "${PLAIX_BASE_URL}/live/start" -H "Content-Type: application/json" -d '{"player_id":"P_SMOKE","match_format":"T20","scenario":"normal","baseline_mean_runs":22,"baseline_std_runs":8,"overs":10,"tone":"commentator","include_narrative":false}')
if [ "$LIVE_STATUS" != "200" ]; then
  echo "Live start returned HTTP $LIVE_STATUS" >&2
  head -c 500 "$LIVE_TMP" >&2 || true
  exit 1
fi
LIVE_JSON="$(cat "$LIVE_TMP")"
SESSION_ID="$("${PYTHON_BIN}" - <<PY
import json, sys
raw = """$LIVE_JSON"""
if not raw.strip():
    print("Empty response from live start", file=sys.stderr)
    sys.exit(1)
data=json.loads(raw)
assert "session_id" in data and "total_steps" in data
print(data["session_id"])
PY
)"
echo "OK: live start (session_id=${SESSION_ID})"

# D) live step
STEP_TMP="$(mktemp)"
STEP_STATUS=$(curl -s -o "$STEP_TMP" -w "%{http_code}" "${PLAIX_BASE_URL}/live/step/${SESSION_ID}?i=0&include_narrative=true&tone=commentator")
if [ "$STEP_STATUS" != "200" ]; then
  echo "Live step returned HTTP $STEP_STATUS" >&2
  head -c 500 "$STEP_TMP" >&2 || true
  exit 1
fi
STEP_JSON="$(cat "$STEP_TMP")"
"${PYTHON_BIN}" - <<PY
import json, sys
raw = """$STEP_JSON"""
if not raw.strip():
    print("Empty response from live step", file=sys.stderr)
    sys.exit(1)
data=json.loads(raw)
for k in ["cumulative_runs","ups_score","headline","key_drivers"]:
    assert k in data, f"missing {k}"
print("OK: live step 0")
PY

# E) report PDF
PDF_BYTES="/tmp/test_report.pdf"
curl -fsS -X POST "${PLAIX_BASE_URL}/report/anomaly/pdf" \
  -H "Content-Type: application/json" \
  -d '{"player_id":"P_SMOKE","match_format":"T20","current_runs":55,"baseline_mean_runs":22,"baseline_std_runs":8,"ups_score":2.1,"ups_bucket":"strong_spike","model_anomaly_probability":0.6,"model_anomaly_label":1}' \
  --output "$PDF_BYTES"
if [ ! -s "$PDF_BYTES" ]; then
  echo "PDF not created" >&2; exit 1
fi
head_bytes=$(head -c 4 "$PDF_BYTES")
if [ "$head_bytes" != "%PDF" ]; then
  echo "PDF signature missing" >&2; exit 1
fi
echo "OK: report PDF"

echo "Smoke test completed successfully."
