from datetime import datetime, timedelta, timezone

from event_normalizer.errors import InvalidEventError


def is_event_expired(
    occurred_at: str,
    ttl_seconds: int,
    *,
    now: datetime | None = None,
) -> bool:
    """Return whether an ISO-8601 event timestamp is older than its TTL."""
    if isinstance(ttl_seconds, bool) or ttl_seconds < 0:
        raise InvalidEventError("event TTL must be a non-negative integer")
    try:
        parsed = datetime.fromisoformat(str(occurred_at).replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidEventError("event timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise InvalidEventError("event timestamp must include a timezone")

    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        raise InvalidEventError("reference time must include a timezone")
    return parsed + timedelta(seconds=ttl_seconds) < reference
