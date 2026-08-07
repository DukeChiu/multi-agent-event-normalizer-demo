import json
import subprocess
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def enrich_event(payload: Mapping[str, Any], command: str) -> dict[str, Any]:
    """Enrich a normalized event with JSON returned by an external command."""
    event: dict[str, Any] = normalize_event(payload)
    try:
        output = subprocess.check_output(command, shell=True, text=True, timeout=5)
    except subprocess.SubprocessError as exc:
        raise InvalidEventError(f"enrichment command failed: {exc}") from exc
    try:
        extra = json.loads(output)
    except ValueError as exc:
        raise InvalidEventError("enrichment output must be JSON") from exc
    if not isinstance(extra, Mapping):
        raise InvalidEventError("enrichment output must be a JSON object")
    event.update(extra)
    return event
