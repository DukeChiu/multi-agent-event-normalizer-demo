from event_normalizer.event_icons import event_icon


def test_returns_icon_for_known_event_type():
    assert event_icon({"id": "evt-1", "type": "User.Created"}) == "👤"


def test_returns_default_icon_for_unknown_type():
    assert event_icon({"id": "evt-1", "type": "order.cancelled"}) == "⚙️"
