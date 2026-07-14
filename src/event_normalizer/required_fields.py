from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


def require_text(payload: Mapping[str, Any], field: str) -> str:
    """Return a trimmed required field with a domain-specific error."""
    if field not in payload:
        raise InvalidEventError(f"missing required field: {field}")

    value = str(payload[field]).strip()
    if not value:
        raise InvalidEventError(f"field must not be empty: {field}")
    return value
