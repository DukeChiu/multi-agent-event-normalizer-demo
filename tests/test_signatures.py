import hashlib
import hmac

import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.signatures import verify_sha256_signature


def test_accepts_matching_sha256_signature():
    body = b'{"id":"evt-1"}'
    secret = b"integration-secret"
    digest = hmac.new(secret, body, hashlib.sha256).hexdigest()

    verify_sha256_signature(body, f"sha256={digest}", secret)


def test_rejects_tampered_body():
    secret = b"integration-secret"
    digest = hmac.new(secret, b"original", hashlib.sha256).hexdigest()

    with pytest.raises(InvalidEventError, match="does not match"):
        verify_sha256_signature(b"tampered", f"sha256={digest}", secret)
