import pytest

from event_normalizer import InvalidEventError, normalize_event


def test_normalizes_valid_event():
    result = normalize_event(
        {
            "id": 42,
            "type": "  User.Created ",
            "source": " Billing ",
        }
    )

    assert result == {
        "id": "42",
        "type": "user.created",
        "source": "billing",
    }


def test_rejects_non_mapping_payload():
    with pytest.raises(InvalidEventError, match="payload must be a mapping"):
        normalize_event(None)  # type: ignore[arg-type]
