#!/usr/bin/env python3
"""Generate SVG circuit schematics for MACROBRUTE.

Produces traditional electronic schematics with:
- Standard component symbols (resistors, caps, op-amps, transistors)
- Connection lines and junction dots
- Labels and values
- Consistent styling with stripboard layouts

Usage: python3 tools/generate_schematics.py
Output: schematics/*_schematic.svg
"""

import os
from html import escape as _esc

# Colors (matching stripboard style)
C_BG = "#F5F5F0"
C_BOARD = "#E8D5A3"
C_TEXT = "#222"
C_TEXT_LIGHT = "#555"
C_WIRE = "#0066CC"
C_COMPONENT = "#333"
C_RESISTOR = "#C4A265"
C_CAP_CER = "#4A90D9"
C_CAP_ELEC = "#8B4513"
C_IC = "#2D2D2D"
C_GROUND = "#4A4"
C_POWER = "#D44"
C_DOT = "#0066CC"


def svg_start(w, h, title, subtitle=None):
    """Start SVG document with standard header."""
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '<defs>',
        '  <style>',
        '    text { font-family: "SF Mono", Consolas, "Liberation Mono", monospace; }',
        '    .title { font-size: 16px; font-weight: bold; fill: #222; }',
        '    .subtitle { font-size: 11px; fill: #555; }',
        '    .label { font-size: 10px; fill: #333; font-weight: bold; }',
        '    .value { font-size: 9px; fill: #555; }',
        '    .pin { font-size: 8px; fill: #666; }',
        '    .wire { stroke: #0066CC; stroke-width: 2; fill: none; }',
        '    .component { stroke: #333; stroke-width: 1.5; fill: none; }',
        '    .filled { fill: #333; }',
        '    .junction { fill: #0066CC; }',
        '    .ground { stroke: #4A4; stroke-width: 2; }',
        '    .power { stroke: #D44; stroke-width: 2; }',
        '  </style>',
        '</defs>',
        f'<rect width="{w}" height="{h}" fill="#F5F5F0"/>',
        f'<text x="{w//2}" y="20" class="title" text-anchor="middle">{title}</text>',
    ]
    if subtitle:
        lines.append(f'<text x="{w//2}" y="36" class="subtitle" text-anchor="middle">{subtitle}</text>')
    return lines


def svg_end():
    return ['</svg>']


def wire(x1, y1, x2, y2):
    """Draw a wire connection."""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="wire"/>'


def junction(x, y, r=4):
    """Draw a junction dot."""
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="junction"/>'


def ground(x, y, size=15):
    """Draw ground symbol."""
    lines = [
        f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+size}" class="ground"/>',
        f'<line x1="{x-size}" y1="{y+size}" x2="{x+size}" y2="{y+size}" class="ground"/>',
        f'<line x1="{x-size*0.7}" y1="{y+size+5}" x2="{x+size*0.7}" y2="{y+size+5}" class="ground"/>',
    ]
    return '\n'.join(lines)


def resistor(x, y, label=None, value=None, vertical=True):
    """Draw resistor (zigzag)."""
    w, h = 40, 12
    if vertical:
        # Vertical resistor
        zig = []
        for i in range(5):
            zig.append(f"L{x+(-h/2 if i%2==0 else h/2)},{y-15+i*7.5}")
        path = f'M{x},{y-20} {" ".join(zig)} L{x},{y+20}'
    else:
        # Horizontal resistor
        zig = []
        for i in range(5):
            zig.append(f"L{x-15+i*7.5},{y+(-h/2 if i%2==0 else h/2)}")
        path = f'M{x-20},{y} {" ".join(zig)} L{x+20},{y}'
    
    result = [f'<path d="{path}" class="component"/>']
    if label:
        lx, ly = (x, y-28) if vertical else (x, y-15)
        result.append(f'<text x="{lx}" y="{ly}" class="label" text-anchor="middle">{label}</text>')
    if value:
        lx, ly = (x, y+35) if vertical else (x, y+20)
        result.append(f'<text x="{lx}" y="{ly}" class="value" text-anchor="middle">{value}</text>')
    return '\n'.join(result)


def capacitor(x, y, label=None, value=None, polarized=False, vertical=True):
    """Draw capacitor (two parallel lines)."""
    if vertical:
        # Vertical capacitor
        lines = [
            wire(x, y-20, x, y-5),
            wire(x, y+5, x, y+20),
            f'<line x1="{x-10}" y1="{y-5}" x2="{x+10}" y2="{y-5}" class="component" stroke-width="2"/>',
            f'<line x1="{x-10}" y1="{y+5}" x2="{x+10}" y2="{y+5}" class="component" stroke-width="2"/>',
        ]
        if polarized:
            lines.append(f'<text x="{x-15}" y="{y-8}" class="value" fill="#D44">+</text>')
    else:
        # Horizontal capacitor
        lines = [
            wire(x-20, y, x-5, y),
            wire(x+5, y, x+20, y),
            f'<line x1="{x-5}" y1="{y-10}" x2="{x-5}" y2="{y+10}" class="component" stroke-width="2"/>',
            f'<line x1="{x+5}" y1="{y-10}" x2="{x+5}" y2="{y+10}" class="component" stroke-width="2"/>',
        ]
        if polarized:
            lines.append(f'<text x="{x-8}" y="{y-15}" class="value" fill="#D44">+</text>')
    
    if label:
        lx, ly = (x+18, y-8) if vertical else (x, y-20)
        lines.append(f'<text x="{lx}" y="{ly}" class="label" text-anchor="left">{label}</text>')
    if value:
        lx, ly = (x+18, y+5) if vertical else (x, y+25)
        lines.append(f'<text x="{lx}" y="{ly}" class="value" text-anchor="left">{value}</text>')
    return '\n'.join(lines)


def opamp(x, y, label="TL072", pins=None):
    """Draw op-amp triangle symbol."""
    size = 30
    result = [
        # Triangle
        f'<polygon points="{x-size},{y-size} {x-size},{y+size} {x+size},{y}" class="component"/>',
        f'<text x="{x}" y="{y}" class="label" text-anchor="middle" dominant-baseline="central">{label}</text>',
        # Input pins
        f'<text x="{x-size-3}" y="{y-15}" class="pin" text-anchor="end">-</text>',
        f'<text x="{x-size-3}" y="{y+15}" class="pin" text-anchor="end">+</text>',
    ]
    if pins:
        result.extend([
            f'<text x="{x-size-15}" y="{y-15}" class="value" text-anchor="end">{pins[0]}</text>',
            f'<text x="{x-size-15}" y="{y+15}" class="value" text-anchor="end">{pins[1]}</text>',
            f'<text x="{x+size+5}" y="{y}" class="value" text-anchor="start">{pins[2]}</text>',
        ])
    return '\n'.join(result)


def transistor_npn(x, y, label="2N3904"):
    """Draw NPN transistor symbol."""
    result = [
        # Circle
        f'<circle cx="{x}" cy="{y}" r="20" class="component"/>',
        # Base line
        f'<line x1="{x-20}" y1="{y}" x2="{x}" y2="{y}" class="component"/>',
        # Collector (top)
        f'<line x1="{x}" y1="{y}" x2="{x+12}" y2="{y-15}" class="component"/>',
        wire(x+12, y-15, x+15, y-25),
        # Emitter (bottom) with arrow
        f'<line x1="{x}" y1="{y}" x2="{x+12}" y2="{y+12}" class="component"/>',
        f'<polygon points="{x+12},{y+12} {x+16},{y+6} {x+8},{y+8}" class="filled"/>',
        wire(x+12, y+12, x+15, y+25),
        # Labels
        f'<text x="{x-25}" y="{y}" class="value" text-anchor="end">B</text>',
        f'<text x="{x+20}" y="{y-25}" class="value" text-anchor="start">C</text>',
        f'<text x="{x+20}" y="{y+25}" class="value" text-anchor="start">E</text>',
    ]
    if label:
        result.append(f'<text x="{x}" y="{y+35}" class="label" text-anchor="middle">{label}</text>')
    return '\n'.join(result)


def jack(x, y, label=None):
    """Draw audio jack symbol."""
    result = [
        f'<circle cx="{x}" cy="{y}" r="8" class="component"/>',
        f'<line x1="{x}" y1="{y}" x2="{x+20}" y2="{y}" class="component"/>',
    ]
    if label:
        result.append(f'<text x="{x}" y="{y+20}" class="label" text-anchor="middle">{label}</text>')
    return '\n'.join(result)


def potentiometer(x, y, label=None, value=None):
    """Draw potentiometer (resistor with arrow)."""
    result = [
        # Resistor zigzag
        f'<path d="M{x-20},{y} L{x-15},{y-8} L{x-7},{y+8} L{x},{y-8} L{x+7},{y+8} L{x+15},{y-8} L{x+20},{y}" class="component"/>',
        # Arrow from top
        wire(x, y-30, x, y-8),
        f'<polygon points="{x},{y-8} {x-4},{y-16} {x+4},{y-16}" class="filled"/>',
    ]
    if label:
        result.append(f'<text x="{x}" y="{y-35}" class="label" text-anchor="middle">{label}</text>')
    if value:
        result.append(f'<text x="{x}" y="{y+18}" class="value" text-anchor="middle">{value}</text>')
    return '\n'.join(result)


def generate_noise_schematic():
    """Generate white noise generator schematic."""
    w, h = 500, 400
    lines = svg_start(w, h, "White Noise Generator — Schematic", "2N3904 avalanche breakdown + TL072 amplifier")
    
    # Power rail at top
    lines.append(wire(100, 60, 400, 60))
    lines.append(f'<text x="250" y="55" class="label" text-anchor="middle" fill="#D44">+12V</text>')
    
    # 2N3904 transistor noise source
    lines.append(transistor_npn(150, 150))
    lines.append(wire(150, 60, 150, 125))  # Base bias from +12V
    lines.append(resistor(130, 90, label="470k", vertical=False))
    lines.append(resistor(170, 90, label="470k", vertical=False))
    
    # Emitter to ground via cap
    lines.append(wire(165, 175, 165, 250))
    lines.append(capacitor(165, 250, value="100pF", vertical=True))
    lines.append(wire(165, 270, 165, 290))
    lines.append(ground(165, 290))
    
    # TL072 amplifier
    lines.append(opamp(300, 200, "TL072", pins=["2(-)", "3(+)", "1(out)"]))
    
    # Input from transistor
    lines.append(wire(165, 150, 250, 150))  # Emitter to opamp area
    lines.append(wire(250, 150, 250, 185))  # Down to -in
    lines.append(wire(250, 185, 270, 185))  # Into -in
    
    # Feedback resistor
    lines.append(wire(330, 200, 360, 200))  # Output
    lines.append(wire(360, 200, 360, 130))  # Up
    lines.append(wire(360, 130, 230, 130))  # Across
    lines.append(wire(230, 130, 230, 185))  # Down to -in
    lines.append(resistor(295, 130, label="4.7M", value="feedback", vertical=False))
    
    # +in to ground
    lines.append(wire(250, 215, 250, 290))
    lines.append(resistor(250, 260, label="100k", vertical=True))
    lines.append(ground(250, 290))
    
    # Output to jack
    lines.append(wire(360, 200, 420, 200))
    lines.append(jack(440, 200, label="NOISE"))
    
    lines.extend(svg_end())
    return '\n'.join(lines)


def generate_lfo_schematic():
    """Generate LFO schematic (integrator + Schmitt trigger)."""
    w, h = 600, 450
    lines = svg_start(w, h, "Triangle/Square LFO — Schematic", "TL072 integrator + Schmitt trigger")
    
    # First opamp - Integrator
    lines.append(opamp(150, 150, "A", pins=["2(-)", "3(+)", "1(out)"]))
    
    # Second opamp - Schmitt trigger
    lines.append(opamp(400, 150, "B", pins=["6(-)", "5(+)", "7(out)"]))
    
    # Integrator feedback capacitor
    lines.append(wire(180, 150, 220, 150))  # Output
    lines.append(wire(220, 150, 220, 100))  # Up
    lines.append(wire(220, 100, 130, 100))  # Across
    lines.append(wire(130, 100, 130, 135))  # Down to -in
    lines.append(capacitor(130, 85, label="C1", value="1µF", vertical=False))
    
    # Rate pot
    lines.append(potentiometer(220, 280, label="RATE", value="1MΩ"))
    lines.append(wire(220, 250, 220, 200))  # To integrator output area
    lines.append(wire(220, 200, 250, 200))  # To Schmitt trigger
    lines.append(wire(250, 200, 250, 165))  # Into -in of B
    
    # Schmitt trigger feedback
    lines.append(wire(430, 150, 480, 150))  # Output
    lines.append(wire(480, 150, 480, 80))   # Up
    lines.append(wire(480, 80, 330, 80))    # Across
    lines.append(wire(330, 80, 330, 100))   # To voltage divider
    lines.append(resistor(330, 110, label="100k", vertical=True))
    lines.append(resistor(330, 140, label="100k", vertical=True))
    lines.append(ground(330, 160))
    
    # Triangle output
    lines.append(wire(220, 150, 220, 320))
    lines.append(jack(240, 320, label="TRI"))
    
    # Square output  
    lines.append(wire(480, 150, 480, 350))
    lines.append(resistor(480, 320, label="1.8k", vertical=True))
    lines.append(jack(500, 350, label="SQR"))
    
    lines.extend(svg_end())
    return '\n'.join(lines)


def generate_wiring_diagram():
    """Generate simplified system wiring diagram."""
    w, h = 900, 600
    lines = svg_start(w, h, "MACROBRUTE System Wiring — Overview", "Signal flow from MicroBrute to Expander")
    
    # Column labels
    blocks = [
        ("MicroBrute\nPCB", 100, 200),
        ("Breakout\nPCB", 280, 200),
        ("DB-9 A\n(Rear)", 450, 200),
        ("Cable", 580, 200),
        ("Expander", 750, 200),
    ]
    
    for label, x, y in blocks:
        lines.append(f'<rect x="{x-60}" y="{y-40}" width="120" height="80" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
        for i, line in enumerate(label.split('\n')):
            lines.append(f'<text x="{x}" y="{y-10+i*18}" class="label" text-anchor="middle">{line}</text>')
    
    # Signal lines
    signals = [
        ("TP94 Saw", 100, 100, 750, 100),
        ("TP93 Sqr", 100, 130, 750, 130),
        ("TP30 Mix", 100, 160, 750, 160),
        ("TP19 VCF", 100, 190, 750, 190),
        ("TP83 Gate", 100, 280, 750, 280),
        ("Pitch CV", 100, 310, 750, 310),
        ("Envelope", 100, 340, 750, 340),
        ("LFO", 100, 370, 750, 370),
    ]
    
    for label, x1, y1, x2, y2 in signals:
        lines.append(wire(x1+60, y1, x2-60, y2))
        lines.append(f'<text x="{x1+70}" y="{y1-5}" class="value" font-size="8">{label}</text>')
    
    lines.extend(svg_end())
    return '\n'.join(lines)


def main():
    """Generate all schematics."""
    os.makedirs("schematics", exist_ok=True)
    
    schematics = [
        ("noise_generator_schematic.svg", generate_noise_schematic),
        ("lfo_schematic.svg", generate_lfo_schematic),
        ("wiring_overview.svg", generate_wiring_diagram),
    ]
    
    for filename, generator in schematics:
        filepath = f"schematics/{filename}"
        with open(filepath, 'w') as f:
            f.write(generator())
        print(f"Generated: {filepath}")
    
    print("\nDone. Add these to SVG_MAP in build_manual.py to include in manual.")


if __name__ == "__main__":
    main()
