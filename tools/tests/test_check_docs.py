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


def test_flags_p0_0_p0_1_claimed_as_uart0():
    docs = {"a.md": "| TX | P0.1 (RXD0) - Pin 47 |", "b.md": "#define PIN_UART0_TX 0  // P0.0"}
    problems = check_lpc_uart_claims(docs)
    assert any("a.md:1" in p for p in problems)
    assert any("b.md:1" in p for p in problems)


def test_correct_uart0_pins_not_flagged():
    docs = {"a.md": "ISP UART0 is P0.2 (TXD0) and P0.3 (RXD0), pins 98 and 99"}
    assert check_lpc_uart_claims(docs) == []


def test_spi_oled_rows_pass_and_old_i2c_row_is_flagged():
    ok = "\n".join([
        "| GP2 | 4 | OLED SCK (SPI0 SCK) | OUT | x |",
        "| GP3 | 5 | OLED MOSI (SPI0 TX) | OUT | x |",
        "| GP4 | 6 | OLED DC | OUT | x |",
        "| GP5 | 7 | OLED RES | OUT | x |",
        "| GP11 | 15 | Gate input (Pico mirror of DB-9 A:1) | IN | x |",
    ])
    assert check_connection_map(ok) == []
    # ruling 2026-10-17: OLED CS is strapped to GND, GP11 is the gate input
    assert any("GP11" in p for p in check_connection_map("| GP11 | 15 | OLED CS | OUT | x |"))
    assert any("GP4" in p for p in check_connection_map("| GP4 | 6 | I²C0 SDA | I/O | x |"))


def test_flags_allocated_gpio_called_free_in_prose():
    from tools.check_docs import check_spare_claims
    problems = check_spare_claims({"a.md": "Free pins: GP2, GP3 and GP26-28 for expansion."})
    assert any("a.md:1: GP2 is" in p for p in problems)
    assert any(": GP3 is" in p for p in problems)
    assert not any(": GP26 is" in p for p in problems)


def test_spare_claim_allows_tables_history_and_negation():
    from tools.check_docs import check_spare_claims
    docs = {"a.md": "\n".join([
        "| GP2 | 4 | Free, reserved | x |",
        "SUPERSEDED: GP2, GP3 and GP11 were free before the SPI ruling.",
        "GP2, GP3 and GP11 went to the SPI OLED; free pins are GP26-28 only.",
        "GP6 and GP7 are NOT free: they are aux outputs.",
        "STALE drawing: MPR121 on GP2/GP3 (spare).",
    ])}
    assert check_spare_claims(docs) == []


def test_main_scans_schematics_and_readme(tmp_path, monkeypatch):
    import tools.check_docs as cd
    files = cd.doc_files(cd.Path(__file__).resolve().parents[2])
    names = {str(f) for f in files}
    assert any(n.endswith("README.md") and "/docs/" not in n for n in names)
    assert any("/schematics/" in n for n in names)
