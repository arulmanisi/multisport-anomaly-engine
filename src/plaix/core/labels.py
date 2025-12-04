"""Label creation abstractions and registry for PLAIX."""

from __future__ import annotations

from typing import Any, Callable, Dict

from pydantic import BaseModel


class LabelRequest(BaseModel):
    """Input payload for label creation."""

    sport: str
    match_json: Dict[str, Any]


class LabelResponse(BaseModel):
    """Label outputs keyed by label name."""

    labels: Dict[str, Any]


LabelFn = Callable[[Dict[str, Any]], Any]


class LabelRegistry:
    """Registry for label functions."""

    def __init__(self) -> None:
        self._registry: Dict[str, LabelFn] = {}

    def register_label(self, name: str, func: LabelFn) -> None:
        """Register a label function under a unique name."""
        self._registry[name] = func

    def get_label_output(self, name: str, match_json: Dict[str, Any]) -> Any:
        """Call a registered label function."""
        if name not in self._registry:
            raise KeyError(f"Label not registered: {name}")
        return self._registry[name](match_json)

    def available_labels(self) -> Dict[str, LabelFn]:
        """Return registered labels."""
        return dict(self._registry)


label_registry = LabelRegistry()
