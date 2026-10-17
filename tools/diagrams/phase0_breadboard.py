"""Phase 0 breadboard layout card -> schematics/phase0_breadboard.svg.

Run from the repo root:  python3 -m tools.diagrams.phase0_breadboard

Top view of a half-size solderless board (30 columns, rows a-e / f-j, centre
channel, + and - rails). The Pico straddles the channel with its USB end to the
right. Every part lead and every jumper has a hole name (row letter + column
number). The jumper table is generated from the same JUMPERS list that is
drawn, and the nets are the ones the wiring card uses (phase0_nets).
"""
import math
import sys
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import (BB_PITCH, PALETTE, PICO_NAMES, Card, _dot, _line, _n, _t,
                               breadboard, breadboard_pins, jack, jack_pins, label_box,
                               wire)
from tools.diagrams.phase0_nets import (CLOCK_IN_NOTE, CS_NOTE, MISSING_PARTS, NETS, RAILS,  # noqa: F401
                                        RGB_ORDER)
from tools.hwdata.pico import FIRMWARE_ROLES as R
from tools.hwdata.pico import PICO_PHYSICAL_PIN

OUT = Path(__file__).resolve().parents[2] / "schematics" / "phase0_breadboard.svg"

C_3V3, C_GND = PALETTE["p3v3"], PALETTE["gnd"]
C_SPI, C_LED = PALETTE["audio"], PALETTE["p12"]
C_GPIO, C_CLK = PALETTE["cv"], PALETTE["clock"]
COLOUR_NAME = {C_3V3: "amber", C_GND: "green", C_SPI: "blue", C_LED: "red",
               C_GPIO: "orange", C_CLK: "violet"}

W, H = 1010, 1150
X0, Y0 = 70, 330            # hole a1
PINS = breadboard_pins(X0, Y0)
HALO = "#fbfaf4"


def hxy(hole):
    return PINS.xy(hole)


def colx(c):
    return X0 + (c - 1) * BB_PITCH


def gp(role):
    return f"GP{R[role]}"


# --------------------------------------------------------------- pico map
def pico_hole(pin):
    """USB end to the right: pins 1-20 run right to left on row c, pins 21-40
    left to right on row h (column 31 - n and n - 10)."""
    return f"c{31 - pin}" if pin <= 20 else f"h{pin - 10}"


# ------------------------------------------------------------------ leads
# (part, pin, hole). Part and pin spellings match phase0_nets.NETS.
LEADS = [("PICO", PICO_NAMES[n - 1], pico_hole(n)) for n in range(1, 41)]
LEADS += [
    ("R", "220_R.a", "e1"), ("R", "220_R.b", "f1"),
    ("R", "220_G.a", "e3"), ("R", "220_G.b", "f3"),
    ("R", "220_B.a", "e4"), ("R", "220_B.b", "f4"),
    ("LED", "R_A", "h1"), ("LED", "K", "h2"), ("LED", "G_A", "h3"), ("LED", "B_A", "h4"),
    ("BTN", "1", "e5"), ("BTN", "2", "f5"),
    ("ENC", "GND", "c6"), ("ENC", "+", "c7"), ("ENC", "SW", "c8"),
    ("ENC", "DT", "c9"), ("ENC", "CLK", "c10"),
    ("R", "1K_OUT.a", "g9"), ("R", "1K_OUT.b", "g6"),
    ("R", "1K_IN.a", "i10"), ("R", "1K_IN.b", "i7"),
]


def _phys(role):
    return PICO_PHYSICAL_PIN[R[role]]


# ---------------------------------------------------------------- jumpers
def _jumper(kind, net, a_end, a_hole, b_end, b_hole, color, lane=None, dashed=False, via=()):
    return {"kind": kind, "net": net, "a_end": a_end, "a_hole": a_hole,
            "b_end": b_end, "b_hole": b_hole, "color": color, "lane": lane,
            "dashed": dashed, "via": tuple(via)}


def _top_signal(role, net, dest_end, dest_hole, lane, color):
    src = "a" + pico_hole(_phys(role))[1:]
    return _jumper("signal", net, ("PICO", gp(role)), src, dest_end, dest_hole, color, lane)


# routing channel between the OLED module and the top lanes
JOG_RES_Y2, JOG_DC_Y, JOG_RES_Y = 188, 206, 226  # DC and RES swap columns here
JOG_RES_X = colx(24) + BB_PITCH / 2


def _oled(role, pin, via=()):
    """Pico top-row hole of a role to the OLED module pin."""
    return _jumper("module", role, ("PICO", gp(role)), "a" + pico_hole(_phys(role))[1:],
                   ("OLED", pin), None, C_SPI, via=via)


JUMPERS = [
    # signal jumpers from the Pico's top row, nested lanes above the board
    _top_signal("LED_CLOCK", "LED_R", ("R", "220_R.a"), "a1", 7, C_LED),
    _top_signal("LED_GATE", "LED_G", ("R", "220_G.a"), "a3", 6, C_LED),
    _top_signal("LED_MODE", "LED_B", ("R", "220_B.a"), "a4", 5, C_LED),
    _top_signal("BTN_TAP", "BTN_TAP", ("BTN", "1"), "a5", 4, C_GPIO),
    _top_signal("ENC_SW", "ENC_SW", ("ENC", "SW"), "a8", 3, C_GPIO),
    _top_signal("ENC_DT", "ENC_DT", ("ENC", "DT"), "a9", 2, C_GPIO),
    _top_signal("ENC_CLK", "ENC_CLK", ("ENC", "CLK"), "a10", 1, C_GPIO),
    # 7-pin SPI OLED module (off the board) wired down to the board
    _oled("OLED_SCK", "D0"),
    _oled("OLED_MOSI", "D1"),
    _oled("OLED_DC", "DC", via=[(colx(25), JOG_DC_Y), (colx(24), JOG_DC_Y)]),
    _oled("OLED_RES", "RES", via=[(colx(24), JOG_RES_Y), (JOG_RES_X, JOG_RES_Y),
                                  (JOG_RES_X, JOG_RES_Y2), (colx(25), JOG_RES_Y2)]),
    # CS strapped to GND: straight down to the top GND rail (PROVISIONAL, BT-14)
    _jumper("module", "GND", ("OLED", "CS"), None, ("RAIL", "GND"), "-T23", C_GND),
    _jumper("module", "3V3", ("OLED", "VCC"), None, ("RAIL", "3V3"), "+T28", C_3V3),
    _jumper("module", "GND", ("OLED", "GND"), None, ("RAIL", "GND"), "-T29", C_GND),
    # power taps
    _jumper("power", "3V3", ("ENC", "+"), "a7", ("RAIL", "3V3"), "+T7", C_3V3),
    _jumper("power", "GND", ("ENC", "GND"), "a6", ("RAIL", "GND"), "-T6", C_GND),
    _jumper("power", "GND", ("LED", "K"), "j2", ("RAIL", "GND"), "-B2", C_GND),
    _jumper("power", "GND", ("BTN", "2"), "j5", ("RAIL", "GND"), "-B5", C_GND),
    _jumper("power", "3V3", ("PICO", "3V3"), "j26", ("RAIL", "3V3"), "+B26", C_3V3),
    _jumper("power", "GND", ("PICO", "GND"), "j28", ("RAIL", "GND"), "-B28", C_GND),
    _jumper("power", "GND", ("PICO", "GND"), "a28", ("RAIL", "GND"), "-T28", C_GND),
    _jumper("bridge", "3V3", ("RAIL", "3V3"), "+B1", ("RAIL", "3V3"), "+T1", C_3V3),
    # clock loop-back: Pico bottom row to the 1k resistors, jacks, test jumper
    _jumper("signal", "CLOCK_OUT", ("PICO", gp("CLOCK_OUT")), "j" + pico_hole(_phys("CLOCK_OUT"))[1:],
            ("R", "1K_OUT.a"), "j9", C_CLK, 2),
    _jumper("signal", "CLOCK_IN", ("PICO", gp("CLOCK_IN")), "j" + pico_hole(_phys("CLOCK_IN"))[1:],
            ("R", "1K_IN.a"), "j10", C_CLK, 1),
    _jumper("test", None, ("JUMPER", "A"), "h6", ("JUMPER", "B"), "h10", C_CLK, dashed=True),
    _jumper("module", "CLOCK_OUT_JACK", ("R", "1K_OUT.b"), "j6", ("JACK_OUT", "T"), None, C_CLK),
    _jumper("module", "CLOCK_IN_JACK", ("R", "1K_IN.b"), "j7", ("JACK_IN", "T"), None, C_CLK),
    _jumper("module", "GND", ("JACK_OUT", "S"), None, ("RAIL", "GND"), "-B8", C_GND),
    _jumper("module", "GND", ("JACK_IN", "S"), None, ("RAIL", "GND"), "-B21", C_GND),
]

# ------------------------------------------------------- off-board geometry
OLED_X = {"CS": colx(23), "DC": colx(24), "RES": colx(25), "D1": colx(26), "D0": colx(27),
          "VCC": colx(28), "GND": colx(29)}
OLED_BOX = (colx(23) - 18, 64, 6 * BB_PITCH + 36, 66)
OLED_PIN_Y = OLED_BOX[1] + OLED_BOX[3]
JACK_Y = 805
JACK_OUT_X = colx(6) + 2
JACK_IN_X = colx(21) - 24


def _module_xy(end):
    part, pin = end
    if part == "OLED":
        return OLED_X[pin], OLED_PIN_Y
    jx = JACK_OUT_X if part == "JACK_OUT" else JACK_IN_X
    return (jx if pin == "T" else jx + 24), JACK_Y


def _end_xy(end, hole):
    return hxy(hole) if hole else _module_xy(end)


LANE_TOP_Y = lambda k: PINS.xy("+T1")[1] - 28 - 9 * k          # noqa: E731
LANE_BOT_Y = lambda k: PINS.xy("+B1")[1] + 22 + 12 * k         # noqa: E731
JACK_RUN_Y = PINS.xy("+B1")[1] + 22 + 12 * 3 + 6               # tip-IN horizontal run


def _route(j):
    ax, ay = _end_xy(j["a_end"], j["a_hole"])
    bx, by = _end_xy(j["b_end"], j["b_hole"])
    k = j["kind"]
    if j["lane"] is not None and j["a_hole"][0] == "a":
        ly = LANE_TOP_Y(j["lane"])
        return [(ax, ay), (ax, ly), (bx, ly), (bx, by)]
    if j["lane"] is not None:
        ly = LANE_BOT_Y(j["lane"])
        return [(ax, ay), (ax, ly), (bx, ly), (bx, by)]
    if k == "bridge":
        lx = X0 - 30
        return [(ax, ay), (lx, ay), (lx, by), (bx, by)]
    if k == "module" and "JACK" in j["a_end"][0] + j["b_end"][0]:
        jack_end = j["a_end"] if "JACK" in j["a_end"][0] else j["b_end"]
        mx, my = _module_xy(jack_end)
        hx, hy = (bx, by) if jack_end == j["a_end"] else (ax, ay)
        if jack_end == ("JACK_IN", "T"):
            return [(mx, my), (mx, JACK_RUN_Y), (hx, JACK_RUN_Y), (hx, hy)]
        if abs(mx - hx) < 0.5:
            return [(mx, my), (hx, hy)]
        return [(mx, my), (mx, my - 12), (hx, my - 12), (hx, hy)]
    return [(ax, ay), *j["via"], (bx, by)]


def _length_class(j):
    ax, ay = _end_xy(j["a_end"], j["a_hole"])
    bx, by = _end_xy(j["b_end"], j["b_hole"])
    holes = math.hypot(ax - bx, ay - by) / BB_PITCH
    return "S" if holes <= 6 else ("M" if holes <= 14 else "L")


def _desc(end):
    part, pin = end
    if part == "RAIL":
        return f"{pin} rail"
    if part == "PICO":
        return pin
    if part == "R":
        return pin
    return f"{part} {pin}"


def jumper_rows():
    rows = []
    for i, j in enumerate(JUMPERS, 1):
        ha = j["a_hole"] or "mod"
        hb = j["b_hole"] or "mod"
        rows.append({"n": i, "from": f"{ha} {_desc(j['a_end'])}", "to": f"{hb} {_desc(j['b_end'])}",
                     "colour": COLOUR_NAME[j["color"]], "length": _length_class(j),
                     "net": j["net"] or "test"})
    return rows


# ----------------------------------------------------------------- drawing
def _wire(points, color, dashed=False):
    halo = wire(points, HALO).replace('stroke-width="2"', 'stroke-width="5.5"')
    w = wire(points, color)
    if dashed:
        w = w.replace("<polyline", '<polyline stroke-dasharray="6 4"', 1)
    return halo + w


def _tag(x, y, text):
    w = len(text) * 5.6 + 10
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="14" rx="3" fill="#fff3cd" '
            f'stroke="#c96a00" stroke-width="1"/>'
            + _t(x + 5, y + 10.5, text, 9, "start", "#7a4100", True))


def _missing(x, y, text):
    """Red tag for a part that is not owned."""
    w = len(text) * 5.6 + 10
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="14" rx="3" fill="#fde2e1" '
            f'stroke="#b3261e" stroke-width="1"/>'
            + _t(x + 5, y + 10.5, text, 9, "start", "#8c1d18", True))


def _pico_svg():
    top = hxy("c11")[1]
    bot = hxy("h11")[1]
    x1, x2 = colx(11) - 8, colx(30) + 14
    out = [f'<rect x="{_n(x1)}" y="{_n(top - 16)}" width="{_n(x2 - x1)}" '
           f'height="{_n(bot - top + 32)}" rx="5" fill="#3b7d4f" stroke="#2a5c39" stroke-width="1.5"/>']
    ym = (hxy("e1")[1] + hxy("f1")[1]) / 2
    usb_y = ym - 15
    out.append(f'<rect x="{_n(x2 - 1)}" y="{_n(usb_y)}" width="22" height="30" rx="3" '
               f'fill="#cfcfc7" stroke="#555" stroke-width="1.2"/>')
    out.append(_t(x2 + 10, ym + 3.5, "USB", 9, "middle", "#222", True))
    for n in range(1, 41):
        hole = pico_hole(n)
        px, py = hxy(hole)
        name = PICO_NAMES[n - 1]
        is_gnd = "GND" in name
        out.append(_dot(px, py, 3.5, PALETTE["gnd"] if is_gnd else PALETTE["pin"]))
        if n <= 20:
            out.append(_t(px, py + 15, n, 9, "middle", "#fff"))
            out.append(f'<text x="{_n(px + 3.5)}" y="{_n(py + 24)}" font-size="9" '
                       f'transform="rotate(90 {_n(px + 3.5)} {_n(py + 24)})" fill="#fff" '
                       f'font-weight="bold">{name}</text>')
        else:
            out.append(_t(px, py - 8, n, 9, "middle", "#fff"))
            out.append(f'<text x="{_n(px + 3.5)}" y="{_n(py - 20)}" font-size="9" '
                       f'transform="rotate(-90 {_n(px + 3.5)} {_n(py - 20)})" fill="#fff" '
                       f'font-weight="bold">{name}</text>')
    # pin-1 marker; the Pico body hides the kit's column numbers, so 11-30 are redrawn on it
    p1x, p1y = hxy("c30")
    out.append(f'<rect x="{_n(p1x - 9)}" y="{_n(p1y - 9)}" width="18" height="18" rx="2" '
               f'fill="none" stroke="#fff" stroke-width="1.8"/>')
    cy = ym + 3.5
    for c in range(11, 31):
        out.append(f'<text x="{_n(colx(c))}" y="{_n(cy)}" font-size="10" text-anchor="middle" '
                   f'fill="none" stroke="#3b7d4f" stroke-width="3">{c}</text>')
        out.append(_t(colx(c), cy, c, 10, "middle", "#e8f3ea", True))
    out.append(label_box(x2 + 28, p1y - 7, "pin 1 corner"))
    out.append(label_box(x2 + 28, ym - 7 + 34, "Pico, top view"))
    return "".join(out)


def _lead(pin, part="R"):
    return [h for p, q, h in LEADS if (p, q) == (part, pin)][0]


def _resistor_v(col, label):
    x = colx(col)
    yt, yb = hxy(f"e{col}")[1], hxy(f"f{col}")[1]
    ym = (yt + yb) / 2 - 24
    return (_line(x, yt, x, yb, "#444", 2)
            + f'<rect x="{_n(x - 7)}" y="{_n(ym - 14)}" width="14" height="28" rx="2" '
              f'fill="{PALETTE["body"]}" stroke="#8a6d3b" stroke-width="1"/>'
            + f'<text x="{_n(x + 3)}" y="{_n(ym)}" font-size="9" text-anchor="middle" '
              f'transform="rotate(-90 {_n(x + 3)} {_n(ym)})" fill="#222" font-weight="bold">{label}</text>'
            + _dot(x, yt, 3) + _dot(x, yb, 3))


def _resistor_h(row, c1, c2, label):
    y = hxy(f"{row}{c1}")[1]
    xa, xb = colx(c1), colx(c2)
    xm = (xa + xb) / 2
    return (_line(xa, y, xb, y, "#444", 2)
            + f'<rect x="{_n(xm - 18)}" y="{_n(y - 7)}" width="36" height="14" rx="2" '
              f'fill="{PALETTE["body"]}" stroke="#8a6d3b" stroke-width="1"/>'
            + _t(xm, y + 3.2, label, 9, "middle", "#222", True)
            + _dot(xa, y, 3) + _dot(xb, y, 3))


def _led_svg():
    cx = (colx(1) + colx(4)) / 2
    cy = hxy("h1")[1]
    out = [f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="42" fill="#ffffff" fill-opacity="0.55" '
           f'stroke="#777" stroke-width="1.2"/>']
    legs = {"h1": ("R", C_LED), "h2": ("K", "#333"), "h3": ("G", PALETTE["gate"]),
            "h4": ("B", C_SPI)}
    for hole, (ltr, col) in legs.items():
        x, y = hxy(hole)
        out.append(_dot(x, y, 4, col))
        out.append(_t(x, y - 9, ltr, 10, "middle", "#222", True))
    return "".join(out)


def _button_svg():
    x = colx(5)
    yt, yb = hxy("e5")[1], hxy("f5")[1]
    ym = (yt + yb) / 2 - 24
    return (_line(x, yt, x, yb, "#444", 2)
            + f'<rect x="{_n(x - 10)}" y="{_n(ym - 14)}" width="20" height="28" rx="3" '
              f'fill="#555" stroke="#222" stroke-width="1"/>'
            + f'<circle cx="{_n(x)}" cy="{_n(ym)}" r="6" fill="#bbb" stroke="#222" stroke-width="1"/>'
            + _dot(x, yt, 3) + _dot(x, yb, 3))


def _enc_svg():
    x1, x2 = colx(6) - 10, colx(10) + 10
    y = hxy("c6")[1]
    out = [f'<rect x="{_n(x1)}" y="{_n(y - 9)}" width="{_n(x2 - x1)}" height="18" rx="2" '
           f'fill="#2d2d2d" stroke="#111" stroke-width="1"/>']
    for i, name in enumerate(("GND", "+", "SW", "DT", "CLK")):
        px = colx(6 + i)
        out.append(_dot(px, y, 3.5))
        ty = hxy("d6")[1]
        out.append(f'<rect x="{_n(px - 12)}" y="{_n(ty - 7)}" width="24" height="14" rx="2" fill="#ece6d2"/>')
        out.append(_t(px, ty + 3.5, name, 9, "middle", PALETTE["title"], True))
    out.append(label_box(x1 + 2, hxy("e6")[1] - 7, "KY-040 header"))
    return "".join(out)


def _oled_svg():
    x, y, w, h = OLED_BOX
    out = [f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="4" fill="#e4e4dc" '
           f'stroke="#555" stroke-width="1.2"/>',
           _t(x + w / 2, y + 17, "1.3in OLED module", 11, "middle", PALETTE["title"], True),
           _t(x + w / 2, y + 30, "7-pin SPI, chip per marking", 9, "middle", PALETTE["muted"]),
           _t(x + w / 2, y + 42, "flipped: header toward board", 9, "middle", PALETTE["muted"])]
    for name, px in OLED_X.items():
        out.append(_t(px, y + h - 5, name, 9, "middle", PALETTE["title"], True))
        out.append(_dot(px, OLED_PIN_Y, 3.5))
    return "".join(out)


def _rail_labels():
    out = []
    for rail, txt in (("+T", "3V3 rail"), ("-T", "GND rail"), ("-B", "GND rail"), ("+B", "3V3 rail")):
        x, y = hxy(f"{rail}1")
        out.append(label_box(colx(30) + 30, y - 7, txt))
    return "".join(out)


def build():
    card = Card(W, H, "Phase 0 - Pico Breadboard Layout",
                "Half-size breadboard, top view, 3V3 logic only. Hole = column number + row letter.")
    # reading notes
    notes = [
        "Rows a-e of a column are one strip, rows f-j another; rails run the full length.",
        "Pico straddles the channel: pins 1-20 on row c (pin 1 at column 30), pins 21-40 on row h.",
        "Rails: outer bar is 3V3, inner bar is GND, top and bottom 3V3 rails joined by one bridge.",
    ]
    card.add(f'<rect x="30" y="56" width="530" height="102" rx="4" fill="#fff" '
             f'stroke="{PALETTE["stroke"]}" stroke-width="1"/>')
    for i, line in enumerate(notes):
        card.add(_t(40, 73 + i * 14, line, 9, "start", PALETTE["text"]))
    card.add(_tag(40, 113, "UNVERIFIED: hole grid assumes a standard 0.1 in half-size board"))
    card.add(_tag(40, 132, "UNVERIFIED: continuous rails assumed (some boards split them)"))

    card.add(breadboard(X0, Y0))
    card.add(_rail_labels())
    card.add(_pico_svg())

    # parts on the board
    for name in ("220_R", "220_G", "220_B"):
        card.add(_resistor_v(int(_lead(name + ".a")[1:]), "220"))
    card.add(_led_svg())
    card.add(_button_svg())
    card.add(_enc_svg())
    for name in ("1K_OUT", "1K_IN"):
        ha, hb = _lead(name + ".a"), _lead(name + ".b")
        assert ha[0] == hb[0]
        card.add(_resistor_h(ha[0], *sorted((int(ha[1:]), int(hb[1:]))), "1k"))
    card.add(label_box(colx(1) - 8, hxy("c1")[1] - 7, "RGB LED + 3 x 220R"))
    card.add(label_box(colx(1) - 8, hxy("d1")[1] - 7, "Tap button"))

    # off-board modules
    card.add(_oled_svg())
    card.add(jack(JACK_OUT_X, JACK_Y, f"CLOCK OUT ({gp('CLOCK_OUT')})"))
    card.add(jack(JACK_IN_X, JACK_Y, f"CLOCK IN ({gp('CLOCK_IN')})"))
    ty = 712
    for i, line in enumerate(CLOCK_IN_NOTE):
        card.add(_tag(640, ty + 18 * i, line))
    for i, line in enumerate(MISSING_PARTS):
        card.add(_missing(640, ty + 40 + 18 * i, line))
    card.add(_tag(640, ty + 40 + 18 * len(MISSING_PARTS), RGB_ORDER))

    # wires on top
    for j in JUMPERS:
        pts = _route(j)
        card.add(_wire(pts, j["color"], j["dashed"]))
    for j in JUMPERS:
        for end, hole in ((j["a_end"], j["a_hole"]), (j["b_end"], j["b_hole"])):
            x, y = _end_xy(end, hole)
            card.add(_dot(x, y, 3.5, j["color"]))
    tj = [j for j in JUMPERS if j["kind"] == "test"][0]
    mx = (hxy(tj["a_hole"])[0] + hxy(tj["b_hole"])[0]) / 2
    card.add(label_box(mx - 32, hxy(tj["a_hole"])[1] - 7, "test jumper"))

    # tags for anything not verified
    card.add(_tag(OLED_BOX[0] + OLED_BOX[2] + 6, 70, "UNVERIFIED: OLED chip"))
    card.add(_tag(OLED_BOX[0] + OLED_BOX[2] + 6, 88, "UNVERIFIED: OLED pin order"))
    card.add(_tag(OLED_BOX[0] + OLED_BOX[2] + 6, 106, CS_NOTE))
    card.add(_tag(colx(6) - 10, hxy("b6")[1] - 7, "UNVERIFIED: KY-040 header order, read silkscreen"))

    _tables(card)
    card.legend([(C_3V3, "3V3 supply"), (C_GND, "GND"), (C_SPI, "SPI0 main OLED"),
                 (C_LED, "RGB LED drive"), (C_GPIO, "Button and encoder"),
                 (C_CLK, "Clock in and out")])
    return card


def _tables(card):
    y0 = 880
    card.add(_t(30, y0, "Part leads (hole)", 11, "start", PALETTE["title"], True))
    groups = {}
    for part, pin, hole in LEADS:
        if part == "PICO":
            continue
        groups.setdefault(part if part != "R" else "R " + pin.split(".")[0], []).append((pin.split(".")[-1] if part == "R" else pin, hole))
    names = {"R 220_R": "220R red", "R 220_G": "220R green", "R 220_B": "220R blue",
             "R 1K_OUT": "1k clock out", "R 1K_IN": "1k clock in", "LED": "RGB LED",
             "BTN": "Tap button", "ENC": "KY-040"}
    y = y0 + 16
    for key, leads in groups.items():
        card.add(_t(30, y, names.get(key, key), 9, "start", PALETTE["text"], True))
        card.add(_t(130, y, "  ".join(f"{p} {h}" for p, h in leads), 9, "start", PALETTE["text"]))
        y += 14
    card.add(_t(30, y + 2, "Pico: pin n at c(31-n) for n<=20, h(n-10) for n>=21", 9, "start", PALETTE["muted"]))
    card.add(_t(30, y + 16, "Length class: S up to 6 holes, M 7-14 holes, L longer", 9, "start", PALETTE["muted"]))

    rows = jumper_rows()
    card.add(_t(430, y0, "Jumper table (from, to, colour, length)", 11, "start", PALETTE["title"], True))
    half = (len(rows) + 1) // 2
    for i, r in enumerate(rows):
        col, k = divmod(i, half)
        x = 430 + col * 265
        yy = y0 + 16 + k * 14
        j = JUMPERS[i]
        card.add(f'<line x1="{x}" y1="{yy - 3}" x2="{x + 12}" y2="{yy - 3}" stroke="{j["color"]}" '
                 f'stroke-width="4" stroke-linecap="round"/>')
        txt = f'{r["n"]:02d} {r["from"]} > {r["to"]}  {r["length"]}'
        card.add(_t(x + 18, yy, txt, 9, "start", PALETTE["text"]))


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
