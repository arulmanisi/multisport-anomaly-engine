"""Sport registry and dispatch helpers."""

from __future__ import annotations

from typing import Any, Callable, Dict, List


Handler = Callable[[List[dict]], List[dict]]


class SportRegistry:
    """Registry to route scoring requests to sport-specific handlers."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, sport: str, handler: Handler) -> None:
        self._handlers[sport.lower()] = handler

    def get(self, sport: str) -> Handler:
        handler = self._handlers.get(sport.lower())
        if handler is None:
            raise KeyError(f"Unsupported sport: {sport}")
        return handler

    def supported_sports(self) -> List[str]:
        return sorted(self._handlers.keys())


registry = SportRegistry()
