import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.routing import select_event_route


def test_selects_route_using_normalized_event_type():
    route = select_event_route(
        {"id": "evt-1", "type": " User.Created "},
        {"user.created": "identity-events"},
    )
    assert route == "identity-events"


def test_uses_default_route_for_unknown_event_type():
    route = select_event_route(
        {"id": "evt-1", "type": "order.cancelled"},
        {},
        default_route="audit-events",
    )
    assert route == "audit-events"


def test_rejects_empty_route():
    with pytest.raises(InvalidEventError, match="event route must not be empty"):
        select_event_route(
            {"id": "evt-1", "type": "user.created"},
            {"user.created": "   "},
        )
