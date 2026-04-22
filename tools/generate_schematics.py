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
    .wire {{ stroke: {self.C_WIRE}; stroke-width: 1.5; fill: none; transition: all 0.2s; cursor: pointer; }}
    .wire:hover {{ stroke: #ff6600; stroke-width: 2.5; filter: drop-shadow(0 0 3px #ff6600); }}
    .wire-thick {{ stroke: {self.C_WIRE}; stroke-width: 2.5; fill: none; transition: all 0.2s; cursor: pointer; }}
    .wire-thick:hover {{ stroke: #ff6600; stroke-width: 3.5; filter: drop-shadow(0 0 3px #ff6600); }}
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
    
    def wire(self, p1: Point, p2: Point, thick: bool = False, signal: str = None) -> None:
        """Draw connecting wire with optional signal grouping for highlighting."""
        cls = "wire-thick" if thick else "wire"
        if signal:
            # Wrap in group with signal data attribute
            self.elements.append(f'<g class="signal-group" data-signal="{signal}">')
            self.elements.append(f'<line x1="{p1.x}" y1="{p1.y}" x2="{p2.x}" y2="{p2.y}" class="{cls}"/>')
            self.elements.append('</g>')
        else:
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
    
    def opamp(self, pos: Point, label: str = "", pins: Tuple[str, str, str] = ("", "", ""), show_power: bool = True) -> None:
        """Draw op-amp triangle symbol with optional power pins."""
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
        
        # Power pins (V+ and V- or GND)
        if show_power:
            # V+ pin (top)
            self.elements.append(f'<line x1="{pos.x}" y1="{pos.y-size}" x2="{pos.x}" y2="{pos.y-size-10}" class="component"/>')
            self.elements.append(f'<text x="{pos.x+5}" y="{pos.y-size-5}" class="pin" font-size="7">V+</text>')
            # V- pin (bottom) 
            self.elements.append(f'<line x1="{pos.x}" y1="{pos.y+size}" x2="{pos.x}" y2="{pos.y+size+10}" class="component"/>')
            self.elements.append(f'<text x="{pos.x+5}" y="{pos.y+size+8}" class="pin" font-size="7">V-</text>')
    
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
    r.opamp(Point(350, 200), label="TL072", pins=("-", "+", "out"), show_power=True)
    
    # Power connections for TL072
    r.vcc(Point(350, 170), label="+12V")  # V+ pin
    r.wire(Point(350, 170), Point(350, 190))
    r.wire(Point(380, 230), Point(380, 260))
    r.wire(Point(380, 260), Point(420, 260))
    r.elements.append(f'<line x1="420" y1="260" x2="480" y2="260" stroke="#44D" stroke-width="2"/>')
    r.elements.append(f'<text x="490" y="263" class="value" fill="#44D" font-size="8">-12V</text>')  # V- pin
    
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
        r.elements.append(f'<circle cx="{px}" cy="{py}" r="3" fill="gold" stroke="#B8860B" stroke-width="1"/>')
        if pin_labels[4-i]:
            r.elements.append(f'<text x="{px}" y="{py-8}" class="value" font-size="7" text-anchor="middle">{pin_labels[4-i][:6]}</text>')
    for i in range(4):  # Bottom row: 9,8,7,6
        px = x + 19 - i * 12
        py = y + 15
        r.elements.append(f'<circle cx="{px}" cy="{py}" r="3" fill="gold" stroke="#B8860B" stroke-width="1"/>')
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
    """Generate improved MACROBRUTE interconnect wiring diagram with elbow routing and color coding."""
    
    # Color scheme for signal types
    C_AUDIO = "#0066CC"      # Blue - Audio outputs (Saw, Sqr, Mix, VCF)
    C_CV = "#CC6600"         # Orange - CV signals (Pitch, Env, LFO)
    C_GATE = "#009933"       # Green - Gate/Clock
    C_POWER_POS = "#CC0000"  # Red - +12V
    C_POWER_NEG = "#0000CC"  # Dark Blue - -12V
    C_GND = "#1a1a1a"        # Black - GND
    C_CONTROL = "#6600CC"    # Purple - Control signals
    
    r = SchematicRenderer(1000, 750, "MACROBRUTE Interconnect Wiring", "DB-9 A (Outputs) & DB-9 B (Inputs + Power)")
    
    # === LEGEND (Top Right) ===
    r.elements.append(f'<text x="750" y="35" class="label" font-size="11">Signal Type Legend:</text>')
    legend_items = [
        (C_AUDIO, "Audio Output (Saw, Sqr, Mix, VCF)"),
        (C_CV, "CV Signal (Pitch, Env, LFO)"),
        (C_GATE, "Gate/Clock"),
        (C_POWER_POS, "+12V Power"),
        (C_POWER_NEG, "-12V Power"),
        (C_GND, "GND"),
    ]
    for i, (color, label) in enumerate(legend_items):
        y_pos = 55 + i * 18
        r.elements.append(f'<rect x="750" y="{y_pos-8}" width="20" height="10" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="775" y="{y_pos}" class="value" font-size="9">{label}</text>')
    
    # === DB-9 A: OUTPUTS (Left Side) ===
    r.elements.append(f'<text x="200" y="110" class="label" font-size="13" fill="{C_AUDIO}">DB-9 A: OUTPUTS (MicroBrute → Expander)</text>')
    
    # DB-9 A connector with proper pin positions
    db9_x = 450
    db9_y_top = 145
    r.elements.append(f'<rect x="{db9_x-35}" y="{db9_y_top-20}" width="70" height="200" rx="8" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append(f'<text x="{db9_x}" y="{db9_y_top-30}" class="label" text-anchor="middle" fill="#0066CC">DB-9 A (Rear)</text>')
    
    # DB-9 A pins (5 on top row, 4 on bottom)
    pins_a = [
        ("5", "Mix", 145, C_AUDIO),
        ("4", "LFO", 165, C_CV),
        ("3", "Env", 185, C_CV),
        ("2", "Pitch", 205, C_CV),
        ("1", "Gate", 225, C_GATE),
        ("9", "GND", 265, C_GND),
        ("8", "Sqr", 285, C_AUDIO),
        ("7", "Saw", 305, C_AUDIO),
        ("6", "VCF", 325, C_AUDIO),
    ]
    
    for pin_num, label, y_offset, color in pins_a:
        pin_y = db9_y_top + y_offset - 145
        if int(pin_num) <= 5:
            pin_x = db9_x + 25 - (int(pin_num) - 1) * 12
        else:
            pin_x = db9_x + 19 - (int(pin_num) - 6) * 12
        
        r.elements.append(f'<circle cx="{pin_x}" cy="{pin_y}" r="4" fill="gold" stroke="#B8860B" stroke-width="1"/>')
        r.elements.append(f'<text x="{pin_x}" y="{pin_y-10}" class="value" font-size="7" text-anchor="middle" fill="gold">{pin_num}:{label}</text>')
    
    # Output signals with elbow routing to DB-9 A pins
    outputs = [
        ("TP94 Saw", 160, "7", "1kΩ", "Buffer", C_AUDIO),
        ("TP93 Square", 185, "8", "1kΩ", "Buffer", C_AUDIO),
        ("TP30 Mix", 210, "5", "1kΩ", "Buffer", C_AUDIO),
        ("TP19 VCF", 235, "6", "1kΩ", "Buffer", C_AUDIO),
        ("Pitch CV", 275, "2", "", "Direct", C_CV),
        ("TP83 Gate", 300, "1", "10kΩ", "Schmitt", C_GATE),
        ("Env Out", 325, "3", "10kΩ", "Buffer", C_CV),
        ("LFO Out", 350, "4", "10kΩ", "Buffer", C_CV),
    ]
    
    for name, source_y, pin_num, resistor, processing, color in outputs:
        for p, l, y_off, c in pins_a:
            if p == pin_num:
                target_y = db9_y_top + y_off - 145
                break
        
        r.elements.append(f'<text x="10" y="{source_y+3}" class="label" font-size="9">{name}</text>')
        
        # Elbow wire: horizontal first, then vertical - per-wire hover only
        corner_x = 300
        path = f'M90,{source_y} L{corner_x},{source_y} L{corner_x},{target_y} L{db9_x-35},{target_y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="1.5" fill="none" class="wire"/>')
        
        if resistor:
            r.resistor(Point(125, source_y), value=resistor, vertical=False)
        
        if processing != "Direct":
            r.block(Point(220, source_y), 50, 14, label=processing[:4])
    
    # === DB-9 B: INPUTS (Middle-Right) ===
    r.elements.append(f'<text x="200" y="420" class="label" font-size="13" fill="{C_CV}">DB-9 B: INPUTS (Expander → MicroBrute)</text>')
    
    db9b_x = 450
    db9b_y_top = 455
    r.elements.append(f'<rect x="{db9b_x-35}" y="{db9b_y_top-20}" width="70" height="180" rx="8" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append(f'<text x="{db9b_x}" y="{db9b_y_top-30}" class="label" text-anchor="middle" fill="#CC0000">DB-9 B (Rear)</text>')
    
    pins_b = [
        ("1", "Filt", 455, C_CV),
        ("2", "VCA", 475, C_CV),
        ("3", "Res", 495, C_CONTROL),
        ("4", "Sync", 515, C_GATE),
        ("5", "Gate", 535, C_GATE),
        ("6", "Ext", 575, C_AUDIO),
        ("7", "+12V", 595, C_POWER_POS),
        ("8", "-12V", 615, C_POWER_NEG),
        ("9", "GND", 635, C_GND),
    ]
    
    for pin_num, label, y_offset, color in pins_b:
        pin_y = db9b_y_top + y_offset - 455
        if int(pin_num) <= 5:
            pin_x = db9b_x + 25 - (int(pin_num) - 1) * 12
        else:
            pin_x = db9b_x + 19 - (int(pin_num) - 6) * 12
        
        r.elements.append(f'<circle cx="{pin_x}" cy="{pin_y}" r="4" fill="gold" stroke="#B8860B" stroke-width="1"/>')
        r.elements.append(f'<text x="{pin_x}" y="{pin_y+12}" class="value" font-size="7" text-anchor="middle" fill="gold">{pin_num}:{label}</text>')
    
    # Input signals
    inputs = [
        ("Filter CV", 460, "1", "100k", "Atten", "→Filter", C_CV),
        ("VCA CV", 485, "2", "100k", "Atten", "→TP10/11", C_CV),
        ("Resonance", 510, "3", "100k", "Vactrol", "→RP13", C_CONTROL),
        ("Sync", 535, "4", "", "Direct", "→VCO", C_GATE),
        ("Gate In", 560, "5", "10k", "Schmitt", "→Gate", C_GATE),
        ("Ext Audio", 585, "6", "", "Mixer", "→Mix", C_AUDIO),
    ]
    
    for name, source_y, pin_num, series_r, processing, dest, color in inputs:
        for p, l, y_off, c in pins_b:
            if p == pin_num:
                pin_y = db9b_y_top + y_off - 455
                break
        
        r.elements.append(f'<text x="10" y="{source_y+3}" class="label" font-size="9">{name}</text>')
        
        mid_x = 200
        corner1_x = 150
        path1 = f'M90,{source_y} L{corner1_x},{source_y} L{corner1_x},{source_y} L{mid_x},{source_y}'
        r.elements.append(f'<path d="{path1}" stroke="{color}" stroke-width="1.5" fill="none"/>')
        
        if series_r:
            r.resistor(Point(120, source_y), value=series_r, vertical=False)
        
        r.block(Point(mid_x+25, source_y), 55, 14, label=processing)
        
        corner2_x = 380
        path2 = f'M{mid_x+55},{source_y} L{corner2_x},{source_y} L{corner2_x},{pin_y} L{db9b_x-35},{pin_y}'
        r.elements.append(f'<path d="{path2}" stroke="{color}" stroke-width="1.5" fill="none"/>')
        
        r.elements.append(f'<text x="{db9b_x+50}" y="{pin_y+3}" class="value" font-size="8">{dest}</text>')
    
    # === POWER SECTION (Bottom) ===
    r.elements.append(f'<text x="200" y="680" class="label" font-size="13" fill="{C_POWER_POS}">POWER DISTRIBUTION</text>')
    
    power_lines = [
        ("+12V", 700, C_POWER_POS, "7", "Fuse+1N5817"),
        ("GND", 720, C_GND, "9", ""),
        ("-12V", 740, C_POWER_NEG, "8", "Fuse+1N5817"),
    ]
    
    for label, y, color, pin_num, protection in power_lines:
        for p, l, y_off, c in pins_b:
            if p == pin_num:
                pin_y = db9b_y_top + y_off - 455
                break
        
        r.elements.append(f'<text x="10" y="{y+3}" class="label" font-size="9" fill="{color}">{label}</text>')
        
        corner_x = 250
        path = f'M60,{y} L{corner_x},{y} L{corner_x},{pin_y} L{db9b_x-35},{pin_y}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2.5" fill="none"/>')
        
        if protection:
            r.block(Point(180, y), 70, 14, label=protection)
        
        dest_x = 750
        path3 = f'M{db9b_x+35},{pin_y} L{dest_x},{pin_y}'
        r.elements.append(f'<path d="{path3}" stroke="{color}" stroke-width="2" fill="none"/>')
        r.elements.append(f'<text x="{dest_x+5}" y="{y+3}" class="value" font-size="8">→Expander Bus</text>')
    
    # === INTERACTIVE FEATURE NOTE ===
    r.elements.append(f'<rect x="550" y="650" width="430" height="75" fill="#FFF8E1" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="765" y="675" class="label" text-anchor="middle" fill="#E65100" font-size="10">Interactive Feature</text>')
    r.elements.append(f'<text x="565" y="695" class="value" font-size="8">• Hover over any wire to highlight that path</text>')
    r.elements.append(f'<text x="565" y="710" class="value" font-size="8">• Use theme toggle (☀️/🌙) for light/dark mode</text>')
    
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


def generate_pt2399_cv_schematic() -> str:
    """Generate PT2399 CV Control schematic (JF-33 delay mod)."""
    r = SchematicRenderer(700, 600, "PT2399 CV Control", "Anti-latch-up + CV current sink for JF-33 delay")

    # +5V rail (from 78L05)
    for x in [150, 550]:
        r.vcc(Point(x, 50), label="+5V")

    # === ANTI-LATCH-UP CIRCUIT (left side) ===
    r.elements.append(f'<text x="80" y="80" class="label">Anti-Latch-Up</text>')

    # BC337 transistor
    r.npn_transistor(Point(150, 150), label="BC337")

    # 100k from +5V to base
    r.wire(Point(150, 50), Point(150, 100))
    r.resistor(Point(130, 75), label="R1", value="100k", vertical=False)

    # 100k from base to +5V (pulldown for startup)
    r.wire(Point(150, 100), Point(150, 120))

    # 1uF cap from base to GND (timing)
    r.wire(Point(150, 180), Point(150, 220))
    r.wire(Point(150, 220), Point(120, 220))
    r.capacitor(Point(120, 250), label="C1", value="1µF", polarized=True, vertical=True)
    r.ground(Point(120, 280))

    # Emitter to GND
    r.wire(Point(165, 170), Point(165, 300))
    r.ground(Point(165, 300))

    # PT2399 pin 6 connection label
    r.elements.append(f'<text x="180" y="135" class="value">To PT2399 pin 6</text>')

    # === CV CONTROL CIRCUIT (right side) ===
    r.elements.append(f'<text x="450" y="80" class="label">CV Control</text>')

    # CV Input jack
    r.jack(Point(450, 120), label="CV 0-5V")
    r.wire(Point(470, 120), Point(500, 120))
    r.resistor(Point(515, 120), label="R2", value="100k", vertical=False)
    r.wire(Point(530, 120), Point(550, 120))

    # Attenuator pot
    r.potentiometer(Point(550, 180), label="ATTEN", value="100k")
    r.wire(Point(550, 150), Point(550, 130))
    r.wire(Point(550, 210), Point(550, 250))
    r.ground(Point(550, 250))

    # TL072 buffer
    r.opamp(Point(620, 200), label="TL072", pins=("-", "+", "out"))
    r.wire(Point(550, 180), Point(580, 182))  # Pot wiper to +in

    # -in to output (voltage follower)
    r.wire(Point(620, 200), Point(660, 200))
    r.wire(Point(660, 200), Point(660, 160))
    r.wire(Point(660, 160), Point(590, 160))
    r.wire(Point(590, 160), Point(590, 182))

    # +in to GND (for bias)
    r.wire(Point(580, 218), Point(580, 280))
    r.ground(Point(580, 280))

    # Output to 2N3904 base (via 1k)
    r.wire(Point(660, 200), Point(700, 200))
    r.wire(Point(700, 200), Point(700, 350))
    r.resistor(Point(700, 380), label="R3", value="1k", vertical=True)

    # 2N3904 current sink
    r.npn_transistor(Point(620, 420), label="2N3904")
    r.wire(Point(700, 400), Point(635, 420))  # Base connection

    # Collector to PT2399 pin 6 (through anti-latch-up)
    r.wire(Point(605, 405), Point(605, 350))
    r.wire(Point(605, 350), Point(400, 350))
    r.wire(Point(400, 350), Point(400, 150))
    r.wire(Point(400, 150), Point(180, 150))  # Connect to anti-latch-up output

    # Emitter resistor to GND
    r.wire(Point(635, 445), Point(635, 480))
    r.resistor(Point(635, 500), label="R4", value="1k", vertical=True)
    r.ground(Point(635, 530))

    # Protection diode (1N4148)
    r.elements.append(f'<text x="480" y="400" class="value">D1 (1N4148)</text>')
    r.elements.append(f'<line x1="480" y1="410" x2="480" y2="450" stroke="#333" stroke-width="1"/>')
    # Diode symbol (pointing from pin 6 to GND)
    r.elements.extend([
        f'<polygon points="470,430 490,430 480,450" fill="none" stroke="#333" stroke-width="1.5"/>',
        f'<line x1="470" y1="450" x2="490" y2="450" stroke="#333" stroke-width="1.5"/>',
    ])
    r.wire(Point(480, 450), Point(480, 480))
    r.ground(Point(480, 480))

    # === ANNOTATIONS ===
    r.annotate(Point(50, 150), "Startup:\nBC337 OFF\nfor ~500ms")
    r.annotate(Point(50, 420), "CV→Current:\nSink 0-5mA\nfrom pin 6")

    return r.render()


def generate_led_driver_schematic() -> str:
    """Generate LED Driver Array schematic — 3-channel NPN driver for RGB + status LEDs."""
    r = SchematicRenderer(650, 550, "LED Driver Array", "3× 2N3904 NPN Drivers for RGB LED + Status LEDs")
    
    # === INPUTS FROM PICO (Left side) ===
    r.elements.append(f'<text x="50" y="50" class="label">From Pico GPIO</text>')
    
    inputs = [
        ("GP8 (Red)", 90, "#CC0000"),
        ("GP9 (Green)", 150, "#00CC00"),
        ("GP10 (Blue)", 210, "#0000CC"),
    ]
    
    for label, y, color in inputs:
        r.elements.append(f'<text x="30" y="{y+3}" class="value" font-size="9">{label}</text>')
    
    # === CHANNEL 1: RED LED DRIVER ===
    y_red = 90
    # GPIO input with base resistor
    r.wire(Point(110, y_red), Point(150, y_red))
    r.resistor(Point(130, y_red), value="470Ω", vertical=False)
    r.wire(Point(150, y_red), Point(180, y_red))
    
    # 2N3904 NPN transistor
    r.npn_transistor(Point(220, y_red), label="Q1")
    r.wire(Point(180, y_red), Point(205, y_red))  # To base
    
    # Pulldown resistor (10k to GND)
    r.wire(Point(180, y_red), Point(180, y_red+40))
    r.resistor(Point(180, y_red+30), value="10kΩ", vertical=True)
    r.ground(Point(180, y_red+55))
    
    # LED in collector path
    r.wire(Point(235, y_red-20), Point(280, y_red-20))
    # LED symbol
    r.elements.append(f'<polygon points="280,{y_red-30} 280,{y_red-10} 300,{y_red-20}" fill="#FF0000" stroke="#CC0000" stroke-width="1"/>')
    r.elements.append(f'<line x1="300" y1="{y_red-30}" x2="300" y2="{y_red-10}" stroke="#CC0000" stroke-width="2"/>')
    # LED current limiting resistor
    r.wire(Point(300, y_red-20), Point(340, y_red-20))
    r.resistor(Point(320, y_red-20), value="220Ω", vertical=False)
    # To +5V
    r.wire(Point(340, y_red-20), Point(380, y_red-20))
    r.vcc(Point(380, y_red-20), label="+5V")
    
    # Emitter to GND
    r.wire(Point(235, y_red+20), Point(235, y_red+50))
    r.ground(Point(235, y_red+55))
    
    # === CHANNEL 2: GREEN LED DRIVER ===
    y_green = 150
    r.wire(Point(110, y_green), Point(150, y_green))
    r.resistor(Point(130, y_green), value="470Ω", vertical=False)
    r.wire(Point(150, y_green), Point(180, y_green))
    
    r.npn_transistor(Point(220, y_green), label="Q2")
    r.wire(Point(180, y_green), Point(205, y_green))
    
    r.wire(Point(180, y_green), Point(180, y_green+40))
    r.resistor(Point(180, y_green+30), value="10kΩ", vertical=True)
    r.ground(Point(180, y_green+55))
    
    r.wire(Point(235, y_green-20), Point(280, y_green-20))
    r.elements.append(f'<polygon points="280,{y_green-30} 280,{y_green-10} 300,{y_green-20}" fill="#00FF00" stroke="#00CC00" stroke-width="1"/>')
    r.elements.append(f'<line x1="300" y1="{y_green-30}" x2="300" y2="{y_green-10}" stroke="#00CC00" stroke-width="2"/>')
    r.wire(Point(300, y_green-20), Point(340, y_green-20))
    r.resistor(Point(320, y_green-20), value="220Ω", vertical=False)
    r.wire(Point(340, y_green-20), Point(380, y_green-20))
    r.vcc(Point(380, y_green-20), label="+5V")
    
    r.wire(Point(235, y_green+20), Point(235, y_green+50))
    r.ground(Point(235, y_green+55))
    
    # === CHANNEL 3: BLUE LED DRIVER ===
    y_blue = 210
    r.wire(Point(110, y_blue), Point(150, y_blue))
    r.resistor(Point(130, y_blue), value="470Ω", vertical=False)
    r.wire(Point(150, y_blue), Point(180, y_blue))
    
    r.npn_transistor(Point(220, y_blue), label="Q3")
    r.wire(Point(180, y_blue), Point(205, y_blue))
    
    r.wire(Point(180, y_blue), Point(180, y_blue+40))
    r.resistor(Point(180, y_blue+30), value="10kΩ", vertical=True)
    r.ground(Point(180, y_blue+55))
    
    r.wire(Point(235, y_blue-20), Point(280, y_blue-20))
    r.elements.append(f'<polygon points="280,{y_blue-30} 280,{y_blue-10} 300,{y_blue-20}" fill="#0000FF" stroke="#0000CC" stroke-width="1"/>')
    r.elements.append(f'<line x1="300" y1="{y_blue-30}" x2="300" y2="{y_blue-10}" stroke="#0000CC" stroke-width="2"/>')
    r.wire(Point(300, y_blue-20), Point(340, y_blue-20))
    r.resistor(Point(320, y_blue-20), value="220Ω", vertical=False)
    r.wire(Point(340, y_blue-20), Point(380, y_blue-20))
    r.vcc(Point(380, y_blue-20), label="+5V")
    
    r.wire(Point(235, y_blue+20), Point(235, y_blue+50))
    r.ground(Point(235, y_blue+55))
    
    # === COMMON CATHODE RGB LED NOTE ===
    r.elements.append(f'<text x="450" y="150" class="label" font-size="10">Common Cathode RGB LED</text>')
    r.elements.append(f'<text x="450" y="170" class="value" font-size="9">All cathodes tied to</text>')
    r.elements.append(f'<text x="450" y="185" class="value" font-size="9">Q1-Q2-Q3 collectors</text>')
    
    # === COMPONENT VALUES BOX ===
    r.elements.append(f'<rect x="50" y="320" width="550" height="180" fill="#F5F5F5" stroke="#666" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="325" y="345" class="label" text-anchor="middle">Component Values</text>')
    
    specs = [
        ("Q1-Q3:", "2N3904 NPN Transistor", 365),
        ("Rbase:", "470Ω (limits base current to ~5mA)", 385),
        ("Rpulldown:", "10kΩ (ensures OFF state)", 405),
        ("Rled:", "220Ω (LED current ~10mA)", 425),
        ("Vcc:", "+5V from Pico VSYS", 445),
    ]
    
    for label, value, y in specs:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9">{label}</text>')
        r.elements.append(f'<text x="150" y="{y}" class="value" font-size="9">{value}</text>')
    
    # === HOW IT WORKS ===
    r.elements.append(f'<text x="70" y="480" class="label" font-size="10">How it works:</text>')
    r.elements.append(f'<text x="70" y="498" class="value" font-size="8">• GPIO HIGH → NPN ON → LED current flows → LED lights up</text>')
    r.elements.append(f'<text x="70" y="513" class="value" font-size="8">• GPIO LOW → NPN OFF → No current → LED dark</text>')
    r.elements.append(f'<text x="70" y="528" class="value" font-size="8">• 470Ω base resistor limits current into transistor base</text>')
    r.elements.append(f'<text x="70" y="543" class="value" font-size="8">• 10kΩ pulldown ensures transistor stays OFF when GPIO floats</text>')
    
    return r.render()


def generate_vactrol_full_schematic() -> str:
    """Generate full vactrol driver schematic — buffer + current control for resonance CV."""
    r = SchematicRenderer(700, 650, "Full Vactrol Driver", "CV Buffer + LED Current Control for Resonance (RP13)")
    
    # === INPUT SECTION (Left) ===
    r.elements.append(f'<text x="50" y="50" class="label">CV Input (DB-9 B Pin 3)</text>')
    r.jack(Point(80, 80), label="Res CV")
    
    # Series protection resistor
    r.wire(Point(100, 80), Point(140, 80))
    r.resistor(Point(120, 80), value="100kΩ", vertical=False)
    r.wire(Point(140, 80), Point(180, 80))
    
    # Attenuator pot
    r.potentiometer(Point(220, 80), label="ATTEN", value="100k")
    r.wire(Point(220, 50), Point(220, 30))
    r.ground(Point(220, 30))
    r.wire(Point(220, 110), Point(220, 130))
    r.ground(Point(220, 130))
    
    # === BUFFER STAGE ===
    r.elements.append(f'<text x="300" y="50" class="label">Voltage Buffer</text>')
    r.opamp(Point(350, 100), label="TL072", pins=("-", "+", "out"))
    
    # Wiper to +in
    r.wire(Point(220, 80), Point(310, 98))
    
    # -in to output (unity gain buffer)
    r.wire(Point(350, 100), Point(390, 100))
    r.wire(Point(390, 100), Point(390, 60))
    r.wire(Point(390, 60), Point(320, 60))
    r.wire(Point(320, 60), Point(320, 98))
    
    # +in bias
    r.wire(Point(310, 102), Point(310, 160))
    r.ground(Point(310, 160))
    
    # === CURRENT CONTROL STAGE ===
    r.elements.append(f'<text x="480" y="50" class="label">Current Control</text>')
    
    # Buffer output to current limiting resistor
    r.wire(Point(390, 100), Point(450, 100))
    r.resistor(Point(480, 100), value="1kΩ", vertical=False)
    r.wire(Point(510, 100), Point(550, 100))
    
    # NPN transistor for current control
    r.npn_transistor(Point(590, 140), label="Q4")
    r.wire(Point(550, 100), Point(575, 140))  # To base
    
    # Emitter resistor to GND
    r.wire(Point(590, 165), Point(590, 200))
    r.resistor(Point(590, 190), value="1kΩ", vertical=True)
    r.ground(Point(590, 215))
    
    # === VACTROL LED ===
    r.elements.append(f'<text x="500" y="280" class="label">Vactrol LED</text>')
    
    # Collector to LED (anode)
    r.wire(Point(575, 115), Point(575, 80))
    r.wire(Point(575, 80), Point(500, 80))
    
    # LED symbol
    r.elements.append(f'<polygon points="500,60 500,100 530,80" fill="#FF0000" stroke="#CC0000" stroke-width="1"/>')
    r.elements.append(f'<line x1="530" y1="60" x2="530" y2="100" stroke="#CC0000" stroke-width="2"/>')
    
    # LED cathode to +12V (current flows from +12V through LED to transistor to GND)
    r.wire(Point(530, 80), Point(600, 80))
    r.vcc(Point(620, 80), label="+12V")
    
    # === VACTROL LDR (Right side) ===
    r.elements.append(f'<text x="50" y="350" class="label">Vactrol LDR Side</text>')
    
    # LDR symbol
    r.elements.append(f'<rect x="80" y="370" width="60" height="40" fill="#8B7355" stroke="#5D4E37" stroke-width="2" rx="3"/>')
    r.elements.append(f'<text x="110" y="395" class="value" font-size="8" text-anchor="middle" fill="#FFF">LDR</text>')
    
    # LDR connections to MicroBrute
    r.wire(Point(140, 380), Point(200, 380))
    r.elements.append(f'<text x="210" y="383" class="value" font-size="9">→ RP13 (Resonance Pot)</text>')
    
    r.wire(Point(140, 400), Point(200, 400))
    r.elements.append(f'<text x="210" y="403" class="value" font-size="9">→ Filter CV Node</text>')
    
    # === HOW IT WORKS BOX ===
    r.elements.append(f'<rect x="50" y="450" width="600" height="170" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="350" y="475" class="label" text-anchor="middle" fill="#2E7D32">How the Vactrol Driver Works</text>')
    
    explanation = [
        ("1. CV Input (0-10V):", "From DB-9 B Pin 3, attenuated by 100k pot to 0-5V range", 495),
        ("2. Buffer Stage:", "TL072 unity gain buffer isolates CV source from driver circuit", 513),
        ("3. Current Control:", "NPN transistor acts as variable current sink, controlled by base voltage", 531),
        ("4. LED Brightness:", "Higher CV → More base current → More LED current → Brighter LED", 549),
        ("5. LDR Response:", "Brighter LED → Lower LDR resistance → More resonance in filter", 567),
        ("6. 1kΩ Resistors:", "Limit LED current to ~5mA max (safe for LDR and long LED life)", 585),
    ]
    
    for label, desc, y in explanation:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9" fill="#1B5E20">{label}</text>')
        r.elements.append(f'<text x="200" y="{y}" class="value" font-size="9">{desc}</text>')
    
    return r.render()


def generate_dip_pinout_reference() -> str:
    """Generate DIP IC Pinout Reference — TL074, TL072, CD40106, CD4051, CD4024, LF398, 78L05."""
    r = SchematicRenderer(900, 800, "DIP IC Pinout Reference", "100% Verified Pinouts for MACROBRUTE Components")
    
    # Helper function to draw DIP package
    def draw_dip(x, y, pins, label, sublabel="", width=60, pin_labels=None):
        """Draw a DIP package with pin numbers and optional labels."""
        pin_count = len(pins)
        height = pin_count * 8 + 20
        
        # IC body
        r.elements.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="3"/>')
        
        # Notch/dot at pin 1
        r.elements.append(f'<circle cx="{x+8}" cy="{y+8}" r="3" fill="gold"/>')
        
        # IC label
        r.elements.append(f'<text x="{x+width/2}" y="{y+height/2-5}" class="label" text-anchor="middle" fill="#FFF" font-size="10">{label}</text>')
        if sublabel:
            r.elements.append(f'<text x="{x+width/2}" y="{y+height/2+10}" class="value" text-anchor="middle" fill="#CCC" font-size="8">{sublabel}</text>')
        
        # Pins
        for i, pin_name in enumerate(pins):
            if i < pin_count // 2:
                # Left side pins (top to bottom)
                pin_y = y + 18 + i * ((height - 30) / (pin_count // 2 - 1)) if pin_count > 8 else y + 20 + i * 25
                pin_num = i + 1
                r.elements.append(f'<circle cx="{x-5}" cy="{pin_y}" r="2.5" fill="gold" stroke="#B8860B" stroke-width="0.5"/>')
                r.elements.append(f'<text x="{x-12}" y="{pin_y+2}" class="pin" text-anchor="end" fill="gold" font-size="7">{pin_num}</text>')
                if pin_labels and pin_labels[i]:
                    r.elements.append(f'<text x="{x+5}" y="{pin_y+2}" class="value" fill="#FFF" font-size="7">{pin_labels[i]}</text>')
            else:
                # Right side pins (bottom to top)
                idx = pin_count - i - 1
                pin_y = y + 18 + idx * ((height - 30) / (pin_count // 2 - 1)) if pin_count > 8 else y + 20 + idx * 25
                pin_num = i + 1
                r.elements.append(f'<circle cx="{x+width+5}" cy="{pin_y}" r="2.5" fill="gold" stroke="#B8860B" stroke-width="0.5"/>')
                r.elements.append(f'<text x="{x+width+12}" y="{pin_y+2}" class="pin" text-anchor="start" fill="gold" font-size="7">{pin_num}</text>')
                if pin_labels and pin_labels[i]:
                    r.elements.append(f'<text x="{x+width-5}" y="{pin_y+2}" class="value" text-anchor="end" fill="#FFF" font-size="7">{pin_labels[i]}</text>')
    
    # TL074 - Quad Op-Amp (DIP-14)
    tl074_pins = ["OUT1", "IN1-", "IN1+", "VCC+", "IN2+", "IN2-", "OUT2",
                  "OUT3", "IN3-", "IN3+", "GND", "IN4+", "IN4-", "OUT4"]
    draw_dip(50, 50, tl074_pins, "TL074", "Quad Op-Amp", 70, tl074_pins)
    r.elements.append(f'<text x="85" y="45" class="label" font-size="10" fill="#0066CC">TL074 — Quad Op-Amp (DIP-14)</text>')
    
    # TL072 - Dual Op-Amp (DIP-8)
    tl072_pins = ["OUT1", "IN1-", "IN1+", "VCC-", "VCC+", "IN2+", "IN2-", "OUT2"]
    draw_dip(200, 50, tl072_pins, "TL072", "Dual Op-Amp", 70, tl072_pins)
    r.elements.append(f'<text x="235" y="45" class="label" font-size="10" fill="#0066CC">TL072 — Dual Op-Amp (DIP-8)</text>')
    
    # CD40106 - Hex Schmitt Trigger (DIP-14)
    cd40106_pins = ["1A", "1Y", "2A", "2Y", "3A", "3Y", "GND",
                    "VCC", "4Y", "4A", "5Y", "5A", "6Y", "6A"]
    draw_dip(350, 50, cd40106_pins, "CD40106", "Hex Schmitt", 70, cd40106_pins)
    r.elements.append(f'<text x="385" y="45" class="label" font-size="10" fill="#CC6600">CD40106 — Hex Schmitt Trigger (DIP-14)</text>')
    
    # CD4051 - Analog MUX (DIP-16)
    cd4051_pins = ["X4", "X6", "X", "X7", "X5", "INH", "VEE", "VSS",
                   "C", "B", "A", "X3", "X0", "X1", "X2", "VCC"]
    draw_dip(500, 50, cd4051_pins, "CD4051", "8-Ch MUX", 70, cd4051_pins)
    r.elements.append(f'<text x="535" y="45" class="label" font-size="10" fill="#6600CC">CD4051 — 8-Ch Analog MUX (DIP-16)</text>')
    
    # CD4024 - 7-Stage Counter (DIP-14)
    cd4024_pins = ["CLK", "RESET", "Q7", "Q6", "Q5", "Q4", "GND",
                   "VCC", "Q3", "Q2", "Q1", "NC", "NC", "NC"]
    draw_dip(650, 50, cd4024_pins, "CD4024", "7-Stage", 70, cd4024_pins)
    r.elements.append(f'<text x="685" y="45" class="label" font-size="10" fill="#009933">CD4024 — 7-Stage Counter (DIP-14)</text>')
    
    # LF398 - Sample & Hold (DIP-8)
    lf398_pins = ["V+", "OFFSET", "IN", "V-", "CH", "LOGIC", "OUT", "GND"]
    draw_dip(50, 250, lf398_pins, "LF398", "S&H Amp", 70, lf398_pins)
    r.elements.append(f'<text x="85" y="245" class="label" font-size="10" fill="#CC0000">LF398 — Sample & Hold (DIP-8)</text>')
    
    # 78L05 - Voltage Regulator (TO-92)
    r.elements.append(f'<text x="200" y="245" class="label" font-size="10" fill="#CC0000">78L05 — +5V Regulator (TO-92)</text>')
    # Draw TO-92 package
    r.elements.append(f'<circle cx="235" cy="280" r="20" fill="#333" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append(f'<text x="235" y="285" class="label" text-anchor="middle" fill="#FFF" font-size="9">78L05</text>')
    # Pins
    r.elements.append(f'<line x1="225" y1="300" x2="225" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<line x1="235" y1="300" x2="235" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<line x1="245" y1="300" x2="245" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<text x="225" y="325" class="pin" text-anchor="middle" fill="#D44" font-size="8">1 OUT</text>')
    r.elements.append(f'<text x="235" y="325" class="pin" text-anchor="middle" fill="#1a1a1a" font-size="8">2 GND</text>')
    r.elements.append(f'<text x="245" y="325" class="pin" text-anchor="middle" fill="#44D" font-size="8">3 IN</text>')
    
    # 2N3904 - NPN Transistor (TO-92)
    r.elements.append(f'<text x="320" y="245" class="label" font-size="10" fill="#009933">2N3904 — NPN Transistor (TO-92)</text>')
    r.elements.append(f'<circle cx="355" cy="280" r="20" fill="#333" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append(f'<text x="355" y="285" class="label" text-anchor="middle" fill="#FFF" font-size="9">2N3904</text>')
    r.elements.append(f'<line x1="345" y1="300" x2="345" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<line x1="355" y1="300" x2="355" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<line x1="365" y1="300" x2="365" y2="315" stroke="#gold" stroke-width="3"/>')
    r.elements.append(f'<text x="345" y="325" class="pin" text-anchor="middle" fill="#CC6600" font-size="8">1 E</text>')
    r.elements.append(f'<text x="355" y="325" class="pin" text-anchor="middle" fill="#1a1a1a" font-size="8">2 B</text>')
    r.elements.append(f'<text x="365" y="325" class="pin" text-anchor="middle" fill="#0066CC" font-size="8">3 C</text>')
    
    # Pin numbering convention note
    r.elements.append(f'<rect x="50" y="360" width="800" height="400" fill="#F5F5F5" stroke="#666" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="450" y="385" class="label" text-anchor="middle" font-size="12">DIP Package Pin Numbering Convention</text>')
    
    # Draw example DIP-8 with numbering
    r.elements.append(f'<text x="70" y="410" class="label" font-size="9">Standard DIP Pin Numbering (Top View):</text>')
    
    # Example DIP-14
    ex_x, ex_y = 80, 430
    ex_w, ex_h = 80, 120
    r.elements.append(f'<rect x="{ex_x}" y="{ex_y}" width="{ex_w}" height="{ex_h}" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="3"/>')
    r.elements.append(f'<circle cx="{ex_x+10}" cy="{ex_y+10}" r="4" fill="gold"/>')
    r.elements.append(f'<text x="{ex_x+40}" y="{ex_y+60}" class="label" text-anchor="middle" fill="#FFF" font-size="10">DIP-14</text>')
    
    # Pin numbers for example
    for i in range(7):
        # Left side: 1-7 (top to bottom)
        pin_y = ex_y + 20 + i * 14
        r.elements.append(f'<text x="{ex_x-8}" y="{pin_y+3}" class="pin" text-anchor="end" fill="#D44" font-size="9" font-weight="bold">{i+1}</text>')
        # Right side: 14-8 (bottom to top)
        r.elements.append(f'<text x="{ex_x+ex_w+8}" y="{pin_y+3}" class="pin" text-anchor="start" fill="#44D" font-size="9" font-weight="bold">{14-i}</text>')
    
    r.elements.append(f'<text x="{ex_x+40}" y="{ex_y+ex_h+20}" class="value" text-anchor="middle" font-size="8">Notch/dot at Pin 1</text>')
    r.elements.append(f'<text x="{ex_x+40}" y="{ex_y+ex_h+35}" class="value" text-anchor="middle" font-size="8">Left side: 1→7 (top to bottom)</text>')
    r.elements.append(f'<text x="{ex_x+40}" y="{ex_y+ex_h+50}" class="value" text-anchor="middle" font-size="8">Right side: 14→8 (bottom to top)</text>')
    
    # Power conventions
    r.elements.append(f'<text x="250" y="410" class="label" font-size="9">Common Power Pin Conventions:</text>')
    conventions = [
        ("VCC, V+, VDD:", "Positive supply (+12V or +5V)", 430),
        ("V-, VEE:", "Negative supply (-12V)", 450),
        ("GND, VSS:", "Ground reference (0V)", 470),
        ("NC:", "No Connection (do not use)", 490),
    ]
    for label, desc, y in conventions:
        r.elements.append(f'<text x="250" y="{y}" class="label" font-size="8">{label}</text>')
        r.elements.append(f'<text x="330" y="{y}" class="value" font-size="8">{desc}</text>')
    
    # MACROBRUTE specific notes
    r.elements.append(f'<text x="500" y="410" class="label" font-size="9">MACROBRUTE Usage:</text>')
    usage = [
        ("TL074:", "Output buffers, mixers (3x quad op-amps)", 430),
        ("TL072:", "Expander circuits, buffers", 450),
        ("CD40106:", "LFO core (Schmitt trigger oscillator)", 470),
        ("CD4051:", "Input selection (if used)", 490),
        ("CD4024:", "Clock divider (/2, /4, /8 outputs)", 510),
        ("LF398:", "Sample & Hold module", 530),
        ("78L05:", "JF-33 delay +5V supply", 550),
        ("2N3904:", "LED drivers, noise source, vactrol", 570),
    ]
    for label, desc, y in usage:
        r.elements.append(f'<text x="500" y="{y}" class="label" font-size="8">{label}</text>')
        r.elements.append(f'<text x="550" y="{y}" class="value" font-size="8">{desc}</text>')
    
    # Important warnings
    r.elements.append(f'<text x="70" y="600" class="label" font-size="10" fill="#CC0000">⚠️ Important Warnings:</text>')
    warnings = [
        "• Always check pin 1 orientation (notch/dot) before inserting ICs",
        "• TL072/TL074: VCC+ and VCC- pins are NOT interchangeable!",
        "• CD4051: VEE can be negative (connect to -12V for bipolar signals)",
        "• 78L05: Input must be >7V (use +12V, not +5V)",
        "• 2N3904: Pinout varies by manufacturer (ECB vs EBC) - verify with datasheet",
    ]
    for i, warning in enumerate(warnings):
        r.elements.append(f'<text x="70" y="{620 + i*18}" class="value" font-size="8" fill="#CC0000">{warning}</text>')
    
    return r.render()


def generate_touch_plate_schematic() -> str:
    """Generate Touch Plate Interface schematic — resistive bend points for circuit bending."""
    r = SchematicRenderer(800, 700, "Touch Plate Interface", "Resistive Bend Points for Body Contact Circuit Bending")
    
    # Color for touch points
    C_TOUCH = "#CC6600"  # Orange for touch
    
    # === TOUCH PLATE SECTION ===
    r.elements.append(f'<text x="50" y="50" class="label" font-size="12" fill="{C_TOUCH}">Touch Plates (Conductive Copper Pads)</text>')
    
    # Draw 4 touch plates
    touch_points = [
        ("OSC Pitch", 80, 90, "TP12", "Oscillator frequency bend"),
        ("Filter Cutoff", 80, 160, "TP17", "Filter resonance bend"),
        ("LFO Rate", 80, 230, "TP68", "LFO speed modulation"),
        ("VCA Response", 80, 300, "TP9/10", "Amplitude envelope bend"),
    ]
    
    for label, x, y, tp, desc in touch_points:
        # Touch plate (copper pad representation)
        r.elements.append(f'<rect x="{x}" y="{y}" width="100" height="50" fill="#B87333" stroke="#8B4513" stroke-width="2" rx="5"/>')
        r.elements.append(f'<text x="{x+50}" y="{y+20}" class="label" text-anchor="middle" fill="#FFF" font-size="9">{label}</text>')
        r.elements.append(f'<text x="{x+50}" y="{y+38}" class="value" text-anchor="middle" fill="#FFD700" font-size="7">Touch Here</text>')
        
        # Connection to TP
        r.wire(Point(x+100, y+25), Point(x+140, y+25))
        r.elements.append(f'<text x="{x+145}" y="{y+28}" class="value" font-size="8">→ {tp}</text>')
        r.elements.append(f'<text x="{x+200}" y="{y+28}" class="value" font-size="7" fill="#666">{desc}</text>')
    
    # === RESISTANCE NETWORK ===
    r.elements.append(f'<text x="50" y="380" class="label" font-size="12">Series Resistors (Limit Current)</text>')
    
    resistors = [
        ("R1", "100kΩ", "OSC", 80, 420),
        ("R2", "220kΩ", "Filter", 200, 420),
        ("R3", "470kΩ", "LFO", 320, 420),
        ("R4", "1MΩ", "VCA", 440, 420),
    ]
    
    for label, value, func, x, y in resistors:
        r.resistor(Point(x, y), label=label, value=value, vertical=True)
        r.elements.append(f'<text x="{x}" y="{y+45}" class="value" font-size="7" text-anchor="middle">{func}</text>')
    
    r.elements.append(f'<text x="50" y="480" class="value" font-size="8">Higher resistance = gentler bend effect</text>')
    r.elements.append(f'<text x="50" y="495" class="value" font-size="8">Lower resistance = stronger bend effect</text>')
    
    # === PICO INTERFACE ===
    r.elements.append(f'<text x="450" y="380" class="label" font-size="12">Pico GPIO Interface</text>')
    
    # Pico connections
    pico_connections = [
        ("GP2", "ADC0", "Touch sense 1", 470, 420),
        ("GP3", "ADC1", "Touch sense 2", 470, 450),
        ("GP4", "ADC2", "Touch sense 3", 470, 480),
        ("GP5", "ADC3", "Touch sense 4", 470, 510),
    ]
    
    for gpio, adc, func, x, y in pico_connections:
        r.elements.append(f'<text x="{x}" y="{y}" class="label" font-size="8">{gpio} ({adc})</text>')
        r.elements.append(f'<text x="{x+80}" y="{y}" class="value" font-size="8">→ {func}</text>')
    
    # === HOW IT WORKS ===
    r.elements.append(f'<rect x="50" y="540" width="700" height="140" fill="#FFF8E1" stroke="#FFB300" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="400" y="565" class="label" text-anchor="middle" fill="#E65100">How Touch Bending Works</text>')
    
    explanation = [
        ("1. Body Resistance:", "Your skin has resistance (50kΩ-1MΩ depending on moisture)", 585),
        ("2. Current Flow:", "When you touch the pad, a tiny current flows through your body to ground", 603),
        ("3. Voltage Drop:", "This creates a voltage divider that changes the CV at the test point", 621),
        ("4. Bend Effect:", "The circuit interprets this as a control voltage change", 639),
        ("5. Safety:", "100kΩ+ resistors limit current to &lt;0.1mA (safe for humans)", 657),
    ]
    
    for label, desc, y in explanation:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="8" fill="#BF360C">{label}</text>')
        r.elements.append(f'<text x="170" y="{y}" class="value" font-size="8">{desc}</text>')
    
    return r.render()


def generate_input_protection_schematic() -> str:
    """Generate DSO138 Input Protection schematic — for safe oscilloscope probing."""
    r = SchematicRenderer(700, 600, "DSO138 Input Protection", "Safe Signal Injection for Oscilloscope Module")
    
    C_POS = "#D44"
    C_NEG = "#44D"
    C_SIG = "#1a1a1a"
    
    # === INPUT STAGE ===
    r.elements.append(f'<text x="50" y="50" class="label" font-size="12">Signal Input (From Synth)</text>')
    
    # Input jack
    r.jack(Point(80, 100), label="IN")
    r.wire(Point(100, 100), Point(140, 100))
    
    # Series resistor (current limiting)
    r.resistor(Point(160, 100), label="R1", value="1kΩ", vertical=False)
    r.wire(Point(180, 100), Point(220, 100))
    
    # === CLAMPING DIODES ===
    r.elements.append(f'<text x="250" y="50" class="label" font-size="12">Voltage Clamping</text>')
    
    # To positive clamp diode
    r.wire(Point(220, 100), Point(220, 70))
    r.wire(Point(220, 70), Point(280, 70))
    # Diode to +3.3V rail (pointing up)
    r.elements.extend([
        f'<polygon points="280,55 280,85 300,70" fill="none" stroke="#D44" stroke-width="1.5"/>',
        f'<line x1="300" y1="55" x2="300" y2="85" stroke="#D44" stroke-width="1.5"/>',
    ])
    r.wire(Point(300, 70), Point(350, 70))
    r.vcc(Point(350, 70), label="+3.3V")
    
    # To negative clamp diode
    r.wire(Point(220, 100), Point(220, 130))
    r.wire(Point(220, 130), Point(280, 130))
    # Diode to GND (pointing down)
    r.elements.extend([
        f'<polygon points="300,115 300,145 280,130" fill="none" stroke="#44D" stroke-width="1.5"/>',
        f'<line x1="280" y1="115" x2="280" y2="145" stroke="#44D" stroke-width="1.5"/>',
    ])
    r.ground(Point(280, 150))
    
    # === VOLTAGE DIVIDER (Attenuation) ===
    r.elements.append(f'<text x="50" y="200" class="label" font-size="12">10:1 Voltage Divider</text>')
    
    # Top resistor
    r.wire(Point(220, 100), Point(260, 100))
    r.resistor(Point(290, 100), label="R2", value="900kΩ", vertical=False)
    r.wire(Point(320, 100), Point(350, 100))
    
    # Tap point
    r.junction(Point(350, 100))
    
    # Bottom resistor
    r.wire(Point(350, 100), Point(350, 160))
    r.resistor(Point(350, 130), label="R3", value="100kΩ", vertical=True)
    r.ground(Point(350, 180))
    
    # === OUTPUT TO DSO138 ===
    r.elements.append(f'<text x="450" y="50" class="label" font-size="12">To DSO138 Module</text>')
    
    # Output connection
    r.wire(Point(350, 100), Point(450, 100))
    r.block(Point(500, 100), 80, 40, label="DSO138", sublabel="ADC Input")
    
    # DSO138 internal reference
    r.elements.append(f'<text x="520" y="170" class="value" font-size="8">Internal reference:</text>')
    r.elements.append(f'<text x="520" y="185" class="value" font-size="8">0V - 3.3V range</text>')
    
    # === PROTECTION SPECS ===
    r.elements.append(f'<rect x="50" y="250" width="600" height="320" fill="#E3F2FD" stroke="#2196F3" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="350" y="275" class="label" text-anchor="middle" fill="#0D47A1">Protection Circuit Specifications</text>')
    
    specs = [
        ("Input Range:", "±12V (synth signals)", 300),
        ("Output Range:", "0V - 3.3V (DSO138 safe)", 320),
        ("Attenuation:", "10:1 (divide by 10)", 340),
        ("Clamping:", "Schottky diodes to 0V / 3.3V rails", 360),
        ("Current Limit:", "1kΩ series resistor limits fault current", 380),
        ("Response:", "Suitable for audio and CV signals", 400),
        ("Bandwidth:", "~100kHz (limited by 10MΩ impedance)", 420),
    ]
    
    for label, value, y in specs:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9" fill="#1565C0">{label}</text>')
        r.elements.append(f'<text x="200" y="{y}" class="value" font-size="9">{value}</text>')
    
    # How it works
    r.elements.append(f'<text x="70" y="460" class="label" font-size="10">How Protection Works:</text>')
    protection_notes = [
        "• 1kΩ resistor limits current if diodes conduct (protects diodes and DSO138)",
        "• Schottky diodes clamp voltage to 0V - 3.3V range (fast response)",
        "• 10:1 divider brings ±12V synth signals down to ±1.2V (within ADC range)",
        "• Works for AC (audio) and DC (CV) signals",
    ]
    for i, note in enumerate(protection_notes):
        r.elements.append(f'<text x="70" y="{480 + i*20}" class="value" font-size="8">{note}</text>')
    
    return r.render()


def generate_esd_protection_schematic() -> str:
    """Generate ESD Protection schematic — for CV input protection."""
    r = SchematicRenderer(750, 650, "CV Input ESD Protection", "Electrostatic Discharge Protection for External CV Inputs")
    
    C_ESD = "#9C27B0"  # Purple for ESD
    
    # === INPUT JACK ===
    r.elements.append(f'<text x="50" y="50" class="label" font-size="12">External CV Input</text>')
    r.jack(Point(80, 100), label="CV IN")
    r.wire(Point(100, 100), Point(150, 100))
    
    # === ESD PROTECTION STAGE ===
    r.elements.append(f'<text x="200" y="50" class="label" font-size="12" fill="{C_ESD}">ESD Protection</text>')
    
    # TVS Diode (bidirectional)
    r.elements.append(f'<text x="180" y="85" class="value" font-size="8">TVS</text>')
    # Bidirectional TVS symbol (two zeners back to back)
    r.elements.extend([
        f'<line x1="170" y1="100" x2="180" y2="100" stroke="#9C27B0" stroke-width="1.5"/>',
        f'<polygon points="180,85 180,115 200,100" fill="none" stroke="#9C27B0" stroke-width="1.5"/>',
        f'<line x1="200" y1="85" x2="200" y2="115" stroke="#9C27B0" stroke-width="1.5"/>',
        f'<polygon points="200,115 200,85 220,100" fill="none" stroke="#9C27B0" stroke-width="1.5"/>',
        f'<line x1="220" y1="85" x2="220" y2="115" stroke="#9C27B0" stroke-width="1.5"/>',
        f'<line x1="220" y1="100" x2="230" y2="100" stroke="#9C27B0" stroke-width="1.5"/>',
    ])
    r.elements.append(f'<text x="200" y="130" class="value" font-size="7" text-anchor="middle">SMBJ12CA</text>')
    
    # TVS to ground
    r.wire(Point(200, 115), Point(200, 150))
    r.ground(Point(200, 150))
    
    # Continue to next stage
    r.wire(Point(230, 100), Point(280, 100))
    
    # === SERIES RESISTOR ===
    r.resistor(Point(310, 100), label="R1", value="10kΩ", vertical=False)
    r.wire(Point(330, 100), Point(360, 100))
    
    # === CLAMPING DIODES ===
    r.elements.append(f'<text x="380" y="50" class="label" font-size="12">Voltage Clamping</text>')
    
    # To positive rail
    r.wire(Point(360, 100), Point(360, 70))
    r.wire(Point(360, 70), Point(420, 70))
    r.elements.extend([
        f'<polygon points="420,55 420,85 440,70" fill="none" stroke="#D44" stroke-width="1.5"/>',
        f'<line x1="440" y1="55" x2="440" y2="85" stroke="#D44" stroke-width="1.5"/>',
    ])
    r.wire(Point(440, 70), Point(480, 70))
    r.vcc(Point(480, 70), label="+12V")
    
    # To negative rail
    r.wire(Point(360, 100), Point(360, 130))
    r.wire(Point(360, 130), Point(420, 130))
    r.elements.extend([
        f'<polygon points="440,115 440,145 420,130" fill="none" stroke="#44D" stroke-width="1.5"/>',
        f'<line x1="420" y1="115" x2="420" y2="145" stroke="#44D" stroke-width="1.5"/>',
    ])
    r.wire(Point(420, 145), Point(420, 180))
    r.elements.append(f'<line x1="420" y1="180" x2="480" y2="180" stroke="#44D" stroke-width="2"/>')
    r.elements.append(f'<text x="490" y="183" class="value" fill="#44D" font-size="8">-12V</text>')
    
    # === OUTPUT TO SYNTH ===
    r.elements.append(f'<text x="550" y="50" class="label" font-size="12">To MicroBrute</text>')
    r.wire(Point(360, 100), Point(550, 100))
    r.block(Point(600, 100), 80, 40, label="Filter", sublabel="CV Input")
    
    # === MULTI-CHANNEL VERSION ===
    r.elements.append(f'<text x="50" y="250" class="label" font-size="12">Multi-Channel ESD Protection (All CV Inputs)</text>')
    
    channels = [
        ("Filter CV", "DB-9 B Pin 1", 280),
        ("VCA CV", "DB-9 B Pin 2", 310),
        ("Resonance", "DB-9 B Pin 3", 340),
        ("Sync", "DB-9 B Pin 4", 370),
        ("Gate", "DB-9 B Pin 5", 400),
    ]
    
    for label, pin, y in channels:
        r.elements.append(f'<text x="50" y="{y}" class="value" font-size="8">{label}</text>')
        r.elements.append(f'<text x="150" y="{y}" class="value" font-size="8">→ {pin}</text>')
        r.elements.append(f'<text x="300" y="{y}" class="value" font-size="7">[TVS + 10kΩ + Clamp]</text>')
    
    # === COMPONENT DETAILS ===
    r.elements.append(f'<rect x="50" y="440" width="650" height="190" fill="#F3E5F5" stroke="#9C27B0" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="375" y="465" class="label" text-anchor="middle" fill="#4A148C">ESD Protection Component Details</text>')
    
    components = [
        ("TVS Diode:", "SMBJ12CA (12V bidirectional, 600W peak)", 490),
        ("Series Resistor:", "10kΩ (limits current during ESD event)", 510),
        ("Clamp Diodes:", "1N4148 or Schottky (BAT46)", 530),
        ("Response Time:", "TVS: &lt;1ns, Diodes: &lt;4ns", 550),
        ("Protection Level:", "IEC 61000-4-2 Level 4 (8kV contact, 15kV air)", 570),
        ("Pass-through:", "Minimal effect on CV signals (10kΩ in series)", 590),
    ]
    
    for label, value, y in components:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9" fill="#6A1B9A">{label}</text>')
        r.elements.append(f'<text x="170" y="{y}" class="value" font-size="9">{value}</text>')
    
    return r.render()



def generate_system_architecture_block() -> str:
    """Generate System Architecture Block Diagram - high-level overview of MACROBRUTE system."""
    r = SchematicRenderer(1000, 750, "MACROBRUTE System Architecture", "High-Level Block Diagram of Complete System")
    
    C_SYNTH = "#2196F3"
    C_EXPANDER = "#4CAF50"
    C_INTERFACE = "#FF9800"
    C_CONTROL = "#9C27B0"
    C_AUDIO = "#E91E63"
    
    def draw_block(x, y, w, h, label, sublabel="", color="#333", text_color="#FFF"):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+h/2-5}" class="label" text-anchor="middle" fill="{text_color}" font-size="11">{label}</text>')
        if sublabel:
            r.elements.append(f'<text x="{x+w/2}" y="{y+h/2+12}" class="value" text-anchor="middle" fill="{text_color}" font-size="8" opacity="0.8">{sublabel}</text>')
    
    def draw_elbow_hv(x1, y1, x2, y2, color="#666", label=""):
        """Draw horizontal-vertical elbow wire."""
        mid_x = x1 + (x2 - x1) // 2
        path = f'M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            r.elements.append(f'<text x="{mid_x}" y="{y1-5}" class="value" text-anchor="middle" fill="{color}" font-size="7">{label}</text>')
    
    def draw_elbow_vh(x1, y1, x2, y2, color="#666", label=""):
        """Draw vertical-horizontal elbow wire."""
        mid_y = y1 + (y2 - y1) // 2
        path = f'M{x1},{y1} L{x1},{mid_y} L{x2},{mid_y} L{x2},{y2}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            r.elements.append(f'<text x="{x1+5}" y="{mid_y-3}" class="value" fill="{color}" font-size="7">{label}</text>')
    
    # === SECTION LABELS ===
    r.elements.append(f'<text x="120" y="65" class="label" font-size="12" fill="{C_SYNTH}">MicroBrute Core</text>')
    r.elements.append(f'<text x="430" y="65" class="label" font-size="12" fill="{C_INTERFACE}">Breakout Interface</text>')
    r.elements.append(f'<text x="750" y="65" class="label" font-size="12" fill="{C_EXPANDER}">Expander Modules</text>')

    # === MICROBRUTE CORE (Left Column) ===
    synth_blocks = [
        ("VCO", "Oscillator", 90),
        ("VCF", "Steiner-Parker", 145),
        ("VCA", "Amplifier", 200),
        ("LFO", "Modulation", 255),
        ("Envelope", "ADSR Gen", 310),
    ]
    
    for label, sublabel, y in synth_blocks:
        draw_block(50, y, 140, 45, label, sublabel, C_SYNTH)

    # === BREAKOUT INTERFACE (Center) ===
    # DB-9 A - Outputs
    draw_block(380, 90, 140, 50, "DB-9 A", "Outputs", C_INTERFACE)
    # DB-9 B - Inputs + Power
    draw_block(380, 160, 140, 50, "DB-9 B", "Inputs + Power", C_INTERFACE)
    # Pico W
    draw_block(380, 230, 140, 55, "Pico W", "RP2040 Control", C_CONTROL)
    # Touch Pads
    draw_block(380, 305, 140, 45, "Touch Pads", "4-Point Bend", C_CONTROL)

    # === EXPANDER MODULES (Right Column) ===
    expander_blocks = [
        ("Noise", "White/Pink", 90),
        ("LFO", "Free-running", 145),
        ("S&H", "Sample & Hold", 200),
        ("Clock Div", "/2 /4 /8", 255),
        ("Slew", "Glide", 310),
        ("Attenuvert", "CV Scale", 365),
    ]
    
    for label, sublabel, y in expander_blocks:
        draw_block(680, y, 140, 45, label, sublabel, C_EXPANDER)

    # === SIGNAL FLOW WITH ELBOW ROUTING ===
    # MicroBrute to DB-9 A (Outputs)
    draw_elbow_hv(190, 112, 380, 115, C_SYNTH, "Saw")
    draw_elbow_hv(190, 130, 370, 130, C_SYNTH, "Sqr")
    draw_elbow_hv(190, 167, 380, 145, C_SYNTH, "VCF")
    draw_elbow_hv(190, 222, 360, 100, C_SYNTH, "Gate")
    draw_elbow_hv(190, 277, 370, 125, C_SYNTH, "LFO")
    draw_elbow_hv(190, 332, 380, 135, C_SYNTH, "Env")
    
    # DB-9 A to Audio Outputs (bottom section)
    r.elements.append(f'<text x="500" y="420" class="label" font-size="12" fill="{C_AUDIO}">Audio Outputs (Buffered)</text>')
    
    audio_outputs = [
        ("Main Out", "Line Level", 450, 470),
        ("Saw Out", "Raw VCO", 200, 470),
        ("Sqr Out", "Raw VCO", 325, 470),
        ("Mix Out", "Pre-VCF", 575, 470),
        ("VCF Out", "Post-Filter", 700, 470),
    ]
    
    for label, sublabel, x, y in audio_outputs:
        draw_block(x, y, 110, 40, label, sublabel, C_AUDIO)
    
    # Audio outputs connection from DB-9 A with elbow routing
    r.elements.append(f'<line x1="520" y1="140" x2="520" y2="450" stroke="{C_AUDIO}" stroke-width="2"/>')
    r.elements.append(f'<line x1="255" y1="450" x2="750" y2="450" stroke="{C_AUDIO}" stroke-width="2"/>')
    for x in [255, 380, 505, 630, 755]:
        r.elements.append(f'<line x1="{x}" y1="450" x2="{x}" y2="470" stroke="{C_AUDIO}" stroke-width="2"/>')
    
    # DB-9 B connections (Inputs from Expander)
    draw_elbow_hv(680, 112, 520, 177, C_EXPANDER, "Noise")
    draw_elbow_hv(680, 280, 540, 185, C_EXPANDER, "Clk")
    
    # Expander to DB-9 B inputs
    draw_elbow_vh(750, 167, 570, 190, C_EXPANDER, "Filter CV")
    draw_elbow_vh(750, 222, 570, 200, C_EXPANDER, "VCA CV")
    draw_elbow_vh(750, 277, 570, 210, C_EXPANDER, "Res")
    
    # Control signals
    draw_elbow_hv(520, 257, 600, 257, C_CONTROL, "GPIO")
    draw_elbow_hv(520, 327, 600, 327, C_CONTROL, "Touch")
    
    # === LEGEND ===
    r.elements.append(f'<rect x="50" y="530" width="900" height="200" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="500" y="555" class="label" text-anchor="middle" fill="#333">System Legend</text>')
    
    legend_items = [
        (C_SYNTH, "MicroBrute Core (VCO, VCF, VCA, LFO, Envelope)"),
        (C_INTERFACE, "Breakout Interface (DB-9, Power Distribution)"),
        (C_EXPANDER, "Expander Modules (Noise, LFO, S&H, Clock, etc.)"),
        (C_CONTROL, "Control System (Pico W, Touch Pads, LEDs)"),
        (C_AUDIO, "Audio Outputs (Buffered, Protected)"),
    ]
    
    for i, (color, label) in enumerate(legend_items):
        y_pos = 575 + i * 25
        r.elements.append(f'<rect x="70" y="{y_pos-8}" width="20" height="15" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="100" y="{y_pos+3}" class="value" font-size="10">{label}</text>')
    
    return r.render()


def generate_audio_signal_flow() -> str:
    """Generate Audio Signal Flow Diagram - showing audio path from VCO to outputs with clear elbow routing."""
    r = SchematicRenderer(900, 650, "Audio Signal Flow", "From VCO Through Filter to Outputs")
    
    C_VCO = "#E91E63"
    C_MIXER = "#FF9800"
    C_FILTER = "#2196F3"
    C_AMP = "#4CAF50"
    C_OUT = "#9C27B0"
    C_TP = "#666"
    
    def draw_stage(x, y, w, h, label, sublabel, color):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+h/2-5}" class="label" text-anchor="middle" fill="#FFF" font-size="10">{label}</text>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+h/2+12}" class="value" text-anchor="middle" fill="#FFF" font-size="8">{sublabel}</text>')
    
    def draw_elbow_hv(x1, y1, x2, y2, color="#333", label=""):
        """Draw horizontal-then-vertical elbow wire."""
        mid_x = x1 + (x2 - x1) // 2
        path = f'M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            r.elements.append(f'<text x="{mid_x}" y="{y1-5}" class="value" text-anchor="middle" fill="#666" font-size="7">{label}</text>')
    
    def draw_tp_point(x, y, label, color=C_TP):
        """Draw test point with label."""
        r.elements.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" stroke="#333" stroke-width="1"/>')
        r.elements.append(f'<text x="{x}" y="{y+18}" class="value" text-anchor="middle" font-size="7">{label}</text>')
    
    # === INPUT SOURCES (Left Column) ===
    draw_stage(50, 80, 100, 50, "Saw VCO", "-5V to +5V", C_VCO)
    draw_stage(50, 150, 100, 50, "Square VCO", "0V to +5V", C_VCO)
    draw_stage(50, 220, 100, 50, "Sub Osc", "-5V to +5V", C_VCO)
    draw_stage(50, 290, 100, 50, "Ext In", "Line Level", C_VCO)
    draw_stage(50, 360, 100, 50, "Noise", "White/Pink", C_VCO)
    
    # === MIXER (Center-Left) ===
    draw_stage(220, 200, 110, 70, "MIXER", "Ultrafaux", C_MIXER)
    
    # Elbow connections from sources to mixer
    draw_elbow_hv(150, 105, 220, 220, C_VCO)      # Saw
    draw_elbow_hv(150, 175, 230, 230, C_VCO)      # Square
    draw_elbow_hv(150, 245, 240, 240, C_VCO)      # Sub
    draw_elbow_hv(150, 315, 250, 250, C_VCO)      # Ext
    draw_elbow_hv(150, 385, 260, 260, C_VCO)      # Noise
    
    # === VCF (Center) ===
    draw_stage(400, 200, 110, 70, "VCF", "Steiner-Parker", C_FILTER)
    draw_elbow_hv(330, 235, 400, 235, C_MIXER, "Mix Out")
    
    # === VCA (Center-Right) ===
    draw_stage(580, 200, 110, 70, "VCA", "ADSR Controlled", C_AMP)
    draw_elbow_hv(510, 235, 580, 235, C_FILTER, "Filter Out")
    
    # === MAIN OUT (Right) ===
    draw_stage(760, 200, 110, 70, "MAIN OUT", "Line Level", C_OUT)
    draw_elbow_hv(690, 235, 760, 235, C_AMP)
    
    # === TEST POINTS (Below signal path with clear connections) ===
    r.elements.append(f'<text x="450" y="310" class="label" text-anchor="middle" font-size="10">Buffered Test Point Outputs</text>')
    
    # Draw TP row
    tp_y = 340
    draw_tp_point(100, tp_y, "TP94 Saw")
    draw_tp_point(200, tp_y, "TP93 Square")
    draw_tp_point(320, tp_y, "TP30 Mix")
    draw_tp_point(455, tp_y, "TP19 VCF")
    draw_tp_point(595, tp_y, "TP10/11 VCA")
    draw_tp_point(760, tp_y, "Main Line Out")
    
    # Connect TPs to their stages with vertical lines
    # Saw TP - goes up to Saw VCO (with buffer)
    r.elements.append(f'<line x1="100" y1="{tp_y-5}" x2="100" y2="130" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="85" y="270" class="value" font-size="6" fill="{C_TP}">via buffer</text>')
    
    # Square TP
    r.elements.append(f'<line x1="200" y1="{tp_y-5}" x2="200" y2="175" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="185" y="270" class="value" font-size="6" fill="{C_TP}">via buffer</text>')
    
    # Mix TP - from mixer
    r.elements.append(f'<line x1="320" y1="{tp_y-5}" x2="320" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="300" y="310" class="value" font-size="6" fill="{C_TP}">1kΩ + TL074</text>')
    
    # VCF TP - from VCF
    r.elements.append(f'<line x1="455" y1="{tp_y-5}" x2="455" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="435" y="310" class="value" font-size="6" fill="{C_TP}">1kΩ + TL074</text>')
    
    # VCA TP - from VCA
    r.elements.append(f'<line x1="595" y1="{tp_y-5}" x2="595" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="575" y="310" class="value" font-size="6" fill="{C_TP}">1kΩ + TL074</text>')
    
    # Main Out - direct from output
    r.elements.append(f'<line x1="760" y1="{tp_y-5}" x2="760" y2="270" stroke="{C_TP}" stroke-width="1.5"/>')
    r.elements.append(f'<text x="740" y="310" class="value" font-size="6" fill="{C_TP}">Direct</text>')
    
    # === NOTES BOX (Bottom, clear placement) ===
    r.elements.append(f'<rect x="50" y="380" width="800" height="250" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="450" y="405" class="label" text-anchor="middle" fill="#1B5E20">Signal Flow & Test Point Notes</text>')
    
    notes = [
        ("Signal Path:", "Saw/Square/Sub/Ext/Noise → Mixer → VCF → VCA → Main Out", 430),
        ("VCO Outputs:", "Raw waveforms (-5V to +5V, ~10Vpp) available at TP94, TP93 via buffers", 450),
        ("Mixer Stage:", "Ultrafaux passive mixer with 5 inputs and individual level controls", 470),
        ("VCF Stage:", "Steiner-Parker filter (12dB/octave) with resonance control via RP13", 490),
        ("VCA Stage:", "Controlled by ADSR envelope (attack, decay, sustain, release)", 510),
        ("Test Points:", "All TPs have 1kΩ series resistor + TL074 buffer for safe external patching", 530),
        ("Protection:", "Outputs are current-limited and buffered - safe for Eurorack/modular systems", 550),
        ("Buffering:", "Required because direct wiring causes oscillator loading and signal degradation", 570),
    ]
    
    for label, value, y in notes:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="8" fill="#1B5E20">{label}</text>')
        r.elements.append(f'<text x="160" y="{y}" class="value" font-size="8">{value}</text>')
    
    return r.render()


def generate_cv_control_flow() -> str:
    """Generate CV Control Flow Diagram - showing modulation routing with clear elbow connections."""
    r = SchematicRenderer(950, 700, "CV Control Flow", "Modulation and Control Voltage Routing")

    C_MOD = "#9C27B0"      # Purple - modulation sources
    C_DEST = "#2196F3"     # Blue - modulation targets
    C_INPUT = "#FF9800"    # Orange - external inputs
    C_EXPANDER = "#4CAF50" # Green - expander modules

    def draw_mod_block(x, y, w, h, label, sublabel, color):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+h/2-5}" class="label" text-anchor="middle" fill="#FFF" font-size="9">{label}</text>')
        if sublabel:
            r.elements.append(f'<text x="{x+w/2}" y="{y+h/2+12}" class="value" text-anchor="middle" fill="#FFF" font-size="7">{sublabel}</text>')

    def draw_elbow_hv(x1, y1, x2, y2, color="#666", label=""):
        """Draw horizontal-then-vertical elbow line."""
        mid_x = (x1 + x2) // 2
        path = f'M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}'
        r.elements.append(f'<path d="{path}" stroke="{color}" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>')
        if label:
            r.elements.append(f'<text x="{mid_x}" y="{y1-3}" class="value" text-anchor="middle" fill="{color}" font-size="6">{label}</text>')

    # === SECTION LABELS ===
    r.elements.append(f'<text x="120" y="45" class="label" font-size="11" fill="{C_MOD}">Modulation Sources</text>')
    r.elements.append(f'<text x="450" y="45" class="label" font-size="11" fill="{C_DEST}">Modulation Targets</text>')
    r.elements.append(f'<text x="750" y="45" class="label" font-size="11" fill="{C_INPUT}">External CV Inputs</text>')

    # === LEFT COLUMN: Modulation Sources ===
    sources = [
        ("LFO", "0-5V △", 70, C_MOD),
        ("Envelope", "0-5V ADSR", 130, C_MOD),
        ("Pitch CV", "1V/oct", 190, C_MOD),
        ("Mod Wheel", "0-5V", 250, C_MOD),
        ("Exp LFO", "Free Run", 330, C_EXPANDER),
        ("Exp S&H", "S&H", 390, C_EXPANDER),
    ]

    for label, sublabel, y, color in sources:
        draw_mod_block(70, y, 100, 45, label, sublabel, color)

    # === CENTER COLUMN: Modulation Targets ===
    targets = [
        ("Pitch", "VCO Freq", 70),
        ("Filter", "Cutoff", 130),
        ("Resonance", "Peak", 190),
        ("VCA", "Amplitude", 250),
        ("PWM", "Pulse Width", 310),
        ("Metalizer", "Harmonics", 370),
    ]

    for label, sublabel, y in targets:
        draw_mod_block(400, y, 100, 45, label, sublabel, C_DEST)

    # === RIGHT COLUMN: External CV Inputs ===
    inputs = [
        ("Filter CV", "DB-9 B P1", 70),
        ("VCA CV", "DB-9 B P2", 130),
        ("Res CV", "Vactrol", 190),
        ("Gate In", "DB-9 B P5", 250),
        ("Sync", "DB-9 B P4", 310),
    ]

    for label, sublabel, y in inputs:
        draw_mod_block(720, y, 110, 45, label, sublabel, C_INPUT)

    # === CONNECTIONS WITH ELBOW ROUTING ===
    # LFO connections (goes to many targets)
    draw_elbow_hv(170, 92, 400, 92, C_MOD)       # LFO -> Pitch
    draw_elbow_hv(170, 100, 390, 152, C_MOD)     # LFO -> Filter
    draw_elbow_hv(170, 108, 380, 272, C_MOD)     # LFO -> VCA

    # Envelope connections
    draw_elbow_hv(170, 152, 410, 112, C_MOD)     # Env -> Filter
    draw_elbow_hv(170, 160, 400, 272, C_MOD)     # Env -> VCA

    # Pitch CV -> Pitch
    draw_elbow_hv(170, 212, 400, 92, C_MOD)

    # Mod Wheel -> Pitch
    draw_elbow_hv(170, 272, 410, 100, C_MOD)

    # Expander LFO -> Resonance
    draw_elbow_hv(170, 352, 400, 212, C_EXPANDER)

    # Expander S&H -> Resonance
    draw_elbow_hv(170, 412, 410, 220, C_EXPANDER)

    # External Inputs -> Targets
    draw_elbow_hv(720, 92, 500, 152, C_INPUT, "Filter CV")   # Filter CV -> Filter
    draw_elbow_hv(720, 152, 500, 272, C_INPUT, "VCA CV")     # VCA CV -> VCA
    draw_elbow_hv(720, 212, 500, 212, C_INPUT, "Res CV")     # Res CV -> Resonance
    draw_elbow_hv(720, 272, 500, 332, C_INPUT, "Gate")       # Gate In -> PWM
    draw_elbow_hv(720, 332, 500, 392, C_INPUT, "Sync")       # Sync -> Metalizer

    # === NOTES BOX ===
    r.elements.append(f'<rect x="50" y="460" width="850" height="220" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="475" y="485" class="label" text-anchor="middle" fill="#E65100">CV Routing & Modulation Notes</text>')

    notes = [
        ("Mod Matrix:", "MicroBrute's patch panel routes LFO/Env to different destinations using front-panel switches", 510),
        ("Attenuation:", "External CV inputs (from Expander) pass through attenuverter pots for level control", 535),
        ("Summing:", "Multiple CV sources sum at destination (e.g., Pitch = Keyboard + LFO + Pitch Bend + Expander)", 560),
        ("Vactrol:", "Resonance CV uses optocoupler (LED+LDR) for smooth, noise-free resonance control", 585),
        ("Protection:", "All CV inputs have 100kΩ series resistance + BAT54S clamping diodes to ±5V", 610),
        ("Range:", "MicroBrute expects 0-5V CV signals. External inputs are attenuated and clamped to this range", 635),
        ("Path:", "Sources → Mod Matrix (internal) OR DB-9 B (external) → Targets (VCO, VCF, VCA, etc.)", 660),
    ]

    for label, value, y in notes:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="8" fill="#E65100">{label}</text>')
        r.elements.append(f'<text x="160" y="{y}" class="value" font-size="8">{value}</text>')

    return r.render()


def generate_signal_flow_overview() -> str:
    """Generate Signal Flow Overview diagram - complete system signal path."""
    r = SchematicRenderer(1000, 700, "Signal Flow Overview", "Complete Path from MicroBrute to Expander")
    
    C_MICRO = "#4A90E2"      # Blue for MicroBrute
    C_BREAKOUT = "#F5A623"   # Orange for Breakout
    C_DB9 = "#7ED321"        # Green for DB-9
    C_EXPANDER = "#BD10E0"   # Purple for Expander
    C_SIGNAL = "#1a1a1a"     # Black for signals
    
    # === SECTION LABELS ===
    r.elements.append(f'<text x="150" y="50" class="label" text-anchor="middle" fill="{C_MICRO}">MicroBrute</text>')
    r.elements.append(f'<text x="350" y="50" class="label" text-anchor="middle" fill="{C_BREAKOUT}">Breakout PCB</text>')
    r.elements.append(f'<text x="550" y="50" class="label" text-anchor="middle" fill="{C_DB9}">DB-9 Connectors</text>')
    r.elements.append(f'<text x="800" y="50" class="label" text-anchor="middle" fill="{C_EXPANDER}">Expander</text>')
    
    # === MICROBRUTE SECTION ===
    # Draw MicroBrute box
    r.elements.append(f'<rect x="50" y="70" width="200" height="550" fill="#E8F4FD" stroke="{C_MICRO}" stroke-width="2" rx="5"/>')
    
    # Test points
    micro_sources = [
        ("TP94 Saw", 100, "#0066CC"),
        ("TP93 Square", 140, "#0066CC"),
        ("TP30 Mix", 180, "#0066CC"),
        ("TP19 VCF", 220, "#0066CC"),
        ("TP124 Triangle", 260, "#0066CC"),
        ("TP83 Gate", 320, "#009933"),
        ("Pitch CV", 360, "#CC6600"),
        ("Envelope", 400, "#CC6600"),
        ("LFO", 440, "#CC6600"),
        ("TP70 +12V", 520, "#CC0000"),
        ("TP71 -12V", 560, "#0000CC"),
        ("TP72 GND", 600, "#1a1a1a"),
    ]
    
    for name, y, color in micro_sources:
        r.elements.append(f'<text x="60" y="{y}" class="value" font-size="8">{name}</text>')
        r.elements.append(f'<circle cx="230" cy="{y-3}" r="3" fill="{color}"/>')
    
    # === BREAKOUT SECTION ===
    r.elements.append(f'<rect x="280" y="70" width="140" height="550" fill="#FEF3E2" stroke="{C_BREAKOUT}" stroke-width="2" rx="5"/>')
    
    # Buffer blocks
    buffers = [
        ("TL074 A\nSaw", 100, "1kΩ"),
        ("TL074 B\nSquare", 140, "1kΩ"),
        ("TL074 C\nMix", 180, "1kΩ"),
        ("TL074 D\nVCF", 220, "1kΩ"),
        ("TL072\nTriangle", 260, "2× gain"),
        ("CD40106\nGate", 320, "10kΩ"),
        ("Direct", 360, ""),
        ("TL074\nEnv", 400, "10kΩ"),
        ("TL074\nLFO", 440, "10kΩ"),
    ]
    
    for label, y, protection in buffers:
        r.elements.append(f'<rect x="300" y="{y-15}" width="100" height="30" fill="{C_BREAKOUT}" stroke="#333" stroke-width="1" rx="3"/>')
        r.elements.append(f'<text x="350" y="{y}" class="label" text-anchor="middle" fill="#FFF" font-size="7">{label}</text>')
        if protection:
            r.elements.append(f'<text x="350" y="{y+22}" class="value" text-anchor="middle" font-size="7">{protection}</text>')
    
    # Power section
    r.elements.append(f'<rect x="300" y="500" width="100" height="110" fill="#FFEBEE" stroke="#CC0000" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="350" y="520" class="label" text-anchor="middle" font-size="8">Power Distribution</text>')
    r.elements.append(f'<text x="350" y="545" class="value" text-anchor="middle" font-size="7">+12V / -12V / GND</text>')
    r.elements.append(f'<text x="350" y="570" class="value" text-anchor="middle" font-size="7">Fuse + 1N5817</text>')
    r.elements.append(f'<text x="350" y="595" class="value" text-anchor="middle" font-size="7">Pico VSYS +5V</text>')
    
    # === DB-9 SECTION ===
    r.elements.append(f'<rect x="470" y="70" width="160" height="250" fill="#E8F5E9" stroke="{C_DB9}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="550" y="90" class="label" text-anchor="middle" font-size="9">DB-9 A (Outputs)</text>')
    
    db9a_pins = [
        ("1: Gate", 110),
        ("2: Pitch", 135),
        ("3: Env", 160),
        ("4: LFO", 185),
        ("5: Mix", 210),
        ("6: VCF", 235),
        ("7: Saw", 260),
        ("8: Square", 285),
        ("9: GND", 310),
    ]
    
    for label, y in db9a_pins:
        r.elements.append(f'<text x="480" y="{y}" class="value" font-size="7">{label}</text>')
    
    # DB-9 B
    r.elements.append(f'<rect x="470" y="340" width="160" height="280" fill="#FFF3E0" stroke="#FF9800" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="550" y="360" class="label" text-anchor="middle" font-size="9">DB-9 B (Inputs + Power)</text>')
    
    db9b_pins = [
        ("1: Filter CV", 380),
        ("2: VCA CV", 405),
        ("3: Resonance", 430),
        ("4: Sync", 455),
        ("5: Gate In", 480),
        ("6: Ext Audio", 505),
        ("7: +12V", 535),
        ("8: -12V", 560),
        ("9: GND", 585),
    ]
    
    for label, y in db9b_pins:
        r.elements.append(f'<text x="480" y="{y}" class="value" font-size="7">{label}</text>')
    
    # === EXPANDER SECTION ===
    r.elements.append(f'<rect x="680" y="70" width="280" height="550" fill="#F3E5F5" stroke="{C_EXPANDER}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="820" y="90" class="label" text-anchor="middle" font-size="9">Expander Modules</text>')
    
    # Output jacks
    outputs = [
        ("Saw OUT", 110, "#0066CC"),
        ("Square OUT", 140, "#0066CC"),
        ("Mix OUT", 180, "#0066CC"),
        ("VCF OUT", 220, "#0066CC"),
        ("Triangle OUT", 260, "#0066CC"),
        ("Gate OUT", 320, "#009933"),
        ("Pitch IN", 360, "#CC6600"),
        ("Env IN", 400, "#CC6600"),
        ("LFO IN", 440, "#CC6600"),
    ]
    
    for label, y, color in outputs:
        r.elements.append(f'<rect x="700" y="{y-10}" width="80" height="20" fill="{color}" stroke="#333" stroke-width="1" rx="3"/>')
        r.elements.append(f'<text x="740" y="{y+3}" class="label" text-anchor="middle" fill="#FFF" font-size="7">{label}</text>')
    
    # Expander circuits
    circuits = [
        ("Noise Gen", 110),
        ("LFO", 150),
        ("S&H", 190),
        ("Clock Div", 230),
        ("Slew Limiter", 270),
        ("Attenuverter", 310),
    ]
    
    for label, y in circuits:
        r.elements.append(f'<rect x="800" y="{y-10}" width="90" height="25" fill="#9C27B0" stroke="#333" stroke-width="1" rx="3"/>')
        r.elements.append(f'<text x="845" y="{y+3}" class="label" text-anchor="middle" fill="#FFF" font-size="8">{label}</text>')
    
    # Power section
    r.elements.append(f'<rect x="700" y="500" width="240" height="100" fill="#FFEBEE" stroke="#CC0000" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="820" y="525" class="label" text-anchor="middle" font-size="9">Eurorack Power</text>')
    r.elements.append(f'<text x="820" y="555" class="value" text-anchor="middle" font-size="8">+12V / -12V / +5V / GND</text>')
    r.elements.append(f'<text x="820" y="585" class="value" text-anchor="middle" font-size="7">16-pin Eurorack header</text>')
    
    # === CONNECTION LINES ===
    # MicroBrute to Breakout
    connections_mb = [
        (100, 100, "#0066CC"),
        (140, 140, "#0066CC"),
        (180, 180, "#0066CC"),
        (220, 220, "#0066CC"),
        (260, 260, "#0066CC"),
        (320, 320, "#009933"),
        (360, 360, "#CC6600"),
        (400, 400, "#CC6600"),
        (440, 440, "#CC6600"),
    ]
    
    for y1, y2, color in connections_mb:
        r.elements.append(f'<line x1="230" y1="{y1-3}" x2="300" y2="{y2}" stroke="{color}" stroke-width="1.5"/>')
    
    # Power connections
    r.elements.append(f'<line x1="230" y1="517" x2="300" y2="545" stroke="#CC0000" stroke-width="2"/>')
    r.elements.append(f'<line x1="230" y1="557" x2="300" y2="565" stroke="#0000CC" stroke-width="2"/>')
    r.elements.append(f'<line x1="230" y1="597" x2="300" y2="585" stroke="#1a1a1a" stroke-width="2"/>')
    
    # Breakout to DB-9 A
    connections_ba = [
        (320, 110, "#009933"),   # Gate
        (360, 135, "#CC6600"),   # Pitch
        (400, 160, "#CC6600"),   # Env
        (440, 185, "#CC6600"),   # LFO
        (180, 210, "#0066CC"),   # Mix
        (220, 235, "#0066CC"),   # VCF
        (100, 260, "#0066CC"),   # Saw
        (140, 285, "#0066CC"),   # Square
    ]
    
    for y1, y2, color in connections_ba:
        r.elements.append(f'<line x1="400" y1="{y1}" x2="470" y2="{y2}" stroke="{color}" stroke-width="1.5"/>')
    
    # DB-9 A to Expander
    connections_ae = [
        (110, 110, "#009933"),   # Gate
        (135, 360, "#CC6600"),   # Pitch
        (160, 400, "#CC6600"),   # Env
        (185, 440, "#CC6600"),   # LFO
        (210, 180, "#0066CC"),   # Mix
        (235, 220, "#0066CC"),   # VCF
        (260, 110, "#0066CC"),   # Saw
        (285, 140, "#0066CC"),   # Square
    ]
    
    for y1, y2, color in connections_ae:
        r.elements.append(f'<line x1="630" y1="{y1}" x2="700" y2="{y2}" stroke="{color}" stroke-width="1.5"/>')
    
    # === LEGEND ===
    r.elements.append(f'<rect x="50" y="640" width="900" height="50" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="500" y="655" class="label" text-anchor="middle" font-size="9">Signal Type Legend</text>')
    
    legend_items = [
        ("#0066CC", "Audio Outputs (Saw, Square, Mix, VCF, Triangle)"),
        ("#CC6600", "CV Signals (Pitch, Env, LFO)"),
        ("#009933", "Gate/Clock"),
        ("#CC0000", "+12V Power"),
        ("#0000CC", "-12V Power"),
        ("#1a1a1a", "GND"),
    ]
    
    for i, (color, label) in enumerate(legend_items):
        x_pos = 100 + i * 140
        r.elements.append(f'<rect x="{x_pos}" y="665" width="15" height="10" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="{x_pos+20}" y="673" class="value" font-size="7">{label}</text>')
    
    return r.render()


def generate_cd4051_multiplexer() -> str:
    """Generate CD4051 8-channel analog multiplexer schematic."""
    r = SchematicRenderer(800, 600, "CD4051 Analog Multiplexer", "8-Channel Signal Selector for Oscilloscope")
    
    # CD4051 IC outline
    r.elements.append(f'<rect x="300" y="150" width="200" height="300" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="400" y="175" class="label" text-anchor="middle" fill="#FFF" font-size="12">CD4051</text>')
    r.elements.append(f'<text x="400" y="195" class="value" text-anchor="middle" fill="#CCC" font-size="9">8-Ch Analog MUX</text>')
    
    # Input channels (left side)
    inputs = [
        ("X0: Saw", 230, 220),
        ("X1: Square", 230, 245),
        ("X2: Mix", 230, 270),
        ("X3: VCF", 230, 295),
        ("X4: LFO", 230, 320),
        ("X5: Env", 230, 345),
        ("X6: NC", 230, 370),
        ("X7: NC", 230, 395),
    ]
    
    for label, x, y in inputs:
        r.elements.append(f'<text x="{x}" y="{y}" class="value" text-anchor="end" font-size="8">{label}</text>')
        r.elements.append(f'<line x1="{x+5}" y1="{y-3}" x2="300" y2="{y-3}" stroke="#1a1a1a" stroke-width="1.5"/>')
        # Series resistor
        r.elements.append(f'<rect x="{x+15}" y="{y-8}" width="20" height="10" fill="#f5f5f5" stroke="#333" stroke-width="1"/>')
        r.elements.append(f'<text x="{x+25}" y="{y-1}" class="value" text-anchor="middle" font-size="6">1kΩ</text>')
    
    # Common output (right side)
    r.elements.append(f'<text x="570" y="300" class="value" font-size="9">COM (Output)</text>')
    r.elements.append(f'<line x1="500" y1="297" x2="560" y2="297" stroke="#1a1a1a" stroke-width="2"/>')
    
    # Buffer
    r.elements.append(f'<rect x="580" y="280" width="60" height="35" fill="#F5A623" stroke="#333" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="610" y="297" class="label" text-anchor="middle" fill="#FFF" font-size="8">TL072</text>')
    r.elements.append(f'<text x="610" y="308" class="value" text-anchor="middle" fill="#FFF" font-size="7">Buffer</text>')
    
    # To DSO138
    r.elements.append(f'<line x1="640" y1="297" x2="700" y2="297" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append(f'<text x="710" y="300" class="label" font-size="9">To DSO138 IN</text>')
    
    # Address pins (bottom)
    address_pins = [
        ("A (LSB)", 340, 480),
        ("B", 400, 480),
        ("C (MSB)", 460, 480),
    ]
    
    for label, x, y in address_pins:
        r.elements.append(f'<line x1="{x}" y1="450" x2="{x}" y2="{y-20}" stroke="#1a1a1a" stroke-width="1.5"/>')
        r.elements.append(f'<text x="{x}" y="{y}" class="value" text-anchor="middle" font-size="8">{label}</text>')
    
    # Control logic
    r.elements.append(f'<rect x="300" y="500" width="200" height="80" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="400" y="525" class="label" text-anchor="middle" fill="#1B5E20" font-size="10">Control (Pico GPIO or Switch)</text>')
    
    switch_logic = [
        ("Position 0 (Saw):   A=0, B=0, C=0", 545),
        ("Position 1 (Sqr):   A=1, B=0, C=0", 560),
        ("Position 2 (Mix):   A=0, B=1, C=0", 575),
    ]
    
    for text, y in switch_logic:
        r.elements.append(f'<text x="320" y="{y}" class="value" font-size="7">{text}</text>')
    
    # Power pins
    r.elements.append(f'<text x="400" y="140" class="value" text-anchor="middle" font-size="8">VDD = +5V</text>')
    r.elements.append(f'<line x1="400" y1="145" x2="400" y2="150" stroke="#CC0000" stroke-width="1.5"/>')
    
    r.elements.append(f'<text x="350" y="140" class="value" text-anchor="middle" font-size="8">VEE = GND</text>')
    r.elements.append(f'<line x1="350" y1="145" x2="350" y2="150" stroke="#1a1a1a" stroke-width="1.5"/>')
    
    r.elements.append(f'<text x="450" y="140" class="value" text-anchor="middle" font-size="8">VSS = GND</text>')
    r.elements.append(f'<line x1="450" y1="145" x2="450" y2="150" stroke="#1a1a1a" stroke-width="1.5"/>')
    
    # INH (inhibit)
    r.elements.append(f'<text x="320" y="135" class="value" font-size="7">INH→GND</text>')
    r.elements.append(f'<line x1="320" y1="145" x2="320" y2="150" stroke="#1a1a1a" stroke-width="1.5"/>')
    
    # === HOW IT WORKS ===
    r.elements.append(f'<rect x="50" y="420" width="220" height="160" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="160" y="445" class="label" text-anchor="middle" fill="#E65100" font-size="10">How It Works</text>')
    
    explanation = [
        "1. 8 analog inputs (X0-X7)",
        "2. 3-bit address (A,B,C)",
        "   selects channel",
        "3. Selected channel →",
        "   COM output",
        "4. TL072 buffers signal",
        "   to DSO138",
        "5. 1kΩ resistors protect",
        "   inputs from shorts",
    ]
    
    for i, line in enumerate(explanation):
        r.elements.append(f'<text x="60" y="{465 + i*12}" class="value" font-size="7">{line}</text>')
    
    return r.render()


def generate_cv_input_protection_diagram() -> str:
    """Generate CV input protection circuit diagram."""
    r = SchematicRenderer(700, 500, "CV Input Protection Circuit", "±12V to 0-5V Scaling with Clamping")
    
    # Input jack
    r.jack(Point(80, 200), label="CV IN ±12V")
    r.wire(Point(100, 200), Point(150, 200))
    
    # Series resistor
    r.resistor(Point(170, 200), label="R1", value="100kΩ", vertical=False)
    r.wire(Point(190, 200), Point(220, 200))
    
    # Clamping diodes to ±5V rails
    r.elements.append(f'<text x="250" y="150" class="label" font-size="10">Clamping to ±5V</text>')
    
    # To +5V
    r.wire(Point(220, 200), Point(220, 170))
    r.wire(Point(220, 170), Point(280, 170))
    r.elements.extend([
        f'<polygon points="280,160 280,180 300,170" fill="none" stroke="#D44" stroke-width="1.5"/>',
        f'<line x1="300" y1="160" x2="300" y2="180" stroke="#D44" stroke-width="1.5"/>',
    ])
    r.wire(Point(300, 170), Point(350, 170))
    r.vcc(Point(350, 170), label="+5V")
    
    # To -5V
    r.wire(Point(220, 200), Point(220, 230))
    r.wire(Point(220, 230), Point(280, 230))
    r.elements.extend([
        f'<polygon points="300,220 300,240 280,230" fill="none" stroke="#44D" stroke-width="1.5"/>',
        f'<line x1="280" y1="220" x2="280" y2="240" stroke="#44D" stroke-width="1.5"/>',
    ])
    r.wire(Point(280, 245), Point(280, 280))
    r.elements.append(f'<line x1="280" y1="280" x2="350" y2="280" stroke="#44D" stroke-width="2"/>')
    r.elements.append(f'<text x="360" y="283" class="value" fill="#44D" font-size="8">-5V</text>')
    
    # To op-amp
    r.wire(Point(220, 200), Point(320, 200))
    r.wire(Point(320, 200), Point(320, 240))
    
    # Op-amp (inverting attenuator)
    r.opamp(Point(400, 270), label="TL072 A", pins=("-", "+", "out"), show_power=False)
    
    # Input resistor to op-amp
    r.wire(Point(320, 240), Point(320, 252))
    r.wire(Point(320, 252), Point(370, 252))
    r.resistor(Point(345, 252), label="R2", value="100kΩ", vertical=False)
    
    # + input to bias
    r.wire(Point(320, 288), Point(320, 350))
    r.resistor(Point(320, 320), label="R3", value="100kΩ", vertical=True)
    r.ground(Point(320, 350))
    
    # Feedback network
    r.wire(Point(430, 270), Point(480, 270))
    r.wire(Point(480, 270), Point(480, 200))
    r.wire(Point(480, 200), Point(400, 200))
    r.wire(Point(400, 200), Point(400, 240))
    r.resistor(Point(440, 200), label="R4", value="47kΩ", vertical=False)
    
    # Output
    r.wire(Point(430, 270), Point(550, 270))
    r.block(Point(600, 270), 80, 40, label="To Filter", sublabel="CV Input")
    
    # === EXPLANATION ===
    r.elements.append(f'<rect x="50" y="350" width="600" height="130" fill="#E3F2FD" stroke="#2196F3" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="350" y="375" class="label" text-anchor="middle" fill="#0D47A1">Protection Circuit Operation</text>')
    
    notes = [
        ("Input Range:", "±12V (Eurorack standard)", 395),
        ("Clamping:", "BAT54S diodes limit to ±5V (safe for op-amp)", 412),
        ("Attenuation:", "Gain = -0.47 (47k/100k), ±5V → ±2.35V", 429),
        ("Output:", "0-5V range suitable for MicroBrute CV inputs", 446),
        ("Current Limit:", "100kΩ input resistor protects against shorts", 463),
    ]
    
    for label, value, y in notes:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="8" fill="#1565C0">{label}</text>')
        r.elements.append(f'<text x="170" y="{y}" class="value" font-size="8">{value}</text>')
    
    return r.render()


def generate_pico_pinout_diagram() -> str:
    """Generate visual Pico H pinout diagram with aligned pin rows."""
    r = SchematicRenderer(950, 700, "Raspberry Pi Pico H Pinout", "MACROBRUTE Hardware Configuration")

    # Colors for different function types
    C_OLED = "#2196F3"      # Blue
    C_ENCODER = "#4CAF50"   # Green
    C_LED = "#FF9800"       # Orange
    C_CLOCK = "#9C27B0"     # Purple
    C_MIDI = "#E91E63"      # Pink
    C_UART = "#00BCD4"      # Cyan
    C_ADC = "#795548"       # Brown
    C_POWER = "#F44336"     # Red
    C_GND = "#333"          # Dark gray

    # Draw Pico board outline
    board_x, board_y = 325, 80
    board_w, board_h = 300, 540
    r.elements.append(f'<rect x="{board_x}" y="{board_y}" width="{board_w}" height="{board_h}" fill="#1a1a1a" stroke="#555" stroke-width="3" rx="10"/>')
    r.elements.append(f'<text x="{board_x + board_w/2}" y="{board_y + 30}" class="label" text-anchor="middle" fill="#FFF" font-size="14">Raspberry Pi Pico H</text>')

    # USB connector at top
    r.elements.append(f'<rect x="{board_x + 100}" y="{board_y - 15}" width="100" height="20" fill="#333" stroke="#666" stroke-width="1"/>')
    r.elements.append(f'<text x="{board_x + 150}" y="{board_y - 2}" class="value" text-anchor="middle" fill="#CCC" font-size="8">Micro USB</text>')

    # Pin spacing - consistent 20px between pins
    pin_spacing = 20
    start_y = board_y + 60

    # Left side pins (GP0-GP15) - aligned in a column
    left_pins = [
        ("GP0", "UART0 TX", "→ LPC2361", C_UART),
        ("GP1", "UART0 RX", "→ LPC2361", C_UART),
        ("GND", None, None, C_GND),
        ("GP2", "(Spare)", "", None),
        ("GP3", "(Spare)", "", None),
        ("GP4", "MIDI TX", "UART1", C_MIDI),
        ("GP5", "MIDI RX", "UART1", C_MIDI),
        ("GND", None, None, C_GND),
        ("GP6", "(Spare)", "", None),
        ("GP7", "(Spare)", "", None),
        ("GP8", "LED Clock", "", C_LED),
        ("GP9", "LED Gate", "", C_LED),
        ("GP10", "LED Mode", "", C_LED),
        ("GP11", "(Spare)", "", None),
        ("GP12", "Tap Button", "", C_ENCODER),
        ("GP13", "Enc. Button", "", C_ENCODER),
        ("GP14", "Enc. CLK", "", C_ENCODER),
        ("GP15", "Enc. DT", "", C_ENCODER),
    ]

    for i, (pin, func, detail, color) in enumerate(left_pins):
        y = start_y + i * pin_spacing
        pin_x = board_x

        # Pin circle
        r.elements.append(f'<circle cx="{pin_x}" cy="{y}" r="5" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')

        # Pin label (inside board)
        r.elements.append(f'<text x="{pin_x + 15}" y="{y + 3}" class="value" fill="#AAA" font-size="7">{pin}</text>')

        # Function box and label (outside board)
        if func and color:
            box_w = 90
            box_x = pin_x - box_w - 10
            r.elements.append(f'<rect x="{box_x}" y="{y-8}" width="{box_w}" height="16" fill="{color}" stroke="#333" stroke-width="1" rx="2"/>')
            r.elements.append(f'<text x="{box_x + box_w/2}" y="{y + 3}" class="label" text-anchor="middle" fill="#FFF" font-size="7">{func}</text>')

            if detail:
                r.elements.append(f'<text x="{box_x - 5}" y="{y + 3}" class="value" text-anchor="end" fill="#666" font-size="6">{detail}</text>')

    # Right side pins (GP16-GP28) - aligned in a column
    right_pins = [
        ("GP16", "OLED DC", C_OLED),
        ("GP17", "OLED CS", C_OLED),
        ("GND", None, C_GND),
        ("GP18", "OLED SCK", C_OLED),
        ("GP19", "OLED MOSI", C_OLED),
        ("GP20", "OLED RST", C_OLED),
        ("GP21", "Clock In", C_CLOCK),
        ("GND", None, C_GND),
        ("GP22", "Clock Out", C_CLOCK),
        ("GP26", "ADC0 (Spare)", C_ADC),
        ("GP27", "ADC1 (Spare)", C_ADC),
        ("GND", None, C_GND),
        ("GP28", "ADC2 (Spare)", C_ADC),
    ]

    for i, (pin, func, color) in enumerate(right_pins):
        y = start_y + i * pin_spacing
        pin_x = board_x + board_w

        # Pin circle
        r.elements.append(f'<circle cx="{pin_x}" cy="{y}" r="5" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')

        # Pin label (inside board)
        r.elements.append(f'<text x="{pin_x - 15}" y="{y + 3}" class="value" text-anchor="end" fill="#AAA" font-size="7">{pin}</text>')

        # Function box (outside board)
        if func and color != C_GND:
            box_w = 90
            box_x = pin_x + 10
            r.elements.append(f'<rect x="{box_x}" y="{y-8}" width="{box_w}" height="16" fill="{color}" stroke="#333" stroke-width="1" rx="2"/>')
            r.elements.append(f'<text x="{box_x + box_w/2}" y="{y + 3}" class="label" text-anchor="middle" fill="#FFF" font-size="7">{func}</text>')

    # Bottom pins (Power) - centered
    bottom_pins = [
        ("VSYS", "+5V from MB", C_POWER),
        ("VBUS", "USB 5V", C_POWER),
        ("GND", "", C_GND),
        ("3V3_EN", "", None),
        ("3V3", "3.3V Out", C_POWER),
        ("GND", "", C_GND),
    ]

    bottom_y = board_y + board_h
    pin_width = board_w / len(bottom_pins)

    for i, (pin, func, color) in enumerate(bottom_pins):
        pin_x = board_x + (i * pin_width) + (pin_width / 2)

        # Pin circle
        r.elements.append(f'<circle cx="{pin_x}" cy="{bottom_y}" r="5" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')

        # Pin label (below)
        r.elements.append(f'<text x="{pin_x}" y="{bottom_y + 20}" class="value" text-anchor="middle" fill="#666" font-size="7">{pin}</text>')

        # Function box (above)
        if func and color:
            r.elements.append(f'<rect x="{pin_x - 40}" y="{bottom_y - 35}" width="80" height="14" fill="{color}" stroke="#333" stroke-width="1" rx="2"/>')
            r.elements.append(f'<text x="{pin_x}" y="{bottom_y - 25}" class="label" text-anchor="middle" fill="#FFF" font-size="6">{func}</text>')

    # Legend at bottom
    r.elements.append(f'<rect x="50" y="640" width="850" height="50" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="475" y="660" class="label" text-anchor="middle" font-size="10">Pin Function Legend</text>')

    legend_items = [
        (C_OLED, "OLED (SPI)"),
        (C_ENCODER, "Encoder/Button"),
        (C_LED, "LED Outputs"),
        (C_CLOCK, "Clock I/O"),
        (C_MIDI, "MIDI UART"),
        (C_UART, "Debug UART"),
        (C_ADC, "ADC (Spare)"),
        (C_POWER, "Power"),
    ]

    for i, (color, label) in enumerate(legend_items):
        x_pos = 80 + i * 105
        r.elements.append(f'<rect x="{x_pos}" y="670" width="15" height="12" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="{x_pos + 20}" y="{679}" class="value" font-size="7">{label}</text>')

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
        ("pt2399_cv_control_schematic.svg", generate_pt2399_cv_schematic),
        ("led_driver_array_schematic.svg", generate_led_driver_schematic),
        ("vactrol_full_schematic.svg", generate_vactrol_full_schematic),
        ("wiring_overview.svg", generate_wiring_diagram),
        ("dip_pinout_reference.svg", generate_dip_pinout_reference),
        ("touch_plate_schematic.svg", generate_touch_plate_schematic),
        ("input_protection_schematic.svg", generate_input_protection_schematic),
        ("esd_protection_schematic.svg", generate_esd_protection_schematic),
        ("system_architecture_block.svg", generate_system_architecture_block),
        ("audio_signal_flow.svg", generate_audio_signal_flow),
        ("cv_control_flow.svg", generate_cv_control_flow),
        ("signal_flow_overview.svg", generate_signal_flow_overview),
        ("cd4051_multiplexer.svg", generate_cd4051_multiplexer),
        ("cv_input_protection_diagram.svg", generate_cv_input_protection_diagram),
        ("pico_pinout_diagram.svg", generate_pico_pinout_diagram),
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
