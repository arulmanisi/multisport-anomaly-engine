You are my coding agent.

Goal:
Enhance the Streamlit UI to include:
1) A Player search dropdown (populated from available player IDs in the dataset)
2) A Top Anomalies Leaderboard (most extreme UPS events)

Constraints:
- Keep existing UI behavior intact (single innings + trend tabs).
- Do not break the backend API. Prefer doing leaderboard and player list in UI first.
- If a real dataset exists locally, use it; otherwise fall back to a small demo dataset.
- Keep it fast and demo-friendly.

Assumptions:
- Streamlit UI is at: ui/demo_streamlit/demo_ui.py
- There is a dataset available from prior steps, potentially:
    data/processed/per_innings_with_ups.csv
  or a synthetic dataset under:
    data/synthetic_ups_dataset.csv
  or the backend provides events via the recent trend endpoint.

-------------------------------------------------------------------
PART A — Implement a shared data loader for UI
-------------------------------------------------------------------

1) In ui/demo_streamlit/demo_ui.py:
- Add a small helper that tries to load a dataset from disk for UI-only features.

Implement:

  @st.cache_data
  def load_events_dataset() -> pd.DataFrame:
      """
      Load a local dataset for UI features (player list + leaderboard).
      Tries processed real dataset first, then synthetic dataset.
      If none exist, returns an empty DataFrame.
      """
      # Try in this order:
      # 1) data/processed/per_innings_with_ups.csv
      # 2) data/processed/per_innings_cricsheet.csv (if labeled file not found)
      # 3) data/synthetic_ups_dataset.csv
      # Return df with normalized columns where possible.

- Normalize columns so UI can use them consistently:
  Required columns for leaderboard:
    - player_id or player_name (choose one and standardize to "player_id")
    - match_format
    - current_runs (or runs_scored)
    - ups_score
    - ups_bucket
    - model_anomaly_probability (if present; if not present, fill with NaN)
    - date (if present; if not present, create a placeholder or leave blank)

- If the dataset has "player_name" but not "player_id", rename player_name -> player_id (MVP shortcut).
- If it has "runs_scored" but not "current_runs", rename runs_scored -> current_runs.
- If it does not have "ups_score", "ups_bucket", then keep it empty and leaderboard will not show.

-------------------------------------------------------------------
PART B — Player search dropdown (with search)
-------------------------------------------------------------------

2) Create a player selector in both:
   - Single Innings tab
   - Recent Innings Trend tab

Instead of a plain text_input for player_id, do:

- Load df = load_events_dataset()
- Build a sorted unique list of player IDs:

    player_options = sorted(df["player_id"].dropna().unique().tolist()) if not df.empty else []

- Provide UI behavior:
  - If player_options is non-empty:
      use st.selectbox with a placeholder like:
        player_id = st.selectbox("Player", options=player_options, index=0)
    Also add a fallback option "Custom..." to allow manual entry.
  - If player_options is empty:
      keep a text_input fallback.

Implementation detail:
- Easiest: include "Custom..." at top of select list:
    ["Custom..."] + player_options
  If user selects "Custom...", show a text_input to type a player id.

Keep the old default "P_DEMO" as the typed default if needed.

-------------------------------------------------------------------
PART C — Top Anomalies Leaderboard (most extreme UPS events)
-------------------------------------------------------------------

3) Add a new section/tab:
- Add a third tab:
    tab1, tab2, tab3 = st.tabs(["Single Innings", "Recent Innings Trend", "Top Anomalies"])

4) In "Top Anomalies" tab:
- Load df = load_events_dataset()

- If df is empty or missing ups_score:
    show st.info("No local dataset with UPS scores found. Generate or load data to view the leaderboard.")
  and provide a short hint:
    - run dataset build scripts
    - or use synthetic generator

- If data is available:
    - Add filters at the top of tab:
        * match_format filter (All, T20, ODI, TEST)
        * minimum UPS score slider (0–5)
        * top_k slider (5–50, default 15)

    - Derive a "severity_score" for sorting:
        severity_score = ups_score
        If model_anomaly_probability exists, optionally combine:
           combined = 0.7 * ups_score + 0.3 * (model_prob*5)
        Use combined only if model probability is present; otherwise use ups_score.

    - Create leaderboard DataFrame with columns:
        - rank
        - player_id
        - match_format
        - date (if available)
        - current_runs
        - ups_score
        - ups_bucket
        - model_anomaly_probability (if available)
        - combined_score (if used)

    - Sort by combined_score descending (or ups_score) and take top_k.
    - Display via st.dataframe with friendly formatting:
        - ups_score to 2 decimals
        - probability to percentage if present

5) Optional nice touch:
- Add a "Select a row to demo" behavior:
  Streamlit doesn’t support row click natively in basic dataframe,
  but you can add a selectbox allowing user to pick a player from top results,
  then auto-populate Single Innings tab inputs via st.session_state.

Keep it simple for MVP:
- Add a selectbox below the leaderboard:
    selected_player = st.selectbox("Quick jump to player", options=top_df["player_id"].unique())
  And show:
    st.write("Tip: Use this player in the Single Innings tab to demo.")

-------------------------------------------------------------------
PART D — Keep performance fast and safe
-------------------------------------------------------------------

6) Use st.cache_data for dataset loading.
7) Ensure UI does not crash if columns are missing; degrade gracefully.

-------------------------------------------------------------------
DELIVERABLES
-------------------------------------------------------------------

After changes, show me:
- The updated ui/demo_streamlit/demo_ui.py with:
   - dataset loader helper
   - player dropdown with Custom fallback
   - "Top Anomalies" tab with filters and leaderboard
- Brief notes in comments describing which dataset paths it tries first.
