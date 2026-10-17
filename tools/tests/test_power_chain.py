import re
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagrams import power_chain as pc

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "schematics" / "power_regulation_diagram.svg"
CM = (ROOT / "docs" / "MACROBRUTE_CONNECTION_MAP.md").read_text()
SUPPLY_NETS = {"P12_RACK", "P12", "N12_RACK", "N12", "P5_RACK", "VSYS", "3V3",
               "P12_BRK", "N12_BRK", "P5_LOCAL", "TP70", "TP71"}


def _svg():
    return pc.render()


def _texts(svg):
    root = ET.fromstring(svg)
    return [(el.text or "") for el in root.iter("{http://www.w3.org/2000/svg}text")]


def test_nets_pass_validator():
    assert validate_nets(pc.NETS, pc.RAILS) == []


def test_svg_valid_xml_with_viewbox():
    assert ET.fromstring(_svg()).get("viewBox")


def test_no_text_below_9px():
    root = ET.fromstring(_svg())
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        assert float(el.get("font-size", "10")) >= 9


def test_forbidden_text_absent():
    s = _svg().lower()
    for bad in ("strip oled", "effigy", "+12v on db-9", "+12 v on db-9"):
        assert bad not in s


def test_rack_header_pins_match_datasheet_f():
    pins = {"N12_RACK": {"1", "2"}, "P12_RACK": {"9", "10"}, "P5_RACK": {"11", "12"},
            "GND": {"3", "4", "5", "6", "7", "8"}}
    for net, want in pins.items():
        got = {p for part, p in pc.NETS[net] if part == "HDR"}
        assert got == want, net
    used = set().union(*pins.values())
    assert not used & {"13", "14", "15", "16"}      # pins 13-16 unused


def test_n12_diode_orientation_matches_connection_map():
    # the connection map states: cathode to the TP71 / -12 V side, anode to the breakout rail
    assert re.search(r"cathode goes to the TP71 / -12 V side and its anode to\s+the breakout rail", CM)
    tp71 = pc.NETS["TP71"]
    brk = pc.NETS["N12_BRK"]
    assert ("D_BRK_N12", "K") in tp71 and ("TP71", "-12V") in tp71
    assert ("D_BRK_N12", "A") in brk
    # and the same rule on the rack side: cathode toward the header
    assert ("D_RACK_N12", "K") in pc.NETS["N12_RACK"]
    assert ("D_RACK_N12", "A") in pc.NETS["N12"]


def test_no_supply_rail_on_the_cable():
    for name, ends in pc.NETS.items():
        parts = {p for p, _ in ends}
        if any(p.startswith("DB9") for p in parts):
            assert name not in SUPPLY_NETS
            assert name.startswith("CABLE_") or name == "GND_TIE"
    for name in pc.NETS:
        if name.startswith("CABLE_"):
            assert not any(s in name for s in ("12V", "P12", "N12", "5V", "3V3", "VSYS"))
    assert any("NO SUPPLY ON THE CABLE" in t for t in _texts(_svg()))


def test_ground_tie_includes_db9_pin_9_and_b_grounds():
    tie = set(pc.NETS["GND_TIE"])
    assert ("DB9_A", "9") in tie
    for pin in ("2", "4", "7", "8", "9"):
        assert ("DB9_B", pin) in tie


def test_provisional_and_unverified_tags_present():
    s = _svg()
    assert s.count(">PROVISIONAL<") >= 3
    assert s.count(">UNVERIFIED<") >= 3
    assert s.count(">OPEN<") >= 1


def test_review_fixes_pinned():
    t = " ".join(_texts(_svg()))
    assert "(LF398 not owned, Q1;" in t and "CD4051 alternative)" in t
    assert "VSYS diode is the only +5 V diode" in t and "OWNER-CONFIRM" in t
    # the main OLED is SPI (owner ruling 2026-10-17): no I2C0 pull-up row any more
    assert "SPI: no pull-ups" in t and "4.7k" not in t and "I2C" not in t
    assert "each cable's braid" in t
    assert "200 mA continuous" in t
    # electrolytic polarity: + to GND on -12V_BRK, + to the rail on +12V_BRK
    assert ("C_N12", "+") in pc.NETS["GND_BRK"] and ("C_P12", "+") in pc.NETS["P12_BRK"]
    assert _svg().count(">+<") >= 2


def test_committed_svg_matches_generator():
    assert SVG.read_text() == pc.render()


def test_vsys_filter_has_a_ground_return_and_u2_note_is_neutral():
    gnd = [n for n, ends in pc.NETS.items() if ("VSYS_FILTER", "GND") in ends]
    assert gnd and ("PICO", "GND") in pc.NETS[gnd[0]]
    t = " ".join(_texts(_svg()))
    # owner has both op-amps in stock: U2 is a layout choice, not an open question
    assert "OPEN U2" not in t
    assert ("U1/U2: TL074C or TL072IP, both owned (×4 / ×6); final op-amp count and "
            "split chosen at breakout layout") in t


def test_cable_labels_follow_the_nets():
    t = " ".join(_texts(_svg()))
    tx = [q for p, q in pc.NETS["CABLE_UART_TX"] if p == "DB9_B"][0]
    rx = [q for p, q in pc.NETS["CABLE_UART_RX"] if p == "DB9_B"][0]
    assert f"B:{tx} UART TX" in t and f"B:{rx} UART RX" in t
    gnds = [q for p, q in pc.NETS["GND_TIE"] if p == "DB9_B"]
    assert "  ".join(f"B:{g}" for g in gnds) + " GND" in t
