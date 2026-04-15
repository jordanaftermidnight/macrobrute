#!/usr/bin/env python3
"""Generate diagrams v3 - comprehensive fixes."""

import os


class SVGRenderer:
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
    <polygon points="0 0, 8 3, 0 6" fill="#333"/>
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
        
    def text(self, x, y, text, cls="v", anchor="start", size=9, color="#333"):
        return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" font-size="{size}" fill="{color}">{text}</text>\n'


def system_architecture_v3():
    """System Architecture - Cleaner with explicit signal flow."""
    r = SVGRenderer(1000, 700, "MACROBRUTE System Architecture", "Signal Flow Direction: Left → Right")
    
    C_MICRO = "#2196F3"
    C_DB9A = "#FF9800"
    C_DB9B = "#FF5722"
    C_PICO = "#9C27B0"
    C_TOUCH = "#673AB7"
    C_EXPAND = "#4CAF50"
    C_AUDIO = "#E91E63"
    
    svg = r.header()
    
    # Section headers
    svg += r.text(150, 70, "MICROBRUTE", "l", "middle", 11, C_MICRO)
    svg += r.text(500, 70, "INTERFACE", "l", "middle", 11, "#666")
    svg += r.text(850, 70, "EXPANDER", "l", "middle", 11, C_EXPAND)
    
    # MicroBrute blocks
    micro = [
        ("VCO", "Osc", 85),
        ("VCF", "Filter", 135),
        ("VCA", "Amp", 185),
        ("LFO", "LFO", 235),
        ("ENV", "Env", 285),
    ]
    micro_y = {}
    for name, sub, y in micro:
        svg += r.rect(50, y, 110, 40, C_MICRO, label=name, sublabel=sub)
        micro_y[name] = y + 20
    
    # DB-9 A (Outputs from MicroBrute)
    svg += r.rect(400, 85, 120, 100, C_DB9A, label="DB-9 A", sublabel="OUTPUTS")
    svg += r.text(460, 130, "Saw→Pin7", "v", "middle", 8)
    svg += r.text(460, 145, "Sqr→Pin8", "v", "middle", 8)
    svg += r.text(460, 160, "Mix→Pin5", "v", "middle", 8)
    svg += r.text(460, 175, "VCF→Pin6", "v", "middle", 8)
    
    # DB-9 B (Inputs TO MicroBrute)
    svg += r.rect(400, 235, 120, 100, C_DB9B, label="DB-9 B", sublabel="INPUTS")
    svg += r.text(460, 275, "Filter CV ←P1", "v", "middle", 8)
    svg += r.text(460, 290, "VCA CV ←P2", "v", "middle", 8)
    svg += r.text(460, 305, "Res CV ←P3", "v", "middle", 8)
    svg += r.text(460, 320, "Sync ←P4", "v", "middle", 8)
    
    # Pico W
    svg += r.rect(400, 380, 120, 50, C_PICO, label="Pico W", sublabel="Control")
    
    # Touch Pads
    svg += r.rect(400, 450, 120, 40, C_TOUCH, label="Touch", sublabel="4-Point")
    
    # Expander blocks
    exp = [
        ("Noise", "Gen", 85),
        ("LFO", "Free", 135),
        ("S&H", "Sample", 185),
        ("Clock", "Div", 235),
        ("Slew", "Glide", 285),
        ("Atten", "CV", 335),
    ]
    exp_y = {}
    for name, sub, y in exp:
        svg += r.rect(820, y, 110, 40, C_EXPAND, label=name, sublabel=sub)
        exp_y[name] = y + 20
    
    # FLOW 1: MicroBrute → DB-9 A (outputs)
    svg += r.line(160, micro_y["VCO"], 400, 120, C_MICRO, 3)
    svg += r.text(280, 115, "Saw/Sqr→", "v", "middle", 8)
    
    svg += r.line(160, micro_y["VCF"], 400, 150, C_MICRO, 3)
    svg += r.text(280, 145, "VCF→", "v", "middle", 8)
    
    # FLOW 2: DB-9 A → Expander (outputs to modules)
    svg += r.line(520, 120, 820, exp_y["Noise"], C_DB9A, 3)
    svg += r.text(670, 100, "→Noise In", "v", "middle", 8)
    
    svg += r.line(520, 150, 820, 155, C_DB9A, 3)
    svg += r.text(670, 145, "Audio→LFO", "v", "middle", 8)
    
    # FLOW 3: Expander → DB-9 B (inputs FROM expander)
    svg += r.line(820, exp_y["LFO"], 600, 275, C_EXPAND, 3)
    svg += r.text(710, 260, "Filter CV→", "v", "middle", 8)
    
    svg += r.line(820, exp_y["S&H"], 600, 290, C_EXPAND, 3)
    svg += r.text(710, 280, "Res CV→", "v", "middle", 8)
    
    svg += r.line(820, exp_y["Clock"], 600, 320, C_EXPAND, 3)
    svg += r.text(710, 310, "Sync→", "v", "middle", 8)
    
    # FLOW 4: DB-9 B → MicroBrute (inputs to synth)
    svg += r.line(400, 285, 160, micro_y["VCF"]+5, C_DB9B, 3)
    svg += r.text(280, 270, "→Filter", "v", "middle", 8)
    
    svg += r.line(400, 300, 160, micro_y["VCA"]+5, C_DB9B, 3)
    svg += r.text(280, 295, "→VCA", "v", "middle", 8)
    
    # Control signals
    svg += r.line(520, 405, 820, 350, C_PICO, 2, True)
    svg += r.text(670, 370, "GPIO Control", "v", "middle", 8)
    
    svg += r.line(520, 470, 820, 370, C_TOUCH, 2, True)
    svg += r.text(670, 415, "Touch Sense", "v", "middle", 8)
    
    # Legend
    svg += r.rect(50, 550, 900, 120, "#F5F5F5", "#999", 1)
    svg += r.text(500, 575, "Signal Flow", "l", "middle", 10)
    
    notes = [
        "1. MicroBrute outputs (VCO, VCF) → DB-9 A pins",
        "2. DB-9 A → Expander modules (audio/CV distribution)",
        "3. Expander generates CV/gates → DB-9 B inputs",
        "4. DB-9 B → MicroBrute (modulates Filter, VCA, etc.)",
    ]
    for i, note in enumerate(notes):
        svg += r.text(70, 600 + i*18, note, "v", "start", 9)
    
    svg += r.footer()
    return svg


def audio_signal_flow_v3():
    """Audio Signal Flow - Compact with smaller notes."""
    r = SVGRenderer(850, 450, "Audio Signal Flow", "VCO → Mixer → Filter → VCA → Output")
    
    C_VCO = "#E91E63"
    C_MIXER = "#FF9800"
    C_FILTER = "#2196F3"
    C_VCA = "#4CAF50"
    C_OUT = "#9C27B0"
    
    svg = r.header()
    
    # Input sources
    sources = [
        ("Saw", "-5/+5V", 50),
        ("Square", "0/+5V", 85),
        ("Sub", "-5/+5V", 120),
        ("Ext In", "Line", 155),
        ("Noise", "White", 190),
    ]
    for name, sub, y in sources:
        svg += r.rect(30, y, 80, 28, C_VCO, label=name, sublabel=sub)
    
    # Mixer
    svg += r.rect(170, 110, 90, 50, C_MIXER, label="5-Input", sublabel="Mixer")
    
    # Connections to mixer
    for y in [64, 99, 134, 169, 204]:
        svg += r.line(110, y, 170, 135, C_VCO, 2)
    
    # Filter
    svg += r.rect(320, 115, 80, 45, C_FILTER, label="VCF", sublabel="Filter")
    svg += r.line(260, 135, 320, 137, C_MIXER, 3)
    
    # VCA
    svg += r.rect(460, 115, 80, 45, C_VCA, label="VCA", sublabel="ADSR")
    svg += r.line(400, 137, 460, 137, C_FILTER, 3)
    
    # Output
    svg += r.rect(600, 115, 90, 45, C_OUT, label="MAIN", sublabel="Output")
    svg += r.line(540, 137, 600, 137, C_VCA, 3)
    
    # Test points
    svg += r.text(425, 185, "Test Points: TP94 (Saw), TP93 (Sqr), TP30 (Mix), TP19 (VCF), TP10/11 (VCA)", "v", "middle", 8)
    
    # Compact notes box
    svg += r.rect(30, 220, 790, 130, "#E8F5E9", "#4CAF50", 1)
    svg += r.text(425, 240, "Notes", "l", "middle", 10, "#1B5E20")
    
    notes = [
        "Path: Saw/Square/Sub/Ext/Noise → Mixer → VCF → VCA → Main Out",
        "Mixer: Passive with 5 inputs including noise | VCF: Steiner-Parker 12dB/oct",
        "All test points buffered with 1kΩ + TL074 for protection",
    ]
    for i, txt in enumerate(notes):
        svg += r.text(50, 265 + i*20, txt, "v", "start", 9)
    
    # Add buffer notes inline
    svg += r.text(140, 100, "1kΩ+buf", "v", "middle", 7, "#666")
    svg += r.text(290, 100, "1kΩ+buf", "v", "middle", 7, "#666")
    svg += r.text(430, 100, "1kΩ+buf", "v", "middle", 7, "#666")
    
    svg += r.footer()
    return svg


def cv_control_flow_v3():
    """CV Control Flow - Grid-based routing, no overlapping lines."""
    r = SVGRenderer(1000, 600, "CV Control Flow", "Modulation Matrix")
    
    C_MOD = "#9C27B0"
    C_DEST = "#2196F3"
    C_INPUT = "#FF9800"
    C_EXPAND = "#4CAF50"
    
    svg = r.header()
    
    # Headers
    svg += r.text(120, 60, "SOURCES", "l", "middle", 10, C_MOD)
    svg += r.text(500, 60, "DESTINATIONS", "l", "middle", 10, C_DEST)
    svg += r.text(850, 60, "EXTERNAL", "l", "middle", 10, C_INPUT)
    
    # Sources (left column)
    sources = [
        ("LFO", 80),
        ("Envelope", 120),
        ("Pitch CV", 160),
        ("Mod Wheel", 200),
        ("Exp LFO", 260),
        ("Exp S&H", 300),
    ]
    src_y = {}
    for name, y in sources:
        color = C_EXPAND if "Exp" in name else C_MOD
        svg += r.rect(50, y, 85, 32, color, label=name)
        src_y[name] = y + 16
    
    # Destinations (center column)
    dests = [
        ("Pitch", 80),
        ("Filter", 120),
        ("Resonance", 160),
        ("VCA", 200),
        ("PWM", 240),
        ("Metalizer", 280),
    ]
    dst_y = {}
    for name, y in dests:
        svg += r.rect(450, y, 90, 32, C_DEST, label=name)
        dst_y[name] = y + 16
    
    # External inputs (right column)
    inputs = [
        ("Filter CV", 80),
        ("VCA CV", 120),
        ("Res CV", 160),
        ("Gate In", 200),
        ("Sync", 240),
    ]
    inp_y = {}
    for name, y in inputs:
        svg += r.rect(800, y, 100, 32, C_INPUT, label=name)
        inp_y[name] = y + 16
    
    # Connection matrix - using vertical/horizontal grid routing
    # Each connection gets a unique path
    
    # LFO → multiple destinations (use different x-offsets)
    connections = [
        # (source, dest, color, x_channel)
        ("LFO", "Pitch", C_MOD, 180),
        ("LFO", "Filter", C_MOD, 200),
        ("LFO", "VCA", C_MOD, 220),
        ("Envelope", "Filter", C_MOD, 240),
        ("Envelope", "VCA", C_MOD, 260),
        ("Pitch CV", "Pitch", C_MOD, 280),
        ("Mod Wheel", "Pitch", C_MOD, 300),
        ("Exp LFO", "Resonance", C_EXPAND, 320),
        ("Exp S&H", "Resonance", C_EXPAND, 340),
    ]
    
    for src, dst, color, x_chan in connections:
        # Source → channel
        svg += r.line(135, src_y[src], x_chan, src_y[src], color, 2)
        # Channel → destination height
        svg += r.line(x_chan, src_y[src], x_chan, dst_y[dst], color, 2)
        # → destination
        svg += r.line(x_chan, dst_y[dst], 450, dst_y[dst], color, 2)
    
    # External inputs (from right)
    ext_connections = [
        ("Filter CV", "Filter", 600),
        ("VCA CV", "VCA", 620),
        ("Res CV", "Resonance", 640),
        ("Gate In", "PWM", 660),
        ("Sync", "Metalizer", 680),
    ]
    
    for src, dst, x_chan in ext_connections:
        svg += r.line(800, inp_y[src], x_chan, inp_y[src], C_INPUT, 2)
        svg += r.line(x_chan, inp_y[src], x_chan, dst_y[dst], C_INPUT, 2)
        svg += r.line(x_chan, dst_y[dst], 540, dst_y[dst], C_INPUT, 2)
    
    # Notes (compact)
    svg += r.rect(50, 360, 900, 100, "#FFF3E0", "#FF9800", 1)
    svg += r.text(500, 380, "CV Routing", "l", "middle", 10, "#E65100")
    svg += r.text(70, 405, "• LFO/Envelope route via MicroBrute mod matrix panel switches", "v", "start", 9)
    svg += r.text(70, 425, "• Multiple CV sources sum at destination (Pitch = Key + LFO + Wheel)", "v", "start", 9)
    svg += r.text(70, 445, "• External CV inputs protected with 100kΩ series + clamping diodes", "v", "start", 9)
    
    svg += r.footer()
    return svg


def pico_pinout_v3():
    """Pico H Pinout - Compact, fits in frame."""
    r = SVGRenderer(900, 650, "Raspberry Pi Pico H Pinout", "All GPIO with Functions")
    
    svg = r.header()
    
    # Board (slightly smaller)
    bx, by, bw, bh = 280, 60, 340, 530
    svg += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#006600" stroke="#1a1a1a" stroke-width="3" rx="8"/>\n'
    
    # USB
    svg += f'<rect x="{bx+120}" y="{by-12}" width="100" height="18" fill="#333" stroke="#666"/>\n'
    svg += r.text(bx+170, by-2, "Micro USB", "v", "middle", 8, "#CCC")
    
    # Left side pins 0-15 (compact spacing)
    left_pins = [
        (0, "UART0 TX", "#00BCD4", True),
        (1, "UART0 RX", "#00BCD4", True),
        (2, "ADC0", "#9E9E9E", False),
        (3, "ADC1", "#9E9E9E", False),
        (4, "MIDI TX", "#E91E63", True),
        (5, "MIDI RX", "#E91E63", True),
        (6, "GPIO", "#9E9E9E", False),
        (7, "GPIO", "#9E9E9E", False),
        (8, "LED Clk", "#FF9800", True),
        (9, "LED Gate", "#FF9800", True),
        (10, "LED Mode", "#FF9800", True),
        (11, "GPIO", "#9E9E9E", False),
        (12, "Tap Btn", "#4CAF50", True),
        (13, "Enc Btn", "#4CAF50", True),
        (14, "Enc CLK", "#4CAF50", True),
        (15, "Enc DT", "#4CAF50", True),
    ]
    
    for i, (pin, func, color, used) in enumerate(left_pins):
        y = by + 35 + i * 32
        svg += f'<circle cx="{bx}" cy="{y}" r="5" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+10, y+3, f"GP{pin}", "v", "start", 7, "#FFF")
        if used:
            svg += f'<rect x="{bx-85}" y="{y-9}" width="70" height="18" fill="{color}" stroke="#333" rx="2"/>\n'
            svg += r.text(bx-50, y+4, func, "sl", "middle", 7)
        else:
            svg += r.text(bx-8, y+3, func, "v", "end", 6, "#AAA")
    
    # Right side pins 16-28
    right_pins = [
        (16, "OLED DC", "#2196F3", True),
        (17, "OLED CS", "#2196F3", True),
        (18, "OLED SCK", "#2196F3", True),
        (19, "OLED MOSI", "#2196F3", True),
        (20, "OLED RST", "#2196F3", True),
        (21, "Clk In", "#9C27B0", True),
        (22, "Clk Out", "#9C27B0", True),
        (26, "ADC0", "#9E9E9E", False),
        (27, "ADC1", "#9E9E9E", False),
        (28, "ADC2", "#9E9E9E", False),
    ]
    
    for i, (pin, func, color, used) in enumerate(right_pins):
        y = by + 35 + i * 48
        svg += f'<circle cx="{bx+bw}" cy="{y}" r="5" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+bw-8, y+3, f"GP{pin}", "v", "end", 7, "#FFF")
        if used:
            svg += f'<rect x="{bx+bw+12}" y="{y-9}" width="65" height="18" fill="{color}" stroke="#333" rx="2"/>\n'
            svg += r.text(bx+bw+44, y+4, func, "sl", "middle", 7)
        else:
            svg += r.text(bx+bw+8, y+3, func, "v", "start", 6, "#AAA")
    
    # Debug pins at bottom (inside board area)
    svg += r.text(bx+bw/2, by+bh-15, "DEBUG: SWDIO | SWCLK | VSYS | GND", "v", "middle", 8, "#CCC")
    
    # Pin 1 marker
    svg += f'<rect x="{bx+8}" y="{by+8}" width="12" height="4" fill="#FFF"/>\n'
    
    # Legend (inside frame, bottom)
    svg += r.rect(50, 610, 800, 35, "#F5F5F5", "#999", 1)
    svg += r.text(450, 630, "Colored = Used in MACROBRUTE | Gray = Unused/Available", "v", "middle", 9)
    
    items = [
        ("#2196F3", "SPI"), ("#4CAF50", "BTN"), ("#FF9800", "LED"),
        ("#00BCD4", "UART"), ("#E91E63", "MIDI"), ("#9C27B0", "CLK"),
    ]
    for i, (c, txt) in enumerate(items):
        x = 100 + i * 120
        svg += f'<rect x="{x}" y="{640}" width="18" height="12" fill="{c}" stroke="#333" rx="2"/>\n'
        svg += r.text(x+26, 651, txt, "v", "start", 8)
    
    svg += r.footer()
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("system_architecture_block", system_architecture_v3),
        ("audio_signal_flow", audio_signal_flow_v3),
        ("cv_control_flow", cv_control_flow_v3),
        ("pico_pinout_diagram", pico_pinout_v3),
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
