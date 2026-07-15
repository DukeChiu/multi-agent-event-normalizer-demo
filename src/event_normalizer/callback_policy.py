from ipaddress import ip_address
from urllib.parse import urlsplit, urlunsplit

from event_normalizer.errors import InvalidEventError


def validate_callback_url(value: str) -> str:
    """Validate and canonicalize a callback URL before delivery."""
    parsed = urlsplit(str(value).strip())
    if parsed.scheme.lower() != "https":
        raise InvalidEventError("callback URL must use HTTPS")
    if not parsed.hostname:
        raise InvalidEventError("callback URL must include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise InvalidEventError("callback URL must not include credentials")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise InvalidEventError("callback URL must not use localhost")
    try:
        literal_address = ip_address(hostname)
    except ValueError:
        literal_address = None
    if literal_address is not None and not literal_address.is_global:
        raise InvalidEventError("callback URL must use a public address")

    port = parsed.port
    netloc = hostname if port in (None, 443) else f"{hostname}:{port}"
    path = parsed.path or "/"
    return urlunsplit(("https", netloc, path, parsed.query, ""))
