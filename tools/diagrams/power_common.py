"""Shared drawing helpers for the power chain and Pico protection cards.

Status tags, a module box, a left-pointing diode, a vertical capacitor and a
word-wrapped note panel. Everything is built from tools.diagram_kit helpers so
the cards keep the approved Phase 0 visual language.
"""
import textwrap

from tools.diagram_kit import PALETTE, _dot, _line, _n, _t, label_box

C_5V = "#7a4b1e"     # +5 V rail colour (same as the Pico pinout card)
C_SIG = "#8a8a80"    # signal conductor (not a supply)

TAG_STYLE = {
    "PROVISIONAL": ("#fff1c2", "#c98a00"),
    "UNVERIFIED": ("#fde3e3", "#c0392b"),
    "OWNER-CONFIRM": ("#e3ecfd", "#2a5bd7"),
    "OPEN": ("#ece3fd", "#6a3fc4"),
}
TAG_CHAR = 5.6


def tag_w(text):
    return len(text) * TAG_CHAR + 8


def tag(x, y, kind, text=None):
    """Visible status tag (top-left x, y). kind picks the colours."""
    text = text or kind
    fill, edge = TAG_STYLE[kind]
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(tag_w(text))}" height="13" rx="3" '
            f'fill="{fill}" stroke="{edge}" stroke-width="1"/>'
            + _t(x + 4, y + 10, text, 9, "start", edge, bold=True))


def box(x, y, w, h, title, lines=(), left=(), right=()):
    """Module body, title above, pin names inside the edges."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#e4e4dc" '
           f'stroke="#555" stroke-width="1.2"/>']
    for i, tl in enumerate(title):
        out.append(_t(x, y - 6 - 12 * (len(title) - 1 - i), tl, 11 if i == 0 else 10,
                      "start", PALETTE["title"] if i == 0 else PALETTE["muted"], bold=(i == 0)))
    for i, tl in enumerate(lines):
        out.append(_t(x + w / 2, y + h / 2 + 3 + (i - (len(lines) - 1) / 2) * 13, tl, 9,
                      "middle", PALETTE["muted"]))
    for name, py in left:
        out.append(_t(x + 6, py + 3, name, 9, "start", PALETTE["title"], bold=True))
        out.append(_dot(x, py, 3.5))
    for name, py in right:
        out.append(_t(x + w - 6, py + 3, name, 9, "end", PALETTE["title"], bold=True))
        out.append(_dot(x + w, py, 3.5))
    return "".join(out)


def diode_left(ox, oy, label):
    """Diode flowing right to left: cathode at ox, anode at ox + 30."""
    tri = (f'<path d="M{_n(ox + 22)},{_n(oy - 7)} L{_n(ox + 22)},{_n(oy + 7)} '
           f'L{_n(ox + 9)},{_n(oy)} Z" fill="#333" stroke="#222" stroke-width="1"/>')
    w = len(label) * 6.2 + 6
    return (_line(ox, oy, ox + 30, oy) + tri + _line(ox + 8, oy - 7, ox + 8, oy + 7, "#222", 2)
            + label_box(ox + 15 - w / 2, oy - 25, label) + _dot(ox, oy) + _dot(ox + 30, oy))


def cap_v(x, y, label, polar=False):
    """Vertical capacitor: top lead at (x, y), bottom lead at (x, y + 30)."""
    out = (_line(x, y, x, y + 12) + _line(x, y + 18, x, y + 30)
           + _line(x - 9, y + 12, x + 9, y + 12, "#222", 2.5)
           + _line(x - 9, y + 18, x + 9, y + 18, "#222", 2.5)
           + label_box(x + 14, y + 8, label) + _dot(x, y) + _dot(x, y + 30))
    if polar:
        out += _t(x - 16, y + 9, "+", 11, "middle", "#222", True)
    return out


def bar_v(x, y1, y2, color, label=None, label_above=True):
    """Thick vertical rail bar centred on x, with an optional boxed name."""
    out = (f'<rect x="{_n(x - 4)}" y="{_n(y1)}" width="8" height="{_n(y2 - y1)}" rx="3" '
           f'fill="{color}"/>')
    if label:
        w = len(label) * 6.2 + 6
        out += label_box(x - w / 2, (y1 - 20) if label_above else (y2 + 6), label)
    return out


def notes(x, y, w, title, rows, size=9):
    """Word-wrapped bullet panel. rows: text or (text, tag_kind_or_None).
    Returns (svg, bottom_y). Panel is a white card with a border."""
    cw = 5.5 if size == 9 else 6.1
    inner = int((w - 20) // cw)
    body, cy = [], y + 30
    for row in rows:
        text, kind = (row, None) if isinstance(row, str) else row
        first_off = (tag_w(kind) + 5) if kind else 0
        first_chars = max(8, int((w - 20 - first_off) // cw))
        lines = textwrap.wrap(text, first_chars)
        if len(lines) > 1:
            rest = textwrap.wrap(" ".join(lines[1:]), inner)
            lines = [lines[0]] + rest
        if kind:
            body.append(tag(x + 10, cy - 10, kind))
        for i, ln in enumerate(lines):
            body.append(_t(x + 10 + (first_off if i == 0 else 0), cy, ln, size, "start",
                           PALETTE["text"]))
            cy += 13
        cy += 5
    h = cy - y + 2
    frame = (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" rx="4" '
             f'fill="#fff" stroke="{PALETTE["stroke"]}" stroke-width="1"/>'
             + _t(x + 10, y + 16, title, 11, "start", PALETTE["title"], bold=True))
    return frame + "".join(body), y + h
