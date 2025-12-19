You are my coding agent.

Goal:
Enhance the “Featured Anomaly Story” section in the Streamlit UI (Top Anomalies tab) with:
1) A one-line sports-media headline
2) A “Key drivers” bullet list (UPS magnitude, volatility trend, context)
3) A Share button that copies the story text for demos

Constraints:
- Keep LLM keys server-side only.
- Continue calling backend narration endpoint for narrative text.
- UI must degrade gracefully if data is missing (no crashes).

Assumptions:
- UI file: ui/demo_streamlit/demo_ui.py
- There is a "Top Anomalies" tab that computes top_df and selects a featured row.
- Featured story is generated via a backend call (e.g., POST /narrate/anomaly),
  returning narrative_title and narrative_summary.

-------------------------------------------------------------------
PART A — Add sports-media headline (one-liner)
-------------------------------------------------------------------

1) In the Featured Anomaly Story rendering area:

- Construct a one-line headline that sounds like sports media.
- Prefer to generate it deterministically (rule-based) to avoid extra LLM calls.

Implement a helper in UI:

    def build_headline(featured: dict) -> str:
        # Use player_id, match_format, current_runs, baseline_mean_runs, ups_bucket
        # Examples:
        # "P_TEST lights up T20 with a breakout 60 — way above his usual 22"
        # "Shock surge: P_TEST posts 60 in T20, smashing baseline expectations"
        # "Out-of-nowhere masterclass: P_TEST rockets past his baseline in T20"
        # Choose wording based on ups_bucket severity.

- Display it above the narrative in a prominent style, e.g.:
    st.markdown("#### 🗞️ Headline")
    st.markdown(f"**{headline}**")

If key fields are missing, fallback headline:
    "Featured anomaly: unusually high performance vs baseline"

-------------------------------------------------------------------
PART B — Add “Key drivers” bullet list
-------------------------------------------------------------------

2) Add a section titled:
    st.markdown("#### Key drivers")

3) Compute the following drivers (rule-based) and display as bullet list:

A) UPS spike magnitude:
- Use ups_score if available. Convert into plain language:
    - >= 3.0 → "Extreme spike (≈ {ups_score:.1f}σ above baseline)"
    - 2.0–3.0 → "Strong spike (≈ {ups_score:.1f}σ above baseline)"
    - 1.0–2.0 → "Moderate spike (≈ {ups_score:.1f}σ above baseline)"
    - else → "Near baseline (≈ {ups_score:.1f}σ)"

If ups_score missing, fallback:
    "Spike magnitude: not available"

B) Volatility trend (requires recent events):
- If your UI already has access to recent events for the same player/format
  (from the recent trend endpoint or cached dataset), compute:
    - Standard deviation of last N UPS scores
    - Compare last N vs prior N if available, or simple heuristic:
        * if std_dev high → "High volatility recently"
        * if std_dev low → "Stable recent performance"
        * if last UPS > first UPS → "Trend improving"
        * if last UPS < first UPS → "Trend cooling off"

Implement helper:

    def compute_volatility_driver(recent_events_df: pd.DataFrame) -> str:
        # expects a column ups_score
        # return one sentence

If no recent events available, fallback:
    "Volatility trend: not available (enable Recent Innings data to compute)"

C) Context driver:
- Use available context fields if present in featured row:
    - opposition_strength (0–1) → "Strong opposition increases anomaly confidence"
    - venue_flatness (0–1) → "Batting-friendly venue may partially explain spike"
    - batting_position → "Higher batting position typically increases scoring opportunity"

If no context fields exist, use a generic bullet:
    "Context: baseline vs current runs is the primary signal in this demo"

4) Render as bullets, e.g.:

    st.markdown(f"- {driver_1}")
    st.markdown(f"- {driver_2}")
    st.markdown(f"- {driver_3}")

-------------------------------------------------------------------
PART C — Add Share button (copy story text)
-------------------------------------------------------------------

5) Add a "Share" section with a copyable text payload:

- Compose a shareable text block that includes:
    - headline
    - narrative_title
    - narrative_summary
    - key stats (runs, baseline, UPS score, probability)

Example:

    share_text = f"""{headline}

{narrative_title}
{narrative_summary}

Key stats:
- Runs: {current_runs}
- Baseline: {baseline_mean_runs:.1f} ± {baseline_std_runs:.1f}
- UPS: {ups_score:.2f} ({ups_bucket})
- Model anomaly probability: {model_prob:.2%}
"""

6) Streamlit doesn’t have a native clipboard-copy button everywhere, but we can do
a demo-friendly approach:

- Add:
    st.text_area("Share text (copy/paste)", value=share_text, height=180)

- Add a button:
    if st.button("Share"):
        # set session state flag so the text_area is highlighted/instructions shown
        st.success("Share text is ready — copy it from the box above.")

Optionally:
- Add a tiny JS clipboard component if the repo already uses streamlit-components.
But keep it MVP: use text_area + instructions (reliable in any environment).

7) Make sure the Share section is placed at the bottom of the Featured Anomaly Story box.

-------------------------------------------------------------------
PART D — Avoid repeated API calls & keep stable UX
-------------------------------------------------------------------

8) Ensure narrative generation is cached:
- Use st.session_state keyed by a "featured_key" (player_id + format + date/current_runs + ups_score).
- Only call narration endpoint when:
    - key changes, OR
    - user clicks "Regenerate Story"

9) Ensure no crashes when fields are missing:
- Use .get() with defaults for featured dict fields.
- If baseline_mean_runs/baseline_std_runs are missing, use simple safe defaults
  and add TODO comments.

-------------------------------------------------------------------
DELIVERABLES
-------------------------------------------------------------------

After implementing, show me the updated portion of ui/demo_streamlit/demo_ui.py that includes:
- Headline rendering
- Key drivers bullet list helpers
- Share text block + Share button behavior
- Any volatility helper logic and how it gets recent events (or the fallback path)
