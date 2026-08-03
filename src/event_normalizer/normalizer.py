from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


def normalize_event(payload: Mapping[str, Any]) -> dict[str, str]:
    """Normalize an external webhook payload for internal processing."""
    if not isinstance(payload, Mapping):
        raise InvalidEventError("payload must be a mapping")

    event_id = _required_text(payload, "id")
    event_type = _required_text(payload, "type").lower()
    source = _optional_text(payload, "source", default="unknown").lower()

    return {"id": event_id, "type": event_type, "source": source}


def _reject_control_characters(value: str, key: str) -> None:
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise InvalidEventError(f"{key} must not contain control characters")


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if value is None:
        raise InvalidEventError(f"{key} is required")
    normalized = str(value).strip()
    if not normalized:
        raise InvalidEventError(f"{key} must not be blank")
    _reject_control_characters(normalized, key)
    return normalized


def _optional_text(payload: Mapping[str, Any], key: str, *, default: str) -> str:
    value = payload.get(key)
    if value is None:
        return default
    normalized = str(value).strip()
    if not normalized:
        return default
    _reject_control_characters(normalized, key)
    return normalized
