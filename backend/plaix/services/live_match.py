"""Live match simulation endpoints (MVP, deterministic scenarios)."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from typing import Dict, List

from fastapi import HTTPException

from plaix.api.inference import InferenceService
from llm.anomaly_narrator import AnomalyEvent, AnomalyNarrator
from llm.factory import get_llm_client_from_env


@dataclass
class LiveSession:
    steps: List[dict]
    payload: dict


_sessions: Dict[str, LiveSession] = {}
_inference = InferenceService(model_path="models/ups_logreg.pkl")
_narrator = AnomalyNarrator(get_llm_client_from_env())


def generate_innings_stream(seed: int, overs: int = 20, scenario: str = "normal") -> List[dict]:
    """Create deterministic innings steps."""
    rnd = random.Random(seed)
    steps: List[dict] = []
    cumulative_runs = 0
    cumulative_balls = 0
    for over in range(1, overs + 1):
        for ball in range(1, 7):
            cumulative_balls += 1
            if scenario == "breakout" and over > max(6, overs // 3):
                base = 6
                spread = 4
            elif scenario == "collapse" and over <= max(6, overs // 3):
                base = 1
                spread = 2
            else:
                base = 3
                spread = 2
            runs_this_ball = max(0, int(rnd.gauss(base, spread)))
            cumulative_runs += runs_this_ball
            steps.append(
                {
                    "index": len(steps),
                    "over": over,
                    "ball": ball,
                    "runs_this_ball": runs_this_ball,
                    "cumulative_runs": cumulative_runs,
                    "cumulative_balls": cumulative_balls,
                }
            )
    return steps


def start_session(request: dict) -> dict:
    """Start a live session and return session id."""
    session_id = str(uuid.uuid4())
    steps = generate_innings_stream(
        seed=int(uuid.uuid4().int % 1_000_000),
        overs=int(request.get("overs", 20)),
        scenario=request.get("scenario", "normal"),
    )
    _sessions[session_id] = LiveSession(steps=steps, payload=request)
    return {"session_id": session_id, "total_steps": len(steps)}


def _build_headline(event: dict) -> str:
    bucket = event.get("ups_bucket", "normal")
    runs = event.get("current_runs", 0)
    fmt = event.get("match_format", "T20")
    player = event.get("player_id", "player")
    if bucket in {"extreme_spike", "strong_spike"}:
        return f"{player} surges in {fmt}: {runs} runs and climbing"
    if bucket == "mild_spike":
        return f"{player} finding rhythm in {fmt}, now at {runs}"
    return f"{player} steady at {runs} in {fmt}"


def _build_key_drivers(ups_score: float) -> List[str]:
    if ups_score >= 3:
        return [f"Extreme spike (~{ups_score:.1f}σ)", "Momentum building fast", "Well above baseline expectation"]
    if ups_score >= 2:
        return [f"Strong spike (~{ups_score:.1f}σ)", "Performance accelerating", "Outpacing typical innings"]
    if ups_score >= 1:
        return [f"Moderate spike (~{ups_score:.1f}σ)", "Positive momentum", "Slightly above baseline"]
    return [f"Near baseline (~{ups_score:.1f}σ)", "Stable progress", "No major anomaly detected"]


def get_step(session_id: str, index: int, include_narrative: bool = False, tone: str = "commentator") -> dict:
    """Return a scored step."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = _sessions[session_id]
    if index < 0 or index >= len(session.steps):
        raise HTTPException(status_code=404, detail="Step not found")
    step = session.steps[index]
    payload = session.payload
    current_runs = step["cumulative_runs"]
    scoring_payload = {
        "player_id": payload.get("player_id", "P_LIVE"),
        "match_format": payload.get("match_format", "T20"),
        "baseline_mean_runs": payload.get("baseline_mean_runs", 20.0),
        "baseline_std_runs": payload.get("baseline_std_runs", 10.0),
        "current_runs": current_runs,
        "venue_flatness": payload.get("venue_flatness", 0.5),
        "opposition_strength": payload.get("opposition_strength", 0.5),
        "batting_position": payload.get("batting_position", 4),
    }
    scored = _inference.run_inference(scoring_payload, tone=tone or "commentator")
    event_dict = {
        "session_id": session_id,
        "index": index,
        "over": step["over"],
        "ball": step["ball"],
        "cumulative_runs": current_runs,
        "cumulative_balls": step["cumulative_balls"],
        "baseline_mean_runs": scoring_payload["baseline_mean_runs"],
        "baseline_std_runs": scoring_payload["baseline_std_runs"],
        "ups_score": scored.ups_score,
        "ups_bucket": scored.ups_bucket,
        "ups_anomaly_flag_baseline": scored.ups_anomaly_flag_baseline,
        "model_anomaly_probability": scored.model_anomaly_probability,
        "model_anomaly_label": scored.model_anomaly_label,
    }
    event_dict["headline"] = _build_headline(
        {
            "ups_bucket": scored.ups_bucket,
            "current_runs": current_runs,
            "match_format": scoring_payload["match_format"],
            "player_id": scoring_payload["player_id"],
        }
    )
    event_dict["key_drivers"] = _build_key_drivers(scored.ups_score)

    if include_narrative:
        try:
            event = AnomalyEvent(
                player_id=scoring_payload["player_id"],
                match_format=scoring_payload["match_format"],
                team=None,
                opposition=None,
                venue=None,
                baseline_mean_runs=scoring_payload["baseline_mean_runs"],
                baseline_std_runs=scoring_payload["baseline_std_runs"],
                current_runs=current_runs,
                ups_score=scored.ups_score,
                ups_bucket=scored.ups_bucket,
                ups_anomaly_flag_baseline=scored.ups_anomaly_flag_baseline,
                model_anomaly_probability=scored.model_anomaly_probability,
                model_anomaly_label=scored.model_anomaly_label,
                match_context={},
            )
            narrative = _narrator.generate_description(event, tone=tone or "commentator")
            event_dict.update(narrative)
        except Exception:
            pass
    return event_dict


def stop_session(session_id: str) -> dict:
    """Delete session."""
    _sessions.pop(session_id, None)
    return {"status": "stopped", "session_id": session_id}
