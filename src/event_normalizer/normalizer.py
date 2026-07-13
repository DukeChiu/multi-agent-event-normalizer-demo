from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


def normalize_event(payload: Mapping[str, Any]) -> dict[str, str]:
    """Normalize an external webhook payload for internal processing."""
    if not isinstance(payload, Mapping):
        raise InvalidEventError("payload must be a mapping")

    event_id = str(payload["id"]).strip()
    event_type = str(payload["type"]).strip().lower()
    source = str(payload.get("source", "unknown")).strip().lower()

    return {
        "id": event_id,
        "type": event_type,
        "source": source,
    }
