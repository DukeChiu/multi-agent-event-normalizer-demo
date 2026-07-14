from collections.abc import Iterable, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_events(
    payloads: Iterable[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Normalize a batch and reject duplicate event identifiers."""
    results = []
    seen_ids = set()

    for payload in payloads:
        event = normalize_event(payload)
        if event["id"] in seen_ids:
            raise InvalidEventError(
                f"duplicate event identifier: {event['id']}"
            )
        seen_ids.add(event["id"])
        results.append(event)

    return results
