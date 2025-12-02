"""Example script to score a sample CSV."""

from __future__ import annotations

from pathlib import Path

from plaix.data.baselines import attach_baselines, compute_phase_baselines
from plaix.data.loader import load_events_csv
from plaix.models.anomaly_scorer import AnomalyRequest, score_events


def main() -> None:
    csv_path = Path(__file__).resolve().parent / "sample_events.csv"
    df = load_events_csv(csv_path)
    baselines = compute_phase_baselines(df)
    df_with_expected = attach_baselines(df, baselines)

    events = [
        AnomalyRequest(
            match_id=row["match_id"],
            over=int(row["over"]),
            ball=int(row["ball"]),
            runs=float(row["runs"]),
            wickets=float(row["wickets"]),
        )
        for _, row in df_with_expected.iterrows()
    ]
    results = score_events(events)
    anomalies = [r for r in results if r.is_anomaly]

    print(f"Scored {len(results)} events; anomalies: {len(anomalies)}")
    for res in anomalies:
        print(
            f"{res.match_id} over {res.over}.{res.ball}: score={res.anomaly_score:.2f} reason={res.reason}"
        )


if __name__ == "__main__":
    main()
