from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


DEFAULT_MAX_PAYLOAD_BYTES = 1_000_000


def validate_payload_bytes(
    body: bytes | bytearray | str,
    *,
    max_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
) -> bytes:
    """Reject webhook bodies larger than the configured byte budget."""
    if isinstance(max_bytes, bool) or max_bytes <= 0:
        raise InvalidEventError("max payload size must be a positive integer")
    if isinstance(body, str):
        body = body.encode("utf-8")
    if not isinstance(body, (bytes, bytearray)):
        raise InvalidEventError("payload must be bytes")
    if len(body) > max_bytes:
        raise InvalidEventError(f"payload exceeds maximum size of {max_bytes} bytes")
    return bytes(body)
