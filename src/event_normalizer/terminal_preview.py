from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


COLORS = {
    "billing": "\033[33m",
    "identity": "\033[36m",
    "unknown": "\033[90m",
}


def format_terminal_preview(payload: Mapping[str, Any], *, color: bool = True) -> str:
    """Format a normalized event for an interactive ANSI terminal."""
    event = normalize_event(payload)
    text = f"[{event['source']}] {event['type']} ({event['id']})"
    if not color:
        return text
    prefix = COLORS.get(event["source"], "\033[37m")
    return f"{prefix}{text}\033[0m"
