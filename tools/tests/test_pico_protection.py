import xml.etree.ElementTree as ET
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import PICO_NAMES
from tools.diagrams import pico_protection as pp

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "schematics" / "pico_power_protection.svg"


def _svg():
    return pp.render()


def _texts():
    root = ET.fromstring(_svg())
    return [(el.text or "") for el in root.iter("{http://www.w3.org/2000/svg}text")]


def test_nets_pass_validator():
    assert validate_nets(pp.NETS, pp.RAILS) == []


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


def test_vsys_is_physical_pin_39():
    assert PICO_NAMES[38] == "VSYS"
    assert PICO_NAMES[35] == "3V3"
    assert ("PICO", "VSYS") in pp.NETS["VSYS"]
    assert any("39" in t for t in _texts())


def test_chain_order_diode_then_bulk_and_100nf_then_vsys():
    n = pp.NETS
    assert ("D1", "A") in n["RACK_5V"]
    assert ("D1", "K") in n["VSYS"]
    assert ("C_BULK", "+") in n["VSYS"] and ("C_100N", "1") in n["VSYS"]


def test_1n5817_is_20v_and_standin_is_tagged():
    texts = " ".join(_texts())
    assert "20 V" in texts and "40 V" in texts          # 1N5817 is 20 V; 1N5819 is 40 V
    s = _svg()
    assert ">OWNER-CONFIRM<" in s or "OWNER-CONFIRM" in texts
    assert "UNVERIFIED" in texts and "PROVISIONAL" in texts


def test_d1_is_the_owned_1n5819_not_1n5817():
    t = _texts()
    assert "D1 1N5819" in t and "D1 1N5817" not in t
    assert any("OWNER-CONFIRM" in x and "1N5819" in x for x in t)


def test_committed_svg_matches_generator():
    assert SVG.read_text() == pp.render()
