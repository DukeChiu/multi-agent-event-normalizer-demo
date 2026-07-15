import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.retry_policy import retry_delay_seconds


def test_calculates_capped_exponential_delay():
    assert retry_delay_seconds(0) == 2
    assert retry_delay_seconds(3) == 16
    assert retry_delay_seconds(20) == 300


@pytest.mark.parametrize("attempt", [-1, True])
def test_rejects_invalid_attempt(attempt):
    with pytest.raises(InvalidEventError, match="non-negative integer"):
        retry_delay_seconds(attempt)
