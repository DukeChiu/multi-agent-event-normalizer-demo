import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.source_policy import normalize_event_from_sources


def test_accepts_source_case_insensitively():
    result = normalize_event_from_sources(
        {"id": "evt-1", "type": "user.created", "source": " Billing "},
        {"billing", "identity"},
    )
    assert result["source"] == "billing"


def test_rejects_source_outside_allowlist():
    with pytest.raises(InvalidEventError, match="source is not allowed: unknown"):
        normalize_event_from_sources(
            {"id": "evt-1", "type": "user.created"},
            {"billing"},
        )
