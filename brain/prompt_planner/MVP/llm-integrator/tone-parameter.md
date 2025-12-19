You are my coding agent.

Goal:
Extend the AnomalyNarrator to support different tones for the generated
description, such as "casual", "analyst", "commentator".

Assumptions:
- backend/llm/anomaly_narrator.py defines:
    - AnomalyEvent
    - LLMClient
    - DummyLLMClient
    - AnomalyNarrator with generate_description(event) -> dict

Tasks:

1) Extend AnomalyNarrator API
- Modify generate_description to accept an optional tone parameter:

    from typing import Literal

    Tone = Literal["analyst", "commentator", "casual"]

    def generate_description(self, event: AnomalyEvent, tone: Tone = "analyst") -> dict:
        ...

- Store tone in the method call only; AnomalyNarrator itself does not need a tone attribute.

2) Include tone in prompt
- Update _build_prompt(self, event: AnomalyEvent, tone: Tone) -> str:
    - Add a short instruction at the top such as:
        - "Tone: analyst" → neutral, data-driven, concise.
        - "Tone: commentator" → energetic, broadcast-style language.
        - "Tone: casual" → simple, friendly explanations.
    - Make the tone explicit in the prompt string.

- Update generate_description() to pass tone into _build_prompt.

3) Rule-based behavior for DummyLLMClient
- In generate_description(), continue to ignore the actual llm_client output for now,
  but adapt the narrative_title and narrative_summary based on tone.

  Example:
    - analyst:
        title: "Significant spike in batting performance"
        summary: "In this T20 innings, the player scored 60 runs versus a baseline of 22 (UPS 3.1σ), indicating a strong positive anomaly."
    - commentator:
        title: "This innings is off the charts!"
        summary: "The batter has smashed 60 runs where they usually average 22 – that’s a huge jump and a clear breakout performance today."
    - casual:
        title: "Big game from this player"
        summary: "They scored 60 runs versus a typical 22, which is a big step up from their usual form."

- Implement a clean helper inside AnomalyNarrator, like:
    _build_rule_based_narrative(event: AnomalyEvent, tone: Tone) -> dict

4) REST + CLI usage
- In the API and CLI where AnomalyNarrator is called, keep tone default as "analyst" for now,
  but design the call so that changing tone later is trivial, e.g.:

    narrative = narrator.generate_description(event, tone="analyst")

- Optionally add a small TODO/comment where a query param or CLI flag could be used later
  to choose tone.

After implementing, show me:
- Updated AnomalyNarrator class (generate_description, _build_prompt, and tone handling),
- And one example call to generate_description() with tone specified.
