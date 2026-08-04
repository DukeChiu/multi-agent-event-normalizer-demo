from event_normalizer.claim_store import EventClaimStore


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


EVENT = {"id": "evt-1", "type": "order.created", "source": "checkout"}


def test_claim_is_atomic_for_duplicate_identity():
    store = EventClaimStore()

    assert store.claim(EVENT) is True
    assert store.claim(dict(EVENT)) is False
    assert len(store) == 1


def test_claim_can_be_reacquired_after_ttl():
    clock = Clock()
    store = EventClaimStore(ttl_seconds=10, clock=clock)

    assert store.claim(EVENT) is True
    clock.now += 10
    assert store.claim(EVENT) is True


def test_oldest_claim_is_evicted_at_capacity():
    store = EventClaimStore(max_entries=2)

    assert store.claim({**EVENT, "id": "1"}) is True
    assert store.claim({**EVENT, "id": "2"}) is True
    assert store.claim({**EVENT, "id": "3"}) is True
    assert len(store) == 2
    assert store.claim({**EVENT, "id": "1"}) is True
