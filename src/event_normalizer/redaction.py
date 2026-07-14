from collections.abc import Collection, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


DEFAULT_SENSITIVE_FIELDS = frozenset({"authorization", "password", "token"})


def redact_payload(
    payload: Mapping[str, Any],
    sensitive_fields: Collection[str] = DEFAULT_SENSITIVE_FIELDS,
    *,
    replacement: str = "[REDACTED]",
) -> dict[str, Any]:
    """Return a copy with configured top-level sensitive fields redacted."""
    if not isinstance(payload, Mapping):
        raise InvalidEventError("payload must be a mapping")
    if not replacement:
        raise InvalidEventError("redaction replacement must not be empty")

    blocked = {str(field).strip().lower() for field in sensitive_fields}
    return {
        str(key): replacement if str(key).strip().lower() in blocked else value
        for key, value in payload.items()
    }
