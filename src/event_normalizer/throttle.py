from collections import defaultdict
from time import monotonic
from typing import Callable

from event_normalizer.errors import InvalidEventError


class SourceThrottle:
    """Reject sources that exceed a fixed-window delivery budget."""

    def __init__(
        self,
        *,
        limit: int = 100,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if isinstance(limit, bool) or limit <= 0:
            raise InvalidEventError("throttle limit must be a positive integer")
        if window_seconds <= 0:
            raise InvalidEventError("throttle window must be positive")
        self._limit = limit
        self._window = window_seconds
        self._clock = clock
        self._events: dict[str, list[float]] = defaultdict(list)

    def allow(self, source: str) -> bool:
        now = self._clock()
        window_start = now - self._window
        recent = [ts for ts in self._events[source] if ts >= window_start]
        self._events[source] = recent
        if len(recent) >= self._limit:
            return False
        self._events[source].append(now)
        return True

    def check(self, source: str) -> None:
        if not self.allow(source):
            raise InvalidEventError(f"source is throttled: {source}")
