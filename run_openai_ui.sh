#!/usr/bin/env bash
set -e

# Run backend + UI with the OpenAI LLM provider enabled.
# Usage: OPENAI_API_KEY=sk-... ./run_openai_ui.sh

if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: OPENAI_API_KEY is not set. Export it before running." >&2
  exit 1
fi

export LLM_PROVIDER=openai
export PLAIX_API_URL=${PLAIX_API_URL:-"http://localhost:8000/predict/single"}

echo "Starting with LLM_PROVIDER=$LLM_PROVIDER and PLAIX_API_URL=$PLAIX_API_URL"
./start_app.sh
echo "Open http://localhost:8501 to test the UI (LLM=OpenAI)."
