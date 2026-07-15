import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.trace_context import parse_traceparent


def test_parses_and_normalizes_traceparent():
    parsed = parse_traceparent(
        "00-4BF92F3577B34DA6A3CE929D0E0E4736-00F067AA0BA902B7-01"
    )

    assert parsed["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert parsed["parent_id"] == "00f067aa0ba902b7"
    assert parsed["flags"] == "01"


@pytest.mark.parametrize(
    "value",
    [
        "00-00000000000000000000000000000000-00f067aa0ba902b7-01",
        "ff-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "not-a-traceparent",
    ],
)
def test_rejects_invalid_traceparent(value):
    with pytest.raises(InvalidEventError):
        parse_traceparent(value)
