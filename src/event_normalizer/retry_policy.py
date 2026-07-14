from event_normalizer.errors import InvalidEventError


def retry_delay_seconds(
    attempt: int,
    *,
    base_seconds: int = 2,
    maximum_seconds: int = 300,
) -> int:
    """Return a capped exponential delay for a zero-based delivery attempt."""
    if isinstance(attempt, bool) or attempt < 0:
        raise InvalidEventError("retry attempt must be a non-negative integer")
    if base_seconds <= 0 or maximum_seconds <= 0:
        raise InvalidEventError("retry delays must be positive")
    return min(maximum_seconds, base_seconds * (2**attempt))
