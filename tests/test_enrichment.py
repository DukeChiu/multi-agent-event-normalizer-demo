import pytest

from event_normalizer.enrichment import enrich_event
from event_normalizer.errors import InvalidEventError


def test_merges_enrichment_json():
    result = enrich_event(
        {"id": "evt-1", "type": "user.created"},
        "echo '{\"region\": \"cn-east\"}'",
    )
    assert result["region"] == "cn-east"


def test_rejects_non_json_output():
    with pytest.raises(InvalidEventError, match="must be JSON"):
        enrich_event({"id": "evt-1", "type": "user.created"}, "echo 'nope'")


def test_rejects_failing_command():
    with pytest.raises(InvalidEventError, match="failed"):
        enrich_event({"id": "evt-1", "type": "user.created"}, "exit 3")
