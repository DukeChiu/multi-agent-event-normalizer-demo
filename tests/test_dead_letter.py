import pytest

from event_normalizer.dead_letter import DeadLetterQueue
from event_normalizer.errors import InvalidEventError


def test_quarantines_and_drains_events():
    queue = DeadLetterQueue(capacity=10)
    queue.quarantine({"id": "evt-1"}, "invalid payload")
    queue.quarantine({"id": "evt-2"}, "invalid payload")
    assert queue.size == 2

    seen = []
    assert queue.drain(lambda payload, reason: seen.append(payload["id"])) == 2
    assert seen == ["evt-1", "evt-2"]
    assert queue.size == 0


def test_drops_oldest_when_capacity_exceeded():
    queue = DeadLetterQueue(capacity=2)
    queue.quarantine({"id": "evt-1"}, "a")
    queue.quarantine({"id": "evt-2"}, "a")
    queue.quarantine({"id": "evt-3"}, "a")
    assert queue.size == 2

    seen = []
    queue.drain(lambda payload, reason: seen.append(payload["id"]))
    assert seen == ["evt-2", "evt-3"]


def test_rejects_empty_reason():
    with pytest.raises(InvalidEventError, match="reason must not be empty"):
        DeadLetterQueue().quarantine({"id": "evt-1"}, "")
