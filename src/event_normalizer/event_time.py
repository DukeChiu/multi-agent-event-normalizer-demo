from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def parse_event_time(value: Any) -> datetime:
    """Parse ISO-8601 text or Unix seconds/milliseconds into UTC."""
    if isinstance(value, (int, float)):
        numeric = float(value)
        seconds = numeric / 1000.0 if abs(numeric) >= 1_000_000_000_000 else numeric
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError) as exc:
            raise InvalidEventError("event timestamp is outside the supported range") from exc

    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise InvalidEventError("event timestamp is malformed") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def event_ordering_key(payload: Mapping[str, Any]) -> tuple[datetime, str]:
    """Build a deterministic ordering key from event time and normalized identity."""
    event = normalize_event(payload)
    if "created_at" not in payload:
        raise InvalidEventError("event timestamp is required")
    return parse_event_time(payload["created_at"]), event["id"]
