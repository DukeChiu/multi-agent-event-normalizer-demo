import json
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

from event_normalizer.normalizer import normalize_event


@lru_cache(maxsize=2048)
def _normalize_serialized(serialized: str) -> dict[str, str]:
    payload = json.loads(serialized)
    return normalize_event(payload)


def normalize_event_cached(payload: Mapping[str, Any]) -> dict[str, str]:
    """Normalize repeated payloads through a bounded process-local cache."""
    serialized = json.dumps(
        dict(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return _normalize_serialized(serialized)


def cache_stats() -> dict[str, int]:
    info = _normalize_serialized.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "size": info.currsize,
        "capacity": info.maxsize,
    }
