from event_normalizer.random_ids import assign_random_id


def test_assigns_new_random_identifier():
    first = assign_random_id({"id": "evt-1", "type": "user.created"})
    second = assign_random_id({"id": "evt-1", "type": "user.created"})
    assert first["id"] != "evt-1"
    assert len(first["id"]) == 32
    assert first["id"] != second["id"]
