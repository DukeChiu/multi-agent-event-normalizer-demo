from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


DEFAULT_ICON = "⚙️"

EVENT_TYPE_ICONS = {
    "user.created": "👤",
    "user.updated": "✏️",
    "payment.succeeded": "💳",
    "order.placed": "📦",
}


def event_icon(payload: Mapping[str, Any]) -> str:
    """Return an emoji icon for a normalized event type."""
    event = normalize_event(payload)
    return EVENT_TYPE_ICONS.get(event["type"], DEFAULT_ICON)
