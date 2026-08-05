import pytest

from event_normalizer.attributes import normalize_event_with_attributes
from event_normalizer.errors import InvalidEventError


def test_preserves_only_explicit_bounded_attributes():
    result = normalize_event_with_attributes(
        {
            "id": "evt-1",
            "type": "order.created",
            "secret": "do-not-copy",
            "attr_tenant": " acme ",
        }
    )

    assert result["attributes"] == {"tenant": "acme"}
    assert "secret" not in result


def test_rejects_oversized_attribute_value():
    with pytest.raises(InvalidEventError, match="attribute"):
        normalize_event_with_attributes(
            {"id": "evt-1", "type": "order.created", "attr_note": "x" * 257}
        )
