import re
from pathlib import Path
import xml.etree.ElementTree as ET

from tools.hwdata.pico import PICO_PHYSICAL_PIN
from tools.diagram_kit import (
    PICO_NAMES,
    Card, PALETTE, resistor, led, diode, capacitor, jack, dip, db9,
    pico_header, header_block, wire, label_box,
    resistor_pins, led_pins, diode_pins, capacitor_pins, jack_pins,
    dip_pins, db9_pins, pico_header_pins, header_block_pins,
)


def test_card_is_valid_xml_and_fits_viewbox():
    c = Card(400, 200, "T", "sub")
    c.add(resistor(50, 50, "1kΩ"))
    c.add(wire([(10, 10), (100, 10)], PALETTE["audio"]))
    root = ET.fromstring(c.render())
    assert root.get("viewBox") == "0 0 400 200"


def test_text_never_below_9px():
    c = Card(300, 100, "T", "s")
    c.add(label_box(20, 20, "hello"))
    for el in ET.fromstring(c.render()).iter():
        fs = el.get("font-size")
        if fs:
            assert float(fs.replace("px", "")) >= 9


def test_card_uses_light_self_contained_background():
    svg = Card(100, 100, "T", "s").render()
    assert PALETTE["card"] in svg


def _demo():
    c = Card(900, 700, "Demo", "every glyph")
    for s in (
        resistor(40, 100, "1k"), resistor(40, 140, "2k", horizontal=False),
        led(120, 100, "D1", "#ff0000"), diode(120, 140, "D2"),
        capacitor(200, 100, "100n"), jack(240, 100, "IN"),
        dip(300, 100, "U1", ["1", "2", "3", "4", "5", "6", "7", "8"]),
        db9(450, 100, "DB-9 A"), db9(450, 220, "DB-9 B"),
        pico_header(600, 80, "Pico"), header_block(780, 100, "J1", ["A", "B", "C"]),
    ):
        c.add(s)
    c.legend([(PALETTE["audio"], "Audio"), (PALETTE["gnd"], "GND")])
    return c.render()


def test_every_glyph_is_valid_xml_and_deterministic():
    assert ET.fromstring(_demo()) is not None
    assert _demo() == _demo()


def test_glyphs_return_strings():
    for s in (resistor(0, 0, "a"), led(0, 0, "a", "#f00"), diode(0, 0, "a"),
              capacitor(0, 0, "a"), jack(0, 0, "a"), dip(0, 0, "U", ["1", "2"]),
              db9(0, 0, "DB-9 A"), pico_header(0, 0, "P"),
              header_block(0, 0, "J", ["x"]), wire([(0, 0), (1, 1)], "#000"),
              label_box(0, 0, "t")):
        assert isinstance(s, str)


def test_anchor_places_named_pin_at_xy():
    p = resistor_pins(100, 50)
    assert p.xy("a") == (100, 50)
    q = resistor_pins(100, 50, anchor="b")
    assert q.xy("b") == (100, 50)
    assert q.xy("a") == (100 - 40, 50)
    assert (q.xy("b")[0] - q.xy("a")[0], q.xy("b")[1] - q.xy("a")[1]) == \
        (p.xy("b")[0] - p.xy("a")[0], p.xy("b")[1] - p.xy("a")[1])
    # drawing with the same anchor puts a pin dot on the anchor point
    assert 'cx="100" cy="50"' in resistor(100, 50, "r", anchor="b")


def test_every_part_has_pin_helpers_and_anchor():
    assert diode_pins(10, 10, anchor="k").xy("k") == (10, 10)
    assert led_pins(10, 10, anchor="k").xy("k") == (10, 10)
    assert capacitor_pins(10, 10, anchor="b").xy("b") == (10, 10)
    assert jack_pins(10, 10, anchor="sleeve").xy("sleeve") == (10, 10)
    assert resistor_pins(10, 10, horizontal=False).xy("b")[0] == 10
    d = dip_pins(10, 10, ["1", "2", "3", "4"], anchor="3")
    assert d.xy("3") == (10, 10)
    assert db9_pins(10, 10, anchor="9").xy("9") == (10, 10)
    assert pico_header_pins(10, 10, anchor="40").xy("40") == (10, 10)
    assert header_block_pins(10, 10, ["a", "b"], anchor="2").xy("2") == (10, 10)


def test_dip_pin_numbering():
    d = dip_pins(0, 0, [str(i) for i in range(1, 9)])
    # pins 1-4 down the left, 5-8 up the right
    assert d.xy("1")[0] == d.xy("4")[0] < d.xy("5")[0] == d.xy("8")[0]
    assert d.xy("1")[1] < d.xy("4")[1]
    assert d.xy("5")[1] == d.xy("4")[1] and d.xy("8")[1] == d.xy("1")[1]


def test_db9_two_rows_numbered_with_title():
    p = db9_pins(0, 0)
    assert len(p.names) == 9
    top = {p.xy(str(i))[1] for i in range(1, 6)}
    bot = {p.xy(str(i))[1] for i in range(6, 10)}
    assert len(top) == 1 and len(bot) == 1 and max(top) < min(bot)
    svg = db9(0, 0, "DB-9 B")
    assert "DB-9 B" in svg
    for n in "123456789":
        assert f">{n}</text>" in svg


def test_pico_header_has_40_pins_and_gp_labels():
    p = pico_header_pins(0, 0)
    assert len(p.names) == 40
    svg = pico_header(0, 0, "Pico")
    for lab in ("GP0", "GP15", "GP28", "VBUS", "VSYS", "3V3"):
        assert f">{lab}</text>" in svg
    assert p.xy("1")[0] < p.xy("40")[0] and p.xy("1")[1] == p.xy("40")[1]


def test_wire_draws_junction_dots():
    svg = wire([(0, 0), (10, 0), (10, 10)], "#123456", junctions=[(10, 0)])
    assert "<circle" in svg and "#123456" in svg


def _texts_boxes(svg_fragment):
    root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{svg_fragment}</svg>')
    return root


def test_label_box_rect_precedes_and_covers_text():
    root = _texts_boxes(label_box(20, 20, "hello"))
    kids = [k.tag.split("}")[1] for k in root]
    assert kids.index("rect") < kids.index("text")
    rect = root.find("{http://www.w3.org/2000/svg}rect")
    assert float(rect.get("width")) >= len("hello") * 6.2


def test_no_style_font_size_below_9_and_no_genre_words():
    svg = _demo()
    for m in re.finditer(r"font-size:\s*([\d.]+)px", svg):
        assert float(m.group(1)) >= 9
    for el in ET.fromstring(svg).iter():
        fs = el.get("font-size")
        if fs:
            assert float(fs) >= 9
    assert not re.search(r"synth|music|techno|rave", (Path(__file__).resolve().parents[1] / "diagram_kit.py").read_text(), re.I)


def test_pico_gp_labels_match_canonical_pin_map():
    for gp, phys in PICO_PHYSICAL_PIN.items():
        assert PICO_NAMES[phys - 1] == f"GP{gp}"
    mapped = set(PICO_PHYSICAL_PIN.values())
    for phys in range(1, 41):
        if phys not in mapped:
            assert not re.fullmatch(r"GP\d+", PICO_NAMES[phys - 1])
    svg = pico_header(0, 0, "Pico")
    assert f">GP{max(PICO_PHYSICAL_PIN)}</text>" in svg


def test_db9_faces_mirror_pin_positions_and_caption():
    m = db9_pins(0, 0, face="male-front")
    f = db9_pins(0, 0, face="female-front")
    assert m.xy("1")[0] < m.xy("5")[0]
    assert f.xy("1")[0] > f.xy("5")[0]
    for n in "123456789":
        assert m.xy(n)[1] == f.xy(n)[1]
        assert m.xy(n)[0] + f.xy(n)[0] == 4 * 22
    assert db9_pins(0, 0, face="male-solder").as_dict() == f.as_dict()
    assert db9_pins(0, 0, face="female-solder").as_dict() == m.as_dict()
    assert "female" in db9(0, 0, "DB-9 A", face="female-front")
    assert "solder" in db9(0, 0, "DB-9 A", face="male-solder")
    assert db9_pins(10, 10, anchor="1", face="female-front").xy("1") == (10, 10)
