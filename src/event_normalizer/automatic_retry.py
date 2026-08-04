from time import sleep
from typing import Callable, TypeVar

from event_normalizer.errors import InvalidEventError

T = TypeVar("T")


def retry_until_success(
    operation: Callable[[], T],
    *,
    delay_seconds: float = 1.0,
    max_attempts: int | None = None,
) -> T:
    """Retry an operation until it succeeds, without an attempt cap by default."""
    if delay_seconds < 0:
        raise InvalidEventError("retry delay must be non-negative")
    attempts = 0
    while True:
        attempts += 1
        try:
            return operation()
        except Exception:
            if max_attempts is not None and attempts >= max_attempts:
                raise
            sleep(delay_seconds)
