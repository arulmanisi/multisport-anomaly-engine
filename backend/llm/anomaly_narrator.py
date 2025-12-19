"""LLM-based anomaly narration for cricket UPS outputs (design with dummy backend)."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Protocol, Optional, Literal, List


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

    Tone = Literal["analyst", "commentator", "casual"]

    def __init__(self, llm_client: LLMClient):
        """
        Args:
            llm_client: abstraction over LLM providers. Plug in real providers later.
        Notes:
            - This layer is optional; adds explainability on top of UPS/model outputs.
            - For production, replace DummyLLMClient with a real client (OpenAI, etc.).
        """
        self.llm_client = llm_client

    def _build_prompt(self, event: AnomalyEvent, tone: Tone) -> str:
        """Build a prompt suitable for an LLM backend."""
        event_dict = asdict(event)
        prompt = (
            "You are an assistant that explains cricket batting anomalies.\n"
            f"Tone: {tone} (analyst = neutral/data-driven; commentator = energetic/broadcast; casual = simple/friendly).\n"
            "Given the following JSON of an innings and its anomaly scores, "
            "write a short title and 2–3 sentence summary for a human user.\n"
            f"JSON: {json.dumps(event_dict)}\n"
            "Respond in JSON with keys: narrative_title, narrative_summary."
        )
        return prompt

    def _build_rule_based_narrative(self, event: AnomalyEvent, tone: Tone) -> Dict[str, str]:
        """Rule-based narrative for dummy/offline mode with tone support."""
        if tone == "commentator":
            title = "This innings is off the charts!"
            summary = (
                f"The batter has smashed {event.current_runs:.0f} runs where they usually average "
                f"{event.baseline_mean_runs:.0f} – that's a huge jump and a clear breakout performance today."
            )
        elif tone == "casual":
            title = "Big game from this player"
            summary = (
                f"They scored {event.current_runs:.0f} runs versus a typical {event.baseline_mean_runs:.0f}, "
                "which is a big step up from their usual form."
            )
        else:  # analyst
            title = "Significant spike in batting performance"
            summary = (
                f"In this {event.match_format} innings, the player scored {event.current_runs:.0f} runs "
                f"versus a baseline of {event.baseline_mean_runs:.0f} (UPS {event.ups_score:.2f}), "
                "indicating a strong positive anomaly."
            )
        return {"narrative_title": title, "narrative_summary": summary}

    def generate_description(self, event: AnomalyEvent, tone: Tone = "analyst") -> Dict[str, str]:
        """
        Generate a human-readable description for an anomaly event.

        Returns:
            Dict with narrative_title and narrative_summary.
        """
        if isinstance(self.llm_client, DummyLLMClient):
            return self._build_rule_based_narrative(event, tone)

        prompt = self._build_prompt(event, tone)
        response = self.llm_client.generate(prompt)
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "narrative_title" in parsed and "narrative_summary" in parsed:
                return {"narrative_title": parsed["narrative_title"], "narrative_summary": parsed["narrative_summary"]}
        except Exception:  # pragma: no cover - fallback path
            pass
        return {"narrative_title": "Anomaly summary", "narrative_summary": response}

    def _build_sequence_prompt(self, events: List[AnomalyEvent], tone: Tone) -> str:
        """Build a prompt for an LLM to summarize multiple innings (future provider use)."""
        events_dicts = [asdict(e) for e in events]
        innings_lines = [
            f"Innings {idx}: format={e.match_format}, runs={e.current_runs} vs baseline={e.baseline_mean_runs}, "
            f"UPS={e.ups_score:.2f} ({e.ups_bucket})"
            for idx, e in enumerate(events, start=1)
        ]
        innings_block = "\n".join(innings_lines)
        prompt = (
            "You are an assistant that summarizes cricket batting anomaly sequences.\n"
            f"Tone: {tone} (analyst = neutral/data-driven; commentator = energetic/broadcast; casual = simple/friendly).\n"
            "Describe each innings briefly (format, runs vs baseline, UPS bucket), summarize trend over time, "
            "and highlight spikes/dips. Keep it concise and respect the tone.\n"
            f"Innings summaries:\n{innings_block}\n"
            f"Raw JSON: {json.dumps(events_dicts)}\n"
            "Respond in JSON with keys: summary_title, summary_body."
        )
        # TODO: in future, pass this prompt to a real LLM client for richer narratives.
        return prompt

    def _build_rule_based_sequence_summary(self, events: List[AnomalyEvent], tone: Tone) -> Dict[str, str]:
        """Rule-based sequence summary with tone-aware wording."""
        if not events:
            return {"summary_title": "No data", "summary_body": "No innings available to summarize."}

        ups_values = [e.ups_score for e in events]
        avg_ups = sum(ups_values) / len(ups_values)
        first_ups, last_ups = ups_values[0], ups_values[-1]
        spikes = sum(1 for e in events if e.ups_bucket in {"strong_spike", "extreme_spike"})

        trend = "stable"
        if last_ups > first_ups + 0.5:
            trend = "upward"
        elif last_ups < first_ups - 0.5:
            trend = "downward"

        if tone == "commentator":
            title = "Momentum watch: recent innings story"
            body = (
                f"Over {len(events)} innings, there were {spikes} big spikes and an average UPS of {avg_ups:.2f}. "
                f"The trend looks {trend}, with the latest innings showing UPS {last_ups:.2f}."
            )
        elif tone == "casual":
            title = "How recent games look"
            body = (
                f"In the last {len(events)} innings, average UPS is {avg_ups:.2f} with {spikes} strong spikes. "
                f"Overall trend seems {trend}, ending at UPS {last_ups:.2f}."
            )
        else:  # analyst
            title = "Recent anomaly trend"
            body = (
                f"Across {len(events)} recent innings, average UPS is {avg_ups:.2f} with {spikes} strong/extreme spikes. "
                f"Trend: {trend} (first UPS {first_ups:.2f}, last UPS {last_ups:.2f})."
            )
        return {"summary_title": title, "summary_body": body}

    def generate_sequence_summary(self, events: List[AnomalyEvent], tone: Tone = "analyst") -> Dict[str, str]:
        """
        Generate a narrative summary over a sequence of anomaly events.

        Example usage:
            events = [...]  # list of AnomalyEvent objects (e.g., last N innings)
            summary = narrator.generate_sequence_summary(events, tone=\"analyst\")

        Returns:
            Dict with summary_title and summary_body.
        """
        # TODO: when a real LLM is configured, use _build_sequence_prompt and llm_client.generate
        if isinstance(self.llm_client, DummyLLMClient):
            return self._build_rule_based_sequence_summary(events, tone)

        prompt = self._build_sequence_prompt(events, tone)
        response = self.llm_client.generate(prompt)
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict) and "summary_title" in parsed and "summary_body" in parsed:
                return {"summary_title": parsed["summary_title"], "summary_body": parsed["summary_body"]}
        except Exception:  # pragma: no cover - fallback path
            pass
        return {"summary_title": "Anomaly sequence summary", "summary_body": response}
