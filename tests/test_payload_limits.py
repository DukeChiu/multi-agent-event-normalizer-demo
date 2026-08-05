import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.payload_limits import validate_payload_bytes


def test_accepts_payload_within_budget():
    body = b'{"id": "evt-1"}'
    assert validate_payload_bytes(body, max_bytes=1024) == body


def test_rejects_oversized_payload():
    with pytest.raises(InvalidEventError, match="exceeds maximum size"):
        validate_payload_bytes(b"x" * 2048, max_bytes=1024)


def test_accepts_text_body_by_encoding():
    assert (
        validate_payload_bytes('{"id": "evt-1"}', max_bytes=1024)
        == b'{"id": "evt-1"}'
    )


@pytest.mark.parametrize("max_bytes", [0, -1, True])
def test_rejects_invalid_max_bytes(max_bytes):
    with pytest.raises(InvalidEventError, match="positive integer"):
        validate_payload_bytes(b"{}", max_bytes=max_bytes)
