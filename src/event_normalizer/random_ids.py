import uuid
from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def assign_random_id(payload: Mapping[str, Any]) -> dict[str, str]:
    """Replace the normalized event id with a fresh random identifier."""
    event = normalize_event(payload)
    event["id"] = uuid.uuid4().hex
    return event
