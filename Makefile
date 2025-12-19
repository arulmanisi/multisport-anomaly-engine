SHELL := /bin/bash

PYTHON ?= python3

help:
	@echo "Targets:"
	@echo "  run-backend    Start backend (override BACKEND_APP=app.main:app)"
	@echo "  stop-backend   Stop backend started by run-backend (uses backend.pid if present)"
	@echo "  smoke-test     Run backend smoke test (curl-based)"
	@echo "  benchmark      Run synthetic benchmark (train/val metrics)"

run-backend:
	cd backend && BACKEND_APP=$${BACKEND_APP:-app.main:app} uvicorn $${BACKEND_APP} --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
	echo $$! > backend.pid
	@echo "Backend started on http://127.0.0.1:8000 (pid $$(cat backend.pid))"

stop-backend:
	@if [ -f backend.pid ]; then kill $$(cat backend.pid) && rm backend.pid && echo "Backend stopped."; else echo "No backend.pid found."; fi

smoke-test:
	bash scripts/smoke_test_backend.sh

benchmark:
	PYTHONPATH=backend:backend/src $(PYTHON) backend/scripts/run_benchmark.py
