import re
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.hwdata.pico import FIRMWARE_ROLES, PICO_PHYSICAL_PIN, load_firmware_gpio
from tools.diagrams import phase0_wiring as p0

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "schematics" / "phase0_wiring_schematic.svg"


def _svg_text():
    return p0.render()


def test_nets_pass_validator():
    assert validate_nets(p0.NETS, p0.RAILS) == []


def test_svg_valid_xml_with_viewbox():
    root = ET.fromstring(_svg_text())
    assert root.get("viewBox")


def test_no_text_below_9px():
    root = ET.fromstring(_svg_text())
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        assert float(el.get("font-size", "10")) >= 9


def test_every_gp_label_is_a_firmware_pin():
    roles = set()
    for v in FIRMWARE_ROLES.values():
        roles.update(v if isinstance(v, tuple) else (v,))
    roles.update((26, 27, 28))  # unassigned ADC pins the header glyph always prints
    for m in re.findall(r">GP(\d+)<", _svg_text()):
        assert int(m) in roles


def test_wired_gpios_match_config():
    cfg = load_firmware_gpio(ROOT / "firmware" / "pico" / "config.py")
    wired = {n: e[1] for n, ends in p0.NETS.items() for e in ends
             if e[0] == "PICO" and e[1].startswith("GP")}
    expect = {"OLED_SCK": cfg["OLED_SCK"], "OLED_MOSI": cfg["OLED_MOSI"],
              "OLED_DC": cfg["OLED_DC"], "OLED_RES": cfg["OLED_RES"],
              "LED_R": cfg["LED_CLOCK"], "LED_G": cfg["LED_GATE"], "LED_B": cfg["LED_MODE"],
              "BTN_TAP": cfg["BTN_TAP"], "ENC_SW": cfg["ENC_SW"], "ENC_CLK": cfg["ENC_CLK"],
              "ENC_DT": cfg["ENC_DT"], "CLOCK_IN": cfg["CLOCK_IN"], "CLOCK_OUT": cfg["CLOCK_OUT"]}
    assert wired == {k: f"GP{v}" for k, v in expect.items()}
    assert all(int(g[2:]) in PICO_PHYSICAL_PIN for g in wired.values())


def test_forbidden_text_absent():
    s = _svg_text().lower()
    for bad in ("strip oled", "0x3d", "0x3c", "effigy", "i2c", "sda", "scl"):
        assert bad not in s
    assert "spi" in s


def test_oled_owner_stated_items_tagged():
    s = _svg_text()
    assert "Pin order: owner-stated" in s
    assert "Chip SH1106: owner-stated" in s
    assert "UNVERIFIED: OLED" not in s
    assert "IIC/SPI pads" not in s
    assert "SPI-only 7-pin header (owner confirmed)" in s
    assert "V2.0, SH1106 (owner)" in s


def test_committed_svg_matches_generator():
    assert SVG.read_text() == p0.render()


def test_clock_in_is_loop_back_only_and_unowned_parts_are_flagged():
    s = _svg_text()
    assert "loop-back only, no external signals" in s
    assert "no CD4049UB on the bench" in s
    for tag in ("MISSING: RGB LED", "MISSING: tactile button", "MISSING: half-size breadboard",
                "UNVERIFIED: RGB lead order R-K-G-B"):
        assert tag in s, tag
    assert "not valid until the SPI driver" not in s
    assert "OLED_SPI" in s


def test_oled_cs_strapped_to_gnd_and_gp11_unused_in_phase0():
    # ruling 2026-10-17: CS tied to GND (BT-14); GP11 is the gate input, not drawn in Phase 0
    assert ("OLED", "CS") in p0.NETS["GND"]
    assert "OLED_CS" not in p0.NETS
    gps = {e[1] for ends in p0.NETS.values() for e in ends if e[0] == "PICO"}
    assert "GP11" not in gps
    s = _svg_text()
    assert "CS to GND: PROVISIONAL (BT-14)" in s
    assert "to GP11" not in s and "OLED CS" not in s
