"""REST-style inference service design (structure only)."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

# TODO: Uncomment when wiring real FastAPI app.
# from fastapi import FastAPI

from plaix.core.model import AnomalyModel
from plaix.core.ups_scorer import BaselineStats, UPSScorer
from plaix.sports.cricket.features import CricketFeatureExtractor
from llm.anomaly_narrator import AnomalyEvent, AnomalyNarrator
from llm.factory import get_llm_client_from_env


class SinglePredictRequest(BaseModel):
    """Request payload for single prediction."""

    payload: dict
    tone: str | None = None
    model_path: str | None = None


class SinglePredictResponse(BaseModel):
    """Response payload for single prediction."""

    ups_score: float
    ups_bucket: str
    ups_anomaly_flag_baseline: int
    model_anomaly_probability: float
    model_anomaly_label: int
    explanation: str | None = None
    narrative_title: str | None = None
    narrative_summary: str | None = None


class BatchPredictRequest(BaseModel):
    """Request payload for batch prediction."""

    records: List[dict]
    model_path: str | None = None


class BatchPredictResponse(BaseModel):
    """Response payload for batch prediction."""

    results: List[SinglePredictResponse]


class RecentSummaryRequest(BaseModel):
    """Request for recent innings narrative summary."""

    player_id: str
    match_format: str = "T20"
    n: int = 5
    tone: str | None = None


class NarrateRequest(BaseModel):
    """Request payload for narration-only endpoint."""

    player_id: str
    match_format: str = "T20"
    team: str | None = None
    opposition: str | None = None
    venue: str | None = None
    baseline_mean_runs: float | None = None
    baseline_std_runs: float | None = None
    current_runs: float
    ups_score: float | None = None
    ups_bucket: str | None = None
    ups_anomaly_flag_baseline: int | None = None
    model_anomaly_probability: float | None = None
    model_anomaly_label: int | None = None
    tone: str | None = None


class NarrateResponse(BaseModel):
    """Response payload for narration-only endpoint."""

    narrative_title: str | None = None
    narrative_summary: str | None = None


class DummyHistoryProvider:
    """Simple history provider stub."""

    def get_player_innings_history(self, player_id: str, match_format: str):
        return []


def extract_features(payload: Dict[str, Any]) -> Dict[str, float]:
    """Build feature vector consistent with training."""
    return {
        "baseline_mean_runs": float(payload["baseline_mean_runs"]),
        "baseline_std_runs": float(payload["baseline_std_runs"]),
        "current_runs": float(payload["current_runs"]),
        "venue_flatness": float(payload.get("venue_flatness", 0.5)),
        "opposition_strength": float(payload.get("opposition_strength", 0.5)),
        "batting_position": int(payload.get("batting_position", 4)),
    }


class InferenceService:
    """Inference service that wires UPS scoring and model inference."""

    def __init__(self, model_path: str | None = None) -> None:
        self.feature_extractor = self._load_feature_extractor()
        self.ups_scorer = UPSScorer(DummyHistoryProvider())
        self.model = self._load_model(model_path)
        self.narrator = AnomalyNarrator(get_llm_client_from_env())
        self.demo_events = self._load_demo_events()

    def _load_feature_extractor(self) -> CricketFeatureExtractor:
        """Construct feature extractor (placeholder)."""
        return CricketFeatureExtractor()

    def _load_model(self, model_path: str | None) -> AnomalyModel:
        """Load model wrapper and weights."""
        model = AnomalyModel(model_type="logistic_regression", model_config={}, sport="cricket")
        if model_path:
            try:
                model.load_model(model_path)
            except FileNotFoundError:
                # Model artifact missing; continue with uninitialized model for demo/testing.
                pass
        return model

    def preprocess_input(self, payload: dict) -> Dict[str, float]:
        """Validate and convert raw payload to feature representation."""
        if "baseline_mean_runs" not in payload or "baseline_std_runs" not in payload:
            baseline = BaselineStats(mean_runs=20.0, std_runs=15.0, num_innings=0, source="default")
            payload["baseline_mean_runs"] = baseline.mean_runs
            payload["baseline_std_runs"] = baseline.std_runs
        return extract_features(payload)

    def run_inference(self, payload: dict, tone: str = "analyst") -> SinglePredictResponse:
        """Run UPS scoring + model inference for a single record."""
        ups_score = self.ups_scorer.compute_ups_score(
            payload.get("player_id", "unknown"),
            payload.get("match_format", "T20"),
            current_runs=float(payload["current_runs"]),
        )
        flag, bucket = self.ups_scorer.classify_ups(ups_score)
        features = self.preprocess_input(payload)
        proba = float(self.model.predict_proba([[features[c] for c in features]])[0][1])
        label = int(self.model.predict([[features[c] for c in features]])[0])
        event = AnomalyEvent(
            player_id=payload.get("player_id", "unknown"),
            match_format=payload.get("match_format", "T20"),
            team=payload.get("team"),
            opposition=payload.get("opposition"),
            venue=payload.get("venue"),
            baseline_mean_runs=payload["baseline_mean_runs"],
            baseline_std_runs=payload["baseline_std_runs"],
            current_runs=float(payload["current_runs"]),
            ups_score=ups_score,
            ups_bucket=bucket,
            ups_anomaly_flag_baseline=flag,
            model_anomaly_probability=proba,
            model_anomaly_label=label,
            match_context=payload.get("match_context", {}),
        )
        narration = {"narrative_title": None, "narrative_summary": None}
        try:
            narration = self.narrator.generate_description(event, tone=tone or "analyst")
        except Exception:
            # TODO: add logging; narration optional
            narration = {"narrative_title": None, "narrative_summary": None}

        return SinglePredictResponse(
            ups_score=ups_score,
            ups_bucket=bucket,
            ups_anomaly_flag_baseline=flag,
            model_anomaly_probability=proba,
            model_anomaly_label=label,
            explanation=None,
            narrative_title=narration.get("narrative_title"),
            narrative_summary=narration.get("narrative_summary"),
        )

    def _load_demo_events(self) -> List[dict]:
        """Load or synthesize a small demo set of innings for trend view."""
        demo = []
        for idx, runs in enumerate([18, 24, 32, 15, 55, 42, 28, 65, 33, 48], start=1):
            baseline_mean = 25.0
            baseline_std = 8.0
            ups_score = (runs - baseline_mean) / max(baseline_std, 1.0)
            flag, bucket = self.ups_scorer.classify_ups(ups_score)
            proba = min(max(0.2 + 0.05 * ups_score, 0.01), 0.99)
            demo.append(
                {
                    "date": f"2024-0{(idx % 9) + 1}-0{(idx % 27) + 1}",
                    "player_id": "P_DEMO",
                    "match_format": "T20",
                    "current_runs": runs,
                    "baseline_mean_runs": baseline_mean,
                    "baseline_std_runs": baseline_std,
                    "ups_score": ups_score,
                    "ups_bucket": bucket,
                    "ups_anomaly_flag_baseline": flag,
                    "model_anomaly_probability": proba,
                    "model_anomaly_label": 1 if proba > 0.55 else 0,
                }
            )
        return demo

    def get_recent_events(self, player_id: str, match_format: str, n: int = 5) -> List[dict]:
        """Return last N demo events (placeholder for real data source)."""
        filtered = [e for e in self.demo_events if e["player_id"] == player_id and e["match_format"] == match_format]
        if not filtered and player_id != "P_DEMO":
            # Fallback to demo data for non-demo player IDs
            filtered = [e for e in self.demo_events if e["player_id"] == "P_DEMO" and e["match_format"] == match_format]
        return filtered[-n:]

    def summarize_recent_events(self, player_id: str, match_format: str, n: int, tone: str = "analyst") -> dict:
        """Return recent events plus multi-event narrative."""
        events = self.get_recent_events(player_id, match_format, n)
        anomaly_events = [
            AnomalyEvent(
                player_id=e["player_id"],
                match_format=e["match_format"],
                team=None,
                opposition=None,
                venue=None,
                baseline_mean_runs=e["baseline_mean_runs"],
                baseline_std_runs=e["baseline_std_runs"],
                current_runs=e["current_runs"],
                ups_score=e["ups_score"],
                ups_bucket=e["ups_bucket"],
                ups_anomaly_flag_baseline=e["ups_anomaly_flag_baseline"],
                model_anomaly_probability=e["model_anomaly_probability"],
                model_anomaly_label=e["model_anomaly_label"],
                match_context={},
            )
            for e in events
        ]
        summary = {"summary_title": None, "summary_body": None}
        try:
            summary = self.narrator.generate_sequence_summary(anomaly_events, tone=tone or "analyst")
        except Exception:
            summary = {"summary_title": None, "summary_body": None}
        return {"events": events, **summary}

    def narrate_only(self, request: NarrateRequest) -> NarrateResponse:
        """Generate narration from precomputed anomaly inputs."""
        baseline_mean = request.baseline_mean_runs if request.baseline_mean_runs is not None else 20.0
        baseline_std = request.baseline_std_runs if request.baseline_std_runs is not None else 10.0
        event = AnomalyEvent(
            player_id=request.player_id,
            match_format=request.match_format,
            team=request.team,
            opposition=request.opposition,
            venue=request.venue,
            baseline_mean_runs=baseline_mean,
            baseline_std_runs=baseline_std,
            current_runs=request.current_runs,
            ups_score=request.ups_score if request.ups_score is not None else 0.0,
            ups_bucket=request.ups_bucket if request.ups_bucket is not None else "normal",
            ups_anomaly_flag_baseline=request.ups_anomaly_flag_baseline if request.ups_anomaly_flag_baseline is not None else 0,
            model_anomaly_probability=request.model_anomaly_probability if request.model_anomaly_probability is not None else 0.0,
            model_anomaly_label=request.model_anomaly_label if request.model_anomaly_label is not None else 0,
            match_context={},
        )
        narrative = self.narrator.generate_description(event, tone=request.tone or "commentator")
        return NarrateResponse(**narrative)


# TODO: Uncomment and wire FastAPI when ready.
# app = FastAPI(title="PLAIX Inference Service")
# service = InferenceService(model_path="models/ups_logreg.pkl")
#
# @app.post("/predict/single", response_model=SinglePredictResponse)
# def predict_single(request: SinglePredictRequest) -> SinglePredictResponse:
#     """
#     Predict UPS score and anomaly probability for a single payload.
#     """
#     return service.run_inference(request.payload)
#
# @app.post("/predict/batch", response_model=BatchPredictResponse)
# def predict_batch(request: BatchPredictRequest) -> BatchPredictResponse:
#     """
#     Predict UPS score and anomaly probability for a batch of payloads.
#     """
#     results: List[SinglePredictResponse] = [service.run_inference(rec) for rec in request.records]
#     return BatchPredictResponse(results=results)
