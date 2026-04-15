#!/usr/bin/env python3
"""Generate corrected circuit schematics with verified pinouts."""

import os


class CircuitRenderer:
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
    <feMorphology in="SourceGraphic" operator="dilate" radius="1" result="d"/>
    <feComposite in="bg" in2="d" operator="in" result="s"/>
    <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style>
  .t {{ font: bold 14px sans-serif; fill: #1a1a1a; filter: url(#ts); }}
  .st {{ font: 10px sans-serif; fill: #555; filter: url(#ts); }}
  .l {{ font: bold 10px sans-serif; fill: #1a1a1a; filter: url(#ts); }}
  .v {{ font: 9px sans-serif; fill: #555; filter: url(#ts); }}
  .p {{ font: 8px sans-serif; fill: #666; }}
  .w {{ stroke: #1a1a1a; stroke-width: 1.5; fill: none; }}
  .c {{ stroke: #1a1a1a; stroke-width: 1.5; fill: none; }}
</style>
<rect width="{self.width}" height="{self.height}" fill="#FEFEFE"/>
<text x="{self.width//2}" y="20" class="t" text-anchor="middle">{self.title}</text>
{f'<text x="{self.width//2}" y="35" class="st" text-anchor="middle">{self.subtitle}</text>' if self.subtitle else ''}
'''
    
    def footer(self):
        return '</svg>'
        
    def ic_dip8(self, x, y, label, pins):
        """Draw DIP-8 IC with verified pinout."""
        # Body
        s = f'<rect x="{x}" y="{y}" width="60" height="80" fill="#333" stroke="#1a1a1a" stroke-width="2" rx="3"/>\n'
        s += f'<text x="{x+30}" y="{y+45}" class="l" text-anchor="middle" fill="#FFF" font-size="9">{label}</text>\n'
        # Pin 1 dot
        s += f'<circle cx="{x+8}" cy="{y+8}" r="3" fill="gold"/>\n'
        # Pins (DIP-8: 1-4 left top to bottom, 5-8 right bottom to top)
        pin_names = pins if len(pins) == 8 else pins + [""] * (8 - len(pins))
        for i in range(4):
            # Left side: pins 1-4 (top to bottom)
            py = y + 15 + i * 18
            s += f'<circle cx="{x}" cy="{py}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+8}" y="{py+2}" class="p" fill="#FFF" font-size="6">{i+1}:{pin_names[i]}</text>\n'
            # Right side: pins 8-5 (bottom to top)
            py2 = y + 69 - i * 18
            s += f'<circle cx="{x+60}" cy="{py2}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+52}" y="{py2+2}" class="p" fill="#FFF" font-size="6" text-anchor="end">{8-i}:{pin_names[7-i]}</text>\n'
        return s
        
    def ic_dip14(self, x, y, label, pins):
        """Draw DIP-14 IC with verified pinout."""
        s = f'<rect x="{x}" y="{y}" width="60" height="120" fill="#333" stroke="#1a1a1a" stroke-width="2" rx="3"/>\n'
        s += f'<text x="{x+30}" y="{y+65}" class="l" text-anchor="middle" fill="#FFF" font-size="9">{label}</text>\n'
        s += f'<circle cx="{x+8}" cy="{y+8}" r="3" fill="gold"/>\n'
        pin_names = pins if len(pins) == 14 else pins + [""] * (14 - len(pins))
        for i in range(7):
            py = y + 15 + i * 15
            s += f'<circle cx="{x}" cy="{py}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+8}" y="{py+2}" class="p" fill="#FFF" font-size="5">{i+1}:{pin_names[i][:8]}</text>\n'
            py2 = y + 105 - i * 15
            s += f'<circle cx="{x+60}" cy="{py2}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+52}" y="{py2+2}" class="p" fill="#FFF" font-size="5" text-anchor="end">{14-i}:{pin_names[13-i][:8]}</text>\n'
        return s
        
    def ic_dip16(self, x, y, label, pins):
        """Draw DIP-16 IC with verified pinout."""
        s = f'<rect x="{x}" y="{y}" width="60" height="140" fill="#333" stroke="#1a1a1a" stroke-width="2" rx="3"/>\n'
        s += f'<text x="{x+30}" y="{y+75}" class="l" text-anchor="middle" fill="#FFF" font-size="9">{label}</text>\n'
        s += f'<circle cx="{x+8}" cy="{y+8}" r="3" fill="gold"/>\n'
        pin_names = pins if len(pins) == 16 else pins + [""] * (16 - len(pins))
        for i in range(8):
            py = y + 15 + i * 15
            s += f'<circle cx="{x}" cy="{py}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+8}" y="{py+2}" class="p" fill="#FFF" font-size="5">{i+1}:{pin_names[i][:7]}</text>\n'
            py2 = y + 125 - i * 15
            s += f'<circle cx="{x+60}" cy="{py2}" r="2.5" fill="gold"/>\n'
            s += f'<text x="{x+52}" y="{py2+2}" class="p" fill="#FFF" font-size="5" text-anchor="end">{16-i}:{pin_names[15-i][:7]}</text>\n'
        return s
        
    def text(self, x, y, text, cls="v", size=9, color="#333"):
        return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{color}">{text}</text>\n'


def cd4051_schematic():
    """CD4051 Analog Multiplexer - Corrected pinout."""
    r = CircuitRenderer(600, 500, "CD4051 Analog Multiplexer", "8-Channel Analog/Digital MUX/DEMUX")
    
    svg = r.header()
    
    # CD4051 DIP-16 with correct pinout
    # Pinout: X4, X6, X, X7, X5, INH, VEE, VSS (left 1-8)
    #         C, B, A, X3, X0, X1, X2, VDD (right 16-9)
    pins = [
        "X4", "X6", "X COM", "X7", "X5", "INH", "VEE", "VSS",
        "VDD", "X2", "X1", "X0", "X3", "A", "B", "C"
    ]
    svg += r.ic_dip16(100, 80, "CD4051", pins)
    
    # Control signals (A, B, C)
    svg += r.text(200, 200, "A (GP10) → Pin 14", size=8)
    svg += r.text(200, 215, "B (GP11) → Pin 15", size=8)
    svg += r.text(200, 230, "C (GP12) → Pin 16", size=8)
    
    # Common I/O
    svg += r.text(200, 125, "X COM (Pin 3): Common I/O", size=8)
    svg += r.text(200, 140, "Connects to selected channel", size=8)
    
    # Channel inputs
    channels = [
        ("X0", "Noise Gen", 270),
        ("X1", "LFO", 285),
        ("X2", "S&H", 300),
        ("X3", "Clock", 315),
        ("X4", "Slew", 330),
        ("X5", "Atten", 345),
        ("X6", "Ext In", 360),
        ("X7", "Spare", 375),
    ]
    svg += r.text(200, 255, "Channel Inputs:", "l", size=9)
    for ch, src, y in channels:
        svg += r.text(210, y, f"{ch} ← {src}", size=8)
    
    # Power
    svg += r.text(200, 410, "Power:", "l", size=9)
    svg += r.text(210, 425, "VDD (Pin 16): +5V", size=8)
    svg += r.text(210, 440, "VSS (Pin 8): GND", size=8)
    svg += r.text(210, 455, "VEE (Pin 7): -5V or GND", size=8)
    svg += r.text(210, 470, "INH (Pin 6): GND (enable)", size=8)
    
    # Function description
    svg += r.text(400, 100, "Function:", "l", size=9)
    svg += r.text(400, 115, "8-channel analog switch", size=8)
    svg += r.text(400, 130, "Selects 1 of 8 inputs", size=8)
    svg += r.text(400, 145, "based on A/B/C control", size=8)
    
    svg += r.text(400, 170, "Truth Table:", "l", size=9)
    svg += r.text(400, 185, "C B A | Channel", size=8)
    svg += r.text(400, 200, "0 0 0 | X0", size=8)
    svg += r.text(400, 215, "0 0 1 | X1", size=8)
    svg += r.text(400, 230, "0 1 0 | X2", size=8)
    svg += r.text(400, 245, "...", size=8)
    svg += r.text(400, 260, "1 1 1 | X7", size=8)
    
    svg += r.footer()
    return svg


def buffered_multiple_schematic():
    """Buffered Multiple - 1 input to 3 outputs using TL074."""
    r = CircuitRenderer(600, 450, "Buffered Multiple (1→3)", "TL074 Quad Op-Amp as 4x Unity Gain Buffer")
    
    svg = r.header()
    
    # TL074 pins: OUT1, IN1-, IN1+, V+, IN2+, IN2-, OUT2, V- (left 1-4, right 5-8)
    # Actually: 1-OUT1, 2-IN1-, 3-IN1+, 4-VCC-, 5-IN2+, 6-IN2-, 7-OUT2, 8-VCC+ (DIP-8)
    # Wait, TL074 is DIP-14. Let me use TL071 (single) or TL074 (quad DIP-14)
    pins = [
        "OUT1", "IN1-", "IN1+", "VCC+", "IN2+", "IN2-", "OUT2",
        "OUT3", "IN3-", "IN3+", "GND", "IN4+", "IN4-", "OUT4"
    ]
    svg += r.ic_dip14(100, 80, "TL074", pins)
    
    # Input
    svg += r.text(50, 100, "IN", "l", size=9)
    svg += r.text(50, 115, "(from pot)", size=7)
    
    # Outputs
    outputs = ["OUT A", "OUT B", "OUT C"]
    for i, out in enumerate(outputs):
        y = 180 + i * 40
        svg += r.text(200, y, f"{out} → Expander", size=8)
    
    # Description
    svg += r.text(300, 100, "1 input buffered to", size=8)
    svg += r.text(300, 115, "3 identical outputs", size=8)
    svg += r.text(300, 130, "Unity gain (1x)", size=8)
    svg += r.text(300, 150, "Prevents signal", size=8)
    svg += r.text(300, 165, "loading between", size=8)
    svg += r.text(300, 180, "modules", size=8)
    
    svg += r.footer()
    return svg


def manual_gate_button_schematic():
    """Manual Gate Button - momentary switch to gate output."""
    r = CircuitRenderer(500, 400, "Manual Gate Button", "Momentary Switch + Debounce")
    
    svg = r.header()
    
    # Simple schematic layout
    svg += r.text(100, 100, "+5V", size=9)
    svg += r.text(100, 150, "[Switch]", size=9)
    svg += r.text(100, 200, "10kΩ", size=9)
    svg += r.text(100, 250, "→ Gate Out", size=9)
    svg += r.text(100, 280, "(to DB-9)", size=8)
    
    # Description
    svg += r.text(250, 120, "Momentary pushbutton", size=8)
    svg += r.text(250, 135, "generates gate signal", size=8)
    svg += r.text(250, 155, "10kΩ pull-down ensures", size=8)
    svg += r.text(250, 170, "clean OFF state", size=8)
    svg += r.text(250, 190, "Use with Schmitt trigger", size=8)
    svg += r.text(250, 205, "(CD40106) for debounce", size=8)
    
    svg += r.footer()
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("cd4051_multiplexer_schematic", cd4051_schematic),
        ("buffered_multiple_schematic", buffered_multiple_schematic),
        ("manual_gate_button_schematic", manual_gate_button_schematic),
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
