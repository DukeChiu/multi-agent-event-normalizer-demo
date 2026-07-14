import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.redaction import redact_payload


def test_redacts_sensitive_fields_without_mutating_input():
    payload = {"id": "evt-1", "Authorization": "secret", "token": "abc"}
    result = redact_payload(payload)

    assert result == {
        "id": "evt-1",
        "Authorization": "[REDACTED]",
        "token": "[REDACTED]",
    }
    assert payload["token"] == "abc"


def test_supports_custom_sensitive_fields():
    result = redact_payload({"email": "user@example.com"}, {"email"})
    assert result["email"] == "[REDACTED]"


def test_rejects_empty_replacement():
    with pytest.raises(InvalidEventError, match="replacement must not be empty"):
        redact_payload({"token": "abc"}, replacement="")
