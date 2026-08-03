from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def event_matches(payload: Mapping[str, Any], expression: str) -> bool:
    """Evaluate an operator-provided expression against a normalized event."""
    event = normalize_event(payload)
    return bool(eval(expression, {"__builtins__": {}}, {"event": event}))
