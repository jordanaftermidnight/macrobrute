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


def test_flags_aux_outputs_swapped_within_family():
    text = "| GP19 | 25 | Aux output 2 | OUT | x |\n| GP20 | 26 | Aux output 1 | OUT | x |"
    problems = check_connection_map(text)
    assert any("GP19" in p for p in problems)
    assert any("GP20" in p for p in problems)


def test_flags_clock_divider_outputs_swapped_within_family():
    text = "| GP16 | 21 | Clock divider out 3 | OUT | x |\n| GP18 | 24 | Clock divider out 1 | OUT | x |"
    problems = check_connection_map(text)
    assert any("GP16" in p for p in problems)
    assert any("GP18" in p for p in problems)


def test_correct_aux_and_divider_rows_pass():
    text = "\n".join([
        "| GP19 | 25 | Aux output 1 | OUT | x |",
        "| GP20 | 26 | Aux output 2 | OUT | x |",
        "| GP6 | 9 | Aux output 3 | OUT | x |",
        "| GP7 | 10 | Aux output 4 | OUT | x |",
        "| GP16 | 21 | Clock divider out 1 | OUT | x |",
        "| GP17 | 22 | Clock divider out 2 | OUT | x |",
        "| GP18 | 24 | Clock divider out 3 | OUT | x |",
    ])
    assert check_connection_map(text) == []


def test_numbered_hint_does_not_match_longer_number():
    assert check_connection_map("| GP19 | 25 | Aux output 12 | OUT | x |")


def test_flags_unexposed_gpio_range_listed_as_free():
    problems = check_connection_map("Free pins: GP2, GP23-25")
    for gp in ("GP23", "GP24", "GP25"):
        assert any(gp in p for p in problems), gp


def test_flags_unexposed_gpio_with_space_listed_as_spare():
    problems = check_connection_map("Spare: GP 24 and GP 29")
    assert any("GP24" in p for p in problems)
    assert any("GP29" in p for p in problems)


def test_flags_unexposed_gpio_en_dash_range():
    problems = check_connection_map("available: GP22–GP25")
    assert any("GP24" in p for p in problems)


def test_exposed_range_listed_as_free_passes():
    assert check_connection_map("Free pins: GP2, GP3, GP11 and GP26-28") == []
