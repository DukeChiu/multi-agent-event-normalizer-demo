from datetime import datetime, timezone

import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.event_time import event_ordering_key, parse_event_time


def test_parses_equivalent_iso_seconds_and_milliseconds():
    expected = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)

    assert parse_event_time("2023-11-14T22:13:20Z") == expected
    assert parse_event_time(1_700_000_000) == expected
    assert parse_event_time(1_700_000_000_000) == expected


def test_orders_equal_timestamps_by_normalized_event_id():
    first = {"id": "a", "type": "x", "created_at": "2024-01-01T00:00:00Z"}
    second = {"id": "b", "type": "x", "created_at": "2024-01-01T00:00:00Z"}

    assert event_ordering_key(first) < event_ordering_key(second)


def test_rejects_malformed_timestamp():
    with pytest.raises(InvalidEventError, match="malformed"):
        parse_event_time("yesterday")
