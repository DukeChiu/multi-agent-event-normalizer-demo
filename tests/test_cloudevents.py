import pytest

from event_normalizer.cloudevents import normalize_cloudevent
from event_normalizer.errors import InvalidEventError


def test_maps_cloudevent_attributes_to_normalized_event():
    assert normalize_cloudevent(
        {
            "specversion": "1.0",
            "id": " evt-7 ",
            "type": "Order.Paid",
            "source": "HTTPS://Billing.Example/",
            "data": {"amount": 42},
        }
    ) == {
        "id": "evt-7",
        "type": "order.paid",
        "source": "https://billing.example/",
    }


def test_rejects_unsupported_cloudevent_version():
    with pytest.raises(InvalidEventError, match="specversion"):
        normalize_cloudevent({"specversion": "0.3"})
