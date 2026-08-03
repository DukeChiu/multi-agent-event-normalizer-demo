from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_cloudevent(envelope: Mapping[str, Any]) -> dict[str, str]:
    """Map a CloudEvents 1.0 envelope to the normal event representation."""
    if not isinstance(envelope, Mapping):
        raise InvalidEventError("CloudEvent envelope must be a mapping")
    if str(envelope.get("specversion", "")).strip() != "1.0":
        raise InvalidEventError("CloudEvent specversion must be 1.0")

    return normalize_event(
        {
            "id": envelope.get("id"),
            "type": envelope.get("type"),
            "source": envelope.get("source"),
        }
    )
