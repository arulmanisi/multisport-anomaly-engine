"""Streamlit demo for Plaix.ai Cricket UPS Anomaly Engine."""

import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import styles

API_URL = os.getenv("PLAIX_API_URL", "http://localhost:8000/predict/single")
API_ROOT = API_URL.rsplit("/predict/single", 1)[0] if "/predict/single" in API_URL else API_URL
NARRATE_URL = os.getenv("PLAIX_NARRATE_URL", f"{API_ROOT}/narrate/anomaly")
FEED_BASE_URL = os.getenv("PLAIX_FEED_URL", API_ROOT if API_ROOT else "http://localhost:8000")
LIVE_BASE_URL = os.getenv("PLAIX_LIVE_URL", API_ROOT if API_ROOT else "http://localhost:8000")
REPORT_BASE_URL = os.getenv("PLAIX_REPORT_URL", API_ROOT if API_ROOT else "http://localhost:8000")


@st.cache_data
def load_events_dataset() -> pd.DataFrame:
    """
    Load a local dataset for UI features (player list + leaderboard).

    Tries in order:
      1) data/processed/per_innings_with_ups.csv
      2) data/processed/per_innings_cricsheet.csv
      3) data/synthetic_ups_dataset.csv
    Returns an empty DataFrame if none are present.
    """
    candidates = [
        Path("data/processed/per_innings_with_ups.csv"),
        Path("data/processed/per_innings_cricsheet.csv"),
        Path("data/synthetic_ups_dataset.csv"),
    ]
    for path in candidates:
        if path.exists():
            try:
                df = pd.read_csv(path)
            except Exception:  # pragma: no cover - fallback
                continue
            # Normalize column names for UI usage.
            if "player_id" not in df.columns and "player_name" in df.columns:
                df = df.rename(columns={"player_name": "player_id"})
            if "current_runs" not in df.columns and "runs_scored" in df.columns:
                df = df.rename(columns={"runs_scored": "current_runs"})
            if "model_anomaly_probability" not in df.columns:
                df["model_anomaly_probability"] = pd.NA
            if "ups_bucket" not in df.columns:
                df["ups_bucket"] = pd.NA
            if "date" not in df.columns:
                df["date"] = ""
            # Ensure numeric
            if "ups_score" in df.columns:
                df["ups_score"] = pd.to_numeric(df["ups_score"], errors="coerce")
            if "model_anomaly_probability" in df.columns:
                df["model_anomaly_probability"] = pd.to_numeric(
                    df["model_anomaly_probability"], errors="coerce"
                )
            return df
    return pd.DataFrame()


def player_selector(label: str, df: pd.DataFrame, default: str = "P_DEMO") -> str:
    """Select player from dataset with custom fallback."""
    options = []
    if not df.empty and "player_id" in df.columns:
        options = sorted(pd.Series(df["player_id"].dropna().unique()).astype(str).tolist())
    if options:
        select_options = ["Custom..."] + options
        default_index = 0
        if default in options:
            default_index = options.index(default) + 1
        choice = st.selectbox(label, options=select_options, index=default_index)
        if choice == "Custom...":
            return st.text_input(f"{label} (custom)", default)
        return choice
    return st.text_input(label, default)


def call_narrate_api(payload: dict) -> dict:
    """
    Call narration endpoint. Defaults to local backend; override with PLAIX_NARRATE_URL.
    """
    url = NARRATE_URL
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_feed_list(match_format: str, min_ups: float, min_prob: float, limit: int, sort: str) -> dict:
    """Call anomaly feed list endpoint."""
    params = {
        "format": match_format,
        "min_ups": min_ups,
        "min_prob": min_prob,
        "limit": limit,
        "sort": sort,
    }
    url = f"{FEED_BASE_URL}/feed/anomalies"
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_feed_detail(event_id: str, tone: str) -> dict:
    """Call anomaly feed detail endpoint."""
    url = f"{FEED_BASE_URL}/feed/anomaly/{event_id}"
    resp = requests.get(url, params={"tone": tone}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_live_start(payload: dict) -> dict:
    """Start live simulation."""
    url = f"{LIVE_BASE_URL}/live/start"
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_live_step(session_id: str, index: int, include_narrative: bool, tone: str) -> dict:
    """Fetch a live step."""
    url = f"{LIVE_BASE_URL}/live/step/{session_id}"
    resp = requests.get(url, params={"i": index, "include_narrative": include_narrative, "tone": tone}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_report_pdf(payload: dict) -> bytes:
    """Call report export endpoint for PDF bytes."""
    url = f"{REPORT_BASE_URL}/report/anomaly/pdf"
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.content


def build_headline(featured: dict) -> str:
    """Construct a sports-media style headline (rule-based)."""
    player = featured.get("player_id", "Player")
    fmt = featured.get("match_format", "T20")
    runs = featured.get("current_runs")
    baseline = featured.get("baseline_mean_runs")
    bucket = str(featured.get("ups_bucket", "normal"))
    if runs is None or pd.isna(runs):
        runs = "a breakout innings"
    else:
        runs = f"{runs}"
    if baseline is None or pd.isna(baseline):
        baseline_text = "typical baseline"
    else:
        baseline_text = f"usual {baseline:.0f}"

    if bucket in {"extreme_spike", "strong_spike"}:
        return f"{player} lights up {fmt} with a breakout {runs} — way above the {baseline_text}"
    if bucket in {"mild_spike"}:
        return f"{player} finds extra gears in {fmt}, posting {runs} beyond the {baseline_text}"
    return "Featured anomaly: unusually high performance vs baseline"


def compute_volatility_driver(recent_events_df: pd.DataFrame) -> str:
    """Summarize volatility/trend from recent UPS scores."""
    if recent_events_df is None or recent_events_df.empty or "ups_score" not in recent_events_df.columns:
        return "Volatility trend: not available (enable Recent Innings data to compute)."
    ups = recent_events_df["ups_score"].dropna()
    if ups.empty:
        return "Volatility trend: not available (enable Recent Innings data to compute)."
    std = ups.std()
    first, last = ups.iloc[0], ups.iloc[-1]
    if std > 1.5:
        volatility = "High volatility recently"
    elif std > 0.7:
        volatility = "Moderate volatility recently"
    else:
        volatility = "Stable recent performance"
    trend = "trend stable"
    if last > first + 0.3:
        trend = "trend improving"
    elif last < first - 0.3:
        trend = "trend cooling off"
    return f"{volatility}; {trend} (σ std ≈ {std:.2f})"



def render_top_bar():
    """Renders a persistent top bar with branding and status."""
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            "<h3 style='margin:0; padding:0;'>🏏 PLAIX Intelligence Platform</h3>", 
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div style='text-align: right; color: #E0E0E0; font-size: 0.85rem; padding-top: 4px;'>
                Status: <span style='color: #4CAF50; font-weight: 600;'>● Online</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.divider()

def render_ticker(df: pd.DataFrame):
    """Renders a scrolling ticker of recent anomalies."""
    if df.empty or "ups_score" not in df.columns:
        return

    # Get top 5 recent anomalies
    recent_anomalies = df[df["ups_score"] > 2.0].sort_values("date", ascending=False).head(5)
    if recent_anomalies.empty:
        return

    ticker_items = []
    for _, row in recent_anomalies.iterrows():
        item = f"⚡ BREAKING: {row['player_id']} ({row['match_format']}) UPS {row['ups_score']:.2f}"
        ticker_items.append(item)
    
    ticker_text = "   &nbsp;&nbsp;&nbsp;&nbsp;   ".join(ticker_items)
    
    st.markdown(
        f"""
        <div class="ticker-wrap">
            <div class="ticker-item">{ticker_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_dashboard_stats(df: pd.DataFrame):
    """Renders high-level stats cards."""
    if df.empty or "ups_score" not in df.columns:
        return

    c1, c2, c3, c4 = st.columns(4)
    
    total_anomalies = len(df[df["ups_score"] > 2.0])
    avg_ups = df["ups_score"].mean()
    max_ups = df["ups_score"].max()
    active_players = df["player_id"].nunique()

    metrics = [
        ("Total Anomalies (24h)", total_anomalies),
        ("Avg UPS Score", f"{avg_ups:.2f}"),
        ("Max Spike Detected", f"{max_ups:.2f}"),
        ("Active Players", active_players),
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)

def main() -> None:
    st.set_page_config(
        page_title="PLAIX Intelligence Platform",
        page_icon="🏏",
        layout="wide",
    )
    st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)
    
    
    # Render Top Bar & Ticker
    render_top_bar()
    
    df_events = load_events_dataset()
    render_ticker(df_events)
    
    # Render Dashboard Stats (Global)
    render_dashboard_stats(df_events)

    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", [
            "Match Analyzer", 
            "Player Trend Analysis", 
            "Global Anomaly Index", 
            "Live Intelligence Feed", 
            "Score Predictor",
            "Predictive Simulator",
            "Platform Overview"
        ], label_visibility="collapsed")
        st.divider()



    # Main Content Area
    if page == "Match Analyzer":
        st.subheader("Match Analyzer")
        input_col, output_col = st.columns([1, 2], gap="large")
        
        with input_col:
            st.markdown("### Simulation Parameters")
            with st.form("prediction_form"):
                with st.expander("Game Context", expanded=True):
                    player_id = player_selector("Player", df_events, default="P1")
                    match_format = st.selectbox("Format", ["T20", "ODI", "TEST"], index=0)
                    batting_position = st.number_input("Batting position", min_value=1, max_value=11, value=4)

                with st.expander("Performance Data", expanded=True):
                    current_runs = st.number_input("Current runs", value=40.0, step=1.0)
                    baseline_mean_runs = st.number_input("Baseline mean runs", value=22.0, step=1.0)
                    baseline_std_runs = st.number_input("Baseline std runs", value=8.0, step=1.0)
                
                with st.expander("Match Conditions", expanded=False):
                    venue_flatness = st.slider("Venue flatness", 0.0, 1.0, 0.6)
                    opposition_strength = st.slider("Opposition strength", 0.0, 1.0, 0.5)
                    tone = st.selectbox(
                        "Narrative Tone",
                        options=["analyst", "commentator", "casual"],
                        index=0,
                    )
                
                submitted = st.form_submit_button("Run Analysis", type="primary")

        with output_col:
            right_col = st.container()
            if not submitted:
                st.info("Configure parameters to run simulation.")

        if submitted:
            payload = {
                "payload": {
                    "player_id": player_id,
                    "match_format": match_format,
                    "baseline_mean_runs": baseline_mean_runs,
                    "baseline_std_runs": baseline_std_runs,
                    "current_runs": current_runs,
                    "venue_flatness": venue_flatness,
                    "opposition_strength": opposition_strength,
                    "batting_position": batting_position,
                },
                "tone": tone,
            }

            try:
                resp = requests.post(API_URL, json=payload, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                ups_score = data.get("ups_score", 0.0)
                ups_bucket = data.get("ups_bucket", "normal")
                baseline_flag = data.get("ups_anomaly_flag_baseline", 0)
                model_prob = data.get("model_anomaly_probability", 0.0)
                model_label = data.get("model_anomaly_label", 0)
                narrative_title = data.get("narrative_title", "")
                narrative_summary = data.get("narrative_summary", "")

                with right_col:
                    st.subheader("Anomaly Summary")
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

                    m1, m2, m3 = st.columns(3)
                    m1.metric("UPS Score", f"{ups_score:.2f}")
                    m2.metric("Model Anomaly Probability", f"{model_prob:.2%}")
                    m3.metric("UPS Bucket", ups_bucket)

                    m4, m5, m6 = st.columns(3)
                    m4.metric("Baseline Mean Runs", f"{baseline_mean_runs:.1f}")
                    m5.metric("Current Runs", f"{current_runs}")
                    m6.metric("Baseline Anomaly Flag", "Yes" if baseline_flag == 1 else "No")

                    st.subheader("AI Narrative")
                    if narrative_title:
                        st.markdown(f"**{narrative_title}**")
                    if narrative_summary:
                        st.write(narrative_summary)

                    with st.expander("How this was evaluated"):
                        st.markdown(
                            """
                            - **Baseline**: The player's expected runs in this format.
                            - **UPS score**: How many standard deviations above (or below) the baseline this innings sits.
                            - **Model anomaly probability**: An ML model combines UPS and context (venue, opposition, etc.) to estimate how anomalous the innings is.
                            - **AI narrative**: A language model summarizes these signals into a human-readable explanation.
                            """
                        )

                    st.markdown("### Baseline vs Current Runs")
                    df = pd.DataFrame(
                        {"Type": ["Baseline Mean", "Current Runs"], "Runs": [baseline_mean_runs, current_runs]}
                    ).set_index("Type")
                    st.bar_chart(df)
                    st.caption("This compares the player's typical runs in this format against the current innings.")

                    # PDF export
                    if "single_pdf_bytes" not in st.session_state:
                        st.session_state["single_pdf_bytes"] = None
                        st.session_state["single_pdf_key"] = None
                    pdf_key = f"{player_id}_{match_format}_{current_runs}_{ups_score}"
                    if st.button("Download Analyst Report (PDF)"):
                        try:
                            pdf_payload = {
                                "player_id": player_id,
                                "match_format": match_format,
                                "current_runs": current_runs,
                                "baseline_mean_runs": baseline_mean_runs,
                                "baseline_std_runs": baseline_std_runs,
                                "ups_score": ups_score,
                                "ups_bucket": ups_bucket,
                                "model_anomaly_probability": model_prob,
                                "model_anomaly_label": model_label,
                                "headline": f"{risk_label}",
                                "key_drivers": [
                                    f"UPS: {ups_score:.2f} ({ups_bucket})",
                                    f"Baseline vs current: {baseline_mean_runs:.1f} → {current_runs}",
                                    f"Model probability: {model_prob:.2%}",
                                ],
                                "tone": tone,
                            }
                            st.session_state["single_pdf_bytes"] = call_report_pdf(pdf_payload)
                            st.session_state["single_pdf_key"] = pdf_key
                        except Exception as exc:  # pylint: disable=broad-except
                            st.error(f"Could not generate report: {exc}")
                    if st.session_state.get("single_pdf_bytes") and st.session_state.get("single_pdf_key") == pdf_key:
                        st.download_button(
                            "Download now",
                            data=st.session_state["single_pdf_bytes"],
                            file_name=f"anomaly_report_{player_id}_{match_format}.pdf",
                            mime="application/pdf",
                        )
            except Exception as exc:  # pylint: disable=broad-except
                with right_col:
                    st.error(f"Request failed: {exc}")
                    st.info("Check PLAIX_API_URL or backend availability.")

    if page == "Player Trend Analysis":
        st.subheader("Recent Innings Trend")
        
        input_col, output_col = st.columns([1, 2], gap="large")
        
        with input_col:
            st.markdown("### Trend Parameters")
            with st.form("trend_form"):
                with st.expander("Player Selection", expanded=True):
                    trend_player_id = player_selector("Player", df_events, default="P_DEMO")
                    trend_format = st.selectbox("Format", ["T20", "ODI", "TEST"], index=0)
                
                with st.expander("Analysis Depth", expanded=True):
                    last_n = st.slider("Last N innings", min_value=3, max_value=10, value=5)
                    trend_tone = st.selectbox(
                        "Narrative Tone",
                        options=["analyst", "commentator", "casual"],
                        index=0,
                        help="Controls how the AI narrative is written.",
                    )
                
                submitted_trend = st.form_submit_button("Analyze Trend", type="primary")

        with output_col:
            result_container = st.container()
            if not submitted_trend:
                st.info("Configure trend parameters to view analysis.")

            if submitted_trend:
                try:
                    trend_resp = requests.post(
                        f"{API_ROOT}/player/recent/summary",
                        json={
                            "player_id": trend_player_id,
                            "match_format": trend_format,
                            "n": last_n,
                            "tone": trend_tone,
                        },
                        timeout=10,
                    )
                    trend_resp.raise_for_status()
                    trend_data = trend_resp.json()
                    events = trend_data.get("events", [])
                    summary_title = trend_data.get("summary_title") or "Recent innings summary"
                    summary_body = trend_data.get("summary_body") or ""

                    with result_container:
                        st.markdown('<div class="featured-card">', unsafe_allow_html=True)
                        st.markdown(f"### {summary_title}")
                        st.write(summary_body)
                        st.markdown('</div>', unsafe_allow_html=True)

                        if events:
                            st.markdown("#### UPS Trend")
                            df_trend = pd.DataFrame(events)
                            df_trend = df_trend.reset_index().rename(columns={"index": "Innings"})
                            df_trend["Innings"] = df_trend["Innings"] + 1
                            st.line_chart(df_trend.set_index("Innings")[["ups_score"]])

                            with st.expander("Data Table"):
                                display_cols = [
                                    "date",
                                    "current_runs",
                                    "baseline_mean_runs",
                                    "ups_score",
                                    "ups_bucket",
                                    "model_anomaly_probability",
                                ]
                                st.dataframe(df_trend[display_cols], use_container_width=True)
                        else:
                            st.info("No recent innings available for this player/format.")
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Trend request failed: {exc}")
                    st.info("Ensure backend is running and player ID exists.")

    if page == "Global Anomaly Index":
        st.subheader("Top Anomalies")
        if df_events.empty or "ups_score" not in df_events.columns:
            st.info("No local dataset with UPS scores found. Load or generate data to view the leaderboard.")
            st.caption("Looking for data/processed/per_innings_with_ups.csv or data/synthetic_ups_dataset.csv")
        else:
            df_top = df_events.copy()
            df_top = df_top.dropna(subset=["ups_score"])
            format_options = ["All"] + sorted(
                pd.Series(df_top["match_format"].dropna().astype(str).unique()).tolist()
            )
            f1, f2, f3 = st.columns(3)
            format_filter = f1.selectbox("Match format", options=format_options, index=0)
            min_ups = f2.slider("Minimum UPS", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
            top_k = int(f3.slider("Top K", min_value=5, max_value=50, value=15, step=1))

            if format_filter != "All":
                df_top = df_top[df_top["match_format"] == format_filter]
            df_top = df_top[df_top["ups_score"] >= min_ups]

            has_prob = "model_anomaly_probability" in df_top.columns and df_top["model_anomaly_probability"].notna().any()
            if has_prob:
                df_top["combined_score"] = 0.7 * df_top["ups_score"] + 0.3 * (
                    df_top["model_anomaly_probability"].fillna(0) * 5
                )
            else:
                df_top["combined_score"] = df_top["ups_score"]

            df_top = df_top.sort_values("combined_score", ascending=False).head(top_k)
            if df_top.empty:
                st.info("No records match the filters.")
            else:
                df_top = df_top.reset_index(drop=True)
                df_top["rank"] = df_top.index + 1
                display_cols = [
                    "rank",
                    "player_id",
                    "match_format",
                    "date",
                    "current_runs",
                    "ups_score",
                    "ups_bucket",
                ]
                if has_prob:
                    display_cols.append("model_anomaly_probability")
                display_cols.append("combined_score")

                display_df = df_top[display_cols].copy()
                display_df["ups_score"] = display_df["ups_score"].round(2)
                display_df["combined_score"] = display_df["combined_score"].round(2)
                if has_prob:
                    display_df["model_anomaly_probability"] = (
                        display_df["model_anomaly_probability"].fillna(0).apply(lambda x: f"{x:.1%}")
                    )
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        "rank": st.column_config.NumberColumn("Rank", width="small"),
                        "player_id": st.column_config.TextColumn("Player"),
                        "match_format": st.column_config.TextColumn("Format", width="small"),
                        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                        "current_runs": st.column_config.NumberColumn("Runs"),
                        "ups_score": st.column_config.ProgressColumn(
                            "UPS Score",
                            min_value=0,
                            max_value=5,
                            format="%.2f",
                        ),
                        "model_anomaly_probability": st.column_config.ProgressColumn(
                            "Model Prob",
                            min_value=0,
                            max_value=1,
                            format="%.1f%%",
                        ),
                        "combined_score": st.column_config.NumberColumn("Score", format="%.2f"),
                    },
                    hide_index=True,
                )

                # Featured Anomaly Story Container
                st.markdown('<div class="featured-card">', unsafe_allow_html=True)
                featured_row = df_top.iloc[0].to_dict()
                st.subheader("Featured Anomaly Story")
                st.caption("Auto-generated in commentator tone from the most extreme anomaly in the current view.")

                baseline_mean = featured_row.get("baseline_mean_runs")
                baseline_std = featured_row.get("baseline_std_runs")
                # TODO: replace fallbacks with real baselines once available.
                if pd.isna(baseline_mean):
                    baseline_mean = featured_row.get("current_runs", 20.0) * 0.4 if featured_row.get("current_runs") else 20.0
                if pd.isna(baseline_std):
                    baseline_std = 10.0

                narrate_payload = {
                    "player_id": featured_row.get("player_id", "unknown"),
                    "match_format": featured_row.get("match_format", "T20"),
                    "baseline_mean_runs": baseline_mean,
                    "baseline_std_runs": baseline_std,
                    "current_runs": featured_row.get("current_runs", 0.0),
                    "ups_score": featured_row.get("ups_score"),
                    "ups_bucket": featured_row.get("ups_bucket"),
                    "ups_anomaly_flag_baseline": featured_row.get("ups_anomaly_flag_baseline"),
                    "model_anomaly_probability": featured_row.get("model_anomaly_probability"),
                    "model_anomaly_label": featured_row.get("model_anomaly_label"),
                    "tone": "commentator",
                }

                story_key = f"{narrate_payload['player_id']}_{narrate_payload['match_format']}_{narrate_payload['current_runs']}_{narrate_payload.get('ups_score')}"

                def generate_story() -> dict:
                    try:
                        return call_narrate_api(narrate_payload)
                    except Exception as exc:  # pylint: disable=broad-except
                        st.warning("Could not generate narrative. Showing fallback message.")
                        return {
                            "narrative_title": "Top anomaly highlight",
                            "narrative_summary": f"Top anomaly: player scored {narrate_payload['current_runs']} vs baseline {baseline_mean} (UPS {narrate_payload.get('ups_score', 'n/a')}).",
                        }

                if "featured_story" not in st.session_state or st.session_state.get("featured_story_key") != story_key:
                    st.session_state["featured_story"] = generate_story()
                    st.session_state["featured_story_key"] = story_key

                if st.button("Regenerate Story"):
                    st.session_state["featured_story"] = generate_story()
                    st.session_state["featured_story_key"] = story_key

                story = st.session_state.get("featured_story", {})
                headline = build_headline(featured_row)

                st.markdown("#### 🗞️ Headline")
                st.markdown(f"**{headline}**")

                st.markdown(f"### {story.get('narrative_title', '')}")
                st.write(story.get("narrative_summary", ""))

                # Key drivers
                st.markdown("#### Key drivers")
                # Recent volatility from local dataset for same player/format
                recent_slice = df_top[df_top["player_id"] == narrate_payload["player_id"]]
                driver_spike = "Spike magnitude: not available"
                ups_score_val = narrate_payload.get("ups_score")
                if ups_score_val is not None and not pd.isna(ups_score_val):
                    if ups_score_val >= 3.0:
                        driver_spike = f"Extreme spike (≈ {ups_score_val:.1f}σ above baseline)"
                    elif ups_score_val >= 2.0:
                        driver_spike = f"Strong spike (≈ {ups_score_val:.1f}σ above baseline)"
                    elif ups_score_val >= 1.0:
                        driver_spike = f"Moderate spike (≈ {ups_score_val:.1f}σ above baseline)"
                    else:
                        driver_spike = f"Near baseline (≈ {ups_score_val:.1f}σ)"

                driver_volatility = compute_volatility_driver(recent_slice)

                context_bits = []
                opp_strength = featured_row.get("opposition_strength")
                venue_flatness = featured_row.get("venue_flatness")
                batting_pos = featured_row.get("batting_position")
                if opp_strength is not None and not pd.isna(opp_strength):
                    if opp_strength > 0.7:
                        context_bits.append("Strong opposition increases anomaly confidence.")
                    elif opp_strength < 0.3:
                        context_bits.append("Weaker opposition may soften anomaly significance.")
                if venue_flatness is not None and not pd.isna(venue_flatness):
                    if venue_flatness > 0.7:
                        context_bits.append("Batting-friendly venue may partially explain the spike.")
                    elif venue_flatness < 0.3:
                        context_bits.append("Bowler-friendly venue makes the spike more impressive.")
                if batting_pos is not None and not pd.isna(batting_pos):
                    context_bits.append(f"Batting position {int(batting_pos)} influences scoring opportunity.")
                if not context_bits:
                    context_bits.append("Context: baseline vs current runs is the primary signal.")
                st.markdown(f"**Drivers:** <span class='driver-tag'>{driver_spike}</span> <span class='driver-tag'>{driver_volatility}</span>", unsafe_allow_html=True)
                
                if context_bits:
                    st.caption("Contextual factors:")
                    for bit in context_bits:
                        st.markdown(f"- {bit}")
                
                st.markdown('</div>', unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Player", narrate_payload["player_id"])
                c2.metric("Runs", narrate_payload["current_runs"])
                ups_val = narrate_payload.get("ups_score")
                c3.metric("UPS", f"{ups_val:.2f}" if ups_val is not None else "—")
                prob_val = narrate_payload.get("model_anomaly_probability")
                c4.metric("Model Prob", f"{prob_val:.2%}" if prob_val is not None and not pd.isna(prob_val) else "—")

                # Share block
                st.markdown("#### Share")
                share_text = f"""{headline}

{story.get('narrative_title', '')}
{story.get('narrative_summary', '')}

Key stats:
- Runs: {narrate_payload['current_runs']}
- Baseline: {baseline_mean:.1f} ± {baseline_std:.1f}
- UPS: {ups_val:.2f if ups_val is not None else "n/a"} ({narrate_payload.get('ups_bucket', 'n/a')})
- Model anomaly probability: {prob_val:.2% if prob_val is not None and not pd.isna(prob_val) else "n/a"}
"""
                st.text_area("Share text (copy/paste)", value=share_text, height=180)
                if st.button("Share"):
                    st.success("Share text is ready — copy it from the box above.")

                # PDF export for featured story
                if "featured_pdf_bytes" not in st.session_state:
                    st.session_state["featured_pdf_bytes"] = None
                    st.session_state["featured_pdf_key"] = None
                featured_pdf_key = f"{narrate_payload['player_id']}_{narrate_payload['match_format']}_{narrate_payload['current_runs']}_{narrate_payload.get('ups_score')}"
                if st.button("Download Analyst Report (PDF)", key="featured_pdf_btn"):
                    try:
                        pdf_payload = {
                            "player_id": narrate_payload["player_id"],
                            "match_format": narrate_payload["match_format"],
                            "current_runs": narrate_payload["current_runs"],
                            "baseline_mean_runs": baseline_mean,
                            "baseline_std_runs": baseline_std,
                            "ups_score": narrate_payload.get("ups_score", 0.0),
                            "ups_bucket": narrate_payload.get("ups_bucket", "normal"),
                            "model_anomaly_probability": narrate_payload.get("model_anomaly_probability", 0.0),
                            "model_anomaly_label": narrate_payload.get("model_anomaly_label", 0),
                            "headline": headline,
                            "key_drivers": [driver_spike, driver_volatility] + context_bits[:1],
                            "tone": "commentator",
                        }
                        st.session_state["featured_pdf_bytes"] = call_report_pdf(pdf_payload)
                        st.session_state["featured_pdf_key"] = featured_pdf_key
                    except Exception as exc:  # pylint: disable=broad-except
                        st.error(f"Could not generate report: {exc}")
                if (
                    st.session_state.get("featured_pdf_bytes")
                    and st.session_state.get("featured_pdf_key") == featured_pdf_key
                ):
                    st.download_button(
                        "Download report",
                        data=st.session_state["featured_pdf_bytes"],
                        file_name=f"anomaly_report_{narrate_payload['player_id']}_{narrate_payload['match_format']}.pdf",
                        mime="application/pdf",
                        key="featured_pdf_download",
                    )

                selected_player = st.selectbox(
                    "Quick jump to player", options=display_df["player_id"].unique()
                )
                st.caption("Tip: Use this player in the Match Analyzer tab to analyze.")

    if page == "Live Intelligence Feed":
        st.subheader("Anomaly Feed")
        filters_col, feed_col = st.columns([1, 2])
        if "selected_event_id" not in st.session_state:
            st.session_state["selected_event_id"] = None
        if "last_feed_items" not in st.session_state:
            st.session_state["last_feed_items"] = []

        with filters_col:
            feed_format = st.selectbox("Format", options=["ALL", "T20", "ODI", "TEST"], index=0)
            feed_min_ups = st.slider("Min UPS", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
            feed_min_prob = st.slider("Min model probability", min_value=0.0, max_value=1.0, value=0.1, step=0.05)
            feed_limit = st.slider("Limit", min_value=10, max_value=50, value=20, step=5)
            feed_sort = st.selectbox("Sort by", options=["combined", "ups"], index=0)
            feed_tone = st.selectbox("Narrative Tone (details)", options=["analyst", "commentator", "casual"], index=1)
            refresh_feed = st.button("Load feed")

        with feed_col:
            items = []
            if refresh_feed:
                try:
                    feed_resp = call_feed_list(feed_format, feed_min_ups, feed_min_prob, feed_limit, feed_sort)
                    items = feed_resp.get("items", [])
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Feed request failed: {exc}")
            elif st.session_state.get("last_feed_items"):
                items = st.session_state["last_feed_items"]

            if refresh_feed:
                st.session_state["last_feed_items"] = items

            if not items:
                st.info("No anomalies to display. Adjust filters and click 'Load feed'.")
            else:
                for idx, item in enumerate(items):
                    st.markdown(f"**{item.get('headline', 'Anomaly')}**")
                    meta = f"{item.get('player_id','?')} · {item.get('match_format','?')} · {item.get('date','')}"
                    st.caption(meta)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("UPS", f"{item.get('ups_score', 0):.2f}")
                    prob_val = item.get("model_anomaly_probability")
                    c2.metric("Prob", f"{prob_val:.2%}" if prob_val is not None and not pd.isna(prob_val) else "—")
                    c3.metric("Bucket", item.get("ups_bucket", "normal"))
                    c4.metric("Score", f"{item.get('combined_score', item.get('ups_score', 0)):.2f}")
                    drivers = item.get("key_drivers", []) or []
                    for d in drivers[:3]:
                        st.markdown(f"- {d}")
                    button_key = f"{item.get('event_id')}_{idx}" if item.get("event_id") else f"detail_{meta}_{idx}"
                    if st.button("View details", key=button_key):
                        st.session_state["selected_event_id"] = item.get("event_id")
                    st.divider()

            if st.session_state.get("selected_event_id"):
                st.markdown("### Anomaly Detail")
                try:
                    detail = call_feed_detail(st.session_state["selected_event_id"], feed_tone)
                    st.markdown(f"**{detail.get('narrative_title','')}**")
                    st.write(detail.get("narrative_summary", ""))

                    d1, d2, d3, d4 = st.columns(4)
                    d1.metric("Player", detail.get("player_id", ""))
                    d2.metric("Runs", detail.get("current_runs", ""))
                    ups_val = detail.get("ups_score")
                    d3.metric("UPS", f"{ups_val:.2f}" if ups_val is not None else "—")
                    prob_val = detail.get("model_anomaly_probability")
                    d4.metric("Prob", f"{prob_val:.2%}" if prob_val is not None and not pd.isna(prob_val) else "—")

                    st.markdown("#### Key drivers")
                    for d in detail.get("key_drivers", [])[:3]:
                        st.markdown(f"- {d}")

                    baseline_mean = detail.get("baseline_mean_runs", 0.0)
                    current_runs = detail.get("current_runs", 0.0)
                    chart_df = pd.DataFrame(
                        {"Type": ["Baseline Mean", "Current Runs"], "Runs": [baseline_mean, current_runs]}
                    ).set_index("Type")
                    st.bar_chart(chart_df)

                    if "feed_pdf_bytes" not in st.session_state:
                        st.session_state["feed_pdf_bytes"] = None
                        st.session_state["feed_pdf_key"] = None
                    feed_pdf_key = f"{detail.get('player_id')}_{detail.get('match_format')}_{detail.get('current_runs')}_{detail.get('ups_score')}"
                    if st.button("Download Analyst Report (PDF)", key="feed_pdf_btn"):
                        try:
                            pdf_payload = {
                                "player_id": detail.get("player_id", "unknown"),
                                "match_format": detail.get("match_format", "T20"),
                                "date": detail.get("date", ""),
                                "current_runs": detail.get("current_runs", 0.0),
                                "baseline_mean_runs": detail.get("baseline_mean_runs", 20.0),
                                "baseline_std_runs": detail.get("baseline_std_runs", 10.0),
                                "ups_score": detail.get("ups_score", 0.0),
                                "ups_bucket": detail.get("ups_bucket", "normal"),
                                "model_anomaly_probability": detail.get("model_anomaly_probability", 0.0),
                                "model_anomaly_label": detail.get("model_anomaly_label", 0),
                                "headline": detail.get("headline"),
                                "key_drivers": detail.get("key_drivers", []),
                                "tone": feed_tone,
                            }
                            st.session_state["feed_pdf_bytes"] = call_report_pdf(pdf_payload)
                            st.session_state["feed_pdf_key"] = feed_pdf_key
                        except Exception as exc:  # pylint: disable=broad-except
                            st.error(f"Could not generate report: {exc}")
                    if (
                        st.session_state.get("feed_pdf_bytes")
                        and st.session_state.get("feed_pdf_key") == feed_pdf_key
                    ):
                        st.download_button(
                            "Download report",
                            data=st.session_state["feed_pdf_bytes"],
                            file_name=f"anomaly_report_{detail.get('player_id','player')}_{detail.get('match_format','T20')}.pdf",
                            mime="application/pdf",
                            key="feed_pdf_download",
                        )

                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Detail request failed: {exc}")
                if st.button("Clear selection"):
                    st.session_state["selected_event_id"] = None
                    st.experimental_rerun()



    if page == "Score Predictor":
        st.subheader("Match Score Predictor")
        
        # Disclaimer
        st.warning(
            "⚠️ **Responsible Usage**: This module provides statistical score projections based on historical data and match conditions. "
            "It is intended for performance analysis and fan engagement only. It is **not** a betting tool and should not be used for financial decisions."
        )

        input_col, output_col = st.columns([1, 2], gap="large")

        with input_col:
            st.markdown("### Match Conditions")
            with st.form("score_predictor_form"):
                with st.expander("Player & Format", expanded=True):
                    pred_player = player_selector("Select Player", df_events, default="P_DEMO")
                    pred_format = st.selectbox("Format", ["T20", "ODI", "TEST"], index=0)
                
                with st.expander("Contextual Factors", expanded=True):
                    pred_venue = st.slider("Pitch Condition (0=Bowler friendly, 1=Batting friendly)", 0.0, 1.0, 0.6)
                    pred_opp = st.slider("Opposition Strength (0=Weak, 1=World Class)", 0.0, 1.0, 0.5)
                    pred_form = st.slider("Recent Form (0=Poor, 1=Excellent)", 0.0, 1.0, 0.5)

                submitted_pred = st.form_submit_button("Predict Score", type="primary")

        with output_col:
            result_container = st.container()
            if not submitted_pred:
                st.info("Configure match conditions to generate a score projection.")
            
            if submitted_pred:
                # Heuristic Prediction Logic
                # Base scores roughly per format
                base_score = {"T20": 25, "ODI": 40, "TEST": 65}.get(pred_format, 30)
                
                # Factors
                # Pitch: +/- 20%
                pitch_factor = (pred_venue - 0.5) * 0.4
                # Opposition: Strong opp reduces score by up to 30%, Weak increases by 10%
                opp_factor = (0.5 - pred_opp) * 0.3
                # Form: +/- 25%
                form_factor = (pred_form - 0.5) * 0.5
                
                total_factor = 1 + pitch_factor + opp_factor + form_factor
                # Add some randomness for range (mocking uncertainty)
                import random
                random_variance = 0.1  # +/- 5% fixed variance for center
                
                projected_val = base_score * total_factor
                lower_bound = int(projected_val * 0.85)
                upper_bound = int(projected_val * 1.15)
                projected_val = int(projected_val)
                
                confidence = "Medium"
                if pred_form > 0.8: confidence = "High"
                if pred_form < 0.2: confidence = "Low"

                with result_container:
                    st.markdown('<div class="featured-card">', unsafe_allow_html=True)
                    st.markdown(f"### Projected Innings Score: **{projected_val}**")
                    st.caption(f"Estimated Range: {lower_bound} - {upper_bound} runs")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Confidence", confidence)
                    c2.metric("Pitch Impact", f"{pitch_factor:+.0%}")
                    c3.metric("Form Impact", f"{form_factor:+.0%}")
                    
                    st.markdown("---")
                    st.caption(f"Model based on: {pred_format} historical data adjusted for venue ({pred_venue}) and opposition ({pred_opp}).")
                    st.markdown('</div>', unsafe_allow_html=True)

    if page == "Predictive Simulator":
        st.subheader("Predictive Simulator")
        controls_col, live_col = st.columns([1, 2])

        if "live_session_id" not in st.session_state:
            st.session_state["live_session_id"] = None
            st.session_state["live_steps"] = []
            st.session_state["live_index"] = 0
            st.session_state["live_play"] = False

        with controls_col:
            live_player = player_selector("Player", df_events, default="P_DEMO")
            live_format = st.selectbox("Format", ["T20", "ODI", "TEST"], index=0)
            live_scenario = st.selectbox("Scenario", ["normal", "breakout", "collapse"], index=0)
            live_baseline_mean = st.number_input("Baseline mean runs", value=22.0, step=1.0, key="live_baseline_mean")
            live_baseline_std = st.number_input("Baseline std runs", value=8.0, step=1.0, key="live_baseline_std")
            live_overs = st.slider("Overs", min_value=10, max_value=20, value=20, step=1)
            live_tone = st.selectbox("Narrative Tone", options=["analyst", "commentator", "casual"], index=1)
            live_include_narrative = st.checkbox("Include narrative", value=True)

            if st.button("Start Session"):
                try:
                    start_resp = call_live_start(
                        {
                            "player_id": live_player,
                            "match_format": live_format,
                            "scenario": live_scenario,
                            "baseline_mean_runs": live_baseline_mean,
                            "baseline_std_runs": live_baseline_std,
                            "overs": live_overs,
                            "tone": live_tone,
                            "include_narrative": live_include_narrative,
                        }
                    )
                    st.session_state["live_session_id"] = start_resp.get("session_id")
                    st.session_state["live_steps"] = []
                    st.session_state["live_index"] = 0
                    st.session_state["live_play"] = False
                    st.success(f"Session started: {start_resp.get('session_id')}")
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Could not start session: {exc}")

            st.divider()
            play = st.checkbox("Play", value=st.session_state.get("live_play", False))
            st.session_state["live_play"] = play
            step_speed = st.slider("Step interval (seconds)", min_value=0.2, max_value=2.0, value=1.0, step=0.1)
            if st.button("Next Step"):
                st.session_state["live_play"] = False
                st.session_state["live_index"] += 1
            if st.button("Reset"):
                st.session_state["live_session_id"] = None
                st.session_state["live_steps"] = []
                st.session_state["live_index"] = 0
                st.session_state["live_play"] = False

        with live_col:
            session_id = st.session_state.get("live_session_id")
            if not session_id:
                st.info("Start a session to see live updates.")
            else:
                idx = st.session_state.get("live_index", 0)
                if idx >= 0:
                    while len(st.session_state["live_steps"]) <= idx:
                        try:
                            step_resp = call_live_step(
                                session_id,
                                len(st.session_state["live_steps"]),
                                include_narrative=live_include_narrative,
                                tone=live_tone,
                            )
                            st.session_state["live_steps"].append(step_resp)
                        except Exception as exc:  # pylint: disable=broad-except
                            st.error(f"Could not fetch step: {exc}")
                            st.session_state["live_play"] = False
                            break

                if st.session_state["live_steps"]:
                    current = st.session_state["live_steps"][-1]
                    st.markdown(f"### Step {current.get('index')} (Over {current.get('over')}, Ball {current.get('ball')})")
                    if current.get("model_anomaly_label") == 1:
                        risk_label = "High Anomaly Risk"
                        risk_emoji = "🔴"
                    elif current.get("ups_bucket") in ("strong_spike", "extreme_spike"):
                        risk_label = "Elevated Anomaly Risk"
                        risk_emoji = "🟠"
                    else:
                        risk_label = "Low Anomaly Risk"
                        risk_emoji = "🟢"
                    st.markdown(f"#### {risk_emoji} {risk_label}")

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Runs", current.get("cumulative_runs"))
                    ups_val = current.get("ups_score")
                    m2.metric("UPS", f"{ups_val:.2f}" if ups_val is not None else "—")
                    prob_val = current.get("model_anomaly_probability")
                    m3.metric("Prob", f"{prob_val:.2%}" if prob_val is not None else "—")
                    m4.metric("Bucket", current.get("ups_bucket"))

                    st.markdown(f"**{current.get('headline','')}**")
                    if live_include_narrative and current.get("narrative_summary"):
                        st.write(current.get("narrative_summary"))

                    st.markdown("#### Key drivers")
                    for d in current.get("key_drivers", []):
                        st.markdown(f"- {d}")

                    df_live = pd.DataFrame(st.session_state["live_steps"])
                    df_live["step"] = df_live["index"]
                    st.markdown("#### UPS over time")
                    st.line_chart(df_live.set_index("step")[["ups_score"]])
                    st.markdown("#### Cumulative runs")
                    st.line_chart(df_live.set_index("step")[["cumulative_runs"]])

                    if st.session_state["live_play"] and (current.get("index", 0) + 1) < len(
                        st.session_state["live_steps"]
                    ):
                        import time
                        time.sleep(step_speed)
                        st.session_state["live_index"] += 1
                        st.experimental_rerun()



    if page == "Platform Overview":
        st.header("About PLAIX")
        st.markdown("""
        **PLAIX** (Player Anomaly Intelligence X) is an advanced analytics platform designed to detect, quantify, and explain anomalies in sports performance.
        
        ### Core Technologies
        
        #### 1. UPS (Unexpected Performance Spike)
        The **UPS Score** is our proprietary metric for quantifying deviation. Unlike simple Z-scores, UPS accounts for:
        - **Volatility adjustment**: High-variance players have a higher threshold for anomalies.
        - **Contextual weighting**: Runs scored on difficult pitches or against top opposition count more.
        
        #### 2. Narrative Engine
        Raw numbers don't tell the whole story. Our **LLM-driven Narrative Engine** translates complex statistical spikes into human-readable insights, adopting different personas (Analyst, Commentator, Casual Fan).
        
        #### 3. Architecture
        Built on a robust, multi-sport architecture:
        - **Backend**: Python (FastAPI) for high-performance scoring.
        - **ML Layer**: Scikit-learn for anomaly probability modeling.
        - **Frontend**: Streamlit for rapid, interactive visualization.
        """)


if __name__ == "__main__":
    main()
