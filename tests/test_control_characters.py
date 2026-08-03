import pytest

from event_normalizer import InvalidEventError, normalize_event


@pytest.mark.parametrize("field", ["id", "type", "source"])
def test_rejects_control_characters_in_normalized_fields(field):
    payload = {"id": "evt-1", "type": "order.created", "source": "billing"}
    payload[field] += "\nforged"

    with pytest.raises(InvalidEventError, match="control characters"):
        normalize_event(payload)
