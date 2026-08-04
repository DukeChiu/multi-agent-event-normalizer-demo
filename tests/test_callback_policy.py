import pytest

from event_normalizer.callback_policy import validate_callback_url
from event_normalizer.errors import InvalidEventError


def test_accepts_and_canonicalizes_public_https_url():
    assert validate_callback_url(" HTTPS://Hooks.Example.COM:443/events?tenant=7#part ") == (
        "https://hooks.example.com/events?tenant=7"
    )


@pytest.mark.parametrize(
    "value",
    [
        "http://hooks.example.com/events",
        "https://127.0.0.1/events",
        "https://user:secret@hooks.example.com/events",
        "https://localhost/events",
    ],
)
def test_rejects_obviously_unsafe_callback_urls(value):
    with pytest.raises(InvalidEventError):
        validate_callback_url(value)
