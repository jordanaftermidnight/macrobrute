"""Shared SVG diagram kit in the stripboard-template visual style.

Light board-coloured card, fixed-width font, colour-coded rails, a legend,
and label boxes with an opaque background so wires never run through text.

Every function is pure and deterministic. Glyph functions return an SVG
fragment string. Each glyph has a matching ``*_pins`` helper returning a
``PartPins`` so a generator can route wires to exact pin coordinates.
Every glyph and helper takes an optional ``anchor`` (a pin name): the named
pin is then placed at (x, y) instead of the part's default origin.
"""

from dataclasses import dataclass
from html import escape as _esc

from tools.hwdata.pico import PICO_PHYSICAL_PIN

FONT = '"SF Mono", Consolas, "Liberation Mono", monospace'
CHAR_W = 6.2        # label width per character at 10px
MIN_FONT = 9

PALETTE = {
    "card": "#f5f5ee",
    "title": "#222",
    "text": "#333",
    "muted": "#555",
    "stroke": "#b8b8a8",
    "ink": "#2d2d2d",
    "body": "#c4a265",
    "p12": "#d9534f",
    "n12": "#6a5acd",
    "gnd": "#5cb85c",
    "p5": "#e8a317",
    "p3v3": "#e8a317",
    "audio": "#1f6fd1",
    "cv": "#c96a00",
    "gate": "#1a9a3a",
    "clock": "#8a2be2",
    "pin": "#e8a317",
    "label_bg": "#ffffff",
}


def _n(v):
    """Compact deterministic number formatting."""
    v = round(float(v), 2)
    return str(int(v)) if v == int(v) else repr(v)


def _t(x, y, text, size=10, anchor="start", fill=None, bold=False):
    fill = fill or PALETTE["text"]
    w = ' font-weight="bold"' if bold else ""
    return (f'<text x="{_n(x)}" y="{_n(y)}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}"{w}>{_esc(str(text))}</text>')


def _line(x1, y1, x2, y2, color=None, w=1.5):
    color = color or PALETTE["ink"]
    return (f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" '
            f'stroke="{color}" stroke-width="{_n(w)}" stroke-linecap="round"/>')


def _dot(x, y, r=3, fill=None):
    return (f'<circle cx="{_n(x)}" cy="{_n(y)}" r="{_n(r)}" '
            f'fill="{fill or PALETTE["pin"]}" stroke="#444" stroke-width="0.8"/>')


@dataclass(frozen=True)
class PartPins:
    """Pin coordinates of one placed part."""
    points: tuple  # tuple of (name, (x, y)) in drawing order

    def xy(self, name):
        for n, p in self.points:
            if n == str(name):
                return p
        raise KeyError(name)

    @property
    def names(self):
        return [n for n, _ in self.points]

    def as_dict(self):
        return dict(self.points)


def _place(offsets, x, y, anchor):
    """offsets: list of (name, (dx, dy)). Returns (ox, oy, PartPins)."""
    ox, oy = x, y
    if anchor is not None:
        d = dict(offsets)
        if str(anchor) not in d:
            raise KeyError(anchor)
        ox, oy = x - d[str(anchor)][0], y - d[str(anchor)][1]
    pins = PartPins(tuple((str(n), (ox + dx, oy + dy)) for n, (dx, dy) in offsets))
    return ox, oy, pins


def _lab(cx, cy, text):
    """Centred label with opaque background, sized from the text."""
    w = len(str(text)) * CHAR_W + 6
    return label_box(cx - w / 2, cy - 7, text)


# ---------------------------------------------------------------- label box
def label_box(x, y, text):
    """White rounded box (top-left x, y) with text; hides wires beneath."""
    w = len(str(text)) * CHAR_W + 6
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="14" rx="3" '
            f'fill="{PALETTE["label_bg"]}" stroke="{PALETTE["stroke"]}" stroke-width="0.8"/>'
            + _t(x + 3, y + 10.5, text, 10))


# --------------------------------------------------------------------- wire
def wire(points, color, junctions=()):
    pts = " ".join(f"{_n(px)},{_n(py)}" for px, py in points)
    out = (f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
           f'stroke-linejoin="round" stroke-linecap="round"/>')
    for jx, jy in junctions:
        out += f'<circle cx="{_n(jx)}" cy="{_n(jy)}" r="3.5" fill="{color}"/>'
    return out


# ----------------------------------------------------------------- resistor
def _res_off(horizontal):
    return [("a", (0, 0)), ("b", (40, 0) if horizontal else (0, 40))]


def resistor_pins(x, y, horizontal=True, anchor=None):
    return _place(_res_off(horizontal), x, y, anchor)[2]


def resistor(x, y, label, horizontal=True, anchor=None):
    ox, oy, p = _place(_res_off(horizontal), x, y, anchor)
    if horizontal:
        s = (_line(ox, oy, ox + 40, oy)
             + f'<rect x="{_n(ox + 8)}" y="{_n(oy - 5)}" width="24" height="10" rx="2" '
               f'fill="{PALETTE["body"]}" stroke="#8a6d3b" stroke-width="1"/>'
             + _lab(ox + 20, oy - 16, label))
    else:
        s = (_line(ox, oy, ox, oy + 40)
             + f'<rect x="{_n(ox - 5)}" y="{_n(oy + 8)}" width="10" height="24" rx="2" '
               f'fill="{PALETTE["body"]}" stroke="#8a6d3b" stroke-width="1"/>'
             + _lab(ox + 8 + (len(str(label)) * CHAR_W + 6) / 2, oy + 20, label))
    return s + "".join(_dot(*xy) for _, xy in p.points)


# ------------------------------------------------------- diode / led / cap
_TWO_H = [("a", (0, 0)), ("k", (30, 0))]


def diode_pins(x, y, anchor=None):
    return _place(_TWO_H, x, y, anchor)[2]


def _tri(ox, oy, fill):
    return (_line(ox, oy, ox + 30, oy)
            + f'<path d="M{_n(ox + 8)},{_n(oy - 7)} L{_n(ox + 8)},{_n(oy + 7)} '
              f'L{_n(ox + 21)},{_n(oy)} Z" fill="{fill}" stroke="#222" stroke-width="1"/>'
            + _line(ox + 22, oy - 7, ox + 22, oy + 7, "#222", 2))


def diode(x, y, label, anchor=None):
    ox, oy, p = _place(_TWO_H, x, y, anchor)
    return (_tri(ox, oy, "#333") + _lab(ox + 15, oy - 18, label)
            + "".join(_dot(*xy) for _, xy in p.points))


_LED = [("a", (0, 0)), ("k", (30, 0))]


def led_pins(x, y, anchor=None):
    return _place(_LED, x, y, anchor)[2]


def led(x, y, label, color, anchor=None):
    ox, oy, p = _place(_LED, x, y, anchor)
    rays = (_line(ox + 12, oy - 9, ox + 18, oy - 15, color, 1.2)
            + _line(ox + 17, oy - 6, ox + 23, oy - 12, color, 1.2))
    return (_tri(ox, oy, color) + rays + _lab(ox + 15, oy + 20, label)
            + "".join(_dot(*xy) for _, xy in p.points))


_CAP = [("a", (0, 0)), ("b", (30, 0))]


def capacitor_pins(x, y, anchor=None):
    return _place(_CAP, x, y, anchor)[2]


def capacitor(x, y, label, anchor=None):
    ox, oy, p = _place(_CAP, x, y, anchor)
    return (_line(ox, oy, ox + 12, oy) + _line(ox + 18, oy, ox + 30, oy)
            + _line(ox + 12, oy - 9, ox + 12, oy + 9, "#222", 2.5)
            + _line(ox + 18, oy - 9, ox + 18, oy + 9, "#222", 2.5)
            + _lab(ox + 15, oy - 20, label)
            + "".join(_dot(*xy) for _, xy in p.points))


# --------------------------------------------------------------- 3.5 mm jack
_JACK = [("tip", (0, 0)), ("sleeve", (24, 0))]


def jack_pins(x, y, anchor=None):
    return _place(_JACK, x, y, anchor)[2]


def jack(x, y, label, anchor=None):
    ox, oy, p = _place(_JACK, x, y, anchor)
    return (f'<rect x="{_n(ox - 8)}" y="{_n(oy + 6)}" width="40" height="28" rx="4" '
            f'fill="#d8d8d0" stroke="#555" stroke-width="1.2"/>'
            f'<circle cx="{_n(ox + 12)}" cy="{_n(oy + 20)}" r="8" fill="#444" '
            f'stroke="#222" stroke-width="1"/>'
            f'<circle cx="{_n(ox + 12)}" cy="{_n(oy + 20)}" r="3" fill="#bbb"/>'
            + _t(ox - 1, oy - 5, "T", 9, "middle", bold=True)
            + _t(ox + 25, oy - 5, "S", 9, "middle", bold=True)
            + _lab(ox + 12, oy + 46, label)
            + "".join(_dot(*xy) for _, xy in p.points))


# ---------------------------------------------------------------------- DIP
DIP_PITCH = 16
DIP_W = 100
DIP_STUB = 10


def _dip_off(pins):
    n = len(pins)
    half = n // 2
    off = []
    for i in range(half):
        off.append((str(i + 1), (0, 14 + i * DIP_PITCH)))
    for i in range(half):
        off.append((str(n - i), (DIP_W + 2 * DIP_STUB, 14 + i * DIP_PITCH)))
    return sorted(off, key=lambda t: int(t[0]))


def dip_pins(x, y, pins, anchor=None):
    return _place(_dip_off(pins), x, y, anchor)[2]


def dip(x, y, name, pins, anchor=None):
    """pins: names in physical order 1..n (left side down, right side up)."""
    n = len(pins)
    half = n // 2
    ox, oy, p = _place(_dip_off(pins), x, y, anchor)
    bx, bw, bh = ox + DIP_STUB, DIP_W, 14 + (half - 1) * DIP_PITCH + 12
    out = [f'<rect x="{_n(bx)}" y="{_n(oy + 2)}" width="{bw}" height="{_n(bh - 2)}" rx="3" '
           f'fill="{PALETTE["ink"]}" stroke="#111" stroke-width="1"/>',
           f'<path d="M{_n(bx + bw / 2 - 6)},{_n(oy + 2)} a6,6 0 0 0 12,0" '
           f'fill="#555"/>']
    for i, pname in enumerate(pins):
        num = i + 1
        px, py = p.xy(num)
        if num <= half:
            out.append(_line(px, py, bx, py, "#888", 2))
            out.append(_t(bx + 4, py + 3, pname, 9, "start", "#fff"))
        else:
            out.append(_line(bx + bw, py, px, py, "#888", 2))
            out.append(_t(bx + bw - 4, py + 3, pname, 9, "end", "#fff"))
    out.append(_t(ox + DIP_STUB + DIP_W / 2, oy - 5, name, 12, "middle",
                  PALETTE["title"], bold=True))
    out += [_dot(*xy, r=2.5) for _, xy in p.points]
    return "".join(out)


# --------------------------------------------------------------------- DB-9
DB9_PITCH = 22


DB9_W = 4 * DB9_PITCH
DB9_FACES = {
    # face -> (mirrored relative to the male front view, caption)
    "male-front": (False, "front view, male (pins)"),
    "female-front": (True, "front view, female (sockets)"),
    "male-solder": (True, "solder-cup side, male"),
    "female-solder": (False, "solder-cup side, female"),
}


def _db9_off(face="male-front"):
    if face not in DB9_FACES:
        raise ValueError(f"unknown DB-9 face {face!r}")
    mirror = DB9_FACES[face][0]
    off = []
    for i in range(5):
        off.append((str(i + 1), (i * DB9_PITCH, 0)))
    for i in range(4):
        off.append((str(i + 6), (DB9_PITCH / 2 + i * DB9_PITCH, 26)))
    if mirror:
        off = [(n, (DB9_W - dx, dy)) for n, (dx, dy) in off]
    return off


def db9_pins(x, y, anchor=None, face="male-front"):
    return _place(_db9_off(face), x, y, anchor)[2]


def db9(x, y, title, anchor=None, face="male-front"):
    """Pins 1-5 in the top row, 6-9 in the bottom row, title above, and a
    caption below naming the face drawn. Default face is "male-front".

    D-sub numbering is mirrored between faces: the female front view and the
    male solder-cup view show pin 1 at top right; the male front view and
    the female solder-cup view show pin 1 at top left.
    """
    ox, oy, p = _place(_db9_off(face), x, y, anchor)
    # body is placed from the unmirrored origin so the shape never moves
    w = DB9_W
    left = min(px for _, (px, _) in p.points)
    out = [f'<path d="M{_n(left - 16)},{_n(oy - 12)} L{_n(left + w + 16)},{_n(oy - 12)} '
           f'L{_n(left + w + 8)},{_n(oy + 38)} L{_n(left - 8)},{_n(oy + 38)} Z" '
           f'fill="#e4e4dc" stroke="#555" stroke-width="1.5" stroke-linejoin="round"/>']
    for name, (px, py) in p.points:
        out.append(f'<circle cx="{_n(px)}" cy="{_n(py)}" r="8" fill="#fff" '
                   f'stroke="#444" stroke-width="1"/>')
        out.append(_t(px, py + 3.2, name, 9, "middle", PALETTE["title"], bold=True))
    out.append(_t(left + w / 2, oy - 20, title, 11, "middle", PALETTE["title"], bold=True))
    out.append(_t(left + w / 2, oy + 54, DB9_FACES[face][1], 9, "middle", PALETTE["muted"]))
    return "".join(out)


# ------------------------------------------------------------- Pico header
_PICO_FIXED = {
    3: "GND", 8: "GND", 13: "GND", 18: "GND", 23: "GND", 28: "GND", 38: "GND",
    30: "RUN", 33: "AGND", 35: "ADC_VREF", 36: "3V3", 37: "3V3_EN",
    39: "VSYS", 40: "VBUS",
}


def _pico_names():
    """Physical pin 1..40 -> label. GPn comes from the canonical pin map."""
    names = {phys: f"GP{gp}" for gp, phys in PICO_PHYSICAL_PIN.items()}
    overlap = set(names) & set(_PICO_FIXED)
    if overlap or len(names) + len(_PICO_FIXED) != 40:
        raise ValueError(f"Pico pin map inconsistent: {sorted(overlap)}")
    names.update(_PICO_FIXED)
    return [names[i] for i in range(1, 41)]


PICO_NAMES = _pico_names()
PICO_PITCH = 14
PICO_W = 64


def _pico_off():
    off = []
    for i in range(20):
        off.append((str(i + 1), (0, i * PICO_PITCH)))
    for i in range(20):
        off.append((str(40 - i), (PICO_W, i * PICO_PITCH)))
    return sorted(off, key=lambda t: int(t[0]))


def pico_header_pins(x, y, anchor=None):
    return _place(_pico_off(), x, y, anchor)[2]


def pico_header(x, y, title, anchor=None):
    """Pico 40-pin header: physical pin numbers inside, GP labels outside."""
    ox, oy, p = _place(_pico_off(), x, y, anchor)
    out = [f'<rect x="{_n(ox - 6)}" y="{_n(oy - 8)}" width="{PICO_W + 12}" '
           f'height="{20 * PICO_PITCH + 2}" rx="4" fill="#3b7d4f" stroke="#2a5c39" '
           f'stroke-width="1.2"/>']
    for i in range(40):
        num = i + 1
        px, py = p.xy(num)
        gp = PICO_NAMES[i]
        col = PALETTE["gnd"] if "GND" in gp else "#fff"
        if num <= 20:
            out.append(_t(px + 8, py + 3, num, 9, "start", "#fff"))
            out.append(_t(px - 10, py + 3, gp, 9, "end", PALETTE["title"], bold=True))
        else:
            out.append(_t(px - 8, py + 3, num, 9, "end", "#fff"))
            out.append(_t(px + 10, py + 3, gp, 9, "start", PALETTE["title"], bold=True))
        out.append(_dot(px, py, 3, col if col != "#fff" else PALETTE["pin"]))
    out.append(_t(ox + PICO_W / 2, oy - 14, title, 12, "middle", PALETTE["title"], bold=True))
    return "".join(out)


# ------------------------------------------------------------ header block
HB_PITCH = 18


def _hb_off(pins):
    return [(str(i + 1), (0, i * HB_PITCH)) for i in range(len(pins))]


def header_block_pins(x, y, pins, anchor=None):
    return _place(_hb_off(pins), x, y, anchor)[2]


def header_block(x, y, label, pins, anchor=None):
    """Single-row header drawn as a column; pin names to the right."""
    ox, oy, p = _place(_hb_off(pins), x, y, anchor)
    out = [f'<rect x="{_n(ox - 8)}" y="{_n(oy - 9)}" width="16" '
           f'height="{_n(len(pins) * HB_PITCH)}" rx="3" fill="#2d2d2d" stroke="#111" '
           f'stroke-width="1"/>']
    for i, name in enumerate(pins):
        px, py = p.xy(i + 1)
        out.append(_dot(px, py, 3.5))
        out.append(_t(px + 14, py + 3.5, f"{i + 1} {name}", 10, "start"))
    out.append(_t(ox - 8, oy - 15, label, 11, "start", PALETTE["title"], bold=True))
    return "".join(out)


# --------------------------------------------------------------------- Card
class Card:
    def __init__(self, width, height, title, subtitle=""):
        self.width, self.height = width, height
        self.title, self.subtitle = title, subtitle
        self._parts = []
        self._legend = []

    def add(self, svg_fragment):
        self._parts.append(svg_fragment)

    def legend(self, items):
        """items: (colour, text) pairs."""
        self._legend = list(items)

    def _legend_svg(self):
        if not self._legend:
            return ""
        col_w = max(len(t) for _, t in self._legend) * CHAR_W + 44
        per_row = max(1, int((self.width - 40) // col_w))
        rows = (len(self._legend) + per_row - 1) // per_row
        y0 = self.height - 14 - rows * 18
        out = [_t(20, y0 - 6, "Legend", 11, "start", PALETTE["title"], bold=True)]
        for i, (color, text) in enumerate(self._legend):
            x = 20 + (i % per_row) * col_w
            y = y0 + 8 + (i // per_row) * 18
            out.append(f'<line x1="{_n(x)}" y1="{_n(y)}" x2="{_n(x + 22)}" y2="{_n(y)}" '
                       f'stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
            out.append(_t(x + 30, y + 3.5, text, 10))
        return "".join(out)

    def render(self):
        w, h = self.width, self.height
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
                f'width="{w}" height="{h}">'
                f'<style>text {{ font-family: {FONT}; }}</style>'
                f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="6" '
                f'fill="{PALETTE["card"]}" stroke="{PALETTE["stroke"]}" stroke-width="1"/>'
                + _t(w / 2, 24, self.title, 16, "middle", PALETTE["title"], bold=True)
                + _t(w / 2, 40, self.subtitle, 11, "middle", PALETTE["muted"]))
        return head + "".join(self._parts) + self._legend_svg() + "</svg>"
