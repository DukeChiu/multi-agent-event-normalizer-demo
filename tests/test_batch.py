import pytest

from event_normalizer.batch import normalize_events
from event_normalizer.errors import InvalidEventError


def test_normalizes_multiple_events_in_input_order():
    result = normalize_events(
        [
            {"id": "evt-1", "type": "user.created"},
            {"id": "evt-2", "type": "payment.succeeded"},
        ]
    )
    assert [event["id"] for event in result] == ["evt-1", "evt-2"]


def test_rejects_duplicate_event_identifiers():
    with pytest.raises(InvalidEventError, match="duplicate event identifier: evt-1"):
        normalize_events(
            [
                {"id": "evt-1", "type": "user.created"},
                {"id": "evt-1", "type": "user.updated"},
            ]
        )
