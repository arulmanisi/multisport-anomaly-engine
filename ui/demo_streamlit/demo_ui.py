"""Streamlit demo for Plaix.ai Cricket UPS Anomaly Engine."""

import os
import json

import requests
import streamlit as st

API_URL = os.getenv("PLAIX_API_URL", "http://localhost:8000/predict/single")


def main() -> None:
    st.set_page_config(
        page_title="Plaix.ai – Cricket Anomaly Engine",
        page_icon="🏏",
        layout="centered",
    )

    st.title("🏏 Plaix.ai – Cricket UPS Anomaly Engine")
    st.markdown("This UI calls the Plaix.ai Cricket UPS Anomaly Engine end-to-end.")

    st.subheader("Input")
    player_id = st.text_input("Player ID", "P1")
    match_format = st.selectbox("Format", ["T20", "ODI", "TEST"], index=0)
    baseline_mean_runs = st.number_input("Baseline mean runs", value=22.0, step=1.0)
    baseline_std_runs = st.number_input("Baseline std runs", value=8.0, step=1.0)
    current_runs = st.number_input("Current runs", value=40.0, step=1.0)
    venue_flatness = st.slider("Venue flatness", 0.0, 1.0, 0.6)
    opposition_strength = st.slider("Opposition strength", 0.0, 1.0, 0.5)
    batting_position = st.number_input("Batting position", min_value=1, max_value=7, value=4)

    if st.button("Predict anomaly"):
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
            }
        }

        try:
            resp = requests.post(API_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.subheader("Prediction")
            st.json(data)
        except Exception as exc:  # pylint: disable=broad-except
            st.error(f"Request failed: {exc}")
            st.info("Check PLAIX_API_URL or backend availability.")


if __name__ == "__main__":
    main()
