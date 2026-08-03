import hashlib
from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def event_audit_token(payload: Mapping[str, Any], *, length: int = 24) -> str:
    """Return a compact deterministic token for cross-service audit correlation."""
    if isinstance(length, bool) or not 16 <= length <= 64:
        raise ValueError("audit token length must be between 16 and 64")
    event = normalize_event(payload)
    canonical_identity = "\x00".join(
        (event["source"], event["type"], event["id"])
    ).encode("utf-8")
    return hashlib.sha256(canonical_identity).hexdigest()[:length]
