from collections.abc import Collection, Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def resolve_schema_version(
    payload: Mapping[str, Any],
    supported_versions: Collection[int],
) -> int:
    """Select a supported schema version, falling back for unknown senders."""
    normalize_event(payload)
    supported = sorted(
        version
        for version in supported_versions
        if isinstance(version, int) and not isinstance(version, bool) and version > 0
    )
    if not supported:
        raise ValueError("at least one positive schema version is required")

    try:
        requested = int(payload.get("schema_version", supported[-1]))
    except (TypeError, ValueError):
        return supported[-1]
    if requested in supported:
        return requested

    older_versions = [version for version in supported if version < requested]
    return older_versions[-1] if older_versions else supported[0]
