#!/usr/bin/env python3
"""Generate SVG stripboard layouts for MACROBRUTE.

Produces visual diagrams with:
- Copper tracks, holes, and board grid
- Color-coded IC packages, resistors, caps, diodes
- Track cuts marked in red
- Jumper wires as colored lines
- Clear labels and legend

Usage: python3 tools/generate_layouts.py
Output: schematics/*.svg
"""

import os
from html import escape as _esc

CELL = 30           # px per grid hole
HOLE_R = 4          # hole radius
MARGIN_L = 90       # left margin for row labels
MARGIN_T = 55       # top margin for col labels
PAD = 30            # board edge padding

# Colors
C_BOARD = "#E8D5A3"
C_COPPER = "#CD853F"
C_COPPER_STROKE = "#B8722D"
C_HOLE = "#444"
C_IC = "#2D2D2D"
C_IC_NOTCH = "#555"
C_RESISTOR = "#C4A265"
C_CAP_CER = "#4A90D9"
C_CAP_ELEC = "#8B4513"
C_DIODE = "#333"
C_CUT = "#FF0000"
C_JUMPER = ["#0066CC", "#CC6600", "#009933", "#CC0066", "#6600CC", "#CC9900"]
C_RAIL_12V = "#D44"
C_RAIL_GND = "#4A4"
C_RAIL_N12V = "#44D"
C_RAIL_5V = "#D84"


def xy(row, col):
    """Row/col (1-based) → center pixel coords."""
    return MARGIN_L + (col - 1) * CELL + CELL // 2, MARGIN_T + (row - 1) * CELL + CELL // 2


def svg_start(cols, rows, title, extra_h=0):
    w = MARGIN_L + cols * CELL + PAD
    h = MARGIN_T + rows * CELL + PAD + extra_h
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '<defs>',
        '  <style>',
        '    text { font-family: "SF Mono", Consolas, "Liberation Mono", monospace; }',
        '    .title { font-size: 16px; font-weight: bold; fill: #222; }',
        '    .subtitle { font-size: 11px; fill: #555; }',
        '    .row-label { font-size: 11px; fill: #444; font-weight: bold; text-anchor: end; dominant-baseline: central; }',
        '    .col-label { font-size: 11px; fill: #444; font-weight: bold; text-anchor: middle; }',
        '    .ic-name { font-size: 12px; fill: #FFF; text-anchor: middle; font-weight: bold; dominant-baseline: central; }',
        '    .ic-type { font-size: 10px; fill: #DDD; text-anchor: middle; dominant-baseline: central; }',
        '    .pin { font-size: 9px; fill: #222; font-weight: bold; text-anchor: middle; dominant-baseline: central; filter: url(#textshadow); }',
        '    .comp { font-size: 9px; fill: #111; font-weight: bold; text-anchor: middle; dominant-baseline: central; filter: url(#textshadow); }',
        '    .rail { font-size: 11px; fill: #FFF; font-weight: bold; dominant-baseline: central; }',
        '    .cut-x { stroke: #FF0000; stroke-width: 2.5; stroke-linecap: round; }',
        '    .legend-text { font-size: 10px; fill: #333; dominant-baseline: central; }',
        '    .legend-title { font-size: 11px; fill: #222; font-weight: bold; dominant-baseline: central; }',
        '    .zone-label { font-size: 10px; fill: #444; font-weight: bold; font-style: italic; dominant-baseline: central; filter: url(#textshadow); }',
        '    .note { font-size: 9px; fill: #222; dominant-baseline: central; filter: url(#textshadow); }',
        '  </style>',
        '  <filter id="textshadow" x="-5%" y="-5%" width="110%" height="110%">',
        '    <feFlood flood-color="white" flood-opacity="0.85" result="bg"/>',
        '    <feMorphology in="SourceGraphic" operator="dilate" radius="2" result="dilated"/>',
        '    <feComposite in="bg" in2="dilated" operator="in" result="shadow"/>',
        '    <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '  </filter>',
        '  <marker id="arrowhead" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">',
        '    <polygon points="0 0, 6 2, 0 4" fill="#CC0000"/>',
        '  </marker>',
        '</defs>',
        f'<rect width="{w}" height="{h}" fill="#F5F5F0"/>',
        f'<text x="{w // 2}" y="20" class="title" text-anchor="middle">{title}</text>',
        f'<text x="{w // 2}" y="36" class="subtitle" text-anchor="middle">Component side (top view) — Copper tracks run horizontally</text>',
    ]
    return lines


def svg_board(cols, rows):
    """Draw board background, copper tracks, holes, row/col labels."""
    lines = []
    bx = MARGIN_L - 8
    by = MARGIN_T - 8
    bw = cols * CELL + 16
    bh = rows * CELL + 16

    # Board background
    lines.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{C_BOARD}" '
                 f'rx="4" stroke="#B8A070" stroke-width="1.5"/>')

    # Copper tracks (horizontal strips)
    for r in range(1, rows + 1):
        _, cy = xy(r, 1)
        tx = MARGIN_L - 4
        tw = cols * CELL + 8
        lines.append(f'<rect x="{tx}" y="{cy - CELL // 2 + 3}" width="{tw}" height="{CELL - 6}" '
                     f'fill="{C_COPPER}" opacity="0.25" rx="2"/>')

    # Holes
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            cx, cy = xy(r, c)
            lines.append(f'<circle cx="{cx}" cy="{cy}" r="{HOLE_R}" fill="{C_HOLE}" opacity="0.5"/>')

    # Row labels
    for r in range(1, rows + 1):
        _, cy = xy(r, 1)
        lines.append(f'<text x="{MARGIN_L - 14}" y="{cy}" class="row-label">{r}</text>')

    # Col labels
    for c in range(1, cols + 1):
        cx, _ = xy(1, c)
        lines.append(f'<text x="{cx}" y="{MARGIN_T - 14}" class="col-label">{c}</text>')

    return lines


def svg_rail(row, cols, label, color):
    """Draw a highlighted power rail across the full row."""
    _, cy = xy(row, 1)
    tx = MARGIN_L - 4
    tw = cols * CELL + 8
    lines = [
        f'<rect x="{tx}" y="{cy - CELL // 2 + 2}" width="{tw}" height="{CELL - 4}" '
        f'fill="{color}" opacity="0.7" rx="3"/>',
        f'<text x="{tx + 8}" y="{cy}" class="rail">{label}</text>',
    ]
    return lines


def svg_dip(name, subname, row_start, col_left, pin_count, col_span=4, pin_labels_l=None, pin_labels_r=None):
    """Draw a DIP IC package. pin_count must be even."""
    rows_span = pin_count // 2
    col_right = col_left + col_span - 1

    x1, y1 = xy(row_start, col_left)
    x2, y2 = xy(row_start + rows_span - 1, col_right)

    rx = x1 - CELL // 2 + 3
    ry = y1 - CELL // 2 + 3
    rw = (x2 - x1) + CELL - 6
    rh = (y2 - y1) + CELL - 6

    lines = [
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{C_IC}" rx="3"/>',
        # Notch
        f'<circle cx="{rx + rw // 2}" cy="{ry + 2}" r="5" fill="{C_IC_NOTCH}"/>',
        # Name
        f'<text x="{rx + rw // 2}" y="{ry + rh // 2 - 6}" class="ic-name">{name}</text>',
        f'<text x="{rx + rw // 2}" y="{ry + rh // 2 + 8}" class="ic-type">{subname}</text>',
    ]

    # Pin numbers + trace stubs showing copper strip direction
    for i in range(rows_span):
        # Left pins (1, 2, 3, ...)
        px, py = xy(row_start + i, col_left)
        pin_num = i + 1
        # Trace stub: pin extends LEFT along the copper strip
        lines.append(f'<line x1="{rx - 1}" y1="{py}" x2="{px - CELL // 2}" y2="{py}" '
                     f'stroke="{C_COPPER}" stroke-width="2" opacity="0.6"/>')
        lines.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>')
        lines.append(f'<text x="{px - 13}" y="{py}" class="pin">{pin_num}</text>')
        if pin_labels_l and i < len(pin_labels_l):
            lines.append(f'<text x="{px - 26}" y="{py}" class="note" text-anchor="end">{pin_labels_l[i]}</text>')

        # Right pins (N, N-1, ...)
        px2, py2 = xy(row_start + i, col_right)
        pin_num_r = pin_count - i
        # Trace stub: pin extends RIGHT along the copper strip
        lines.append(f'<line x1="{rx + rw + 1}" y1="{py2}" x2="{px2 + CELL // 2}" y2="{py2}" '
                     f'stroke="{C_COPPER}" stroke-width="2" opacity="0.6"/>')
        lines.append(f'<circle cx="{px2}" cy="{py2}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>')
        lines.append(f'<text x="{px2 + 13}" y="{py2}" class="pin">{pin_num_r}</text>')
        if pin_labels_r and i < len(pin_labels_r):
            lines.append(f'<text x="{px2 + 26}" y="{py2}" class="note">{pin_labels_r[i]}</text>')

    return lines


def svg_track_cut(row, col):
    """Draw a red X at a hole position indicating a track cut."""
    cx, cy = xy(row, col)
    s = 5
    return [
        f'<line x1="{cx - s}" y1="{cy - s}" x2="{cx + s}" y2="{cy + s}" class="cut-x"/>',
        f'<line x1="{cx + s}" y1="{cy - s}" x2="{cx - s}" y2="{cy + s}" class="cut-x"/>',
    ]


def svg_resistor_h(row, col_start, col_end, label, color=C_RESISTOR):
    """Draw a horizontal resistor between two columns on the same row."""
    x1, y1 = xy(row, col_start)
    x2, _ = xy(row, col_end)
    mid_x = (x1 + x2) // 2
    lines = [
        # Solder points at each end
        f'<circle cx="{x1}" cy="{y1}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>',
        f'<circle cx="{x2}" cy="{y1}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>',
        f'<line x1="{x1}" y1="{y1}" x2="{x1 + 6}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<rect x="{x1 + 6}" y="{y1 - 4}" width="{x2 - x1 - 12}" height="8" fill="{color}" rx="2" '
        f'stroke="#8B6914" stroke-width="0.5"/>',
        f'<line x1="{x2 - 6}" y1="{y1}" x2="{x2}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<text x="{mid_x}" y="{y1 - 8}" class="comp">{label}</text>',
    ]
    return lines


def svg_resistor_v(row_start, row_end, col, label, color=C_RESISTOR):
    """Draw a vertical resistor between two rows in the same column."""
    _, y1 = xy(row_start, col)
    x2, y2 = xy(row_end, col)
    mid_y = (y1 + y2) // 2
    # Cap body height at ~24px so multi-row resistors look proportional
    max_body = 24
    span = y2 - y1
    body_h = min(max_body, span - 10)
    body_top = mid_y - body_h // 2
    lines = [
        # Solder points
        f'<circle cx="{x2}" cy="{y1}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>',
        f'<circle cx="{x2}" cy="{y2}" r="3" fill="#FFA500" stroke="#C80" stroke-width="0.5"/>',
        f'<line x1="{x2}" y1="{y1}" x2="{x2}" y2="{body_top}" stroke="#666" stroke-width="1.5"/>',
        f'<rect x="{x2 - 4}" y="{body_top}" width="8" height="{body_h}" fill="{color}" rx="2" '
        f'stroke="#8B6914" stroke-width="0.5"/>',
        f'<line x1="{x2}" y1="{body_top + body_h}" x2="{x2}" y2="{y2}" stroke="#666" stroke-width="1.5"/>',
        f'<text x="{x2 + 10}" y="{mid_y}" class="comp">{label}</text>',
    ]
    return lines


def svg_cap_h(row, col_start, col_end, label, electrolytic=False):
    """Draw a horizontal capacitor."""
    x1, y1 = xy(row, col_start)
    x2, _ = xy(row, col_end)
    mid_x = (x1 + x2) // 2
    color = C_CAP_ELEC if electrolytic else C_CAP_CER
    lines = [
        f'<line x1="{x1}" y1="{y1}" x2="{mid_x - 4}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<rect x="{mid_x - 6}" y="{y1 - 5}" width="12" height="10" fill="{color}" rx="1" '
        f'stroke="#333" stroke-width="0.5"/>',
        f'<line x1="{mid_x + 4}" y1="{y1}" x2="{x2}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<text x="{mid_x}" y="{y1 - 9}" class="comp">{label}</text>',
    ]
    if electrolytic:
        lines.append(f'<text x="{x1 + 4}" y="{y1 - 4}" class="pin">+</text>')
    return lines


def svg_cap_v(row_start, row_end, col, label, electrolytic=False):
    """Draw a vertical capacitor."""
    x1, y1 = xy(row_start, col)
    _, y2 = xy(row_end, col)
    mid_y = (y1 + y2) // 2
    color = C_CAP_ELEC if electrolytic else C_CAP_CER
    lines = [
        f'<line x1="{x1}" y1="{y1}" x2="{x1}" y2="{mid_y - 4}" stroke="#666" stroke-width="1.5"/>',
        f'<rect x="{x1 - 5}" y="{mid_y - 5}" width="10" height="10" fill="{color}" rx="1" '
        f'stroke="#333" stroke-width="0.5"/>',
        f'<line x1="{x1}" y1="{mid_y + 5}" x2="{x1}" y2="{y2}" stroke="#666" stroke-width="1.5"/>',
        f'<text x="{x1 + 12}" y="{mid_y}" class="comp">{label}</text>',
    ]
    return lines


def svg_diode_h(row, col_start, col_end, label):
    """Draw a horizontal diode (anode at col_start, cathode at col_end)."""
    x1, y1 = xy(row, col_start)
    x2, _ = xy(row, col_end)
    mid_x = (x1 + x2) // 2
    # Triangle + bar
    lines = [
        f'<line x1="{x1}" y1="{y1}" x2="{mid_x - 6}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<polygon points="{mid_x - 6},{y1 - 5} {mid_x - 6},{y1 + 5} {mid_x + 4},{y1}" '
        f'fill="{C_DIODE}"/>',
        f'<line x1="{mid_x + 4}" y1="{y1 - 5}" x2="{mid_x + 4}" y2="{y1 + 5}" stroke="{C_DIODE}" stroke-width="2"/>',
        f'<line x1="{mid_x + 4}" y1="{y1}" x2="{x2}" y2="{y1}" stroke="#666" stroke-width="1.5"/>',
        f'<text x="{mid_x}" y="{y1 - 9}" class="comp">{label}</text>',
    ]
    return lines


def svg_transistor(row, col, label, cut_collector=False):
    """Draw a transistor (TO-92) symbol at position."""
    cx, cy = xy(row, col)
    lines = [
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="#DDD" stroke="#666" stroke-width="1"/>',
        f'<text x="{cx}" y="{cy + 1}" class="comp" font-size="9">{label}</text>',
    ]
    if cut_collector:
        # Draw 3 leads: E (bottom), B (left), C (top) with snip mark on C
        # Collector lead — short stub with red X snip
        lines.append(f'<line x1="{cx}" y1="{cy - 9}" x2="{cx}" y2="{cy - 16}" '
                     f'stroke="#666" stroke-width="1.5"/>')
        lines.append(f'<line x1="{cx - 4}" y1="{cy - 14}" x2="{cx + 4}" y2="{cy - 18}" '
                     f'stroke="#FF0000" stroke-width="2.5" stroke-linecap="round"/>')
        lines.append(f'<line x1="{cx + 4}" y1="{cy - 14}" x2="{cx - 4}" y2="{cy - 18}" '
                     f'stroke="#FF0000" stroke-width="2.5" stroke-linecap="round"/>')
        # Pin labels
        lines.append(f'<text x="{cx - 13}" y="{cy}" class="pin" text-anchor="end">B</text>')
        lines.append(f'<text x="{cx}" y="{cy + 16}" class="pin">E</text>')
        lines.append(f'<text x="{cx + 8}" y="{cy - 16}" class="pin" fill="#FF0000">C ✂</text>')
    return lines


def svg_jumper(row1, col1, row2, col2, color_idx=0):
    """Draw a jumper wire (component side)."""
    x1, y1 = xy(row1, col1)
    x2, y2 = xy(row2, col2)
    color = C_JUMPER[color_idx % len(C_JUMPER)]
    # Arc for visibility — offset control point so arc is always visible
    ctrl_y = min(y1, y2) - 18
    ctrl_x = (x1 + x2) // 2
    if abs(x1 - x2) < 5:
        # Same column: push control point sideways so the arc is visible
        ctrl_x += CELL
    lines = [
        f'<path d="M{x1},{y1} Q{ctrl_x},{ctrl_y} {x2},{y2}" '
        f'fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" '
        f'stroke-dasharray="6,3"/>',
        # Solder points — larger and outlined for visibility
        f'<circle cx="{x1}" cy="{y1}" r="4" fill="{color}" stroke="white" stroke-width="1"/>',
        f'<circle cx="{x2}" cy="{y2}" r="4" fill="{color}" stroke="white" stroke-width="1"/>',
    ]
    return lines


def svg_zone_label(row, col, label):
    """Zone annotation."""
    cx, cy = xy(row, col)
    return [f'<text x="{cx}" y="{cy}" class="zone-label">{label}</text>']


def svg_callout(row, col, text_lines, color="#CC0000", anchor="start", arrow_to=None):
    """Draw a callout box with optional arrow. text_lines is a list of strings."""
    cx, cy = xy(row, col)
    line_h = 13
    pad_x, pad_y = 6, 4
    max_len = max(len(t) for t in text_lines)
    box_w = max_len * 6 + pad_x * 2
    box_h = len(text_lines) * line_h + pad_y * 2
    if anchor == "end":
        bx = cx - box_w - 4
    else:
        bx = cx + 4
    by = cy - box_h // 2
    lines = [
        f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" '
        f'fill="white" stroke="{color}" stroke-width="1.5" rx="3" opacity="0.95"/>',
    ]
    if arrow_to:
        ax, ay = xy(*arrow_to)
        lines.append(f'<line x1="{bx if anchor == "end" else bx + box_w}" y1="{cy}" '
                     f'x2="{ax}" y2="{ay}" stroke="{color}" stroke-width="1" '
                     f'stroke-dasharray="3,2" marker-end="url(#arrowhead)"/>')
    for i, t in enumerate(text_lines):
        tx = bx + pad_x
        ty = by + pad_y + line_h * (i + 1) - 2
        weight = 'font-weight="bold"' if i == 0 else ''
        lines.append(f'<text x="{tx}" y="{ty}" font-size="8" fill="{color}" '
                     f'font-family="sans-serif" {weight}>{t}</text>')
    return lines


def svg_decoupling(row_vp, row_vn, col, cols):
    """Draw a pair of 100nF decoupling caps at the V+/V- pins, connecting to nearest rail.

    Places caps 2 columns right of `col` with labels offset to avoid pin label collisions.
    """
    lines = []
    # V+ cap — offset further right to avoid pin labels
    cx, cy = xy(row_vp, col + 1)
    lines.append(f'<rect x="{cx - 5}" y="{cy - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx}" y="{cy + 12}" class="comp" font-size="8">100n</text>')
    # V- cap
    cx2, cy2 = xy(row_vn, col + 1)
    lines.append(f'<rect x="{cx2 - 5}" y="{cy2 - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx2}" y="{cy2 + 12}" class="comp" font-size="8">100n</text>')
    return lines


def svg_pot(row, col, label, value, pin1_label="CW", pin2_label="W", pin3_label="CCW"):
    """Draw a panel-mount potentiometer with 3 labeled pins.

    Pot body is off-board (panel-mount). 3 wires come down to row at col, col+1, col+2.
    Pin 1 (CW) at col, Pin 2 (Wiper) at col+1, Pin 3 (CCW) at col+2.
    """
    x1, y1 = xy(row, col)
    x2, _ = xy(row, col + 1)
    x3, _ = xy(row, col + 2)
    # Pot body (above the board)
    body_y = y1 - 28
    body_cx = x2
    lines = [
        # Pot body circle
        f'<circle cx="{body_cx}" cy="{body_y}" r="14" fill="#C0C0C0" stroke="#888" stroke-width="1.5"/>',
        # Shaft indicator
        f'<circle cx="{body_cx}" cy="{body_y}" r="3" fill="#666"/>',
        # Value + label
        f'<text x="{body_cx}" y="{body_y - 18}" class="comp">{label}</text>',
        f'<text x="{body_cx}" y="{body_y + 1}" class="comp" font-size="9">{value}</text>',
        # 3 wires from pot body down to board holes
        f'<line x1="{x1}" y1="{body_y + 14}" x2="{x1}" y2="{y1}" stroke="#888" stroke-width="1.5"/>',
        f'<line x1="{x2}" y1="{body_y + 14}" x2="{x2}" y2="{y1}" stroke="#888" stroke-width="1.5"/>',
        f'<line x1="{x3}" y1="{body_y + 14}" x2="{x3}" y2="{y1}" stroke="#888" stroke-width="1.5"/>',
        # Pin dots
        f'<circle cx="{x1}" cy="{y1}" r="3" fill="#888"/>',
        f'<circle cx="{x2}" cy="{y1}" r="3" fill="#D80"/>',  # wiper highlighted
        f'<circle cx="{x3}" cy="{y1}" r="3" fill="#888"/>',
        # Pin labels below
        f'<text x="{x1}" y="{y1 + 12}" class="comp" font-size="9">{pin1_label}</text>',
        f'<text x="{x2}" y="{y1 + 12}" class="comp" font-size="9" fill="#D80">{pin2_label}</text>',
        f'<text x="{x3}" y="{y1 + 12}" class="comp" font-size="9">{pin3_label}</text>',
    ]
    return lines


def svg_header_block(row, col_start, col_end, label, color="#666"):
    """Draw a pin header block."""
    x1, y1 = xy(row, col_start)
    x2, _ = xy(row, col_end)
    lines = [
        f'<rect x="{x1 - 6}" y="{y1 - 6}" width="{x2 - x1 + 12}" height="12" '
        f'fill="{color}" rx="2" stroke="#333" stroke-width="0.5"/>',
        f'<text x="{(x1 + x2) // 2}" y="{y1 - 10}" class="comp">{label}</text>',
    ]
    return lines


def svg_legend(y_start, items, board_cols=28):
    """Draw a legend at the bottom."""
    lines = [
        f'<text x="{MARGIN_L}" y="{y_start}" class="legend-title">Legend</text>',
    ]
    # Adapt columns to board width: fit as many as possible at 180px each
    avail_w = board_cols * CELL
    cols_per_row = max(1, avail_w // 180)
    col_w = avail_w // cols_per_row
    for i, (shape, color, label) in enumerate(items):
        x = MARGIN_L + (i % cols_per_row) * col_w
        y = y_start + 20 + (i // cols_per_row) * 18
        if shape == "rect":
            lines.append(f'<rect x="{x}" y="{y - 5}" width="14" height="10" fill="{color}" rx="2"/>')
        elif shape == "circle":
            lines.append(f'<circle cx="{x + 7}" cy="{y}" r="5" fill="{color}"/>')
        elif shape == "line":
            lines.append(f'<line x1="{x}" y1="{y}" x2="{x + 14}" y2="{y}" stroke="{color}" stroke-width="2.5"/>')
        elif shape == "x":
            lines.append(f'<line x1="{x + 2}" y1="{y - 4}" x2="{x + 12}" y2="{y + 4}" stroke="{color}" stroke-width="2"/>')
            lines.append(f'<line x1="{x + 12}" y1="{y - 4}" x2="{x + 2}" y2="{y + 4}" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{x + 20}" y="{y + 1}" class="legend-text">{label}</text>')
    return lines


# ============================================================
# BREAKOUT BOARD LAYOUT
# ============================================================

def generate_breakout():
    COLS = 28
    ROWS = 20
    lines = svg_start(COLS, ROWS, "MACROBRUTE — Breakout Board Stripboard Layout", extra_h=100)
    lines += svg_board(COLS, ROWS)

    # --- Power Rails ---
    lines += svg_rail(3, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(4, COLS, "-12V", C_RAIL_N12V)
    lines += svg_rail(5, COLS, "GND", C_RAIL_GND)

    # --- Power Input ---
    # +12V path: wire@col1 → D1 → FB1 on row 3 left end
    # Track cuts at cols 3,6 force current through D1 and FB1 in series
    lines += svg_track_cut(3, 3)
    lines += svg_track_cut(3, 6)
    lines += svg_diode_h(3, 2, 4, "D1")
    lines += svg_resistor_h(3, 5, 7, "FB1 100Ω")

    # -12V path: wire@col1 → D2 → FB2 on row 4 left end
    lines += svg_track_cut(4, 3)
    lines += svg_track_cut(4, 6)
    lines += svg_diode_h(4, 2, 4, "D2")
    lines += svg_resistor_h(4, 5, 7, "FB2 100Ω")

    # +5V path: wire → D3 on row 1, jumper to Pico VSYS pad (row 20)
    lines += svg_track_cut(1, 3)
    lines += svg_diode_h(1, 2, 4, "D3 1N5817")
    lines += svg_track_cut(1, 5)
    lines += svg_jumper(1, 4, 20, 23, 2)    # +5V → VSYS pad

    # GND: wire directly to GND rail (row 5 col 1) — no protection needed

    # Power input wire pads (labeled solder points at col 1)
    for r, lbl in [(1, "+5V"), (3, "+12V"), (4, "-12V"), (5, "GND")]:
        cx, cy = xy(r, 1)
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#FFA500" '
                     f'stroke="#C80" stroke-width="0.5"/>')
        lines.append(f'<text x="{cx}" y="{cy - 10}" class="comp" '
                     f'font-size="9">{lbl}</text>')

    # Bulk decoupling caps near right edge (rail → GND)
    lines += svg_cap_v(3, 5, 26, "100µF", electrolytic=True)  # +12V → GND
    lines += svg_cap_v(4, 5, 27, "100µF", electrolytic=True)  # -12V → GND

    # Zone labels
    lines += svg_zone_label(1, 7, "+5V → U3 &amp; Pico")

    # --- U1 TL074 (rows 6-12, cols 10-13) ---
    lines += svg_dip("U1", "TL074", 6, 10, 14, col_span=4,
                     pin_labels_l=["OUT_A", "-IN_A", "+IN_A", "V+", "+IN_B", "-IN_B", "OUT_B"],
                     pin_labels_r=["OUT_D", "-IN_D", "+IN_D", "V-", "+IN_C", "-IN_C", "OUT_C"])

    # U1 decoupling caps — V+ (pin 4, row 9 left) and V- (pin 11, row 9 right)
    # Place separately since both are on the same row
    cx1, cy1 = xy(9, 9)  # one col left of IC left pin
    lines.append(f'<rect x="{cx1 - 5}" y="{cy1 - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx1}" y="{cy1 + 12}" class="comp" font-size="8">100n V+</text>')
    cx2, cy2 = xy(9, 14)  # one col right of IC right pin
    lines.append(f'<rect x="{cx2 - 5}" y="{cy2 - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx2}" y="{cy2 + 12}" class="comp" font-size="8">100n V-</text>')

    # U1 power: V+ (pin 4, row 9, col 10 left strip) → +12V, V- (pin 11, row 9, col 13 right strip) → -12V
    lines += svg_jumper(3, 9, 9, 9, 0)    # +12V rail → V+ via left strip col 9
    lines += svg_jumper(4, 14, 9, 14, 1)  # -12V rail → V- via right strip col 14

    # U1 pin layout (rows 6-12, left=col 10, right=col 13):
    #   Row 6:  pin 1 (OUT_A)   pin 14 (OUT_D)
    #   Row 7:  pin 2 (-IN_A)   pin 13 (-IN_D)
    #   Row 8:  pin 3 (+IN_A)   pin 12 (+IN_D)
    #   Row 9:  pin 4 (V+)      pin 11 (V-)
    #   Row 10: pin 5 (+IN_B)   pin 10 (+IN_C)
    #   Row 11: pin 6 (-IN_B)   pin 9  (-IN_C)
    #   Row 12: pin 7 (OUT_B)   pin 8  (OUT_C)

    # Left-side input resistors
    lines += svg_resistor_h(8, 5, 9, "1kΩ")       # Saw → +IN_A (pin 3, row 8)
    lines += svg_resistor_h(10, 5, 9, "1kΩ")      # Sqr → +IN_B (pin 5, row 10)

    # Right-side input resistors (VCF → +IN_D at row 8, Mix → +IN_C at row 10)
    lines += svg_resistor_h(8, 21, 23, "1kΩ")
    lines += svg_resistor_h(10, 21, 23, "1kΩ")

    # Output resistors: jumper from IC output pin across cut to header zone
    # OUT_A (row 6, col 10 left) and OUT_D (row 6, col 13 right) → headers
    lines += svg_jumper(6, 10, 6, 16, 0)   # OUT_A → header zone (Saw)
    lines += svg_jumper(6, 13, 8, 17, 1)   # OUT_D → DB9A:6 (VCF, row 8)
    lines += svg_jumper(12, 10, 12, 16, 2) # OUT_B → header zone (Sqr)
    lines += svg_jumper(12, 13, 10, 17, 3) # OUT_C → DB9A:5 (Mix, row 10)

    # Right-side inputs: jumper from input resistors (cols 21+) across cut to IC pins
    lines += svg_jumper(8, 21, 8, 14, 4)   # VCF input → +IN_D (col 13 right strip)
    lines += svg_jumper(10, 21, 10, 14, 5) # Mix input → +IN_C (col 13 right strip)

    # Feedback jumpers (output → -input, same strip side)
    lines += svg_jumper(6, 10, 7, 10, 0)   # OUT_A → -IN_A (left strip)
    lines += svg_jumper(12, 10, 11, 10, 0) # OUT_B → -IN_B (left strip)
    lines += svg_jumper(12, 13, 11, 13, 1) # OUT_C → -IN_C (right strip)
    lines += svg_jumper(6, 13, 7, 13, 1)   # OUT_D → -IN_D (right strip)

    # Bias resistors (10MΩ from +IN to GND)
    lines += svg_resistor_v(5, 8, 7, "10M")   # +IN_A to GND (row 5)
    lines += svg_resistor_v(5, 10, 7, "10M")  # +IN_B to GND (row 5)

    # Input headers
    lines += svg_header_block(8, 1, 3, "TP94 Saw")
    lines += svg_header_block(10, 1, 3, "TP93 Sqr")

    # Output headers (buffer outputs → DB-9)
    lines += svg_header_block(6, 17, 19, "→ DB9A:7")    # Saw buf
    lines += svg_header_block(12, 17, 19, "→ DB9A:8")   # Sqr buf
    lines += svg_header_block(8, 17, 19, "→ DB9A:6")    # VCF buf
    lines += svg_header_block(10, 17, 19, "→ DB9A:5")   # Mix buf

    # Right-side input headers
    lines += svg_header_block(8, 24, 26, "TP19 VCF")
    lines += svg_header_block(10, 24, 26, "TP30 Mix")

    # Zone label
    lines += svg_zone_label(6, 2, "Waveform Buffers →")

    # --- U2 TL072 (rows 15-18, cols 22-25) — Mod signal buffers ---
    lines += svg_zone_label(14, 22, "Mod Signal Buffers →")
    lines += svg_dip("U2", "TL072", 15, 22, 8, col_span=4,
                     pin_labels_l=["OUT_A", "-IN_A", "+IN_A", "V-"],
                     pin_labels_r=["V+", "OUT_B", "-IN_B", "+IN_B"])

    # U2 decoupling — place left of IC to avoid colliding with output headers
    lines += svg_decoupling(15, 18, 20, COLS)

    # U2 power jumpers
    lines += svg_jumper(3, 25, 15, 25, 0)   # +12V → V+ (pin 8)
    lines += svg_jumper(4, 22, 18, 22, 1)   # -12V → V- (pin 4)

    # U2 input resistors — track cuts force current through R (not copper bypass)
    lines += svg_resistor_h(17, 17, 21, "10kΩ")       # Env → +IN_A (pin 3)
    lines += svg_resistor_h(18, 17, 20, "10kΩ")       # LFO → +IN_B (pin 5, shortened)
    lines += svg_track_cut(17, 19)                      # Env R series isolation
    lines += svg_track_cut(18, 19)                      # LFO R series isolation
    lines += svg_track_cut(18, 21)                      # isolate V- from LFO signal
    lines += svg_jumper(18, 20, 18, 25, 4)             # LFO R output → +IN_B
    lines += svg_header_block(17, 14, 16, "Env (mod)")
    lines += svg_header_block(18, 14, 16, "LFO (mod)")

    # U2 feedback jumpers
    lines += svg_jumper(15, 22, 16, 22, 2)  # pin 1→2 (OUT_A → -IN_A)
    lines += svg_jumper(16, 25, 17, 25, 3)  # pin 7→6 (OUT_B → -IN_B)

    # U2 outputs — V+ isolation on row 15
    lines += svg_track_cut(15, 26)                      # isolate V+ from header
    lines += svg_jumper(15, 22, 15, 27, 5)             # OUT_A → header
    lines += svg_header_block(15, 27, 28, "→ DB9A:3")
    lines += svg_header_block(16, 26, 28, "→ DB9A:4")

    # --- U3 CD40106 gate buffer (rows 13-19, cols 5-8) — full DIP-14 ---
    lines += svg_dip("U3", "CD40106", 13, 5, 14, col_span=4,
                     pin_labels_l=["IN_A", "OUT_A", "IN_B", "OUT_B", "IN_C", "OUT_C", "VSS"],
                     pin_labels_r=["VDD", "IN_F", "OUT_F", "IN_E", "OUT_E", "IN_D", "OUT_D"])

    # U3 gate input: TP83 → 10kΩ → IN_A (pin 1, row 13, col 5)
    lines += svg_header_block(13, 1, 2, "TP83 Gate")
    lines += svg_resistor_h(13, 3, 5, "10kΩ")
    lines += svg_track_cut(13, 4)     # series R isolation

    # U3 gate output: OUT_A (pin 2, row 14, col 5) → DB9A:1
    lines += svg_header_block(14, 1, 3, "→ DB9A:1")

    # U3 power
    lines += svg_jumper(1, 4, 13, 8, 4)   # +5V → VDD (pin 14)
    lines += svg_jumper(5, 5, 19, 5, 5)   # GND → VSS (pin 7)

    # U3 DIP center cuts + right-side isolation
    for r in range(13, 20):
        lines += svg_track_cut(r, 6)
        lines += svg_track_cut(r, 7)
        lines += svg_track_cut(r, 9)   # isolate right pins from LED/empty area

    lines += svg_zone_label(19, 1, "Gate buffer")

    # --- LED Drivers (rows 13-15, cols 10-18, right of U3) ---
    for i, (name, gpio) in enumerate([("CLK", "GP8"), ("GATE", "GP9"), ("MODE", "GP10")]):
        r = 13 + i
        lines += svg_header_block(r, 10, 10, gpio)
        lines += svg_resistor_h(r, 11, 13, "1kΩ")
        lines += svg_transistor(r, 14, f"Q{i + 1}")
        lines += svg_resistor_h(r, 15, 17, "220Ω")
        lines += svg_track_cut(r, 12)   # base R in series
        lines += svg_track_cut(r, 16)   # LED R in series
        lines += svg_jumper(r, 14, 5, 14, 3)  # Q emitter → GND rail
        cx, cy = xy(r, 18)
        # LED symbol
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#FF4444" stroke="#CC0000" stroke-width="1" opacity="0.8"/>')
        lines.append(f'<text x="{cx + 12}" y="{cy}" class="comp">{name}</text>')

    # Isolate LED zone from U2 on shared row 15
    lines += svg_track_cut(15, 19)
    lines += svg_zone_label(12, 14, "LED Drivers")

    # --- VCO — CD40106 gate B oscillator (rows 15-16 left, output via row 2) ---
    # Timing: 100kΩ feedback R (OUT_B → IN_B), 100nF C (IN_B → GND)
    lines += svg_resistor_v(15, 16, 3, "100kΩ")  # timing R: IN_B ↔ OUT_B
    lines += svg_cap_v(5, 15, 2, "100nF")         # timing C: IN_B → GND
    lines += svg_zone_label(16, 1, "VCO")

    # VCO outputs routed to row 2 (empty) with series Rs
    # Triangle (cap voltage at IN_B) — high-Z tap to avoid loading oscillator
    lines += svg_jumper(15, 1, 2, 1, 4)           # IN_B strip → row 2
    lines += svg_resistor_h(2, 1, 3, "100kΩ")     # series R (high-Z buffer)
    lines += svg_track_cut(2, 2)                    # R series isolation
    lines += svg_header_block(2, 4, 5, "△ DB9A:9")

    # Square (OUT_B rail level) — low-Z series for cable drive
    lines += svg_jumper(16, 1, 2, 7, 5)           # OUT_B strip → row 2
    lines += svg_resistor_h(2, 7, 9, "1kΩ")       # series R (anti-ringing)
    lines += svg_track_cut(2, 8)                    # R series isolation
    lines += svg_header_block(2, 10, 11, "□ DB9A:2")

    # Isolate triangle from square on row 2
    lines += svg_track_cut(2, 6)

    lines += svg_zone_label(2, 13, "← VCO out")

    # --- Track cuts for U1 ---
    # DIP center gap: isolate left pins (col 10) from right pins (col 13)
    for r in range(6, 13):
        lines += svg_track_cut(r, 11)
        lines += svg_track_cut(r, 12)
    # Right strip isolation: separate IC right pins from output/input headers
    # Rows 6,8,10,12 right strip has IC pins AND headers — need cuts at col 15
    for r in [6, 8, 10, 12]:
        lines += svg_track_cut(r, 15)
    # Also isolate output headers from right-side input resistors on rows 8, 10
    for r in [8, 10]:
        lines += svg_track_cut(r, 20)
    # Input resistor series cuts — force current through 1kΩ (not copper bypass)
    for r in [8, 10]:
        lines += svg_track_cut(r, 6)    # left-side 1kΩ (legs at 5,9)
        lines += svg_track_cut(r, 22)   # right-side 1kΩ (legs at 21,23)

    # Track cuts for U2
    for r in range(15, 19):
        lines += svg_track_cut(r, 23)
        lines += svg_track_cut(r, 24)

    # --- Pico connection header ---
    lines += svg_header_block(20, 1, 6, "J_PICO (to Pico WH via ribbon)")
    lines += svg_header_block(20, 8, 13, "J_OUT (to DB-9 A)")
    lines += svg_header_block(20, 15, 20, "J_IN (from DB-9 B)")
    lines += svg_header_block(20, 22, 24, "+5V/VSYS")

    # --- Legend ---
    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "DIP IC (in socket)"),
        ("rect", C_RESISTOR, "Resistor"),
        ("rect", C_CAP_CER, "Ceramic capacitor"),
        ("rect", C_CAP_ELEC, "Electrolytic cap"),
        ("x", C_CUT, "Track cut (copper side)"),
        ("line", C_JUMPER[0], "Jumper wire (top side)"),
        ("circle", "#FF4444", "LED"),
        ("circle", "#DDD", "Transistor (2N3904)"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# EXPANDER MODULE LAYOUTS
# ============================================================

def generate_expander_noise():
    """Noise generator module.

    Schematic ref (expander_stripboard.md Module 2):
      Row 1: Power (+12V, GND, -12V) + 100nF decoupling
      Row 2: V+ bias chain: 470k + 470k → Q1 base
      Row 3: Q1 base junction
      Row 4: Q1 emitter → GND (noise source)
      Rows 5-8: TL072 section A (gain = 4.7M/100k = 47×)
      Output: 10kΩ series → OUT jack
    """
    COLS = 12
    ROWS = 10
    lines = svg_start(COLS, ROWS, "Expander Module 2 — White Noise Generator", extra_h=80)
    lines += svg_board(COLS, ROWS)

    # Power rails
    lines += svg_rail(1, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(2, COLS, "GND", C_RAIL_GND)
    lines += svg_rail(3, COLS, "-12V", C_RAIL_N12V)

    # --- Q1 avalanche noise source ---
    # Bias: +12V (row 1) → 470kΩ → junction (row 4) → 470kΩ → GND (row 2)
    # This reverse-biases the B-E junction at ~6V for avalanche
    lines += svg_resistor_v(1, 3, 3, "470kΩ")
    lines += svg_resistor_v(3, 4, 3, "470kΩ")
    # Q1 at the bias junction — only B and E connected, collector lead cut short
    lines += svg_transistor(4, 5, "Q1", cut_collector=True)
    # Emitter to GND
    lines += svg_jumper(4, 5, 2, 5, 2)  # emitter → GND rail

    # Callout: explain why collector is cut
    lines += svg_callout(2, 7, [
        "2N3904: CUT COLLECTOR",
        "LEAD flush to body.",
        "Only B-E junction used",
        "(reverse-biased, ~8V",
        "avalanche noise source).",
    ], color="#CC0000", arrow_to=(4, 5))

    # --- U1 TL072 section A (rows 5-8, cols 5-8) ---
    lines += svg_dip("U1", "TL072", 5, 5, 8, col_span=4,
                     pin_labels_l=["OUT_A", "-IN_A", "+IN_A", "V-"],
                     pin_labels_r=["V+", "OUT_B", "-IN_B", "+IN_B"])

    # Track cuts: DIP halves + isolate V+ from output path
    for r in range(5, 9):
        lines += svg_track_cut(r, 6)   # left DIP gap
        lines += svg_track_cut(r, 7)   # right DIP gap
    lines += svg_track_cut(5, 9)       # isolate V+ (col 8) from output (cols 10+)

    # V+ decoupling: on right strip at col 8 (V+ pin), route to +12V rail
    lines += svg_jumper(5, 8, 1, 8, 1)   # V+ → +12V rail
    # V- decoupling: pin 4 at row 8 col 5 (left strip), route to -12V rail
    lines += svg_jumper(8, 5, 3, 5, 2)   # V- → -12V rail

    # Input: noise from Q1 → 100kΩ → -IN_A (pin 2, row 6, left strip)
    lines += svg_resistor_h(6, 1, 3, "100kΩ")

    # Feedback: 4.7MΩ from OUT_A (pin 1, row 5) → -IN_A (pin 2, row 6)
    # Both on left strip — col 3 bridges rows 5-6 via vertical resistor ✓
    lines += svg_resistor_v(5, 6, 3, "4.7MΩ")

    # +IN_A (pin 3, row 7, left strip) → 100kΩ → GND
    lines += svg_resistor_h(7, 1, 3, "100kΩ")
    lines += svg_jumper(7, 1, 2, 1, 3)   # to GND rail

    # Output: jumper from OUT_A (row 5, left strip) across cuts to right strip
    lines += svg_jumper(5, 4, 5, 10, 0)  # OUT_A → cols 10+ (past V+ isolation cut)
    lines += svg_resistor_h(5, 10, 11, "10kΩ")
    lines += svg_header_block(5, 12, 12, "OUT")

    # Section B unused — tie +IN_B to GND
    lines += svg_jumper(8, 8, 2, 8, 4)   # +IN_B (row 8 right) → GND
    cx, cy = xy(9, 2)
    lines.append(f'<text x="{cx}" y="{cy}" class="note">Sect. B: +IN_B tied to GND</text>')

    # Gain annotation
    cx, cy = xy(10, 2)
    lines.append(f'<text x="{cx}" y="{cy}" class="note" font-size="9">'
                 f'Gain: 4.7MΩ / 100kΩ = 47× → ~5-8Vpp noise</text>')

    # Legend
    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("circle", "#DDD", "2N3904 (avalanche)"),
        ("rect", C_IC, "TL072 (section A)"),
        ("rect", C_RESISTOR, "Resistor"),
        ("x", C_CUT, "Track cut"),
        ("rect", C_CAP_CER, "100nF decoupling"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_expander_lfo():
    """LFO module.

    Schematic ref (expander_stripboard.md Module 3):
      Section A = Integrator: 1µF feedback cap, rate via 1MΩ pot from square out
      Section B = Schmitt trigger: 100kΩ hysteresis divider
      Outputs: Triangle (pin 1), Square (pin 7 via 3.3k+3.3k divider → ±5V)
    """
    COLS = 16
    ROWS = 10
    lines = svg_start(COLS, ROWS, "Expander Module 3 — Triangle/Square LFO", extra_h=80)
    lines += svg_board(COLS, ROWS)

    lines += svg_rail(1, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(2, COLS, "GND", C_RAIL_GND)
    lines += svg_rail(3, COLS, "-12V", C_RAIL_N12V)

    # U1 TL072 (rows 4-7, cols 5-8)
    lines += svg_dip("U1", "TL072", 4, 5, 8, col_span=4,
                     pin_labels_l=["OUT_A", "-IN_A", "+IN_A", "V-"],
                     pin_labels_r=["V+", "OUT_B", "-IN_B", "+IN_B"])

    for r in range(4, 8):
        lines += svg_track_cut(r, 6)
        lines += svg_track_cut(r, 7)

    # Decoupling caps — col 10 (one further right to clear pin labels)
    lines += svg_decoupling(4, 7, 10, COLS)

    # Power jumpers: V+ (pin 8, row 4 right) → +12V, V- (pin 4, row 7 left) → -12V
    lines += svg_jumper(4, 8, 1, 8, 1)   # V+ → +12V rail
    lines += svg_jumper(7, 5, 3, 5, 2)   # V- → -12V rail

    # Section labels — on rows 9-10 below IC to avoid pin label collision
    lines += svg_zone_label(9, 3, "Sect. A = Integrator")
    lines += svg_zone_label(9, 10, "Sect. B = Schmitt trigger")

    # Timing cap: 1µF from OUT_A (pin 1, row 4) → -IN_A (pin 2, row 5)
    # Both on left strip (cols 1-5). Cap at col 3 bridges the two rows. ✓
    lines += svg_cap_v(4, 5, 3, "1µF")

    # Rate pot (panel-mount, 1MΩ): SQR out → pot CW, wiper → -IN_A, CCW → GND
    # Pot pins land on row 8 at cols 1, 2, 3.
    # Pin 1 (CW) = SQR in, Pin 2 (W) = wiper out, Pin 3 (CCW) = GND
    lines += svg_pot(8, 1, "RATE", "1MΩ", pin1_label="SQR", pin2_label="W", pin3_label="GND")
    lines += svg_jumper(5, 8, 8, 1, 5)   # OUT_B (SQR, right strip) → pot pin 1 (CW)
    lines += svg_jumper(8, 2, 5, 4, 4)   # pot wiper → -IN_A (left strip)
    lines += svg_jumper(8, 3, 2, 3, 3)   # pot CCW → GND rail
    cx, _ = xy(8, 5)
    cy = xy(8, 1)[1]
    lines.append(f'<text x="{cx}" y="{cy}" class="note">~0.04–40 Hz</text>')

    # +IN_A (pin 3, row 6, left strip) → 100kΩ → GND
    lines += svg_resistor_h(6, 1, 3, "100kΩ")
    lines += svg_jumper(6, 1, 2, 1, 3)   # to GND rail

    # Hysteresis: OUT_B (row 5 right) → 100kΩ → +IN_B (row 7 right)
    # Both on right strip. Need jumper from OUT_B (row 5) down to row 7.
    lines += svg_jumper(5, 9, 7, 9, 0)   # OUT_B strip → row 7 right strip
    lines += svg_resistor_h(7, 10, 12, "100kΩ")
    # +IN_B → 100kΩ → GND (vertical from GND rail to row 7 right strip)
    lines += svg_resistor_v(2, 7, 14, "100kΩ")

    # Square output voltage divider: OUT_B (row 5 right) → 3.3k+3.3k → ±5V
    lines += svg_jumper(5, 10, 10, 10, 2)  # OUT_B strip → row 10
    lines += svg_resistor_h(10, 10, 12, "3.3kΩ")
    lines += svg_resistor_h(10, 12, 14, "3.3kΩ")

    # Output jacks
    lines += svg_header_block(4, 1, 1, "TRI")    # TRI = OUT_A, left strip ✓
    lines += svg_header_block(10, 15, 16, "SQR")  # SQR = after divider ✓

    # LED indicator: driven from SQR output via jumper to row 8
    lines += svg_jumper(5, 11, 8, 11, 3)  # OUT_B strip → row 8
    lines += svg_resistor_h(8, 12, 14, "1kΩ")
    cx, cy = xy(8, 15)
    lines.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#44FF44" stroke="#22AA22" '
                 f'stroke-width="1" opacity="0.8"/>')
    lines.append(f'<text x="{cx + 10}" y="{cy}" class="comp">LED</text>')

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "TL072 (both sections)"),
        ("circle", "#AAA", "1MΩ Rate pot"),
        ("rect", C_RESISTOR, "Resistor"),
        ("rect", C_CAP_CER, "Capacitor"),
        ("x", C_CUT, "Track cut"),
        ("circle", "#44FF44", "LED"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_expander_clockdiv():
    """Clock divider module.

    Schematic ref (expander_stripboard.md Module 4):
      +5V only (from 78L05 on power distribution board).
      CD40106 conditions input clock (Eurorack 10V → 5V CMOS).
      CD4024 binary counter: /2, /4, /8 outputs with LEDs.
      RST held LOW via 10kΩ, momentary button to +5V for manual reset.
    """
    COLS = 14
    ROWS = 12
    lines = svg_start(COLS, ROWS, "Expander Module 4 — Clock Divider (/2 /4 /8)", extra_h=80)
    lines += svg_board(COLS, ROWS)

    lines += svg_rail(1, COLS, "+5V", C_RAIL_5V)
    lines += svg_rail(2, COLS, "GND", C_RAIL_GND)

    # Decoupling cap
    cx, cy = xy(1, 12)
    lines.append(f'<rect x="{cx + 2}" y="{cy - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx + 7}" y="{cy - 7}" class="comp" font-size="9">100n</text>')

    # --- Input conditioning ---
    lines += svg_zone_label(3, 10, "Input conditioning")
    lines += svg_header_block(3, 1, 1, "CLK IN")
    # Voltage divider: 120kΩ + 100kΩ → ~4.2V from 10V Eurorack
    lines += svg_resistor_h(3, 2, 4, "120kΩ")
    lines += svg_resistor_v(2, 3, 5, "100kΩ")

    # CD40106 Schmitt gate (simplified — 1 gate used, 5 spare)
    x1, y1 = xy(3, 6)
    x2, y2 = xy(4, 8)
    lines.append(f'<rect x="{x1 - 6}" y="{y1 - 8}" width="{x2 - x1 + 16}" height="{y2 - y1 + 16}" '
                 f'fill="{C_IC}" rx="3"/>')
    lines.append(f'<text x="{(x1 + x2) // 2 + 3}" y="{(y1 + y2) // 2 - 5}" '
                 f'class="ic-name" font-size="8">CD40106</text>')
    lines.append(f'<text x="{(x1 + x2) // 2 + 3}" y="{(y1 + y2) // 2 + 7}" '
                 f'class="ic-type" font-size="9">1 gate used</text>')

    # --- CD4024 binary counter (rows 5-11, cols 5-8) ---
    # CD4024 pinout:
    #   Left (col 5):  1=CLK, 2=RST, 3=Q1(/2), 4=Q2(/4), 5=Q3(/8), 6=Q4(/16), 7=VSS
    #   Right (col 8): 14=VDD, 13=nc, 12=Q7(/128), 11=Q6(/64), 10=Q5(/32), 9=nc, 8=nc
    lines += svg_dip("U1", "CD4024", 5, 5, 14, col_span=4,
                     pin_labels_l=["CLK", "RST", "/2", "/4", "/8", "/16", "GND"],
                     pin_labels_r=["VDD", "nc", "/128", "/64", "/32", "nc", "nc"])

    for r in range(5, 12):
        lines += svg_track_cut(r, 6)
        lines += svg_track_cut(r, 7)

    # CLK input: CD40106 output (row 4) → pin 1 CLK (row 5, col 5)
    lines += svg_jumper(4, 7, 5, 4, 0)

    # RST pin (pin 2, row 6 LEFT strip col 5):
    # Need jumper from left strip to right strip for pulldown + button
    lines += svg_jumper(6, 4, 6, 9, 3)     # RST (left) → right strip via jumper
    lines += svg_track_cut(6, 9)            # isolate RST from pin 13 (nc)
    lines += svg_resistor_h(6, 10, 12, "10kΩ")
    lines += svg_jumper(6, 12, 2, 12, 3)   # pull-down to GND rail
    # Reset button (momentary to +5V)
    cx, cy = xy(6, 13)
    lines.append(f'<rect x="{cx - 8}" y="{cy - 6}" width="16" height="12" fill="#CC4444" rx="2"/>')
    lines.append(f'<text x="{cx}" y="{cy + 1}" class="comp" fill="white" font-size="9">RST</text>')
    lines += svg_jumper(6, 14, 1, 14, 4)   # button to +5V

    # VDD (pin 14, row 5, col 8 RIGHT strip) → +5V rail
    lines += svg_jumper(5, 8, 1, 8, 0)
    # GND (pin 7, row 11, col 5 LEFT strip) → GND rail
    lines += svg_jumper(11, 5, 2, 5, 1)

    # Outputs: /2, /4, /8 are pins 3, 4, 5 — LEFT side (col 5)
    # Output jacks on left side. LEDs need jumper from left → right strip.
    for i, (div, r) in enumerate([("/2", 7), ("/4", 8), ("/8", 9)]):
        # Output jack on left strip
        lines += svg_resistor_h(r, 1, 3, "1kΩ")
        lines += svg_header_block(r, 1, 1, "")
        # LED: jumper from left strip across cuts to right strip
        lines += svg_jumper(r, 4, r, 10, i)  # left → right (past cuts + IC pin)
        lines += svg_track_cut(r, 9)          # isolate IC right pin from LED
        lines += svg_resistor_h(r, 10, 12, "1kΩ")
        cx, cy = xy(r, 13)
        lines.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#FFAA00" '
                     f'stroke="#CC8800" stroke-width="1" opacity="0.8"/>')

    # Note about unused outputs
    cx, cy = xy(12, 2)
    lines.append(f'<text x="{cx}" y="{cy}" class="note" font-size="8">'
                 f'/16, /32, /64, /128 available but not wired to jacks</text>')

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "CD4024 (DIP-14)"),
        ("rect", C_IC, "CD40106 (1 gate)"),
        ("rect", "#CC4444", "Reset momentary"),
        ("circle", "#FFAA00", "LED indicator"),
        ("x", C_CUT, "Track cut"),
        ("rect", C_CAP_CER, "100nF decoupling"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_expander_sah():
    """Sample & Hold module.

    Schematic ref (expander_stripboard.md Module 5):
      LF398 dedicated S&H IC. Hold cap MUST be polystyrene/polypropylene.
      Pin 5 (OUT) → Pin 2 (IN-) feedback. Pin 6 (HOLD) → 1nF to GND.
      Pin 8 (L/S) = logic/clock input. Pin 3 (IN+) = signal input via 10kΩ.
    """
    COLS = 12
    ROWS = 9
    lines = svg_start(COLS, ROWS, "Expander Module 5 — Sample &amp; Hold (LF398)", extra_h=80)
    lines += svg_board(COLS, ROWS)

    lines += svg_rail(1, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(2, COLS, "GND", C_RAIL_GND)
    lines += svg_rail(3, COLS, "-12V", C_RAIL_N12V)

    # LF398 (DIP-8, rows 4-7, cols 4-7)
    # Correct pinout:
    #   Row 4: Pin 1 (OFFS)  left=col4,  Pin 8 (L/S)   right=col7
    #   Row 5: Pin 2 (IN-)   left=col4,  Pin 7 (OUT)   right=col7
    #   Row 6: Pin 3 (IN+)   left=col4,  Pin 6 (HOLD)  right=col7
    #   Row 7: Pin 4 (V-)    left=col4,  Pin 5 (V+)    right=col7
    lines += svg_dip("U1", "LF398", 4, 4, 8, col_span=4,
                     pin_labels_l=["OFFS", "IN-", "IN+", "V-"],
                     pin_labels_r=["L/S", "OUT", "HOLD", "V+"])

    for r in range(4, 8):
        lines += svg_track_cut(r, 5)
        lines += svg_track_cut(r, 6)

    # Power jumpers: V+ (pin 5, row 7 right) → +12V, V- (pin 4, row 7 left) → -12V
    lines += svg_jumper(7, 7, 1, 7, 1)   # V+ → +12V rail
    lines += svg_jumper(7, 4, 3, 4, 2)   # V- → -12V rail

    # Decoupling cap near V+ (pin 5, row 7 right)
    cx_vp, cy_vp = xy(7, 9)
    lines.append(f'<rect x="{cx_vp - 5}" y="{cy_vp - 4}" width="10" height="8" fill="{C_CAP_CER}" '
                 f'rx="1" stroke="#333" stroke-width="0.5" opacity="0.8"/>')
    lines.append(f'<text x="{cx_vp}" y="{cy_vp + 12}" class="comp" font-size="8">100n</text>')

    # Feedback: OUT (pin 7, row 5, col 7) → IN- (pin 2, row 5, col 4)
    lines += svg_jumper(5, 7, 5, 4, 0)

    # Hold cap: HOLD (pin 6, row 6, col 7) → 1nF → GND (row 2)
    lines += svg_cap_v(2, 6, 9, "1nF")

    # Signal input: IN+ (pin 3, row 6, col 4) via 10kΩ
    lines += svg_header_block(6, 1, 1, "IN")
    lines += svg_resistor_h(6, 2, 3, "")
    cx_r, cy_r = xy(6, 2)
    lines.append(f'<text x="{(cx_r + xy(6,3)[0])//2}" y="{cy_r + 12}" class="comp" font-size="9">10kΩ</text>')

    # Clock/trigger input: L/S (pin 8, row 4, col 7) — header on right
    lines += svg_header_block(4, 10, 11, "CLK")

    # Output: OUT (pin 7, row 5, col 7) — header on right
    lines += svg_header_block(5, 10, 11, "OUT")

    # Callout for cap type — below board to avoid collision
    lines += svg_callout(8, 5, [
        "POLYSTYRENE ONLY",
        "Ceramic/electrolytic",
        "cause excessive droop.",
    ], color="#CC0000", arrow_to=(6, 9))

    # OFFS pin: leave unconnected or 100kΩ to GND
    cx, cy = xy(9, 2)
    lines.append(f'<text x="{cx}" y="{cy}" class="note" font-size="8">Pin 1 (OFFS): NC or 100kΩ to GND</text>')

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "LF398"),
        ("line", C_JUMPER[0], "Feedback jumper"),
        ("rect", C_CAP_CER, "1nF polystyrene"),
        ("x", C_CUT, "Track cut"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# SLEW LIMITER MODULE
# ============================================================

def generate_expander_slew():
    """Expander Module 6 — Slew Limiter (TL072 + diode steering)."""
    COLS = 16
    ROWS = 10
    lines = svg_start(COLS, ROWS, "Expander Module 6 — Slew Limiter", extra_h=100)
    lines += svg_board(COLS, ROWS)

    # Power rails
    lines += svg_rail(1, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(3, COLS, "-12V", C_RAIL_N12V)
    lines += svg_rail(10, COLS, "GND", C_RAIL_GND)

    # TL072 dual opamp (DIP8) - rows 4-7, cols 4-7
    lines += svg_dip("U1", "TL072", 4, 4, 8, col_span=4,
                     pin_labels_l=["OUT-A", "-IN-A", "+IN-A", "V-"],
                     pin_labels_r=["V+", "+IN-B", "-IN-B", "OUT-B"])

    # Input zone and series resistor (10k)
    lines += svg_zone_label(5, 1, "IN")
    lines += svg_resistor_h(5, 2, 3, "10k")

    # RISE pot path (D1) - rows 4-5
    lines += svg_pot(4, 11, 1, "RISE", "1M log")
    lines += svg_diode_h(4, 9, 10, "D1")

    # FALL pot path (D2) - rows 6-7
    lines += svg_pot(7, 11, 1, "FALL", "1M log")
    lines += svg_diode_h(7, 9, 10, "D2")

    # D1 and D2 connect to input node
    lines += svg_jumper(5, 4, 4, 4, 0)  # Input to D1
    lines += svg_jumper(5, 4, 7, 4, 1)  # Input to D2

    # Pots connect to opamp -in (pin 2)
    lines += svg_jumper(4, 10, 5, 6, 2)  # RISE pot wiper to pin 2
    lines += svg_jumper(7, 10, 5, 6, 3)  # FALL pot wiper to pin 2

    # Timing capacitor (1µF) from output (pin 1) to -in (pin 2)
    lines += svg_cap_h(6, 8, 10, "1µF", C_CAP_ELEC)

    # +IN-A (pin 3) to GND
    lines += svg_jumper(6, 5, 10, 5, 0)

    # Output
    lines += svg_zone_label(6, 15, "OUT")
    lines += svg_jumper(5, 8, 6, 15, 1)

    # Track cuts
    lines += svg_track_cut(5, 6)  # Cut at pin 2
    lines += svg_track_cut(6, 9)  # Cut for cap

    # Annotation
    lines += svg_callout(2, 12, [
        "SLEW LIMITER",
        "Separate rise/fall via",
        "diode steering (D1/D2)",
    ])

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "TL072"),
        ("rect", C_DIODE, "1N4148"),
        ("rect", C_CAP_ELEC, "1µF timing"),
        ("x", C_CUT, "Track cut"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# ATTENUVERTER MODULE
# ============================================================

def generate_expander_attenuverter():
    """Expander Module 7 — Attenuverter (TL072 + center-detent pot)."""
    COLS = 16
    ROWS = 9
    lines = svg_start(COLS, ROWS, "Expander Module 7 — Attenuverter", extra_h=100)
    lines += svg_board(COLS, ROWS)

    # Power rails
    lines += svg_rail(1, COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(3, COLS, "-12V", C_RAIL_N12V)
    lines += svg_rail(9, COLS, "GND", C_RAIL_GND)

    # TL072 (DIP8) - rows 4-7, cols 4-7
    lines += svg_dip("U1", "TL072", 4, 4, 8, col_span=4,
                     pin_labels_l=["OUT", "-IN", "+IN", "V-"],
                     pin_labels_r=["V+", "NC", "NC", "NC"])

    # Input zone and Rin (100k)
    lines += svg_zone_label(5, 1, "IN")
    lines += svg_resistor_h(5, 2, 3, "100k")

    # Center-detent pot (100k)
    lines += svg_pot(5, 11, 1, "ATTEN", "100k center")

    # Pot connections:
    # CCW (left) to input signal (for inverted path)
    lines += svg_jumper(5, 3, 5, 10, 0)  # Rin to pot CCW

    # CW (right) to GND
    lines += svg_jumper(5, 12, 9, 12, 1)

    # Wiper (center) to opamp -in (pin 2)
    lines += svg_jumper(5, 11, 5, 6, 2)

    # Feedback resistor (100k) from output to -in
    lines += svg_resistor_v(4, 8, 6, "100k")
    lines += svg_jumper(4, 8, 5, 8, 3)  # Connect to pin 2

    # +IN (pin 3) to GND
    lines += svg_jumper(6, 5, 9, 5, 0)

    # Output
    lines += svg_zone_label(5, 15, "OUT")
    lines += svg_jumper(5, 8, 5, 15, 1)

    # Track cuts
    lines += svg_track_cut(5, 6)  # At pin 2
    lines += svg_track_cut(5, 11)  # At pot wiper

    # Annotation
    lines += svg_callout(2, 12, [
        "ATTENUVERTER",
        "-1x to +1x via",
        "center-detent pot",
    ])

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC, "TL072"),
        ("rect", C_RESISTOR, "100k (Rin/Rf)"),
        ("x", C_CUT, "Track cut"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# TOUCH TEST BOARD
# ============================================================

def generate_touch_test():
    """Circuit Bend Test Board — 8 body-contact touch channels on stripboard.

    Temporary board for testing touch mods before permanent panel install.
    Each channel: input header → safety R → track cut → touch bolt pad → optional divider R → GND.
    """
    COLS = 10
    ROWS = 10
    lines = svg_start(COLS, ROWS, "Circuit Bend Test Board — 8 Touch Channels", extra_h=100)
    lines += svg_board(COLS, ROWS)

    # Row 1: Power/GND header
    lines += svg_rail(1, COLS, "GND Reference", C_RAIL_GND)
    lines += svg_header_block(1, 1, 2, "GND")

    # Row 10: GND bus
    lines += svg_rail(10, COLS, "GND Bus", C_RAIL_GND)

    # Connect row 1 GND to row 10 GND bus
    lines += svg_jumper(1, 9, 10, 9, 0)

    # Channel names matching the 8 researched touch mods
    channels = [
        ("PITCH", "10kΩ"),
        ("CRUNCH", "4.7kΩ"),
        ("WAH", "22kΩ"),
        ("DISTORT", "15kΩ"),
        ("DECAY", "33kΩ"),
        ("HARMONIC", "10kΩ"),
        ("LFO SPD", "47kΩ"),
        ("FB GATE", "1kΩ"),
    ]

    for row_idx, (name, r_val) in enumerate(channels, start=2):
        # Col 1: Input header pin (clip lead from MicroBrute)
        lines += svg_header_block(row_idx, 1, 1, "IN")

        # Cols 2-4: Safety resistor
        lines += svg_resistor_h(row_idx, 2, 4, r_val)

        # Col 3: Track cut (resistor series isolation)
        lines += svg_track_cut(row_idx, 3)

        # Col 5: Touch bolt pad — gold circle with crosshairs
        cx_t, cy_t = xy(row_idx, 5)
        lines.append(f'<circle cx="{cx_t}" cy="{cy_t}" r="8" fill="#FFD700" '
                     f'stroke="#B8860B" stroke-width="1.5"/>')
        lines.append(f'<text x="{cx_t}" y="{cy_t + 2}" class="comp" '
                     f'font-size="8" font-weight="bold">T</text>')

        # Cols 6-8: Optional second resistor to GND (voltage divider)
        lines += svg_resistor_h(row_idx, 6, 8, "")
        cx_opt = (xy(row_idx, 6)[0] + xy(row_idx, 8)[0]) // 2
        lines.append(f'<text x="{cx_opt}" y="{cy_t + 14}" class="comp" '
                     f'font-size="8" fill="#999">opt divider</text>')

        # Col 7: Track cut (optional R isolation)
        lines += svg_track_cut(row_idx, 7)

        # Col 9: GND bus jumper
        lines += svg_jumper(row_idx, 9, 10, 9, (row_idx - 2) % len(C_JUMPER))

        # Channel label (left margin)
        cx_lbl, cy_lbl = xy(row_idx, 1)
        lines.append(f'<text x="{cx_lbl - 36}" y="{cy_lbl}" class="zone-label" '
                     f'font-size="9">{name}</text>')

    # Legend
    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_RESISTOR, "Safety / divider resistor"),
        ("circle", "#FFD700", "Touch bolt pad (brass M3)"),
        ("x", C_CUT, "Track cut"),
        ("line", C_JUMPER[0], "GND bus jumper"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# MOD STRIPBOARDS — small, focused boards for individual mods
# ============================================================

def generate_mod_m02_soft_sync():
    """M02 — Active soft sync (LM393 comparator).

    Replaces the broken stock soft-sync with a clean comparator-based
    pulse generator. Off-board: SPDT toggle (hard/soft selector) + sync
    input/output jacks. On-board: LM393 with bias network and pull-up.
    """
    COLS = 12
    ROWS = 9
    lines = svg_start(COLS, ROWS, "M02 — Active Soft Sync Stripboard", extra_h=110)
    lines += svg_board(COLS, ROWS)

    # Power rails
    lines += svg_rail(1, COLS, "GND",  C_RAIL_GND)
    lines += svg_rail(2, COLS, "+5V",  C_RAIL_5V)

    # LM393 DIP-8 at rows 4-7, cols 5-8
    lines += svg_dip("U1", "LM393", 4, 5, 8, col_span=4,
                     pin_labels_l=["OUT-A", "-IN-A", "+IN-A", "GND"],
                     pin_labels_r=["VCC", "+IN-B", "-IN-B", "OUT-B"])

    # Track cuts between left/right pins of the DIP
    for r in range(4, 8):
        lines += svg_track_cut(r, 7)

    # Power: VCC pin 8 (row 4 col 8) → +5V rail (row 2 col 8)
    lines += svg_jumper(2, 9, 4, 9, 0)
    # GND pin 4 (row 7 col 5) → GND rail (row 1 col 5)
    lines += svg_jumper(1, 4, 7, 4, 1)

    # Decoupling cap (100n) at VCC corner
    lines += svg_cap_v(2, 4, 10, "100n")

    # Threshold divider: 100k from +5V to pin 2 (-IN-A row 5 col 5)
    #                    100k from pin 2 to GND  → ≈ +2.5V reference
    lines += svg_resistor_v(2, 5, 3, "100k Vref+")
    lines += svg_resistor_v(5, 8, 3, "100k Vref−")
    lines += svg_jumper(5, 3, 5, 4, 2)  # divider midpoint → pin 2

    # AC coupling: SYNC_IN header at col 1, 100nF on row 6 → pin 3 (+IN-A)
    lines += svg_header_block(6, 1, 1, "SYNC")
    lines += svg_cap_h(6, 2, 4, "100n")
    # Track cut to force series cap path
    lines += svg_track_cut(6, 4)
    lines += svg_jumper(6, 4, 6, 5, 3)  # cap output → +IN-A

    # 1N4148 clamp from pin 3 to GND (protects against >5V or <0V sync)
    lines += svg_diode_h(8, 5, 7, "1N4148")
    lines += svg_jumper(6, 5, 8, 5, 4)  # +IN-A → diode anode
    lines += svg_jumper(8, 7, 1, 7, 1)  # diode cathode → GND

    # Pull-up: 10k from OUT-A (pin 1, row 4 col 5) to +5V
    lines += svg_resistor_v(2, 4, 2, "10k pull")
    lines += svg_jumper(4, 2, 4, 5, 5)  # pull-up node → OUT-A

    # SPDT toggle + SYNC_OUT off-board (3-pin header)
    lines += svg_header_block(4, 12, 12, "OUT")
    lines += svg_jumper(4, 5, 4, 12, 5)  # OUT-A → off-board to SPDT pole

    # Off-board indicator
    lines += svg_callout(8, 9, [
        "Off-board:",
        "• SPDT toggle (hard/soft)",
        "• SYNC_OUT → VCO pin",
    ], color="#0066CC", anchor="start")

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC,        "LM393 (DIP-8)"),
        ("rect", C_RESISTOR,  "Resistor"),
        ("rect", C_CAP_CER,   "Ceramic 100nF"),
        ("rect", C_DIODE,     "1N4148 clamp"),
        ("x",    C_CUT,       "Track cut"),
        ("line", C_JUMPER[0], "Jumper wire"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_mod_m04_metalizer_vca():
    """M04 — Metalizer CV depth (LM13700 OTA).

    Inserts an LM13700 OTA into the Metalizer feedback loop so a panel
    CV can modulate fold intensity. Most invasive of the new mods —
    requires cutting the existing Metalizer feedback trace.
    """
    COLS = 14
    ROWS = 12
    lines = svg_start(COLS, ROWS, "M04 — Metalizer VCA Stripboard", extra_h=110)
    lines += svg_board(COLS, ROWS)

    # Power rails (need ±12V for the LM13700)
    lines += svg_rail(1,  COLS, "+12V", C_RAIL_12V)
    lines += svg_rail(2,  COLS, "−12V", C_RAIL_N12V)
    lines += svg_rail(12, COLS, "GND",  C_RAIL_GND)

    # LM13700 DIP-16 at rows 4-11, cols 5-8
    lines += svg_dip("U1", "LM13700", 4, 5, 16, col_span=4,
                     pin_labels_l=["OUT-A", "DB-A", "−IN-A", "+IN-A",
                                   "Iabc-A", "V−", "BufIn-A", "BufOut-A"],
                     pin_labels_r=["BufOut-B", "BufIn-B", "V+", "Iabc-B",
                                   "+IN-B", "−IN-B", "DB-B", "OUT-B"])

    # Track cuts between left/right pins
    for r in range(4, 12):
        lines += svg_track_cut(r, 7)

    # Power: V+ (pin 11, row 6 right) → +12V; V- (pin 6, row 9 left) → −12V
    lines += svg_jumper(1, 9, 6, 9, 0)   # +12V → V+
    lines += svg_jumper(2, 4, 9, 4, 1)   # −12V → V-

    # Decoupling caps near power pins
    lines += svg_cap_v(1, 4, 10, "100n V+")
    lines += svg_cap_v(2, 5, 10, "100n V-")

    # Signal IN (Metalizer feedback tap) → 100k → pin 3 (-IN-A row 6 left col 5)
    lines += svg_header_block(6, 1, 1, "FB-IN")
    lines += svg_resistor_h(6, 2, 4, "100k")

    # +IN-A (pin 4, row 7 col 5) → GND reference
    lines += svg_jumper(7, 5, 12, 5, 2)

    # Iabc-A (pin 5, row 8 col 5) ← 10kΩ ← CV+pot mixing node
    lines += svg_resistor_h(8, 2, 4, "10k")
    lines += svg_jumper(8, 4, 8, 5, 3)

    # Pot (Amount) off-board, 3-pin header at row 8 col 11..13
    lines += svg_pot(8, 11, "Amount", "100k", pin1_label="GND", pin2_label="W", pin3_label="+12V")
    lines += svg_jumper(8, 12, 8, 8, 4)   # pot wiper → through-track to Iabc network

    # CV input jack header
    lines += svg_header_block(10, 1, 1, "CV-IN")
    lines += svg_resistor_h(10, 2, 4, "100k")
    lines += svg_jumper(10, 4, 8, 4, 5)   # CV summing node

    # Output: OUT-A (pin 1, row 4 col 5) → off-board back to Metalizer return
    lines += svg_jumper(4, 5, 4, 14, 5)
    lines += svg_header_block(4, 14, 14, "FB-OUT")

    lines += svg_callout(11, 9, [
        "Cut Metalizer fb trace,",
        "splice in FB-IN / FB-OUT",
        "around the wavefolder.",
    ], color="#CC0000", anchor="start")

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC,        "LM13700 (DIP-16)"),
        ("rect", C_RESISTOR,  "Resistor"),
        ("rect", C_CAP_CER,   "Ceramic 100nF"),
        ("circle", "#C0C0C0", "Panel pot (off-board)"),
        ("x",    C_CUT,       "Track cut"),
        ("line", C_JUMPER[0], "Jumper wire"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_mod_m08_subharmonic():
    """M08 — Sub-harmonic divider (74HC74 D flip-flop /2).

    Square wave → CD40106 buffer (existing breakout) → 74HC74 clock →
    Q output is /2. AC-coupled and pot-mixed back into VCF input.
    """
    COLS = 13
    ROWS = 10
    lines = svg_start(COLS, ROWS, "M08 — Sub-Harmonic Divider Stripboard", extra_h=110)
    lines += svg_board(COLS, ROWS)

    lines += svg_rail(1, COLS, "+5V", C_RAIL_5V)
    lines += svg_rail(2, COLS, "GND", C_RAIL_GND)

    # 74HC74 DIP-14 at rows 3-9, cols 5-8
    lines += svg_dip("U1", "74HC74", 3, 5, 14, col_span=4,
                     pin_labels_l=["1CLR", "1D", "1CLK", "1PRE", "1Q", "1Q'", "GND"],
                     pin_labels_r=["VCC", "2CLR", "2D", "2CLK", "2PRE", "2Q", "2Q'"])

    for r in range(3, 10):
        lines += svg_track_cut(r, 7)

    # Power: VCC (pin 14, row 3 right col 8) → +5V; GND (pin 7, row 9 left col 5) → GND rail
    lines += svg_jumper(1, 9, 3, 9, 0)    # +5V → VCC
    lines += svg_jumper(2, 4, 9, 4, 1)    # GND  → pin 7

    # Decoupling
    lines += svg_cap_v(1, 3, 10, "100n V+")

    # Tie unused 2nd flip-flop pins safely (PRE/CLR high, D to GND)
    lines += svg_jumper(1, 11, 7, 8, 2)   # 2PRE (pin 10) → +5V
    lines += svg_jumper(1, 12, 4, 8, 3)   # 2CLR (pin 13) → +5V
    # Active section: tie 1PRE & 1CLR HIGH so flip-flop runs free
    lines += svg_jumper(1, 6, 6, 5, 4)    # 1PRE (pin 4) → +5V
    lines += svg_jumper(1, 5, 3, 5, 5)    # 1CLR (pin 1) → +5V
    # /2 mode: D (pin 2) ← Q' (pin 6)
    lines += svg_jumper(4, 5, 8, 5, 0)

    # CLK input: SQ_IN at col 1, AC-couple via 100n, into 1CLK (pin 3, row 5 col 5)
    lines += svg_header_block(5, 1, 1, "SQ-IN")
    lines += svg_cap_h(5, 2, 4, "100n")
    lines += svg_track_cut(5, 4)
    lines += svg_jumper(5, 4, 5, 5, 1)

    # Output: 1Q (pin 5, row 7 col 5) → 1µF AC couple → mix pot
    lines += svg_jumper(7, 5, 7, 9, 2)
    lines += svg_cap_h(7, 9, 11, "1µF", electrolytic=True)

    # Mix pot (off-board) at row 7 col 11..13
    lines += svg_pot(7, 11, "Sub Mix", "10k log", pin1_label="GND", pin2_label="W→VCF", pin3_label="OUT")

    # SPDT enable header at row 9 col 11..13 — interrupts pot wiper to mixer
    lines += svg_header_block(9, 11, 13, "SPDT")
    lines += svg_callout(10, 11, [
        "SPDT in series",
        "with wiper → mixer",
    ], color="#0066CC", anchor="start")

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC,        "74HC74 (DIP-14)"),
        ("rect", C_CAP_CER,   "Ceramic 100nF"),
        ("rect", C_CAP_ELEC,  "Electro 1µF"),
        ("circle", "#C0C0C0", "Panel pot (off-board)"),
        ("x",    C_CUT,       "Track cut"),
        ("line", C_JUMPER[0], "Jumper wire"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


def generate_mod_m12_arg():
    """M12 — ARG audio-rate gate (LM393 zero-crossing → gate).

    Audio in → DC-block → comparator with panel-set threshold →
    open-collector gate out (with pull-up).
    """
    COLS = 12
    ROWS = 9
    lines = svg_start(COLS, ROWS, "M12 — ARG Audio-Rate Gate Stripboard", extra_h=110)
    lines += svg_board(COLS, ROWS)

    lines += svg_rail(1, COLS, "GND", C_RAIL_GND)
    lines += svg_rail(2, COLS, "+5V", C_RAIL_5V)

    # LM393 DIP-8 at rows 4-7, cols 5-8
    lines += svg_dip("U1", "LM393", 4, 5, 8, col_span=4,
                     pin_labels_l=["OUT-A", "-IN-A", "+IN-A", "GND"],
                     pin_labels_r=["VCC", "+IN-B", "-IN-B", "OUT-B"])
    for r in range(4, 8):
        lines += svg_track_cut(r, 7)

    # Power
    lines += svg_jumper(2, 9, 4, 9, 0)    # +5V → VCC (pin 8, row 4 col 8)
    lines += svg_jumper(1, 4, 7, 4, 1)    # GND → pin 4 (row 7 col 5)
    lines += svg_cap_v(2, 4, 10, "100n V+")

    # Audio in (col 1) → DC-block 100n → +IN-A (pin 3, row 6 col 5)
    lines += svg_header_block(6, 1, 1, "AUDIO")
    lines += svg_cap_h(6, 2, 4, "100n")
    lines += svg_track_cut(6, 4)
    lines += svg_jumper(6, 4, 6, 5, 2)

    # Threshold via panel pot (100k) → -IN-A (pin 2, row 5 col 5)
    lines += svg_pot(5, 11, "Thresh", "100k", pin1_label="+5V", pin2_label="W", pin3_label="GND")
    lines += svg_jumper(5, 12, 5, 8, 3)
    lines += svg_jumper(5, 8, 5, 5, 4)    # wiper → -IN-A

    # Pull-up 10k on OUT-A (open collector)
    lines += svg_resistor_v(2, 4, 2, "10k pull")
    lines += svg_jumper(4, 2, 4, 5, 5)

    # Gate output header
    lines += svg_header_block(4, 12, 12, "GATE")
    lines += svg_jumper(4, 5, 4, 12, 5)

    lines += svg_callout(8, 9, [
        "Off-board:",
        "• Panel pot (Threshold)",
        "• 6mm audio jack → AUDIO",
        "• GATE → env-retrig / aux",
    ], color="#0066CC", anchor="start")

    legend_y = MARGIN_T + ROWS * CELL + PAD + 10
    lines += svg_legend(legend_y, [
        ("rect", C_IC,        "LM393 (DIP-8)"),
        ("rect", C_RESISTOR,  "Resistor"),
        ("rect", C_CAP_CER,   "Ceramic 100nF"),
        ("circle", "#C0C0C0", "Panel pot (off-board)"),
        ("x",    C_CUT,       "Track cut"),
        ("line", C_JUMPER[0], "Jumper wire"),
    ], COLS)

    lines.append('</svg>')
    return '\n'.join(lines)


# ============================================================
# Main
# ============================================================

def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schematics")
    os.makedirs(out_dir, exist_ok=True)

    layouts = {
        "breakout_layout.svg": generate_breakout,
        "expander_noise.svg": generate_expander_noise,
        "expander_lfo.svg": generate_expander_lfo,
        "expander_clockdiv.svg": generate_expander_clockdiv,
        "expander_sah.svg": generate_expander_sah,
        "expander_slew.svg": generate_expander_slew,
        "expander_attenuverter.svg": generate_expander_attenuverter,
        "touch_test_board.svg": generate_touch_test,
        "mod_m02_soft_sync_stripboard.svg":     generate_mod_m02_soft_sync,
        "mod_m04_metalizer_vca_stripboard.svg": generate_mod_m04_metalizer_vca,
        "mod_m08_subharmonic_stripboard.svg":   generate_mod_m08_subharmonic,
        "mod_m12_arg_stripboard.svg":           generate_mod_m12_arg,
    }

    for filename, generator in layouts.items():
        path = os.path.join(out_dir, filename)
        svg = generator()
        with open(path, 'w') as f:
            f.write(svg)
        print(f"  Generated: schematics/{filename}")

    print(f"\nDone — {len(layouts)} SVG files generated.")
    print("View in browser: open schematics/breakout_layout.svg")


if __name__ == "__main__":
    main()
