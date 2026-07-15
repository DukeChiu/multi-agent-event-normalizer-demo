import pytest

from event_normalizer.complexity import validate_payload_complexity
from event_normalizer.errors import InvalidEventError


def test_accepts_payload_within_limits():
    validate_payload_complexity(
        {"id": "evt-1", "items": [{"sku": "A"}, {"sku": "B"}]},
        max_depth=4,
        max_nodes=10,
    )


def test_rejects_excessive_depth():
    with pytest.raises(InvalidEventError, match="nested too deeply"):
        validate_payload_complexity({"a": {"b": {"c": 1}}}, max_depth=2)


def test_rejects_cycles():
    payload = {}
    payload["self"] = payload

    with pytest.raises(InvalidEventError, match="contains a cycle"):
        validate_payload_complexity(payload)
