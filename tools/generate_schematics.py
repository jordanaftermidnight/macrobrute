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
    .pin {{ font: 10px "SF Mono", Consolas, monospace; fill: {self.C_TEXT_LIGHT}; filter: url(#textshadow); }}
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
    r = SchematicRenderer(600, 500, "Sample &amp; Hold", "LF398 with droop compensation")
    
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
    
    r = SchematicRenderer(1000, 750, "MACROBRUTE Interconnect Wiring", "DB-9 A (Outputs) &amp; DB-9 B (Inputs + Power)")
    
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
    draw_dip(50, 250, lf398_pins, "LF398", "S&amp;H Amp", 70, lf398_pins)
    r.elements.append(f'<text x="85" y="245" class="label" font-size="10" fill="#CC0000">LF398 — Sample &amp; Hold (DIP-8)</text>')
    
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
        ("LF398:", "Sample &amp; Hold module", 530),
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
        ("S&amp;H", "Sample &amp; Hold", 200),
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
        (C_EXPANDER, "Expander Modules (Noise, LFO, S&amp;H, Clock, etc.)"),
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
    r.elements.append(f'<text x="85" y="270" class="value" font-size="8" fill="{C_TP}">via buffer</text>')
    
    # Square TP
    r.elements.append(f'<line x1="200" y1="{tp_y-5}" x2="200" y2="175" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="185" y="270" class="value" font-size="8" fill="{C_TP}">via buffer</text>')
    
    # Mix TP - from mixer
    r.elements.append(f'<line x1="320" y1="{tp_y-5}" x2="320" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="300" y="310" class="value" font-size="8" fill="{C_TP}">1kΩ + TL074</text>')
    
    # VCF TP - from VCF
    r.elements.append(f'<line x1="455" y1="{tp_y-5}" x2="455" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="435" y="310" class="value" font-size="8" fill="{C_TP}">1kΩ + TL074</text>')
    
    # VCA TP - from VCA
    r.elements.append(f'<line x1="595" y1="{tp_y-5}" x2="595" y2="270" stroke="{C_TP}" stroke-width="1" stroke-dasharray="4,2"/>')
    r.elements.append(f'<text x="575" y="310" class="value" font-size="8" fill="{C_TP}">1kΩ + TL074</text>')
    
    # Main Out - direct from output
    r.elements.append(f'<line x1="760" y1="{tp_y-5}" x2="760" y2="270" stroke="{C_TP}" stroke-width="1.5"/>')
    r.elements.append(f'<text x="740" y="310" class="value" font-size="8" fill="{C_TP}">Direct</text>')
    
    # === NOTES BOX (Bottom, clear placement) ===
    r.elements.append(f'<rect x="50" y="380" width="800" height="250" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="450" y="405" class="label" text-anchor="middle" fill="#1B5E20">Signal Flow &amp; Test Point Notes</text>')
    
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
            r.elements.append(f'<text x="{mid_x}" y="{y1-3}" class="value" text-anchor="middle" fill="{color}" font-size="8">{label}</text>')

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
        ("Exp S&amp;H", "S&amp;H", 390, C_EXPANDER),
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
    r.elements.append(f'<text x="475" y="485" class="label" text-anchor="middle" fill="#E65100">CV Routing &amp; Modulation Notes</text>')

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
        ("S&amp;H", 190),
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
        r.elements.append(f'<text x="{x+25}" y="{y-1}" class="value" text-anchor="middle" font-size="8">1kΩ</text>')
    
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
    """Generate visual Pico WH pinout diagram with aligned pin rows."""
    r = SchematicRenderer(950, 700, "Raspberry Pi Pico WH Pinout", "MACROBRUTE Hardware Configuration")

    # Colors for different function types
    C_OLED = "#2196F3"      # Blue — I²C0 OLED
    C_I2C = "#009688"       # Teal — I²C1 Daisy expansion
    C_ENCODER = "#4CAF50"   # Green
    C_LED = "#FF9800"       # Orange
    C_CLOCK = "#9C27B0"     # Purple
    C_USB = "#E91E63"       # Pink — USB-MIDI
    C_UART = "#00BCD4"      # Cyan
    C_ADC = "#795548"       # Brown
    C_POWER = "#F44336"     # Red
    C_GND = "#333"          # Dark gray

    # Draw Pico board outline
    board_x, board_y = 325, 80
    board_w, board_h = 300, 540
    r.elements.append(f'<rect x="{board_x}" y="{board_y}" width="{board_w}" height="{board_h}" fill="#1a1a1a" stroke="#555" stroke-width="3" rx="10"/>')
    r.elements.append(f'<text x="{board_x + board_w/2}" y="{board_y + 30}" class="label" text-anchor="middle" fill="#FFF" font-size="14">Raspberry Pi Pico WH</text>')

    # USB connector at top — now carries USB-MIDI
    r.elements.append(f'<rect x="{board_x + 100}" y="{board_y - 15}" width="100" height="20" fill="#E91E63" stroke="#AD1457" stroke-width="1"/>')
    r.elements.append(f'<text x="{board_x + 150}" y="{board_y - 2}" class="value" text-anchor="middle" fill="#FFF" font-size="9">Micro USB · USB-MIDI</text>')

    # Pin spacing - consistent 20px between pins
    pin_spacing = 20
    start_y = board_y + 60

    # Left side pins (GP0-GP15) - aligned in a column
    C_AUX = "#FF5722"        # Deep orange — programmable aux outputs
    C_DIV = "#9C27B0"        # Purple — clock divider outs
    C_INT = "#FF9800"        # Orange — INT line from EFFIGY
    left_pins = [
        ("GP0", "UART0 TX", "→ LPC (DB-9 B:1)", C_UART),
        ("GP1", "UART0 RX", "← LPC (DB-9 B:2)", C_UART),
        ("GND", None, None, C_GND),
        ("GP2", "I²C1 SDA", "→ EFFIGY (rear)", C_I2C),
        ("GP3", "I²C1 SCL", "→ EFFIGY (rear)", C_I2C),
        ("GP4", "I²C0 SDA", "OLEDs (main+strip)", C_OLED),
        ("GP5", "I²C0 SCL", "OLEDs (main+strip)", C_OLED),
        ("GND", None, None, C_GND),
        ("GP6", "Aux 3", "programmable", C_AUX),
        ("GP7", "Aux 4", "programmable", C_AUX),
        ("GP8", "LED R", "clock tick", C_LED),
        ("GP9", "LED G", "gate active", C_LED),
        ("GP10", "LED B", "mode/pair", C_LED),
        ("GP11", "EFFIGY INT", "open-drain in", C_INT),
        ("GP12", "Tap Button", "tempo/manual gate", C_ENCODER),
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
                r.elements.append(f'<text x="{box_x - 5}" y="{y + 3}" class="value" text-anchor="end" fill="#666" font-size="8">{detail}</text>')

    # Right side pins (GP16-GP28) - aligned in a column
    right_pins = [
        ("GP16", "Div /N out 1", C_DIV),
        ("GP17", "Div /N out 2", C_DIV),
        ("GND", None, C_GND),
        ("GP18", "Div /N out 3", C_DIV),
        ("GP19", "Aux 1", C_AUX),
        ("GP20", "Aux 2", C_AUX),
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
        ("VSYS", "+5V Eurorack", C_POWER),
        ("VBUS", "USB 5V (alt)", C_POWER),
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
            r.elements.append(f'<text x="{pin_x}" y="{bottom_y - 25}" class="label" text-anchor="middle" fill="#FFF" font-size="8">{func}</text>')

    # Legend at bottom
    r.elements.append(f'<rect x="50" y="640" width="850" height="50" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="475" y="660" class="label" text-anchor="middle" font-size="10">Pin Function Legend</text>')

    legend_items = [
        (C_OLED, "OLED I²C0 (shared)"),
        (C_I2C,  "I²C1 EFFIGY"),
        (C_INT,  "EFFIGY INT"),
        (C_ENCODER, "Encoder/Button"),
        (C_LED, "RGB LED"),
        (C_DIV, "Clock div outs"),
        (C_AUX, "Aux programmable"),
        (C_CLOCK, "Clock I/O"),
        (C_UART, "LPC bridge"),
        (C_USB, "USB-MIDI"),
        (C_ADC, "ADC (Spare)"),
        (C_POWER, "Power"),
    ]

    for i, (color, label) in enumerate(legend_items):
        x_pos = 80 + i * 105
        r.elements.append(f'<rect x="{x_pos}" y="670" width="15" height="12" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="{x_pos + 20}" y="{679}" class="value" font-size="7">{label}</text>')

    return r.render()


def generate_lpc2361_pinout_diagram() -> str:
    """Generate LPC2361 (ARM7, 100-LQFP) pinout — focused on documented MACROBRUTE usage."""
    r = SchematicRenderer(950, 650, "NXP LPC2361 Pinout (MACROBRUTE usage)", "100-LQFP ARM7TDMI-S — Stock Arturia firmware, Pico bridge via UART1")

    # IC body (LQFP rendered as rounded rect)
    ic_x, ic_y, ic_w, ic_h = 350, 140, 250, 340
    r.elements.append(f'<rect x="{ic_x}" y="{ic_y}" width="{ic_w}" height="{ic_h}" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="8"/>')
    r.elements.append(f'<circle cx="{ic_x+16}" cy="{ic_y+16}" r="4" fill="gold"/>')
    r.elements.append(f'<text x="{ic_x+ic_w/2}" y="{ic_y+ic_h/2-10}" class="label" text-anchor="middle" fill="#FFF" font-size="16">LPC2361</text>')
    r.elements.append(f'<text x="{ic_x+ic_w/2}" y="{ic_y+ic_h/2+10}" class="value" text-anchor="middle" fill="#CCC" font-size="10">ARM7TDMI-S @ 72 MHz</text>')
    r.elements.append(f'<text x="{ic_x+ic_w/2}" y="{ic_y+ic_h/2+26}" class="value" text-anchor="middle" fill="#AAA" font-size="9">128KB Flash · 34KB SRAM · 100-LQFP</text>')

    # Documented pins (left side — bridge)
    bridge_pins = [
        ("P0.15 (pin 97)", "TXD1 — UART1 TX", "→ Pico GP1 (RX) @ 115200", "#44D", 170),
        ("P0.16 (pin 96)", "RXD1 — UART1 RX", "← Pico GP0 (TX) @ 115200", "#44D", 210),
    ]
    for pin, func, note, color, y in bridge_pins:
        r.elements.append(f'<circle cx="{ic_x-5}" cy="{y}" r="3" fill="gold"/>')
        r.elements.append(f'<line x1="{ic_x-5}" y1="{y}" x2="{ic_x-80}" y2="{y}" stroke="{color}" stroke-width="1.5"/>')
        r.elements.append(f'<text x="{ic_x-85}" y="{y-2}" class="label" text-anchor="end" font-size="10">{pin}</text>')
        r.elements.append(f'<text x="{ic_x-85}" y="{y+10}" class="value" text-anchor="end" font-size="9" fill="{color}">{func}</text>')
        r.elements.append(f'<text x="{ic_x-85}" y="{y+22}" class="value" text-anchor="end" font-size="8">{note}</text>')

    # ISP / RESET (right side)
    ctrl_pins = [
        ("P2.10 (pin 53)", "ISP ENTRY", "Pull LOW during reset → bootloader", "#CC6600", 170),
        ("Pin 17", "nRESET", "Active-low system reset", "#D44", 230),
    ]
    for pin, func, note, color, y in ctrl_pins:
        r.elements.append(f'<circle cx="{ic_x+ic_w+5}" cy="{y}" r="3" fill="gold"/>')
        r.elements.append(f'<line x1="{ic_x+ic_w+5}" y1="{y}" x2="{ic_x+ic_w+80}" y2="{y}" stroke="{color}" stroke-width="1.5"/>')
        r.elements.append(f'<text x="{ic_x+ic_w+85}" y="{y-2}" class="label" font-size="10">{pin}</text>')
        r.elements.append(f'<text x="{ic_x+ic_w+85}" y="{y+10}" class="value" font-size="9" fill="{color}">{func}</text>')
        r.elements.append(f'<text x="{ic_x+ic_w+85}" y="{y+22}" class="value" font-size="8">{note}</text>')

    # Other UART for reference
    other = [("P0.2 (pin 98)", "TXD0", "stock — not used by bridge", 300),
             ("P0.3 (pin 99)", "RXD0", "stock — not used by bridge", 330)]
    for pin, func, note, y in other:
        r.elements.append(f'<circle cx="{ic_x-5}" cy="{y}" r="3" fill="#888"/>')
        r.elements.append(f'<line x1="{ic_x-5}" y1="{y}" x2="{ic_x-80}" y2="{y}" stroke="#888" stroke-width="1"/>')
        r.elements.append(f'<text x="{ic_x-85}" y="{y-2}" class="label" text-anchor="end" font-size="9" fill="#888">{pin}</text>')
        r.elements.append(f'<text x="{ic_x-85}" y="{y+10}" class="value" text-anchor="end" font-size="8">{func} — {note}</text>')

    # TODO block for undocumented pins
    r.elements.append(f'<rect x="50" y="500" width="850" height="120" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="475" y="520" class="label" text-anchor="middle" fill="#E65100" font-size="12">⚠ Undocumented Pin Usage — requires firmware RE</text>')
    todos = [
        "DAC output pin(s) for synth audio — search Ghidra labels for DACR writes",
        "Keyboard matrix scan pins — stock firmware scans via GPIO (to be identified)",
        "Panel encoder, buttons, mode LEDs — routed via port expander or direct GPIO (unknown)",
        "MIDI UART (5-pin DIN @ 31250 baud) — may reuse UART0 or separate pins",
        "Note: LPC2361 has CRP enabled. Firmware extraction blocked by Code Read Protection.",
    ]
    for i, line in enumerate(todos):
        r.elements.append(f'<text x="70" y="{540 + i*15}" class="value" font-size="9">• {line}</text>')

    # Bridge explainer
    r.elements.append(f'<text x="475" y="120" class="anno" text-anchor="middle" font-size="10">Pico ↔ LPC bridge frames: 0xAA [msg_type] [counter] [len] [payload] ...</text>')

    return r.render()


def generate_db9_connector_diagram() -> str:
    """2×DB-9 interconnect — DB-9 A: 8 audio outs + GND. DB-9 B: digital + power + 2 essential CV ins."""
    r = SchematicRenderer(1000, 820, "2× DB-9 Interconnect Detail",
                          "MicroBrute ↔ 17HP expander — DB-9 B carries UART + I²C + 2 CVs + ±12V (no aux cable)")

    def draw_db9(cx, cy, pins, title, color):
        # DB-9 trapezoid shell
        r.elements.append(f'<path d="M{cx-70},{cy-110} L{cx+70},{cy-110} L{cx+60},{cy+110} L{cx-60},{cy+110} Z" fill="#3a3a3a" stroke="#1a1a1a" stroke-width="2"/>')
        r.elements.append(f'<text x="{cx}" y="{cy-130}" class="label" text-anchor="middle" font-size="12" fill="{color}">{title}</text>')
        # 5 pins top row, 4 pins bottom row (standard DB-9)
        top_pins = [1, 2, 3, 4, 5]
        bot_pins = [6, 7, 8, 9]
        for i, pn in enumerate(top_pins):
            px = cx - 50 + i * 25
            py = cy - 80
            r.elements.append(f'<circle cx="{px}" cy="{py}" r="4" fill="gold" stroke="#B8860B" stroke-width="0.5"/>')
            r.elements.append(f'<text x="{px}" y="{py-8}" class="value" text-anchor="middle" font-size="9" fill="#FFF">{pn}</text>')
        for i, pn in enumerate(bot_pins):
            px = cx - 37 + i * 25
            py = cy - 40
            r.elements.append(f'<circle cx="{px}" cy="{py}" r="4" fill="gold" stroke="#B8860B" stroke-width="0.5"/>')
            r.elements.append(f'<text x="{px}" y="{py-8}" class="value" text-anchor="middle" font-size="9" fill="#FFF">{pn}</text>')
        # Shell label
        r.elements.append(f'<text x="{cx}" y="{cy+80}" class="value" text-anchor="middle" fill="#CCC" font-size="8">SHELL → shield drain (MB end only)</text>')

    # DB-9 A (left)
    draw_db9(180, 200, [], "DB-9 A — OUTPUTS (MB → Expander)", "#0066CC")
    # DB-9 B (right)
    draw_db9(180, 540, [], "DB-9 B — INPUTS + POWER (Expander → MB)", "#CC6600")

    # Pin tables
    pinA = [
        (1, "Gate Out",        "TP83 → CD40106 + CD4049UBE",   "10kΩ pull-up",    "White",  "#4A4"),
        (2, "Pitch CV Out",    "Rear jack (stock buffered)",   "—",               "Yellow", "#CC6600"),
        (3, "Envelope Out",    "TL072 A follower from TP5",    "10kΩ series",     "Orange", "#CC6600"),
        (4, "LFO Out",         "TL072 B follower",             "10kΩ series",     "Green",  "#4A4"),
        (5, "VCO Mix Out",     "TL074 C from TP30 (MIXER_OUT)","1kΩ series",      "Blue",   "#0066CC"),
        (6, "VCF Out",         "TL074 D from TP19",            "1kΩ series",      "Purple", "#6600CC"),
        (7, "Saw Out",         "TL074 A from TP94",            "1kΩ series",      "Red",    "#D44"),
        (8, "Square Out",      "TL074 B from TP93",            "1kΩ series",      "Brown",  "#663300"),
        (9, "GND (signal)",    "Star ground at TP72",          "—",               "Black",  "#1a1a1a"),
    ]
    pinB = [
        (1, "UART TX",         "Pico GP0 → LPC P0.16 (RXD1)",  "ferrite bead · 115200",   "White",  "#00BCD4"),
        (2, "UART RX",         "Pico GP1 ← LPC P0.15 (TXD1)",  "ferrite bead · 115200",   "Yellow", "#00BCD4"),
        (3, "I²C0 SDA",        "Pico GP4 ↔ MB-panel strip OLED 0x3D", "4.7kΩ pull-up to 3V3", "Orange", "#2196F3"),
        (4, "I²C0 SCL",        "Pico GP5 ↔ MB-panel strip OLED",      "4.7kΩ pull-up · 100kHz","Green",  "#2196F3"),
        (5, "Filter CV In",    "Summing node U8A (R67)",        "BAT54S clamp · 220kΩ",   "Blue",   "#6600CC"),
        (6, "VCA CV In",       "TP10/TP11",                     "BAT54S clamp · 100kΩ",   "Purple", "#CC6600"),
        (7, "+12V",            "Breakout +12V rail (MB buffers)","1N5817 + ferrite bead", "Red",    "#D44"),
        (8, "-12V",            "Breakout -12V rail",             "1N5817 + ferrite bead", "Brn/Str","#44D"),
        (9, "GND (power+sig)", "Star ground at TP72",            "—",                     "Black",  "#1a1a1a"),
    ]

    # A table
    r.elements.append(f'<text x="330" y="110" class="label" font-size="12" fill="#0066CC">DB-9 A — Outputs from MicroBrute</text>')
    r.elements.append(f'<rect x="330" y="120" width="640" height="25" fill="#E3F2FD" stroke="#0066CC" stroke-width="0.5"/>')
    headers = [("Pin", 345), ("Signal", 390), ("Source", 500), ("Protection / Series R", 700), ("Wire", 900)]
    for t, x in headers:
        r.elements.append(f'<text x="{x}" y="137" class="label" font-size="9">{t}</text>')
    for i, (pn, sig, src, prot, wire, col) in enumerate(pinA):
        yy = 160 + i * 18
        if i % 2 == 0:
            r.elements.append(f'<rect x="330" y="{yy-12}" width="640" height="18" fill="#F8F8F8"/>')
        r.elements.append(f'<circle cx="348" cy="{yy-4}" r="5" fill="gold" stroke="#B8860B"/>')
        r.elements.append(f'<text x="348" y="{yy-1}" class="value" text-anchor="middle" font-size="8" fill="#1a1a1a" font-weight="bold">{pn}</text>')
        r.elements.append(f'<text x="390" y="{yy}" class="label" font-size="9" fill="{col}">{sig}</text>')
        r.elements.append(f'<text x="500" y="{yy}" class="value" font-size="8">{src}</text>')
        r.elements.append(f'<text x="700" y="{yy}" class="value" font-size="8">{prot}</text>')
        r.elements.append(f'<text x="900" y="{yy}" class="value" font-size="8">{wire}</text>')

    # B table
    r.elements.append(f'<text x="330" y="450" class="label" font-size="12" fill="#CC6600">DB-9 B — Inputs + Power to MicroBrute</text>')
    r.elements.append(f'<rect x="330" y="460" width="640" height="25" fill="#FFF3E0" stroke="#CC6600" stroke-width="0.5"/>')
    for t, x in headers:
        r.elements.append(f'<text x="{x}" y="477" class="label" font-size="9">{t}</text>')
    for i, (pn, sig, src, prot, wire, col) in enumerate(pinB):
        yy = 500 + i * 18
        if i % 2 == 0:
            r.elements.append(f'<rect x="330" y="{yy-12}" width="640" height="18" fill="#F8F8F8"/>')
        r.elements.append(f'<circle cx="348" cy="{yy-4}" r="5" fill="gold" stroke="#B8860B"/>')
        r.elements.append(f'<text x="348" y="{yy-1}" class="value" text-anchor="middle" font-size="8" fill="#1a1a1a" font-weight="bold">{pn}</text>')
        r.elements.append(f'<text x="390" y="{yy}" class="label" font-size="9" fill="{col}">{sig}</text>')
        r.elements.append(f'<text x="500" y="{yy}" class="value" font-size="8">{src}</text>')
        r.elements.append(f'<text x="700" y="{yy}" class="value" font-size="8">{prot}</text>')
        r.elements.append(f'<text x="900" y="{yy}" class="value" font-size="8">{wire}</text>')

    # Notes
    r.elements.append('<rect x="50" y="680" width="920" height="120" fill="#F5F5F5" stroke="#666" stroke-width="0.5" rx="4"/>')
    notes = [
        "• Ground strategy: single return at TP72 via DB-9 B pin 9. Do not duplicate via DB-9 A pin 9 (avoid loop).",
        "• Cable: shielded DB-9 (shell tied to shield drain on MB side only). Pin layout puts digital lines (1–4) physically apart from analog CV (5–6).",
        "• Digital crosstalk mitigation: ferrite beads on UART/I²C lines at the Pico end suppress HF emissions into adjacent CV pins.",
        "• I²C @ 100 kHz tolerates the ~30 cm cable length. 400 kHz is NOT recommended for this run.",
        "• Migrated to MB panel jacks (no longer in DB-9): Resonance CV (new jack), Sync In / Gate In / Ext Audio In (use stock MB back-panel jacks).",
        "• VGA HD-15 rejected — commodity VGA cables short pins 6/7/8 to GND, which would collide with our signal assignments.",
        "• All audio outputs buffered (TL072/TL074, unity gain). All CV inputs clamped to ±5V via BAT54S before op-amp stage.",
    ]
    for i, line in enumerate(notes):
        r.elements.append(f'<text x="65" y="{700 + i*15}" class="value" font-size="9">{line}</text>')

    return r.render()


def generate_power_regulation_diagram() -> str:
    """Power flow: Behringer CP1A Eurorack PSU → expander → Pico VSYS + DB-9 B to MB breakout."""
    r = SchematicRenderer(1050, 600, "Power Regulation Chain",
                          "Behringer CP1A bus → expander → Pico VSYS · DB-9 B carries ±12V to MB breakout · MicroBrute stock power untouched")

    def draw_stage(x, y, w, h, title, detail, color):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="1.5" rx="4"/>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+22}" class="label" text-anchor="middle" fill="#FFF" font-size="11">{title}</text>')
        for i, line in enumerate(detail):
            r.elements.append(f'<text x="{x+w/2}" y="{y+40 + i*13}" class="value" text-anchor="middle" fill="#FFF" font-size="9">{line}</text>')

    def draw_arrow(x1, y1, x2, y2, label=""):
        r.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1a1a1a" stroke-width="2" marker-end="url(#arrow)"/>')
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            r.elements.append(f'<text x="{mx}" y="{my-6}" class="anno" text-anchor="middle" font-size="9">{label}</text>')

    # Stage 1: Eurorack PSU (CP1A reference)
    draw_stage(40, 90, 200, 120, "Behringer CP1A PSU",
               ["+12V · -12V · +5V on bus", "13V / 3A wall input",
                "+5V rail ~1A available"], "#555")
    # Stage 2: Pico power filter (3-part minimal)
    draw_stage(280, 90, 200, 120, "Pico Power Filter",
               ["1N5817 reverse-polarity",
                "100µF/10V bulk",
                "100nF ceramic HF bypass"], "#D44")
    # Stage 3: Pico VSYS
    draw_stage(520, 90, 200, 120, "Pico VSYS (pin 39)",
               ["Direct from filtered +5V",
                "Pico draws ~100 mA",
                "Internal LDO → 3V3 (pin 36)"], "#6600CC")
    # Stage 4: ±12V passthrough to MB breakout (does not power the Pico)
    draw_stage(520, 240, 200, 120, "DB-9 B → MB breakout",
               ["+12V (pin 7), -12V (pin 8)",
                "1N5817 + ferrite + 100µF",
                "Powers MB-side op-amp buffers"], "#44D")
    # Stage 5: Expander analog rails
    draw_stage(760, 90, 240, 120, "Expander analog rails",
               ["+12V / -12V → slew op-amp",
                "+5V → Pico VSYS path",
                "GND → star at expander"], "#4A4")
    # Stage 6: MB breakout
    draw_stage(760, 240, 240, 120, "MB-side breakout PCB",
               ["±12V via DB-9 B → buffers",
                "Receives ±12V only",
                "Star ground at TP72"], "#0066CC")

    # Arrows
    draw_arrow(240, 130, 280, 130, "+5V")
    draw_arrow(240, 170, 280, 170, "GND")
    draw_arrow(480, 150, 520, 150, "VSYS")
    draw_arrow(720, 150, 760, 150, "")
    draw_arrow(720, 300, 760, 300, "DB-9 B")
    draw_arrow(140, 210, 600, 240, "")  # ±12V Eurorack → DB-9 B routing

    # Big-print note: non-invasive principle
    r.elements.append('<rect x="40" y="400" width="470" height="170" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append('<text x="275" y="420" class="label" text-anchor="middle" fill="#1B5E20" font-size="12">Non-invasive principle</text>')
    invariants = [
        "• MicroBrute stock power is NOT tapped or modified.",
        "• Pico is fed from Eurorack +5V (CP1A bus), not from any MB rail.",
        "• MB breakout PCB receives only ±12V via DB-9 B for op-amp buffers.",
        "• Removing the DB-9 B cable leaves both MB and Pico in clean states.",
        "• MB stock 5V regulator is never loaded by the mod.",
        "• Star ground at TP72 — single return for audio/CV/gate.",
    ]
    for i, line in enumerate(invariants):
        r.elements.append(f'<text x="55" y="{445 + i*19}" class="value" font-size="9">{line}</text>')

    # Current budget
    r.elements.append('<rect x="540" y="400" width="470" height="170" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append('<text x="775" y="420" class="label" text-anchor="middle" fill="#E65100" font-size="12">Current budget</text>')
    budget = [
        "• +5V from CP1A bus: ~150 mA (Pico + main OLED + strip OLED + LEDs)",
        "• +12V from CP1A bus: ~80 mA (slew op-amp, MB-side buffers via DB-9 B)",
        "• -12V from CP1A bus: ~50 mA (op-amp negative rails)",
        "• CP1A rated: ±12V @ 500 mA, +5V @ 1 A → comfortable headroom.",
        "• Pico filter: 1N5817 (0.2 V drop) + 100 µF + 100 nF — shop-stocked parts.",
        "• Optional armor (defer): PPTC 500 mA fuse, SMAJ5.0A TVS, ferrite bead.",
    ]
    for i, line in enumerate(budget):
        r.elements.append(f'<text x="555" y="{445 + i*19}" class="value" font-size="9">{line}</text>')

    return r.render()


def generate_testpoints_map() -> str:
    """Generate MicroBrute test-points map — 18 documented TPs organized by board + function."""
    r = SchematicRenderer(1050, 780, "MicroBrute Test-Points Map", "18 documented test points used by MACROBRUTE mod — front board, rear board, power")

    def tp_group(x, y, w, h, title, subtitle, color, rows):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F8F8F8" stroke="{color}" stroke-width="1.5" rx="4"/>')
        r.elements.append(f'<text x="{x+12}" y="{y+22}" class="label" font-size="12" fill="{color}">{title}</text>')
        r.elements.append(f'<text x="{x+12}" y="{y+38}" class="value" font-size="9">{subtitle}</text>')
        for i, (tp, sig, usage) in enumerate(rows):
            yy = y + 60 + i * 20
            r.elements.append(f'<circle cx="{x+22}" cy="{yy-4}" r="8" fill="{color}" stroke="#1a1a1a"/>')
            r.elements.append(f'<text x="{x+22}" y="{yy-1}" class="value" text-anchor="middle" font-size="8" fill="#FFF" font-weight="bold">{tp}</text>')
            r.elements.append(f'<text x="{x+42}" y="{yy}" class="label" font-size="9">{sig}</text>')
            r.elements.append(f'<text x="{x+160}" y="{yy}" class="value" font-size="9">{usage}</text>')

    # Rear board — waveform outputs
    rear_waves = [
        ("TP93",  "Square (raw)",        "DB-9 A:8 · touch-bend T5"),
        ("TP94",  "Sawtooth (raw)",      "DB-9 A:7"),
        ("TP102", "Sub osc",             "spare body jack"),
        ("TP109", "Metalizer pre-mix",   "body jack / touch bend"),
        ("TP110", "Metalizer post-mix",  "touch-bend T6 (feedback)"),
        ("TP124", "Triangle (raw)",      "2× gain → body jack"),
    ]
    tp_group(30, 70, 320, 210, "Rear Board — Waveforms (~10Vpp)", "Buffered via TL074 @ unity or 2× gain", "#D44", rear_waves)

    # Front board — filter/control
    front_ctrl = [
        ("TP5",  "Envelope 2 Out",      "DB-9 A:3 (TL072 follower, 10kΩ)"),
        ("TP19", "VCF Out",             "DB-9 A:6 (TL074, 1kΩ)"),
        ("TP26", "Filter CV inject",    "DB-9 B:1 via R67 summing"),
        ("TP30", "VCO Mix (MIXER_OUT)", "DB-9 A:5 (TL074, 1kΩ)"),
    ]
    tp_group(370, 70, 320, 150, "Front Board — Filter / Control", "Summing node access, pre- and post-filter", "#0066CC", front_ctrl)

    # CV injection points
    cv_inject = [
        ("TP10", "CV1 (VCA)",            "panel jack — 100kΩ already in circuit"),
        ("TP11", "CV2 (VCA)",            "alternate VCA CV input"),
        ("TP12", "Misc Amplitude",       "DB-9 B:2 via 100kΩ"),
    ]
    tp_group(710, 70, 320, 130, "Front Board — CV Injection", "Use existing 100kΩ series resistance", "#6600CC", cv_inject)

    # Gate
    gate_row = [
        ("TP83", "Gate from µC", "DB-9 A:1 (CD40106 + CD4049UBE buffer chain, 100kΩ source Z)"),
    ]
    tp_group(370, 240, 660, 70, "Rear Board — Gate", "High source impedance → needs Schmitt + level shift before DB-9", "#4A4", gate_row)

    # Power taps
    power_taps = [
        ("TP70", "+12V",  "Breakout +12V rail (22AWG + 1N5817 + ferrite)"),
        ("TP71", "-12V",  "Breakout -12V rail (22AWG + 1N5817 + ferrite)"),
        ("TP72", "GND",   "⭐ Star ground — single return for DB-9, breakout, expander"),
    ]
    tp_group(30, 330, 660, 130, "Power Taps (shared with stock Arturia rails)", "22AWG stranded · 1N5817 Schottky reverse-polarity on each rail", "#CC6600", power_taps)

    # Touch bends
    touch_bends = [
        ("T1", "PITCH (R309 area)",        "10kΩ safety · vibrato"),
        ("T2", "CRUNCH (C111)",            "4.7kΩ · wavefolder sweep"),
        ("T3", "WAH (filter CV input)",    "22kΩ · manual sweep"),
        ("T4", "DISTORT (TP4 feedback)",   "15kΩ · self-oscillation"),
        ("T5", "HARM (C106 + C107)",       "10kΩ each · cross-coupled"),
        ("T6", "GATE (Metalizer loop)",    "1kΩ · feedback closure"),
    ]
    tp_group(710, 330, 320, 210, "Touch Bends (6 of 8 tested)", "Body-resistance CV mod · Brass M3 bolts through panel", "#CC6600", touch_bends)

    # Footnotes
    r.elements.append(f'<rect x="30" y="570" width="1000" height="190" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="530" y="592" class="label" text-anchor="middle" fill="#E65100" font-size="12">Physical Location &amp; Assembly Notes</text>')
    footnotes = [
        "• Rear board TPs (waveforms, gate, power): accessible with the case open — remove 4 screws + encoder knob. No panel disassembly needed.",
        "• Front board TPs (filter, CV): require lifting the front panel to access. Use a thin hooked probe.",
        "• TP26 (filter CV inject) is the designated mod point for external filter modulation — R67 (220kΩ) is the summing resistor.",
        "• TP72 is the ONLY ground point the mod taps. All GND returns (DB-9 A:9, DB-9 B:9, breakout, LED driver) converge here.",
        "• Touch bends breadboarded before final panel install — test all 8 candidates, select 6 based on musical effect (documented in touch_bend_specs.md).",
        "• After soldering taps, wrap each wire at the PCB exit with heatshrink + strain relief (hot-glue drop on stranded AWG24 or AWG22).",
        "• DO NOT tap TP1-TP4 on the rear board without the bend table — those are raw oscillator cores and short-circuiting will damage the LPC2361 DAC.",
        "• All TPs retain stock functionality — mods are non-destructive and reversible if wire is cut at the solder joint (no PCB traces cut).",
    ]
    for i, line in enumerate(footnotes):
        r.elements.append(f'<text x="45" y="{612 + i*18}" class="value" font-size="9">{line}</text>')

    return r.render()


def generate_expander_power_distribution() -> str:
    """17HP expander power + 5-pin EFFIGY rear header. Most utilities are firmware or external."""
    r = SchematicRenderer(1100, 720, "Expander Power Distribution (17HP)",
                          "Behringer CP1A bus → Pico (filtered) + slew op-amp · 5-pin rear I²C header (EFFIGY) · clock divider in firmware")

    # Eurorack bus header (left)
    r.elements.append('<rect x="40" y="80" width="180" height="200" fill="#2a2a2a" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
    r.elements.append('<text x="130" y="105" class="label" text-anchor="middle" fill="#FFF" font-size="12">CP1A Bus</text>')
    r.elements.append('<text x="130" y="122" class="value" text-anchor="middle" fill="#CCC" font-size="9">16-pin Eurorack IDC</text>')
    rails = [("+12V", "#D44", 150), ("GND", "#4A4", 170), ("GND", "#4A4", 190),
             ("-12V", "#44D", 210), ("+5V", "#CC6600", 230), ("CV/Gate", "#888", 250)]
    for rail, color, y in rails:
        r.elements.append(f'<rect x="60" y="{y}" width="140" height="14" fill="{color}"/>')
        r.elements.append(f'<text x="130" y="{y+10}" class="value" text-anchor="middle" font-size="8" fill="#FFF">{rail}</text>')

    # Pico power filter (3 parts — minimal)
    r.elements.append('<rect x="250" y="80" width="200" height="220" fill="#FFF0F0" stroke="#D44" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="350" y="105" class="label" text-anchor="middle" font-size="11" fill="#D44">Pico power filter</text>')
    r.elements.append('<text x="350" y="122" class="value" text-anchor="middle" font-size="9">3 commodity parts</text>')
    parts = [
        ("1N5817", "Schottky · reverse polarity", 145),
        ("100µF/10V", "Bulk electrolytic", 175),
        ("100nF", "HF ceramic bypass", 205),
    ]
    for name, role, y in parts:
        r.elements.append(f'<text x="270" y="{y}" class="label" font-size="10">{name}</text>')
        r.elements.append(f'<text x="270" y="{y+13}" class="value" font-size="8">{role}</text>')
    r.elements.append('<text x="350" y="245" class="value" text-anchor="middle" font-size="8" fill="#888">Optional armor (defer):</text>')
    r.elements.append('<text x="350" y="258" class="value" text-anchor="middle" font-size="8" fill="#888">PPTC 500 mA · SMAJ5.0A · ferrite</text>')
    r.elements.append('<text x="350" y="280" class="value" text-anchor="middle" font-size="9" fill="#1B5E20">All parts shop-stocked</text>')

    # Pico VSYS
    r.elements.append('<rect x="480" y="80" width="180" height="220" fill="#F3E5F5" stroke="#6600CC" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="570" y="105" class="label" text-anchor="middle" font-size="11" fill="#6600CC">Pico VSYS</text>')
    r.elements.append('<text x="570" y="122" class="value" text-anchor="middle" font-size="9">pin 39 · ~100 mA</text>')
    r.elements.append('<text x="570" y="150" class="value" text-anchor="middle" font-size="9">Internal LDO →</text>')
    r.elements.append('<text x="570" y="163" class="value" text-anchor="middle" font-size="9">3V3 (pin 36)</text>')
    r.elements.append('<text x="570" y="190" class="value" text-anchor="middle" font-size="9">Powers main OLED,</text>')
    r.elements.append('<text x="570" y="203" class="value" text-anchor="middle" font-size="9">strip OLED, encoder,</text>')
    r.elements.append('<text x="570" y="216" class="value" text-anchor="middle" font-size="9">RGB LED, all GPIO</text>')
    r.elements.append('<text x="570" y="245" class="value" text-anchor="middle" font-size="9">USB-MIDI via</text>')
    r.elements.append('<text x="570" y="258" class="value" text-anchor="middle" font-size="9">micro-USB (alt path)</text>')

    # Hardware utilities (just slew on this expander)
    r.elements.append('<rect x="690" y="80" width="180" height="100" fill="#FFFFFF" stroke="#6600CC" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="780" y="105" class="label" text-anchor="middle" font-size="11" fill="#6600CC">Slew limiter (HW)</text>')
    r.elements.append('<text x="780" y="125" class="value" text-anchor="middle" font-size="9">TL072 + 2 diodes</text>')
    r.elements.append('<text x="780" y="140" class="value" text-anchor="middle" font-size="9">±12V supply</text>')
    r.elements.append('<text x="780" y="160" class="value" text-anchor="middle" font-size="9">~10 mA draw</text>')

    # Firmware-only stuff
    r.elements.append('<rect x="690" y="200" width="180" height="100" fill="#E8F5E9" stroke="#4A4" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="780" y="225" class="label" text-anchor="middle" font-size="11" fill="#4A4">Firmware only</text>')
    r.elements.append('<text x="780" y="245" class="value" text-anchor="middle" font-size="9">Clock divider (GP16/17/18)</text>')
    r.elements.append('<text x="780" y="260" class="value" text-anchor="middle" font-size="9">4 aux outputs (GP19/20/6/7)</text>')
    r.elements.append('<text x="780" y="275" class="value" text-anchor="middle" font-size="9">No CD4024 chip needed</text>')

    # MB breakout (powered via DB-9 B)
    r.elements.append('<rect x="900" y="80" width="180" height="220" fill="#E3F2FD" stroke="#0066CC" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="990" y="105" class="label" text-anchor="middle" font-size="11" fill="#0066CC">MB breakout</text>')
    r.elements.append('<text x="990" y="122" class="value" text-anchor="middle" font-size="9">via DB-9 B</text>')
    r.elements.append('<text x="990" y="150" class="value" text-anchor="middle" font-size="9">±12V → buffers</text>')
    r.elements.append('<text x="990" y="165" class="value" text-anchor="middle" font-size="9">(TL074, TL072,</text>')
    r.elements.append('<text x="990" y="178" class="value" text-anchor="middle" font-size="9">CD40106, CD4049)</text>')
    r.elements.append('<text x="990" y="205" class="value" text-anchor="middle" font-size="9">Star GND at TP72</text>')
    r.elements.append('<text x="990" y="240" class="value" text-anchor="middle" font-size="8" fill="#666">MB stock 5V untouched</text>')
    r.elements.append('<text x="990" y="253" class="value" text-anchor="middle" font-size="8" fill="#666">— mod is non-invasive</text>')

    # Flow arrows
    r.elements.append('<line x1="220" y1="170" x2="250" y2="170" stroke="#888" stroke-width="2" marker-end="url(#arrow)"/>')
    r.elements.append('<text x="235" y="162" class="anno" text-anchor="middle" font-size="8">+5V</text>')
    r.elements.append('<line x1="450" y1="170" x2="480" y2="170" stroke="#888" stroke-width="2" marker-end="url(#arrow)"/>')
    r.elements.append('<line x1="660" y1="130" x2="690" y2="130" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>')
    r.elements.append('<line x1="660" y1="245" x2="690" y2="245" stroke="#888" stroke-width="1.5" marker-end="url(#arrow)"/>')
    r.elements.append('<line x1="220" y1="220" x2="900" y2="220" stroke="#44D" stroke-width="1.5" stroke-dasharray="6,4"/>')
    r.elements.append('<text x="560" y="215" class="anno" text-anchor="middle" font-size="8" fill="#44D">±12V via DB-9 B → MB</text>')

    # Rear EFFIGY 5-pin header (UPDATED — was 4-pin)
    r.elements.append('<rect x="40" y="330" width="500" height="220" fill="#E0F2F1" stroke="#009688" stroke-width="2" rx="4"/>')
    r.elements.append('<text x="290" y="355" class="label" text-anchor="middle" font-size="13" fill="#009688">REAR I²C HEADER → EFFIGY (hidden, 5-pin)</text>')
    r.elements.append('<text x="290" y="372" class="value" text-anchor="middle" font-size="9">5-pin JST-XH · mounted behind panel · accessed with case open</text>')
    pins = [
        ("1", "SDA",   "Pico GP2 — I²C1 SDA",          "#009688"),
        ("2", "SCL",   "Pico GP3 — I²C1 SCL",          "#009688"),
        ("3", "INT",   "Pico GP11 — open-drain from EFFIGY", "#FF9800"),
        ("4", "+3.3V", "Pull-ups only (4.7kΩ on each line)", "#D44"),
        ("5", "GND",   "Star ground reference",         "#1a1a1a"),
    ]
    for i, (pn, sig, detail, color) in enumerate(pins):
        yy = 395 + i * 28
        r.elements.append(f'<circle cx="75" cy="{yy}" r="10" fill="gold" stroke="#B8860B"/>')
        r.elements.append(f'<text x="75" y="{yy+3}" class="value" text-anchor="middle" font-size="9" fill="#1a1a1a" font-weight="bold">{pn}</text>')
        r.elements.append(f'<text x="100" y="{yy+3}" class="label" font-size="10" fill="{color}">{sig}</text>')
        r.elements.append(f'<text x="170" y="{yy+3}" class="value" font-size="9">{detail}</text>')
    r.elements.append('<text x="290" y="540" class="value" text-anchor="middle" font-size="8" fill="#666">100 kHz · &lt; 30 cm shielded · target address 0x42 · see docs/MACROBRUTE_EFFIGY_BRIDGE.md</text>')

    # EFFIGY callout
    r.elements.append('<rect x="560" y="330" width="520" height="220" fill="#F3E5F5" stroke="#6600CC" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="820" y="355" class="label" text-anchor="middle" font-size="12" fill="#6600CC">EFFIGY (24HP Daisy DSP, separate module)</text>')
    daisy = [
        "• Standalone Eurorack audio + CV processor — pair mode is purely additive.",
        "• I²C target at 0x42 (see bridge spec). Audio + fast CV stay on patch cables.",
        "• Bus carries: parameter writes (~100 Hz), telemetry, events (INT-driven), pair coordination.",
        "• Default role on pair: MACROBRUTE owns clock, EFFIGY owns main menu, EFFIGY encoder drives.",
        "• Heartbeat-watched link · 1-second pair-loss timeout · graceful solo fallback.",
        "• Power independent — EFFIGY has its own Eurorack bus connection. Header shares only GND.",
        "• I²C addresses: main OLED 0x3C, strip OLED 0x3D, EFFIGY 0x42 — no conflicts.",
    ]
    for i, line in enumerate(daisy):
        r.elements.append(f'<text x="575" y="{378 + i*17}" class="value" font-size="9">{line}</text>')

    # Current budget (revised for 17HP minimal expander)
    r.elements.append('<rect x="40" y="580" width="1040" height="120" fill="#F5F5F5" stroke="#666" stroke-width="0.5" rx="4"/>')
    r.elements.append('<text x="560" y="602" class="label" text-anchor="middle" font-size="12">Current Budget (17HP minimal expander)</text>')
    budget = [
        "• +5V: ~150 mA (Pico ≈ 100 mA + main OLED ≈ 20 mA + strip OLED ≈ 10 mA + RGB LED + I²C pull-ups)",
        "• +12V: ~30 mA (slew TL072 quiescent + headroom; MB-side buffers via DB-9 B add ~50 mA more on the same rail)",
        "• -12V: ~25 mA (op-amp negative rails only — slew + MB buffers)",
        "• CP1A rated: ±12V @ 500 mA, +5V @ 1 A. Total mod draw &lt; 250 mA per rail. Comfortable headroom.",
        "• Dropped utilities (using user's existing rack): noise (NOISE module), S&amp;H (RND CV), buffered mult ('07 MULT), LFO (Tryfelo).",
    ]
    for i, line in enumerate(budget):
        r.elements.append(f'<text x="55" y="{623 + i*16}" class="value" font-size="9">{line}</text>')

    return r.render()


def generate_midi_interface_circuit() -> str:
    """Generate MIDI interface: 5-pin DIN → 6N138 optocoupler → LPC UART0 (stock) + Pico USB-MIDI parallel path."""
    r = SchematicRenderer(1100, 700, "MIDI Interfaces",
                          "5-pin DIN → 6N138 → LPC2361 (stock Arturia) · Pico micro-USB → USB-MIDI (new)")

    def box(x, y, w, h, title, color, fill="#FFFFFF"):
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{color}" stroke-width="1.5" rx="4"/>')
        r.elements.append(f'<text x="{x+w/2}" y="{y+20}" class="label" text-anchor="middle" font-size="11" fill="{color}">{title}</text>')

    # Top lane: STOCK DIN-MIDI path (LPC-only, untouched by mod)
    r.elements.append(f'<rect x="30" y="60" width="1040" height="260" fill="#F5F5F5" stroke="#1a1a1a" stroke-width="1" stroke-dasharray="5,5" rx="6"/>')
    r.elements.append(f'<text x="550" y="80" class="label" text-anchor="middle" font-size="13">LANE A — Stock Arturia DIN-MIDI (unmodified)</text>')
    r.elements.append(f'<text x="550" y="96" class="value" text-anchor="middle" font-size="9">Do NOT tap or reroute — this is the existing MicroBrute MIDI path. Mod does not touch it.</text>')

    # DIN jack
    box(60, 120, 130, 140, "5-pin DIN IN", "#1a1a1a")
    r.elements.append(f'<circle cx="125" cy="200" r="38" fill="none" stroke="#333" stroke-width="2"/>')
    # 5 pins arranged in DIN pattern
    din_pins = [(125, 170, "2"), (97, 188, "4"), (153, 188, "5"), (107, 218, "1"), (143, 218, "3")]
    for px, py, pn in din_pins:
        r.elements.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#333"/>')
        r.elements.append(f'<text x="{px+10}" y="{py+3}" class="value" font-size="8">{pn}</text>')
    r.elements.append(f'<text x="125" y="250" class="value" text-anchor="middle" font-size="9">Standard MIDI-IN</text>')

    # Wiring: DIN 4/5 through 220Ω each
    r.elements.append(f'<line x1="190" y1="188" x2="220" y2="188" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append(f'<rect x="222" y="182" width="30" height="12" fill="#FFFBE6" stroke="#999"/>')
    r.elements.append(f'<text x="237" y="192" class="value" text-anchor="middle" font-size="8">220Ω</text>')
    r.elements.append(f'<line x1="252" y1="188" x2="290" y2="188" stroke="#1a1a1a" stroke-width="1.5"/>')

    # 6N138 optocoupler
    box(290, 130, 180, 160, "6N138 optocoupler", "#6600CC", "#F3E5F5")
    r.elements.append(f'<text x="380" y="175" class="value" text-anchor="middle" font-size="9">Pin 2: IR LED anode</text>')
    r.elements.append(f'<text x="380" y="190" class="value" text-anchor="middle" font-size="9">Pin 3: IR LED cathode (to DIN pin 4 via 220Ω)</text>')
    r.elements.append(f'<text x="380" y="215" class="value" text-anchor="middle" font-size="9">Pin 5: GND  Pin 8: +5V</text>')
    r.elements.append(f'<text x="380" y="230" class="value" text-anchor="middle" font-size="9">Pin 6: open-collector output</text>')
    r.elements.append(f'<text x="380" y="245" class="value" text-anchor="middle" font-size="8">→ 4.7kΩ pull-up to +5V</text>')
    r.elements.append(f'<text x="380" y="265" class="value" text-anchor="middle" font-size="8">1N4148 across IR LED (anti-reverse)</text>')

    # Pull-up
    r.elements.append(f'<line x1="470" y1="210" x2="520" y2="210" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append(f'<line x1="495" y1="210" x2="495" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append(f'<rect x="480" y="160" width="30" height="20" fill="#FFFBE6" stroke="#999"/>')
    r.elements.append(f'<text x="495" y="173" class="value" text-anchor="middle" font-size="8">4.7k</text>')
    r.elements.append(f'<text x="495" y="153" class="value" text-anchor="middle" font-size="8" fill="#D44">+5V</text>')

    # LPC2361 block
    box(540, 130, 200, 160, "LPC2361 UART0 RX", "#0066CC", "#E3F2FD")
    r.elements.append(f'<text x="640" y="175" class="value" text-anchor="middle" font-size="9">P0.3 (pin 99)</text>')
    r.elements.append(f'<text x="640" y="195" class="value" text-anchor="middle" font-size="9">31250 baud, 8N1</text>')
    r.elements.append(f'<text x="640" y="215" class="value" text-anchor="middle" font-size="9">Stock Arturia firmware</text>')
    r.elements.append(f'<text x="640" y="235" class="value" text-anchor="middle" font-size="8">handles SysEx, note on/off,</text>')
    r.elements.append(f'<text x="640" y="250" class="value" text-anchor="middle" font-size="8">CC, program change, clock</text>')
    r.elements.append(f'<text x="640" y="270" class="value" text-anchor="middle" font-size="8">Relays internal events to</text>')
    r.elements.append(f'<text x="640" y="283" class="value" text-anchor="middle" font-size="8">Pico via UART1 bridge</text>')

    # To Pico (via bridge)
    r.elements.append(f'<line x1="740" y1="210" x2="820" y2="210" stroke="#0066CC" stroke-width="2" marker-end="url(#arrow)"/>')
    box(820, 170, 220, 80, "Pico UART0 bridge", "#00BCD4", "#E0F7FA")
    r.elements.append(f'<text x="930" y="212" class="value" text-anchor="middle" font-size="9">GP0/GP1 @ 115200</text>')
    r.elements.append(f'<text x="930" y="228" class="value" text-anchor="middle" font-size="8">Receives MIDI-as-SysEx</text>')

    # Bottom lane: NEW USB-MIDI path (Pico)
    r.elements.append(f'<rect x="30" y="350" width="1040" height="260" fill="#FCE4EC" stroke="#E91E63" stroke-width="1.5" rx="6"/>')
    r.elements.append(f'<text x="550" y="370" class="label" text-anchor="middle" font-size="13" fill="#E91E63">LANE B — Pico USB-MIDI (new, computer-facing)</text>')
    r.elements.append(f'<text x="550" y="386" class="value" text-anchor="middle" font-size="9">Pico enumerates as a USB-MIDI class device. Host DAW/computer sees it as a MIDI port. Does NOT drive 5-pin DIN.</text>')

    # Computer
    box(60, 410, 150, 140, "Host computer / DAW", "#1a1a1a", "#EEEEEE")
    r.elements.append(f'<text x="135" y="450" class="value" text-anchor="middle" font-size="9">Ableton, Bitwig,</text>')
    r.elements.append(f'<text x="135" y="465" class="value" text-anchor="middle" font-size="9">Reaper, etc.</text>')
    r.elements.append(f'<text x="135" y="490" class="value" text-anchor="middle" font-size="8">USB host · macOS/Linux</text>')
    r.elements.append(f'<text x="135" y="505" class="value" text-anchor="middle" font-size="8">detects Pico as MIDI dev</text>')
    r.elements.append(f'<text x="135" y="525" class="value" text-anchor="middle" font-size="9">"Macrobrute Pico"</text>')

    # USB cable
    r.elements.append(f'<line x1="210" y1="480" x2="280" y2="480" stroke="#E91E63" stroke-width="3"/>')
    r.elements.append(f'<text x="245" y="472" class="anno" text-anchor="middle" font-size="9" fill="#E91E63">USB 2.0</text>')

    # Pico with micro-USB
    box(280, 410, 220, 140, "Pico WH · micro-USB", "#E91E63", "#FFF0F5")
    r.elements.append(f'<rect x="300" y="440" width="40" height="20" fill="#E91E63" stroke="#AD1457"/>')
    r.elements.append(f'<text x="320" y="454" class="value" text-anchor="middle" font-size="8" fill="#FFF">USB</text>')
    r.elements.append(f'<text x="390" y="452" class="value" font-size="9">VBUS +5V → VSYS</text>')
    r.elements.append(f'<text x="390" y="467" class="value" font-size="9">D+/D- → RP2040 USB PHY</text>')
    r.elements.append(f'<text x="390" y="490" class="value" font-size="9">TinyUSB (MicroPython)</text>')
    r.elements.append(f'<text x="390" y="505" class="value" font-size="9">exposes MIDI class device</text>')
    r.elements.append(f'<text x="390" y="525" class="value" font-size="8" fill="#666">CDC-ACM optional for debug</text>')

    # Firmware block
    box(540, 410, 240, 140, "Pico firmware (usbmidi.py)", "#CC6600", "#FFF3E0")
    r.elements.append(f'<text x="660" y="450" class="value" text-anchor="middle" font-size="9">midi_in → menu / clock /</text>')
    r.elements.append(f'<text x="660" y="465" class="value" text-anchor="middle" font-size="9">tap tempo / mode switch</text>')
    r.elements.append(f'<text x="660" y="488" class="value" text-anchor="middle" font-size="9">midi_out ← events from</text>')
    r.elements.append(f'<text x="660" y="503" class="value" text-anchor="middle" font-size="9">encoder / clock / LPC bridge</text>')
    r.elements.append(f'<text x="660" y="525" class="value" text-anchor="middle" font-size="8" fill="#666">(to be implemented — issue #TBD)</text>')

    # Bridge to LPC (optional forwarding)
    r.elements.append(f'<line x1="780" y1="480" x2="830" y2="480" stroke="#1a1a1a" stroke-width="1.5" marker-end="url(#arrow)"/>')
    box(830, 440, 210, 80, "Optional: forward to LPC", "#0066CC")
    r.elements.append(f'<text x="935" y="482" class="value" text-anchor="middle" font-size="9">Convert USB-MIDI event →</text>')
    r.elements.append(f'<text x="935" y="497" class="value" text-anchor="middle" font-size="8">SysEx frame over UART1</text>')
    r.elements.append(f'<text x="935" y="512" class="value" text-anchor="middle" font-size="8">(so DAW controls synth)</text>')

    # Footer notes
    r.elements.append(f'<rect x="30" y="625" width="1040" height="60" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="550" y="645" class="label" text-anchor="middle" font-size="11" fill="#E65100">Design Summary</text>')
    r.elements.append(f'<text x="55" y="665" class="value" font-size="9">• DIN MIDI IN stays stock (LPC handles it). Pico USB-MIDI is additive — adds a second MIDI port for computer integration.</text>')
    r.elements.append(f'<text x="55" y="680" class="value" font-size="9">• Optional bridge path: USB-MIDI received by Pico → SysEx frame → LPC → internal MicroBrute MIDI → DAW drives oscillator/filter/VCA remotely.</text>')

    return r.render()


def generate_pico_power_protection() -> str:
    """3-part Pico power filter — 1N5817 + 100µF + 100nF. Stripboard-friendly."""
    r = SchematicRenderer(900, 540, "Pico Power Protection",
                          "Eurorack +5V → 3-part minimal filter → Pico VSYS · all parts shop-stocked")

    # Title strip with the chain
    chain_y = 100
    nodes = [
        ("Eurorack +5V",   90,   "#CC6600", "from CP1A bus"),
        ("1N5817",         260,  "#D44",    "Schottky · ~0.2V drop"),
        ("100µF/10V",      430,  "#0066CC", "bulk electrolytic"),
        ("100nF ceramic",  600,  "#4A4",    "HF bypass"),
        ("Pico VSYS",      770,  "#6600CC", "pin 39 · ~100mA"),
    ]
    for name, x, color, sub in nodes:
        r.elements.append(f'<rect x="{x-60}" y="{chain_y-30}" width="120" height="80" fill="{color}" stroke="#1a1a1a" stroke-width="1.5" rx="6"/>')
        r.elements.append(f'<text x="{x}" y="{chain_y}" class="label" text-anchor="middle" fill="#FFF" font-size="11">{name}</text>')
        r.elements.append(f'<text x="{x}" y="{chain_y+18}" class="value" text-anchor="middle" fill="#FFF" font-size="9">{sub}</text>')
    # Connect
    for x1, x2 in [(150, 200), (320, 370), (490, 540), (660, 710)]:
        r.elements.append(f'<line x1="{x1}" y1="{chain_y+10}" x2="{x2}" y2="{chain_y+10}" stroke="#1a1a1a" stroke-width="2.5" marker-end="url(#arrow)"/>')

    # Schematic-style detail
    r.elements.append('<text x="450" y="220" class="label" text-anchor="middle" font-size="13">Schematic detail</text>')
    # Diode symbol
    r.elements.append('<line x1="120" y1="290" x2="180" y2="290" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<polygon points="180,278 180,302 210,290" fill="none" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<line x1="210" y1="276" x2="210" y2="304" stroke="#1a1a1a" stroke-width="2.5"/>')
    r.elements.append('<line x1="210" y1="290" x2="270" y2="290" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="195" y="265" class="label" text-anchor="middle" font-size="9">1N5817</text>')
    r.elements.append('<text x="100" y="285" class="value" text-anchor="end" font-size="9" fill="#CC6600">+5V</text>')
    # Junction
    r.elements.append('<circle cx="320" cy="290" r="3" fill="#0066CC"/>')
    r.elements.append('<line x1="270" y1="290" x2="430" y2="290" stroke="#1a1a1a" stroke-width="2"/>')
    # 100µF (vertical)
    r.elements.append('<line x1="320" y1="290" x2="320" y2="350" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<line x1="305" y1="350" x2="335" y2="350" stroke="#1a1a1a" stroke-width="3"/>')   # +
    r.elements.append('<line x1="295" y1="362" x2="345" y2="362" stroke="#1a1a1a" stroke-width="3"/>')   # -
    r.elements.append('<line x1="320" y1="362" x2="320" y2="400" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="350" y="350" class="value" font-size="9">100µF / 10V</text>')
    # 100nF
    r.elements.append('<circle cx="380" cy="290" r="3" fill="#0066CC"/>')
    r.elements.append('<line x1="380" y1="290" x2="380" y2="350" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<line x1="368" y1="350" x2="392" y2="350" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="368" y1="358" x2="392" y2="358" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="380" y1="358" x2="380" y2="400" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="408" y="356" class="value" font-size="9">100nF</text>')
    # GND rail
    r.elements.append('<line x1="280" y1="400" x2="500" y2="400" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="380" y1="400" x2="380" y2="412" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<line x1="370" y1="412" x2="390" y2="412" stroke="#1a1a1a" stroke-width="2.5"/>')
    r.elements.append('<line x1="374" y1="416" x2="386" y2="416" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<line x1="378" y1="420" x2="382" y2="420" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="510" y="403" class="value" font-size="9">GND</text>')
    # Output
    r.elements.append('<line x1="430" y1="290" x2="600" y2="290" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="610" y="294" class="label" font-size="10" fill="#6600CC">→ Pico VSYS</text>')

    # Notes
    r.elements.append('<rect x="40" y="450" width="820" height="70" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append('<text x="450" y="470" class="label" text-anchor="middle" fill="#E65100" font-size="11">Notes</text>')
    notes = [
        "• If shop has no 1N5817: substitute 1N4001-1N4007 (0.7V drop, still safe — Pico VSYS spec is 1.8–5.5V).",
        "• Optional armor (defer to v2): PPTC 500 mA polyfuse, SMAJ5.0A TVS clamp, ferrite bead 100Ω@100MHz.",
        "• Mount on a 2×3cm sub-board behind the Pico — same board can carry I²C0 pull-ups (2.2kΩ) and UART/I²C ferrite beads.",
    ]
    for i, line in enumerate(notes):
        r.elements.append(f'<text x="55" y="{490 + i*15}" class="value" font-size="9">{line}</text>')

    return r.render()


# ─── Mod catalog schematics (M01–M14) ─────────────────────────────────────
#
# Each mod_mNN_* generator produces a single-page schematic figure
# documenting one Phase 1 / Phase 2 mod from docs/mods/macrobrute_mod_catalog.md.
# The simple mods (M01, M05–M07, M09–M11, M13–M14) get compact wiring sketches.
# The complex mods (M02, M04, M08, M12) get full schematics with IC pinout
# detail and (separately) stripboard layouts in tools/generate_layouts.py.

def _mod_header(r, body_lines, parts_label="Parts"):
    """Common footer block — parts list + mod-id badge."""
    y = 510
    r.elements.append(f'<rect x="40" y="{y}" width="800" height="80" fill="#F5F5F5" stroke="#666" stroke-width="0.5" rx="4"/>')
    r.elements.append(f'<text x="55" y="{y+18}" class="label" font-size="11" fill="#333">{parts_label}</text>')
    for i, line in enumerate(body_lines):
        r.elements.append(f'<text x="55" y="{y+38 + i*15}" class="value" font-size="9">{line}</text>')


def _draw_jack(r, x, y, label, color="#1a1a1a"):
    r.elements.append(f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{color}" stroke-width="2"/>')
    r.elements.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')
    r.elements.append(f'<text x="{x}" y="{y-22}" class="label" text-anchor="middle" font-size="10">{label}</text>')


def _draw_resistor(r, x, y, value, horizontal=True):
    if horizontal:
        r.elements.append(f'<rect x="{x-15}" y="{y-6}" width="30" height="12" fill="#FFFBE6" stroke="#999" rx="1"/>')
        r.elements.append(f'<text x="{x}" y="{y+3}" class="value" text-anchor="middle" font-size="8">{value}</text>')
    else:
        r.elements.append(f'<rect x="{x-6}" y="{y-15}" width="12" height="30" fill="#FFFBE6" stroke="#999" rx="1"/>')
        r.elements.append(f'<text x="{x+12}" y="{y+3}" class="value" font-size="8">{value}</text>')


def _draw_switch(r, x, y, kind="SPDT", label=""):
    """SPDT or SPST toggle symbol."""
    r.elements.append(f'<circle cx="{x-15}" cy="{y}" r="3" fill="#1a1a1a"/>')
    r.elements.append(f'<circle cx="{x+15}" cy="{y-8}" r="3" fill="#1a1a1a"/>')
    r.elements.append(f'<line x1="{x-15}" y1="{y}" x2="{x+12}" y2="{y-8}" stroke="#1a1a1a" stroke-width="1.5"/>')
    if kind == "SPDT":
        r.elements.append(f'<circle cx="{x+15}" cy="{y+8}" r="3" fill="#1a1a1a"/>')
    if label:
        r.elements.append(f'<text x="{x}" y="{y+22}" class="value" text-anchor="middle" font-size="8">{label}</text>')


def _draw_ic(r, x, y, w, h, name, pins_left, pins_right, color="#2a2a2a"):
    """Draw a DIP IC body with pin labels."""
    r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="3"/>')
    r.elements.append(f'<circle cx="{x+8}" cy="{y+8}" r="3" fill="gold"/>')
    r.elements.append(f'<text x="{x+w/2}" y="{y+h/2}" class="label" text-anchor="middle" fill="#FFF" font-size="11">{name}</text>')
    pin_count = max(len(pins_left), len(pins_right))
    pitch = (h - 20) / max(1, pin_count - 1) if pin_count > 1 else 0
    for i, pl in enumerate(pins_left):
        py = y + 14 + i * pitch
        r.elements.append(f'<circle cx="{x-4}" cy="{py}" r="2.5" fill="gold"/>')
        r.elements.append(f'<text x="{x-8}" y="{py+3}" class="value" text-anchor="end" font-size="8">{pl}</text>')
    for i, pr in enumerate(pins_right):
        py = y + 14 + i * pitch
        r.elements.append(f'<circle cx="{x+w+4}" cy="{py}" r="2.5" fill="gold"/>')
        r.elements.append(f'<text x="{x+w+8}" y="{py+3}" class="value" font-size="8">{pr}</text>')


# ── M01 — Triangle gain ×2 ──────────────────────────────────────────────────
def generate_mod_m01_triangle_gain() -> str:
    r = SchematicRenderer(900, 620, "M01 — Triangle Output Gain ×2",
                          "Restore level parity with saw/square (TL074 D follower in breakout PCB)")
    r.elements.append('<text x="80" y="120" class="label" font-size="11">TP124 (triangle, ~5 Vpp)</text>')
    r.elements.append('<line x1="80" y1="140" x2="240" y2="140" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.opamp(Point(280, 140), label="TL074 D", pins=("+", "-", "out"), show_power=False)
    # Feedback network
    r.elements.append('<line x1="310" y1="140" x2="380" y2="140" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="380" y1="140" x2="380" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="380" y1="200" x2="200" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 290, 200, "33k Rf (was 16k)", horizontal=True)
    r.elements.append('<line x1="200" y1="200" x2="200" y2="160" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Ground leg
    r.elements.append('<line x1="200" y1="200" x2="200" y2="260" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 200, 260, "16k Rg", horizontal=False)
    r.elements.append('<line x1="200" y1="290" x2="200" y2="320" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.ground(Point(200, 320))
    # Output
    r.elements.append('<line x1="380" y1="140" x2="540" y2="140" stroke="#1a1a1a" stroke-width="2"/>')
    _draw_jack(r, 580, 140, "DB-9 A:7 (triangle out)")
    r.elements.append('<text x="450" y="130" class="anno" text-anchor="middle" font-size="9">A = 1 + Rf/Rg ≈ 2.06×</text>')
    _mod_header(r, [
        "• 1× 33 kΩ resistor (replaces existing 16 kΩ feedback R)",
        "• Effect: triangle level matches saw/square at the DB-9 A jack (within ±1 dB)",
        "• Single-component swap — no PCB cuts, no panel work",
    ])
    return r.render()


# ── M02 — Active soft sync ──────────────────────────────────────────────────
def generate_mod_m02_soft_sync() -> str:
    r = SchematicRenderer(900, 620, "M02 — Active Soft Sync (LM393)",
                          "Working soft sync — replaces the broken stock circuit. Toggle between hard / soft.")
    # Sync input jack
    _draw_jack(r, 80, 200, "SYNC IN")
    r.elements.append('<line x1="100" y1="200" x2="180" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    # SPDT toggle (mode select)
    _draw_switch(r, 200, 200, "SPDT", "Hard / Soft")
    r.elements.append('<text x="200" y="170" class="label" text-anchor="middle" font-size="9">M02 toggle</text>')
    # Hard path (top): direct
    r.elements.append('<line x1="215" y1="192" x2="640" y2="100" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="430" y="110" class="anno" font-size="9">A: hard sync (stock direct)</text>')
    # Soft path (bottom): through LM393
    r.elements.append('<line x1="215" y1="208" x2="280" y2="280" stroke="#1a1a1a" stroke-width="1.5"/>')
    # LM393 body
    _draw_ic(r, 280, 240, 150, 90, "LM393", ["IN+", "IN-", "GND"], ["OUT", "+5V", ""])
    # Threshold divider
    _draw_resistor(r, 240, 320, "100k", True)
    _draw_resistor(r, 240, 360, "100k", True)
    r.elements.append('<line x1="220" y1="340" x2="280" y2="270" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="200" y="395" class="value" text-anchor="middle" font-size="8">mid-rail bias</text>')
    # Hysteresis feedback (output → +input)
    r.elements.append('<line x1="430" y1="252" x2="500" y2="252" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="500" y1="252" x2="500" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="500" y1="220" x2="260" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="260" y1="220" x2="260" y2="252" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="260" y1="252" x2="280" y2="252" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 380, 220, "10k hyst", True)
    # Diode
    r.elements.append('<polygon points="450,210 450,230 470,220" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="460" y="200" class="value" font-size="8">1N4148</text>')
    # Pull-up
    _draw_resistor(r, 460, 270, "10k", False)
    r.elements.append('<text x="490" y="252" class="value" font-size="8">+5V</text>')
    # Output to VCO sync
    r.elements.append('<line x1="430" y1="252" x2="640" y2="252" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="640" y1="100" x2="640" y2="252" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="650" y="180" class="label" font-size="10">→ VCO sync node</text>')
    _mod_header(r, [
        "• LM393 dual comparator, 2× 100 kΩ (threshold divider), 1× 10 kΩ (hysteresis), 1× 1N4148, 1× SPDT",
        "• Hard mode (A): sync jack → VCO sync directly (stock behaviour).",
        "• Soft mode (B): comparator + hysteresis produces phase-resync edges that re-time the VCO without forcing it.",
        "• Bench-test on breadboard before final install. Stripboard layout: schematics/mod_m02_soft_sync_stripboard.svg",
    ])
    return r.render()


# ── M03 — Sine extraction + buffer ─────────────────────────────────────────
def generate_mod_m03_sine_extract() -> str:
    r = SchematicRenderer(900, 580, "M03 — Sine Extraction + Buffer",
                          "Tap the triangle wave-shaper, buffer with TL074 spare section, output to new panel jack")
    r.elements.append('<text x="60" y="120" class="label" font-size="11">Triangle shaper output</text>')
    r.elements.append('<text x="60" y="135" class="value" font-size="9">(post diode-clipper, quasi-sine ~3 Vpp)</text>')
    r.elements.append('<line x1="60" y1="180" x2="220" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # DC block cap
    r.elements.append('<line x1="220" y1="170" x2="220" y2="190" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="232" y1="170" x2="232" y2="190" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<text x="226" y="160" class="value" text-anchor="middle" font-size="8">1µF</text>')
    r.elements.append('<line x1="232" y1="180" x2="280" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Series R
    _draw_resistor(r, 310, 180, "10k", True)
    r.elements.append('<line x1="325" y1="180" x2="380" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # TL074 spare follower
    r.opamp(Point(420, 180), label="TL074 (spare)", pins=("+", "-", "out"), show_power=False)
    # Feedback (unity gain)
    r.elements.append('<line x1="450" y1="180" x2="500" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="500" y1="180" x2="500" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="500" y1="220" x2="380" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="380" y1="220" x2="380" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Output
    r.elements.append('<line x1="500" y1="180" x2="600" y2="180" stroke="#1a1a1a" stroke-width="2"/>')
    _draw_jack(r, 640, 180, "SINE OUT (panel)")
    r.elements.append('<text x="510" y="170" class="anno" font-size="9">~10 Vpp Eurorack</text>')
    _mod_header(r, [
        "• 1× TL074 spare section (already on the breakout — re-uses I6 spare op-amp slot)",
        "• 2× 10 kΩ (input + feedback), 1× 1 µF (DC-block), 1× 6 mm panel jack",
        "• Tap point is high-impedance — no PCB cuts, doesn't load the stock signal path",
        "• Adds a clean sine output to the MicroBrute's waveform palette",
    ])
    return r.render()


# ── M04 — Metalizer CV depth (LM13700 OTA) ─────────────────────────────────
def generate_mod_m04_metalizer_vca() -> str:
    r = SchematicRenderer(960, 620, "M04 — Metalizer CV Depth (LM13700 OTA)",
                          "VCA in the Metalizer feedback loop — turns the wavefolder into a dynamic effect")
    # Metalizer feedback TAP (entry)
    r.elements.append('<text x="60" y="120" class="label" font-size="11">Metalizer feedback (cut here)</text>')
    r.elements.append('<line x1="60" y1="180" x2="220" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="140" y="172" class="anno" text-anchor="middle" font-size="9">existing trace cut</text>')
    # OTA body
    _draw_ic(r, 240, 160, 160, 120, "LM13700",
             ["IN+", "IN-", "Iabc", "V-"],
             ["OUT", "Diode B", "Buf", "V+"])
    # CV input network
    r.elements.append('<line x1="100" y1="350" x2="220" y2="350" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_jack(r, 80, 350, "CV IN")
    _draw_resistor(r, 180, 350, "100k", True)
    r.elements.append('<line x1="195" y1="350" x2="280" y2="350" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="280" y1="350" x2="280" y2="225" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Amount pot
    r.potentiometer(Point(360, 380), label="Amount", value="100k")
    r.elements.append('<line x1="370" y1="380" x2="370" y2="225" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Power decoupling
    r.elements.append('<text x="420" y="295" class="value" font-size="8">+12V (V+)</text>')
    r.elements.append('<text x="420" y="245" class="value" font-size="8">-12V (V-)</text>')
    # Output back to feedback path
    r.elements.append('<line x1="404" y1="180" x2="640" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="650" y="184" class="label" font-size="10">→ Metalizer fb (rejoin)</text>')
    _mod_header(r, [
        "• LM13700 (1 OTA section), 1× 100 kΩ CV input R, 1× 10 kΩ control R, 1× 100 kΩ pot, 1× 6 mm CV jack, 4× 0.1 µF decouple",
        "• Cut Metalizer feedback trace at the wavefolder output node; re-route through the OTA's signal input",
        "• CV (0–5 V) modulates Iabc — high CV = full feedback (intense fold), low CV = muted",
        "• Amount pot sets manual offset / minimum-fold floor when CV is at 0V",
        "• Most invasive of the Phase 2 mods — install LAST in build sequence",
    ])
    return r.render()


# ── M05 — Filter self-oscillation kill switch ────────────────────────────
def generate_mod_m05_filter_selfosc_kill() -> str:
    r = SchematicRenderer(900, 540, "M05 — Filter Self-Oscillation Kill Switch",
                          "SPST breaks the Steiner-Parker filter feedback at high resonance")
    r.elements.append('<text x="60" y="130" class="label" font-size="11">Steiner-Parker filter</text>')
    r.elements.append('<rect x="60" y="150" width="160" height="80" fill="#F0F0F5" stroke="#666" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="140" y="195" class="value" text-anchor="middle" font-size="10">Stock filter core</text>')
    # Feedback path tap
    r.elements.append('<line x1="220" y1="190" x2="320" y2="190" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="245" y="180" class="anno" font-size="9">resonance fb</text>')
    # 10k limit + SPST
    _draw_resistor(r, 350, 190, "10k", True)
    r.elements.append('<line x1="365" y1="190" x2="420" y2="190" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_switch(r, 440, 190, "SPST", "Kill")
    r.elements.append('<line x1="460" y1="182" x2="540" y2="182" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="540" y1="182" x2="540" y2="270" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="540" y1="270" x2="140" y2="270" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="140" y1="270" x2="140" y2="230" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="340" y="290" class="anno" text-anchor="middle" font-size="9">closed = stock self-osc · open = clean percussive</text>')
    _mod_header(r, [
        "• 1× SPST mini-toggle, 1× 10 kΩ resistor (current limit during switching)",
        "• Wired in series with the existing resonance feedback path — no PCB cuts",
        "• Closed: filter can self-oscillate at high Q (stock behaviour)",
        "• Open: resonance peak only, no oscillation — clean percussive plucks",
    ])
    return r.render()


# ── M06 — PWM CV input ─────────────────────────────────────────────────────
def generate_mod_m06_pwm_cv() -> str:
    r = SchematicRenderer(900, 540, "M06 — PWM CV Input",
                          "Direct CV injection to PWM summing node (R289)")
    _draw_jack(r, 100, 200, "PWM CV IN")
    r.elements.append('<line x1="120" y1="200" x2="240" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 270, 200, "39k", True)
    r.elements.append('<line x1="285" y1="200" x2="380" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="390" y="195" class="label" font-size="10">→ R289 junction</text>')
    r.elements.append('<text x="390" y="210" class="value" font-size="9">PWM summing node, front board</text>')
    r.elements.append('<rect x="240" y="250" width="450" height="70" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append('<text x="465" y="270" class="label" text-anchor="middle" font-size="11" fill="#E65100">Safety</text>')
    r.elements.append('<text x="260" y="290" class="value" font-size="9">39 kΩ + LPC2361 DAC node internal Z → max ±0.13 mA at ±5 V CV</text>')
    r.elements.append('<text x="260" y="304" class="value" font-size="9">Well below DAC node spec — no clamping diodes required.</text>')
    _mod_header(r, [
        "• 1× 39 kΩ series resistor, 1× 6 mm Thonkiconn jack",
        "• Tap point: R289 junction on the front board (PWM summing node)",
        "• 0V CV = stock PWM (knob position), CV swings shift pulse width",
        "• Pairs with M09 (PWM self-mod normalled jack) — sharing the same panel jack",
    ])
    return r.render()


# ── M07 — Pitch CV starve toggle ───────────────────────────────────────────
def generate_mod_m07_pitch_starve() -> str:
    r = SchematicRenderer(900, 540, "M07 — Pitch CV Starve Toggle",
                          "SPDT introduces a current draw on the VCO pitch CV — drifty/glitchy pitch")
    r.elements.append('<text x="60" y="130" class="label" font-size="11">VCO pitch CV summing node</text>')
    r.elements.append('<rect x="60" y="150" width="160" height="60" fill="#F0F0F5" stroke="#666" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="140" y="185" class="value" text-anchor="middle" font-size="10">Pitch summing</text>')
    r.elements.append('<line x1="220" y1="180" x2="320" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_switch(r, 340, 180, "SPDT", "Stable / Starve")
    r.elements.append('<line x1="355" y1="172" x2="420" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="430" y="176" class="value" font-size="9">A: stock (open)</text>')
    r.elements.append('<line x1="355" y1="188" x2="420" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 460, 240, "470Ω", True)
    r.elements.append('<line x1="475" y1="240" x2="540" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.ground(Point(540, 240))
    r.elements.append('<text x="540" y="270" class="value" font-size="9">B: starved (current sink)</text>')
    _mod_header(r, [
        "• 1× SPDT mini-toggle, 1× 470 Ω resistor",
        "• Position A: open — stock pitch CV behaviour",
        "• Position B: 470 Ω + LPC2361 DAC source impedance limits current to a few mA",
        "• Result: pitch slowly drifts low / becomes unstable while toggle is in B",
    ])
    return r.render()


# ── M08 — Sub-harmonic divider (74HC74) ────────────────────────────────────
def generate_mod_m08_subharmonic() -> str:
    r = SchematicRenderer(960, 620, "M08 — Sub-harmonic Divider (74HC74)",
                          "Square out → Schmitt buffer → /2 flip-flop → mix back into audio path")
    # Square in
    r.elements.append('<text x="60" y="120" class="label" font-size="11">Square out tap (TP93)</text>')
    r.elements.append('<line x1="60" y1="180" x2="180" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Schmitt buffer (CD40106 spare)
    r.elements.append('<polygon points="180,170 180,190 210,180" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<circle cx="214" cy="180" r="3" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="195" y="160" class="value" text-anchor="middle" font-size="8">CD40106 (spare)</text>')
    r.elements.append('<line x1="217" y1="180" x2="280" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # 74HC74 D-flip-flop
    _draw_ic(r, 280, 130, 150, 100, "74HC74",
             ["D", "CLK", "RST", "GND"],
             ["Q", "Q̄", "+5V", "PRE"])
    # D = Q̄ feedback
    r.elements.append('<line x1="434" y1="160" x2="480" y2="160" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="480" y1="160" x2="480" y2="100" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="480" y1="100" x2="240" y2="100" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="240" y1="100" x2="240" y2="144" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="240" y1="144" x2="280" y2="144" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="360" y="92" class="anno" text-anchor="middle" font-size="9">D ← Q̄ (toggles on every clock — /2 division)</text>')
    # Q output → mix
    r.elements.append('<line x1="434" y1="144" x2="500" y2="144" stroke="#1a1a1a" stroke-width="1.5"/>')
    # AC coupling
    r.elements.append('<line x1="500" y1="134" x2="500" y2="154" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="512" y1="134" x2="512" y2="154" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<text x="506" y="125" class="value" text-anchor="middle" font-size="8">1µF</text>')
    r.elements.append('<line x1="512" y1="144" x2="560" y2="144" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Mix pot
    r.potentiometer(Point(610, 144), label="Mix", value="10k")
    r.elements.append('<line x1="640" y1="144" x2="720" y2="144" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="730" y="148" class="label" font-size="10">→ pre-VCF mixer</text>')
    # Enable toggle
    _draw_switch(r, 590, 320, "SPDT", "Sub Enable")
    r.elements.append('<line x1="575" y1="320" x2="500" y2="320" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="490" y="324" class="value" text-anchor="end" font-size="9">SPDT in series with mix tap</text>')
    _mod_header(r, [
        "• 1× 74HC74 dual D-flip-flop, 1× 10 kΩ mix pot, 1× SPDT enable, 4× 0.1 µF decouple, 1× 1 µF AC-couple",
        "• Schmitt buffer reuses a spare CD40106 gate (already on the breakout)",
        "• Generates a square wave one octave below the source — gritty bass enhancement",
        "• Pair with T6 (gate feedback touch bolt) for big metallic textures",
        "• Stripboard: schematics/mod_m08_subharmonic_stripboard.svg",
    ])
    return r.render()


# ── M09 — PWM self-mod normalled jack ──────────────────────────────────────
def generate_mod_m09_pwm_selfmod() -> str:
    r = SchematicRenderer(900, 540, "M09 — PWM Self-Modulation (normalled jack)",
                          "Saw out → 100kΩ → PWM CV (default). Plug a cable to break the loop.")
    r.elements.append('<text x="60" y="130" class="label" font-size="11">Saw output (TP94 area)</text>')
    r.elements.append('<line x1="60" y1="180" x2="200" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 230, 180, "100k", True)
    r.elements.append('<line x1="245" y1="180" x2="320" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Switching jack
    r.elements.append('<rect x="320" y="160" width="120" height="40" fill="none" stroke="#1a1a1a" stroke-width="2" rx="3"/>')
    r.elements.append('<text x="380" y="155" class="label" text-anchor="middle" font-size="10">Switching jack</text>')
    r.elements.append('<text x="380" y="195" class="value" text-anchor="middle" font-size="9">tip · normal · sleeve</text>')
    r.elements.append('<text x="380" y="218" class="value" text-anchor="middle" font-size="8">(M06 panel jack body — re-used)</text>')
    # When unplugged: tip ↔ normal connected internally
    r.elements.append('<line x1="440" y1="180" x2="560" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="570" y="184" class="label" font-size="10">→ M06 PWM CV node</text>')
    r.elements.append('<rect x="40" y="240" width="820" height="60" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append('<text x="450" y="262" class="label" text-anchor="middle" font-size="11" fill="#E65100">How it behaves</text>')
    r.elements.append('<text x="60" y="282" class="value" font-size="9">No cable plugged: the saw self-modulates the PWM via 100 kΩ → metallic FM-ish PWM textures by default.</text>')
    r.elements.append('<text x="60" y="296" class="value" font-size="9">Cable plugged into M06 jack: the switch breaks the saw → normal contact, lets external CV take over.</text>')
    _mod_header(r, [
        "• 1× 6 mm switching (normalled) Thonkiconn jack — replaces the plain jack from M06",
        "• 1× 100 kΩ series resistor (saw → normal contact)",
        "• Cooperates with M06: same panel hole, two behaviours depending on plug state",
    ])
    return r.render()


# ── M10 — Brute Factor extreme toggle ──────────────────────────────────────
def generate_mod_m10_brute_extreme() -> str:
    r = SchematicRenderer(900, 540, "M10 — Brute Factor Extreme Toggle",
                          "SPDT bypasses the internal limit R on the Brute Factor feedback path")
    r.elements.append('<text x="60" y="130" class="label" font-size="11">Brute Factor feedback loop</text>')
    r.elements.append('<rect x="60" y="150" width="160" height="60" fill="#F0F0F5" stroke="#666" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="140" y="185" class="value" text-anchor="middle" font-size="10">BF feedback amp</text>')
    r.elements.append('<line x1="220" y1="180" x2="280" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Stock limit R
    _draw_resistor(r, 320, 180, "Rlim", True)
    r.elements.append('<line x1="335" y1="180" x2="420" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # SPDT
    _draw_switch(r, 450, 180, "SPDT", "Tame / Extreme")
    r.elements.append('<line x1="465" y1="172" x2="540" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="550" y="176" class="value" font-size="9">B: stock (Rlim in circuit)</text>')
    # Bypass path
    r.elements.append('<line x1="465" y1="188" x2="510" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 540, 220, "1k safety", True)
    r.elements.append('<line x1="555" y1="220" x2="610" y2="220" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="610" y1="220" x2="610" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="660" y="220" class="value" font-size="9">A: extreme (Rlim shorted)</text>')
    r.elements.append('<line x1="610" y1="172" x2="700" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="710" y="176" class="label" font-size="10">→ feedback path</text>')
    _mod_header(r, [
        "• 1× SPDT mini-toggle, 1× 1 kΩ inline (safety limiter for switching transients)",
        "• Position B: stock — Rlim in circuit, normal Brute Factor feedback",
        "• Position A: extreme — Rlim bypassed, feedback can self-oscillate / explode",
        "• Output level can spike. Panel-mark the 'extreme' position prominently.",
    ])
    return r.render()


# ── M11 — 9th touch bolt: envelope retrigger ───────────────────────────────
def generate_mod_m11_touch_envretrig() -> str:
    r = SchematicRenderer(900, 540, "M11 — 9th Touch Bolt: Envelope Retrigger",
                          "Body contact injects a brief gate pulse — rhythmic glitch via touch")
    # Brass bolt symbol
    r.elements.append('<rect x="60" y="170" width="40" height="20" fill="#B87333" stroke="#8B4513" stroke-width="1.5" rx="2"/>')
    r.elements.append('<text x="80" y="160" class="label" text-anchor="middle" font-size="10">M3 brass bolt</text>')
    r.elements.append('<text x="80" y="205" class="value" text-anchor="middle" font-size="8">body contact</text>')
    r.elements.append('<line x1="100" y1="180" x2="160" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Series R
    _draw_resistor(r, 190, 180, "100k", True)
    r.elements.append('<line x1="205" y1="180" x2="260" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Diode
    r.elements.append('<polygon points="260,170 260,190 280,180" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="280" y1="170" x2="280" y2="190" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="270" y="155" class="value" font-size="8">1N4148</text>')
    r.elements.append('<line x1="280" y1="180" x2="340" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Pulse-shaping cap
    r.elements.append('<line x1="340" y1="170" x2="340" y2="190" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="352" y1="170" x2="352" y2="190" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<text x="346" y="160" class="value" text-anchor="middle" font-size="8">100nF</text>')
    r.elements.append('<line x1="352" y1="180" x2="440" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="450" y="184" class="label" font-size="10">→ Gate node (env trig)</text>')
    _mod_header(r, [
        "• 1× M3 brass bolt + nut (matches the existing 8 touch bolts)",
        "• 1× 100 kΩ + 1× 1N4148 + 1× 100 nF — the diode prevents back-feed, the cap shapes the touch into a short pulse",
        "• Touching the bolt produces a brief gate edge → envelope retriggers",
        "• Body capacitance can't latch the gate high — falls back to inactive after the cap charges",
    ])
    return r.render()


# ── M12 — ARG (audio-rate gate) ────────────────────────────────────────────
def generate_mod_m12_arg() -> str:
    r = SchematicRenderer(960, 620, "M12 — ARG (Audio-Rate Gate)",
                          "Audio in → LM393 comparator → gate at zero-crossings")
    _draw_jack(r, 80, 200, "AUDIO IN")
    # DC block
    r.elements.append('<line x1="100" y1="200" x2="180" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="180" y1="190" x2="180" y2="210" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="192" y1="190" x2="192" y2="210" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<text x="186" y="180" class="value" text-anchor="middle" font-size="8">100nF</text>')
    r.elements.append('<line x1="192" y1="200" x2="260" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    # LM393
    _draw_ic(r, 280, 160, 150, 90, "LM393", ["IN+", "IN-", "GND"], ["OUT", "+5V", ""])
    r.elements.append('<line x1="260" y1="200" x2="280" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Threshold pot biases IN-
    r.potentiometer(Point(220, 320), label="Threshold", value="100k")
    r.elements.append('<line x1="220" y1="290" x2="220" y2="200" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="220" y1="200" x2="280" y2="208" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Pull-up
    _draw_resistor(r, 460, 250, "10k", False)
    r.elements.append('<text x="490" y="208" class="value" font-size="8">+5V pull-up</text>')
    # Output → gate
    r.elements.append('<line x1="430" y1="180" x2="640" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="650" y="184" class="label" font-size="10">→ Gate input (env / aux out)</text>')
    _mod_header(r, [
        "• 1× LM393 dual comparator, 1× 100 kΩ threshold pot, 1× 10 kΩ pull-up to +5 V, 1× 100 nF DC-block, 1× 6 mm jack",
        "• Audio crosses the threshold → comparator output snaps low → gate edge",
        "• LM393's natural ~few-mV hysteresis gives clean edges; tune threshold pot to reject quiet content",
        "• Use case: trigger envelope from kick drum, vocal, anything",
        "• Stripboard: schematics/mod_m12_arg_stripboard.svg",
    ])
    return r.render()


# ── M13 — VCO sync to envelope toggle ──────────────────────────────────────
def generate_mod_m13_vco_sync_env() -> str:
    r = SchematicRenderer(900, 540, "M13 — VCO Sync to Envelope (toggle)",
                          "SPDT routes envelope decay edge to the VCO sync input")
    r.elements.append('<text x="60" y="130" class="label" font-size="11">External sync jack</text>')
    r.elements.append('<line x1="60" y1="180" x2="200" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_switch(r, 230, 180, "SPDT", "Ext / Env")
    # Position A: external (top) — straight through to VCO sync
    r.elements.append('<line x1="245" y1="172" x2="640" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="430" y="164" class="anno" text-anchor="middle" font-size="9">A: external sync (stock)</text>')
    # Position B: envelope decay → high-pass edge shaper → VCO sync
    r.elements.append('<line x1="245" y1="188" x2="320" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="320" y1="240" x2="380" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Edge shaper: 100n + 10k high-pass
    r.elements.append('<line x1="380" y1="230" x2="380" y2="250" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<line x1="392" y1="230" x2="392" y2="250" stroke="#1a1a1a" stroke-width="3"/>')
    r.elements.append('<text x="386" y="220" class="value" text-anchor="middle" font-size="8">100nF</text>')
    r.elements.append('<line x1="392" y1="240" x2="440" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 470, 240, "10k", True)
    r.elements.append('<line x1="485" y1="240" x2="540" y2="240" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="540" y1="240" x2="540" y2="172" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<text x="290" y="270" class="anno" font-size="9">B: env decay → HPF edge → VCO sync</text>')
    r.elements.append('<text x="650" y="176" class="label" font-size="10">→ VCO sync</text>')
    _mod_header(r, [
        "• 1× SPDT mini-toggle, 1× 100 nF + 1× 10 kΩ (edge-shaper)",
        "• Position A: external sync jack feeds VCO sync (stock)",
        "• Position B: envelope decay → high-pass → produces a sync edge on each note end",
        "• Replicates a classic patch (env → VCO sync) without using a cable",
    ])
    return r.render()


# ── M14 — Safe VCO bias starve ─────────────────────────────────────────────
def generate_mod_m14_vco_bias_starve() -> str:
    r = SchematicRenderer(900, 580, "M14 — Safe VCO Bias Starve (NOT supply rail)",
                          "Body contact loads the VCO pitch-bias node — detune via touch, no risk to LPC2361")
    # Brass bolt
    r.elements.append('<rect x="60" y="170" width="40" height="20" fill="#B87333" stroke="#8B4513" stroke-width="1.5" rx="2"/>')
    r.elements.append('<text x="80" y="160" class="label" text-anchor="middle" font-size="10">M3 brass bolt</text>')
    r.elements.append('<line x1="100" y1="180" x2="160" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    _draw_resistor(r, 190, 180, "22k", True)
    r.elements.append('<line x1="205" y1="180" x2="260" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Diode (anti-backflow)
    r.elements.append('<polygon points="260,170 260,190 280,180" fill="none" stroke="#1a1a1a" stroke-width="1.5"/>')
    r.elements.append('<line x1="280" y1="170" x2="280" y2="190" stroke="#1a1a1a" stroke-width="2"/>')
    r.elements.append('<text x="270" y="155" class="value" font-size="8">1N4148</text>')
    r.elements.append('<line x1="280" y1="180" x2="380" y2="180" stroke="#1a1a1a" stroke-width="1.5"/>')
    # Bias node label
    r.elements.append('<rect x="380" y="160" width="220" height="50" fill="#F0F0F5" stroke="#666" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="490" y="183" class="value" text-anchor="middle" font-size="10">VCO pitch-bias node</text>')
    r.elements.append('<text x="490" y="200" class="value" text-anchor="middle" font-size="9">(high-Z point in temperature-comp network)</text>')
    # Big safety callout
    r.elements.append('<rect x="40" y="260" width="800" height="180" fill="#FFF0F0" stroke="#D44" stroke-width="1.5" rx="4"/>')
    r.elements.append('<text x="450" y="285" class="label" text-anchor="middle" font-size="12" fill="#D44">⚠ SAFETY — read before building</text>')
    safety = [
        "• This mod taps the VCO pitch-BIAS node, NOT the +12V supply rail.",
        "• 22 kΩ + body resistance + 1N4148 caps current at ~0.5 mA on a +12V node — safe for the analog network.",
        "• The LPC2361 DAC and shared +12V/-12V supply rails are NOT touched.",
        "• Worst case if you press-and-hold: pitch drifts low, oscillator slows or briefly stops.",
        "• DO NOT tap the +12V rail directly — that variant was explicitly rejected (risks cooking the LPC2361 DAC).",
    ]
    for i, line in enumerate(safety):
        r.elements.append(f'<text x="60" y="{310 + i*22}" class="value" font-size="10" fill="#D44">{line}</text>')
    _mod_header(r, [
        "• 1× M3 brass bolt + nut, 1× 22 kΩ series R, 1× 1N4148 diode",
        "• Tap point: VCO pitch-bias node (high-Z, in temperature-compensation network)",
        "• Touching the bolt pulls the bias slightly low — oscillator detunes downward / breaks up",
        "• Could double as a 10th touch bolt position alongside M11",
    ])
    return r.render()


# ─── Phase 0 Bench Validation Wiring ────────────────────────────────
# Two views of the same circuit:
#   1. phase0_wiring_schematic.svg — flat schematic, power-rail style
#   2. phase0_breadboard.svg       — top-down breadboard layout
#
# Pin map (must match firmware/pico/config.py — keep in sync):
#   0.96" SSD1306 OLED (I²C0 @ 0x3C):  VCC=+3V3, GND, SDA=GP4, SCL=GP5
#   KY-040 rotary encoder:             SW=GP13, CLK=GP14, DT=GP15
#                                      (firmware enables Pin.PULL_UP on all 3)
#                                      +=+3V3, GND
#   Tap button (SPST momentary):       A=GP12 (firmware Pin.PULL_UP), B=GND
#   RGB LED (common cathode):          R=GP8, G=GP9, B=GP10 (each via 220Ω) → K=GND
#   Clock OUT (3.5mm TS tip):          GP22 → 1kΩ
#   Clock IN  (3.5mm TS tip):          GP21 ← 1kΩ  (Pin.PULL_DOWN, IRQ rising)
#                                      Both jack sleeves → GND
#
# Routing rules (avoid the visual mess we hit on the first pass):
#   • +3V3 rail at the top of the canvas, GND rail at the bottom
#   • Pico signal pins are placed at Y values that EXACTLY match the
#     corresponding peripheral pin Y values — so each signal wire is
#     a single straight horizontal line, never an elbow
#   • Power/GND verticals each get their own unique X coordinate so
#     they never share segments and never look like a bus
#   • Inline 220Ω and 1kΩ resistor symbols are drawn explicitly on
#     their wires so the circuit reads correctly without legend
#   • Peripheral bodies are rendered as proper schematic symbols
#     (switch contacts, LED with separate anodes, jack with sleeve)


def generate_phase0_wiring_schematic() -> str:
    """Phase 0 bench-validation wiring — flat schematic, power-rail style."""
    r = SchematicRenderer(
        1300, 830,
        "Phase 0 — Pico Bench Validation Schematic",
        '0.96" main OLED + 0.91" strip OLED + KY-040 encoder + tap button + '
        "RGB LED + clock I/O · shared I²C0 bus, every pin Y aligned",
    )

    # Net colours (one per logical net)
    C_3V3 = "#D44"
    C_GND = "#333"
    C_I2C = "#2196F3"
    C_GPIO = "#4CAF50"
    C_LED = "#FF9800"
    C_CLK = "#9C27B0"

    RAIL_3V3_Y = 60
    RAIL_GND_Y = 740
    RAIL_X_LEFT = 70
    RAIL_X_RIGHT = 1240

    # ─── Power rails ────────────────────────────────────────────
    r.elements.append(
        f'<line x1="{RAIL_X_LEFT}" y1="{RAIL_3V3_Y}" '
        f'x2="{RAIL_X_RIGHT}" y2="{RAIL_3V3_Y}" '
        f'stroke="{C_3V3}" stroke-width="3"/>'
    )
    r.elements.append(
        f'<text x="{RAIL_X_LEFT - 8}" y="{RAIL_3V3_Y + 4}" class="label" '
        f'fill="{C_3V3}" font-size="11" text-anchor="end">+3V3</text>'
    )
    r.elements.append(
        f'<text x="{RAIL_X_RIGHT + 8}" y="{RAIL_3V3_Y + 4}" class="label" '
        f'fill="{C_3V3}" font-size="11">+3V3</text>'
    )
    r.elements.append(
        f'<line x1="{RAIL_X_LEFT}" y1="{RAIL_GND_Y}" '
        f'x2="{RAIL_X_RIGHT}" y2="{RAIL_GND_Y}" '
        f'stroke="{C_GND}" stroke-width="3"/>'
    )
    r.elements.append(
        f'<text x="{RAIL_X_LEFT - 8}" y="{RAIL_GND_Y + 4}" class="label" '
        f'fill="{C_GND}" font-size="11" text-anchor="end">GND</text>'
    )
    r.elements.append(
        f'<text x="{RAIL_X_RIGHT + 8}" y="{RAIL_GND_Y + 4}" class="label" '
        f'fill="{C_GND}" font-size="11">GND</text>'
    )

    # ─── Pico WH block ──────────────────────────────────────────
    pico_x, pico_y, pico_w, pico_h = 80, 80, 220, 610
    r.elements.append(
        f'<rect x="{pico_x}" y="{pico_y}" width="{pico_w}" height="{pico_h}" '
        f'fill="#1a1a1a" stroke="#555" stroke-width="2.5" rx="10"/>'
    )
    r.elements.append(
        f'<text x="{pico_x + pico_w/2}" y="{pico_y + 24}" class="label" '
        f'text-anchor="middle" fill="#FFF" font-size="13">Raspberry Pi Pico WH</text>'
    )
    r.elements.append(
        f'<text x="{pico_x + pico_w/2}" y="{pico_y + 42}" class="value" '
        f'text-anchor="middle" fill="#AAA" font-size="9">RP2040 · 3V3 logic</text>'
    )
    # USB stub
    r.elements.append(
        f'<rect x="{pico_x + pico_w/2 - 30}" y="{pico_y - 12}" width="60" height="12" '
        f'fill="#E91E63" stroke="#AD1457" stroke-width="1"/>'
    )
    r.elements.append(
        f'<text x="{pico_x + pico_w/2}" y="{pico_y - 3}" class="value" '
        f'text-anchor="middle" fill="#FFF" font-size="7">µUSB</text>'
    )

    # 3V3 power pad on TOP edge of Pico — vertical tap UP to +3V3 rail
    p3v3_x = pico_x + pico_w / 2 + 60
    r.elements.append(
        f'<circle cx="{p3v3_x}" cy="{pico_y}" r="5" fill="#C0C0C0" stroke="#666"/>'
    )
    r.elements.append(
        f'<text x="{p3v3_x}" y="{pico_y + 16}" class="value" text-anchor="middle" '
        f'fill="#AAA" font-size="7">3V3</text>'
    )
    r.elements.append(
        f'<line x1="{p3v3_x}" y1="{pico_y}" x2="{p3v3_x}" y2="{RAIL_3V3_Y}" '
        f'stroke="{C_3V3}" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{p3v3_x}" cy="{RAIL_3V3_Y}" r="3" fill="{C_3V3}"/>')

    # GND power pad on BOTTOM edge — vertical tap DOWN to GND rail
    pgnd_x = pico_x + pico_w / 2 + 60
    r.elements.append(
        f'<circle cx="{pgnd_x}" cy="{pico_y + pico_h}" r="5" fill="#C0C0C0" stroke="#666"/>'
    )
    r.elements.append(
        f'<text x="{pgnd_x}" y="{pico_y + pico_h - 8}" class="value" '
        f'text-anchor="middle" fill="#AAA" font-size="7">GND</text>'
    )
    r.elements.append(
        f'<line x1="{pgnd_x}" y1="{pico_y + pico_h}" x2="{pgnd_x}" y2="{RAIL_GND_Y}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{pgnd_x}" cy="{RAIL_GND_Y}" r="3" fill="{C_GND}"/>')

    # Right-edge signal pins. Y values chosen so each peripheral pin
    # at the same Y receives a single straight horizontal wire.
    pin_x_right = pico_x + pico_w
    signals = [
        ("GP4",  "I²C0 SDA", 130, C_I2C),  # → both OLEDs (shared bus)
        ("GP5",  "I²C0 SCL", 160, C_I2C),  # → both OLEDs (shared bus)
        ("GP8",  "LED R",    280, C_LED),
        ("GP9",  "LED G",    310, C_LED),
        ("GP10", "LED B",    340, C_LED),
        ("GP12", "Tap Btn",  390, C_GPIO),
        ("GP13", "Enc SW",   430, C_GPIO),
        ("GP14", "Enc CLK",  460, C_GPIO),
        ("GP15", "Enc DT",   490, C_GPIO),
        ("GP21", "Clk IN",   550, C_CLK),
        ("GP22", "Clk OUT",  580, C_CLK),
    ]
    pin_anchor = {}
    for gp, func, py, color in signals:
        # pin pad on Pico right edge
        r.elements.append(
            f'<circle cx="{pin_x_right}" cy="{py}" r="5" fill="#C0C0C0" stroke="#666"/>'
        )
        # pin-name label inside the Pico body
        r.elements.append(
            f'<text x="{pin_x_right - 10}" y="{py + 3}" class="value" text-anchor="end" '
            f'fill="#AAA" font-size="8">{gp}</text>'
        )
        # function tag attached to the right side of the pin
        tag_w = 78
        r.elements.append(
            f'<rect x="{pin_x_right + 8}" y="{py - 8}" width="{tag_w}" height="16" '
            f'fill="{color}" stroke="#333" stroke-width="0.6" rx="2"/>'
        )
        r.elements.append(
            f'<text x="{pin_x_right + 8 + tag_w/2}" y="{py + 3}" class="label" '
            f'text-anchor="middle" fill="#FFF" font-size="8">{func}</text>'
        )
        # anchor for any wire that originates at this pin = right edge of tag
        pin_anchor[gp] = (pin_x_right + 8 + tag_w, py)

    # Helper: draw a horizontal inline resistor and return the wire
    def inline_resistor(x_start, x_end, y, color, label):
        body_w = 40
        rcx = (x_start + x_end) / 2
        body_x = rcx - body_w / 2
        # left lead
        r.elements.append(
            f'<line x1="{x_start}" y1="{y}" x2="{body_x}" y2="{y}" '
            f'stroke="{color}" stroke-width="2"/>'
        )
        # body
        r.elements.append(
            f'<rect x="{body_x}" y="{y - 9}" width="{body_w}" height="18" '
            f'fill="#F5E6C8" stroke="#5C4500" stroke-width="1"/>'
        )
        r.elements.append(
            f'<text x="{rcx}" y="{y + 3}" class="value" text-anchor="middle" '
            f'font-size="8" fill="#1a1a1a">{label}</text>'
        )
        # right lead
        r.elements.append(
            f'<line x1="{body_x + body_w}" y1="{y}" x2="{x_end}" y2="{y}" '
            f'stroke="{color}" stroke-width="2"/>'
        )

    # Helper: power tap (vertical wire from a pad to a rail) at unique X
    def tap_to_rail(x, y_start, y_end, color):
        r.elements.append(
            f'<line x1="{x}" y1="{y_start}" x2="{x}" y2="{y_end}" '
            f'stroke="{color}" stroke-width="2"/>'
        )
        r.elements.append(f'<circle cx="{x}" cy="{y_end}" r="3" fill="{color}"/>')

    # Helper: pad on a peripheral edge (small grey rect)
    def pad_left(x, y, label, color):
        r.elements.append(
            f'<rect x="{x - 8}" y="{y - 4}" width="8" height="8" fill="#888" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{x + 5}" y="{y + 3}" class="value" font-size="8" fill="{color}">{label}</text>'
        )

    def pad_right(x, y, label, color):
        r.elements.append(
            f'<rect x="{x}" y="{y - 4}" width="8" height="8" fill="#888" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{x - 5}" y="{y + 3}" class="value" text-anchor="end" '
            f'font-size="8" fill="{color}">{label}</text>'
        )

    def pad_top(x, y, label, color):
        r.elements.append(
            f'<rect x="{x - 4}" y="{y - 8}" width="8" height="8" fill="#888" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{x}" y="{y + 13}" class="value" text-anchor="middle" '
            f'font-size="8" fill="{color}">{label}</text>'
        )

    def pad_bottom(x, y, label, color):
        r.elements.append(
            f'<rect x="{x - 4}" y="{y}" width="8" height="8" fill="#888" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{x}" y="{y - 4}" class="value" text-anchor="middle" '
            f'font-size="8" fill="{color}">{label}</text>'
        )

    # ─── 0.96" SSD1306 OLED (top of middle column) ──────────────
    o_x, o_y, o_w, o_h = 460, 110, 280, 70
    r.elements.append(
        f'<rect x="{o_x}" y="{o_y}" width="{o_w}" height="{o_h}" fill="#101418" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    # screen detail (kept inside the body, not overlapping pin pads)
    r.elements.append(
        f'<rect x="{o_x + 60}" y="{o_y + 14}" width="{o_w - 130}" height="42" '
        f'fill="#020a14" stroke="#222"/>'
    )
    r.elements.append(
        f'<text x="{o_x + (o_w - 130)/2 + 60}" y="{o_y + 32}" class="value" '
        f'text-anchor="middle" fill="#7AC4F2" font-size="9">SSD1306 0x3C</text>'
    )
    r.elements.append(
        f'<text x="{o_x + (o_w - 130)/2 + 60}" y="{o_y + 47}" class="value" '
        f'text-anchor="middle" fill="#7AC4F2" font-size="7">128 × 64</text>'
    )
    r.elements.append(
        f'<text x="{o_x + o_w/2}" y="{o_y - 6}" class="label" text-anchor="middle" '
        f'font-size="10">0.96" SSD1306 OLED</text>'
    )

    # SDA / SCL pads on LEFT edge (signal pins), aligned with Pico GP4 / GP5
    pad_left(o_x, 130, "SDA", C_I2C)
    pad_left(o_x, 160, "SCL", C_I2C)
    # VCC pad on TOP edge — vertical tap UP to +3V3 rail (above OLED, free space)
    oled_vcc_x = o_x + o_w - 50
    pad_top(oled_vcc_x, o_y, "VCC", C_3V3)
    tap_to_rail(oled_vcc_x, o_y - 8, RAIL_3V3_Y, C_3V3)
    # GND pad on BOTTOM edge — but the long drop straight down would cross every
    # peripheral below. Jog LEFT into the empty margin (x = 430) and drop there.
    oled_gnd_pad_x = o_x + 50
    oled_gnd_drop_x = 430
    pad_bottom(oled_gnd_pad_x, o_y + o_h, "GND", C_GND)
    r.elements.append(
        f'<line x1="{oled_gnd_pad_x}" y1="{o_y + o_h + 8}" x2="{oled_gnd_drop_x}" y2="{o_y + o_h + 8}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(oled_gnd_drop_x, o_y + o_h + 8, RAIL_GND_Y, C_GND)

    # ─── 0.91" SSD1306 strip OLED (below the main OLED) ────────────
    # Same I²C0 bus, different address (0x3D via solder-jumper or ADDR
    # pin on the module). Smaller block — physically the strip is
    # ~30 × 12 mm, but we draw it slightly larger here for legibility.
    s_x, s_y, s_w, s_h = 460, 200, 320, 60
    r.elements.append(
        f'<rect x="{s_x}" y="{s_y}" width="{s_w}" height="{s_h}" fill="#101418" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    # narrow screen strip
    r.elements.append(
        f'<rect x="{s_x + 60}" y="{s_y + 12}" width="{s_w - 130}" height="34" '
        f'fill="#020a14" stroke="#222"/>'
    )
    r.elements.append(
        f'<text x="{s_x + (s_w - 130)/2 + 60}" y="{s_y + 33}" class="value" '
        f'text-anchor="middle" fill="#7AC4F2" font-size="9">SSD1306 0x3D</text>'
    )
    r.elements.append(
        f'<text x="{s_x + s_w/2}" y="{s_y - 6}" class="label" text-anchor="middle" '
        f'font-size="10">0.91" SSD1306 strip OLED · 128 × 32</text>'
    )

    # SDA/SCL pads on LEFT edge (aligned at strip-internal Y so each branch
    # arrives as a single straight horizontal stub from the bus column)
    pad_left(s_x, 220, "SDA", C_I2C)
    pad_left(s_x, 240, "SCL", C_I2C)
    # VCC pad on TOP edge (right side, away from main OLED's VCC tap X
    # so verticals don't share a column)
    strip_vcc_x = s_x + s_w - 30
    pad_top(strip_vcc_x, s_y, "VCC", C_3V3)
    tap_to_rail(strip_vcc_x, s_y - 8, RAIL_3V3_Y, C_3V3)
    # GND pad on BOTTOM edge — jog LEFT into margin (x = 425) for the drop
    strip_gnd_pad_x = s_x + 30
    strip_gnd_drop_x = 425
    pad_bottom(strip_gnd_pad_x, s_y + s_h, "GND", C_GND)
    r.elements.append(
        f'<line x1="{strip_gnd_pad_x}" y1="{s_y + s_h + 8}" x2="{strip_gnd_drop_x}" y2="{s_y + s_h + 8}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(strip_gnd_drop_x, s_y + s_h + 8, RAIL_GND_Y, C_GND)

    # ─── I²C0 bus: Pico → branch → both OLEDs ──────────────────────
    # Junction column sits in the left margin so the bus visibly forks
    # from one shared net into two devices. Branch X is unique per net
    # so SDA and SCL verticals never overlap.
    sda_branch_x = 445
    scl_branch_x = 440
    sda_anchor = pin_anchor["GP4"]
    scl_anchor = pin_anchor["GP5"]

    # SDA: Pico GP4 → junction at (445, 130) → main SDA pad → branch
    # down to strip SDA pad at (460, 220)
    r.elements.append(
        f'<line x1="{sda_anchor[0]}" y1="{sda_anchor[1]}" x2="{sda_branch_x}" y2="130" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{sda_branch_x}" y1="130" x2="{o_x}" y2="130" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{sda_branch_x}" y1="130" x2="{sda_branch_x}" y2="220" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{sda_branch_x}" y1="220" x2="{s_x}" y2="220" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    # Junction dot at the branch point
    r.elements.append(
        f'<circle cx="{sda_branch_x}" cy="130" r="3.5" fill="{C_I2C}"/>'
    )

    # SCL: Pico GP5 → junction at (440, 160) → main SCL pad → branch
    # down to strip SCL pad at (460, 240)
    r.elements.append(
        f'<line x1="{scl_anchor[0]}" y1="{scl_anchor[1]}" x2="{scl_branch_x}" y2="160" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{scl_branch_x}" y1="160" x2="{o_x}" y2="160" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{scl_branch_x}" y1="160" x2="{scl_branch_x}" y2="240" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{scl_branch_x}" y1="240" x2="{s_x}" y2="240" '
        f'stroke="{C_I2C}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<circle cx="{scl_branch_x}" cy="160" r="3.5" fill="{C_I2C}"/>'
    )

    # ─── RGB LED (common cathode) ───────────────────────────────
    rgb_x, rgb_y, rgb_w, rgb_h = 460, 270, 320, 90
    r.elements.append(
        f'<rect x="{rgb_x}" y="{rgb_y}" width="{rgb_w}" height="{rgb_h}" fill="#1a1a1a" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<text x="{rgb_x + rgb_w/2}" y="{rgb_y - 6}" class="label" text-anchor="middle" '
        f'font-size="10">RGB LED · common cathode (3 × 220 Ω inline)</text>'
    )
    # LED body (single visual representation with 3 inputs)
    led_cx, led_cy = rgb_x + rgb_w - 50, rgb_y + rgb_h / 2
    r.elements.append(f'<defs><radialGradient id="rgbgrad">'
                      f'<stop offset="0%" stop-color="#FFF"/>'
                      f'<stop offset="40%" stop-color="#D44"/>'
                      f'<stop offset="100%" stop-color="#222"/>'
                      f'</radialGradient></defs>')
    r.elements.append(
        f'<circle cx="{led_cx}" cy="{led_cy}" r="20" fill="url(#rgbgrad)" '
        f'stroke="#888" stroke-width="1.5"/>'
    )
    r.elements.append(
        f'<text x="{led_cx}" y="{led_cy + 5}" class="value" text-anchor="middle" '
        f'font-size="8" fill="#FFF" opacity="0.9">RGB</text>'
    )

    # 3 anode pads on LEFT edge, aligned to Pico GP8/9/10
    rgb_anodes = [("R", "GP8", 210), ("G", "GP9", 240), ("B", "GP10", 270)]
    for lbl, gp, py in rgb_anodes:
        pad_left(rgb_x, py, lbl, C_LED)
        # Pico → 220Ω inline → anode pad (single straight wire with inline R)
        a = pin_anchor[gp]
        inline_resistor(a[0], rgb_x, py, C_LED, "220Ω")
        # tiny stub from pad inside RGB body to LED symbol
        r.elements.append(
            f'<line x1="{rgb_x + 8}" y1="{py}" x2="{led_cx - 22}" y2="{led_cy}" '
            f'stroke="{C_LED}" stroke-width="1.2" opacity="0.45"/>'
        )

    # K (cathode) pad on BOTTOM-RIGHT edge — jog RIGHT into the empty
    # margin (x = 840) before dropping to the GND rail; a straight drop
    # at the pad's X would pass through Tap, Encoder, and Clock blocks.
    rgb_k_pad_x = rgb_x + rgb_w - 30
    rgb_k_drop_x = 840
    pad_bottom(rgb_k_pad_x, rgb_y + rgb_h, "K", C_GND)
    # short stub from LED disc to K pad (visual)
    r.elements.append(
        f'<line x1="{led_cx}" y1="{led_cy + 20}" x2="{rgb_k_pad_x}" y2="{rgb_y + rgb_h - 2}" '
        f'stroke="{C_GND}" stroke-width="1.2" opacity="0.45"/>'
    )
    # horizontal jog right, then vertical drop
    r.elements.append(
        f'<line x1="{rgb_k_pad_x}" y1="{rgb_y + rgb_h + 8}" x2="{rgb_k_drop_x}" y2="{rgb_y + rgb_h + 8}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(rgb_k_drop_x, rgb_y + rgb_h + 8, RAIL_GND_Y, C_GND)

    # ─── Tap button (SPST momentary, NO) ────────────────────────
    tap_x, tap_y, tap_w, tap_h = 460, 375, 220, 30
    r.elements.append(
        f'<rect x="{tap_x}" y="{tap_y}" width="{tap_w}" height="{tap_h}" fill="#1a1a1a" '
        f'stroke="#444" stroke-width="2" rx="4"/>'
    )
    r.elements.append(
        f'<text x="{tap_x + tap_w/2}" y="{tap_y - 5}" class="label" text-anchor="middle" '
        f'font-size="10">Tap Button · SPST momentary</text>'
    )
    # Schematic switch glyph: two pads + a tilted lever that meets at one when pressed
    sw_y = tap_y + tap_h / 2
    sw_left = tap_x + 50
    sw_right = tap_x + tap_w - 50
    # leads in from the two pads
    r.elements.append(
        f'<line x1="{tap_x + 8}" y1="{sw_y}" x2="{sw_left}" y2="{sw_y}" '
        f'stroke="#FFF" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{sw_right}" y1="{sw_y}" x2="{tap_x + tap_w - 8}" y2="{sw_y}" '
        f'stroke="#FFF" stroke-width="2"/>'
    )
    # contact dots
    r.elements.append(f'<circle cx="{sw_left}" cy="{sw_y}" r="2.5" fill="#FFF"/>')
    r.elements.append(f'<circle cx="{sw_right}" cy="{sw_y}" r="2.5" fill="#FFF"/>')
    # tilted lever (NO)
    r.elements.append(
        f'<line x1="{sw_left}" y1="{sw_y}" x2="{sw_right - 6}" y2="{sw_y - 12}" '
        f'stroke="#FFF" stroke-width="2"/>'
    )
    # A pad on LEFT, B pad on RIGHT
    pad_left(tap_x, sw_y, "A", C_GPIO)
    pad_right(tap_x + tap_w, sw_y, "B", C_GND)
    # Pico GP12 → A (straight horizontal)
    a = pin_anchor["GP12"]
    r.elements.append(
        f'<line x1="{a[0]}" y1="{a[1]}" x2="{tap_x}" y2="{sw_y}" '
        f'stroke="{C_GPIO}" stroke-width="2"/>'
    )
    # B → right-side jog → vertical drop to GND rail (unique X = 830, in the
    # gap to the right of the encoder, clear of every other peripheral)
    tap_b_drop_x = 830
    r.elements.append(
        f'<line x1="{tap_x + tap_w + 8}" y1="{sw_y}" x2="{tap_b_drop_x}" y2="{sw_y}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(tap_b_drop_x, sw_y, RAIL_GND_Y, C_GND)

    # ─── KY-040 Rotary Encoder ──────────────────────────────────
    enc_x, enc_y, enc_w, enc_h = 460, 420, 320, 90
    r.elements.append(
        f'<rect x="{enc_x}" y="{enc_y}" width="{enc_w}" height="{enc_h}" fill="#272838" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<text x="{enc_x + enc_w/2}" y="{enc_y - 6}" class="label" text-anchor="middle" '
        f'font-size="10">Rotary Encoder · KY-040 (firmware sets PULL_UP on SW/CLK/DT)</text>'
    )
    # Visual shaft
    shaft_x, shaft_y = enc_x + enc_w - 50, enc_y + enc_h / 2
    r.elements.append(
        f'<circle cx="{shaft_x}" cy="{shaft_y}" r="22" fill="#444" '
        f'stroke="#888" stroke-width="1.5"/>'
    )
    r.elements.append(f'<circle cx="{shaft_x}" cy="{shaft_y}" r="6" fill="#666"/>')
    r.elements.append(
        f'<text x="{shaft_x}" y="{shaft_y + 36}" class="value" text-anchor="middle" '
        f'fill="#AAA" font-size="7">push to click</text>'
    )

    # 3 signal pads on LEFT edge — Y aligned to Pico GP13/14/15
    enc_sigs = [("SW", "GP13", 360), ("CLK", "GP14", 390), ("DT", "GP15", 420)]
    for lbl, gp, py in enc_sigs:
        pad_left(enc_x, py, lbl, C_GPIO)
        a = pin_anchor[gp]
        r.elements.append(
            f'<line x1="{a[0]}" y1="{a[1]}" x2="{enc_x}" y2="{py}" '
            f'stroke="{C_GPIO}" stroke-width="2"/>'
        )

    # + pad on TOP edge — straight UP would cross OLED, RGB, and Tap.
    # Jog LEFT into the empty margin (x = 420) and tap UP from there.
    enc_pos_pad_x = enc_x + 30
    enc_pos_drop_x = 420
    pad_top(enc_pos_pad_x, enc_y, "+", C_3V3)
    r.elements.append(
        f'<line x1="{enc_pos_pad_x}" y1="{enc_y - 8}" x2="{enc_pos_drop_x}" y2="{enc_y - 8}" '
        f'stroke="{C_3V3}" stroke-width="2"/>'
    )
    tap_to_rail(enc_pos_drop_x, enc_y - 8, RAIL_3V3_Y, C_3V3)
    # GND pad on BOTTOM edge — straight DOWN would cross the Clock block.
    # Jog RIGHT into the empty margin (x = 870) and drop there.
    enc_gnd_pad_x = enc_x + enc_w - 30
    enc_gnd_drop_x = 890
    pad_bottom(enc_gnd_pad_x, enc_y + enc_h, "GND", C_GND)
    r.elements.append(
        f'<line x1="{enc_gnd_pad_x}" y1="{enc_y + enc_h + 8}" x2="{enc_gnd_drop_x}" y2="{enc_y + enc_h + 8}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(enc_gnd_drop_x, enc_y + enc_h + 8, RAIL_GND_Y, C_GND)

    # ─── Clock I/O block (3.5mm TS jacks) ───────────────────────
    clk_x, clk_y, clk_w, clk_h = 460, 530, 320, 90
    r.elements.append(
        f'<rect x="{clk_x}" y="{clk_y}" width="{clk_w}" height="{clk_h}" fill="#1a1a1a" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<text x="{clk_x + clk_w/2}" y="{clk_y - 6}" class="label" text-anchor="middle" '
        f'font-size="10">Clock I/O · 3.5 mm TS jacks (1 kΩ inline)</text>'
    )

    # IN jack (Y = 480, matches Pico GP21)
    in_jack_cx = clk_x + clk_w - 70
    in_jack_cy = 550
    r.elements.append(
        f'<circle cx="{in_jack_cx}" cy="{in_jack_cy}" r="14" fill="none" '
        f'stroke="#AAA" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{in_jack_cx}" cy="{in_jack_cy}" r="6" fill="#888"/>')
    r.elements.append(
        f'<text x="{in_jack_cx + 22}" y="{in_jack_cy + 4}" class="value" '
        f'font-size="9" fill="#FFF">IN</text>'
    )

    # OUT jack (Y = 510, matches Pico GP22)
    out_jack_cx = clk_x + clk_w - 70
    out_jack_cy = 580
    r.elements.append(
        f'<circle cx="{out_jack_cx}" cy="{out_jack_cy}" r="14" fill="none" '
        f'stroke="#AAA" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{out_jack_cx}" cy="{out_jack_cy}" r="6" fill="#888"/>')
    r.elements.append(
        f'<text x="{out_jack_cx + 22}" y="{out_jack_cy + 4}" class="value" '
        f'font-size="9" fill="#FFF">OUT</text>'
    )

    # IN tip pad LEFT edge → Pico GP21 via inline 1kΩ
    pad_left(clk_x, in_jack_cy, "tip", C_CLK)
    a = pin_anchor["GP21"]
    inline_resistor(a[0], clk_x, in_jack_cy, C_CLK, "1kΩ")
    r.elements.append(
        f'<line x1="{clk_x + 8}" y1="{in_jack_cy}" x2="{in_jack_cx - 14}" y2="{in_jack_cy}" '
        f'stroke="{C_CLK}" stroke-width="1.5" opacity="0.55"/>'
    )

    # OUT tip pad LEFT edge → Pico GP22 via inline 1kΩ
    pad_left(clk_x, out_jack_cy, "tip", C_CLK)
    a = pin_anchor["GP22"]
    inline_resistor(a[0], clk_x, out_jack_cy, C_CLK, "1kΩ")
    r.elements.append(
        f'<line x1="{clk_x + 8}" y1="{out_jack_cy}" x2="{out_jack_cx - 14}" y2="{out_jack_cy}" '
        f'stroke="{C_CLK}" stroke-width="1.5" opacity="0.55"/>'
    )

    # Sleeves go to GND rail at two unique drop X values, in the gap right of the block.
    in_sleeve_drop_x = 850
    out_sleeve_drop_x = 870
    # IN jack sleeve
    r.elements.append(
        f'<line x1="{in_jack_cx}" y1="{in_jack_cy + 14}" '
        f'x2="{in_jack_cx}" y2="{clk_y + clk_h - 12}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{in_jack_cx}" y1="{clk_y + clk_h - 12}" '
        f'x2="{in_sleeve_drop_x}" y2="{clk_y + clk_h - 12}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(in_sleeve_drop_x, clk_y + clk_h - 12, RAIL_GND_Y, C_GND)
    # OUT jack sleeve
    r.elements.append(
        f'<line x1="{out_jack_cx}" y1="{out_jack_cy + 14}" '
        f'x2="{out_jack_cx}" y2="{clk_y + clk_h - 4}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    r.elements.append(
        f'<line x1="{out_jack_cx}" y1="{clk_y + clk_h - 4}" '
        f'x2="{out_sleeve_drop_x}" y2="{clk_y + clk_h - 4}" '
        f'stroke="{C_GND}" stroke-width="2"/>'
    )
    tap_to_rail(out_sleeve_drop_x, clk_y + clk_h - 4, RAIL_GND_Y, C_GND)

    # ─── Notes panel (below GND rail) ───────────────────────────
    nx, ny, nw, nh = 70, 758, 1170, 62
    r.elements.append(
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" fill="#FFF7E6" '
        f'stroke="#D29922" stroke-width="1" rx="4"/>'
    )
    notes = [
        "Phase 0 bench validation — wire per this diagram on a breadboard, then flash firmware/pico/main.py and run test_hw.py for per-peripheral diagnostics.",
        "Both OLEDs share the same I²C0 bus on GP4/GP5; the bus forks at the junction dot in the left margin so SDA reaches both modules from one wire. Main OLED = 0x3C, strip OLED = 0x3D — set the strip's address via its on-module solder jumper or ADDR pin.",
        "All 220 Ω and 1 kΩ resistors are shown inline. KY-040 has on-board 10 kΩ pull-ups; firmware enables Pin.PULL_UP on GP12/13/14/15 — no external pulls required.",
        "GP21 (Clk IN) = Pin.PULL_DOWN with rising-edge IRQ. Phase 0 only loops GP22 → 1 kΩ → GP21 for self-test; ±12 V Eurorack input buffering belongs on the breakout board.",
    ]
    for i, line in enumerate(notes):
        r.elements.append(
            f'<text x="{nx + 12}" y="{ny + 16 + i*12}" class="value" '
            f'font-size="8.5" fill="#5C4500">{line}</text>'
        )

    return r.render()


def generate_phase0_breadboard() -> str:
    """Phase 0 bench-validation wiring — top-down breadboard layout."""
    r = SchematicRenderer(
        1300, 760,
        "Phase 0 — Breadboard Layout (top-down)",
        "Pico WH on a half-size breadboard · peripherals placed where they'd sit "
        "physically · jumper paths colour-coded by net",
    )

    # Net colours (must match the schematic for cross-reference)
    C_3V3 = "#D44"
    C_GND = "#333"
    C_I2C = "#2196F3"
    C_GPIO = "#4CAF50"
    C_LED = "#FF9800"
    C_CLK = "#9C27B0"

    # ─── Breadboard background + rails + holes ──────────────────
    BB_BG = "#F4E9D6"
    BB_HOLE = "#7A5C2A"
    bb_x, bb_y, bb_w, bb_h = 60, 90, 1180, 540
    r.elements.append(
        f'<rect x="{bb_x}" y="{bb_y}" width="{bb_w}" height="{bb_h}" fill="{BB_BG}" '
        f'stroke="#9E7F4A" stroke-width="2" rx="6"/>'
    )

    # Rail strips: top + (red), top − (blue/dark), bot + (red), bot − (dark)
    rails = [
        (bb_y + 22, C_3V3, "+ 3V3"),       # top +
        (bb_y + 44, C_GND, "− GND"),       # top −
        (bb_y + bb_h - 44, C_3V3, "+ 3V3"),  # bot +
        (bb_y + bb_h - 22, C_GND, "− GND"),  # bot −
    ]
    rail_y = {}
    for ry, color, lbl in rails:
        r.elements.append(
            f'<line x1="{bb_x + 30}" y1="{ry}" x2="{bb_x + bb_w - 30}" y2="{ry}" '
            f'stroke="{color}" stroke-width="2.5"/>'
        )
        r.elements.append(
            f'<text x="{bb_x + 14}" y="{ry + 4}" class="value" font-size="9" '
            f'fill="{color}" text-anchor="end">{lbl}</text>'
        )
        for hx in range(bb_x + 50, bb_x + bb_w - 30, 14):
            r.elements.append(
                f'<circle cx="{hx}" cy="{ry}" r="1.4" fill="{BB_HOLE}" opacity="0.7"/>'
            )
    rail_y["top_pos"] = rails[0][0]
    rail_y["top_gnd"] = rails[1][0]
    rail_y["bot_pos"] = rails[2][0]
    rail_y["bot_gnd"] = rails[3][0]

    # Centre channel
    chan_y = (rail_y["top_gnd"] + rail_y["bot_pos"]) / 2
    r.elements.append(
        f'<rect x="{bb_x + 30}" y="{chan_y - 12}" width="{bb_w - 60}" height="24" '
        f'fill="#E0D5BC" stroke="#9E7F4A" stroke-width="1"/>'
    )
    r.elements.append(
        f'<text x="{bb_x + bb_w - 38}" y="{chan_y + 4}" class="value" '
        f'text-anchor="end" font-size="8" fill="#7A5C2A">centre channel</text>'
    )
    # decorative hole columns above + below the channel
    for side in (-1, 1):
        for row in range(5):
            hy = chan_y + side * (16 + row * 12)
            for hx in range(bb_x + 50, bb_x + bb_w - 30, 14):
                r.elements.append(
                    f'<circle cx="{hx}" cy="{hy}" r="1.2" fill="{BB_HOLE}" opacity="0.35"/>'
                )

    # ─── Pico WH straddling the centre channel (left side) ──────
    pico_w, pico_h = 110, 220
    pico_x = bb_x + 90
    pico_y = chan_y - pico_h / 2
    r.elements.append(
        f'<rect x="{pico_x}" y="{pico_y}" width="{pico_w}" height="{pico_h}" '
        f'fill="#1A3A1A" stroke="#0E2A0E" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<text x="{pico_x + pico_w/2}" y="{pico_y + 16}" class="label" '
        f'text-anchor="middle" fill="#FFF" font-size="10">Pico WH</text>'
    )
    # USB stub
    r.elements.append(
        f'<rect x="{pico_x + pico_w/2 - 14}" y="{pico_y - 10}" width="28" height="10" '
        f'fill="#888" stroke="#222"/>'
    )
    # RP2040 chip rectangle
    r.elements.append(
        f'<rect x="{pico_x + 30}" y="{pico_y + pico_h/2 - 22}" width="50" height="44" '
        f'fill="#000" stroke="#333" stroke-width="1"/>'
    )
    r.elements.append(
        f'<text x="{pico_x + 55}" y="{pico_y + pico_h/2 + 2}" class="value" '
        f'text-anchor="middle" fill="#FFF" font-size="6">RP2040</text>'
    )

    # Pico left-edge pin row (GP0…GP15 + GND/3V3 in correct order),
    # right-edge (GP16…GP28 + GND/3V3). We only label the pins we use.
    LEFT_PINS = [
        ("GP0",  None),
        ("GP1",  None),
        ("GND",  C_GND),
        ("GP2",  None),
        ("GP3",  None),
        ("GP4",  C_I2C),
        ("GP5",  C_I2C),
        ("GND",  C_GND),
        ("GP6",  None),
        ("GP7",  None),
        ("GP8",  C_LED),
        ("GP9",  C_LED),
        ("GP10", C_LED),
        ("GP11", None),
        ("GP12", C_GPIO),
        ("GP13", C_GPIO),
        ("GP14", C_GPIO),
        ("GP15", C_GPIO),
    ]
    RIGHT_PINS = [
        ("GP16", None),
        ("GP17", None),
        ("GND",  C_GND),
        ("GP18", None),
        ("GP19", None),
        ("GP20", None),
        ("GP21", C_CLK),
        ("GND",  C_GND),
        ("GP22", C_CLK),
        ("GP26", None),
        ("GP27", None),
        ("GND",  C_GND),
        ("GP28", None),
        ("VBUS", C_3V3),
        ("VSYS", C_3V3),
        ("GND",  C_GND),
        ("3V3",  C_3V3),
    ]

    pin_step_left = (pico_h - 24) / (len(LEFT_PINS) - 1)
    pin_step_right = (pico_h - 24) / (len(RIGHT_PINS) - 1)
    pin_anchor = {}  # only the pins we actually wire
    used_pins = {"GP4", "GP5", "GP8", "GP9", "GP10", "GP12", "GP13", "GP14", "GP15",
                 "GP21", "GP22", "GND", "3V3"}

    for i, (lbl, color) in enumerate(LEFT_PINS):
        py = pico_y + 12 + i * pin_step_left
        px = pico_x
        r.elements.append(
            f'<circle cx="{px}" cy="{py}" r="3.2" fill="#C0C0C0" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{px - 4}" y="{py + 3}" class="value" text-anchor="end" '
            f'fill="#DDD" font-size="6">{lbl}</text>'
        )
        if color and lbl in used_pins and lbl not in pin_anchor:
            pin_anchor[lbl] = (px, py)

    for i, (lbl, color) in enumerate(RIGHT_PINS):
        py = pico_y + 12 + i * pin_step_right
        px = pico_x + pico_w
        r.elements.append(
            f'<circle cx="{px}" cy="{py}" r="3.2" fill="#C0C0C0" stroke="#333"/>'
        )
        r.elements.append(
            f'<text x="{px + 4}" y="{py + 3}" class="value" '
            f'fill="#DDD" font-size="6">{lbl}</text>'
        )
        if color and lbl in used_pins and lbl not in pin_anchor:
            pin_anchor[lbl] = (px, py)

    # Pico-side power: jumper Pico 3V3 → both + rails, Pico GND → both − rails.
    if "3V3" in pin_anchor:
        ax, ay = pin_anchor["3V3"]
        r.elements.append(
            f'<line x1="{ax}" y1="{ay}" x2="{ax + 22}" y2="{ay}" '
            f'stroke="{C_3V3}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<line x1="{ax + 22}" y1="{ay}" x2="{ax + 22}" y2="{rail_y["top_pos"]}" '
            f'stroke="{C_3V3}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<circle cx="{ax + 22}" cy="{rail_y["top_pos"]}" r="3" fill="{C_3V3}"/>'
        )
        r.elements.append(
            f'<line x1="{ax + 22}" y1="{ay}" x2="{ax + 22}" y2="{rail_y["bot_pos"]}" '
            f'stroke="{C_3V3}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<circle cx="{ax + 22}" cy="{rail_y["bot_pos"]}" r="3" fill="{C_3V3}"/>'
        )
    if "GND" in pin_anchor:
        ax, ay = pin_anchor["GND"]
        r.elements.append(
            f'<line x1="{ax}" y1="{ay}" x2="{ax + 30}" y2="{ay}" '
            f'stroke="{C_GND}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<line x1="{ax + 30}" y1="{ay}" x2="{ax + 30}" y2="{rail_y["top_gnd"]}" '
            f'stroke="{C_GND}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<circle cx="{ax + 30}" cy="{rail_y["top_gnd"]}" r="3" fill="{C_GND}"/>'
        )
        r.elements.append(
            f'<line x1="{ax + 30}" y1="{ay}" x2="{ax + 30}" y2="{rail_y["bot_gnd"]}" '
            f'stroke="{C_GND}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        r.elements.append(
            f'<circle cx="{ax + 30}" cy="{rail_y["bot_gnd"]}" r="3" fill="{C_GND}"/>'
        )

    # Helper: jumper path from Pico pin (p1) to peripheral pin (p2) using
    # a 3-segment elbow; drop_x is given so each net has its own vertical.
    def jumper(p1, p2, color, drop_x, label=None):
        x1, y1 = p1
        x2, y2 = p2
        d = (
            f"M{x1},{y1} L{drop_x},{y1} L{drop_x},{y2} L{x2},{y2}"
        )
        r.elements.append(
            f'<path d="{d}" stroke="{color}" stroke-width="2.4" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
        r.elements.append(f'<circle cx="{x2}" cy="{y2}" r="2.5" fill="{color}"/>')
        if label:
            r.elements.append(
                f'<text x="{drop_x + 6}" y="{(y1 + y2)/2 + 3}" class="value" '
                f'fill="{color}" font-size="7">{label}</text>'
            )

    # Helper: peripheral-side rail tap (vertical from a pin to a rail at unique X)
    def rail_tap(pin, rail, color):
        x, y = pin
        r.elements.append(
            f'<line x1="{x}" y1="{y}" x2="{x}" y2="{rail}" '
            f'stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'
        )
        r.elements.append(f'<circle cx="{x}" cy="{rail}" r="3" fill="{color}"/>')

    def pad(x, y):
        r.elements.append(
            f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="#888" stroke="#222"/>'
        )

    # ─── OLED placement (top-right area of breadboard) ──────────
    o_x, o_y, o_w, o_h = bb_x + 350, bb_y + 80, 230, 110
    r.elements.append(
        f'<rect x="{o_x}" y="{o_y}" width="{o_w}" height="{o_h}" fill="#101418" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<rect x="{o_x + 18}" y="{o_y + 28}" width="{o_w - 36}" height="58" '
        f'fill="#020a14" stroke="#222"/>'
    )
    r.elements.append(
        f'<text x="{o_x + o_w/2}" y="{o_y + 22}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="10">0.96" SSD1306 OLED</text>'
    )
    r.elements.append(
        f'<text x="{o_x + o_w/2}" y="{o_y + 60}" class="value" text-anchor="middle" '
        f'fill="#7AC4F2" font-size="9">128 × 64 · I²C 0x3C</text>'
    )
    # 4 pin pads on the OLED bottom edge (the real-world pin order: GND, VCC, SCL, SDA)
    o_pins = [("GND", C_GND), ("VCC", C_3V3), ("SCL", C_I2C), ("SDA", C_I2C)]
    o_pin_at = {}
    for i, (lbl, color) in enumerate(o_pins):
        px = o_x + 30 + i * 55
        py = o_y + o_h
        pad(px, py)
        r.elements.append(
            f'<text x="{px}" y="{py + 22}" class="value" text-anchor="middle" '
            f'fill="{color}" font-size="8.5">{lbl}</text>'
        )
        o_pin_at[lbl] = (px, py)

    # OLED jumpers (each at its own drop X — staggered by 12px)
    jumper(pin_anchor["GP4"], o_pin_at["SDA"], C_I2C, drop_x=o_pin_at["SDA"][0] - 0, label="SDA")
    jumper(pin_anchor["GP5"], o_pin_at["SCL"], C_I2C, drop_x=o_pin_at["SCL"][0] - 0, label="SCL")
    # OLED VCC ↑ to top + rail (its own X)
    rail_tap(o_pin_at["VCC"], rail_y["top_pos"], C_3V3)
    # OLED GND ↑ to top − rail
    rail_tap(o_pin_at["GND"], rail_y["top_gnd"], C_GND)

    # ─── Strip OLED placement (below main OLED) ─────────────────
    # Same I²C0 bus as the main OLED; address 0x3D set on the module's
    # ADDR pin / solder jumper. Smaller block — physically ~30 × 12 mm.
    s_x, s_y, s_w, s_h = bb_x + 350, bb_y + 210, 230, 50
    r.elements.append(
        f'<rect x="{s_x}" y="{s_y}" width="{s_w}" height="{s_h}" fill="#101418" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<rect x="{s_x + 18}" y="{s_y + 12}" width="{s_w - 36}" height="22" '
        f'fill="#020a14" stroke="#222"/>'
    )
    r.elements.append(
        f'<text x="{s_x + s_w/2}" y="{s_y - 4}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="10">0.91" SSD1306 strip · 128 × 32 · 0x3D</text>'
    )
    # 4 pin pads on the strip-OLED bottom edge (same pin order as main)
    s_pins = [("GND", C_GND), ("VCC", C_3V3), ("SCL", C_I2C), ("SDA", C_I2C)]
    s_pin_at = {}
    for i, (lbl, color) in enumerate(s_pins):
        px = s_x + 30 + i * 55
        py = s_y + s_h
        pad(px, py)
        r.elements.append(
            f'<text x="{px}" y="{py + 22}" class="value" text-anchor="middle" '
            f'fill="{color}" font-size="8.5">{lbl}</text>'
        )
        s_pin_at[lbl] = (px, py)
    # Jumpers: from Pico GP4/GP5 to strip pads. Use drop columns just to
    # the LEFT of the main-OLED drop columns so the two devices' SDA/SCL
    # paths sit visually adjacent and don't share verticals.
    jumper(pin_anchor["GP4"], s_pin_at["SDA"], C_I2C,
           drop_x=s_pin_at["SDA"][0] - 12, label="SDA")
    jumper(pin_anchor["GP5"], s_pin_at["SCL"], C_I2C,
           drop_x=s_pin_at["SCL"][0] - 12, label="SCL")
    # Strip OLED VCC ↑ to top + rail
    rail_tap(s_pin_at["VCC"], rail_y["top_pos"], C_3V3)
    # Strip OLED GND ↑ to top − rail
    rail_tap(s_pin_at["GND"], rail_y["top_gnd"], C_GND)

    # ─── Encoder placement (right-middle) ───────────────────────
    e_x, e_y, e_w, e_h = bb_x + 380, chan_y + 30, 220, 130
    r.elements.append(
        f'<rect x="{e_x}" y="{e_y}" width="{e_w}" height="{e_h}" fill="#272838" '
        f'stroke="#444" stroke-width="2" rx="6"/>'
    )
    r.elements.append(
        f'<text x="{e_x + e_w/2}" y="{e_y + 18}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="10">KY-040 Rotary Encoder</text>'
    )
    r.elements.append(
        f'<circle cx="{e_x + 50}" cy="{e_y + 70}" r="22" fill="#444" '
        f'stroke="#888" stroke-width="1.5"/>'
    )
    r.elements.append(f'<circle cx="{e_x + 50}" cy="{e_y + 70}" r="6" fill="#666"/>')
    r.elements.append(
        f'<text x="{e_x + 50}" y="{e_y + 110}" class="value" text-anchor="middle" '
        f'fill="#AAA" font-size="7">push to click</text>'
    )

    # 5 pin pads on encoder right edge (CLK, DT, SW, +, GND) — vertical stack
    e_pins = [("CLK", "GP14", C_GPIO), ("DT", "GP15", C_GPIO),
              ("SW", "GP13", C_GPIO), ("+", None, C_3V3), ("GND", None, C_GND)]
    e_pin_at = {}
    for i, (lbl, _gp, color) in enumerate(e_pins):
        px = e_x + e_w
        py = e_y + 30 + i * 18
        pad(px, py)
        r.elements.append(
            f'<text x="{px + 8}" y="{py + 3}" class="value" font-size="8.5" '
            f'fill="{color}">{lbl}</text>'
        )
        e_pin_at[lbl] = (px, py)

    # Encoder signal jumpers
    jumper(pin_anchor["GP14"], e_pin_at["CLK"], C_GPIO, drop_x=e_x - 50, label="CLK")
    jumper(pin_anchor["GP15"], e_pin_at["DT"],  C_GPIO, drop_x=e_x - 35, label="DT")
    jumper(pin_anchor["GP13"], e_pin_at["SW"],  C_GPIO, drop_x=e_x - 20, label="SW")
    # Encoder + → bottom + rail (closer than top)
    rail_tap(e_pin_at["+"], rail_y["bot_pos"], C_3V3)
    rail_tap(e_pin_at["GND"], rail_y["bot_gnd"], C_GND)

    # ─── Tap button placement (bottom-left, between Pico and encoder) ───
    t_x, t_y, t_w, t_h = bb_x + 230, chan_y + 80, 110, 70
    r.elements.append(
        f'<rect x="{t_x}" y="{t_y}" width="{t_w}" height="{t_h}" fill="#1a1a1a" '
        f'stroke="#666" stroke-width="1.5" rx="4"/>'
    )
    r.elements.append(
        f'<text x="{t_x + t_w/2}" y="{t_y + 14}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="9">Tap Button</text>'
    )
    r.elements.append(
        f'<circle cx="{t_x + t_w/2}" cy="{t_y + 42}" r="11" fill="#666" stroke="#AAA" stroke-width="1.5"/>'
    )
    # 2 pads on button bottom edge: A (signal) on left, B (GND) on right
    t_a = (t_x + 22, t_y + t_h)
    t_b = (t_x + t_w - 22, t_y + t_h)
    pad(*t_a)
    pad(*t_b)
    r.elements.append(
        f'<text x="{t_a[0]}" y="{t_a[1] + 18}" class="value" text-anchor="middle" '
        f'font-size="8.5" fill="{C_GPIO}">A</text>'
    )
    r.elements.append(
        f'<text x="{t_b[0]}" y="{t_b[1] + 18}" class="value" text-anchor="middle" '
        f'font-size="8.5" fill="{C_GND}">B</text>'
    )
    jumper(pin_anchor["GP12"], t_a, C_GPIO, drop_x=t_a[0], label="Tap")
    rail_tap(t_b, rail_y["bot_gnd"], C_GND)

    # ─── RGB LED placement (bottom-middle) ──────────────────────
    g_x, g_y, g_w, g_h = bb_x + 600, chan_y + 80, 230, 90
    r.elements.append(
        f'<rect x="{g_x}" y="{g_y}" width="{g_w}" height="{g_h}" fill="#1a1a1a" '
        f'stroke="#666" stroke-width="1.5" rx="4"/>'
    )
    r.elements.append(
        f'<text x="{g_x + g_w/2}" y="{g_y + 14}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="9">RGB LED · 3 × 220 Ω</text>'
    )
    # LED disc
    r.elements.append(
        f'<circle cx="{g_x + 35}" cy="{g_y + 50}" r="12" fill="#FFF" stroke="#888" stroke-width="1.5"/>'
    )
    r.elements.append(
        f'<circle cx="{g_x + 35}" cy="{g_y + 50}" r="9" fill="#D44" opacity="0.5"/>'
    )
    # 4 pads bottom edge: R, G, B, K — each anode has its own 220Ω footprint above the pad
    rgb_pin_data = [("R", "GP8", C_LED), ("G", "GP9", C_LED), ("B", "GP10", C_LED),
                    ("K", None, C_GND)]
    rgb_pin_at = {}
    for i, (lbl, _gp, color) in enumerate(rgb_pin_data):
        px = g_x + 80 + i * 38
        py = g_y + g_h
        # 220Ω footprint just above the pad (only for anodes)
        if lbl != "K":
            r.elements.append(
                f'<rect x="{px - 9}" y="{py - 30}" width="18" height="18" '
                f'fill="#F5E6C8" stroke="#5C4500" stroke-width="0.8"/>'
            )
            r.elements.append(
                f'<text x="{px}" y="{py - 18}" class="value" text-anchor="middle" '
                f'font-size="7" fill="#1a1a1a">220Ω</text>'
            )
            r.elements.append(
                f'<line x1="{px}" y1="{py - 12}" x2="{px}" y2="{py - 4}" '
                f'stroke="#1a1a1a" stroke-width="1.5"/>'
            )
        pad(px, py)
        r.elements.append(
            f'<text x="{px}" y="{py + 18}" class="value" text-anchor="middle" '
            f'font-size="8.5" fill="{color}">{lbl}</text>'
        )
        rgb_pin_at[lbl] = (px, py)

    # RGB jumpers — each on its own drop X so verticals don't share segments
    jumper(pin_anchor["GP8"],  rgb_pin_at["R"], C_LED, drop_x=rgb_pin_at["R"][0])
    jumper(pin_anchor["GP9"],  rgb_pin_at["G"], C_LED, drop_x=rgb_pin_at["G"][0])
    jumper(pin_anchor["GP10"], rgb_pin_at["B"], C_LED, drop_x=rgb_pin_at["B"][0])
    rail_tap(rgb_pin_at["K"], rail_y["bot_gnd"], C_GND)

    # ─── Clock I/O placement (top-right of the breadboard) ──────
    j_x, j_y, j_w, j_h = bb_x + 900, bb_y + 80, 220, 230
    r.elements.append(
        f'<rect x="{j_x}" y="{j_y}" width="{j_w}" height="{j_h}" fill="#1a1a1a" '
        f'stroke="#666" stroke-width="1.5" rx="4"/>'
    )
    r.elements.append(
        f'<text x="{j_x + j_w/2}" y="{j_y + 16}" class="label" text-anchor="middle" '
        f'fill="#FFF" font-size="9">Clock I/O · 3.5 mm jacks</text>'
    )

    # OUT jack (top of block)
    r.elements.append(
        f'<circle cx="{j_x + 40}" cy="{j_y + 60}" r="20" fill="none" stroke="#AAA" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{j_x + 40}" cy="{j_y + 60}" r="8" fill="#888"/>')
    r.elements.append(
        f'<text x="{j_x + 40}" y="{j_y + 96}" class="value" text-anchor="middle" '
        f'fill="#FFF" font-size="9">OUT</text>'
    )
    # 1k for OUT — drawn between jack tip and the breadboard pad on the right
    r.elements.append(
        f'<rect x="{j_x + 90}" y="{j_y + 50}" width="36" height="20" '
        f'fill="#F5E6C8" stroke="#5C4500"/>'
    )
    r.elements.append(
        f'<text x="{j_x + 108}" y="{j_y + 64}" class="value" text-anchor="middle" '
        f'font-size="7" fill="#1a1a1a">1 kΩ</text>'
    )
    r.elements.append(
        f'<line x1="{j_x + 60}" y1="{j_y + 60}" x2="{j_x + 90}" y2="{j_y + 60}" '
        f'stroke="#1a1a1a" stroke-width="1.5"/>'
    )

    # IN jack (bottom of block)
    r.elements.append(
        f'<circle cx="{j_x + 40}" cy="{j_y + 170}" r="20" fill="none" stroke="#AAA" stroke-width="2"/>'
    )
    r.elements.append(f'<circle cx="{j_x + 40}" cy="{j_y + 170}" r="8" fill="#888"/>')
    r.elements.append(
        f'<text x="{j_x + 40}" y="{j_y + 206}" class="value" text-anchor="middle" '
        f'fill="#FFF" font-size="9">IN</text>'
    )
    r.elements.append(
        f'<rect x="{j_x + 90}" y="{j_y + 160}" width="36" height="20" '
        f'fill="#F5E6C8" stroke="#5C4500"/>'
    )
    r.elements.append(
        f'<text x="{j_x + 108}" y="{j_y + 174}" class="value" text-anchor="middle" '
        f'font-size="7" fill="#1a1a1a">1 kΩ</text>'
    )
    r.elements.append(
        f'<line x1="{j_x + 60}" y1="{j_y + 170}" x2="{j_x + 90}" y2="{j_y + 170}" '
        f'stroke="#1a1a1a" stroke-width="1.5"/>'
    )

    # OUT/IN tip pads on breadboard (right side of each 1k)
    out_pad = (j_x + 132, j_y + 60)
    in_pad = (j_x + 132, j_y + 170)
    pad(*out_pad)
    pad(*in_pad)
    r.elements.append(
        f'<text x="{out_pad[0]}" y="{out_pad[1] - 14}" class="value" '
        f'text-anchor="middle" font-size="7" fill="{C_CLK}">tip→GP22</text>'
    )
    r.elements.append(
        f'<text x="{in_pad[0]}" y="{in_pad[1] + 22}" class="value" '
        f'text-anchor="middle" font-size="7" fill="{C_CLK}">tip→GP21</text>'
    )

    # Pico → tip pad jumpers (their own drop X each)
    jumper(pin_anchor["GP22"], out_pad, C_CLK, drop_x=j_x - 30, label="OUT")
    jumper(pin_anchor["GP21"], in_pad,  C_CLK, drop_x=j_x - 14, label="IN")

    # Sleeves go to the closest GND rail (top − for OUT, bottom − for IN)
    r.elements.append(
        f'<line x1="{j_x + 40}" y1="{j_y + 80}" x2="{j_x + 40}" y2="{rail_y["top_gnd"]}" '
        f'stroke="{C_GND}" stroke-width="2.4" stroke-dasharray="3,2" stroke-linecap="round"/>'
    )
    r.elements.append(f'<circle cx="{j_x + 40}" cy="{rail_y["top_gnd"]}" r="3" fill="{C_GND}"/>')
    r.elements.append(
        f'<line x1="{j_x + 40}" y1="{j_y + 190}" x2="{j_x + 40}" y2="{rail_y["bot_gnd"]}" '
        f'stroke="{C_GND}" stroke-width="2.4" stroke-dasharray="3,2" stroke-linecap="round"/>'
    )
    r.elements.append(f'<circle cx="{j_x + 40}" cy="{rail_y["bot_gnd"]}" r="3" fill="{C_GND}"/>')

    # ─── Notes + legend ─────────────────────────────────────────
    nx, ny, nw, nh = 60, 642, 1180, 60
    r.elements.append(
        f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" fill="#FFF7E6" '
        f'stroke="#D29922" stroke-width="1" rx="4"/>'
    )
    r.elements.append(
        f'<text x="{nx + 12}" y="{ny + 16}" class="label" font-size="10" fill="#5C4500">'
        f'Breadboard tips</text>'
    )
    notes = [
        "• Pico straddles the centre channel — left column = GP0–15, right column = GP16+ / power.",
        "• Pico 3V3 jumpers up to BOTH + rails and Pico GND down to BOTH − rails so peripherals can pull from the closer side.",
        "• Each net uses its own dedicated drop column — verticals never share an X, so jumper paths can't be mistaken for shorts.",
        "• OLED VCC and GND go to the closest TOP rails; encoder + and GND go to the closest BOTTOM rails.",
    ]
    for i, line in enumerate(notes):
        r.elements.append(
            f'<text x="{nx + 14}" y="{ny + 32 + i*10}" class="value" '
            f'font-size="8.5" fill="#5C4500">{line}</text>'
        )

    # legend
    lgx, lgy = 70, 720
    items = [(C_3V3, "+3V3"), (C_GND, "GND"), (C_I2C, "I²C0"),
             (C_GPIO, "GPIO"), (C_LED, "RGB"), (C_CLK, "Clock")]
    r.elements.append(
        f'<text x="{lgx}" y="{lgy - 5}" class="label" font-size="9">Jumper colours:</text>'
    )
    for i, (color, lbl) in enumerate(items):
        x = lgx + i * 165
        r.elements.append(
            f'<rect x="{x}" y="{lgy}" width="14" height="10" fill="{color}" '
            f'stroke="#333" stroke-width="0.5"/>'
        )
        r.elements.append(
            f'<text x="{x + 18}" y="{lgy + 9}" class="value" font-size="9">{lbl}</text>'
        )

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
        ("led_driver_array_schematic.svg", generate_led_driver_schematic),
        ("vactrol_full_schematic.svg", generate_vactrol_full_schematic),
        ("wiring_overview.svg", generate_wiring_diagram),
        ("dip_pinout_reference.svg", generate_dip_pinout_reference),
        ("touch_plate_schematic.svg", generate_touch_plate_schematic),
        ("esd_protection_schematic.svg", generate_esd_protection_schematic),
        ("system_architecture_block.svg", generate_system_architecture_block),
        ("audio_signal_flow.svg", generate_audio_signal_flow),
        ("cv_control_flow.svg", generate_cv_control_flow),
        ("signal_flow_overview.svg", generate_signal_flow_overview),
        ("cd4051_multiplexer.svg", generate_cd4051_multiplexer),
        ("cv_input_protection_diagram.svg", generate_cv_input_protection_diagram),
        ("pico_pinout_diagram.svg", generate_pico_pinout_diagram),
        ("lpc2361_pinout_diagram.svg", generate_lpc2361_pinout_diagram),
        ("db9_connector_diagram.svg", generate_db9_connector_diagram),
        ("power_regulation_diagram.svg", generate_power_regulation_diagram),
        ("testpoints_map.svg", generate_testpoints_map),
        ("expander_power_distribution.svg", generate_expander_power_distribution),
        ("midi_interface_circuit.svg", generate_midi_interface_circuit),
        ("pico_power_protection.svg", generate_pico_power_protection),
        # Phase 0 bench validation
        ("phase0_wiring_schematic.svg", generate_phase0_wiring_schematic),
        ("phase0_breadboard.svg",       generate_phase0_breadboard),
        # Mod catalog (M01–M14)
        ("mod_m01_triangle_gain.svg",        generate_mod_m01_triangle_gain),
        ("mod_m02_soft_sync.svg",            generate_mod_m02_soft_sync),
        ("mod_m03_sine_extract.svg",         generate_mod_m03_sine_extract),
        ("mod_m04_metalizer_vca.svg",        generate_mod_m04_metalizer_vca),
        ("mod_m05_filter_selfosc_kill.svg",  generate_mod_m05_filter_selfosc_kill),
        ("mod_m06_pwm_cv.svg",               generate_mod_m06_pwm_cv),
        ("mod_m07_pitch_starve.svg",         generate_mod_m07_pitch_starve),
        ("mod_m08_subharmonic.svg",          generate_mod_m08_subharmonic),
        ("mod_m09_pwm_selfmod.svg",          generate_mod_m09_pwm_selfmod),
        ("mod_m10_brute_extreme.svg",        generate_mod_m10_brute_extreme),
        ("mod_m11_touch_envretrig.svg",      generate_mod_m11_touch_envretrig),
        ("mod_m12_arg.svg",                  generate_mod_m12_arg),
        ("mod_m13_vco_sync_env.svg",         generate_mod_m13_vco_sync_env),
        ("mod_m14_vco_bias_starve.svg",      generate_mod_m14_vco_bias_starve),
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
