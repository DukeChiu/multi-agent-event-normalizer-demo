from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def event_display_label(payload: Mapping[str, Any]) -> str:
    """Build a compact label for event lists in developer tools."""
    event = normalize_event(payload)
    event_type = event["type"].replace("_", " ").replace(".", " / ").title()
    return f"{event_type} [{event['source']}] #{event['id']}"
