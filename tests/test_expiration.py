from datetime import datetime, timezone

import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.expiration import is_event_expired


NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def test_detects_expired_and_active_events():
    assert is_event_expired("2026-07-14T11:00:00Z", 1800, now=NOW) is True
    assert is_event_expired("2026-07-14T11:45:00Z", 1800, now=NOW) is False


def test_rejects_timestamp_without_timezone():
    with pytest.raises(InvalidEventError, match="include a timezone"):
        is_event_expired("2026-07-14T11:00:00", 1800, now=NOW)
