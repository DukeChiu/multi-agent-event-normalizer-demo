from collections.abc import Iterable, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


class EventContractRegistry:
    """Validate normalized event types against source-specific contracts."""

    def __init__(self, contracts: Mapping[str, Iterable[str]]) -> None:
        normalized: dict[str, frozenset[str]] = {}
        for source, event_types in contracts.items():
            source_name = str(source).strip().lower()
            allowed = frozenset(
                str(event_type).strip().lower()
                for event_type in event_types
                if str(event_type).strip()
            )
            if not source_name or not allowed:
                raise ValueError("each event source requires at least one event type")
            normalized[source_name] = allowed
        if not normalized:
            raise ValueError("at least one event contract is required")
        self._contracts = normalized

    def validate(self, payload: Mapping[str, Any]) -> dict[str, str]:
        event = normalize_event(payload)
        allowed = self._contracts.get(event["source"])
        if allowed is None:
            raise InvalidEventError("event source has no registered contract")
        if event["type"] not in allowed:
            raise InvalidEventError("event type is not registered for its source")
        return event

    def supported_types(self, source: str) -> tuple[str, ...]:
        return tuple(sorted(self._contracts.get(str(source).strip().lower(), ())))
