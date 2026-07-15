from event_normalizer.display import event_display_label


def test_builds_human_readable_event_label():
    assert event_display_label(
        {"id": "evt-7", "type": "invoice.payment_failed", "source": "Billing"}
    ) == "Invoice / Payment Failed [billing] #evt-7"
