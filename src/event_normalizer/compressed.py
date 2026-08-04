import gzip
import json
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_gzip_event(body: bytes) -> dict[str, str]:
    """Decompress a gzip-encoded JSON webhook and normalize its event fields."""
    try:
        decoded: Any = json.loads(gzip.decompress(body).decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidEventError("compressed webhook body is invalid") from exc
    if not isinstance(decoded, Mapping):
        raise InvalidEventError("compressed webhook payload must be an object")
    return normalize_event(decoded)
