import re

from event_normalizer.errors import InvalidEventError


def to_snake_case(value: str) -> str:
    """Convert an event type to snake_case for display."""
    normalized = str(value).strip().lower()
    if not normalized:
        raise InvalidEventError("event type must not be empty")
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def to_camel_case(value: str) -> str:
    """Convert an event type to camelCase for display."""
    snake = to_snake_case(value)
    head, *tail = snake.split("_")
    return head + "".join(part.capitalize() for part in tail)
