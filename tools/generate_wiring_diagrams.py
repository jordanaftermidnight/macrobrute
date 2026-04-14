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


def generate_internal_wiring() -> str:
    """Internal wiring from MicroBrute test points to breakout PCB."""
    r = SchematicRenderer(700, 600, "Internal Wiring — MicroBrute to Breakout", "Test point taps and power connections")
    
    # Left side: MicroBrute PCB with test points
    r.elements.append(f'<rect x="50" y="80" width="120" height="440" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="110" y="60" class="label" text-anchor="middle">MicroBrute PCB</text>')
    r.elements.append(f'<text x="110" y="540" class="label" text-anchor="middle" font-size="9">Rear Board</text>')
    
    # Right side: Breakout PCB
    r.elements.append(f'<rect x="530" y="80" width="120" height="440" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="590" y="60" class="label" text-anchor="middle">Breakout PCB</text>')
    
    # Test point connections
    connections = [
        ("TP94 Saw", 120, 120, "J1-1", 580, 120, "1kΩ"),
        ("TP93 Square", 120, 150, "J1-2", 580, 150, "1kΩ"),
        ("TP30 Mix", 120, 180, "J1-4", 580, 180, "1kΩ"),
        ("TP19 VCF", 120, 210, "J1-3", 580, 210, "1kΩ"),
        ("TP124 Tri", 120, 240, "J1-5", 580, 240, "1kΩ"),
        ("TP83 Gate", 120, 280, "J2-1", 580, 280, "10kΩ"),
        ("Env (matrix)", 120, 320, "J3-1", 580, 320, "10kΩ"),
        ("LFO (matrix)", 120, 350, "J3-2", 580, 350, "10kΩ"),
    ]
    
    for name, x1, y1, jlabel, x2, y2, resistor in connections:
        # Test point label
        r.elements.append(f'<text x="{x1-5}" y="{y1+3}" class="value" font-size="8" text-anchor="end">{name}</text>')
        # Wire
        r.wire(Point(x1, y1), Point(x2-30, y2))
        # Resistor
        r.resistor(Point((x1+x2-30)//2, y1), value=resistor, vertical=False)
        # Continue to breakout
        r.wire(Point(x2-30, y2), Point(x2, y2))
        # Jack label
        r.elements.append(f'<text x="{x2+5}" y="{y2+3}" class="value" font-size="8">{jlabel}</text>')
    
    # Power connections section
    r.elements.append(f'<text x="110" y="410" class="label" font-size="10" fill="#D44">Power Taps</text>')
    
    power = [
        ("TP70 +12V", 120, 430, "Red", "Power header +12V"),
        ("TP71 -12V", 120, 455, "#44D", "Power header -12V"),
        ("TP72 GND", 120, 480, "#4A4", "Power header GND"),
    ]
    
    for name, x1, y1, color, dest in power:
        r.elements.append(f'<text x="{x1-5}" y="{y1+3}" class="value" font-size="8" text-anchor="end">{name}</text>')
        r.wire(Point(x1, y1), Point(500, y1))
        r.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{500}" y2="{y1}" stroke="{color}" stroke-width="2"/>')
        r.elements.append(f'<text x="{530}" y="{y1+3}" class="value" font-size="8">{dest}</text>')
    
    # Wire gauge note
    r.elements.append(f'<text x="350" y="570" class="value" text-anchor="middle">All signals: 24AWG | Power: 22AWG</text>')
    
    return r.render()


def generate_power_distribution() -> str:
    """Power distribution from MicroBrute rails to all modules."""
    r = SchematicRenderer(600, 500, "Power Distribution", "±12V from MicroBrute to Expander modules")
    
    # MicroBrute power source
    r.elements.append(f'<rect x="50" y="200" width="100" height="100" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="100" y="235" class="label" text-anchor="middle">MicroBrute</text>')
    r.elements.append(f'<text x="100" y="255" class="value" text-anchor="middle" fill="#D44">+12V TP70</text>')
    r.elements.append(f'<text x="100" y="275" class="value" text-anchor="middle" fill="#44D">-12V TP71</text>')
    r.elements.append(f'<text x="100" y="295" class="value" text-anchor="middle" fill="#4A4">GND TP72</text>')
    
    # DB-9 B power pins
    r.elements.append(f'<rect x="250" y="150" width="100" height="200" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="8"/>')
    r.elements.append(f'<text x="300" y="130" class="label" text-anchor="middle" fill="#D44">DB-9 B</text>')
    r.elements.append(f'<text x="300" y="180" class="value" text-anchor="middle" fill="#gold">Pin 7: +12V</text>')
    r.elements.append(f'<text x="300" y="250" class="value" text-anchor="middle" fill="#gold">Pin 9: GND</text>')
    r.elements.append(f'<text x="300" y="320" class="value" text-anchor="middle" fill="#gold">Pin 8: -12V</text>')
    
    # Protection components
    r.elements.append(f'<text x="380" y="175" class="value" font-size="8">Fuse + 1N5817</text>')
    r.elements.append(f'<text x="380" y="315" class="value" font-size="8">Fuse + 1N5817</text>')
    
    # Expander distribution
    r.elements.append(f'<rect x="450" y="100" width="120" height="300" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="510" y="80" class="label" text-anchor="middle">Expander Bus</text>')
    
    modules = [
        ("Noise Gen", 130),
        ("LFO", 160),
        ("S&H", 190),
        ("Clock Div", 220),
        ("Slew", 250),
        ("Atten", 280),
        ("Mult", 310),
        ("Button", 340),
    ]
    
    for name, y in modules:
        r.elements.append(f'<text x="{455}" y="{y}" class="value" font-size="8">{name}</text>')
        r.wire(Point(530, y-3), Point(550, y-3))
        r.wire(Point(550, y-3), Point(550, 250))
        # Power rails horizontal
        r.elements.append(f'<line x1="{550}" y1="{y-3}" x2="{570}" y2="{y-3}" stroke="#D44" stroke-width="1.5"/>')
    
    # Power rail lines
    r.elements.append(f'<line x1="530" y1="115" x2="570" y2="115" stroke="#D44" stroke-width="2"/>')
    r.elements.append(f'<text x="{575}" y="{118}" class="value" font-size="7" fill="#D44">+12V</text>')
    r.elements.append(f'<line x1="530" y1="250" x2="570" y2="250" stroke="#4A4" stroke-width="2"/>')
    r.elements.append(f'<text x="{575}" y="{253}" class="value" font-size="7" fill="#4A4">GND</text>')
    r.elements.append(f'<line x1="530" y1="385" x2="570" y2="385" stroke="#44D" stroke-width="2"/>')
    r.elements.append(f'<text x="{575}" y="{388}" class="value" font-size="7" fill="#44D">-12V</text>')
    
    # Connections from MicroBrute to DB-9
    r.wire(Point(150, 230), Point(250, 230))
    r.elements.append(f'<line x1="150" y1="230" x2="250" y2="230" stroke="#D44" stroke-width="2"/>')
    r.wire(Point(150, 250), Point(250, 250))
    r.elements.append(f'<line x1="150" y1="250" x2="250" y2="250" stroke="#4A4" stroke-width="2"/>')
    r.wire(Point(150, 270), Point(250, 270))
    r.elements.append(f'<line x1="150" y1="270" x2="250" y2="270" stroke="#44D" stroke-width="2"/>')
    
    # DB-9 to Expander
    r.wire(Point(350, 180), Point(450, 115))
    r.wire(Point(350, 250), Point(450, 250))
    r.wire(Point(350, 320), Point(450, 385))
    
    return r.render()


def generate_output_buffer() -> str:
    """TL074 output buffer board schematic."""
    r = SchematicRenderer(600, 500, "Output Buffer Board", "TL074 #1 — 4-channel unity gain buffer")
    
    # TL074 quad opamp
    r.elements.append(f'<rect x="200" y="100" width="200" height="300" fill="#2D2D2D" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
    r.elements.append(f'<text x="300" y="130" class="label" text-anchor="middle" fill="#FFF">TL074</text>')
    r.elements.append(f'<text x="300" y="150" class="value" text-anchor="middle" fill="#DDD">Quad Opamp</text>')
    
    # 4 channels
    channels = [
        ("Saw (TP94)", 180, 1),
        ("Square (TP93)", 220, 2),
        ("Mix (TP30)", 260, 3),
        ("VCF (TP19)", 300, 4),
    ]
    
    for name, y, ch in channels:
        # Input from test point
        r.elements.append(f'<text x="50" y="{y+3}" class="value" font-size="9">{name}</text>')
        r.wire(Point(100, y), Point(150, y))
        r.resistor(Point(125, y), value="1kΩ", vertical=False)
        r.wire(Point(150, y), Point(200, y))
        
        # Opamp symbol inside
        r.elements.append(f'<polygon points="200,{y-15} 200,{y+15} 240,{y}" fill="none" stroke="#FFF" stroke-width="1.5"/>')
        r.elements.append(f'<text x="{215}" y="{y+3}" class="value" fill="#FFF" font-size="8">{ch}</text>')
        
        # Feedback (unity gain)
        r.wire(Point(240, y), Point(260, y))
        r.wire(Point(260, y), Point(260, y-30))
        r.wire(Point(260, y-30), Point(220, y-30))
        r.wire(Point(220, y-30), Point(220, y-10))
        
        # Output to DB-9
        r.wire(Point(240, y), Point(280, y))
        r.wire(Point(280, y), Point(400, y))
        r.elements.append(f'<text x="{410}" y="{y+3}" class="value" font-size="9">DB-9 A Pin {6+ch}</text>')
    
    # Power pins
    r.vcc(Point(250, 420), label="V+ +12V")
    r.vcc(Point(350, 420), label="V- -12V")
    
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
