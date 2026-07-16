import pytest

from event_normalizer.contracts import EventContractRegistry
from event_normalizer.errors import InvalidEventError


REGISTRY = EventContractRegistry(
    {
        "billing": {"invoice.paid", "invoice.failed"},
        "identity": {"user.created"},
    }
)


def test_accepts_registered_source_and_event_type():
    event = REGISTRY.validate(
        {"id": "evt-1", "type": " Invoice.Paid ", "source": " Billing "}
    )

    assert event["type"] == "invoice.paid"
    assert REGISTRY.supported_types("BILLING") == ("invoice.failed", "invoice.paid")


def test_rejects_unregistered_event_type():
    with pytest.raises(InvalidEventError, match="event type"):
        REGISTRY.validate(
            {"id": "evt-2", "type": "invoice.refunded", "source": "billing"}
        )


def test_rejects_unregistered_source():
    with pytest.raises(InvalidEventError, match="source"):
        REGISTRY.validate(
            {"id": "evt-3", "type": "order.created", "source": "checkout"}
        )
