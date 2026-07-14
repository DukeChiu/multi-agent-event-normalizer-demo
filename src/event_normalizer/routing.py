from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def select_event_route(
    payload: Mapping[str, Any],
    routes: Mapping[str, str],
    *,
    default_route: str = "unmatched",
) -> str:
    """Select a destination from a normalized event type."""
    event = normalize_event(payload)
    normalized_routes = {
        str(event_type).strip().lower(): str(route).strip()
        for event_type, route in routes.items()
    }
    destination = normalized_routes.get(event["type"], default_route).strip()
    if not destination:
        raise InvalidEventError("event route must not be empty")
    return destination
