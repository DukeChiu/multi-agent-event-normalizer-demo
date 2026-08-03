import json
from collections.abc import Callable, Mapping
from typing import Any
from urllib.request import Request, urlopen

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def deliver_event(
    payload: Mapping[str, Any],
    destination: str,
    *,
    opener: Callable[..., Any] = urlopen,
) -> int:
    """Normalize and deliver an event to an HTTP destination."""
    if not destination.startswith(("http://", "https://")):
        raise InvalidEventError("event destination must be HTTP")
    body = json.dumps(normalize_event(payload), sort_keys=True).encode("utf-8")
    request = Request(
        destination,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response = opener(request, timeout=10)
    return int(response.status)
