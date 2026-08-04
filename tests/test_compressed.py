import gzip
import json

import pytest

from event_normalizer.compressed import normalize_gzip_event
from event_normalizer.errors import InvalidEventError


def test_normalizes_gzip_encoded_json_event():
    body = gzip.compress(
        json.dumps({"id": "evt-1", "type": "Order.Created"}).encode("utf-8")
    )

    assert normalize_gzip_event(body)["type"] == "order.created"


def test_rejects_invalid_gzip_body():
    with pytest.raises(InvalidEventError, match="compressed"):
        normalize_gzip_event(b"not-gzip")
