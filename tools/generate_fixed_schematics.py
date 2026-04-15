#!/usr/bin/env python3
"""Generate fixed schematics for MACROBRUTE - addressing overlapping lines and incorrect layouts."""

import os
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Point:
    """2D point for schematic coordinates."""
    x: float
    y: float


class SchematicRenderer:
    """Renders electronic schematics to SVG."""
    
    # Color scheme - consistent across all diagrams
    C_BG = "#FEFEFE"
    C_WIRE = "#1a1a1a"
    C_COMPONENT = "#1a1a1a"
    C_TEXT = "#1a1a1a"
    C_TEXT_LIGHT = "#555"
    C_ANNOTATION = "#0066CC"
    
    # Signal type colors (consistent with wiring diagrams)
    C_AUDIO = "#0066CC"      # Blue - Audio
    C_CV = "#CC6600"         # Orange - CV
    C_GATE = "#009933"       # Green - Gate/Clock
    C_POWER_POS = "#CC0000"  # Red - +12V
    C_POWER_NEG = "#0000CC"  # Dark Blue - -12V
    C_GND = "#1a1a1a"        # Black - GND
    C_CONTROL = "#6600CC"    # Purple - Control
    C_SPI = "#2196F3"        # Light Blue - SPI
    C_I2C = "#00BCD4"        # Cyan - I2C/UART
    C_GPIO = "#4CAF50"       # Green - GPIO
    C_ADC = "#795548"        # Brown - ADC
    
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
    
    def wire(self, p1: Point, p2: Point, color: str = None, thick: bool = False) -> None:
        """Draw connecting wire."""
        stroke = color if color else self.C_WIRE
        cls = "wire-thick" if thick else "wire"
        self.elements.append(f'<line x1="{p1.x}" y1="{p1.y}" x2="{p2.x}" y2="{p2.y}" stroke="{stroke}" class="{cls}"/>')
    
    def elbow_hv(self, x1: float, y1: float, x2: float, y2: float, color: str = None, label: str = "") -> None:
        """Draw horizontal-then-vertical elbow wire."""
        stroke = color if color else self.C_WIRE
        mid_x = (x1 + x2) / 2
        path = f'M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}'
        self.elements.append(f'<path d="{path}" stroke="{stroke}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            self.elements.append(f'<text x="{mid_x}" y="{y1-5}" class="value" text-anchor="middle" fill="{color or self.C_TEXT_LIGHT}" font-size="7">{label}</text>')
    
    def elbow_vh(self, x1: float, y1: float, x2: float, y2: float, color: str = None, label: str = "") -> None:
        """Draw vertical-then-horizontal elbow wire."""
        stroke = color if color else self.C_WIRE
        mid_y = (y1 + y2) / 2
        path = f'M{x1},{y1} L{x1},{mid_y} L{x2},{mid_y} L{x2},{y2}'
        self.elements.append(f'<path d="{path}" stroke="{stroke}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            self.elements.append(f'<text x="{x1+5}" y="{mid_y-3}" class="value" fill="{color or self.C_TEXT_LIGHT}" font-size="7">{label}</text>')
    
    def block(self, x: float, y: float, w: float, h: float, label: str, sublabel: str = "", 
              color: str = "#333", text_color: str = "#FFF") -> None:
        """Draw functional block."""
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>')
        self.elements.append(f'<text x="{x+w/2}" y="{y+h/2-5}" class="label" text-anchor="middle" fill="{text_color}" font-size="10">{label}</text>')
        if sublabel:
            self.elements.append(f'<text x="{x+w/2}" y="{y+h/2+12}" class="value" text-anchor="middle" fill="{text_color}" font-size="8">{sublabel}</text>')
    
    def render(self) -> str:
        """Render complete SVG."""
        return self._svg_header() + "\n".join(self.elements) + self._svg_footer()


def generate_pico_pinout_fixed():
    """Generate CORRECTED Pico H pinout with official layout."""
    r = SchematicRenderer(1000, 750, "Raspberry Pi Pico H Pinout (Corrected)", "Official Layout - GPIO Left/Right, Power Right, Debug Bottom")
    
    # Pico H board dimensions and position
    board_x = 300
    board_y = 80
    board_w = 400
    board_h = 540
    
    # Draw main board
    r.elements.append(f'<rect x="{board_x}" y="{board_y}" width="{board_w}" height="{board_h}" fill="#006600" stroke="#1a1a1a" stroke-width="3" rx="8"/>')
    
    # USB connector at top
    usb_x = board_x + board_w/2
    r.elements.append(f'<rect x="{usb_x-50}" y="{board_y-15}" width="100" height="20" fill="#333" stroke="#666" stroke-width="1"/>')
    r.elements.append(f'<text x="{usb_x}" y="{board_y-3}" class="value" text-anchor="middle" fill="#CCC" font-size="8">Micro USB</text>')
    
    # LEFT SIDE GPIO (GP0-GP15) - Top to Bottom
    left_pins = [
        ("GP0", "UART0 TX", "→ LPC2361", r.C_I2C),
        ("GP1", "UART0 RX", "→ LPC2361", r.C_I2C),
        ("GND", None, None, "#1a1a1a"),
        ("GP2", "ADC0", "Touch 1", r.C_ADC),
        ("GP3", "ADC1", "Touch 2", r.C_ADC),
        ("GP4", "MIDI TX", "UART1", r.C_GPIO),
        ("GP5", "MIDI RX", "UART1", r.C_GPIO),
        ("GND", None, None, "#1a1a1a"),
        ("GP6", None, None, r.C_GPIO),
        ("GP7", None, None, r.C_GPIO),
        ("GP8", "LED Clock", "RGB", r.C_CONTROL),
        ("GP9", "LED Gate", "RGB", r.C_CONTROL),
        ("GP10", "LED Mode", "RGB", r.C_CONTROL),
        ("GP11", None, None, r.C_GPIO),
        ("GP12", "Tap Button", None, r.C_GPIO),
        ("GP13", "Enc Button", None, r.C_GPIO),
        ("GP14", "Enc CLK", None, r.C_GPIO),
        ("GP15", "Enc DT", None, r.C_GPIO),
    ]
    
    pin_spacing = 26
    start_y = board_y + 40
    
    for i, (pin_name, func, connection, color) in enumerate(left_pins):
        pin_y = start_y + i * pin_spacing
        
        # Pin circle on board edge
        r.elements.append(f'<circle cx="{board_x}" cy="{pin_y}" r="6" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')
        
        # Pin label on board
        r.elements.append(f'<text x="{board_x+12}" y="{pin_y+3}" class="value" fill="#FFF" font-size="8">{pin_name}</text>')
        
        # Function box and connection
        if func:
            box_w = 90
            r.elements.append(f'<rect x="{board_x-110}" y="{pin_y-10}" width="{box_w}" height="20" fill="{color}" stroke="#333" stroke-width="1" rx="2"/>')
            r.elements.append(f'<text x="{board_x-65}" y="{pin_y+4}" class="label" text-anchor="middle" fill="#FFF" font-size="8">{func}</text>')
        
        if connection:
            r.elements.append(f'<text x="{board_x-120}" y="{pin_y+4}" class="value" text-anchor="end" fill="#666" font-size="7">{connection}</text>')
    
    # RIGHT SIDE GPIO (GP16-GP28) - Top to Bottom
    right_pins = [
        ("GP16", "OLED DC", "SPI", r.C_SPI),
        ("GP17", "OLED CS", "SPI", r.C_SPI),
        ("GND", None, None, "#1a1a1a"),
        ("GP18", "OLED SCK", "SPI", r.C_SPI),
        ("GP19", "OLED MOSI", "SPI", r.C_SPI),
        ("GP20", "OLED RST", "SPI", r.C_SPI),
        ("GP21", "Clock In", None, r.C_GPIO),
        ("GND", None, None, "#1a1a1a"),
        ("GP22", "Clock Out", None, r.C_GPIO),
        ("GP26", "ADC0 Spare", None, r.C_ADC),
        ("GP27", "ADC1 Spare", None, r.C_ADC),
        ("GND", None, None, "#1a1a1a"),
        ("GP28", "ADC2 Spare", None, r.C_ADC),
    ]
    
    for i, (pin_name, func, connection, color) in enumerate(right_pins):
        pin_y = start_y + i * pin_spacing
        
        # Pin circle on board edge
        r.elements.append(f'<circle cx="{board_x+board_w}" cy="{pin_y}" r="6" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')
        
        # Pin label on board
        r.elements.append(f'<text x="{board_x+board_w-10}" y="{pin_y+3}" class="value" text-anchor="end" fill="#FFF" font-size="8">{pin_name}</text>')
        
        # Function box
        if func:
            r.elements.append(f'<rect x="{board_x+board_w+15}" y="{pin_y-10}" width="80" height="20" fill="{color}" stroke="#333" stroke-width="1" rx="2"/>')
            r.elements.append(f'<text x="{board_x+board_w+55}" y="{pin_y+4}" class="label" text-anchor="middle" fill="#FFF" font-size="8">{func}</text>')
    
    # BOTTOM SIDE - DEBUG PINS
    debug_pins = [
        ("VSYS", "+5V Input", "#D44"),
        ("VBUS", "USB 5V", "#D44"),
        ("GND", "Ground", "#1a1a1a"),
        ("3V3_EN", "Enable", "#666"),
        ("3V3_OUT", "3.3V Out", "#D44"),
        ("GND", "Ground", "#1a1a1a"),
        ("SWDIO", "Debug", "#9C27B0"),
        ("SWCLK", "Debug", "#9C27B0"),
    ]
    
    bottom_y = board_y + board_h
    bottom_pin_spacing = 45
    bottom_start_x = board_x + 40
    
    for i, (pin_name, func, color) in enumerate(debug_pins):
        pin_x = bottom_start_x + i * bottom_pin_spacing
        
        # Pin circle
        r.elements.append(f'<circle cx="{pin_x}" cy="{bottom_y}" r="6" fill="#C0C0C0" stroke="#666" stroke-width="1"/>')
        
        # Label below
        r.elements.append(f'<text x="{pin_x}" y="{bottom_y+20}" class="value" text-anchor="middle" fill="#333" font-size="7">{pin_name}</text>')
        
        if func:
            r.elements.append(f'<text x="{pin_x}" y="{bottom_y+32}" class="value" text-anchor="middle" fill="#666" font-size="6">{func}</text>')
    
    # PIN 1 INDICATOR
    r.elements.append(f'<rect x="{board_x+10}" y="{board_y+10}" width="20" height="6" fill="#FFF"/>')
    r.elements.append(f'<text x="{board_x+20}" y="{board_y+15}" class="label" text-anchor="middle" fill="#000" font-size="6">▶</text>')
    
    # LEGEND
    legend_x = 50
    legend_y = 650
    r.elements.append(f'<rect x="{legend_x}" y="{legend_y}" width="900" height="90" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="{legend_x+450}" y="{legend_y+20}" class="label" text-anchor="middle" font-size="11">Pin Function Legend (MACROBRUTE Configuration)</text>')
    
    legend_items = [
        (r.C_SPI, "OLED SPI (GP16-20)"),
        (r.C_GPIO, "GPIO/Buttons/Encoder (GP12-15)"),
        (r.C_CONTROL, "LED Outputs (GP8-10)"),
        (r.C_ADC, "ADC/Touch (GP2-3, 26-28)"),
        (r.C_I2C, "UART Debug/MIDI (GP0-1, GP4-5)"),
        ("#9C27B0", "Debug SWD"),
        ("#D44", "Power (+5V, 3.3V)"),
    ]
    
    for i, (color, label) in enumerate(legend_items):
        row = i // 4
        col = i % 4
        x = legend_x + 20 + col * 220
        y = legend_y + 45 + row * 22
        r.elements.append(f'<rect x="{x}" y="{y-8}" width="20" height="14" fill="{color}" stroke="#333" stroke-width="0.5" rx="2"/>')
        r.elements.append(f'<text x="{x+28}" y="{y+3}" class="value" font-size="9">{label}</text>')
    
    # NOTES
    r.elements.append(f'<rect x="750" y="80" width="230" height="250" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="865" y="105" class="label" text-anchor="middle" fill="#1B5E20">Pico H Layout Notes</text>')
    
    notes = [
        "• GPIO 0-15: LEFT side (top→bottom)",
        "• GPIO 16-28: RIGHT side (top→bottom)",
        "• DEBUG pins: BOTTOM edge",
        "• USB: TOP edge",
        "• Square pad = Pin 1",
        "• All GPIO = 3.3V logic",
        "• ADC pins = 0-3.3V input",
    ]
    
    for i, note in enumerate(notes):
        r.elements.append(f'<text x="765" y="{130 + i*25}" class="value" font-size="8" fill="#1B5E20">{note}</text>')
    
    return r.render()


def main():
    """Generate fixed schematics."""
    output_dir = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("pico_pinout_diagram_fixed", generate_pico_pinout_fixed),
    ]
    
    for name, func in diagrams:
        filepath = os.path.join(output_dir, f"{name}.svg")
        try:
            svg_content = func()
            with open(filepath, 'w') as f:
                f.write(svg_content)
            print(f"Generated: {name}.svg")
        except Exception as e:
            print(f"Failed {name}: {e}")
    
    print("Done!")


if __name__ == "__main__":
    main()


def generate_system_architecture_fixed():
    """Generate System Architecture with improved routing - no overlapping lines."""
    r = SchematicRenderer(1100, 800, "MACROBRUTE System Architecture", "Fixed Layout - Clear Signal Routing")
    
    # Colors
    C_SYNTH = "#2196F3"
    C_EXPANDER = "#4CAF50"
    C_INTERFACE = "#FF9800"
    C_CONTROL = "#9C27B0"
    C_AUDIO = "#E91E63"
    
    # SECTION LABELS
    r.elements.append(f'<text x="120" y="60" class="label" font-size="13" fill="{C_SYNTH}">MICROBRUTE CORE</text>')
    r.elements.append(f'<text x="480" y="60" class="label" font-size="13" fill="{C_INTERFACE}">INTERFACE</text>')
    r.elements.append(f'<text x="850" y="60" class="label" font-size="13" fill="{C_EXPANDER}">EXPANDER MODULES</text>')
    
    # MICROBRUTE CORE (Left Column)
    synth_blocks = [
        ("VCO", "Oscillator", 80),
        ("VCF", "Steiner-Parker", 140),
        ("VCA", "Amplifier", 200),
        ("LFO", "Modulation", 260),
        ("Envelope", "ADSR", 320),
    ]
    
    synth_y_positions = {}
    for label, sublabel, y in synth_blocks:
        r.block(50, y, 130, 45, label, sublabel, C_SYNTH)
        synth_y_positions[label] = y + 22
    
    # INTERFACE CENTER SECTION
    # DB-9 A - Outputs (top)
    r.block(440, 80, 130, 55, "DB-9 A", "Outputs →", C_INTERFACE)
    db9a_y = 107
    
    # DB-9 B - Inputs + Power (middle)
    r.block(440, 160, 130, 55, "DB-9 B", "Inputs + Power", C_INTERFACE)
    db9b_y = 187
    
    # Pico W (below DB-9)
    r.block(440, 250, 130, 60, "Pico W", "RP2040 Control", C_CONTROL)
    pico_y = 280
    
    # Touch Pads
    r.block(440, 330, 130, 50, "Touch Pads", "4-Point Bend", C_CONTROL)
    touch_y = 355
    
    # EXPANDER MODULES (Right Column)
    expander_blocks = [
        ("Noise", "White/Pink", 80),
        ("LFO", "Free-running", 135),
        ("S&H", "Sample & Hold", 190),
        ("Clock Div", "/2 /4 /8", 245),
        ("Slew", "Glide", 300),
        ("Attenuvert", "CV Scale", 355),
    ]
    
    expander_y_positions = {}
    for label, sublabel, y in expander_blocks:
        r.block(850, y, 130, 45, label, sublabel, C_EXPANDER)
        expander_y_positions[label] = y + 22
    
    # SIGNAL ROUTING - ELBOW STYLE WITH VERTICAL SEPARATION
    
    # MicroBrute to DB-9 A outputs (vertical separation to prevent overlap)
    outputs = [
        ("VCO", db9a_y - 15, C_SYNTH, "Saw/Sqr"),
        ("VCF", db9a_y, C_SYNTH, "VCF"),
        ("VCA", db9a_y + 15, C_SYNTH, ""),
        ("LFO", db9a_y + 5, C_SYNTH, "LFO"),
        ("Envelope", db9a_y + 10, C_SYNTH, "Env"),
    ]
    
    for src, target_y, color, label in outputs:
        src_y = synth_y_positions[src]
        r.elbow_hv(180, src_y, 440, target_y, color, label)
    
    # Expander to DB-9 B inputs
    expander_inputs = [
        ("Noise", db9b_y - 15, C_EXPANDER, "Noise"),
        ("LFO", db9b_y - 5, C_EXPANDER, ""),
        ("S&H", db9b_y + 5, C_EXPANDER, ""),
        ("Clock Div", db9b_y + 15, C_EXPANDER, "Clock"),
    ]
    
    for src, target_y, color, label in expander_inputs:
        src_y = expander_y_positions[src]
        r.elbow_hv(850, src_y, 570, target_y, color, label)
    
    # DB-9 B to MicroBrute (inputs)
    r.elbow_hv(440, db9b_y + 20, 180, synth_y_positions["VCF"] + 10, C_INTERFACE, "Filter CV")
    r.elbow_hv(440, db9b_y + 25, 180, synth_y_positions["VCA"] + 10, C_INTERFACE, "VCA CV")
    
    # Control signals
    r.elbow_hv(570, pico_y, 750, expander_y_positions["LFO"], C_CONTROL, "GPIO")
    r.elbow_hv(570, touch_y, 750, expander_y_positions["S&H"], C_CONTROL, "Touch")
    
    # AUDIO OUTPUTS (Bottom Section)
    r.elements.append(f'<text x="550" y="450" class="label" font-size="12" fill="{C_AUDIO}">BUFFERED AUDIO OUTPUTS</text>')
    
    audio_outputs = [
        ("Main Out", "Line Level", 150),
        ("Saw Out", "Raw VCO", 300),
        ("Sqr Out", "Raw VCO", 450),
        ("Mix Out", "Pre-VCF", 600),
        ("VCF Out", "Post-Filter", 750),
    ]
    
    for label, sublabel, x in audio_outputs:
        r.block(x, 480, 100, 40, label, sublabel, C_AUDIO)
    
    # Connection from DB-9 A to audio outputs
    r.elements.append(f'<line x1="505" y1="135" x2="505" y2="470" stroke="{C_AUDIO}" stroke-width="2"/>')
    r.elements.append(f'<line x1="200" y1="470" x2="800" y2="470" stroke="{C_AUDIO}" stroke-width="2"/>')
    for x in [200, 350, 500, 650, 800]:
        r.elements.append(f'<line x1="{x}" y1="470" x2="{x}" y2="480" stroke="{C_AUDIO}" stroke-width="2"/>')
    
    # LEGEND
    r.elements.append(f'<rect x="50" y="560" width="1000" height="220" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="550" y="590" class="label" text-anchor="middle" fill="#333">System Legend & Notes</text>')
    
    legend_items = [
        (C_SYNTH, "MicroBrute Core (VCO, VCF, VCA, LFO, Envelope)"),
        (C_INTERFACE, "Interface (DB-9, Power Distribution)"),
        (C_EXPANDER, "Expander Modules (Noise, LFO, S&H, Clock, etc.)"),
        (C_CONTROL, "Control System (Pico W, Touch Pads, LEDs)"),
        (C_AUDIO, "Audio Outputs (Buffered, Protected)"),
    ]
    
    for i, (color, label) in enumerate(legend_items):
        y_pos = 615 + i * 22
        r.elements.append(f'<rect x="70" y="{y_pos-8}" width="20" height="15" fill="{color}" stroke="#333" stroke-width="0.5" rx="2"/>')
        r.elements.append(f'<text x="100" y="{y_pos+4}" class="value" font-size="10">{label}</text>')
    
    notes = [
        "• Elbow routing prevents signal line crossings",
        "• All audio outputs buffered with 1kΩ + TL074",
        "• CV signals attenuated and protected at interface",
        "• Power: ±12V via DB-9 B, +5V via Pico VSYS",
    ]
    
    for i, note in enumerate(notes):
        r.elements.append(f'<text x="600" y="{615 + i*22}" class="value" font-size="9">{note}</text>')
    
    return r.render()


def generate_audio_signal_flow_fixed():
    """Generate Audio Signal Flow with notes box repositioned to prevent overlap."""
    r = SchematicRenderer(950, 700, "Audio Signal Flow", "From VCO Through Filter to Outputs - Fixed Layout")
    
    C_VCO = "#E91E63"
    C_MIXER = "#FF9800"
    C_FILTER = "#2196F3"
    C_AMP = "#4CAF50"
    C_OUT = "#9C27B0"
    C_TP = "#666"
    
    # INPUT SOURCES (Left Column - staggered vertically)
    sources = [
        ("Saw VCO", "-5V to +5V", 70, C_VCO),
        ("Square VCO", "0V to +5V", 120, C_VCO),
        ("Sub Osc", "-5V to +5V", 170, C_VCO),
        ("Ext In", "Line Level", 220, C_VCO),
        ("Noise", "White/Pink", 270, C_VCO),
    ]
    
    for label, sublabel, y, color in sources:
        r.block(50, y, 100, 35, label, sublabel, color)
    
    # MIXER
    r.block(220, 140, 100, 60, "MIXER", "Ultrafaux", C_MIXER)
    
    # Staggered elbow connections from sources to mixer (no overlap)
    r.elbow_hv(150, 87, 220, 160, C_VCO)
    r.elbow_hv(150, 137, 230, 170, C_VCO)
    r.elbow_hv(150, 187, 240, 180, C_VCO)
    r.elbow_hv(150, 237, 250, 190, C_VCO)
    r.elbow_hv(150, 287, 260, 200, C_VCO)
    
    # VCF
    r.block(380, 150, 100, 50, "VCF", "Steiner-Parker", C_FILTER)
    r.elbow_hv(320, 170, 380, 175, C_MIXER, "Mix Out")
    
    # VCA
    r.block(540, 150, 100, 50, "VCA", "ADSR Controlled", C_AMP)
    r.elbow_hv(480, 175, 540, 175, C_FILTER, "Filter Out")
    
    # MAIN OUT
    r.block(700, 150, 100, 50, "MAIN OUT", "Line Level", C_OUT)
    r.elbow_hv(640, 175, 700, 175, C_AMP)
    
    # TEST POINTS (Separate row below, with clear vertical space)
    r.elements.append(f'<text x="475" y="270" class="label" text-anchor="middle" font-size="11" fill="{C_TP}">Buffered Test Point Outputs</text>')
    
    tp_y = 300
    tps = [
        ("TP94 Saw", 100, 87),
        ("TP93 Square", 220, 137),
        ("TP30 Mix", 340, 175),
        ("TP19 VCF", 480, 175),
        ("TP10/11 VCA", 620, 175),
        ("Main Out", 760, 175),
    ]
    
    for label, x, src_y in tps:
        # Draw TP
        r.elements.append(f'<circle cx="{x}" cy="{tp_y}" r="6" fill="{C_TP}" stroke="#333" stroke-width="1"/>')
        r.elements.append(f'<text x="{x}" y="{tp_y+20}" class="value" text-anchor="middle" font-size="8">{label}</text>')
        
        # Connection line (vertical with buffer note)
        r.elements.append(f'<line x1="{x}" y1="{tp_y-6}" x2="{x}" y2="{src_y+18}" stroke="{C_TP}" stroke-width="1" stroke-dasharray="3,2"/>')
    
    # Buffer notes
    r.elements.append(f'<text x="160" y="240" class="value" font-size="7" fill="{C_TP}">1kΩ+TL074</text>')
    r.elements.append(f'<text x="400" y="240" class="value" font-size="7" fill="{C_TP}">1kΩ+TL074</text>')
    r.elements.append(f'<text x="560" y="240" class="value" font-size="7" fill="{C_TP}">Direct</text>')
    
    # NOTES BOX (Bottom, clear placement - no overlap)
    r.elements.append(f'<rect x="50" y="360" width="850" height="320" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="475" y="385" class="label" text-anchor="middle" fill="#1B5E20">Signal Flow & Test Point Notes</text>')
    
    notes = [
        ("Signal Path:", "Saw/Square/Sub/Ext/Noise → Mixer → VCF → VCA → Main Out", 410),
        ("VCO Outputs:", "Raw waveforms (-5V to +5V, ~10Vpp) at TP94, TP93 via buffers", 435),
        ("Mixer Stage:", "Ultrafaux passive mixer with 5 inputs and individual level controls", 460),
        ("VCF Stage:", "Steiner-Parker filter (12dB/octave) with resonance control via RP13", 485),
        ("VCA Stage:", "Controlled by ADSR envelope (attack, decay, sustain, release)", 510),
        ("Test Points:", "All TPs have 1kΩ series resistor + TL074 buffer for safe external patching", 535),
        ("Protection:", "Outputs are current-limited and buffered - safe for Eurorack/modular systems", 560),
        ("Buffering:", "Required because direct wiring causes oscillator loading and signal degradation", 585),
        ("Key Point:", "TP30 (Mix) captures pre-filter signal; TP19 (VCF) captures post-filter signal", 610),
        ("Output:", "Main Out is line-level (-10dBV nominal) suitable for mixers and audio interfaces", 635),
    ]
    
    for label, value, y in notes:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9" fill="#1B5E20">{label}</text>')
        r.elements.append(f'<text x="160" y="{y}" class="value" font-size="9">{value}</text>')
    
    return r.render()


def generate_cv_control_flow_fixed():
    """Generate CV Control Flow with improved modulation routing - no overlaps."""
    r = SchematicRenderer(1000, 750, "CV Control Flow", "Modulation Routing - Fixed Layout")
    
    C_MOD = "#9C27B0"      # Purple - modulation sources
    C_DEST = "#2196F3"     # Blue - modulation targets
    C_INPUT = "#FF9800"    # Orange - external inputs
    C_EXPANDER = "#4CAF50" # Green - expander modules
    
    # SECTION LABELS
    r.elements.append(f'<text x="120" y="50" class="label" font-size="12" fill="{C_MOD}">MODULATION SOURCES</text>')
    r.elements.append(f'<text x="480" y="50" class="label" font-size="12" fill="{C_DEST}">MODULATION TARGETS</text>')
    r.elements.append(f'<text x="820" y="50" class="label" font-size="12" fill="{C_INPUT}">EXTERNAL INPUTS</text>')
    
    # LEFT COLUMN: Modulation Sources (staggered)
    sources = [
        ("LFO", "0-5V △", 70, C_MOD),
        ("Envelope", "0-5V ADSR", 125, C_MOD),
        ("Pitch CV", "1V/oct", 180, C_MOD),
        ("Mod Wheel", "0-5V", 235, C_MOD),
        ("Exp LFO", "Free Run", 305, C_EXPANDER),
        ("Exp S&H", "S&H", 360, C_EXPANDER),
    ]
    
    source_positions = {}
    for label, sublabel, y, color in sources:
        r.block(60, y, 95, 40, label, sublabel, color)
        source_positions[label] = y + 20
    
    # CENTER COLUMN: Modulation Targets (staggered)
    targets = [
        ("Pitch", "VCO Freq", 70),
        ("Filter", "Cutoff", 125),
        ("Resonance", "Peak", 180),
        ("VCA", "Amplitude", 235),
        ("PWM", "Pulse Width", 290),
        ("Metalizer", "Harmonics", 345),
    ]
    
    target_positions = {}
    for label, sublabel, y in targets:
        r.block(480, y, 95, 40, label, sublabel, C_DEST)
        target_positions[label] = y + 20
    
    # RIGHT COLUMN: External CV Inputs
    inputs = [
        ("Filter CV", "DB-9 B P1", 70),
        ("VCA CV", "DB-9 B P2", 125),
        ("Res CV", "Vactrol", 180),
        ("Gate In", "DB-9 B P5", 235),
        ("Sync", "DB-9 B P4", 290),
    ]
    
    input_positions = {}
    for label, sublabel, y in inputs:
        r.block(820, y, 110, 40, label, sublabel, C_INPUT)
        input_positions[label] = y + 20
    
    # CONNECTIONS - VERTICALLY SEPARATED TO PREVENT OVERLAP
    
    # LFO connections (staggered x positions)
    r.elbow_hv(155, source_positions["LFO"], 480, target_positions["Pitch"], C_MOD, "LFO")
    r.elbow_hv(155, source_positions["LFO"]+5, 480, target_positions["Filter"], C_MOD, "")
    r.elbow_hv(155, source_positions["LFO"]+10, 480, target_positions["VCA"], C_MOD, "")
    
    # Envelope connections
    r.elbow_hv(155, source_positions["Envelope"], 480, target_positions["Filter"]+5, C_MOD, "Env")
    r.elbow_hv(155, source_positions["Envelope"]+5, 480, target_positions["VCA"]+5, C_MOD, "")
    
    # Pitch CV
    r.elbow_hv(155, source_positions["Pitch CV"], 480, target_positions["Pitch"]+5, C_MOD, "1V/oct")
    
    # Mod Wheel
    r.elbow_hv(155, source_positions["Mod Wheel"], 480, target_positions["Pitch"]+10, C_MOD, "")
    
    # Expander connections
    r.elbow_hv(155, source_positions["Exp LFO"], 480, target_positions["Resonance"], C_EXPANDER, "Exp LFO")
    r.elbow_hv(155, source_positions["Exp S&H"], 480, target_positions["Resonance"]+5, C_EXPANDER, "Exp S&H")
    
    # External Inputs -> Targets (from right)
    r.elbow_hv(820, input_positions["Filter CV"], 575, target_positions["Filter"]+10, C_INPUT, "Filter CV")
    r.elbow_hv(820, input_positions["VCA CV"], 575, target_positions["VCA"]+10, C_INPUT, "VCA CV")
    r.elbow_hv(820, input_positions["Res CV"], 575, target_positions["Resonance"]+10, C_INPUT, "Res CV")
    r.elbow_hv(820, input_positions["Gate In"], 575, target_positions["PWM"], C_INPUT, "Gate")
    r.elbow_hv(820, input_positions["Sync"], 575, target_positions["Metalizer"], C_INPUT, "Sync")
    
    # NOTES BOX (Bottom, clear area)
    r.elements.append(f'<rect x="50" y="440" width="900" height="290" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="500" y="465" class="label" text-anchor="middle" fill="#E65100">CV Routing & Modulation Notes</text>')
    
    notes = [
        ("Mod Matrix:", "MicroBrute patch panel routes LFO/Env to destinations using front-panel switches", 490),
        ("Attenuation:", "External CV inputs (from Expander) pass through attenuverter pots for level control", 515),
        ("Summing:", "Multiple CV sources sum at destination (Pitch = Keyboard + LFO + Pitch Bend + Expander)", 540),
        ("Vactrol:", "Resonance CV uses optocoupler (LED+LDR) for smooth, noise-free resonance control", 565),
        ("Protection:", "All CV inputs have 100kΩ series resistance + BAT54S clamping diodes to ±5V", 590),
        ("Range:", "MicroBrute expects 0-5V CV signals. External inputs attenuated/clamped to this range", 615),
        ("Path:", "Sources → Mod Matrix (internal) OR DB-9 B (external) → Targets (VCO, VCF, VCA, etc.)", 640),
        ("Expander LFO:", "Free-running LFO from expander can modulate resonance independently of main LFO", 665),
        ("S&H:", "Sample & Hold can create stepped modulation effects on filter or resonance", 690),
        ("Gate In:", "External gate can trigger envelope or reset LFO phase via DB-9 B Pin 5", 715),
    ]
    
    for label, value, y in notes:
        r.elements.append(f'<text x="70" y="{y}" class="label" font-size="9" fill="#E65100">{label}</text>')
        r.elements.append(f'<text x="165" y="{y}" class="value" font-size="9">{value}</text>')
    
    return r.render()


def generate_signal_flow_overview_fixed():
    """Generate Signal Flow Overview with improved hierarchical routing."""
    r = SchematicRenderer(1100, 800, "Signal Flow Overview", "Complete System - Hierarchical Layout")
    
    C_MICRO = "#4A90E2"
    C_BREAKOUT = "#F5A623"
    C_DB9 = "#7ED321"
    C_EXPANDER = "#BD10E0"
    
    # SECTION LABELS
    r.elements.append(f'<text x="150" y="45" class="label" text-anchor="middle" fill="{C_MICRO}">MICROBRUTE</text>')
    r.elements.append(f'<text x="400" y="45" class="label" text-anchor="middle" fill="{C_BREAKOUT}">BREAKOUT</text>')
    r.elements.append(f'<text x="650" y="45" class="label" text-anchor="middle" fill="{C_DB9}">DB-9</text>')
    r.elements.append(f'<text x="900" y="45" class="label" text-anchor="middle" fill="{C_EXPANDER}">EXPANDER</text>')
    
    # MAIN SECTIONS AS HIERARCHICAL BLOCKS
    
    # MicroBrute Section
    r.elements.append(f'<rect x="50" y="60" width="200" height="400" fill="#E8F4FD" stroke="{C_MICRO}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="150" y="80" class="label" text-anchor="middle" font-size="10">Test Points</text>')
    
    micro_signals = [
        ("TP94 Saw", 100, r.C_AUDIO),
        ("TP93 Square", 130, r.C_AUDIO),
        ("TP30 Mix", 160, r.C_AUDIO),
        ("TP19 VCF", 190, r.C_AUDIO),
        ("TP124 Triangle", 220, r.C_AUDIO),
        ("TP83 Gate", 260, r.C_GATE),
        ("Pitch CV", 290, r.C_CV),
        ("Envelope", 320, r.C_CV),
        ("LFO", 350, r.C_CV),
    ]
    
    for label, y, color in micro_signals:
        r.elements.append(f'<text x="70" y="{y}" class="value" font-size="8">{label}</text>')
        r.elements.append(f'<circle cx="230" cy="{y-3}" r="4" fill="{color}"/>')
    
    # Power test points
    r.elements.append(f'<text x="70" y="400" class="value" font-size="8" fill="{r.C_POWER_POS}">TP70 +12V</text>')
    r.elements.append(f'<text x="70" y="425" class="value" font-size="8" fill="{r.C_POWER_NEG}">TP71 -12V</text>')
    r.elements.append(f'<text x="70" y="450" class="value" font-size="8">TP72 GND</text>')
    
    # Breakout Section
    r.elements.append(f'<rect x="300" y="60" width="200" height="400" fill="#FEF3E2" stroke="{C_BREAKOUT}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="400" y="80" class="label" text-anchor="middle" font-size="10">Processing</text>')
    
    buffers = [
        ("TL074 A", "Saw", 100, "1kΩ"),
        ("TL074 B", "Square", 130, "1kΩ"),
        ("TL074 C", "Mix", 160, "1kΩ"),
        ("TL074 D", "VCF", 190, "1kΩ"),
        ("TL072", "Triangle", 220, "2× gain"),
        ("CD40106", "Gate", 260, "Schmitt"),
        ("Direct", "Pitch", 290, ""),
        ("TL074", "Env", 320, "Buffer"),
        ("TL074", "LFO", 350, "Buffer"),
    ]
    
    for label, sublabel, y, protection in buffers:
        r.block(320, y-12, 160, 24, label, sublabel, C_BREAKOUT)
    
    # Power section in breakout
    r.elements.append(f'<rect x="320" y="400" width="160" height="50" fill="#FFEBEE" stroke="#CC0000" stroke-width="1" rx="3"/>')
    r.elements.append(f'<text x="400" y="420" class="label" text-anchor="middle" font-size="9">Power Distribution</text>')
    r.elements.append(f'<text x="400" y="440" class="value" text-anchor="middle" font-size="7">±12V / +5V / GND</text>')
    
    # DB-9 Section (Split into A and B)
    r.elements.append(f'<rect x="550" y="60" width="200" height="190" fill="#E8F5E9" stroke="{C_DB9}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="650" y="80" class="label" text-anchor="middle" font-size="10">DB-9 A (Outputs)</text>')
    
    db9a_pins = [
        ("1: Gate", 100),
        ("2: Pitch", 120),
        ("3: Env", 140),
        ("4: LFO", 160),
        ("5: Mix", 180),
        ("6: VCF", 200),
        ("7: Saw", 220),
        ("8: Square", 240),
    ]
    
    for label, y in db9a_pins:
        r.elements.append(f'<text x="570" y="{y}" class="value" font-size="7">{label}</text>')
    
    # DB-9 B
    r.elements.append(f'<rect x="550" y="270" width="200" height="190" fill="#FFF3E0" stroke="#FF9800" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="650" y="290" class="label" text-anchor="middle" font-size="10">DB-9 B (Inputs)</text>')
    
    db9b_pins = [
        ("1: Filter CV", 310),
        ("2: VCA CV", 330),
        ("3: Resonance", 350),
        ("4: Sync", 370),
        ("5: Gate In", 390),
        ("7: +12V", 415),
        ("8: -12V", 435),
        ("9: GND", 455),
    ]
    
    for label, y in db9b_pins:
        r.elements.append(f'<text x="570" y="{y}" class="value" font-size="7">{label}</text>')
    
    # Expander Section
    r.elements.append(f'<rect x="800" y="60" width="270" height="400" fill="#F3E5F5" stroke="{C_EXPANDER}" stroke-width="2" rx="5"/>')
    r.elements.append(f'<text x="935" y="80" class="label" text-anchor="middle" font-size="10">Expander Modules</text>')
    
    # Output jacks
    outputs = [
        ("Saw OUT", 100, r.C_AUDIO),
        ("Square OUT", 130, r.C_AUDIO),
        ("Mix OUT", 170, r.C_AUDIO),
        ("VCF OUT", 200, r.C_AUDIO),
        ("Triangle OUT", 230, r.C_AUDIO),
        ("Gate OUT", 270, r.C_GATE),
        ("Pitch IN", 300, r.C_CV),
        ("Env IN", 330, r.C_CV),
        ("LFO IN", 360, r.C_CV),
    ]
    
    for label, y, color in outputs:
        r.block(820, y-10, 90, 22, label, "", color)
    
    # Expander circuits
    circuits = [
        ("Noise Gen", 100),
        ("LFO", 140),
        ("S&H", 180),
        ("Clock Div", 220),
        ("Slew", 260),
        ("Attenuvert", 300),
    ]
    
    for label, y in circuits:
        r.block(930, y-10, 120, 24, label, "", "#9C27B0")
    
    # CONNECTIONS - HIERARCHICAL BUS STYLE
    
    # Horizontal connection lines between sections
    r.elements.append(f'<line x1="250" y1="250" x2="300" y2="250" stroke="#999" stroke-width="2"/>')
    r.elements.append(f'<text x="275" y="240" class="value" text-anchor="middle" font-size="7">Signals</text>')
    
    r.elements.append(f'<line x1="500" y1="170" x2="550" y2="170" stroke="#999" stroke-width="2"/>')
    r.elements.append(f'<text x="525" y="160" class="value" text-anchor="middle" font-size="7">To A</text>')
    
    r.elements.append(f'<line x1="500" y1="380" x2="550" y2="380" stroke="#999" stroke-width="2"/>')
    r.elements.append(f'<text x="525" y="370" class="value" text-anchor="middle" font-size="7">To B</text>')
    
    r.elements.append(f'<line x1="750" y1="170" x2="800" y2="170" stroke="#999" stroke-width="2"/>')
    r.elements.append(f'<text x="775" y="160" class="value" text-anchor="middle" font-size="7">Outputs</text>')
    
    r.elements.append(f'<line x1="750" y1="380" x2="800" y2="380" stroke="#999" stroke-width="2"/>')
    r.elements.append(f'<text x="775" y="370" class="value" text-anchor="middle" font-size="7">Inputs</text>')
    
    # Power bus
    r.elements.append(f'<line x1="250" y1="425" x2="820" y2="425" stroke="#CC0000" stroke-width="3" stroke-dasharray="5,3"/>')
    r.elements.append(f'<text x="535" y="415" class="value" text-anchor="middle" font-size="8" fill="#CC0000">Power Bus (±12V, +5V, GND)</text>')
    
    # LEGEND
    r.elements.append(f'<rect x="50" y="500" width="1020" height="280" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>')
    r.elements.append(f'<text x="560" y="530" class="label" text-anchor="middle" font-size="12">System Legend & Signal Flow</text>')
    
    # Color legend
    legend_items = [
        ("Blue", r.C_AUDIO, "Audio Signals"),
        ("Orange", r.C_CV, "CV Signals"),
        ("Green", r.C_GATE, "Gate/Clock"),
        ("Red", r.C_POWER_POS, "+12V Power"),
        ("Dark Blue", r.C_POWER_NEG, "-12V Power"),
    ]
    
    for i, (name, color, desc) in enumerate(legend_items):
        y = 560 + i * 22
        r.elements.append(f'<rect x="70" y="{y-8}" width="20" height="14" fill="{color}" stroke="#333" stroke-width="0.5"/>')
        r.elements.append(f'<text x="100" y="{y+3}" class="value" font-size="9">{name}: {desc}</text>')
    
    # Flow description
    flow_text = [
        "Signal Flow: MicroBrute Test Points → Breakout Buffers → DB-9 A → Expander Outputs",
        "CV Flow: Expander Outputs → DB-9 B → Breakout Processing → MicroBrute Inputs",
        "Power: MicroBrute ±12V → Breakout Distribution → DB-9 B → Expander Eurorack Power",
        "Control: Pico W (via Breakout) → Expander Module Control + LED Indicators",
    ]
    
    for i, text in enumerate(flow_text):
        r.elements.append(f'<text x="350" y="{560 + i*22}" class="value" font-size="9">• {text}</text>')
    
    # Key notes
    notes = [
        "Key Points:",
        "• All audio outputs buffered with 1kΩ series resistor + TL074 op-amp",
        "• All CV inputs protected with 100kΩ series resistor + clamping diodes",
        "• Gate signal conditioned with CD40106 Schmitt trigger for clean edges",
        "• Power distribution includes fuses and reverse-polarity protection (1N5817)",
        "• Hierarchical layout reduces wiring complexity and improves readability",
    ]
    
    for i, note in enumerate(notes):
        r.elements.append(f'<text x="70" y="{660 + i*20}" class="label" font-size="9" fill="#333">{note}</text>')
    
    return r.render()


def main():
    """Generate all fixed schematics."""
    output_dir = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("pico_pinout_diagram_fixed", generate_pico_pinout_fixed),
        ("system_architecture_block_fixed", generate_system_architecture_fixed),
        ("audio_signal_flow_fixed", generate_audio_signal_flow_fixed),
        ("cv_control_flow_fixed", generate_cv_control_flow_fixed),
        ("signal_flow_overview_fixed", generate_signal_flow_overview_fixed),
    ]
    
    for name, func in diagrams:
        filepath = os.path.join(output_dir, f"{name}.svg")
        try:
            svg_content = func()
            with open(filepath, 'w') as f:
                f.write(svg_content)
            print(f"Generated: {name}.svg")
        except Exception as e:
            print(f"Failed {name}: {e}")
    
    print("All fixed schematics generated successfully!")


if __name__ == "__main__":
    main()
