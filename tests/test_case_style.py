import pytest

from event_normalizer.case_style import to_camel_case, to_snake_case
from event_normalizer.errors import InvalidEventError


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("User.Created", "user_created"),
        ("Payment Succeeded", "payment_succeeded"),
        ("order.placed.v1", "order_placed_v1"),
    ],
)
def test_converts_to_snake_case(raw, expected):
    assert to_snake_case(raw) == expected


def test_converts_to_camel_case():
    assert to_camel_case("User.Created") == "userCreated"


def test_rejects_empty_value():
    with pytest.raises(InvalidEventError, match="must not be empty"):
        to_snake_case("   ")
