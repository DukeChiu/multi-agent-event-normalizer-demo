from event_normalizer.schema_fallback import resolve_schema_version


BASE_EVENT = {"id": "evt-1", "type": "order.created", "source": "checkout"}


def test_uses_explicit_supported_version():
    payload = {**BASE_EVENT, "schema_version": 2}

    assert resolve_schema_version(payload, {1, 2}) == 2


def test_falls_back_from_newer_unknown_version():
    payload = {**BASE_EVENT, "schema_version": 99}

    assert resolve_schema_version(payload, {1, 2}) == 2


def test_falls_back_when_version_is_not_numeric():
    payload = {**BASE_EVENT, "schema_version": "preview"}

    assert resolve_schema_version(payload, {1, 2}) == 2
