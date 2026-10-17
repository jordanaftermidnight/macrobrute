import re
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.hwdata.pico import FIRMWARE_ROLES, PICO_PHYSICAL_PIN
from tools.diagrams import pico_pinout as pp

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "schematics" / "pico_pinout_diagram.svg"
CMAP = (ROOT / "docs" / "MACROBRUTE_CONNECTION_MAP.md").read_text()
FULL_ROW = re.compile(r"^\|\s*GP(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|", re.M)

# keyword each card role must find in the connection map function text
KEYWORD = {
    "uart0": "UART0", "oled": "OLED", "led": "RGB LED", "button": "Tap button",
    "encoder": "Encoder", "clkdiv": "Clock divider", "aux": "Aux output",
    "clock_in": "Clock input", "clock_out": "Clock output", "free": "Free",
    "gate_in": "Gate input",
}


def _table():
    sec1 = CMAP.split("## 1. ", 1)[1].split("\n## 2.", 1)[0]   # not the 12G future-use table
    return {int(g): (int(p), f.strip(), d.strip()) for g, p, f, d in FULL_ROW.findall(sec1)}


def test_nets_pass_validator():
    assert validate_nets(pp.NETS, pp.RAILS) == []


def test_every_table_gp_has_a_card_role_that_matches():
    table = _table()
    assert set(table) == set(pp.ROLES)
    for gp, (pin, func, direction) in table.items():
        r = pp.ROLES[gp]
        assert r["pin"] == pin == PICO_PHYSICAL_PIN[gp]
        assert KEYWORD[r["cat"]].lower() in func.lower(), (gp, r["cat"], func)
        assert r["dir"].replace("-", "—") == direction, gp
        is_free = func.lower().startswith("free") or "(free)" in func.lower()
        assert (r["status"] == "Free") == is_free, gp


def test_roles_cover_firmware_roles():
    used = set()
    for v in FIRMWARE_ROLES.values():
        used.update(v if isinstance(v, tuple) else (v,))
    assert {g for g, r in pp.ROLES.items() if r["status"] == "Used"} == used
    assert {g for g, r in pp.ROLES.items() if r["status"] == "Free"} == {26, 27, 28}


def test_internal_gpios_never_usable():
    assert not set(pp.ROLES) & {23, 24, 25, 29}


def test_svg_valid_and_fonts_ok():
    root = ET.fromstring(pp.render())
    assert root.get("viewBox")
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        assert float(el.get("font-size", "10")) >= 9


def test_unverified_items_tagged_on_card():
    s = pp.render()
    assert s.count("UNVERIFIED") >= 3
    assert "pin order: UNVERIFIED" in s
    assert "I2C0" not in s
    assert "slice 5A" in s


def test_gate_input_on_gp11_and_cs_strapped():
    r = pp.ROLES[11]
    assert r["cat"] == "gate_in" and r["dir"] == "IN" and r["status"] == "Used"
    s = pp.render()
    assert "PROVISIONAL (BT-14)" in s
    assert "CS strapped to GND" in s
    assert all("CS" not in r["func"] for r in pp.ROLES.values())
    assert "OPEN" not in s
    assert pp.NETS["GATE_IN"] == [("PICO", "GP11"), ("DIV", "22K_33K"), ("DB9", "A:1")]


def test_committed_svg_matches_generator():
    assert SVG.read_text() == pp.render()
