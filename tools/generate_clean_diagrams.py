#!/usr/bin/env python3
"""Generate clean, corrected diagrams for MACROBRUTE."""

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


def system_architecture():
    """System Architecture - Clean version with proper DB-9 A and DB-9 B connections."""
    r = SVGRenderer(1000, 700, "MACROBRUTE System Architecture", "Signal Flow: MicroBrute ↔ Breakout ↔ Expander")
    
    C_MICRO = "#2196F3"  # Blue
    C_DB9A = "#FF9800"   # Orange  
    C_DB9B = "#FF5722"   # Deep Orange
    C_PICO = "#9C27B0"   # Purple
    C_TOUCH = "#673AB7"  # Deep Purple
    C_EXPAND = "#4CAF50" # Green
    C_AUDIO = "#E91E63"  # Pink
    
    svg = r.header()
    
    # Section headers
    svg += r.text(150, 70, "MICROBRUTE CORE", "l", "middle", 12, C_MICRO)
    svg += r.text(500, 70, "BREAKOUT INTERFACE", "l", "middle", 12, "#666")
    svg += r.text(850, 70, "EXPANDER", "l", "middle", 12, C_EXPAND)
    
    # MicroBrute blocks (left)
    micro_blocks = [
        ("VCO", "Oscillator", 90),
        ("VCF", "Filter", 140),
        ("VCA", "Amplifier", 190),
        ("LFO", "LFO", 240),
        ("ENV", "Envelope", 290),
    ]
    micro_y = {}
    for name, sub, y in micro_blocks:
        svg += r.rect(50, y, 120, 40, C_MICRO, label=name, sublabel=sub)
        micro_y[name] = y + 20
    
    # DB-9 A - Outputs (top center)
    svg += r.rect(400, 90, 130, 60, C_DB9A, label="DB-9 A", sublabel="OUTPUTS →")
    db9a_y = 120
    
    # DB-9 B - Inputs (bottom center)  
    svg += r.rect(400, 200, 130, 60, C_DB9B, label="DB-9 B", sublabel="← INPUTS")
    db9b_y = 230
    
    # Pico W
    svg += r.rect(400, 320, 130, 50, C_PICO, label="Pico W", sublabel="RP2040 Control")
    pico_y = 345
    
    # Touch Pads
    svg += r.rect(400, 400, 130, 40, C_TOUCH, label="Touch Pads", sublabel="4-Point")
    touch_y = 420
    
    # Expander blocks (right)
    exp_blocks = [
        ("Noise", "Gen", 90),
        ("LFO", "Free", 140),
        ("S&H", "Sample", 190),
        ("Clock", "Div /2/4/8", 240),
        ("Slew", "Glide", 290),
        ("Atten", "CV Scale", 340),
    ]
    exp_y = {}
    for name, sub, y in exp_blocks:
        svg += r.rect(800, y, 120, 40, C_EXPAND, label=name, sublabel=sub)
        exp_y[name] = y + 20
    
    # CONNECTIONS - MicroBrute to DB-9 A (outputs)
    # These are the signals MicroBrute SENDS to DB-9 A
    svg += r.elbow(170, micro_y["VCO"], 400, db9a_y - 10, C_MICRO, "Saw/Sqr")
    svg += r.elbow(170, micro_y["VCF"], 400, db9a_y, C_MICRO, "VCF")
    svg += r.elbow(170, micro_y["LFO"], 400, db9a_y + 10, C_MICRO, "LFO")
    svg += r.elbow(170, micro_y["ENV"], 400, db9a_y + 20, C_MICRO, "Env")
    
    # CONNECTIONS - Expander to DB-9 B (inputs to MicroBrute)
    # These are the signals the Expander SENDS to DB-9 B which go TO MicroBrute
    svg += r.elbow(800, exp_y["Noise"], 530, db9b_y - 10, C_EXPAND, "Ext Audio")
    svg += r.elbow(800, exp_y["LFO"], 530, db9b_y, C_EXPAND, "Filter CV")
    svg += r.elbow(800, exp_y["S&H"], 530, db9b_y + 10, C_EXPAND, "Res CV")
    svg += r.elbow(800, exp_y["Clock"], 530, db9b_y + 20, C_EXPAND, "Sync")
    
    # CONNECTIONS - DB-9 B to MicroBrute (showing the flow)
    svg += r.elbow(400, db9b_y - 5, 170, micro_y["VCF"] + 15, C_DB9B, "→ Filter")
    svg += r.elbow(400, db9b_y + 5, 170, micro_y["VCA"] + 15, C_DB9B, "→ VCA")
    
    # CONNECTIONS - Control signals
    svg += r.elbow(530, pico_y, 800, exp_y["LFO"], C_PICO, "GPIO")
    svg += r.elbow(530, touch_y, 800, exp_y["S&H"], C_TOUCH, "Touch")
    
    # Audio Outputs section (bottom)
    svg += r.text(500, 510, "AUDIO OUTPUTS", "l", "middle", 11, C_AUDIO)
    audio_blocks = [
        ("Saw Out", 150),
        ("Sqr Out", 280),
        ("Mix Out", 410),
        ("VCF Out", 540),
        ("Main", 670),
    ]
    for label, x in audio_blocks:
        svg += r.rect(x, 530, 90, 35, C_AUDIO, label=label)
    
    # Legend
    svg += r.rect(50, 600, 900, 80, "#F5F5F5", "#999", 1)
    svg += r.text(500, 625, "Signal Flow Legend", "l", "middle", 10)
    
    items = [
        (C_MICRO, "MicroBrute internal signals"),
        (C_DB9A, "DB-9 A: Outputs TO expander"),
        (C_DB9B, "DB-9 B: Inputs FROM expander"),
        (C_EXPAND, "Expander modules"),
    ]
    for i, (c, txt) in enumerate(items):
        x = 70 + i * 220
        y = 650
        svg += f'<rect x="{x}" y="{y-8}" width="20" height="14" fill="{c}" stroke="#333" rx="2"/>\n'
        svg += r.text(x + 28, y + 4, txt, size=9)
    
    svg += r.footer()
    return svg


def audio_signal_flow():
    """Audio Signal Flow - Clean version with notes at bottom."""
    r = SVGRenderer(900, 600, "Audio Signal Flow", "VCO → Mixer → Filter → VCA → Output")
    
    C_VCO = "#E91E63"
    C_MIXER = "#FF9800" 
    C_FILTER = "#2196F3"
    C_VCA = "#4CAF50"
    C_OUT = "#9C27B0"
    
    svg = r.header()
    
    # Input sources (staggered left)
    sources = [
        ("Saw", "-5V to +5V", 60),
        ("Square", "0V to +5V", 100),
        ("Sub", "-5V to +5V", 140),
        ("Ext In", "Line Level", 180),
        ("Noise", "White", 220),
    ]
    for name, sub, y in sources:
        svg += r.rect(40, y, 90, 32, C_VCO, label=name, sublabel=sub)
    
    # Mixer (center)
    svg += r.rect(200, 130, 100, 50, C_MIXER, label="5-Input Mixer", sublabel="Passive")
    
    # Connections to mixer
    for y in [76, 116, 156, 196]:
        svg += r.elbow(130, y, 200, 155, C_VCO)
    
    # Filter
    svg += r.rect(360, 135, 100, 45, C_FILTER, label="VCF", sublabel="Steiner-Parker")
    svg += r.elbow(300, 155, 360, 157, C_MIXER, "Mix Out")
    
    # VCA
    svg += r.rect(520, 135, 100, 45, C_VCA, label="VCA", sublabel="ADSR Controlled")
    svg += r.elbow(460, 157, 520, 157, C_FILTER, "Filter Out")
    
    # Output
    svg += r.rect(680, 135, 100, 45, C_OUT, label="MAIN OUT", sublabel="Line Level")
    svg += r.elbow(620, 157, 680, 157, C_VCA)
    
    # Test points row
    svg += r.text(450, 240, "Test Points: TP94 (Saw), TP93 (Sqr), TP30 (Mix), TP19 (VCF), TP10/11 (VCA)", "v", "middle", 9)
    
    # Notes box at bottom (clear separation)
    svg += r.rect(50, 280, 800, 280, "#E8F5E9", "#4CAF50", 1)
    svg += r.text(450, 305, "Signal Flow Notes", "l", "middle", 11, "#1B5E20")
    
    notes = [
        ("Path:", "Saw/Square/Sub/Ext/Noise → Mixer → VCF → VCA → Main Out", 330),
        ("Mixer:", "Passive resistive mixer with 5 inputs, individual level controls", 355),
        ("VCF:", "Steiner-Parker 12dB/octave filter with resonance control via RP13", 380),
        ("VCA:", "ADSR envelope controls amplitude (Attack, Decay, Sustain, Release)", 405),
        ("Buffering:", "All test points have 1kΩ + TL074 buffer for safe external patching", 430),
        ("Protection:", "Current-limited outputs safe for Eurorack/modular systems", 455),
        ("TP30:", "Mix test point captures pre-filter signal", 480),
        ("TP19:", "VCF test point captures post-filter signal", 505),
        ("Output:", "Line level (-10dBV nominal) for mixers and audio interfaces", 530),
    ]
    
    for label, txt, y in notes:
        svg += r.text(70, y, label, "l", "start", 9, "#1B5E20")
        svg += r.text(130, y, txt, "v", "start", 9)
    
    svg += r.footer()
    return svg


def signal_flow_overview():
    """Signal Flow Overview - Simplified hierarchical view."""
    r = SVGRenderer(1000, 650, "Signal Flow Overview", "MicroBrute → Breakout → Expander")
    
    C_MICRO = "#2196F3"
    C_BREAKOUT = "#FF9800"
    C_DB9 = "#4CAF50"
    C_EXPAND = "#9C27B0"
    
    svg = r.header()
    
    # Section labels
    svg += r.text(150, 70, "MICROBRUTE", "l", "middle", 11, C_MICRO)
    svg += r.text(400, 70, "BREAKOUT", "l", "middle", 11, C_BREAKOUT)
    svg += r.text(650, 70, "DB-9", "l", "middle", 11, C_DB9)
    svg += r.text(850, 70, "EXPANDER", "l", "middle", 11, C_EXPAND)
    
    # MicroBrute box
    svg += r.rect(50, 90, 200, 350, "#E3F2FD", C_MICRO, 2)
    svg += r.text(150, 110, "Test Points", "l", "middle", 10)
    
    signals = [
        ("TP94 Saw", 130, "#0066CC"),
        ("TP93 Square", 155, "#0066CC"),
        ("TP30 Mix", 180, "#0066CC"),
        ("TP19 VCF", 205, "#0066CC"),
        ("TP124 Triangle", 230, "#0066CC"),
        ("TP83 Gate", 260, "#009933"),
        ("Pitch CV", 285, "#CC6600"),
        ("Envelope", 310, "#CC6600"),
        ("LFO", 335, "#CC6600"),
        ("+12V / -12V / GND", 380, "#CC0000"),
    ]
    for name, y, c in signals:
        svg += r.text(70, y, name, "v", "start", 8, c)
        svg += f'<circle cx="230" cy="{y-3}" r="3" fill="{c}"/>\n'
    
    # Breakout buffers
    svg += r.rect(300, 90, 180, 350, "#FFF3E0", C_BREAKOUT, 2)
    svg += r.text(390, 110, "Signal Processing", "l", "middle", 10)
    
    buffers = [
        ("TL074 A-D: Audio buffers", 140),
        ("TL072: Env/LFO/Triangle", 170),
        ("CD40106: Gate conditioning", 200),
        ("Direct: Pitch CV", 230),
        ("Attenuverters: CV inputs", 260),
        ("Vactrol driver: Resonance", 290),
        ("LED drivers: RGB status", 320),
        ("", 0),
        ("Power Distribution:", 370),
        ("±12V, +5V, GND", 390),
    ]
    for txt, y in buffers:
        if txt:
            svg += r.text(320, y, txt, "v", "start", 8)
    
    # DB-9 section
    svg += r.rect(520, 90, 150, 160, "#E8F5E9", C_DB9, 2)
    svg += r.text(595, 110, "DB-9 A (Outputs)", "l", "middle", 9)
    outputs = ["1: Gate", "2: Pitch", "3: Env", "4: LFO", "5: Mix", "6: VCF", "7: Saw", "8: Square"]
    for i, pin in enumerate(outputs):
        svg += r.text(540, 135 + i * 18, pin, "v", "start", 7)
    
    svg += r.rect(520, 270, 150, 170, "#FBE9E7", "#FF5722", 2)
    svg += r.text(595, 290, "DB-9 B (Inputs)", "l", "middle", 9)
    inputs = ["1: Filter CV", "2: VCA CV", "3: Resonance", "4: Sync", "5: Gate In", "6: Ext Audio", "7: +12V", "8: -12V", "9: GND"]
    for i, pin in enumerate(inputs):
        svg += r.text(540, 315 + i * 15, pin, "v", "start", 7)
    
    # Expander box
    svg += r.rect(720, 90, 250, 350, "#F3E5F5", C_EXPAND, 2)
    svg += r.text(845, 110, "Expander Modules", "l", "middle", 10)
    
    modules = [
        ("Noise Generator → Noise Out", 140),
        ("LFO → Saw Out / Filter CV", 165),
        ("Sample & Hold → Res CV", 190),
        ("Clock Divider → Gate Out", 215),
        ("Slew Limiter", 240),
        ("Attenuverters → Pitch/Env/LFO IN", 265),
        ("", 0),
        ("Output Jacks:", 300),
        ("Saw, Square, Mix, VCF, Triangle", 320),
        ("Gate Out, Pitch/Env/LFO In", 340),
        ("", 0),
        ("Eurorack Power Header", 380),
    ]
    for txt, y in modules:
        if txt:
            svg += r.text(740, y, txt, "v", "start", 8)
    
    # Connection lines (simplified bus style)
    svg += r.line(250, 250, 300, 250, "#666", 2)
    svg += r.text(275, 240, "Signals", "v", "middle", 7)
    
    svg += r.line(480, 170, 520, 170, "#666", 2)
    svg += r.text(500, 160, "To A", "v", "middle", 7)
    
    svg += r.line(480, 355, 520, 355, "#666", 2)
    svg += r.text(500, 345, "To B", "v", "middle", 7)
    
    svg += r.line(670, 170, 720, 170, "#666", 2)
    svg += r.text(695, 160, "To Exp", "v", "middle", 7)
    
    svg += r.line(670, 355, 720, 355, "#666", 2)
    svg += r.text(695, 345, "From Exp", "v", "middle", 7)
    
    # Power bus
    svg += r.line(250, 380, 770, 380, "#CC0000", 3, True)
    svg += r.text(510, 370, "Power Bus (±12V, +5V, GND)", "v", "middle", 8, "#CC0000")
    
    # Legend
    svg += r.rect(50, 470, 900, 150, "#F5F5F5", "#999", 1)
    svg += r.text(500, 495, "Signal Types", "l", "middle", 10)
    
    legend = [
        ("#0066CC", "Audio (Saw, Square, Mix, VCF)"),
        ("#009933", "Gate/Clock"),
        ("#CC6600", "CV (Pitch, Env, LFO)"),
        ("#CC0000", "Power (+12V, +5V)"),
    ]
    for i, (c, txt) in enumerate(legend):
        x = 80 + i * 220
        svg += f'<rect x="{x}" y="{520}" width="20" height="14" fill="{c}" stroke="#333" rx="2"/>\n'
        svg += r.text(x + 28, 532, txt, "v", "start", 9)
    
    svg += r.text(80, 570, "Flow: MicroBrute signals → Breakout processing → DB-9 A → Expander outputs", "v", "start", 9)
    svg += r.text(80, 590, "CV Flow: Expander outputs → DB-9 B → Breakout → MicroBrute inputs", "v", "start", 9)
    
    svg += r.footer()
    return svg


def pico_pinout_clean():
    """Pico H Pinout - Clean version with correct layout."""
    r = SVGRenderer(900, 650, "Raspberry Pi Pico H Pinout", "MACROBRUTE Hardware Configuration")
    
    svg = r.header()
    
    # Board
    bx, by, bw, bh = 250, 80, 400, 480
    svg += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#006600" stroke="#1a1a1a" stroke-width="3" rx="8"/>\n'
    
    # USB at top
    svg += f'<rect x="{bx+150}" y="{by-15}" width="100" height="20" fill="#333" stroke="#666"/>\n'
    svg += r.text(bx+200, by-3, "Micro USB", "v", "middle", 8, "#CCC")
    
    # Left side pins (GP0-GP15) - only showing used pins for clarity
    left_pins = [
        (0, "UART0 TX", "#00BCD4"),
        (1, "UART0 RX", "#00BCD4"),
        (4, "MIDI TX", "#E91E63"),
        (5, "MIDI RX", "#E91E63"),
        (8, "LED Clock", "#FF9800"),
        (9, "LED Gate", "#FF9800"),
        (10, "LED Mode", "#FF9800"),
        (12, "Tap Button", "#4CAF50"),
        (13, "Enc Button", "#4CAF50"),
        (14, "Enc CLK", "#4CAF50"),
        (15, "Enc DT", "#4CAF50"),
    ]
    
    for i, (pin, func, color) in enumerate(left_pins):
        y = by + 40 + i * 40
        svg += f'<circle cx="{bx}" cy="{y}" r="6" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+12, y+3, f"GP{pin}", "v", "start", 8, "#FFF")
        svg += f'<rect x="{bx-100}" y="{y-10}" width="85" height="20" fill="{color}" stroke="#333" rx="2"/>\n'
        svg += r.text(bx-57, y+4, func, "sl", "middle", 8)
    
    # Right side pins (GP16-GP28)
    right_pins = [
        (16, "OLED DC", "#2196F3"),
        (17, "OLED CS", "#2196F3"),
        (18, "OLED SCK", "#2196F3"),
        (19, "OLED MOSI", "#2196F3"),
        (20, "OLED RST", "#2196F3"),
        (21, "Clock In", "#9C27B0"),
        (22, "Clock Out", "#9C27B0"),
    ]
    
    for i, (pin, func, color) in enumerate(right_pins):
        y = by + 40 + i * 45
        svg += f'<circle cx="{bx+bw}" cy="{y}" r="6" fill="#C0C0C0" stroke="#666"/>\n'
        svg += r.text(bx+bw-10, y+3, f"GP{pin}", "v", "end", 8, "#FFF")
        svg += f'<rect x="{bx+bw+15}" y="{y-10}" width="75" height="20" fill="{color}" stroke="#333" rx="2"/>\n'
        svg += r.text(bx+bw+52, y+4, func, "sl", "middle", 8)
    
    # Bottom debug pins (minimal)
    svg += r.text(bx+bw/2, by+bh+20, "DEBUG: SWDIO, SWCLK, VSYS (+5V), GND", "v", "middle", 8, "#666")
    
    # Pin 1 indicator
    svg += f'<rect x="{bx+10}" y="{by+10}" width="15" height="5" fill="#FFF"/>\n'
    
    # Legend
    svg += r.rect(50, 580, 800, 60, "#F5F5F5", "#999", 1)
    legend = [
        ("#2196F3", "OLED SPI"),
        ("#4CAF50", "Buttons/Encoder"),
        ("#FF9800", "LED Outputs"),
        ("#00BCD4", "Debug UART"),
        ("#E91E63", "MIDI"),
        ("#9C27B0", "Clock I/O"),
    ]
    for i, (c, txt) in enumerate(legend):
        x = 70 + i * 130
        svg += f'<rect x="{x}" y="{595}" width="20" height="14" fill="{c}" stroke="#333" rx="2"/>\n'
        svg += r.text(x+28, 607, txt, "v", "start", 8)
    
    svg += r.footer()
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("system_architecture_clean", system_architecture),
        ("audio_signal_flow_clean", audio_signal_flow),
        ("signal_flow_overview_clean", signal_flow_overview),
        ("pico_pinout_clean", pico_pinout_clean),
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


def internal_wiring_clean():
    """Internal Wiring - Clean version."""
    r = SVGRenderer(900, 550, "Internal Wiring — MicroBrute to Breakout", "Test Point Connections")
    
    C_AUDIO = "#0066CC"
    C_CV = "#CC6600"
    C_GATE = "#009933"
    C_POS = "#CC0000"
    C_NEG = "#0000CC"
    C_GND = "#1a1a1a"
    
    svg = r.header()
    
    # Source/Dest boxes
    svg += r.rect(50, 80, 150, 400, "#E8D5A3", "#B8722D", 2)
    svg += r.text(125, 70, "MicroBrute", "l", "middle", 11)
    svg += r.text(125, 95, "Test Points", "v", "middle", 9)
    
    svg += r.rect(700, 80, 150, 400, "#C4A265", "#8B6914", 2)
    svg += r.text(775, 70, "Breakout", "l", "middle", 11)
    svg += r.text(775, 95, "Connectors", "v", "middle", 9)
    
    # Audio section
    svg += r.text(450, 120, "AUDIO OUTPUTS (1kΩ series resistors)", "l", "middle", 10, C_AUDIO)
    
    audio = [
        ("TP94 Saw", 140, "J1-1"),
        ("TP93 Square", 165, "J1-2"),
        ("TP30 Mix", 190, "J1-4"),
        ("TP19 VCF", 215, "J1-3"),
        ("TP124 Triangle", 240, "J1-5"),
    ]
    for src, y, dst in audio:
        svg += r.text(60, y, src, "v", "start", 9)
        svg += r.line(200, y-3, 700, y-3, C_AUDIO, 2)
        # Resistor symbol
        svg += f'<path d="M350,{y-3} l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5" stroke="#8B4513" stroke-width="2" fill="none"/>\n'
        svg += r.text(450, y-10, "1kΩ", "v", "middle", 7)
        svg += r.text(710, y, f"→ {dst}", "v", "start", 9)
    
    # Gate/CV section
    svg += r.text(450, 280, "GATE & CV (10kΩ series resistors)", "l", "middle", 10, C_GATE)
    
    cv = [
        ("TP83 Gate", 300, "J2-1", C_GATE),
        ("Env (matrix)", 325, "J3-1", C_CV),
        ("LFO (matrix)", 350, "J3-2", C_CV),
    ]
    for src, y, dst, color in cv:
        svg += r.text(60, y, src, "v", "start", 9)
        svg += r.line(200, y-3, 700, y-3, color, 2)
        svg += f'<path d="M350,{y-3} l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5" stroke="#8B4513" stroke-width="2" fill="none"/>\n'
        svg += r.text(450, y-10, "10kΩ", "v", "middle", 7)
        svg += r.text(710, y, f"→ {dst}", "v", "start", 9)
    
    # Power section
    svg += r.text(450, 390, "POWER (Direct connection)", "l", "middle", 10, C_POS)
    
    power = [
        ("TP70 +12V", 410, "Power header +12V", C_POS),
        ("TP71 -12V", 435, "Power header -12V", C_NEG),
        ("TP72 GND", 460, "Power header GND", C_GND),
    ]
    for src, y, dst, color in power:
        svg += r.text(60, y, src, "v", "start", 9, color)
        svg += r.line(200, y-3, 700, y-3, color, 3)
        svg += r.text(710, y, f"→ {dst}", "v", "start", 9, color)
    
    # Wire gauge note
    svg += r.text(450, 510, "Wire Gauge: Signals = 24AWG | Power = 22AWG", "v", "middle", 9)
    svg += r.text(450, 530, "All series resistors mounted on Breakout PCB for protection", "v", "middle", 8)
    
    svg += r.footer()
    return svg


# Update main to include internal wiring
def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("system_architecture_clean", system_architecture),
        ("audio_signal_flow_clean", audio_signal_flow),
        ("signal_flow_overview_clean", signal_flow_overview),
        ("pico_pinout_clean", pico_pinout_clean),
        ("internal_wiring_clean", internal_wiring_clean),
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
