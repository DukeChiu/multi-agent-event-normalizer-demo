import hashlib
import hmac

from event_normalizer.errors import InvalidEventError


def verify_sha256_signature(body: bytes, signature: str, secret: bytes) -> None:
    """Verify a sha256=<hex> webhook signature using constant-time comparison."""
    if not isinstance(body, bytes):
        raise InvalidEventError("webhook body must be bytes")
    if not isinstance(secret, bytes) or not secret:
        raise InvalidEventError("webhook signing secret must be non-empty bytes")

    scheme, separator, supplied_digest = str(signature).partition("=")
    if separator != "=" or scheme.lower() != "sha256":
        raise InvalidEventError("webhook signature must use sha256")
    if len(supplied_digest) != 64:
        raise InvalidEventError("webhook signature has an invalid digest length")
    try:
        int(supplied_digest, 16)
    except ValueError as exc:
        raise InvalidEventError("webhook signature must be hexadecimal") from exc

    expected_digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_digest, supplied_digest.lower()):
        raise InvalidEventError("webhook signature does not match")
