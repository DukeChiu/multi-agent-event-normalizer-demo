import pytest

from event_normalizer.automatic_retry import retry_until_success


def test_returns_result_after_transient_failures():
    state = {"calls": 0}

    def flaky() -> str:
        state["calls"] += 1
        if state["calls"] < 3:
            raise ValueError("transient")
        return "ok"

    assert retry_until_success(flaky, delay_seconds=0, max_attempts=5) == "ok"
    assert state["calls"] == 3


def test_stops_after_max_attempts():
    def always_fails() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        retry_until_success(always_fails, delay_seconds=0, max_attempts=2)
