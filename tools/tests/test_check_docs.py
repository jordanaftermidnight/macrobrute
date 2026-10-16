from tools.check_docs import check_connection_map, check_lpc_uart_claims


def test_flags_unexposed_gpio_listed_as_spare():
    text = "With 8 spare GPIOs (GP2,3,6,7,11,23,24,25) + 3 ADC"
    problems = check_connection_map(text)
    assert any("GP23" in p for p in problems)


def test_flags_gpio_row_disagreeing_with_firmware():
    text = "| GP9 | 12 | Encoder switch | IN | x |"
    problems = check_connection_map(text)
    assert any("GP9" in p for p in problems)


def test_clean_row_passes():
    text = "| GP13 | 17 | Encoder switch | IN | Pull-up |"
    assert check_connection_map(text) == []


def test_lpc_uart_conflict_detected():
    docs = {"a.md": "bridge uses P0.16 (RXD1)", "b.md": "bridge uses P0.2/P0.3 (TXD0/RXD0)"}
    assert check_lpc_uart_claims(docs)


def test_internal_not_exposed_wording_is_not_flagged():
    text = "GP23/24/25 are RP2040-internal and not exposed."
    assert check_connection_map(text) == []
