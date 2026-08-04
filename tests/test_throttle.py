import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.throttle import SourceThrottle


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_events_within_limit_and_blocks_after():
    clock = _FakeClock()
    throttle = SourceThrottle(limit=2, window_seconds=60, clock=clock)
    assert throttle.allow("billing") is True
    assert throttle.allow("billing") is True
    assert throttle.allow("billing") is False
    assert throttle.allow("identity") is True


def test_check_raises_when_throttled():
    throttle = SourceThrottle(limit=1, window_seconds=60)
    throttle.check("billing")
    with pytest.raises(InvalidEventError, match="throttled"):
        throttle.check("billing")


def test_window_rolls_over():
    clock = _FakeClock()
    throttle = SourceThrottle(limit=1, window_seconds=60, clock=clock)
    assert throttle.allow("billing") is True
    assert throttle.allow("billing") is False
    clock.now = 61.0
    assert throttle.allow("billing") is True
