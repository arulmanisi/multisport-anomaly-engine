You are my coding agent.

Goal:
Polish and improve the existing Streamlit UI (ui/demo_streamlit/demo_ui.py) so it looks
more like a professional, demo-ready app:

- Clear layout: inputs on the left, results on the right.
- A concise hero/description at the top.
- A richer results panel with:
    - risk level
    - metrics
    - AI narrative
    - explanation/help section
- Keep behavior the same: still call /predict/single, no breaking changes to backend.

Work only in ui/demo_streamlit/demo_ui.py.

-------------------------------------------------------------------
1) Page header & layout structure
-------------------------------------------------------------------

In demo_ui.py:

1. Keep the existing st.set_page_config but ensure the branding is clear, e.g.:

   st.set_page_config(
       page_title="Cricket UPS Anomaly Engine",
       page_icon="🏏",
       layout="wide",
   )

2. At the top of the page, replace or refine the title/intro as:

   st.title("🏏 AI-Powered Cricket Anomaly Engine")
   st.markdown(
       """
       This demo shows how an AI-driven anomaly engine evaluates a single cricket innings.

       It combines:
       - **Statistical baselines** (player's typical performance),
       - **UPS score** (*Unexpected Performance Spike*),
       - **Anomaly model probability**, and
       - An **AI-generated narrative** explaining what happened.
       """
   )

3. Use a two-column layout for the main content:

   left_col, right_col = st.columns([1, 1.2])

   - The **left column** contains all input controls and the "Run" button.
   - The **right column** shows metrics, risk level, narrative, and charts.

-------------------------------------------------------------------
2) Inputs panel (left column)
-------------------------------------------------------------------

Inside left_col:

1. Wrap the existing input widgets in a container, for example:

   with left_col:
       st.subheader("Innings Input")
       with st.form("prediction_form"):

           # Keep the existing player_id, match_format, batting_position, baseline sliders, etc.
           # Organize them into columns where appropriate, e.g.:
           # c1, c2 = st.columns(2)
           # Put player + format on one side, baseline stats on the other.

           submitted = st.form_submit_button("Run Anomaly Prediction")

2. Do not change the input payload structure (player_id, match_format, current_runs,
   baseline_mean_runs, baseline_std_runs, venue_flatness, opposition_strength, batting_position).

3. After submitted, keep the same call to the backend:

   result = call_prediction_api(payload)

-------------------------------------------------------------------
3) Results panel with risk view & metrics (right column)
-------------------------------------------------------------------

Inside right_col, after we get `result`:

Currently you extract:
- ups_score
- ups_bucket
- ups_anomaly_flag_baseline
- model_anomaly_probability
- model_anomaly_label
- narrative_title
- narrative_summary

Improve the presentation as follows:

1. Top section: "Anomaly Summary"

   with right_col:
       st.subheader("Anomaly Summary")

       # Derive a human-friendly risk label:
       if model_label == 1:
           risk_label = "High Anomaly Risk"
           risk_emoji = "🔴"
       elif ups_bucket in ("strong_spike", "extreme_spike"):
           risk_label = "Elevated Anomaly Risk"
           risk_emoji = "🟠"
       else:
           risk_label = "Low Anomaly Risk"
           risk_emoji = "🟢"

       st.markdown(f"### {risk_emoji} {risk_label}")

2. Under that, show key metrics in columns:

   m1, m2, m3 = st.columns(3)
   m1.metric("UPS Score", f"{ups_score:.2f}")
   m2.metric("Model Anomaly Probability", f"{model_prob:.2%}")
   m3.metric("UPS Bucket", ups_bucket)

   # Optionally another row:
   m4, m5, m6 = st.columns(3)
   m4.metric("Baseline Mean Runs", f"{baseline_mean_runs:.1f}")
   m5.metric("Current Runs", f"{current_runs}")
   m6.metric(
       "Baseline Anomaly Flag",
       "Yes" if baseline_flag == 1 else "No",
   )

3. AI Narrative section:

   st.subheader("AI Narrative")
   if narrative_title:
       st.markdown(f"**{narrative_title}**")
   if narrative_summary:
       st.write(narrative_summary)

4. Explainability / details section (expander):

   with st.expander("How this was evaluated"):
       st.markdown(
           """
           - **Baseline**: The player's expected runs in this format.
           - **UPS score**: How many standard deviations above (or below) the baseline this innings sits.
           - **Model anomaly probability**: An ML model combines UPS and context (venue, opposition, etc.) to estimate how anomalous the innings is.
           - **AI narrative**: A language model summarizes these signals into a human-readable explanation.
           """
       )

-------------------------------------------------------------------
4) Baseline vs current chart (reuse but better labeled)
-------------------------------------------------------------------

At the bottom of right_col (after narrative):

1. Keep the bar chart but add a clearer title and axis meaning:

   st.markdown("### Baseline vs Current Runs")

   df = pd.DataFrame(
       {"Type": ["Baseline Mean", "Current Runs"], "Runs": [baseline_mean_runs, current_runs]}
   ).set_index("Type")

   st.bar_chart(df)

2. Add a short note below:

   st.caption("This compares the player's typical runs in this format against the current innings.")

-------------------------------------------------------------------
5) Guard against no submission / first load
-------------------------------------------------------------------

Ensure that:

- All results panel logic (metrics, narrative, chart) is only executed when
  `submitted` is True and the API call succeeded.

If not submitted yet, right_col can show a simple placeholder:

   with right_col:
       st.subheader("Anomaly Summary")
       st.info("Fill in the innings details on the left and click 'Run Anomaly Prediction' to see results here.")

-------------------------------------------------------------------
6) Final check
-------------------------------------------------------------------

- Do not change how call_prediction_api() works.
- Do not change the JSON payload keys.
- Only improve layout, readability, and explanation.
- After changes, show me the updated demo_ui.py contents, focusing on:
    - Page header
    - Two-column layout
    - Results panel (risk label, metrics, narrative, chart).
