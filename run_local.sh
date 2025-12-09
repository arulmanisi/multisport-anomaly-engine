#!/usr/bin/env bash
set -e

./start_app.sh
sleep 3
open http://localhost:8501
echo "UI opened in browser. Press Ctrl+C to stop, or run ./stop_app.sh."
