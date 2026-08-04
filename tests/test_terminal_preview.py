from event_normalizer.terminal_preview import format_terminal_preview


def test_formats_plain_terminal_preview():
    assert format_terminal_preview(
        {"id": "evt-1", "type": "Order.Created", "source": "Billing"},
        color=False,
    ) == "[billing] order.created (evt-1)"


def test_colors_known_source():
    result = format_terminal_preview(
        {"id": "evt-1", "type": "Order.Created", "source": "Billing"}
    )

    assert result.startswith("\033[33m")
    assert result.endswith("\033[0m")
