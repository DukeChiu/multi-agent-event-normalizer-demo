import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.warehouse import warehouse_object_key


def test_builds_date_partitioned_warehouse_key():
    key = warehouse_object_key(
        {"id": "evt-1", "type": "Order.Paid", "source": "Billing"},
        "2026-08-03T10:15:00Z",
    )

    assert key == (
        "events/source=billing/type=order.paid/day=2026-08-03/evt-1.json"
    )


def test_rejects_invalid_warehouse_timestamp():
    with pytest.raises(InvalidEventError, match="warehouse timestamp"):
        warehouse_object_key({"id": "evt-1", "type": "order.paid"}, "today")
