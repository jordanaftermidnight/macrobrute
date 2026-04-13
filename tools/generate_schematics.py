#!/usr/bin/env python3
"""Generate high-quality SVG circuit schematics for MACROBRUTE.

Features:
- Traditional electronic symbols (IEC/ANSI style)
- Proper component spacing and alignment
- Clear signal flow visualization
- Professional schematic styling

Usage: python3 tools/generate_schematics.py
Output: schematics/*_schematic.svg
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Point:
    """2D point for schematic coordinates."""
    x: float
    y: float
    
    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)


class SchematicRenderer:
    """Renders electronic schematics to SVG."""
    
    # Colors
    C_BG = "#FEFEFE"
    C_WIRE = "#1a1a1a"
    C_COMPONENT = "#1a1a1a"
    C_TEXT = "#1a1a1a"
    C_TEXT_LIGHT = "#555"
    C_ANNOTATION = "#0066CC"
    C_POWER_POS = "#D44"
    C_POWER_NEG = "#44D"
    C_GROUND = "#4A4"
    
    def __init__(self, width: int, height: int, title: str, subtitle: str = ""):
        self.width = width
        self.height = height
        self.title = title
        self.subtitle = subtitle
        self.elements: List[str] = []
        
    def _svg_header(self) -> str:
        """Generate SVG header with styles."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
<defs>
  <style>
    .title {{ font: bold 16px "SF Mono", Consolas, monospace; fill: {self.C_TEXT}; }}
    .subtitle {{ font: 11px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; }}
    .label {{ font: bold 10px "SF Mono", Consolas, monospace; fill: {self.C_TEXT}; }}
    .value {{ font: 9px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; }}
    .pin {{ font: 8px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; }}
    .anno {{ font: 9px "SF Mono", Consolas, monospace; fill: {self.C_ANNOTATION}; }}
    .wire {{ stroke: {self.C_WIRE}; stroke-width: 1.5; fill: none; }}
    .wire-thick {{ stroke: {self.C_WIRE}; stroke-width: 2.5; fill: none; }}
    .component {{ stroke: {self.C_COMPONENT}; stroke-width: 1.5; fill: none; }}
    .filled {{ fill: {self.C_COMPONENT}; }}
    .junction {{ fill: {self.C_ANNOTATION}; }}
  </style>
  <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="{self.C_ANNOTATION}"/>
  </marker>
</defs>
<rect width="{self.width}" height="{self.height}" fill="{self.C_BG}"/>
<text x="{self.width//2}" y="25" class="title" text-anchor="middle">{self.title}</text>
{f'<text x="{self.width//2}" y="42" class="subtitle" text-anchor="middle">{self.subtitle}</text>' if self.subtitle else ''}
'''

    def _svg_footer(self) -> str:
        return '</svg>'
    
    def wire(self, p1: Point, p2: Point, thick: bool = False) -> None:
        """Draw connecting wire."""
        cls = "wire-thick" if thick else "wire"
        self.elements.append(f'<line x1="{p1.x}" y1="{p1.y}" x2="{p2.x}" y2="{p2.y}" class="{cls}"/>')
    
    def junction(self, p: Point) -> None:
        """Draw junction dot."""
        self.elements.append(f'<circle cx="{p.x}" cy="{p.y}" r="3.5" class="junction"/>')
    
    def ground(self, p: Point) -> None:
        """Draw ground symbol."""
        self.elements.extend([
            f'<line x1="{p.x}" y1="{p.y}" x2="{p.x}" y2="{p.y+12}" class="wire"/>',
            f'<line x1="{p.x-10}" y1="{p.y+12}" x2="{p.x+10}" y2="{p.y+12}" class="wire" stroke-width="2"/>',
            f'<line x1="{p.x-6}" y1="{p.y+16}" x2="{p.x+6}" y2="{p.y+16}" class="wire" stroke-width="1.5"/>',
        ])
    
    def vcc(self, p: Point, label: str = "+12V") -> None:
        """Draw positive power rail."""
        self.elements.extend([
            f'<line x1="{p.x}" y1="{p.y}" x2="{p.x}" y2="{p.y-12}" class="wire" stroke="{self.C_POWER_POS}" stroke-width="2"/>',
            f'<text x="{p.x+4}" y="{p.y-6}" class="value" fill="{self.C_POWER_POS}">{label}</text>',
        ])
    
    def resistor(self, pos: Point, label: str = "", value: str = "", vertical: bool = True) -> None:
        """Draw resistor (zigzag)."""
        if vertical:
            # Vertical resistor
            zig = [f"M{pos.x},{pos.y-25}"]
            for i, dx in enumerate([-6, 6, -6, 6, -6, 6, -6, 6]):
                zig.append(f"l{dx},{5}")
            zig.append(f"l0,{5}")
            d = " ".join(zig)
            self.elements.append(f'<path d="{d}" class="component"/>')
            
            if label:
                self.elements.append(f'<text x="{pos.x-20}" y="{pos.y-5}" class="label" text-anchor="end">{label}</text>')
            if value:
                self.elements.append(f'<text x="{pos.x+12}" y="{pos.y}" class="value">{value}</text>')
        else:
            # Horizontal resistor
            zig = [f"M{pos.x-25},{pos.y}"]
            for i, dy in enumerate([-6, 6, -6, 6, -6, 6, -6, 6]):
                zig.append(f"l{5},{dy}")
            zig.append(f"l{5},0")
            d = " ".join(zig)
            self.elements.append(f'<path d="{d}" class="component"/>')
            
            if label:
                self.elements.append(f'<text x="{pos.x}" y="{pos.y-18}" class="label" text-anchor="middle">{label}</text>')
            if value:
                self.elements.append(f'<text x="{pos.x}" y="{pos.y+22}" class="value" text-anchor="middle">{value}</text>')
    
    def capacitor(self, pos: Point, label: str = "", value: str = "", polarized: bool = False, vertical: bool = True) -> None:
        """Draw capacitor (two parallel lines)."""
        if vertical:
            self.elements.extend([
                f'<line x1="{pos.x}" y1="{pos.y-25}" x2="{pos.x}" y2="{pos.y-4}" class="wire"/>',
                f'<line x1="{pos.x}" y1="{pos.y+4}" x2="{pos.x}" y2="{pos.y+25}" class="wire"/>',
                f'<line x1="{pos.x-8}" y1="{pos.y-4}" x2="{pos.x+8}" y2="{pos.y-4}" class="component" stroke-width="2"/>',
                f'<line x1="{pos.x-8}" y1="{pos.y+4}" x2="{pos.x+8}" y2="{pos.y+4}" class="component" stroke-width="2"/>',
            ])
            if polarized:
                self.elements.append(f'<text x="{pos.x-14}" y="{pos.y-8}" class="value" fill="{self.C_POWER_POS}">+</text>')
        else:
            self.elements.extend([
                f'<line x1="{pos.x-25}" y1="{pos.y}" x2="{pos.x-4}" y2="{pos.y}" class="wire"/>',
                f'<line x1="{pos.x+4}" y1="{pos.y}" x2="{pos.x+25}" y2="{pos.y}" class="wire"/>',
                f'<line x1="{pos.x-4}" y1="{pos.y-8}" x2="{pos.x-4}" y2="{pos.y+8}" class="component" stroke-width="2"/>',
                f'<line x1="{pos.x+4}" y1="{pos.y-8}" x2="{pos.x+4}" y2="{pos.y+8}" class="component" stroke-width="2"/>',
            ])
            if polarized:
                self.elements.append(f'<text x="{pos.x-8}" y="{pos.y-14}" class="value" fill="{self.C_POWER_POS}">+</text>')
        
        if label:
            lx = pos.x - 20 if vertical else pos.x
            ly = pos.y - 5 if vertical else pos.y - 18
            anchor = "end" if vertical else "middle"
            self.elements.append(f'<text x="{lx}" y="{ly}" class="label" text-anchor="{anchor}">{label}</text>')
        if value:
            lx = pos.x + 12 if vertical else pos.x
            ly = pos.y + 5 if vertical else pos.y + 22
            anchor = "start" if vertical else "middle"
            self.elements.append(f'<text x="{lx}" y="{ly}" class="value" text-anchor="{anchor}">{value}</text>')
    
    def opamp(self, pos: Point, label: str = "", pins: Tuple[str, str, str] = ("", "", "")) -> None:
        """Draw op-amp triangle symbol."""
        size = 30
        # Triangle
        self.elements.append(f'<polygon points="{pos.x-size},{pos.y-size} {pos.x-size},{pos.y+size} {pos.x+size},{pos.y}" class="component"/>')
        
        if label:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y+5}" class="label" text-anchor="middle" font-size="9">{label}</text>')
        
        # Pin labels
        if pins[0]:  # - input
            self.elements.append(f'<text x="{pos.x-size-3}" y="{pos.y-18}" class="pin" text-anchor="end">-</text>')
        if pins[1]:  # + input
            self.elements.append(f'<text x="{pos.x-size-3}" y="{pos.y+18}" class="pin" text-anchor="end">+</text>')
    
    def npn_transistor(self, pos: Point, label: str = "") -> None:
        """Draw NPN transistor symbol."""
        # Base line
        self.elements.append(f'<line x1="{pos.x-20}" y1="{pos.y}" x2="{pos.x}" y2="{pos.y}" class="component"/>')
        # Collector (angled up)
        self.elements.append(f'<line x1="{pos.x}" y1="{pos.y}" x2="{pos.x+15}" y2="{pos.y-20}" class="component"/>')
        # Emitter (angled down) with arrow
        self.elements.append(f'<line x1="{pos.x}" y1="{pos.y}" x2="{pos.x+15}" y2="{pos.y+20}" class="component"/>')
        # Arrow on emitter
        self.elements.append(f'<polygon points="{pos.x+15},{pos.y+20} {pos.x+10},{pos.y+13} {pos.x+18},{pos.y+15}" class="filled"/>')
        
        if label:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y+45}" class="label" text-anchor="middle">{label}</text>')
        
        # Pin labels
        self.elements.append(f'<text x="{pos.x-25}" y="{pos.y+3}" class="pin" text-anchor="end">B</text>')
        self.elements.append(f'<text x="{pos.x+20}" y="{pos.y-20}" class="pin" text-anchor="start">C</text>')
        self.elements.append(f'<text x="{pos.x+20}" y="{pos.y+25}" class="pin" text-anchor="start">E</text>')
    
    def jack(self, pos: Point, label: str = "") -> None:
        """Draw audio jack."""
        self.elements.extend([
            f'<circle cx="{pos.x}" cy="{pos.y}" r="8" class="component"/>',
            f'<line x1="{pos.x}" y1="{pos.y}" x2="{pos.x+20}" y2="{pos.y}" class="wire"/>',
        ])
        if label:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y+22}" class="label" text-anchor="middle">{label}</text>')
    
    def potentiometer(self, pos: Point, label: str = "", value: str = "") -> None:
        """Draw potentiometer."""
        # Resistor body (zigzag)
        self.elements.append(f'<path d="M{pos.x-20},{pos.y} l5,-8 l5,8 l5,-8 l5,8 l5,-8 l5,8" class="component"/>')
        # Arrow from top
        self.elements.append(f'<line x1="{pos.x}" y1="{pos.y-30}" x2="{pos.x}" y2="{pos.y-10}" class="wire"/>')
        self.elements.append(f'<polygon points="{pos.x},{pos.y-10} {pos.x-4},{pos.y-18} {pos.x+4},{pos.y-18}" class="filled"/>')
        
        if label:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y-35}" class="label" text-anchor="middle">{label}</text>')
        if value:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y+20}" class="value" text-anchor="middle">{value}</text>')
    
    def block(self, pos: Point, width: float, height: float, label: str = "", sublabel: str = "") -> None:
        """Draw functional block (for buffers, etc.)."""
        x1, y1 = pos.x - width/2, pos.y - height/2
        self.elements.append(f'<rect x="{x1}" y="{y1}" width="{width}" height="{height}" class="component" fill="#f5f5f5"/>')
        if label:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y}" class="label" text-anchor="middle">{label}</text>')
        if sublabel:
            self.elements.append(f'<text x="{pos.x}" y="{pos.y+12}" class="value" text-anchor="middle">{sublabel}</text>')
    
    def annotate(self, pos: Point, text: str) -> None:
        """Add annotation text."""
        self.elements.append(f'<text x="{pos.x}" y="{pos.y}" class="anno">{text}</text>')
    
    def render(self) -> str:
        """Render complete SVG."""
        return self._svg_header() + "\n".join(self.elements) + self._svg_footer()


def generate_noise_schematic() -> str:
    """Generate white noise generator schematic."""
    r = SchematicRenderer(600, 500, "White Noise Generator", "2N3904 avalanche breakdown + TL072 amplifier")
    
    # Power rail
    r.vcc(Point(100, 50))
    
    # Transistor noise source
    r.npn_transistor(Point(150, 150), label="2N3904")
    
    # Base bias resistors from +12V
    r.wire(Point(150, 50), Point(150, 125))
    r.resistor(Point(120, 90), label="R1", value="470k", vertical=False)
    r.resistor(Point(180, 90), label="R2", value="470k", vertical=False)
    
    # Emitter to ground via cap
    r.wire(Point(165, 170), Point(165, 280))
    r.capacitor(Point(165, 280), value="100pF", vertical=True)
    r.ground(Point(165, 330))
    
    # TL072 amplifier
    r.opamp(Point(350, 200), label="TL072", pins=("-", "+", "out"))
    
    # Connection from emitter to opamp input
    r.wire(Point(165, 150), Point(200, 150))
    r.wire(Point(200, 150), Point(200, 182))
    r.wire(Point(200, 182), Point(320, 182))
    
    # Feedback network
    r.wire(Point(380, 200), Point(420, 200))
    r.wire(Point(420, 200), Point(420, 100))
    r.wire(Point(420, 100), Point(250, 100))
    r.wire(Point(250, 100), Point(250, 182))
    r.resistor(Point(335, 100), label="R3", value="4.7M", vertical=False)
    
    # + input to ground
    r.wire(Point(200, 218), Point(200, 350))
    r.resistor(Point(200, 290), label="R4", value="100k", vertical=True)
    r.ground(Point(200, 350))
    
    # Output to jack
    r.wire(Point(420, 200), Point(480, 200))
    r.jack(Point(500, 200), label="NOISE OUT")
    
    # Annotations
    r.annotate(Point(50, 150), "Avalanche\\nnoise source")
    r.annotate(Point(450, 100), "Gain = 47x")
    
    return r.render()


def generate_lfo_schematic() -> str:
    """Generate LFO schematic."""
    r = SchematicRenderer(700, 550, "Triangle/Square LFO", "TL072 integrator + Schmitt trigger")
    
    # Opamp A - Integrator
    r.opamp(Point(200, 150), label="A (Integrator)", pins=("-", "+", "out"))
    
    # Opamp B - Schmitt trigger
    r.opamp(Point(500, 150), label="B (Schmitt)", pins=("-", "+", "out"))
    
    # Integrator components
    # Input resistor
    r.wire(Point(120, 150), Point(170, 150))
    r.resistor(Point(145, 150), label="R1", value="1M", vertical=False)
    
    # Feedback capacitor
    r.wire(Point(230, 150), Point(260, 150))
    r.wire(Point(260, 150), Point(260, 80))
    r.wire(Point(260, 80), Point(170, 80))
    r.wire(Point(170, 80), Point(170, 132))
    r.capacitor(Point(200, 80), label="C1", value="1µF", vertical=False)
    
    # + input to ground
    r.wire(Point(170, 168), Point(170, 250))
    r.ground(Point(170, 250))
    
    # Connection between stages
    r.wire(Point(230, 150), Point(280, 150))
    r.wire(Point(280, 150), Point(280, 300))
    r.potentiometer(Point(280, 340), label="RATE", value="1M")
    r.wire(Point(280, 370), Point(280, 420))
    r.wire(Point(280, 420), Point(430, 420))
    r.wire(Point(430, 420), Point(430, 168))
    r.wire(Point(430, 168), Point(470, 168))
    
    # Schmitt trigger feedback
    r.wire(Point(530, 150), Point(580, 150))
    r.wire(Point(580, 150), Point(580, 60))
    r.wire(Point(580, 60), Point(430, 60))
    r.wire(Point(430, 60), Point(430, 132))
    r.resistor(Point(505, 60), label="R2", value="100k", vertical=False)
    r.resistor(Point(430, 96), label="R3", value="100k", vertical=True)
    r.ground(Point(430, 130))
    
    # Triangle output
    r.wire(Point(280, 150), Point(280, 480))
    r.jack(Point(280, 500), label="TRI")
    
    # Square output
    r.wire(Point(580, 150), Point(580, 480))
    r.resistor(Point(580, 450), label="R4", value="1.8k", vertical=True)
    r.jack(Point(580, 500), label="SQR")
    
    return r.render()


def generate_sah_schematic() -> str:
    """Generate Sample & Hold schematic."""
    r = SchematicRenderer(600, 500, "Sample & Hold", "LF398 with droop compensation")
    
    # Input buffer
    r.opamp(Point(150, 150), label="Input Buffer", pins=("-", "+", "out"))
    
    # LF398
    r.block(Point(350, 200), 80, 120, label="LF398", sublabel="S&amp;H")
    
    # Output buffer
    r.opamp(Point(500, 250), label="Output", pins=("-", "+", "out"))
    
    # Sample cap
    r.wire(Point(390, 200), Point(390, 350))
    r.capacitor(Point(390, 350), label="C", value="10nF", polarized=True, vertical=True)
    r.ground(Point(390, 400))
    
    # Inputs/outputs
    r.jack(Point(50, 150), label="SIGNAL")
    r.wire(Point(58, 150), Point(120, 150))
    
    r.jack(Point(50, 300), label="CLOCK")
    r.wire(Point(58, 300), Point(310, 300))
    r.wire(Point(310, 300), Point(310, 260))
    
    r.jack(Point(580, 250), label="OUTPUT")
    r.wire(Point(530, 250), Point(572, 250))
    
    return r.render()


def generate_clock_divider_schematic() -> str:
    """Generate clock divider schematic."""
    r = SchematicRenderer(600, 450, "Clock Divider", "/2 /4 /8 with CD4024 or CD4040")
    
    # Input buffer
    r.opamp(Point(100, 200), label="Buffer", pins=("-", "+", "out"))
    r.jack(Point(30, 200), label="CLK IN")
    r.wire(Point(38, 200), Point(70, 200))
    
    # Divider IC
    r.block(Point(250, 200), 100, 150, label="CD4024", sublabel="7-stage")
    
    # Outputs
    outputs = ["/2", "/4", "/8"]
    for i, div in enumerate(outputs):
        y = 140 + i * 60
        r.wire(Point(300, y), Point(380, y))
        r.block(Point(340, y), 40, 30, label=div)
        r.wire(Point(380, y), Point(450, y))
        r.jack(Point(470, y), label=div)
    
    return r.render()


def generate_wiring_diagram() -> str:
    """Generate comprehensive system wiring diagram with both DB-9 A and B."""
    r = SchematicRenderer(1200, 900, "MACROBRUTE Complete System Wiring", "DB-9 A (Outputs) and DB-9 B (Inputs + Power)")
    
    # Title section with DB-9 pinout summary
    r.elements.append(f'<text x="600" y="65" class="subtitle" text-anchor="middle">DB-9 A = MicroBrute → Expander (Signals) | DB-9 B = Expander → MicroBrute (CV + Power)</text>')
    
    # === DB-9 A SECTION (TOP) ===
    r.elements.append(f'<text x="100" y="100" class="label" font-size="12" fill="#0066CC">DB-9 A: OUTPUTS</text>')
    
    # Stage boxes for DB-9 A
    stages_a = [
        ("MicroBrute\\nPCB", 100, 130),
        ("Breakout\\nPCB", 300, 130),
        ("DB-9 A", 500, 130),
        ("Cable A", 700, 130),
        ("Expander\\nOutput Jacks", 950, 130),
    ]
    
    for label, x, y in stages_a:
        r.elements.append(f'<rect x="{x-50}" y="{y}" width="100" height="50" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
        lines = label.split("\\n")
        for i, line in enumerate(lines):
            r.elements.append(f'<text x="{x}" y="{y+22+i*16}" class="label" text-anchor="middle">{line}</text>')
    
    # DB-9 A signals (Outputs from MicroBrute)
    signals_a = [
        ("Pin 7: TP94 Saw", 220, "1kΩ", "Buf", "Saw Out"),
        ("Pin 8: TP93 Sqr", 250, "1kΩ", "Buf", "Sqr Out"),
        ("Pin 5: TP30 Mix", 280, "1kΩ", "Buf", "Mix Out"),
        ("Pin 6: TP19 VCF", 310, "1kΩ", "Buf", "VCF Out"),
        ("Pin 2: Pitch CV", 350, None, "Buf", "Pitch Out"),
        ("Pin 1: TP83 Gate", 380, "10kΩ", "Schmitt", "Gate Out"),
        ("Pin 3: Env", 410, "10kΩ", "Buf", "Env Out"),
        ("Pin 4: LFO", 440, "10kΩ", "Buf", "LFO Out"),
    ]
    
    for label, y, series_r, buffer, output_label in signals_a:
        # From MicroBrute to Breakout
        r.wire(Point(100, y), Point(200, y))
        if series_r:
            r.resistor(Point(150, y), value=series_r, vertical=False)
        r.elements.append(f'<text x="50" y="{y-5}" class="value" font-size="8">{label}</text>')
        
        # Continue to DB-9 A
        r.wire(Point(200, y), Point(400, y))
        if buffer:
            r.block(Point(300, y), 40, 20, label=buffer)
        
        # To cable
        r.wire(Point(400, y), Point(600, y))
        r.wire(Point(600, y), Point(850, y))
        
        # Output jack
        r.jack(Point(920, y), label=output_label.replace(" Out", ""))
        r.elements.append(f'<text x="{y < 350 and 1000 or 1010}" y="{y+3}" class="value" font-size="8">{output_label}</text>')
    
    # === DB-9 B SECTION (BOTTOM) ===
    r.elements.append(f'<text x="100" y="520" class="label" font-size="12" fill="#D44">DB-9 B: INPUTS + POWER</text>')
    
    # Stage boxes for DB-9 B
    stages_b = [
        ("Expander\\nControls", 100, 550),
        ("Cable B", 300, 550),
        ("DB-9 B", 500, 550),
        ("Breakout", 700, 550),
        ("MicroBrute\\nCircuit", 950, 550),
    ]
    
    for label, x, y in stages_b:
        r.elements.append(f'<rect x="{x-50}" y="{y}" width="100" height="50" fill="#E8D5A3" stroke="#B8722D" stroke-width="2" rx="4"/>')
        lines = label.split("\\n")
        for i, line in enumerate(lines):
            r.elements.append(f'<text x="{x}" y="{y+22+i*16}" class="label" text-anchor="middle">{line}</text>')
    
    # DB-9 B signals (Inputs to MicroBrute)
    signals_b = [
        ("Pin 1: Filter CV", 640, "Pot", "Atten", "Filter In"),
        ("Pin 2: VCA CV", 670, "Pot", "Direct", "VCA In"),
        ("Pin 3: Resonance", 700, "Pot", "Vactrol", "Res CV"),
        ("Pin 4: Sync", 730, None, "Direct", "Sync"),
        ("Pin 5: Gate In", 760, "Diode", "Schmitt", "Gate"),
        ("Pin 6: Ext Audio", 790, None, "Mixer", "Ext In"),
    ]
    
    for label, y, control, protection, dest in signals_b:
        # From expander controls
        r.wire(Point(100, y), Point(200, y))
        if control:
            r.block(Point(150, y), 40, 20, label=control)
        r.elements.append(f'<text x="40" y="{y-5}" class="value" font-size="8">{label}</text>')
        
        # Through cable
        r.wire(Point(200, y), Point(400, y))
        
        # To DB-9 B
        r.wire(Point(400, y), Point(600, y))
        if protection:
            r.block(Point(500, y), 50, 20, label=protection)
        
        # To MicroBrute
        r.wire(Point(600, y), Point(850, y))
        r.elements.append(f'<text x="860" y="{y+3}" class="value" font-size="8">→ {dest}</text>')
    
    # === POWER SECTION ===
    r.elements.append(f'<text x="100" y="860" class="label" font-size="12" fill="#4A4">POWER</text>')
    
    # Power rails
    power_lines = [
        ("Pin 7: +12V", 880, "#D44", "Red"),
        ("Pin 8: -12V", 910, "#44D", "Brown"),
        ("Pin 9: GND", 940, "#4A4", "Black"),
    ]
    
    for label, y, color, wire_color in power_lines:
        # Expander power entry
        r.wire(Point(100, y), Point(200, y))
        r.elements.append(f'<line x1="100" y1="{y}" x2="150" y2="{y}" stroke="{color}" stroke-width="3"/>')
        r.elements.append(f'<text x="40" y="{y+3}" class="value" font-size="8">{label}</text>')
        
        # Through cable
        r.wire(Point(200, y), Point(400, y))
        
        # Protection at DB-9 B
        r.wire(Point(400, y), Point(600, y))
        if "GND" not in label:
            r.block(Point(500, y), 50, 20, label="Fuse+Diode")
        
        # To breakout
        r.wire(Point(600, y), Point(850, y))
        
        # Distribution
        r.elements.append(f'<text x="860" y="{y+3}" class="value" font-size="8">→ All PCBs</text>')
    
    # Legend
    r.elements.append(f'<text x="1000" y="500" class="label" font-size="9">Legend:</text>')
    r.elements.append(f'<rect x="980" y="510" width="15" height="10" fill="#E8D5A3" stroke="#B8722D"/>')
    r.elements.append(f'<text x="1000" y="518" class="value" font-size="8">Stage</text>')
    r.elements.append(f'<line x1="980" y1="530" x2="995" y2="530" class="wire"/>')
    r.elements.append(f'<text x="1000" y="533" class="value" font-size="8">Signal</text>')
    
    return r.render()


def main():
    """Generate all schematics."""
    os.makedirs("schematics", exist_ok=True)
    
    schematics = [
        ("noise_generator_schematic.svg", generate_noise_schematic),
        ("lfo_schematic.svg", generate_lfo_schematic),
        ("sah_schematic.svg", generate_sah_schematic),
        ("clock_divider_schematic.svg", generate_clock_divider_schematic),
        ("wiring_overview.svg", generate_wiring_diagram),
    ]
    
    for filename, generator in schematics:
        filepath = f"schematics/{filename}"
        try:
            with open(filepath, 'w') as f:
                f.write(generator())
            print(f"Generated: {filepath}")
        except Exception as e:
            print(f"Error generating {filepath}: {e}")
    
    print("\nDone. Regenerate with: python3 tools/generate_schematics.py")


if __name__ == "__main__":
    main()
