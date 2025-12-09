#!/usr/bin/env bash
set +e

if [ -f backend.pid ]; then kill $(cat backend.pid) 2>/dev/null || true; rm backend.pid; fi
if [ -f ui.pid ]; then kill $(cat ui.pid) 2>/dev/null || true; rm ui.pid; fi

echo "Stopped backend and UI."
