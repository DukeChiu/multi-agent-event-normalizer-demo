import json

from event_normalizer.raw_archive import archive_raw_payload


def test_archives_complete_payload_for_replay(tmp_path):
    payload = {
        "id": "evt/42",
        "type": "account.updated",
        "source": "identity",
        "access_token": "diagnostic-secret",
    }

    archived = archive_raw_payload(payload, tmp_path)

    assert archived.name == "evt_42.json"
    assert json.loads(archived.read_text(encoding="utf-8")) == payload
