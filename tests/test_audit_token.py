from event_normalizer.audit_token import event_audit_token


def test_token_is_stable_across_normalized_spelling():
    left = event_audit_token(
        {"id": " evt-42 ", "type": "Order.Created", "source": "Checkout"}
    )
    right = event_audit_token(
        {"id": "evt-42", "type": "order.created", "source": "checkout"}
    )

    assert left == right
    assert len(left) == 24


def test_token_does_not_contain_raw_event_identity():
    token = event_audit_token(
        {"id": "customer-7", "type": "user.updated", "source": "identity"}
    )

    assert "customer" not in token
    assert "identity" not in token
