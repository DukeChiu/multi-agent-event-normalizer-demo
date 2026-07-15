from collections import OrderedDict
from collections.abc import Callable, Mapping
from threading import Lock
from time import monotonic
from typing import Any

from event_normalizer.normalizer import normalize_event


class EventClaimStore:
    """Atomically claim event identities for a bounded process-local TTL window."""

    def __init__(
        self,
        *,
        ttl_seconds: float = 300.0,
        max_entries: int = 10_000,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if isinstance(max_entries, bool) or max_entries < 1:
            raise ValueError("max_entries must be a positive integer")
        self._ttl_seconds = float(ttl_seconds)
        self._max_entries = int(max_entries)
        self._clock = clock
        self._claims: OrderedDict[str, float] = OrderedDict()
        self._lock = Lock()

    @staticmethod
    def _key(payload: Mapping[str, Any]) -> str:
        event = normalize_event(payload)
        return "\x00".join((event["source"], event["type"], event["id"]))

    def claim(self, payload: Mapping[str, Any]) -> bool:
        key = self._key(payload)
        now = self._clock()
        with self._lock:
            self._discard_expired(now)
            existing_expiry = self._claims.get(key)
            if existing_expiry is not None and existing_expiry > now:
                return False
            self._claims[key] = now + self._ttl_seconds
            self._claims.move_to_end(key)
            while len(self._claims) > self._max_entries:
                self._claims.popitem(last=False)
            return True

    def _discard_expired(self, now: float) -> None:
        expired = [key for key, expiry in self._claims.items() if expiry <= now]
        for key in expired:
            self._claims.pop(key, None)

    def __len__(self) -> int:
        with self._lock:
            self._discard_expired(self._clock())
            return len(self._claims)
