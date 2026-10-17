"""Power chain card -> schematics/power_regulation_diagram.svg.

Run from the repo root:  python3 -m tools.diagrams.power_chain

SPLIT POWER (docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md and
docs/MACROBRUTE_CONNECTION_MAP.md sections 5.3, 10, 11): the expander runs only
from the Eurorack rack, the MicroBrute breakout only from the synth TP70 / TP71
/ TP72. DB-9 A and B carry signals and grounds only; no supply crosses them.
Current figures appear only where DATASHEETS or BF give them, and unmeasured
ones are tagged UNVERIFIED. Nothing here is built.
"""
import sys
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import (PALETTE, Card, _dot, _line, _t, capacitor, diode, label_box,
                               wire)
from tools.diagrams.power_common import (C_5V, C_SIG, bar_v, box, diode_left, notes, tag)
from tools.hwdata.pico import FIRMWARE_ROLES as R

OUT = Path(__file__).resolve().parents[2] / "schematics" / "power_regulation_diagram.svg"

C_P12, C_N12, C_GND = PALETTE["p12"], PALETTE["n12"], PALETTE["gnd"]
C_3V3 = PALETTE["p3v3"]
W, H = 1520, 1200

# --------------------------------------------------------------------- nets
# Parts: HDR (rack 16-pin header), D_RACK_* (rack rail diodes), ANALOG, VSYS_FILTER,
# PICO, V3V3_LOADS, STAR_EXP; TP70/71/72 (synth), D_BRK_* (breakout rail diodes), C_*,
# OPAMPS, REG78L05, CD40106, STAR_MB; DB9_A / DB9_B (cable ends), R (series resistors).
NETS = {
    "P12_RACK": [("HDR", "9"), ("HDR", "10"), ("D_RACK_P12", "A")],
    "P12": [("D_RACK_P12", "K"), ("ANALOG", "V+")],
    "N12_RACK": [("HDR", "1"), ("HDR", "2"), ("D_RACK_N12", "K")],
    "N12": [("D_RACK_N12", "A"), ("ANALOG", "V-")],
    "P5_RACK": [("HDR", "11"), ("HDR", "12"), ("VSYS_FILTER", "IN")],
    "VSYS": [("VSYS_FILTER", "OUT"), ("PICO", "VSYS")],
    "3V3": [("PICO", "3V3"), ("V3V3_LOADS", "3V3")],
    "GND": [("HDR", "3"), ("HDR", "4"), ("HDR", "5"), ("HDR", "6"), ("HDR", "7"),
            ("HDR", "8"), ("ANALOG", "GND"), ("PICO", "GND"), ("V3V3_LOADS", "GND"),
            ("STAR_EXP", "1")],
    # MicroBrute side: powered only from TP70 / TP71 / TP72
    "TP70": [("TP70", "+12V"), ("D_BRK_P12", "A")],
    "P12_BRK": [("D_BRK_P12", "K"), ("C_P12", "+"), ("OPAMPS", "V+"), ("REG78L05", "IN")],
    "TP71": [("TP71", "-12V"), ("D_BRK_N12", "K")],
    "N12_BRK": [("D_BRK_N12", "A"), ("C_N12", "-"), ("OPAMPS", "V-")],
    "TP72": [("TP72", "GND"), ("STAR_MB", "1")],
    "GND_BRK": [("STAR_MB", "1"), ("C_P12", "-"), ("C_N12", "+"), ("OPAMPS", "GND"),
                ("REG78L05", "GND"), ("CD40106", "VSS")],
    "P5_LOCAL": [("REG78L05", "OUT"), ("CD40106", "VDD")],
    # cable: grounds tie the two stars, signals carry a series resistor on each board
    "GND_TIE": [("STAR_EXP", "1"), ("STAR_MB", "1"), ("DB9_A", "9"), ("DB9_B", "2"),
                ("DB9_B", "4"), ("DB9_B", "7"), ("DB9_B", "8"), ("DB9_B", "9")],
    "CABLE_UART_TX": [("PICO", f"GP{R['LPC_TX']}"), ("R", "1K_EXP_TX"), ("DB9_B", "1"),
                      ("R", "1K_MB_TX")],
    "CABLE_UART_RX": [("PICO", f"GP{R['LPC_RX']}"), ("R", "1K_EXP_RX"), ("DB9_B", "6"),
                      ("R", "1K_MB_RX")],
}
RAILS = {"P12_RACK": 12.0, "N12_RACK": -12.0, "P5_RACK": 5.0, "3V3": 3.3,
         "TP70": 12.0, "TP71": -12.0, "P5_LOCAL": 5.0}

# ------------------------------------------------------------------ layout
XH = 150                     # rack header pin column
PIN_Y = lambda n: 120 + 20 * (n - 1)
XM = 180                     # merge column for same-rail pins
BUS_E = {"P5": 330, "P12": 370, "GND": 410, "N12": 450}
XCOL = 520                   # expander consumer boxes (left edge)
XW = 210
STAR_Y = 775

XT = 850                     # TP boxes
BUS_M = {"N12": 1060, "GND": 1120, "P12": 1180}
XMC = 1260                   # MB consumer boxes (left edge)


def _frame(x, y, w, h, title, sub):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" '
            f'stroke="{PALETTE["stroke"]}" stroke-width="1.2" stroke-dasharray="7 5"/>'
            + _t(x + 14, y + 20, title, 12, "start", PALETTE["title"], True)
            + _t(x + 14, y + 34, sub, 10, "start", PALETTE["muted"]))


def _expander(card):
    card.add(_frame(20, 56, 780, 744, "EXPANDER (rack domain)",
                    "Powered only from the Eurorack rack. No synth supply here."))
    # header glyph
    card.add(f'<rect x="{XH - 8}" y="{PIN_Y(1) - 10}" width="16" height="{PIN_Y(16) - PIN_Y(1) + 20}" '
             f'rx="3" fill="#2d2d2d" stroke="#111" stroke-width="1"/>')
    card.add(label_box(34, 94, "Rack 16-pin header (CP1A)"))
    names = {1: "-12V (red stripe)", 2: "-12V", 9: "+12V", 10: "+12V", 11: "+5V", 12: "+5V"}
    for n in range(1, 17):
        nm = names.get(n, "GND" if 3 <= n <= 8 else "unused")
        card.add(_t(XH - 14, PIN_Y(n) + 3, f"{n} {nm}", 9, "end", PALETTE["title"]))
    card.add(f'<rect x="{XH - 8}" y="{PIN_Y(1) - 10}" width="16" height="6" fill="{C_P12}"/>'.replace(C_P12, "#c0392b"))
    pin_w = {}

    def merge(pins, color, out_y):
        ys = [PIN_Y(p) for p in pins]
        for y in ys:
            pin_w[y] = wire([(XH, y), (XM, y)], color)
        v = wire([(XM, ys[0]), (XM, ys[-1])], color)
        return "".join(pin_w[y] for y in ys) + v + wire([(XM, out_y), (XM + 8, out_y)], color,
                                                        junctions=[(XM, out_y)])

    yn12, ygnd, yp12, yp5 = 130, 210, 290, 330
    card.add(merge((1, 2), C_N12, yn12))
    card.add(merge(tuple(range(3, 9)), C_GND, ygnd))
    card.add(merge((9, 10), C_P12, yp12))
    card.add(merge((11, 12), C_5V, yp5))
    for n in range(1, 17):
        card.add(_dot(XH, PIN_Y(n), 3.5))

    # rack rail diodes (reverse protection) on +12 V and -12 V
    card.add(wire([(XM + 8, yn12), (205, yn12)], C_N12))
    card.add(diode_left(205, yn12, "BAT85"))
    card.add(wire([(235, yn12), (BUS_E["N12"], yn12)], C_N12))
    card.add(tag(200, 142, "PROVISIONAL"))
    card.add(wire([(XM + 8, yp12), (205, yp12)], C_P12))
    card.add(diode(205, yp12, "BAT85"))
    card.add(wire([(235, yp12), (BUS_E["P12"], yp12)], C_P12))
    card.add(tag(200, 302, "PROVISIONAL"))
    card.add(wire([(XM + 8, ygnd), (BUS_E["GND"], ygnd)], C_GND))
    card.add(wire([(XM + 8, yp5), (BUS_E["P5"], yp5)], C_5V))

    # buses
    tap = {"p12": XCOL + 0, }
    a_v, a_n, a_g = 427, 457, 487
    f_y = 710                   # VSYS filter tap
    l_g, l_3 = 613, 578
    p_gnd = 760
    card.add(bar_v(BUS_E["N12"], yn12, a_n, C_N12, "-12V"))
    card.add(bar_v(BUS_E["GND"], ygnd, STAR_Y, C_GND, "GND"))
    card.add(bar_v(BUS_E["P12"], yp12, a_v, C_P12, "+12V"))
    card.add(bar_v(BUS_E["P5"], yp5, f_y, C_5V, "+5V"))

    # analog utilities
    card.add(wire([(XCOL, a_v), (BUS_E["P12"], a_v)], C_P12, junctions=[(BUS_E["P12"], a_v)]))
    card.add(wire([(XCOL, a_n), (BUS_E["N12"], a_n)], C_N12, junctions=[(BUS_E["N12"], a_n)]))
    card.add(wire([(XCOL, a_g), (BUS_E["GND"], a_g)], C_GND, junctions=[(BUS_E["GND"], a_g)]))
    card.add(box(XCOL, 405, XW, 110, ["Analog utilities"],
                 ["Slew: TL072 + 2x 1N4148", "LFO: TL072 + CD40106", "S&H: LF398 + TL072"],
                 left=[("V+", a_v), ("V-", a_n), ("GND", a_g)]))
    card.add(tag(XCOL, 520, "UNVERIFIED", "UNVERIFIED circuits, CD40106 supply TO DESIGN"))

    # 3V3 loads
    card.add(wire([(XCOL, l_g), (BUS_E["GND"], l_g)], C_GND, junctions=[(BUS_E["GND"], l_g)]))
    card.add(box(XCOL, 556, XW, 80, ["3V3 loads (Pico 3V3 OUT)"],
                 ["OLED 1.3in I2C, encoder +", "I2C0 pull-ups 4.7k", "CD4049UB clock buffers"],
                 left=[("GND", l_g)], right=[("3V3", l_3 + 0)]))
    card.add(tag(XCOL, 642, "UNVERIFIED", "UNVERIFIED load"))

    # VSYS filter and Pico
    card.add(wire([(470, f_y), (BUS_E["P5"], f_y)], C_5V, junctions=[(BUS_E["P5"], f_y)]))
    card.add(box(470, 690, 130, 40, ["VSYS filter"], ["D+bulk+100nF"],
                 left=[("IN", f_y)], right=[("OUT", f_y)]))
    card.add(wire([(600, f_y), (620, f_y)], C_5V))
    card.add(box(620, 690, 110, 80, ["Raspberry Pi Pico"], [],
                 left=[("VSYS 39", f_y), ("GND 38", p_gnd)], right=[("3V3 36", f_y)]))
    card.add(wire([(620, p_gnd), (BUS_E["GND"], p_gnd)], C_GND, junctions=[(BUS_E["GND"], p_gnd)]))
    card.add(wire([(730, f_y), (765, f_y), (765, l_3), (XCOL + XW, l_3)], C_3V3,
                  junctions=[(765, l_3)]))
    card.add(tag(470, 736, "PROVISIONAL", "PROVISIONAL diode, see Pico card"))

    # budget panel
    s, _ = notes(490, 76, 300, "Current budget (design values)", [
        "Rack +12 V: 1 A, -12 V: 1 A (CP1A QSG p20).",
        "Rack +5 V: 0.5 A, shared with the rack (CP1A QSG p20).",
        "Pico 3V3 OUT: keep the load under 300 mA (Pico datasheet p9).",
        ("Pico draw from VSYS.", "UNVERIFIED"),
        ("OLED, encoder and pull-up load on 3V3.", "UNVERIFIED"),
        ("Analog utilities draw on +/-12 V.", "UNVERIFIED"),
        ("Rack +5 V present on the owner's bus slot (BT-12).", "UNVERIFIED"),
    ])
    card.add(s)

    # star
    card.add(f'<circle cx="{BUS_E["GND"]}" cy="{STAR_Y}" r="5" fill="{C_GND}" stroke="#444"/>')
    card.add(label_box(BUS_E["GND"] - 12 - 155, STAR_Y - 7, "expander star (rack 0 V)"))


def _mb(card):
    card.add(_frame(830, 56, 670, 744, "MICROBRUTE SIDE (synth domain)",
                    "Buffer-only breakout board, powered only from TP70, TP71, TP72."))
    card.add(label_box(XT, 94, "Synth TPs"))

    ytp70, ytp72, ytp71 = 130, 190, 250
    for name, y, lab in (("TP70", ytp70, "+12V"), ("TP72", ytp72, "GND"), ("TP71", ytp71, "-12V")):
        card.add(f'<rect x="{XT}" y="{y - 11}" width="70" height="22" rx="3" fill="#e4e4dc" '
                 f'stroke="#555" stroke-width="1.2"/>'
                 + _t(XT + 6, y + 3, f"{name} {lab}", 9, "start", PALETTE["title"], True)
                 + _dot(XT + 70, y, 3.5))
    bn, bg, bp = BUS_M["N12"], BUS_M["GND"], BUS_M["P12"]
    # +12 V: TP70 -> BAT85 (anode at TP70) -> +12V_BRK
    card.add(wire([(XT + 70, ytp70), (960, ytp70)], C_P12))
    card.add(diode(960, ytp70, "BAT85"))
    card.add(wire([(990, ytp70), (bp, ytp70)], C_P12))
    card.add(tag(955, 142, "PROVISIONAL"))
    # -12 V: TP71 -> BAT85 (CATHODE toward TP71, anode to the breakout rail) -> -12V_BRK
    card.add(wire([(XT + 70, ytp71), (960, ytp71)], C_N12))
    card.add(diode_left(960, ytp71, "BAT85"))
    card.add(wire([(990, ytp71), (bn, ytp71)], C_N12))
    card.add(tag(955, 262, "PROVISIONAL"))
    card.add(wire([(XT + 70, ytp72), (bg, ytp72)], C_GND))

    y_cn, y_cp = 310, 360
    ya, yb, yc = 352, 382, 412       # op-amp taps
    y78i, y78g = 492, 522
    yu3g, yu3v = 632, 602
    card.add(bar_v(bn, ytp71, yb, C_N12, "-12V_BRK"))
    card.add(bar_v(bg, ytp72, 1100, C_GND, "GND"))
    card.add(bar_v(bp, ytp70, y78i, C_P12, "+12V_BRK"))

    # bulk caps between adjacent rails
    card.add(wire([(bn, y_cn), (bn + 15, y_cn)], C_N12))
    card.add(wire([(bn + 45, y_cn), (bg, y_cn)], C_GND))
    card.add(capacitor(bn + 15, y_cn, "10uF"))
    card.add(wire([(bp, y_cp), (bp - 15, y_cp)], C_P12))
    card.add(wire([(bp - 45, y_cp), (bg, y_cp)], C_GND))
    card.add(capacitor(bp - 45, y_cp, "10uF"))

    # op-amp consumer
    card.add(wire([(XMC, ya), (bp, ya)], C_P12, junctions=[(bp, ya)]))
    card.add(wire([(XMC, yb), (bn, yb)], C_N12, junctions=[(bn, yb)]))
    card.add(wire([(XMC, yc), (bg, yc)], C_GND, junctions=[(bg, yc)]))
    card.add(box(XMC, 330, 210, 100, ["U1 TL074, U2 TL072"], ["buffers, envelope, LFO"],
                 left=[("V+", ya), ("V-", yb), ("GND", yc)]))

    # 78L05 and CD40106
    card.add(wire([(XMC, y78i), (bp, y78i)], C_P12, junctions=[(bp, y78i)]))
    card.add(wire([(XMC, y78g), (bg, y78g)], C_GND, junctions=[(bg, y78g)]))
    card.add(box(XMC, 470, 210, 70, ["78L05 (owned)"], ["local 5 V for U3 only"],
                 left=[("IN", y78i), ("GND", y78g)], right=[("OUT", y78i)]))
    card.add(tag(XMC, 546, "PROVISIONAL", "PROVISIONAL (BF 3.4)"))
    card.add(wire([(XMC, yu3g), (bg, yu3g)], C_GND, junctions=[(bg, yu3g)]))
    card.add(box(XMC, 580, 210, 70, ["U3 CD40106"], ["gate Schmitt, 2 gates"],
                 left=[("VSS", yu3g)], right=[("VDD", yu3v)]))
    card.add(tag(XMC, 656, "PROVISIONAL", "PROVISIONAL (BF 3.4)"))
    card.add(wire([(XMC + 210, y78i), (1488, y78i), (1488, yu3v), (XMC + 210, yu3v)], C_5V))
    card.add(label_box(1412, 543, "+5V_LOCAL"))

    s, _ = notes(850, 300, 190, "Breakout notes", [
        "Powered only from TP70, TP71, TP72. No synth 5 V or 3V3 is tapped.",
        ("Rail protection is open (audit C12): BAT85 shown; owned 1N5819 or "
         "a 4.7-10 ohm series resistor also allowed.", "OPEN"),
        "-12 V diode: cathode to TP71, anode to the breakout rail (CM 5.3).",
        "Bulk: 2-4x owned 10uF/63V per rail in parallel (BF 1.4).",
        "78L05: 3.8 mA quiescent, about 27 mW (BF 3.4).",
        ("CD40106 at 5 V needs TP83 above 3.6 V.", "UNVERIFIED"),
        ("Synth rail headroom for the breakout load (audit E-04).", "UNVERIFIED"),
    ])
    card.add(s)
    card.add(f'<circle cx="{bg}" cy="{STAR_Y}" r="5" fill="{C_GND}" stroke="#444"/>')
    card.add(label_box(bg + 12, STAR_Y - 7, "TP72 star"))


def _cable(card):
    xl, xr = 440, 1070
    gl, gr = BUS_E["GND"], BUS_M["GND"]
    card.add(_t(gl + 20, 830, "DB-9 CABLES (left end: expander, right end: MicroBrute): signals and grounds only", 12, "start", PALETTE["title"], True))
    card.add(f'<rect x="500" y="842" width="540" height="44" rx="6" fill="#fff" '
             f'stroke="#c0392b" stroke-width="2"/>'
             + _t(770, 861, "NO SUPPLY ON THE CABLE", 13, "middle", "#c0392b", True)
             + _t(770, 877, "no +12 V, -12 V, +5 V or 3V3 conductor; each side is powered on its own",
                  9, "middle", PALETTE["text"]))
    # connector shells
    for (y1, y2, nm) in ((896, 962, "DB-9 A"), (976, 1062, "DB-9 B")):
        for x, side in ((xl, "expander end"), (xr, "MicroBrute end")):
            card.add(f'<rect x="{x}" y="{y1}" width="20" height="{y2 - y1}" rx="4" fill="#d8d8d0" '
                     f'stroke="#555" stroke-width="1.2"/>')
        card.add(_t(xl + 10, y1 - 5, nm, 10, "middle", PALETTE["title"], True))
        card.add(_t(xr + 10, y1 - 5, nm, 10, "middle", PALETTE["title"], True))
    ya_s, ya_g = 922, 950
    yb_s = 1000
    yb_g = [1030, 1036, 1042, 1048, 1054]
    # signals (not supply)
    card.add(wire([(xl + 10, ya_s), (xr + 10, ya_s)], C_SIG))
    card.add(label_box(560, ya_s - 7, "A:1 Gate  A:2 Pitch  A:3 Env  A:4 LFO  A:5 Mix  A:6 VCF  A:7 Saw  A:8 Square"))
    card.add(wire([(xl + 10, yb_s), (xr + 10, yb_s)], C_SIG))
    card.add(label_box(640, yb_s - 7, "B:1 UART TX  B:6 UART RX  B:3 VCA CV  B:5 Filter CV"))
    # grounds from star to star
    card.add(wire([(gl, ya_g), (gr, ya_g)], C_GND, junctions=[(gl, ya_g), (gr, ya_g)]))
    card.add(label_box(740, ya_g - 7, "A:9 GND"))
    for y in yb_g:
        card.add(wire([(gl, y), (gr, y)], C_GND, junctions=[(gl, y), (gr, y)]))
    card.add(label_box(700, 1011, "B:2  B:4  B:7  B:8  B:9 GND, ground tie"))
    card.add(f'<rect x="{gl - 4}" y="{STAR_Y}" width="8" height="{yb_g[-1] + 6 - STAR_Y}" rx="3" fill="{C_GND}"/>')
    # TP72 star bar is drawn to y=1090 by the GND bus
    # shield: braid bonded to the MicroBrute shell only, cut back at the expander end
    ysh = 1092
    card.add(f'<polyline points="{xl + 50},{ysh} {xr + 10},{ysh}" fill="none" stroke="#777" '
             f'stroke-width="2" stroke-dasharray="6 4"/>')
    card.add(wire([(xr + 10, ysh), (xr + 10, 1062)], "#777"))
    card.add(wire([(xr + 10, ysh), (gr, ysh)], "#777", junctions=[(gr, ysh)]))
    card.add(_line(xl + 36, ysh - 6, xl + 46, ysh + 6, "#c0392b", 2))
    card.add(_line(xl + 46, ysh - 6, xl + 36, ysh + 6, "#c0392b", 2))
    card.add(label_box(xr - 380, ysh - 22, "braid bonded to the MicroBrute shell, short lead to TP72"))
    card.add(label_box(xl + 56, ysh + 8, "braid cut back and insulated at the expander end; shell isolated from the panel"))
    card.add(tag(xl + 56, ysh + 26, "UNVERIFIED", "UNVERIFIED washers not owned (Q10), bench check BT-8"))


def build():
    card = Card(W, H, "Power Chain - split power, rack to expander, synth to breakout",
                "No supply rail crosses the DB-9 cables: only signals and ground. Design values, nothing built yet")
    _expander(card)
    _mb(card)
    _cable(card)
    card.legend([(C_P12, "+12 V"), (C_N12, "-12 V"), (C_5V, "+5 V"), (C_3V3, "3V3 (Pico out)"),
                 (C_GND, "GND and ground tie"), (C_SIG, "signal conductor, no supply")])
    return card


def render():
    return build().render()


def main():
    problems = validate_nets(NETS, RAILS)
    if problems:
        sys.exit("net problems:\n  " + "\n  ".join(problems))
    OUT.write_text(render())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
