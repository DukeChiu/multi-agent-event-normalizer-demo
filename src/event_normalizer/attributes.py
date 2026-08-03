from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_event_with_attributes(
    payload: Mapping[str, Any],
    *,
    prefix: str = "attr_",
    max_attributes: int = 16,
    max_value_length: int = 256,
) -> dict[str, Any]:
    """Preserve a bounded set of explicitly prefixed string attributes."""
    event: dict[str, Any] = normalize_event(payload)
    attributes = {
        str(key)[len(prefix) :]: str(value).strip()
        for key, value in payload.items()
        if str(key).startswith(prefix)
    }
    if len(attributes) > max_attributes:
        raise InvalidEventError("event contains too many custom attributes")
    if any(not key or len(value) > max_value_length for key, value in attributes.items()):
        raise InvalidEventError("event custom attribute is invalid")
    event["attributes"] = attributes
    return event
