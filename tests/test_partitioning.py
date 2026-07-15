import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.partitioning import event_partition


def test_assigns_same_event_to_same_partition():
    payload = {"id": "evt-42", "type": "user.created"}
    assert event_partition(payload, 16) == event_partition(payload, 16)
    assert 0 <= event_partition(payload, 16) < 16


@pytest.mark.parametrize("partition_count", [0, -1, True])
def test_rejects_invalid_partition_count(partition_count):
    with pytest.raises(InvalidEventError, match="positive integer"):
        event_partition({"id": "evt-1", "type": "user.created"}, partition_count)
