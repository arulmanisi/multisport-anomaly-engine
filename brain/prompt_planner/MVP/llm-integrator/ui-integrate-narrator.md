You are my coding agent.

Goal:
Update the Streamlit demo UI to show the LLM-generated narrative
(narrative_title + narrative_summary) alongside the numeric scores.

Assumptions:
- ui/demo_streamlit/demo_ui.py already calls the /predict/single API and receives JSON.
- The API now returns:
    - narrative_title: str
    - narrative_summary: str

Tasks:

1) Open ui/demo_streamlit/demo_ui.py.

2) After receiving `result = call_prediction_api(payload)` and extracting:
    ups_score, ups_bucket, baseline_flag, model_prob, model_label,
   also extract:

    narrative_title = result.get("narrative_title", "")
    narrative_summary = result.get("narrative_summary", "")

3) Display narrative prominently:
   - Add a section, e.g.:

     st.subheader("AI Narrative")
     if narrative_title:
         st.markdown(f"**{narrative_title}**")
     if narrative_summary:
         st.write(narrative_summary)

   - Place this just below the metrics (UPS Score, Bucket, etc.) so it reads like an explanation of the numbers.

4) Do not change the payload or API URL usage, only the display logic.

5) After editing, show me the updated relevant portion of demo_ui.py.
