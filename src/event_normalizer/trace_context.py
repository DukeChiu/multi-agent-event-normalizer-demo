import re

from event_normalizer.errors import InvalidEventError


TRACEPARENT_PATTERN = re.compile(
    r"^(?P<version>[0-9a-fA-F]{2})-"
    r"(?P<trace_id>[0-9a-fA-F]{32})-"
    r"(?P<parent_id>[0-9a-fA-F]{16})-"
    r"(?P<flags>[0-9a-fA-F]{2})$"
)


def parse_traceparent(value: str) -> dict[str, str]:
    """Parse the fixed-length W3C traceparent header representation."""
    match = TRACEPARENT_PATTERN.fullmatch(str(value).strip())
    if match is None:
        raise InvalidEventError("traceparent header is malformed")

    result = {name: part.lower() for name, part in match.groupdict().items()}
    if result["version"] == "ff":
        raise InvalidEventError("traceparent version ff is forbidden")
    if result["trace_id"] == "0" * 32:
        raise InvalidEventError("traceparent trace id must not be zero")
    if result["parent_id"] == "0" * 16:
        raise InvalidEventError("traceparent parent id must not be zero")
    return result
