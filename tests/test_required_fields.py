import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.required_fields import require_text


def test_returns_trimmed_required_text():
    assert require_text({"id": " evt-1 "}, "id") == "evt-1"


@pytest.mark.parametrize("payload", [{}, {"id": ""}, {"id": "   "}])
def test_rejects_missing_or_empty_required_text(payload):
    with pytest.raises(InvalidEventError):
        require_text(payload, "id")
