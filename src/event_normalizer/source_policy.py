from collections.abc import Collection, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_event_from_sources(
    payload: Mapping[str, Any],
    allowed_sources: Collection[str],
) -> dict[str, str]:
    """Normalize an event and enforce a case-insensitive source allowlist."""
    event = normalize_event(payload)
    allowed = {source.strip().lower() for source in allowed_sources}
    if event["source"] not in allowed:
        raise InvalidEventError(f"source is not allowed: {event['source']}")
    return event
