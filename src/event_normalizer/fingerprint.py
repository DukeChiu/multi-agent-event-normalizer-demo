import hashlib
import json
from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def event_fingerprint(payload: Mapping[str, Any]) -> str:
    """Build a stable SHA-256 fingerprint from normalized event fields."""
    event = normalize_event(payload)
    canonical = json.dumps(
        event,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
