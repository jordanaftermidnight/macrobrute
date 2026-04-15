#!/usr/bin/env python3
"""Generate cleaner diagrams v2 - addressing feedback."""

import os


class SVGRenderer:
    """Simple SVG renderer."""
    
    def __init__(self, width, height, title, subtitle=""):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.elements = []
        
    def header(self):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
<defs>
  <filter id="ts">
    <feFlood flood-color="white" flood-opacity="0.9" result="bg"/>
    <feMorphology in="SourceGraphic" operator="dilate" radius="1.5" result="d"/>
    <feComposite in="bg" in2="d" operator="in" result="s"/>
    <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#666"/>
  </marker>
</defs>
<style>
  .t {{ font: bold 16px sans-serif; fill: #1a1a1a; filter: url(#ts); }}
  .st {{ font: 11px sans-serif; fill: #555; filter: url(#ts); }}
  .l {{ font: bold 10px sans-serif; fill: #1a1a1a; filter: url(#ts); }}
  .v {{ font: 9px sans-serif; fill: #555; filter: url(#ts); }}
  .sl {{ font: bold 9px sans-serif; fill: #FFF; text-anchor: middle; }}
</style>
<rect width="{self.width}" height="{self.height}" fill="#FEFEFE"/>
<text x="{self.width//2}" y="25" class="t" text-anchor="middle">{self.title}</text>
{f'<text x="{self.width//2}" y="45" class="st" text-anchor="middle">{self.subtitle}</text>' if self.subtitle else ''}
'''
    
    def footer(self):
        return '</svg>'
        
    def rect(self, x, y, w, h, fill, stroke="#1a1a1a", sw=2, label="", sublabel=""):
        r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="4"/>\n'
        if label:
            r += f'<text x="{x+w/2}" y="{y+h/2-2}" class="sl" font-size="10">{label}</text>\n'
        if sublabel:
            r += f'<text x="{x+w/2}" y="{y+h/2+12}" class="sl" font-size="8">{sublabel}</text>\n'
        return r
        
    def line(self, x1, y1, x2, y2, color="#666", sw=2, dashed=False):
        dash = ' stroke-dasharray="5,3"' if dashed else ''
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{dash}/>\n'
        
    def elbow(self, x1, y1, x2, y2, color="#666", label=""):
        mid_x = (x1 + x2) / 2
        s = f'<path d="M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
        if label:
            s += f'<text x="{mid_x}" y="{y1-4}" class="v" text-anchor="middle" font-size="7">{label}</text>\n'
        return s
        
    def text(self, x, y, text, cls="v", anchor="start", size=9, color="#333"):
        return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" font-size="{size}" fill="{color}">{text}</text>\n'


def audio_signal_flow_v2():
    """Audio Signal Flow - Fixed with Noise connection."""
    r = SVGRenderer(900, 600, "Audio Signal Flow", "VCO → Mixer → Filter → VCA → Output")
    
    C_VCO = "#E91E63"
    C_MIXER = "#FF9800" 
    C_FILTER = "#2196F3"
    C_VCA = "#4CAF50"
    C_OUT = "#9C27B0"
    
    svg = r.header()
    
    # Input sources (left column)
    sources = [
        ("Saw", "-5V/+5V", 55),
        ("Square", "0V/+5V", 90),
        ("Sub", "-5V/+5V", 125),
        ("Ext In", "Line", 160),
        ("Noise", "White", 195),
    ]
    for name, sub, y in sources:
        svg += r.rect(40, y, 85, 28, C_VCO, label=name, sublabel=sub)
    
    # Mixer (center)
    svg += r.rect(200, 105, 100, 50, C_MIXER, label="5-Input", sublabel="Mixer")
    
    # Connections to mixer - staggered to avoid overlap
    svg += r.elbow(125, 69, 200, 120, C_VCO)      # Saw
    svg += r.elbow(125, 104, 210, 125, C_VCO)     # Square  
    svg += r.elbow(125, 139, 220, 130, C_VCO)     # Sub
    svg += r.elbow(125, 174, 230, 135, C_VCO)     # Ext
    svg += r.elbow(125, 209, 240, 140, C_VCO)     # Noise
    
    # Filter
    svg += r.rect(360, 110, 90, 45, C_FILTER, label="VCF", sublabel="Filter")
    svg += r.elbow(300, 130, 360, 132, C_MIXER)
    
    # VCA
    svg += r.rect(510, 110, 90, 45, C_VCA, label="VCA", sublabel="ADSR")
    svg += r.elbow(450, 132, 510, 132, C_FILTER)
    
    # Output
    svg += r.rect(660, 110, 100, 45, C_OUT, label="MAIN", sublabel="Out")
    svg += r.elbow(600, 132, 660, 132, C_VCA)
    
    # Test points below
    svg += r.text(450, 200, "Test Points: TP94 (Saw), TP93 (Sqr), TP30 (Mix), TP19 (VCF), TP10/11 (VCA)", "v", "middle", 9)
    
    # Notes box at bottom
    svg += r.rect(50, 240, 800, 320, "#E8F5E9", "#4CAF50", 1)
    svg += r.text(450, 265, "Signal Flow Notes", "l", "middle", 11, "#1B5E20")
    
    notes = [
        ("Path:", "Saw/Square/Sub/Ext/Noise → Mixer → VCF → VCA → Main Out", 290),
        ("Mixer:", "Passive resistive mixer with 5 inputs (including noise)", 315),
        ("VCF:", "Steiner-Parker 12dB/octave filter with resonance control", 340),
        ("VCA:", "ADSR envelope controls amplitude", 365),
        ("Buffering:", "All test points have 1kΩ + TL074 buffer for protection", 390),
        ("TP30:", "Mix test point captures pre-filter signal", 415),
        ("TP19:", "VCF test point captures post-filter signal", 440),
    ]
    
    for label, txt, y in notes:
        svg += r.text(70, y, label, "l", "start", 9, "#1B5E20")
        svg += r.text(130, y, txt, "v", "start", 9)
    
    svg += r.footer()
    return svg


def cv_control_flow_v2():
    """CV Control Flow - Cleaner with no overlapping purple lines."""
    r = SVGRenderer(1000, 700, "CV Control Flow", "Modulation Routing")
    
    C_MOD = "#9C27B0"      # Purple - modulation sources
    C_DEST = "#2196F3"     # Blue - modulation targets
    C_INPUT = "#FF9800"    # Orange - external inputs
    C_EXPAND = "#4CAF50"   # Green - expander
    
    svg = r.header()
    
    # Headers
    svg += r.text(120, 70, "SOURCES", "l", "middle", 11, C_MOD)
    svg += r.text(500, 70, "TARGETS", "l", "middle", 11, C_DEST)
    svg += r.text(850, 70, "EXTERNAL INPUTS", "l", "middle", 11, C_INPUT)
    
    # Source blocks (left, staggered vertically with more spacing)
    sources = [
        ("LFO", "0-5V", 90, C_MOD),
        ("Envelope", "0-5V", 140, C_MOD),
        ("Pitch CV", "1V/oct", 190, C_MOD),
        ("Mod Wheel", "0-5V", 240, C_MOD),
        ("Exp LFO", "Free", 310, C_EXPAND),
        ("Exp S&H", "S&H", 360, C_EXPAND),
    ]
    source_pos = {}
    for name, sub, y, color in sources:
        svg += r.rect(50, y, 90, 38, color, label=name, sublabel=sub)
        source_pos[name] = y + 19
    
    # Target blocks (center)
    targets = [
        ("Pitch", "VCO", 90),
        ("Filter", "Cutoff", 140),
        ("Resonance", "Peak", 190),
        ("VCA", "Amp", 240),
        ("PWM", "Width", 290),
        ("Metalizer", "Harm", 340),
    ]
    target_pos = {}
    for name, sub, y in targets:
        svg += r.rect(450, y, 90, 38, C_DEST, label=name, sublabel=sub)
        target_pos[name] = y + 19
    
    # External inputs (right)
    inputs = [
        ("Filter CV", "DB-9 P1", 90),
        ("VCA CV", "DB-9 P2", 140),
        ("Res CV", "Vactrol", 190),
        ("Gate In", "DB-9 P5", 240),
        ("Sync", "DB-9 P4", 290),
    ]
    input_pos = {}
    for name, sub, y in inputs:
        svg += r.rect(800, y, 110, 38, C_INPUT, label=name, sublabel=sub)
        input_pos[name] = y + 19
    
    # CONNECTIONS - using distinct vertical paths to prevent overlap
    # LFO connections - each to a different vertical channel
    svg += r.line(140, source_pos["LFO"], 200, source_pos["LFO"], C_MOD, 2)  # Horizontal out
    svg += r.line(200, source_pos["LFO"], 200, target_pos["Pitch"], C_MOD, 2)  # Vertical down
    svg += r.line(200, target_pos["Pitch"], 450, target_pos["Pitch"], C_MOD, 2)  # To target
    
    svg += r.line(200, source_pos["LFO"], 220, source_pos["LFO"], C_MOD, 2)
    svg += r.line(220, 109, 220, target_pos["Filter"], C_MOD, 2)
    svg += r.line(220, target_pos["Filter"], 450, target_pos["Filter"], C_MOD, 2)
    
    svg += r.line(200, source_pos["LFO"], 240, source_pos["LFO"], C_MOD, 2)
    svg += r.line(240, 109, 240, target_pos["VCA"], C_MOD, 2)
    svg += r.line(240, target_pos["VCA"], 450, target_pos["VCA"], C_MOD, 2)
    
    # Envelope connections
    svg += r.line(140, source_pos["Envelope"], 260, source_pos["Envelope"], C_MOD, 2)
    svg += r.line(260, 159, 260, target_pos["Filter"], C_MOD, 2)
    svg += r.line(260, target_pos["Filter"]+5, 450, target_pos["Filter"]+5, C_MOD, 2)
    
    svg += r.line(260, 159, 280, 159, C_MOD, 2)
    svg += r.line(280, 159, 280, target_pos["VCA"], C_MOD, 2)
    svg += r.line(280, target_pos["VCA"]+5, 450, target_pos["VCA"]+5, C_MOD, 2)
    
    # Pitch CV
    svg += r.line(140, source_pos["Pitch CV"], 300, source_pos["Pitch CV"], C_MOD, 2)
    svg += r.line(300, 209, 300, target_pos["Pitch"], C_MOD, 2)
    svg += r.line(300, target_pos["Pitch"]+5, 450, target_pos["Pitch"]+5, C_MOD, 2)
    
    # Mod Wheel
    svg += r.line(140, source_pos["Mod Wheel"], 320, source_pos["Mod Wheel"], C_MOD, 2)
    svg += r.line(320, 259, 320, target_pos["Pitch"], C_MOD, 2)
    svg += r.line(320, target_pos["Pitch"]+10, 450, target_pos["Pitch"]+10, C_MOD, 2)
    
    # Expander connections (green)
    svg += r.line(140, source_pos["Exp LFO"], 340, source_pos["Exp LFO"], C_EXPAND, 2)
    svg += r.line(340, 329, 340, target_pos["Resonance"], C_EXPAND, 2)
    svg += r.line(340, target_pos["Resonance"], 450, target_pos["Resonance"], C_EXPAND, 2)
    
    svg += r.line(140, source_pos["Exp S&H"], 360, source_pos["Exp S&H"], C_EXPAND, 2)
    svg += r.line(360, 379, 360, target_pos["Resonance"], C_EXPAND, 2)
    svg += r.line(360, target_pos["Resonance"]+5, 450, target_pos["Resonance"]+5, C_EXPAND, 2)
    
    # External inputs (orange) - from right
    for src_name, target_name, x_offset in [
        ("Filter CV", "Filter", 550),
        ("VCA CV", "VCA", 570),
        ("Res CV", "Resonance", 590),
        ("Gate In", "PWM", 610),
        ("Sync", "Metalizer", 630),
    ]:
        svg += r.line(800, input_pos[src_name], x_offset, input_pos[src_name], C_INPUT, 2)
        svg += r.line(x_offset, input_pos[src_name], x_offset, target_pos[target_name], C_INPUT, 2)
        svg += r.line(x_offset, target_pos[target_name], 540, target_pos[target_name], C_INPUT, 2)
    
    # Notes
    svg += r.rect(50, 430, 900, 240, "#FFF3E0", "#FF9800", 1)
    svg += r.text(500, 455, "CV Routing Notes", "l", "middle", 11, "#E65100")
    
    notes = [
        ("Mod Matrix:", "MicroBrute routes LFO/Env to destinations via panel switches", 480),
        ("Summing:", "Multiple CV sources sum at destination (e.g., Pitch = Key + LFO + Wheel)", 505),
        ("Vactrol:", "Resonance uses optocoupler for smooth control", 530),
        ("Protection:", "All CV inputs have 100kΩ series + clamping diodes", 555),
    ]
    for label, txt, y in notes:
        svg += r.text(70, y, label, "l", "start", 9, "#E65100")
        svg += r.text(160, y, txt, "v", "start", 9)
    
    svg += r.footer()
    return svg


def pico_pinout_v2():
    """Pico H Pinout - With all pins shown."""
    r = SVGRenderer(1000, 750, "Raspberry Pi Pico H Pinout", "All GPIO Pins with MACROBRUTE Functions")
    
    svg = r.header()
    
    # Board
    bx, by, bw, bh = 300, 80, 400, 600
    svg += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#006600" stroke="#1a1a1a" stroke-width="3" rx="8"/>\n'
    
    # USB
    svg += f'<rect x="{bx+150}" y="{by-15}" width="100" height="20" fill="#333" stroke="#666"/>\n'
    svg += r.text(bx+200, by-3, "Micro USB", "v", "middle", 8, "#CCC")
    
    # Left side - ALL GPIO 0-15
    left_pins = [
        (0, "UART0 TX", "#00BCD4", True),
        (1, "UART0 RX", "#00BCD4", True),
        (2, "(ADC0)", "#9E9E9E", False),
        (3, "(ADC1)", "#9E9E9E", False),
        (4, "MIDI TX", "#E91E63", True),
        (5, "MIDI RX", "#E91E63", True),
        (6, "(GPIO)", "#9E9E9E", False),
        (7, "(GPIO)", "#9E9E9E", False),
        (8, "LED Clock", "#FF9800", True),
        (9, "LED Gate", "#FF9800", True),
        (10, "LED Mode", "#FF9800", True),
        (11, "(GPIO)", "#9E9E9E", False),
        (12, "Tap Button", "#4CAF50", True),
        (13, "Enc Button", "#4CAF50", True),
        (14, "Enc CLK", "#4CAF50", True),
        (15, "Enc DT", "#4CAF50", True),
    ]
    
    for i, (pin, func, color, used) in enumerate(left_pins):
        y = by + 40 + i * 35
        svg += f'<circle cx="{bx}" cy="{y}" r="6" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+12, y+3, f"GP{pin}", "v", "start", 8, "#FFF")
        if used:
            svg += f'<rect x="{bx-100}" y="{y-10}" width="85" height="20" fill="{color}" stroke="#333" rx="2"/>\n'
            svg += r.text(bx-57, y+4, func, "sl", "middle", 8)
        else:
            svg += r.text(bx-10, y+3, func, "v", "end", 7, "#999")
    
    # Right side - ALL GPIO 16-28
    right_pins = [
        (16, "OLED DC", "#2196F3", True),
        (17, "OLED CS", "#2196F3", True),
        (18, "OLED SCK", "#2196F3", True),
        (19, "OLED MOSI", "#2196F3", True),
        (20, "OLED RST", "#2196F3", True),
        (21, "Clock In", "#9C27B0", True),
        (22, "Clock Out", "#9C27B0", True),
        (26, "(ADC0)", "#9E9E9E", False),
        (27, "(ADC1)", "#9E9E9E", False),
        (28, "(ADC2)", "#9E9E9E", False),
    ]
    
    for i, (pin, func, color, used) in enumerate(right_pins):
        y = by + 40 + i * 50
        svg += f'<circle cx="{bx+bw}" cy="{y}" r="6" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+bw-10, y+3, f"GP{pin}", "v", "end", 8, "#FFF")
        if used:
            svg += f'<rect x="{bx+bw+15}" y="{y-10}" width="75" height="20" fill="{color}" stroke="#333" rx="2"/>\n'
            svg += r.text(bx+bw+52, y+4, func, "sl", "middle", 8)
        else:
            svg += r.text(bx+bw+10, y+3, func, "v", "start", 7, "#999")
    
    # Bottom debug pins
    debug_y = by + bh + 25
    svg += r.text(bx+bw/2, debug_y, "DEBUG HEADER: SWDIO | SWCLK | VSYS (+5V) | GND", "v", "middle", 9, "#666")
    
    # Pin 1 marker
    svg += f'<rect x="{bx+10}" y="{by+10}" width="15" height="5" fill="#FFF"/>\n'
    
    # Legend
    svg += r.rect(50, 670, 900, 70, "#F5F5F5", "#999", 1)
    svg += r.text(500, 690, "Legend: Colored = Used in MACROBRUTE | Gray = Unused/Available", "v", "middle", 10)
    
    items = [
        ("#2196F3", "SPI"),
        ("#4CAF50", "Buttons"),
        ("#FF9800", "LEDs"),
        ("#00BCD4", "UART0"),
        ("#E91E63", "MIDI"),
        ("#9C27B0", "Clock"),
        ("#9E9E9E", "Unused"),
    ]
    for i, (c, txt) in enumerate(items):
        x = 100 + i * 120
        svg += f'<rect x="{x}" y="{705}" width="20" height="14" fill="{c}" stroke="#333" rx="2"/>\n'
        svg += r.text(x+28, 717, txt, "v", "start", 8)
    
    svg += r.footer()
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("audio_signal_flow", audio_signal_flow_v2),
        ("cv_control_flow", cv_control_flow_v2),
        ("pico_pinout_diagram", pico_pinout_v2),
    ]
    
    for name, func in diagrams:
        try:
            svg = func()
            with open(f"{out}/{name}.svg", 'w') as f:
                f.write(svg)
            print(f"Generated: {name}.svg")
        except Exception as e:
            print(f"Error {name}: {e}")
    
    print("Done!")


if __name__ == "__main__":
    main()
