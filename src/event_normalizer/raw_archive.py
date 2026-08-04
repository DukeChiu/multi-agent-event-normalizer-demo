import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from event_normalizer.normalizer import normalize_event


def archive_raw_payload(payload: Mapping[str, Any], directory: Path) -> Path:
    """Persist the complete incoming payload for later diagnostic replay."""
    event_id = normalize_event(payload)["id"]
    safe_event_id = re.sub(r"[^A-Za-z0-9._-]", "_", event_id).strip("._") or "event"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{safe_event_id}.json"
    destination.write_text(
        json.dumps(dict(payload), ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return destination
