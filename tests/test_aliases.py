import pytest

from event_normalizer.aliases import normalize_event_type
from event_normalizer.errors import InvalidEventError


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        (" User-Created ", "user.created"),
        ("USER.CREATED.V1", "user.created"),
        ("order.cancelled", "order.cancelled"),
    ],
)
def test_normalizes_known_aliases_and_preserves_unknown_values(raw_value, expected):
    assert normalize_event_type(raw_value) == expected


def test_rejects_empty_event_type():
    with pytest.raises(InvalidEventError, match="event type must not be empty"):
        normalize_event_type("   ")
