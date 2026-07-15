from collections.abc import Mapping, Sequence
from typing import Any

from event_normalizer.errors import InvalidEventError


def validate_payload_complexity(
    payload: Any,
    *,
    max_depth: int = 12,
    max_nodes: int = 10_000,
) -> None:
    """Reject cyclic or excessively deep webhook payload structures."""
    if isinstance(max_depth, bool) or max_depth < 0:
        raise ValueError("max_depth must be a non-negative integer")
    if isinstance(max_nodes, bool) or max_nodes < 1:
        raise ValueError("max_nodes must be a positive integer")

    active_containers: set[int] = set()
    visited_nodes = 0

    def visit(value: Any, depth: int) -> None:
        nonlocal visited_nodes
        visited_nodes += 1
        if visited_nodes > max_nodes:
            raise InvalidEventError("webhook payload contains too many values")
        if depth > max_depth:
            raise InvalidEventError("webhook payload is nested too deeply")

        is_mapping = isinstance(value, Mapping)
        is_sequence = isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        )
        if not is_mapping and not is_sequence:
            return

        container_id = id(value)
        if container_id in active_containers:
            raise InvalidEventError("webhook payload contains a cycle")
        active_containers.add(container_id)
        try:
            children = value.values() if is_mapping else value
            for child in children:
                visit(child, depth + 1)
        finally:
            active_containers.remove(container_id)

    visit(payload, 0)
