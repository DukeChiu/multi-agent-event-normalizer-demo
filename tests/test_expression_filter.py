from event_normalizer.expression_filter import event_matches


def test_matches_event_type_expression():
    payload = {"id": "evt-1", "type": "Order.Paid", "source": "billing"}

    assert event_matches(payload, "event['type'] == 'order.paid'")


def test_rejects_nonmatching_source_expression():
    payload = {"id": "evt-1", "type": "Order.Paid", "source": "billing"}

    assert not event_matches(payload, "event['source'] == 'identity'")
