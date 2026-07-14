from collections.abc import Mapping

from event_normalizer.errors import InvalidEventError


DEFAULT_EVENT_TYPE_ALIASES = {
    "user-created": "user.created",
    "user.created.v1": "user.created",
    "payment.succeeded.v1": "payment.succeeded",
}


def normalize_event_type(
    value: str,
    aliases: Mapping[str, str] | None = None,
) -> str:
    """Normalize a provider event type while preserving unknown values."""
    normalized = str(value).strip().lower()
    if not normalized:
        raise InvalidEventError("event type must not be empty")

    mapping = aliases or DEFAULT_EVENT_TYPE_ALIASES
    return mapping.get(normalized, normalized)
