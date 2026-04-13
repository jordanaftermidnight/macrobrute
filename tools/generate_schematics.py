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
        """Generate SVG header with text shadow for dark mode readability."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
<defs>
  <filter id="textshadow" x="-20%" y="-20%" width="140%" height="140%">
    <feFlood flood-color="white" flood-opacity="0.9" result="bg"/>
    <feMorphology in="SourceGraphic" operator="dilate" radius="1.5" result="dilated"/>
    <feComposite in="bg" in2="dilated" operator="in" result="shadow"/>
    <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .title {{ font: bold 16px "SF Mono", Consolas, monospace; fill: {self.C_TEXT}; filter: url(#textshadow); }}
    .subtitle {{ font: 11px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; filter: url(#textshadow); }}
    .label {{ font: bold 10px "SF Mono", Consolas, monospace; fill: {self.C_TEXT}; filter: url(#textshadow); }}
    .value {{ font: 9px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; filter: url(#textshadow); }}
    .pin {{ font: 8px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; filter: url(#textshadow); }}
    .anno {{ font: 9px "SF Mono", Consolas, monospace; fill: {self.C_ANNOTATION}; filter: url(#textshadow); }}
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


def db9_connector(r, x, y, label, pins, is_female=True):
    """Draw DB-9 connector with pins labeled."""
    w, h = 70, 110
    # Connector body
    r.elements.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="8" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2"/>')
    # Label
    r.elements.append(f'<text x="{x}" y="{y-h/2-8}" class="label" text-anchor="middle" fill="#0066CC">{label}</text>')
    # Pins (5 on top row, 4 on bottom for DB-9)
    pin_labels = pins if len(pins) == 9 else pins + [""]
    for i in range(5):  # Top row: 5,4,3,2,1 (right to left for female)
        px = x + 25 - i * 12
        py = y - 15
        r.elements.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#gold" stroke="#B8860B" stroke-width="1"/>')
        if pin_labels[4-i]:
            r.elements.append(f'<text x="{px}" y="{py-8}" class="value" font-size="7" text-anchor="middle">{pin_labels[4-i][:6]}</text>')
    for i in range(4):  # Bottom row: 9,8,7,6
        px = x + 19 - i * 12
        py = y + 15
        r.elements.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#gold" stroke="#B8860B" stroke-width="1"/>')
        if pin_labels[8-i]:
            r.elements.append(f'<text x="{px}" y="{py+12}" class="value" font-size="7" text-anchor="middle">{pin_labels[8-i][:6]}</text>')


def switch(r, x, y, label=None):
    """Draw SPST switch symbol."""
    r.elements.extend([
        f'<line x1="{x}" y1="{y-10}" x2="{x}" y2="{y+10}" class="component"/>',
        f'<circle cx="{x}" cy="{y-10}" r="2" class="filled"/>',
        f'<circle cx="{x}" cy="{y+10}" r="2" class="filled"/>',
        f'<line x1="{x}" y1="{y-10}" x2="{x+12}" y2="{y+5}" class="component"/>',
    ])
    if label:
        r.elements.append(f'<text x="{x+15}" y="{y}" class="value" font-size="8">{label}</text>')


def led(r, x, y, label=None, color="#D44"):
    """Draw LED symbol."""
    # Triangle
    r.elements.append(f'<polygon points="{x-8},{y+8} {x-8},{y-8} {x+8},{y}" fill="{color}" stroke="#333" stroke-width="1"/>')
    # Arrows for light emission
    r.elements.append(f'<line x1="{x+10}" y1="{y-8}" x2="{x+14}" y2="{y-12}" class="component"/>')
    r.elements.append(f'<line x1="{x+12}" y1="{y-6}" x2="{x+16}" y2="{y-10}" class="component"/>')
    if label:
        r.elements.append(f'<text x="{x}" y="{y+18}" class="value" font-size="8" text-anchor="middle">{label}</text>')


def generate_wiring_diagram() -> str:
    """Generate compact system wiring diagram."""
    r = SchematicRenderer(900, 650, "MACROBRUTE Interconnect Wiring", "DB-9 A (Outputs) & DB-9 B (Inputs + Power)")
    
    # === COMPACT TWO-COLUMN LAYOUT ===
    # Left: DB-9 A outputs | Right: DB-9 B inputs + Power
    
    # Column headers
    r.elements.append(f'<text x="220" y="50" class="label" font-size="12" fill="#0066CC">DB-9 A: OUTPUTS →</text>')
    r.elements.append(f'<text x="680" y="50" class="label" font-size="12" fill="#D44">← DB-9 B: INPUTS</text>')
    
    # DB-9 connectors (center)
    db9_connector(r, 450, 180, "DB-9 A (Rear)", 
                  ["Gate", "Pitch", "Env", "LFO", "Mix", "VCF", "Saw", "Sqr", "GND"])
    db9_connector(r, 450, 450, "DB-9 B (Rear)",
                  ["Filt", "VCA", "Res", "Sync", "Gate", "Ext", "+12V", "-12V", "GND"])
    
    # === DB-9 A OUTPUTS (Left side, flowing right) ===
    y_start = 110
    spacing = 22
    
    outputs = [
        ("1", "TP83 Gate", "10k", "→Schmitt→"),
        ("2", "Pitch CV", "", "Direct→"),
        ("3", "Env Out", "10k", "→Buffer→"),
        ("4", "LFO Out", "10k", "→Buffer→"),
        ("5", "TP30 Mix", "1k", "→Buffer→"),
        ("6", "TP19 VCF", "1k", "→Buffer→"),
        ("7", "TP94 Saw", "1k", "→Buffer→"),
        ("8", "TP93 Sqr", "1k", "→Buffer→"),
    ]
    
    for i, (pin, name, resistor, processing) in enumerate(outputs):
        y = y_start + i * spacing
        
        # Signal name on far left
        r.elements.append(f'<text x="10" y="{y+3}" class="label" font-size="9">{name}</text>')
        
        # Series resistor if present
        r.wire(Point(90, y), Point(130, y))
        if resistor:
            r.resistor(Point(110, y), value=resistor, vertical=False)
        
        # Processing block
        r.wire(Point(130, y), Point(200, y))
        r.block(Point(165, y), 50, 16, label=processing.replace("→", "").replace("Buffer", "Buf"))
        
        # To DB-9 A
        r.wire(Point(200, y), Point(415, y))
        
        # Pin label
        r.elements.append(f'<text x="425" y="{y+3}" class="value" font-size="8" fill="#gold">{pin}</text>')
    
    # === DB-9 B INPUTS (Right side, flowing left) ===
    y_start = 380
    
    inputs = [
        ("1", "Filter CV", "Pot", "Atten→", "→Filter"),
        ("2", "VCA CV", "Pot", "→", "→TP10/11"),
        ("3", "Resonance", "Pot", "Vactrol→", "→RP13"),
        ("4", "Sync", "", "→", "→VCO"),
        ("5", "Gate In", "", "Diode→", "→Gate"),
        ("6", "Ext Audio", "", "→", "→Mixer"),
    ]
    
    for i, (pin, name, control, processing, dest) in enumerate(inputs):
        y = y_start + i * spacing
        
        # From DB-9 B
        r.elements.append(f'<text x="485" y="{y+3}" class="value" font-size="8" fill="#gold" text-anchor="middle">{pin}</text>')
        r.wire(Point(485, y), Point(550, y))
        
        # Processing
        if processing.strip("→"):
            r.block(Point(580, y), 45, 16, label=processing.replace("→", "").replace("Atten", "Att"))
        r.wire(Point(550, y), Point(620, y))
        
        # Control element
        if control:
            r.block(Point(655, y), 35, 16, label=control)
        r.wire(Point(620, y), Point(720, y))
        
        # Destination
        r.elements.append(f'<text x="730" y="{y+3}" class="label" font-size="9">{dest}</text>')
    
    # === POWER (Bottom right) ===
    r.elements.append(f'<text x="550" y="570" class="label" font-size="11" fill="#4A4">POWER</text>')
    
    power = [
        ("7", "+12V", "#D44", "Fuse", "→Breakout"),
        ("8", "-12V", "#44D", "Fuse", "→Breakout"),
        ("9", "GND", "#4A4", "", "→Star Gnd"),
    ]
    
    for i, (pin, name, color, protect, dest) in enumerate(power):
        y = 590 + i * 18
        
        r.elements.append(f'<text x="485" y="{y+3}" class="value" font-size="8" fill="#gold" text-anchor="middle">{pin}</text>')
        r.wire(Point(485, y), Point(550, y))
        r.elements.append(f'<line x1="485" y1="{y}" x2="515" y2="{y}" stroke="{color}" stroke-width="2"/>')
        
        if protect:
            r.block(Point(575, y), 40, 14, label=protect)
        r.wire(Point(550, y), Point(650, y))
        
        r.elements.append(f'<text x="660" y="{y+3}" class="label" font-size="9" fill="{color}">{dest}</text>')
    
    # === CLOCK BYPASS (Bottom left) ===
    r.elements.append(f'<text x="10" y="570" class="label" font-size="11" fill="#666">CLOCK I/O (Direct)</text>')
    r.elements.append(f'<text x="10" y="588" class="value" font-size="8">Pico GP22 → CLK Out jack</text>')
    r.elements.append(f'<text x="10" y="603" class="value" font-size="8">Pico GP21 → CLK In jack</text>')
    r.elements.append(f'<text x="10" y="618" class="value" font-size="8">Pico GND → Common GND</text>')
    
    # Legend box
    r.elements.append(f'<rect x="750" y="85" width="140" height="75" fill="#f5f5f5" stroke="#ccc" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="760" y="100" class="label" font-size="9">Legend</text>')
    r.elements.append(f'<line x1="760" y1="110" x2="780" y2="110" class="wire"/>')
    r.elements.append(f'<text x="785" y="113" class="value" font-size="8">Signal wire</text>')
    r.resistor(Point(770, 125), value="R", vertical=False)
    r.elements.append(f'<text x="785" y="128" class="value" font-size="8">Series resistor</text>')
    r.block(Point(785, 145), 30, 12, label="Buf")
    r.elements.append(f'<text x="820" y="148" class="value" font-size="8">= Buffer</text>')
    
    return r.render()


def generate_slew_limiter_schematic() -> str:
    """Generate Slew Limiter schematic (TL072 + diode steering)."""
    r = SchematicRenderer(550, 450, "Slew Limiter", "Separate Rise/Fall with Diode Steering")
    
    # Input
    r.jack(Point(50, 200), label="IN")
    r.wire(Point(70, 200), Point(100, 200))
    r.resistor(Point(115, 200), label="Rin", value="10k", vertical=False)
    r.wire(Point(130, 200), Point(160, 200))
    r.junction(Point(160, 200))
    
    # RISE path (D1)
    r.wire(Point(160, 200), Point(160, 120))
    r.wire(Point(160, 120), Point(200, 120))
    # Diode D1 (pointing right)
    r.elements.extend([
        f'<polygon points="200,110 200,130 220,120" fill="none" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="220" y1="110" x2="220" y2="130" stroke="#333" stroke-width="1.5"/>',
    ])
    r.wire(Point(220, 120), Point(260, 120))
    r.potentiometer(Point(290, 120), label="RISE", value="1M log")
    r.wire(Point(290, 90), Point(290, 60))
    r.wire(Point(290, 60), Point(380, 60))
    
    # FALL path (D2)  
    r.wire(Point(160, 200), Point(160, 280))
    r.wire(Point(160, 280), Point(200, 280))
    # Diode D2 (pointing left)
    r.elements.extend([
        f'<polygon points="220,270 220,290 200,280" fill="none" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="200" y1="270" x2="200" y2="290" stroke="#333" stroke-width="1.5"/>',
    ])
    r.wire(Point(160, 280), Point(260, 280))
    r.potentiometer(Point(290, 280), label="FALL", value="1M log")
    r.wire(Point(290, 310), Point(290, 340))
    r.wire(Point(290, 340), Point(380, 340))
    
    # Both paths join
    r.wire(Point(380, 60), Point(380, 200))
    r.wire(Point(380, 340), Point(380, 200))
    r.junction(Point(380, 200))
    
    # Opamp
    r.opamp(Point(450, 200), label="TL072", pins=("-", "+", "out"))
    r.wire(Point(380, 200), Point(420, 200))
    
    # Feedback capacitor
    r.wire(Point(480, 200), Point(520, 200))
    r.wire(Point(520, 200), Point(520, 320))
    r.wire(Point(520, 320), Point(420, 320))
    r.wire(Point(420, 320), Point(420, 218))
    r.capacitor(Point(470, 320), label="C", value="1µF", vertical=False)
    
    # +in to ground
    r.wire(Point(420, 182), Point(420, 380))
    r.ground(Point(420, 380))
    
    # Output
    r.wire(Point(480, 200), Point(520, 200))
    r.jack(Point(520, 200), label="OUT")
    
    return r.render()


def generate_attenuverter_schematic() -> str:
    """Generate Attenuverter schematic (TL072)."""
    r = SchematicRenderer(550, 400, "Attenuverter", "Center-Detent Pot for -1x to +1x")
    
    # Input
    r.jack(Point(50, 150), label="IN")
    r.wire(Point(70, 150), Point(100, 150))
    r.resistor(Point(125, 150), label="R1", value="100k", vertical=False)
    r.wire(Point(150, 150), Point(180, 150))
    
    # Potentiometer (center-detent)
    r.potentiometer(Point(220, 150), label="Atten", value="100k center")
    r.wire(Point(220, 120), Point(220, 100))
    r.wire(Point(220, 100), Point(350, 100))
    r.wire(Point(220, 180), Point(220, 250))
    r.wire(Point(220, 250), Point(180, 250))
    r.ground(Point(180, 250))
    
    # Pot CCW end goes to input (for inverted signal)
    r.wire(Point(150, 150), Point(150, 280))
    r.wire(Point(150, 280), Point(120, 280))
    r.wire(Point(120, 280), Point(120, 250))
    r.wire(Point(120, 250), Point(120, 200))
    
    # Opamp
    r.opamp(Point(400, 180), label="TL072", pins=("-", "+", "out"))
    
    # Wiper to -in
    r.wire(Point(350, 100), Point(350, 162))
    r.wire(Point(350, 162), Point(370, 162))
    
    # +in to ground
    r.wire(Point(370, 198), Point(370, 300))
    r.ground(Point(370, 300))
    
    # Feedback resistor
    r.wire(Point(430, 180), Point(480, 180))
    r.wire(Point(480, 180), Point(480, 100))
    r.wire(Point(480, 100), Point(350, 100))
    r.resistor(Point(415, 100), label="Rf", value="100k", vertical=False)
    
    # Output
    r.wire(Point(430, 180), Point(480, 180))
    r.jack(Point(500, 180), label="OUT")
    
    return r.render()


def main():
    """Generate all schematics."""
    os.makedirs("schematics", exist_ok=True)
    
    schematics = [
        ("noise_generator_schematic.svg", generate_noise_schematic),
        ("lfo_schematic.svg", generate_lfo_schematic),
        ("sah_schematic.svg", generate_sah_schematic),
        ("clock_divider_schematic.svg", generate_clock_divider_schematic),
        ("slew_limiter_schematic.svg", generate_slew_limiter_schematic),
        ("attenuverter_schematic.svg", generate_attenuverter_schematic),
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
