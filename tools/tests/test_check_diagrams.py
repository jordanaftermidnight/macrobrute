import pytest

from tools.check_diagrams import validate_nets


@pytest.mark.parametrize("gp", ["GP23", "GP24", "GP25", "GP29"])
def test_unexposed_gpio_rejected(gp):
    nets = {"n": [("PICO", gp), ("LED", "A")]}
    assert any(gp in p for p in validate_nets(nets, {}))


def test_five_volt_to_gpio_rejected():
    nets = {"gate": [("PICO", "GP12"), ("U3", "out")]}
    assert any("5" in p for p in validate_nets(nets, {"gate": 5.0}))


def test_five_volt_with_shifter_ok():
    nets = {"gate": [("PICO", "GP12"), ("U3", "out"), ("SHIFT", "U4")]}
    assert validate_nets(nets, {"gate": 5.0}) == []


def test_five_volt_with_divider_ok():
    nets = {"gate": [("PICO", "GP12"), ("U3", "out"), ("DIV", "22k/33k")]}
    assert validate_nets(nets, {"gate": 5.0}) == []


def test_gpio_on_two_nets_rejected():
    nets = {"a": [("PICO", "GP4"), ("X", "1")], "b": [("PICO", "GP4"), ("Y", "1")]}
    assert any("GP4" in p for p in validate_nets(nets, {}))


@pytest.mark.parametrize("gp", ["GP2", "GP3", "GP11", "GP26", "GP27", "GP28"])
def test_free_gpio_valid_but_not_shareable(gp):
    one = {"a": [("PICO", gp), ("X", "1")]}
    assert validate_nets(one, {}) == []
    two = {"a": [("PICO", gp), ("X", "1")], "b": [("PICO", gp), ("Y", "1")]}
    assert any(gp in p for p in validate_nets(two, {}))


def test_cable_digital_line_needs_series_resistor():
    bad = {"CABLE_UART_TX": [("PICO", "GP0"), ("DB9B", "1")]}
    assert any("series" in p for p in validate_nets(bad, {}))
    good = {"CABLE_UART_TX": [("PICO", "GP0"), ("R", "R1"), ("DB9B", "1")]}
    assert validate_nets(good, {}) == []


@pytest.mark.parametrize("name", ["CABLE_UART_RX", "CABLE_I2C_SDA", "CABLE_CLK_OUT"])
def test_cable_rule_applies_to_named_prefixes(name):
    bad = {name: [("X", "1"), ("DB9B", "1")]}
    assert any("series" in p for p in validate_nets(bad, {}))


@pytest.mark.parametrize("name", ["CABLE_GND", "CABLE_5V", "GATE", "UART_TX", "MY_CABLE_UART"])
def test_cable_rule_ignores_other_nets(name):
    nets = {name: [("X", "1"), ("DB9B", "1")]}
    assert validate_nets(nets, {}) == []


def test_floating_net_rejected():
    assert validate_nets({"a": [("X", "1")]}, {})
