"""LLM-based anomaly narration for cricket UPS outputs (design with dummy backend)."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Protocol, Optional


class LLMClient(Protocol):
    """Protocol for LLM clients."""

    def generate(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """Return a string response given a prompt."""


@dataclass
class AnomalyEvent:
    """Structured anomaly event for narration."""

    player_id: str
    match_format: str  # e.g., "T20", "ODI", "TEST"
    team: str | None
    opposition: str | None
    venue: str | None
    baseline_mean_runs: float
    baseline_std_runs: float
    current_runs: float
    ups_score: float
    ups_bucket: str  # "normal", "mild_spike", "strong_spike", "extreme_spike"
    ups_anomaly_flag_baseline: int  # 0/1
    model_anomaly_probability: float
    model_anomaly_label: int  # 0/1
    match_context: Dict[str, Any] | None = None


class DummyLLMClient:
    """Rule-based dummy LLM client (no external calls)."""

    def generate(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:  # pragma: no cover - simple passthrough
        return "DUMMY_RESPONSE"

    def generate_from_event(self, event: AnomalyEvent) -> Dict[str, str]:
        """Return a basic narrative without external LLM calls."""
        title = "UPS anomaly detected"
        if event.ups_bucket in {"strong_spike", "extreme_spike"}:
            title = "Huge spike in batting performance"
        elif event.model_anomaly_label == 1 and event.ups_bucket == "normal" and event.current_runs < event.baseline_mean_runs:
            title = "Unusual dip in batting performance"
        summary = (
            f"{event.player_id} ({event.match_format}) scored {event.current_runs:.0f} runs "
            f"vs baseline {event.baseline_mean_runs:.0f}. UPS={event.ups_score:.2f} ({event.ups_bucket}), "
            f"model anomaly probability={event.model_anomaly_probability:.2f}."
        )
        return {"narrative_title": title, "narrative_summary": summary}


class AnomalyNarrator:
    """Generate human-readable narratives for detected anomalies."""

    def __init__(self, llm_client: LLMClient):
        """
        Args:
            llm_client: abstraction over LLM providers. Plug in real providers later.
        Notes:
            - This layer is optional; adds explainability on top of UPS/model outputs.
            - For production, replace DummyLLMClient with a real client (OpenAI, etc.).
        """
        self.llm_client = llm_client

    def _build_prompt(self, event: AnomalyEvent) -> str:
        """Build a prompt suitable for an LLM backend."""
        event_dict = asdict(event)
        prompt = (
            "You are an assistant that explains cricket batting anomalies.\n"
            "Given the following JSON of an innings and its anomaly scores, "
            "write a short title and 2–3 sentence summary for a human user.\n"
            f"JSON: {json.dumps(event_dict)}\n"
            "Respond in JSON with keys: narrative_title, narrative_summary."
        )
        return prompt

    def generate_description(self, event: AnomalyEvent) -> Dict[str, str]:
        """
        Generate a human-readable description for an anomaly event.

        Returns:
            Dict with narrative_title and narrative_summary.
        """
        if isinstance(self.llm_client, DummyLLMClient):
            return self.llm_client.generate_from_event(event)

        prompt = self._build_prompt(event)
        response = self.llm_client.generate(prompt)
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "narrative_title" in parsed and "narrative_summary" in parsed:
                return {"narrative_title": parsed["narrative_title"], "narrative_summary": parsed["narrative_summary"]}
        except Exception:  # pragma: no cover - fallback path
            pass
        return {"narrative_title": "Anomaly summary", "narrative_summary": response}
