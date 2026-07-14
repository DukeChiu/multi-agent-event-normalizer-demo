from event_normalizer.fingerprint import event_fingerprint


def test_fingerprint_is_stable_after_normalization():
    left = event_fingerprint(
        {"id": "evt-1", "type": " User.Created ", "source": " Billing "}
    )
    right = event_fingerprint(
        {"source": "billing", "type": "user.created", "id": "evt-1"}
    )
    assert left == right
    assert len(left) == 64


def test_fingerprint_changes_with_event_identity():
    left = event_fingerprint({"id": "evt-1", "type": "user.created"})
    right = event_fingerprint({"id": "evt-2", "type": "user.created"})
    assert left != right
