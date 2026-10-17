import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from tools.diagram_kit import bb_strip
from tools.diagrams import phase0_breadboard as bb
from tools.diagrams.phase0_nets import NETS, RAILS
from tools.check_diagrams import validate_nets
from tools.hwdata.pico import PICO_PHYSICAL_PIN

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "schematics" / "phase0_breadboard.svg"

RAIL_NET = {"+T": "3V3", "+B": "3V3", "-T": "GND", "-B": "GND"}


def _net_of(part, pin):
    p, q = part.upper(), pin.upper().replace(" ", "")
    for name, ends in NETS.items():
        for ep, eq in ends:
            if (ep.upper(), eq.upper().replace(" ", "")) == (p, q):
                return name
    return None


def _all_endpoints():
    return {(p, q): n for n, ends in NETS.items() for p, q in ends}


def test_nets_still_pass_validator():
    assert validate_nets(NETS, RAILS) == []


def test_every_net_endpoint_is_placed():
    placed = {(p, q) for p, q, _ in bb.LEADS}
    for j in bb.JUMPERS:
        placed.update(e for e in (j["a_end"], j["b_end"]) if e[0] != "RAIL")
    missing = [e for e in _all_endpoints() if e not in placed]
    assert missing == []


def test_every_hole_name_exists():
    from tools.diagram_kit import breadboard_pins
    names = set(breadboard_pins(0, 0).names)
    for _, _, h in bb.LEADS:
        assert h in names
    for j in bb.JUMPERS:
        for h in (j["a_hole"], j["b_hole"]):
            assert h is None or h in names


def test_no_two_leads_share_a_hole_unless_same_net():
    users = defaultdict(set)
    for part, pin, hole in bb.LEADS:
        users[hole].add(_net_of(part, pin) or f"unused:{part}.{pin}")
    for j in bb.JUMPERS:
        for h, e in ((j["a_hole"], j["a_end"]), (j["b_hole"], j["b_end"])):
            if h:
                users[h].add(j["net"] or f"test:{h}")
    lead_count = defaultdict(int)
    for _, _, hole in bb.LEADS:
        lead_count[hole] += 1
    for hole, nets in users.items():
        assert len(nets) == 1, (hole, nets)
    # a hole holds at most one part lead
    assert all(c == 1 for c in lead_count.values())


def test_unused_pico_pins_share_strips_with_nothing():
    strip_users = defaultdict(list)
    for part, pin, hole in bb.LEADS:
        strip_users[bb_strip(hole)].append((part, pin))
    for j in bb.JUMPERS:
        for h in (j["a_hole"], j["b_hole"]):
            if h:
                strip_users[bb_strip(h)].append(("JUMPER", j["net"]))
    for strip, users in strip_users.items():
        pico = [u for u in users if u[0] == "PICO" and _net_of(*u) is None]
        assert not pico or len(users) == 1, (strip, users)


def _components(include_test):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for part, pin, hole in bb.LEADS:
        union(("end", part, pin), ("strip", bb_strip(hole)))
    for part, pin, _ in bb.LEADS:
        if part == "PICO" and pin == "GND":
            union(("end", "PICO", "GND"), ("pico", "gnd"))
    for j in bb.JUMPERS:
        if j["kind"] == "test" and not include_test:
            continue
        nodes = []
        for end, hole in ((j["a_end"], j["a_hole"]), (j["b_end"], j["b_hole"])):
            if hole:
                nodes.append(("strip", bb_strip(hole)))
            else:
                nodes.append(("end",) + end)
        union(*nodes)
    return find


def test_breadboard_connectivity_realises_every_net():
    find = _components(include_test=False)
    comp_nets = defaultdict(set)
    for (part, pin), net in _all_endpoints().items():
        if part == "JUMPER":
            continue
        comp_nets[find(("end", part, pin))].add(net)
    assert all(len(v) == 1 for v in comp_nets.values()), dict(comp_nets)
    per_net = defaultdict(set)
    for (part, pin), net in _all_endpoints().items():
        if part != "JUMPER":
            per_net[net].add(find(("end", part, pin)))
    assert {n: len(c) for n, c in per_net.items() if len(c) != 1} == {}


def test_rails_carry_the_right_nets():
    find = _components(include_test=False)
    for j in bb.JUMPERS:
        for end, hole in ((j["a_end"], j["a_hole"]), (j["b_end"], j["b_hole"])):
            if hole and hole[0] in "+-":
                assert RAIL_NET[hole[:2]] == j["net"]
    assert find(("strip", "+T")) == find(("strip", "+B"))
    assert find(("strip", "-T")) == find(("strip", "-B"))
    assert find(("strip", "+T")) != find(("strip", "-T"))


def test_test_jumper_joins_exactly_the_two_clock_nets():
    base = _components(include_test=False)
    withj = _components(include_test=True)
    a = base(("end", "R", "1K_OUT.b"))
    b = base(("end", "R", "1K_IN.a"))
    assert a != b
    assert withj(("end", "R", "1K_OUT.b")) == withj(("end", "R", "1K_IN.a"))
    other = base(("end", "PICO", "GP4"))
    assert withj(("end", "PICO", "GP4")) == other != withj(("end", "R", "1K_IN.a"))
    tests = [j for j in bb.JUMPERS if j["kind"] == "test"]
    assert len(tests) == 1 and tests[0]["dashed"]


def test_jumper_table_rows_are_net_endpoint_pairs():
    rows = bb.jumper_rows()
    assert len(rows) == len(bb.JUMPERS) >= 20
    for r in rows:
        assert set(r) >= {"from", "to", "colour", "length"}
        assert r["length"] in ("S", "M", "L")
    for j in bb.JUMPERS:
        if j["kind"] == "bridge":
            assert j["a_end"] == j["b_end"] == ("RAIL", "3V3")
            continue
        if j["kind"] == "test":
            assert _net_of(*j["a_end"]) == "CLOCK_OUT_JACK"
            assert _net_of(*j["b_end"]) == "CLOCK_IN"
            continue
        net = j["net"]
        members = set(NETS[net])
        for end in (j["a_end"], j["b_end"]):
            assert end in members or end == ("RAIL", net), (net, end)
        assert j["a_end"] != j["b_end"]


def test_every_net_is_wired_by_some_jumper_or_shared_strip():
    wired = {j["net"] for j in bb.JUMPERS}
    for net, ends in NETS.items():
        if len(ends) < 2:
            continue
        # either a jumper carries the net, or all its endpoints share one strip
        strips = {bb_strip(h) for p, q, h in bb.LEADS if (p, q) in set(ends)}
        assert net in wired or len(strips) == 1, net


def test_pico_pins_match_physical_map():
    pico = {pin: hole for part, pin, hole in bb.LEADS if part == "PICO"}
    for gp, phys in PICO_PHYSICAL_PIN.items():
        hole = pico[f"GP{gp}"]
        assert hole[0] == ("c" if phys <= 20 else "h")
        col = 31 - phys if phys <= 20 else phys - 10
        assert hole[1:] == str(col)
    assert len([1 for p, _, _ in bb.LEADS if p == "PICO"]) == 40


def _svg():
    return bb.render()


def test_svg_valid_and_text_sizes():
    root = ET.fromstring(_svg())
    assert root.get("viewBox")
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        assert float(el.get("font-size", "10")) >= 9


def test_card_content_and_exclusions():
    s = _svg()
    low = s.lower()
    for bad in ("strip oled", "0x3d", "0x3c", "effigy", "i2c", "sda", "scl"):
        assert bad not in low
    assert "spi" in low
    assert "UNVERIFIED: OLED pin order" in s and "UNVERIFIED: OLED chip" in s
    assert "UNVERIFIED: SPI mode set on board" in s
    for lab in ("USB", "pin 1", "UNVERIFIED", "test jumper", "Legend"):
        assert lab in s
    for n in range(1, 41):
        assert f">{n}</text>" in s
    for gp in PICO_PHYSICAL_PIN:
        assert f">GP{gp}</text>" in s
    assert not re.search(r"synth|" + "tech" + "no" + r"|rave", low)


def test_jack_captions_are_far_apart():
    assert abs(bb.JACK_IN_X - bb.JACK_OUT_X) >= 160


def test_committed_svg_matches_generator():
    assert SVG.read_text() == bb.render()


def _drawn():
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(bb.render())
    dots = {(float(c.get("cx")), float(c.get("cy"))) for c in root.iter(ns + "circle")}
    lines = {frozenset([(float(l.get("x1")), float(l.get("y1"))),
                        (float(l.get("x2")), float(l.get("y2")))])
             for l in root.iter(ns + "line")}
    return dots, lines


def test_every_lead_is_drawn_at_its_hole():
    dots, _ = _drawn()
    for part, pin, hole in bb.LEADS:
        assert bb.hxy(hole) in dots, (part, pin, hole)


def test_each_resistor_is_drawn_between_its_own_two_leads():
    _, lines = _drawn()
    holes = {(p, q): h for p, q, h in bb.LEADS}
    names = {q.split(".")[0] for p, q, _ in bb.LEADS if p == "R"}
    assert len(names) == 5
    for n in names:
        ends = frozenset([bb.hxy(holes[("R", n + ".a")]), bb.hxy(holes[("R", n + ".b")])])
        assert ends in lines, n


def test_oled_module_has_seven_leads_in_one_order():
    names = list(bb.OLED_X)
    assert len(names) == 7 and set(names) == {"GND", "VCC", "D0", "D1", "RES", "DC", "CS"}
    xs = [bb.OLED_X[n] for n in names]
    assert xs == sorted(xs)
    # module drawn header-toward-the-board: the assumed order GND VCC D0 D1 RES DC CS
    # (UNVERIFIED) reads right to left
    assert names == ["CS", "DC", "RES", "D1", "D0", "VCC", "GND"]


def test_clock_in_is_loop_back_only_and_unowned_parts_are_flagged():
    s = _svg()
    assert "loop-back only, no external signals" in s
    assert "no CD4049UB on the bench" in s
    for tag in ("MISSING: RGB LED", "MISSING: tactile button", "MISSING: half-size breadboard",
                "UNVERIFIED: RGB lead order R-K-G-B"):
        assert tag in s, tag


def test_oled_cs_lead_goes_to_the_gnd_rail():
    cs = [j for j in bb.JUMPERS if ("OLED", "CS") in (j["a_end"], j["b_end"])]
    assert len(cs) == 1
    j = cs[0]
    assert j["net"] == "GND" and j["color"] == bb.C_GND
    assert j["b_end"] == ("RAIL", "GND") and j["b_hole"].startswith("-T")
    # GP11 (gate input) is not used in Phase 0: nothing sits on its strip
    gp11_col = bb.pico_hole(PICO_PHYSICAL_PIN[11])[1:]
    holes = {h for jj in bb.JUMPERS for h in (jj["a_hole"], jj["b_hole"]) if h}
    assert not any(h[0] in "abcde" and h[1:] == gp11_col for h in holes)
    assert "CS to GND: PROVISIONAL (BT-14)" in _svg()
