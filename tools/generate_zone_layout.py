#!/usr/bin/env python3
"""Generate Zone Layout SVG for MACROBRUTE stripboard."""

import os


def generate_zone_layout() -> str:
    """Generate SVG zone layout diagram."""
    
    width = 900
    height = 700
    
    # SVG Header
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
  <filter id="textshadow" x="-20%" y="-20%" width="140%" height="140%">
    <feFlood flood-color="white" flood-opacity="0.9" result="bg"/>
    <feMorphology in="SourceGraphic" operator="dilate" radius="1.5" result="dilated"/>
    <feComposite in="bg" in2="dilated" operator="in" result="shadow"/>
    <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .title {{ font: bold 16px "SF Mono", Consolas, monospace; fill: #1a1a1a; filter: url(#textshadow); }}
    .subtitle {{ font: 11px "SF Mono", Consolas, monospace; fill: #555; filter: url(#textshadow); }}
    .label {{ font: bold 10px "SF Mono", Consolas, monospace; fill: #1a1a1a; filter: url(#textshadow); }}
    .value {{ font: 9px "SF Mono", Consolas, monospace; fill: #555; filter: url(#textshadow); }}
    .zone-label {{ font: bold 9px "SF Mono", Consolas, monospace; fill: #FFF; text-anchor: middle; }}
    .track {{ stroke: #B87333; stroke-width: 2; }}
    .hole {{ fill: #E0E0E0; stroke: #999; stroke-width: 0.5; }}
    .ic-body {{ fill: #333; stroke: #1a1a1a; stroke-width: 2; }}
    .ic-label {{ font: bold 8px "SF Mono", Consolas, monospace; fill: #FFF; text-anchor: middle; }}
    .resistor {{ stroke: #CD853F; stroke-width: 3; }}
    .capacitor {{ stroke: #4682B4; stroke-width: 2; }}
    .connector {{ fill: #2F4F4F; stroke: #1a1a1a; stroke-width: 2; }}
  </style>
</defs>
<rect width="{width}" height="{height}" fill="#F5F5DC"/>
<text x="{width//2}" y="25" class="title" text-anchor="middle">MACROBRUTE Breakout Board — Zone Layout</text>
<text x="{width//2}" y="45" class="subtitle" text-anchor="middle">90 × 50mm Stripboard (Component Side View)</text>
'''
    
    # Board dimensions
    board_x = 100
    board_y = 70
    board_w = 700
    board_h = 500
    
    # Draw board outline
    svg += f'<rect x="{board_x}" y="{board_y}" width="{board_w}" height="{board_h}" fill="#F5DEB3" stroke="#8B4513" stroke-width="3" rx="5"/>\n'
    
    # Grid parameters
    rows = 20
    cols = 35
    cell_w = board_w / cols
    cell_h = board_h / rows
    
    # Draw tracks (horizontal copper strips)
    for row in range(rows):
        y = board_y + row * cell_h + cell_h/2
        # +12V rails (rows 3-4)
        if row == 2 or row == 3:
            svg += f'<line x1="{board_x}" y1="{y}" x2="{board_x+board_w}" y2="{y}" stroke="#D44" stroke-width="3"/>\n'
        # -12V rails (rows 4-5)
        elif row == 4 or row == 5:
            svg += f'<line x1="{board_x}" y1="{y}" x2="{board_x+board_w}" y2="{y}" stroke="#44D" stroke-width="3"/>\n'
        # GND rail (row 5)
        elif row == 6:
            svg += f'<line x1="{board_x}" y1="{y}" x2="{board_x+board_w}" y2="{y}" stroke="#666" stroke-width="3" stroke-dasharray="5,3"/>\n'
        else:
            svg += f'<line x1="{board_x}" y1="{y}" x2="{board_x+board_w}" y2="{y}" class="track"/>\n'
    
    # Draw holes
    for row in range(rows):
        for col in range(cols):
            x = board_x + col * cell_w + cell_w/2
            y = board_y + row * cell_h + cell_h/2
            svg += f'<circle cx="{x}" cy="{y}" r="3" class="hole"/>\n'
    
    # Draw ICs
    # U1 - TL074 (rows 6-12, cols 5-8)
    u1_x = board_x + 5 * cell_w
    u1_y = board_y + 5 * cell_h
    u1_w = 4 * cell_w
    u1_h = 7 * cell_h
    svg += f'<rect x="{u1_x}" y="{u1_y}" width="{u1_w}" height="{u1_h}" class="ic-body" rx="3"/>\n'
    svg += f'<text x="{u1_x+u1_w/2}" y="{u1_y+u1_h/2}" class="ic-label">TL074</text>\n'
    svg += f'<text x="{u1_x+u1_w/2}" y="{u1_y+u1_h/2+12}" class="ic-label" font-size="7">4ch Buffer</text>\n'
    # Pin 1 dot
    svg += f'<circle cx="{u1_x+8}" cy="{u1_y+8}" r="4" fill="gold"/>\n'
    
    # U2 - TL072 (rows 6-9, cols 18-21)
    u2_x = board_x + 17 * cell_w
    u2_y = board_y + 5 * cell_h
    u2_w = 4 * cell_w
    u2_h = 4 * cell_h
    svg += f'<rect x="{u2_x}" y="{u2_y}" width="{u2_w}" height="{u2_h}" class="ic-body" rx="3"/>\n'
    svg += f'<text x="{u2_x+u2_w/2}" y="{u2_y+u2_h/2}" class="ic-label">TL072</text>\n'
    svg += f'<text x="{u2_x+u2_w/2}" y="{u2_y+u2_h/2+12}" class="ic-label" font-size="7">Env/LFO/Tri</text>\n'
    svg += f'<circle cx="{u2_x+8}" cy="{u2_y+8}" r="4" fill="gold"/>\n'
    
    # U3 - CD40106 (rows 13-19, cols 5-8)
    u3_x = board_x + 5 * cell_w
    u3_y = board_y + 12 * cell_h
    u3_w = 4 * cell_w
    u3_h = 7 * cell_h
    svg += f'<rect x="{u3_x}" y="{u3_y}" width="{u3_w}" height="{u3_h}" class="ic-body" rx="3"/>\n'
    svg += f'<text x="{u3_x+u3_w/2}" y="{u3_y+u3_h/2}" class="ic-label">CD40106</text>\n'
    svg += f'<text x="{u3_x+u3_w/2}" y="{u3_y+u3_h/2+12}" class="ic-label" font-size="7">Gate Buffer</text>\n'
    svg += f'<circle cx="{u3_x+8}" cy="{u3_y+8}" r="4" fill="gold"/>\n'
    
    # LED Drivers (rows 13-15, cols 15-20)
    for i, label in enumerate(["R", "G", "B"]):
        led_y = board_y + (13 + i) * cell_h + cell_h/2
        svg += f'<rect x="{board_x+15*cell_w}" y="{led_y-8}" width="{3*cell_w}" height="16" fill="#8B4513" stroke="#5D4E37" stroke-width="1" rx="2"/>\n'
        svg += f'<text x="{board_x+16.5*cell_w}" y="{led_y+3}" class="zone-label" font-size="7">LED {label}</text>\n'
    
    # Connectors (bottom row 20)
    # Power input
    svg += f'<rect x="{board_x+2*cell_w}" y="{board_y+19*cell_w}" width="{6*cell_w}" height="{cell_h-5}" class="connector" rx="3"/>\n'
    svg += f'<text x="{board_x+5*cell_w}" y="{board_y+19.7*cell_h}" class="zone-label" font-size="8">J_PWR (Power)</text>\n'
    
    # DB-9 A Output
    svg += f'<rect x="{board_x+12*cell_w}" y="{board_y+19*cell_w}" width="{8*cell_w}" height="{cell_h-5}" class="connector" rx="3"/>\n'
    svg += f'<text x="{board_x+16*cell_w}" y="{board_y+19.7*cell_h}" class="zone-label" font-size="8">DB-9 A (Outputs)</text>\n'
    
    # DB-9 B Input
    svg += f'<rect x="{board_x+22*cell_w}" y="{board_y+19*cell_w}" width="{8*cell_w}" height="{cell_h-5}" class="connector" rx="3"/>\n'
    svg += f'<text x="{board_x+26*cell_w}" y="{board_y+19.7*cell_h}" class="zone-label" font-size="8">DB-9 B (Inputs)</text>\n'
    
    # Pico header
    svg += f'<rect x="{board_x+31*cell_w}" y="{board_y+15*cell_w}" width="{3*cell_w}" height="{5*cell_h}" class="connector" rx="3"/>\n'
    svg += f'<text x="{board_x+32.5*cell_w}" y="{board_y+17.5*cell_h}" class="zone-label" font-size="7" transform="rotate(-90, {board_x+32.5*cell_w}, {board_y+17.5*cell_h})">Pico</text>\n'
    
    # Row labels (left side)
    row_labels = [
        ("1-2", "Power Input"),
        ("3", "+12V Rail"),
        ("4", "-12V Rail"),
        ("5-6", "GND Rail"),
        ("6-12", "Buffers (U1)"),
        ("13-19", "Gate + LEDs (U3)"),
        ("20", "Connectors"),
    ]
    
    for row_num, label in row_labels:
        y_pos = board_y + 20 + (row_labels.index((row_num, label)) * 60)
        svg += f'<text x="{board_x-10}" y="{y_pos}" class="value" text-anchor="end" font-size="8">{label}</text>\n'
    
    # Legend
    legend_y = height - 100
    svg += f'<rect x="50" y="{legend_y}" width="800" height="90" fill="#FFF" stroke="#999" stroke-width="1" rx="4"/>\n'
    svg += f'<text x="450" y="{legend_y+20}" class="label" text-anchor="middle">Zone Legend</text>\n'
    
    legend_items = [
        ("#B87333", "Copper Track"),
        ("#D44", "+12V Power Rail"),
        ("#44D", "-12V Power Rail"),
        ("#666", "GND Rail (Dashed)"),
        ("#333", "DIP IC"),
        ("#2F4F4F", "Connector"),
    ]
    
    for i, (color, label) in enumerate(legend_items):
        x = 70 + (i % 3) * 250
        y = legend_y + 40 + (i // 3) * 22
        svg += f'<rect x="{x}" y="{y-8}" width="20" height="14" fill="{color}" stroke="#333" stroke-width="0.5" rx="2"/>\n'
        svg += f'<text x="{x+28}" y="{y+3}" class="value" font-size="9">{label}</text>\n'
    
    svg += '</svg>'
    return svg


def main():
    """Generate zone layout SVG."""
    output_dir = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    filepath = os.path.join(output_dir, "zone_layout_stripboard.svg")
    
    try:
        svg_content = generate_zone_layout()
        with open(filepath, 'w') as f:
            f.write(svg_content)
        print(f"Generated: zone_layout_stripboard.svg")
    except Exception as e:
        print(f"Failed: {e}")


if __name__ == "__main__":
    main()
