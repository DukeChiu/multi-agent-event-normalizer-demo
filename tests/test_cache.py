from event_normalizer.cache import cache_stats, normalize_event_cached


def test_reuses_normalization_for_equivalent_payloads():
    payload = {"id": "evt-1", "type": "Order.Created", "source": "Checkout"}

    first = normalize_event_cached(payload)
    second = normalize_event_cached(dict(reversed(list(payload.items()))))

    assert first == second
    assert cache_stats()["hits"] >= 1


def test_cache_is_bounded():
    stats = cache_stats()

    assert stats["capacity"] == 2048
    assert stats["size"] <= stats["capacity"]
