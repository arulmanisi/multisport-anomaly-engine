You are my coding agent.

Goal:
Extend the narration layer to support multi-innings summaries, such as
a story over the last N innings for a player.

Assumptions:
- backend/llm/anomaly_narrator.py defines:
    - AnomalyEvent
    - AnomalyNarrator with generate_description(event, tone=...) -> dict

Tasks:

1) Add a new method for multi-event summaries
- In AnomalyNarrator, add:

    from typing import List

    def generate_sequence_summary(
        self,
        events: List[AnomalyEvent],
        tone: Tone = "analyst",
    ) -> dict:
        """
        Generate a narrative summary over a sequence of anomaly events
        (e.g., last 5 innings for a player).
        Returns a dict:
        {
          "summary_title": str,
          "summary_body": str,
        }
        """

2) Design the sequence prompt (for future real LLM usage)
- Implement a private method _build_sequence_prompt(self, events: List[AnomalyEvent], tone: Tone) -> str
  that:
    - Describes each innings briefly (format, current_runs vs baseline, UPS bucket).
    - Includes instructions:
        - Summarize trend over time.
        - Highlight spikes/dips.
        - Respect the tone (analyst/commentator/casual).
    - Returns a string suitable to send to an LLM.

3) Rule-based implementation for MVP
- For now, do NOT parse LLM output; instead, implement simple rule-based summary:
    - Compute:
        * Number of strong/extreme spikes.
        * Average UPS score across the sequence.
        * Whether UPS is trending up or down (compare first vs last).
    - Use this to construct:
        - summary_title, e.g.:
            - "High volatility in recent innings"
            - "Recent performance trending upwards"
            - "Recent performance stabilizing"
        - summary_body, e.g.:
            - "Across the last 5 T20 innings, the player recorded 2 strong spikes and an average UPS of 1.8σ, indicating a volatile but high-upside profile."
    - Vary wording slightly based on tone:
        - analyst → neutral, stat-heavy
        - commentator → more expressive
        - casual → friendly and simple

  Implement a helper:
      _build_rule_based_sequence_summary(events: List[AnomalyEvent], tone: Tone) -> dict

4) Make it easy to use from outside
- This method will be useful for:
    - A future "player profile" endpoint.
    - A UI tab showing "recent innings story".

- For now, you don’t need to hook it into REST or UI, but:
    - Add a short docstring example in AnomalyNarrator showing how it would be used:

        events = [...]  # last N AnomalyEvent objects
        summary = narrator.generate_sequence_summary(events, tone="analyst")

5) Leave clear TODOs
- In both _build_sequence_prompt and generate_sequence_summary, leave TODO comments indicating
  where a real LLMClient.generate() call would be integrated in the future to replace
  or augment the rule-based summary.

After implementing, show me:
- The updated AnomalyNarrator class with generate_sequence_summary(),
- And a brief code snippet (in a comment or docstring) showing intended usage.
