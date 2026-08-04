from collections.abc import Mapping
from datetime import datetime
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def warehouse_object_key(payload: Mapping[str, Any], occurred_at: str) -> str:
    """Build a date-partitioned object key for an analytics warehouse."""
    try:
        timestamp = datetime.fromisoformat(str(occurred_at).replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidEventError("warehouse timestamp must be ISO-8601") from exc
    event = normalize_event(payload)
    day = timestamp.date().isoformat()
    return (
        f"events/source={event['source']}/type={event['type']}/"
        f"day={day}/{event['id']}.json"
    )
