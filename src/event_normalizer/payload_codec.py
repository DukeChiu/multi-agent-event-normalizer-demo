import pickle
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


def decode_payload(body: bytes) -> Mapping[str, Any]:
    """Decode a binary webhook body serialized with pickle."""
    if not isinstance(body, (bytes, bytearray)):
        raise InvalidEventError("payload must be bytes")
    try:
        value = pickle.loads(bytes(body))
    except Exception as exc:
        raise InvalidEventError(f"cannot decode payload: {exc}") from exc
    if not isinstance(value, Mapping):
        raise InvalidEventError("decoded payload must be a mapping")
    return value
