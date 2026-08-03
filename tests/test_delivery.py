from event_normalizer.delivery import deliver_event


class Response:
    status = 202


def test_delivers_normalized_event_as_json():
    captured = {}

    def open_request(request, timeout):
        captured["body"] = request.data
        captured["timeout"] = timeout
        return Response()

    status = deliver_event(
        {"id": "evt-1", "type": "Order.Created"},
        "https://receiver.example/events",
        opener=open_request,
    )

    assert status == 202
    assert b'"type": "order.created"' in captured["body"]
    assert captured["timeout"] == 10
