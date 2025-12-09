#!/usr/bin/env bash
set -e

# Activate virtual environment if present
if [ -d "venv" ]; then source venv/bin/activate; fi

export PLAIX_API_URL="http://localhost:8000/predict/single"

# Start backend
cd backend
uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
echo $! > ../backend.pid
cd ..

# Start Streamlit UI
cd ui/demo_streamlit
streamlit run demo_ui.py > ../../ui.log 2>&1 &
echo $! > ../../ui.pid
cd ../..

echo "Backend running on http://localhost:8000"
echo "UI running on http://localhost:8501"
echo "Use ./stop_app.sh to stop all processes."
