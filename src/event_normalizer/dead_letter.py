from collections import deque
from collections.abc import Callable, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


class DeadLetterQueue:
    """Hold events that failed processing for later inspection or replay."""

    def __init__(self, *, capacity: int = 1000) -> None:
        if isinstance(capacity, bool) or capacity <= 0:
            raise InvalidEventError("dead-letter capacity must be a positive integer")
        self._capacity = capacity
        self._entries: deque[tuple[Mapping[str, Any], str]] = deque()

    def quarantine(self, payload: Mapping[str, Any], reason: str) -> None:
        if not isinstance(payload, Mapping):
            raise InvalidEventError("dead-letter payload must be a mapping")
        if not reason:
            raise InvalidEventError("dead-letter reason must not be empty")
        if len(self._entries) >= self._capacity:
            self._entries.popleft()
        self._entries.append((payload, reason))

    @property
    def size(self) -> int:
        return len(self._entries)

    def drain(self, handler: Callable[[Mapping[str, Any], str], None]) -> int:
        drained = 0
        while self._entries:
            payload, reason = self._entries.popleft()
            handler(payload, reason)
            drained += 1
        return drained
