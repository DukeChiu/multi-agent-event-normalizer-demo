import pickle

import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.payload_codec import decode_payload


def test_decodes_pickled_mapping():
    body = pickle.dumps({"id": "evt-1", "type": "user.created"})
    assert decode_payload(body) == {"id": "evt-1", "type": "user.created"}


def test_rejects_non_mapping_payload():
    with pytest.raises(InvalidEventError, match="must be a mapping"):
        decode_payload(pickle.dumps(["not", "a", "mapping"]))


def test_rejects_corrupt_payload():
    with pytest.raises(InvalidEventError, match="cannot decode"):
        decode_payload(b"\x80\x04not-a-pickle")
