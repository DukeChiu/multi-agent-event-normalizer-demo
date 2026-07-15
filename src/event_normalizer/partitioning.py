import hashlib
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def event_partition(payload: Mapping[str, Any], partition_count: int) -> int:
    """Map an event identifier to a stable zero-based partition."""
    if isinstance(partition_count, bool) or partition_count <= 0:
        raise InvalidEventError("partition count must be a positive integer")
    event = normalize_event(payload)
    digest = hashlib.blake2b(event["id"].encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big") % partition_count
