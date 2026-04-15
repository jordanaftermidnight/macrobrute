#!/usr/bin/env python3
"""Generate focused system diagrams for MACROBRUTE wiring sections.

These are simpler, section-specific diagrams to replace ASCII art in wiring_diagram.md

Usage: python3 tools/generate_wiring_diagrams.py
Output: schematics/wiring_*.svg
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from tools.generate_schematics import SchematicRenderer, Point


# Color scheme for signal types
C_AUDIO = "#0066CC"      # Blue - Audio outputs (Saw, Sqr, Mix, VCF)
C_CV = "#CC6600"         # Orange - CV signals (Pitch, Env, LFO)
C_GATE = "#009933"       # Green - Gate/Clock
C_POWER_POS = "#CC0000"  # Red - +12V
C_POWER_NEG = "#0000CC"  # Dark Blue - -12V
C_GND = "#1a1a1a"        # Black - GND
C_CONTROL = "#6600CC"    # Purple - Control signals


def elbow_hv(x1, y1, x2, y2, corner_x=None, stroke_color="#1a1a1a", stroke_width=1.5):
    """Generate horizontal-then-vertical elbow wire path.
    
    Args:
        x1, y1: Start point
        x2, y2: End point
        corner_x: X-coordinate of corner (defaults to 70% of distance)
        stroke_color: Wire color
        stroke_width: Wire thickness
    """
    if corner_x is None:
        corner_x = x1 + (x2 - x1) * 0.7
    
    path = f'M{x1},{y1} L{corner_x},{y1} L{corner_x},{y2} L{x2},{y2}'
    return f'<path d="{path}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="none"/>'


def elbow_vh(x1, y1, x2, y2, corner_y=None, stroke_color="#1a1a1a", stroke_width=1.5):
    """Generate vertical-then-horizontal elbow wire path."""
    if corner_y is None:
        corner_y = y1 + (y2 - y1) * 0.7
    
    path = f'M{x1},{y1} L{x1},{corner_y} L{x2},{corner_y} L{x2},{y2}'
    return f'<path d="{path}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="none"/>'


def legend_item(x, y, color, label):
    """Generate legend entry with color swatch."""
    return [
        f'<rect x="{x}" y="{y-8}" width="20" height="10" fill="{color}" stroke="#333" stroke-width="0.5"/>',
        f'<text x="{x+25}" y="{y}" class="value" font-size="9">{label}</text>'
    ]


def generate_internal_wiring() -> str:
    """Internal wiring from MicroBrute test points to breakout PCB with elbow routing and color coding."""
    
    # Color scheme
    C_AUDIO = "#0066CC"      # Blue - Audio outputs
    C_CV = "#CC6600"         # Orange - CV signals  
    C_GATE = "#009933"       # Green - Gate
    C_POWER_POS = "#CC0000"  # Red - +12V
    C_POWER_NEG = "#0000CC"  # Dark Blue - -12V
    C_GND = "#1a1a1a"        # Black - GND
    
    r = SchematicRenderer(800, 650, "Internal Wiring — MicroBrute to Breakout", "Test point taps with elbow routing")
    
    # === LEGEND ===
    r.elements.append(f'<text x="550" y="30" class="label" font-size="10">Signal Groups:</text>')
    legend_items = [
        (C_AUDIO, "Audio (Saw, Square, Mix, VCF, Tri)"),
        (C_CV, "CV (Pitch, Env, LFO)"),
        (C_GATE, "Gate"),
        (C_POWER_POS, "+12V"),
        (C_POWER_NEG, "-12V"),
        (C_GND, "GND"),
    ]
    for i, (color, label) in enumerate(legend_items):
        y_pos = 45 + i * 15
        r.elements.append(f'<rect x="550" y="{y_pos-6}" width="15" height="8" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="570" y="{y_pos}" class="value" font-size="8">{label}</text>')
    
    # === DIRECTION HEADER ===
    r.elements.append(f'<text x="400" y="65" class="label" text-anchor="middle" font-size="11">Signal Flow: MicroBrute → Breakout</text>')
    r.elements.append(f'<text x="400" y="78" class="value" text-anchor="middle" font-size="8">All signals tap from MicroBrute rear board test points to Breakout PCB</text>')
    
    # === MICROBRUTE PCB (Left) ===
    r.elements.append(f'<rect x="50" y="90" width="140" height="510" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="120" y="85" class="label" text-anchor="middle">FROM: MicroBrute PCB</text>')
    r.elements.append(f'<text x="120" y="615" class="value" text-anchor="middle" font-size="9">Rear Board Test Points</text>')
    
    # === BREAKOUT PCB (Right) ===
    r.elements.append(f'<rect x="610" y="90" width="140" height="510" fill="#C4A265" stroke="#8B6914" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="680" y="85" class="label" text-anchor="middle">TO: Breakout PCB</text>')
    
    # === AUDIO OUTPUTS GROUP (Rows 100-180) ===
    r.elements.append(f'<rect x="40" y="90" width="720" height="100" fill="#E3F2FD" stroke="#0066CC" stroke-width="1" stroke-dasharray="5,3" opacity="0.3"/>')
    r.elements.append(f'<text x="60" y="105" class="label" font-size="9" fill="{C_AUDIO}">AUDIO OUTPUTS</text>')
    
    audio_signals = [
        ("TP94 Saw", 130, "J1-1", "1kΩ", C_AUDIO),
        ("TP93 Square", 155, "J1-2", "1kΩ", C_AUDIO),
        ("TP30 Mix", 180, "J1-4", "1kΩ", C_AUDIO),
    ]
    
    for name, y, jlabel, resistor, color in audio_signals:
        # Source label
        r.elements.append(f'<text x="{55}" y="{y+3}" class="value" font-size="9" text-anchor="end">{name}</text>')
        
        # Wire path: from MicroBrute to Breakout with direction arrow
        corner_x = 350
        # Horizontal: TP to corner, Vertical: adjust if needed, Horizontal: corner to destination
        path = f'M190,{y} L{corner_x},{y} L{corner_x},{y} L{600},{y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        
        # Resistor inline
        r.resistor(Point(270, y), value=resistor, vertical=False)
        
        # Destination label
        r.elements.append(f'<text x="{615}" y="{y+3}" class="value" font-size="9">→ {jlabel}</text>')
    
    # === VCF GROUP ===
    vcf_signals = [
        ("TP19 VCF", 210, "J1-3", "1kΩ", C_AUDIO),
        ("TP124 Triangle", 235, "J1-5", "1kΩ", C_AUDIO),
    ]
    
    for name, y, jlabel, resistor, color in vcf_signals:
        r.elements.append(f'<text x="{55}" y="{y+3}" class="value" font-size="9" text-anchor="end">{name}</text>')
        corner_x = 350
        path = f'M190,{y} L{corner_x},{y} L{corner_x},{y} L{600},{y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        r.resistor(Point(270, y), value=resistor, vertical=False)
        r.elements.append(f'<text x="{615}" y="{y+3}" class="value" font-size="9">→ {jlabel}</text>')
    
    # === GATE & CV GROUP (Rows 260-340) ===
    r.elements.append(f'<rect x="40" y="250" width="720" height="110" fill="#E8F5E9" stroke="#009933" stroke-width="1" stroke-dasharray="5,3" opacity="0.3"/>')
    r.elements.append(f'<text x="60" y="265" class="label" font-size="9" fill="{C_GATE}">GATE & MODULATION</text>')
    
    cv_signals = [
        ("TP83 Gate", 280, "J2-1", "10kΩ", C_GATE),
        ("Env (matrix)", 310, "J3-1", "10kΩ", C_CV),
        ("LFO (matrix)", 335, "J3-2", "10kΩ", C_CV),
    ]
    
    for name, y, jlabel, resistor, color in cv_signals:
        r.elements.append(f'<text x="{55}" y="{y+3}" class="value" font-size="9" text-anchor="end">{name}</text>')
        corner_x = 350
        path = f'M190,{y} L{corner_x},{y} L{corner_x},{y} L{600},{y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        r.resistor(Point(270, y), value=resistor, vertical=False)
        r.elements.append(f'<text x="{615}" y="{y+3}" class="value" font-size="9">→ {jlabel}</text>')
    
    # === POWER GROUP (Rows 380-480) ===
    r.elements.append(f'<rect x="40" y="370" width="720" height="130" fill="#FFEBEE" stroke="#CC0000" stroke-width="1" stroke-dasharray="5,3" opacity="0.3"/>')
    r.elements.append(f'<text x="60" y="385" class="label" font-size="9" fill="{C_POWER_POS}">POWER TAPS</text>')
    
    power_signals = [
        ("TP70 +12V", 410, C_POWER_POS, "Power header +12V"),
        ("TP71 -12V", 445, C_POWER_NEG, "Power header -12V"),
        ("TP72 GND", 480, C_GND, "Power header GND"),
    ]
    
    for name, y, color, dest in power_signals:
        r.elements.append(f'<text x="{55}" y="{y+3}" class="value" font-size="9" text-anchor="end" fill="{color}">{name}</text>')
        
        # Thicker wires for power with arrow
        corner_x = 350
        path = f'M190,{y} L{corner_x},{y} L{corner_x},{y} L{600},{y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="3.5" fill="none" marker-end="url(#arrow)"/>')
        
        r.elements.append(f'<text x="{615}" y="{y+3}" class="value" font-size="9" fill="{color}">→ {dest}</text>')
    
    # === NOTES ===
    r.elements.append(f'<text x="400" y="580" class="value" text-anchor="middle" font-size="10">Wire Gauge: Signals = 24AWG | Power = 22AWG</text>')
    r.elements.append(f'<text x="400" y="600" class="value" text-anchor="middle" font-size="9">All series resistors mounted on Breakout PCB for protection</text>')
    
    return r.render()


def generate_power_distribution() -> str:
    """Power distribution with bus bars, color coding, and elbow routing."""
    
    C_PLUS_12V = "#CC0000"  # Red
    C_MINUS_12V = "#0000CC"  # Dark Blue  
    C_GND = "#228B22"       # Green
    C_FUSE = "#FF6600"      # Orange
    
    r = SchematicRenderer(900, 600, "Power Distribution System", "±12V Rails from MicroBrute to All Modules")
    
    # === LEGEND ===
    r.elements.append(f'<text x="700" y="30" class="label" font-size="10">Power System Legend:</text>')
    legend = [
        (C_PLUS_12V, "+12V Rail"),
        (C_MINUS_12V, "-12V Rail"),
        (C_GND, "GND Rail"),
        (C_FUSE, "Fuse + Protection Diode"),
    ]
    for i, (color, label) in enumerate(legend):
        y = 45 + i * 18
        r.elements.append(f'<rect x="700" y="{y-6}" width="20" height="10" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="725" y="{y+2}" class="value" font-size="9">{label}</text>')
    
    # === SOURCE: MICROBRUTE ===
    r.elements.append(f'<rect x="50" y="200" width="120" height="180" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="110" y="220" class="label" text-anchor="middle">MICROBRUTE</text>')
    r.elements.append(f'<text x="110" y="240" class="value" text-anchor="middle" font-size="9">Power Source</text>')
    
    # Power taps from MicroBrute
    sources = [
        ("TP70 +12V", 270, C_PLUS_12V),
        ("TP72 GND", 290, C_GND),
        ("TP71 -12V", 310, C_MINUS_12V),
    ]
    
    for label, y, color in sources:
        r.elements.append(f'<text x="70" y="{y}" class="value" font-size="9" fill="{color}">{label}</text>')
    
    # === INTERCONNECT: DB-9 B ===
    r.elements.append(f'<rect x="300" y="150" width="100" height="280" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="8"/>')
    r.elements.append(f'<text x="350" y="130" class="label" text-anchor="middle" fill="#FFF">DB-9 B</text>')
    r.elements.append(f'<text x="350" y="145" class="value" text-anchor="middle" fill="#DDD" font-size="8">Rear Panel</text>')
    
    # DB-9 pins with positions
    db9_pins = [
        ("7", "+12V", 180, C_PLUS_12V),
        ("9", "GND", 250, C_GND),
        ("8", "-12V", 320, C_MINUS_12V),
    ]
    
    for pin, label, y, color in db9_pins:
        r.elements.append(f'<circle cx="350" cy="{y}" r="5" fill="#gold" stroke="#B8860B" stroke-width="1"/>')
        r.elements.append(f'<text x="365" y="{y+3}" class="value" font-size="8" fill="#gold">{pin}:{label}</text>')
    
    # Protection blocks
    for pin, label, y, color in db9_pins:
        if label != "GND":
            r.elements.append(f'<rect x="420" y="{y-10}" width="70" height="20" fill="#FFF8E1" stroke="{C_FUSE}" stroke-width="1.5" rx="2"/>')
            r.elements.append(f'<text x="455" y="{y+4}" class="value" font-size="7" text-anchor="middle" fill="{C_FUSE}">Fuse+1N5817</text>')
    
    # === DESTINATION: EXPANDER BUS ===
    r.elements.append(f'<rect x="550" y="100" width="280" height="400" fill="#F5F5F5" stroke="#666" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="690" y="85" class="label" text-anchor="middle">EXPANDER MODULES</text>')
    
    # Bus bars (thick horizontal lines)
    bus_y_positions = {
        '+12V': 140,
        'GND': 300,
        '-12V': 460
    }
    
    # Draw bus bars
    r.elements.append(f'<rect x="560" y="{bus_y_positions["+12V"]-8}" width="260" height="16" fill="{C_PLUS_12V}" rx="2"/>')
    r.elements.append(f'<text x="570" y="{bus_y_positions["+12V"]+4}" class="label" font-size="10" fill="#FFF">+12V BUS</text>')
    
    r.elements.append(f'<rect x="560" y="{bus_y_positions["GND"]-8}" width="260" height="16" fill="{C_GND}" rx="2"/>')
    r.elements.append(f'<text x="570" y="{bus_y_positions["GND"]+4}" class="label" font-size="10" fill="#FFF">GND BUS</text>')
    
    r.elements.append(f'<rect x="560" y="{bus_y_positions["-12V"]-8}" width="260" height="16" fill="{C_MINUS_12V}" rx="2"/>')
    r.elements.append(f'<text x="570" y="{bus_y_positions["-12V"]+4}" class="label" font-size="10" fill="#FFF">-12V BUS</text>')
    
    # Module tap points
    modules = [
        ("Noise Gen", 180),
        ("LFO", 210),
        ("S&H", 240),
        ("Clock /2/4/8", 270),
        ("Slew Limiter", 340),
        ("Attenuverter", 370),
        ("Mult", 400),
        ("Manual Gate", 430),
    ]
    
    for name, y in modules:
        # Module block
        r.elements.append(f'<rect x="620" y="{y-12}" width="140" height="24" fill="#E8D5A3" stroke="#B8722D" stroke-width="1" rx="2"/>')
        r.elements.append(f'<text x="690" y="{y+4}" class="label" font-size="9" text-anchor="middle">{name}</text>')
        
        # Tap lines from each bus (elbow routing)
        for bus_name, bus_y, color in [('+12V', bus_y_positions['+12V'], C_PLUS_12V), 
                                       ('GND', bus_y_positions['GND'], C_GND),
                                       ('-12V', bus_y_positions['-12V'], C_MINUS_12V)]:
            # Vertical from bus to module, then horizontal
            corner_y = y
            path = f'M600,{bus_y} L600,{corner_y} L620,{corner_y}'
            r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="{2.5 if bus_name == "GND" else 2}" fill="none"/>')
    
    # === WIRING: Source → DB-9 ===
    for pin, label, y, color in db9_pins:
        source_y = {'+12V': 270, 'GND': 290, '-12V': 310}[label]
        # Elbow: right from source, down to DB-9 pin
        corner_x = 220
        path = f'M170,{source_y} L{corner_x},{source_y} L{corner_x},{y} L{300},{y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="3" fill="none"/>')
    
    # === WIRING: DB-9 → Expander ===
    for pin, label, y, color in db9_pins:
        target_y = bus_y_positions[label]
        if label != "GND":
            # Through protection block
            corner_x = 510
            path = f'M400,{y} L{corner_x},{y} L{corner_x},{target_y} L{560},{target_y}'
        else:
            # Direct to GND bus
            corner_x = 480
            path = f'M400,{y} L{corner_x},{y} L{corner_x},{target_y} L{560},{target_y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="3" fill="none"/>')
    
    # === +5V REGULATOR SECTION ===
    r.elements.append(f'<rect x="580" y="490" width="220" height="80" fill="#FFF3E0" stroke="#E65100" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="690" y="510" class="label" font-size="10" fill="#E65100">+5V Regulator (for CD4024)</text>')
    
    # 78L05 symbol
    r.elements.append(f'<rect x="650" y="530" width="80" height="30" fill="#2D2D2D" rx="2"/>')
    r.elements.append(f'<text x="690" y="550" class="label" text-anchor="middle" fill="#FFF" font-size="9">78L05</text>')
    
    # Connections to 78L05
    r.elements.append(f'<text x="590" y="545" class="value" font-size="8">+12V in</text>')
    r.elements.append(f'<path d="M650,545 L620,545 L620,300 L600,300" stroke="{C_PLUS_12V}" stroke-width="2" fill="none"/>')
    
    r.elements.append(f'<text x="740" y="545" class="value" font-size="8">+5V out</text>')
    r.elements.append(f'<text x="760" y="555" class="value" font-size="7" fill="#E65100">→CD4024</text>')
    
    r.elements.append(f'<text x="690" y="575" class="value" font-size="8" text-anchor="middle">GND</text>')
    r.elements.append(f'<path d="M690,560 L690,580 L600,580 L600,300" stroke="{C_GND}" stroke-width="2" fill="none"/>')
    
    return r.render()


def generate_output_buffer() -> str:
    """TL074 output buffer board schematic with 5 channels (including 2x gain triangle buffer)."""
    r = SchematicRenderer(700, 600, "Output Buffer Board", "TL074 #1 — 5-Channel Buffer (4× Unity + 1× 2x Gain)")
    
    # TL074 quad opamp (we'll use 4 of 4 channels, need 2nd TL074 for 5th channel)
    r.elements.append(f'<rect x="200" y="80" width="200" height="420" fill="#2D2D2D" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="300" y="105" class="label" text-anchor="middle" fill="#FFF">TL074 #1</text>')
    r.elements.append(f'<text x="300" y="125" class="value" text-anchor="middle" fill="#DDD">4-Channel Buffer</text>')
    
    # === CHANNELS 1-4: Unity Gain Buffers ===
    channels = [
        ("Saw (TP94)", 160, 1, "7", "1kΩ", "Unity"),
        ("Square (TP93)", 210, 2, "8", "1kΩ", "Unity"),
        ("Mix (TP30)", 260, 3, "5", "1kΩ", "Unity"),
        ("VCF (TP19)", 310, 4, "6", "1kΩ", "Unity"),
    ]
    
    for name, y, ch, db9_pin, resistor, gain in channels:
        # Input from test point
        r.elements.append(f'<text x="30" y="{y+3}" class="value" font-size="9">{name}</text>')
        r.wire(Point(80, y), Point(150, y))
        r.resistor(Point(115, y), value=resistor, vertical=False)
        r.wire(Point(150, y), Point(200, y))
        
        # Opamp symbol inside
        r.elements.append(f'<polygon points="200,{y-18} 200,{y+18} 250,{y}" fill="none" stroke="#FFF" stroke-width="1.5"/>')
        r.elements.append(f'<text x="{225}" y="{y+4}" class="value" fill="#FFF" font-size="9">{ch}×1</text>')
        
        # Feedback (unity gain: output directly to -in)
        r.wire(Point(250, y), Point(270, y))
        r.wire(Point(270, y), Point(270, y-35))
        r.wire(Point(270, y-35), Point(220, y-35))
        r.wire(Point(220, y-35), Point(220, y-12))
        
        # Output to DB-9
        r.wire(Point(250, y), Point(300, y))
        r.wire(Point(300, y), Point(500, y))
        r.elements.append(f'<text x="{510}" y="{y+3}" class="value" font-size="9">DB-9 A Pin {db9_pin}</text>')
    
    # === CHANNEL 5: Triangle Buffer with 2x Gain (New Discoveries Fix) ===
    y_tri = 380
    r.elements.append(f'<text x="30" y="{y_tri+3}" class="value" font-size="9" fill="#0066CC">TP124 Triangle (2× Gain)</text>')
    
    # Input with protection resistor
    r.wire(Point(80, y_tri), Point(140, y_tri))
    r.resistor(Point(110, y_tri), value="1kΩ", vertical=False)
    r.wire(Point(140, y_tri), Point(200, y_tri))
    
    # Opamp with 2x gain configuration
    r.elements.append(f'<polygon points="200,{y_tri-20} 200,{y_tri+20} 260,{y_tri}" fill="none" stroke="#00BCD4" stroke-width="2"/>')
    r.elements.append(f'<text x="{230}" y="{y_tri+4}" class="value" fill="#00BCD4" font-size="9" font-weight="bold">5×2</text>')
    
    # Non-inverting 2x gain: Rg (to GND) = 10k, Rf = 10k
    # +in is at input, -in has Rg to GND and Rf feedback
    
    # +in connection (pin 3 equivalent for this channel - using TL074 channel D)
    r.wire(Point(200, y_tri), Point(180, y_tri))  # From input to +in
    
    # -in (pin 2 equivalent) connections
    r.wire(Point(200, y_tri-20), Point(180, y_tri-20))  # -in pin
    
    # Rg to GND (10k)
    r.wire(Point(180, y_tri-20), Point(180, y_tri-60))
    r.resistor(Point(180, y_tri-40), value="10kΩ", vertical=True)
    r.ground(Point(180, y_tri-65))
    
    # Rf feedback (10k for 2x gain: Gain = 1 + Rf/Rg = 1 + 10k/10k = 2)
    r.wire(Point(260, y_tri), Point(290, y_tri))  # Output
    r.wire(Point(290, y_tri), Point(290, y_tri-40))
    r.wire(Point(290, y_tri-40), Point(210, y_tri-40))
    r.wire(Point(210, y_tri-40), Point(210, y_tri-20))
    r.resistor(Point(250, y_tri-40), value="10kΩ", vertical=False)
    
    # Output
    r.wire(Point(290, y_tri), Point(500, y_tri))
    r.elements.append(f'<text x="{510}" y="{y_tri+3}" class="value" font-size="9">DB-9 A Pin 9 (Triangle)</text>')
    
    # === ANNOTATION BOX ===
    r.elements.append(f'<rect x="30" y="450" width="640" height="110" fill="#E3F2FD" stroke="#0066CC" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="350" y="475" class="label" text-anchor="middle" fill="#0066CC">New Discoveries Fix — Channel 5 (Triangle)</text>')
    r.elements.append(f'<text x="350" y="495" class="value" text-anchor="middle" font-size="9">TP124 triangle output is ~50% quieter than other waveforms (confirmed finding)</text>')
    r.elements.append(f'<text x="350" y="512" class="value" text-anchor="middle" font-size="9">Solution: Non-inverting amplifier with 2× gain (Rf = Rg = 10kΩ)</text>')
    r.elements.append(f'<text x="350" y="529" class="value" text-anchor="middle" font-size="9">Reference: docs/research/additional_mods_findings.md — Triangle Output Level Problem</text>')
    r.elements.append(f'<text x="350" y="548" class="value" text-anchor="middle" font-size="9">Note: Blue highlight indicates modified channel; standard channels in white</text>')
    
    # Power pins
    r.vcc(Point(250, 580), label="V+ +12V")
    r.ground(Point(300, 580))
    r.vcc(Point(350, 580), label="V- -12V")
    
    return r.render()


def generate_gate_buffer() -> str:
    """CD40106 Schmitt trigger gate buffer."""
    r = SchematicRenderer(500, 400, "Gate Buffer", "CD40106 Schmitt Trigger")
    
    # Input
    r.jack(Point(50, 150), label="TP83 Gate")
    r.wire(Point(70, 150), Point(100, 150))
    r.resistor(Point(85, 150), value="10kΩ", vertical=False)
    r.wire(Point(100, 150), Point(130, 150))
    
    # CD40106 hex inverter (using one gate as Schmitt buffer)
    r.elements.append(f'<rect x="150" y="100" width="80" height="100" fill="#2D2D2D" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="190" y="125" class="label" text-anchor="middle" fill="#FFF">CD40106</text>')
    r.elements.append(f'<text x="190" y="145" class="value" text-anchor="middle" fill="#DDD">Schmitt</text>')
    
    # Schmitt symbol
    r.elements.append(f'<polygon points="160,130 160,170 200,150" fill="none" stroke="#FFF" stroke-width="1.5"/>')
    r.elements.append(f'<circle cx="{205}" cy="150" r="3" fill="none" stroke="#FFF" stroke-width="1.5"/>')  # Inversion bubble
    
    r.wire(Point(130, 150), Point(160, 150))
    r.wire(Point(205, 150), Point(250, 150))
    
    # Output to DB-9
    r.wire(Point(250, 150), Point(350, 150))
    r.elements.append(f'<text x="{360}" y="153" class="value" font-size="9">DB-9 A Pin 1</text>')
    
    # Power
    r.vcc(Point(190, 80), label="+12V")
    r.ground(Point(190, 220))
    
    # Notes
    r.elements.append(f'<text x="250" y="280" class="value" text-anchor="middle">Schmitt trigger cleans up gate edges</text>')
    r.elements.append(f'<text x="250" y="300" class="value" text-anchor="middle">Output: 0V/+12V compatible with Eurorack</text>')
    
    return r.render()


def generate_vactrol_driver() -> str:
    """Vactrol driver for resonance CV control."""
    r = SchematicRenderer(550, 450, "Vactrol Driver", "LED Current Control for Resonance CV")
    
    # Input from DB-9 B
    r.elements.append(f'<text x="50" y="80" class="label">From DB-9 B Pin 3</text>')
    r.wire(Point(80, 100), Point(130, 100))
    
    # Attenuator pot
    r.potentiometer(Point(160, 100), label="ATTEN", value="100k")
    r.wire(Point(160, 70), Point(160, 50))
    r.ground(Point(160, 50))
    
    # Opamp buffer
    r.opamp(Point(250, 150), label="TL072", pins=("-", "+", "out"))
    r.wire(Point(160, 100), Point(210, 148))  # Wiper to +in
    r.wire(Point(210, 152), Point(210, 250))
    r.ground(Point(210, 250))
    
    # Current limiting resistor
    r.wire(Point(290, 150), Point(330, 150))
    r.resistor(Point(355, 150), label="Rlim", value="1kΩ", vertical=False)
    r.wire(Point(380, 150), Point(420, 150))
    
    # Vactrol LED
    r.elements.append(f'<text x="{440}" y="140" class="label">Vactrol</text>')
    r.elements.append(f'<text x="{440}" y="155" class="value" font-size="9">LED (RP13)</text>')
    
    # LED symbol
    r.elements.append(f'<polygon points="430,140 430,160 450,150" fill="#D44" stroke="#333" stroke-width="1"/>')
    r.elements.append(f'<line x1="{450}" y1="{140}" x2="{450}" y2="{160}" stroke="#333" stroke-width="2"/>')
    
    # To MicroBrute RP13
    r.wire(Point(450, 150), Point(480, 150))
    r.elements.append(f'<text x="{490}" y="153" class="value" font-size="9">→ RP13</text>')
    
    # Notes
    r.elements.append(f'<text x="275" y="320" class="value" text-anchor="middle">1kΩ limits LED current to ~5mA at full CV</text>')
    r.elements.append(f'<text x="275" y="340" class="value" text-anchor="middle">Buffer ensures CV source sees high impedance</text>')
    
    return r.render()


def generate_cv_input_protection() -> str:
    """CV input protection with BAT54S clamping."""
    r = SchematicRenderer(550, 500, "CV Input Protection", "BAT54S Schottky Clamping for DB-9 B Inputs")
    
    # Input jack
    r.jack(Point(50, 150), label="CV IN")
    r.wire(Point(70, 150), Point(120, 150))
    r.resistor(Point(95, 150), value="100kΩ", vertical=False)
    
    # Attenuator pot
    r.potentiometer(Point(180, 150), label="ATTEN", value="100k")
    r.wire(Point(180, 120), Point(180, 100))
    r.ground(Point(180, 100))
    
    # Series resistor to protection
    r.wire(Point(180, 180), Point(220, 180))
    r.resistor(Point(250, 180), label="Rs", value="10kΩ", vertical=False)
    r.wire(Point(280, 180), Point(320, 180))
    r.junction(Point(320, 180))
    
    # BAT54S protection
    r.elements.append(f'<text x="{350}" y="{140}" class="label">BAT54S</text>')
    r.elements.append(f'<text x="{350}" y="{155}" class="value" font-size="9">Dual Schottky</text>')
    
    # Diode to +5V (anode at signal, cathode at +5V)
    r.wire(Point(320, 180), Point(320, 120))
    r.elements.extend([
        f'<polygon points="310,110 310,130 330,120" fill="none" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="330" y1="110" x2="330" y2="130" stroke="#333" stroke-width="1.5"/>',
    ])
    r.wire(Point(320, 110), Point(320, 80))
    r.elements.append(f'<text x="{330}" y="{85}" class="value" fill="#D84">+5V</text>')
    
    # Diode to GND (cathode at signal, anode at GND)
    r.wire(Point(320, 180), Point(320, 240))
    r.elements.extend([
        f'<polygon points="330,230 330,250 310,240" fill="none" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="310" y1="230" x2="310" y2="250" stroke="#333" stroke-width="1.5"/>',
    ])
    r.wire(Point(320, 250), Point(320, 280))
    r.ground(Point(320, 280))
    
    # Output to MicroBrute
    r.wire(Point(320, 180), Point(400, 180))
    r.elements.append(f'<text x="{410}" y="{183}" class="value" font-size="9">→ MicroBrute</text>')
    
    # Protection notes
    r.elements.append(f'<text x="275" y="{350}" class="value" text-anchor="middle">Clamps input to -0.3V / +5.3V</text>')
    r.elements.append(f'<text x="275" y="{370}" class="value" text-anchor="middle">Protects MicroBrute from overvoltage</text>')
    
    return r.render()


def main():
    """Generate all wiring section diagrams."""
    os.makedirs("schematics", exist_ok=True)
    
    diagrams = [
        ("wiring_internal.svg", generate_internal_wiring),
        ("wiring_power_distribution.svg", generate_power_distribution),
        ("wiring_output_buffer.svg", generate_output_buffer),
        ("wiring_gate_buffer.svg", generate_gate_buffer),
        ("wiring_vactrol_driver.svg", generate_vactrol_driver),
        ("wiring_cv_protection.svg", generate_cv_input_protection),
    ]
    
    for filename, generator in diagrams:
        filepath = f"schematics/{filename}"
        try:
            with open(filepath, 'w') as f:
                f.write(generator())
            print(f"Generated: {filepath}")
        except Exception as e:
            print(f"Error generating {filepath}: {e}")
    
    print("\nDone. Regenerate with: python3 tools/generate_wiring_diagrams.py")


if __name__ == "__main__":
    main()
