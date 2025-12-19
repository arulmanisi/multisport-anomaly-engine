You are my coding agent.

Goal:
Update the Streamlit demo UI to:
- Live under ui/demo_streamlit/demo_ui.py (after the restructure),
- Use plaix.ai branding,
- Read the backend API URL from an environment variable.

Tasks:

1) Open ui/demo_streamlit/demo_ui.py

2) Branding updates:
- Update page configuration to something like:

  st.set_page_config(
      page_title="Plaix.ai – Cricket Anomaly Engine",
      page_icon="🏏",
      layout="centered",
  )

- Update the main title to:

  st.title("🏏 Plaix.ai – Cricket UPS Anomaly Engine")

- In the introductory markdown, make sure the project name references Plaix.ai, for example:
  "This UI calls the Plaix.ai Cricket UPS Anomaly Engine end-to-end."

3) API URL via environment variable:
- At the top of the file, import os:

  import os

- Replace any hard-coded API URL (e.g., "http://localhost:8000/predict/single") with:

  API_URL = os.getenv("PLAIX_API_URL", "http://localhost:8000/predict/single")

- Ensure the rest of the code uses API_URL from this variable.

4) Make sure no functionality breaks:
- Do not remove existing logic for calling the /predict/single endpoint.
- Only update branding text and API_URL definition.

5) At the bottom of the file, keep the main guard:

  if __name__ == "__main__":
      main()

6) After changes, show me the updated demo_ui.py.
