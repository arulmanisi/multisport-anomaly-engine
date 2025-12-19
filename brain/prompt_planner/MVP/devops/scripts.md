You are my coding agent.

Goal:
Create three bash scripts in the project root that allow me to:
1) Start the entire anomaly engine (backend + UI)
2) Stop everything cleanly
3) Run the app locally end-to-end and automatically open the UI in a browser

These scripts must work on macOS.

----------------------------------------------------------------------
CREATE SCRIPT: start_app.sh
----------------------------------------------------------------------

Create start_app.sh with the following behavior:

1. Shebang + safety:
   #!/usr/bin/env bash
   set -e

2. Activate virtual environment if venv/ exists:
   if [ -d "venv" ]; then source venv/bin/activate; fi

3. Export the backend API URL:
   export PLAIX_API_URL="http://localhost:8000/predict/single"

4. Start backend (FastAPI) in the background:
   cd backend
   uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
   echo $! > ../backend.pid
   cd ..

5. Start Streamlit UI in the background:
   cd ui/demo_streamlit
   streamlit run demo_ui.py > ../../ui.log 2>&1 &
   echo $! > ../../ui.pid
   cd ../..

6. Print helpful messages:
   echo "Backend running on http://localhost:8000"
   echo "UI running on http://localhost:8501"
   echo "Use ./stop_app.sh to stop all processes."

7. Make script executable:
   chmod +x start_app.sh


----------------------------------------------------------------------
CREATE SCRIPT: stop_app.sh
----------------------------------------------------------------------

Create stop_app.sh with this behavior:

1. Shebang:
   #!/usr/bin/env bash
   set +e

2. Stop backend:
   if [ -f backend.pid ]; then kill $(cat backend.pid) 2>/dev/null || true; rm backend.pid; fi

3. Stop UI:
   if [ -f ui.pid ]; then kill $(cat ui.pid) 2>/dev/null || true; rm ui.pid; fi

4. Print success:
   echo "Stopped backend and UI."

5. Make script executable:
   chmod +x stop_app.sh


----------------------------------------------------------------------
CREATE SCRIPT: run_local.sh  (MAC-FRIENDLY)
----------------------------------------------------------------------

Create run_local.sh that:

1. Shebang:
   #!/usr/bin/env bash
   set -e

2. Calls start_app.sh:
   ./start_app.sh

3. Waits 2–3 seconds for services to start:
   sleep 3

4. Opens UI in macOS default browser:
   open http://localhost:8501

5. Print instructions:
   echo "UI opened in browser. Press Ctrl+C to stop, or run ./stop_app.sh."


6. Make script executable:
   chmod +x run_local.sh


----------------------------------------------------------------------
VALIDATION REQUIRED
----------------------------------------------------------------------

After creating all three scripts, show me:

- The final content of start_app.sh
- The final content of stop_app.sh
- The final content of run_local.sh

Ensure:
- They are executable
- They work on macOS
- They assume backend is at backend/app/main.py
- They assume UI is at ui/demo_streamlit/demo_ui.py

Implement now.
