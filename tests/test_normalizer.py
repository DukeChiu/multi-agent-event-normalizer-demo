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


def test_rejects_missing_id_with_domain_error():
    with pytest.raises(InvalidEventError, match="id is required"):
        normalize_event({"type": "user.created"})


def test_rejects_blank_event_type():
    with pytest.raises(InvalidEventError, match="type must not be blank"):
        normalize_event({"id": "evt-1", "type": "   "})


def test_uses_default_source_when_source_is_none():
    result = normalize_event(
        {
            "id": "evt-2",
            "type": "invoice.paid",
            "source": None,
        }
    )

    assert result == {
        "id": "evt-2",
        "type": "invoice.paid",
        "source": "unknown",
    }
