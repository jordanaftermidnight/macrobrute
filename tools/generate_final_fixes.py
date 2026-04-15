#!/usr/bin/env python3
"""Final fixes for problematic diagrams with proper elbow routing."""

import os


def system_architecture_final():
    """System Architecture - Clean elbow routing, no overlapping text."""
    width, height = 1000, 700
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#333"/>
  </marker>
</defs>
<style>
  .t {{ font: bold 15px sans-serif; fill: #1a1a1a; }}
  .st {{ font: 11px sans-serif; fill: #555; }}
  .l {{ font: bold 10px sans-serif; fill: #FFF; text-anchor: middle; }}
  .v {{ font: 9px sans-serif; fill: #333; }}
  .vl {{ font: 8px sans-serif; fill: #666; }}
</style>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="500" y="25" class="t" text-anchor="middle">MACROBRUTE System Architecture</text>
<text x="500" y="45" class="st" text-anchor="middle">Signal Flow: MicroBrute → Breakout → Expander</text>
'''
    
    # Colors
    C_MICRO = "#2196F3"
    C_DB9A = "#FF9800"
    C_DB9B = "#FF5722"
    C_PICO = "#9C27B0"
    C_TOUCH = "#673AB7"
    C_EXPAND = "#4CAF50"
    
    # Section labels
    svg += '<text x="120" y="70" class="v" font-weight="bold" font-size="11" fill="#333">MICROBRUTE</text>\n'
    svg += '<text x="500" y="70" class="v" font-weight="bold" font-size="11" fill="#333">INTERFACE</text>\n'
    svg += '<text x="850" y="70" class="v" font-weight="bold" font-size="11" fill="#333">EXPANDER</text>\n'
    
    # MicroBrute blocks (left side)
    micro_blocks = [
        ("VCO", "Osc", 90, C_MICRO),
        ("VCF", "Filter", 140, C_MICRO),
        ("VCA", "Amp", 190, C_MICRO),
        ("LFO", "LFO", 240, C_MICRO),
        ("ENV", "Env", 290, C_MICRO),
    ]
    
    micro_y = {}
    for name, sub, y, color in micro_blocks:
        svg += f'<rect x="50" y="{y}" width="110" height="40" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="105" y="{y+17}" class="l" font-size="10">{name}</text>\n'
        svg += f'<text x="105" y="{y+32}" class="l" font-size="8">{sub}</text>\n'
        micro_y[name] = y + 20
    
    # DB-9 A - Outputs (top center) - simplified, no internal text
    svg += f'<rect x="400" y="90" width="120" height="100" fill="{C_DB9A}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="120" class="l" font-size="11">DB-9 A</text>\n'
    svg += f'<text x="460" y="140" class="l" font-size="9">OUTPUTS</text>\n'
    svg += f'<text x="460" y="160" class="l" font-size="8">→ Expander</text>\n'
    db9a_y = 140
    
    # DB-9 B - Inputs (bottom center)
    svg += f'<rect x="400" y="240" width="120" height="100" fill="{C_DB9B}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="270" class="l" font-size="11">DB-9 B</text>\n'
    svg += f'<text x="460" y="290" class="l" font-size="9">INPUTS</text>\n'
    svg += f'<text x="460" y="310" class="l" font-size="8">← Expander</text>\n'
    db9b_y = 290
    
    # Pico W
    svg += f'<rect x="400" y="390" width="120" height="50" fill="{C_PICO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="415" class="l" font-size="10">Pico W</text>\n'
    svg += f'<text x="460" y="430" class="l" font-size="8">Control</text>\n'
    pico_y = 415
    
    # Touch Pads
    svg += f'<rect x="400" y="470" width="120" height="40" fill="{C_TOUCH}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="488" class="l" font-size="10">Touch</text>\n'
    svg += f'<text x="460" y="502" class="l" font-size="8">4-Point</text>\n'
    touch_y = 490
    
    # Expander blocks (right side)
    exp_blocks = [
        ("Noise", "Gen", 90, C_EXPAND),
        ("LFO", "Free", 140, C_EXPAND),
        ("S&H", "Sample", 190, C_EXPAND),
        ("Clock", "Div", 240, C_EXPAND),
        ("Slew", "Glide", 290, C_EXPAND),
        ("Atten", "CV", 340, C_EXPAND),
    ]
    
    exp_y = {}
    for name, sub, y, color in exp_blocks:
        svg += f'<rect x="820" y="{y}" width="110" height="40" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="875" y="{y+17}" class="l" font-size="10">{name}</text>\n'
        svg += f'<text x="875" y="{y+32}" class="l" font-size="8">{sub}</text>\n'
        exp_y[name] = y + 20
    
    # ELBOW CONNECTIONS - proper routing
    
    # 1. MicroBrute → DB-9 A (outputs)
    # VCO to DB-9 A (horizontal then vertical)
    svg += f'<path d="M160,{micro_y["VCO"]} L280,{micro_y["VCO"]} L280,110 L400,110" stroke="{C_MICRO}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="220" y="105" class="vl" font-size="7">Saw/Sqr</text>\n'
    
    # VCF to DB-9 A
    svg += f'<path d="M160,{micro_y["VCF"]} L300,{micro_y["VCF"]} L300,140 L400,140" stroke="{C_MICRO}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="240" y="135" class="vl" font-size="7">VCF</text>\n'
    
    # LFO to DB-9 A
    svg += f'<path d="M160,{micro_y["LFO"]} L280,{micro_y["LFO"]} L280,170 L400,170" stroke="{C_MICRO}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="220" y="165" class="vl" font-size="7">LFO</text>\n'
    
    # ENV to DB-9 A
    svg += f'<path d="M160,{micro_y["ENV"]} L300,{micro_y["ENV"]} L300,125 L400,125" stroke="{C_MICRO}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="240" y="120" class="vl" font-size="7">Env</text>\n'
    
    # 2. DB-9 A → Expander (outputs to modules)
    # To Noise
    svg += f'<path d="M520,{db9a_y-20} L670,{db9a_y-20} L670,{exp_y["Noise"]} L820,{exp_y["Noise"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="670" y="115" class="vl" font-size="7">Audio→</text>\n'
    
    # To LFO
    svg += f'<path d="M520,{db9a_y} L650,{db9a_y} L650,{exp_y["LFO"]} L820,{exp_y["LFO"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="650" y="150" class="vl" font-size="7">→LFO</text>\n'
    
    # 3. Expander → DB-9 B (inputs FROM expander)
    # LFO to DB-9 B
    svg += f'<path d="M820,{exp_y["LFO"]+10} L700,{exp_y["LFO"]+10} L700,{db9b_y-20} L520,{db9b_y-20}" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="700" y="270" class="vl" font-size="7">Filter CV→</text>\n'
    
    # S&H to DB-9 B
    svg += f'<path d="M820,{exp_y["S&H"]} L680,{exp_y["S&H"]} L680,{db9b_y} L520,{db9b_y}" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="680" y="240" class="vl" font-size="7">Res CV→</text>\n'
    
    # Clock to DB-9 B
    svg += f'<path d="M820,{exp_y["Clock"]} L660,{exp_y["Clock"]} L660,{db9b_y+20} L520,{db9b_y+20}" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="660" y="265" class="vl" font-size="7">Sync→</text>\n'
    
    # 4. DB-9 B → MicroBrute (inputs to synth)
    # To VCF
    svg += f'<path d="M400,{db9b_y-10} L320,{db9b_y-10} L320,{micro_y["VCF"]+15} L160,{micro_y["VCF"]+15}" stroke="{C_DB9B}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="320" y="160" class="vl" font-size="7">→Filter</text>\n'
    
    # To VCA
    svg += f'<path d="M400,{db9b_y+10} L340,{db9b_y+10} L340,{micro_y["VCA"]+15} L160,{micro_y["VCA"]+15}" stroke="{C_DB9B}" stroke-width="3" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="340" y="205" class="vl" font-size="7">→VCA</text>\n'
    
    # 5. Control signals (dashed)
    svg += f'<path d="M520,{pico_y} L700,{pico_y} L700,{exp_y["Slew"]} L820,{exp_y["Slew"]}" stroke="{C_PICO}" stroke-width="2" stroke-dasharray="5,3" fill="none"/>\n'
    svg += f'<text x="700" y="395" class="vl" font-size="7">GPIO</text>\n'
    
    svg += f'<path d="M520,{touch_y} L720,{touch_y} L720,{exp_y["Atten"]} L820,{exp_y["Atten"]}" stroke="{C_TOUCH}" stroke-width="2" stroke-dasharray="5,3" fill="none"/>\n'
    svg += f'<text x="720" y="415" class="vl" font-size="7">Touch</text>\n'
    
    # Legend
    svg += '<rect x="50" y="540" width="900" height="140" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>\n'
    svg += '<text x="500" y="565" class="v" font-weight="bold" font-size="10">Signal Flow</text>\n'
    
    legend_items = [
        (C_MICRO, "MicroBrute → DB-9 A"),
        (C_DB9A, "DB-9 A → Expander (audio/CV)"),
        (C_EXPAND, "Expander → DB-9 B (CV/gates)"),
        (C_DB9B, "DB-9 B → MicroBrute (modulation)"),
    ]
    
    for i, (color, txt) in enumerate(legend_items):
        y = 590 + i * 20
        svg += f'<rect x="70" y="{y-8}" width="20" height="14" fill="{color}" stroke="#333" rx="2"/>\n'
        svg += f'<text x="100" y="{y+3}" class="v" font-size="9">{txt}</text>\n'
    
    svg += '</svg>'
    return svg


def cv_control_flow_final():
    """CV Control Flow - Clean bus-style routing."""
    width, height = 1000, 550
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#333"/>
  </marker>
</defs>
<style>
  .t {{ font: bold 15px sans-serif; fill: #1a1a1a; }}
  .st {{ font: 11px sans-serif; fill: #555; }}
  .l {{ font: bold 10px sans-serif; fill: #FFF; text-anchor: middle; }}
  .v {{ font: 9px sans-serif; fill: #333; }}
  .vl {{ font: 8px sans-serif; fill: #666; }}
</style>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="500" y="25" class="t" text-anchor="middle">CV Control Flow</text>
<text x="500" y="45" class="st" text-anchor="middle">Modulation Matrix</text>
'''
    
    C_MOD = "#9C27B0"
    C_DEST = "#2196F3"
    C_INPUT = "#FF9800"
    C_EXPAND = "#4CAF50"
    
    # Headers
    svg += '<text x="100" y="70" class="v" font-weight="bold" font-size="10" fill="#333">SOURCES</text>\n'
    svg += '<text x="480" y="70" class="v" font-weight="bold" font-size="10" fill="#333">DESTINATIONS</text>\n'
    svg += '<text x="850" y="70" class="v" font-weight="bold" font-size="10" fill="#333">EXTERNAL INPUTS</text>\n'
    
    # Sources (left)
    sources = [
        ("LFO", 85, C_MOD),
        ("Envelope", 120, C_MOD),
        ("Pitch CV", 155, C_MOD),
        ("Mod Wheel", 190, C_MOD),
        ("Exp LFO", 240, C_EXPAND),
        ("Exp S&H", 275, C_EXPAND),
    ]
    
    src_y = {}
    for name, y, color in sources:
        svg += f'<rect x="50" y="{y}" width="85" height="28" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="92" y="{y+18}" class="l" font-size="9">{name}</text>\n'
        src_y[name] = y + 14
    
    # Destinations (center)
    dests = [
        ("Pitch", 85, C_DEST),
        ("Filter", 120, C_DEST),
        ("Resonance", 155, C_DEST),
        ("VCA", 190, C_DEST),
        ("PWM", 225, C_DEST),
        ("Metalizer", 260, C_DEST),
    ]
    
    dst_y = {}
    for name, y, color in dests:
        svg += f'<rect x="450" y="{y}" width="85" height="28" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="492" y="{y+18}" class="l" font-size="9">{name}</text>\n'
        dst_y[name] = y + 14
    
    # External inputs (right)
    inputs = [
        ("Filter CV", 85, C_INPUT),
        ("VCA CV", 120, C_INPUT),
        ("Res CV", 155, C_INPUT),
        ("Gate In", 190, C_INPUT),
        ("Sync", 225, C_INPUT),
    ]
    
    inp_y = {}
    for name, y, color in inputs:
        svg += f'<rect x="820" y="{y}" width="100" height="28" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="870" y="{y+18}" class="l" font-size="9">{name}</text>\n'
        inp_y[name] = y + 14
    
    # MODULATION BUS - vertical channels for each source
    # Each source gets its own vertical "bus" line that branches to destinations
    
    # LFO bus (leftmost channel)
    svg += f'<line x1="180" y1="{src_y["LFO"]}" x2="180" y2="99" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="180" y1="99" x2="450" y2="99" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'  # To Pitch
    svg += f'<text x="210" y="95" class="vl" font-size="6">LFO→Pitch</text>\n'
    
    svg += f'<line x1="185" y1="{src_y["LFO"]}" x2="185" y2="134" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="185" y1="134" x2="450" y2="134" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'  # To Filter
    svg += f'<text x="290" y="130" class="vl" font-size="6">LFO→Filter</text>\n'
    
    svg += f'<line x1="190" y1="{src_y["LFO"]}" x2="190" y2="204" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="190" y1="204" x2="450" y2="204" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'  # To VCA
    svg += f'<text x="290" y="200" class="vl" font-size="6">LFO→VCA</text>\n'
    
    # Envelope bus
    svg += f'<line x1="195" y1="{src_y["Envelope"]}" x2="195" y2="139" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="195" y1="139" x2="450" y2="139" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="290" y="148" class="vl" font-size="6">Env→Filter</text>\n'
    
    svg += f'<line x1="200" y1="{src_y["Envelope"]}" x2="200" y2="209" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="200" y1="209" x2="450" y2="209" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="290" y="217" class="vl" font-size="6">Env→VCA</text>\n'
    
    # Pitch CV bus
    svg += f'<line x1="205" y1="{src_y["Pitch CV"]}" x2="205" y2="104" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="205" y1="104" x2="450" y2="104" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="290" y="100" class="vl" font-size="6">Pitch→VCO</text>\n'
    
    # Mod Wheel bus
    svg += f'<line x1="210" y1="{src_y["Mod Wheel"]}" x2="210" y2="109" stroke="{C_MOD}" stroke-width="2"/>\n'
    svg += f'<line x1="210" y1="109" x2="450" y2="109" stroke="{C_MOD}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="290" y="117" class="vl" font-size="6">Wheel→Pitch</text>\n'
    
    # Exp LFO bus
    svg += f'<line x1="180" y1="{src_y["Exp LFO"]}" x2="180" y2="169" stroke="{C_EXPAND}" stroke-width="2"/>\n'
    svg += f'<line x1="180" y1="169" x2="450" y2="169" stroke="{C_EXPAND}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="260" y="165" class="vl" font-size="6">ExpLFO→Res</text>\n'
    
    # Exp S&H bus
    svg += f'<line x1="185" y1="{src_y["Exp S&H"]}" x2="185" y2="174" stroke="{C_EXPAND}" stroke-width="2"/>\n'
    svg += f'<line x1="185" y1="174" x2="450" y2="174" stroke="{C_EXPAND}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="260" y="182" class="vl" font-size="6">ExpS&H→Res</text>\n'
    
    # EXTERNAL INPUTS - from right side
    # Filter CV
    svg += f'<line x1="820" y1="{inp_y["Filter CV"]}" x2="600" y2="{inp_y["Filter CV"]}" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="600" y1="{inp_y["Filter CV"]}" x2="600" y2="139" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="600" y1="139" x2="535" y2="139" stroke="{C_INPUT}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="670" y="135" class="vl" font-size="6">Ext→Filter</text>\n'
    
    # VCA CV
    svg += f'<line x1="820" y1="{inp_y["VCA CV"]}" x2="620" y2="{inp_y["VCA CV"]}" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="620" y1="{inp_y["VCA CV"]}" x2="620" y2="209" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="620" y1="209" x2="535" y2="209" stroke="{C_INPUT}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="670" y="205" class="vl" font-size="6">Ext→VCA</text>\n'
    
    # Res CV
    svg += f'<line x1="820" y1="{inp_y["Res CV"]}" x2="640" y2="{inp_y["Res CV"]}" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="640" y1="{inp_y["Res CV"]}" x2="640" y2="174" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="640" y1="174" x2="535" y2="174" stroke="{C_INPUT}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="670" y="170" class="vl" font-size="6">Ext→Res</text>\n'
    
    # Gate In
    svg += f'<line x1="820" y1="{inp_y["Gate In"]}" x2="660" y2="{inp_y["Gate In"]}" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="660" y1="{inp_y["Gate In"]}" x2="660" y2="239" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="660" y1="239" x2="535" y2="239" stroke="{C_INPUT}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="720" y="235" class="vl" font-size="6">Gate→PWM</text>\n'
    
    # Sync
    svg += f'<line x1="820" y1="{inp_y["Sync"]}" x2="680" y2="{inp_y["Sync"]}" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="680" y1="{inp_y["Sync"]}" x2="680" y2="274" stroke="{C_INPUT}" stroke-width="2"/>\n'
    svg += f'<line x1="680" y1="274" x2="535" y2="274" stroke="{C_INPUT}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="720" y="270" class="vl" font-size="6">Sync→Metal</text>\n'
    
    # Notes
    svg += '<rect x="50" y="330" width="900" height="200" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>\n'
    svg += '<text x="500" y="355" class="v" font-weight="bold" font-size="10" fill="#E65100">CV Routing Notes</text>\n'
    
    notes = [
        "• LFO, Envelope, Pitch CV, Mod Wheel are internal MicroBrute sources",
        "• Exp LFO and Exp S&H are from the Expander module",
        "• Multiple CV sources sum at destinations (e.g., Pitch = Keyboard + LFO + Wheel)",
        "• External inputs (Filter CV, VCA CV, etc.) come from DB-9 B",
        "• All external CV inputs protected with 100kΩ series resistor + clamping diodes",
    ]
    
    for i, note in enumerate(notes):
        svg += f'<text x="70" y="{380 + i*22}" class="v" font-size="9">{note}</text>\n'
    
    svg += '</svg>'
    return svg


def cv_input_protection_final():
    """CV Input Protection - Organized layout."""
    width, height = 600, 450
    
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#333"/>
  </marker>
</defs>
<style>
  .t {{ font: bold 14px sans-serif; fill: #1a1a1a; }}
  .st {{ font: 10px sans-serif; fill: #555; }}
  .l {{ font: bold 10px sans-serif; fill: #1a1a1a; }}
  .v {{ font: 9px sans-serif; fill: #333; }}
  .vl {{ font: 8px sans-serif; fill: #666; }}
</style>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="300" y="25" class="t" text-anchor="middle">CV Input Protection</text>
<text x="300" y="42" class="st" text-anchor="middle">BAT54S Schottky Clamping for DB-9 B Inputs</text>
'''
    
    # Input jack (left)
    svg += '<circle cx="60" cy="200" r="6" fill="none" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<text x="60" y="225" class="l" text-anchor="middle" font-size="9">CV IN</text>\n'
    svg += '<text x="60" y="238" class="vl" text-anchor="middle" font-size="7">±12V max</text>\n'
    
    # Series resistor R1 (input protection)
    svg += '<line x1="66" y1="200" x2="120" y2="200" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<path d="M120,200 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,0" stroke="#CD853F" stroke-width="2" fill="none"/>\n'
    svg += '<text x="145" y="190" class="l" text-anchor="middle" font-size="8">R1</text>\n'
    svg += '<text x="145" y="215" class="vl" text-anchor="middle" font-size="7">100kΩ</text>\n'
    svg += '<text x="145" y="225" class="vl" text-anchor="middle" font-size="7">(protection)</text>\n'
    
    # Main node
    svg += '<line x1="170" y1="200" x2="200" y2="200" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<circle cx="200" cy="200" r="3" fill="#0066CC"/>\n'
    
    # To attenuator pot
    svg += '<line x1="200" y1="200" x2="240" y2="200" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<path d="M240,200 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,0" stroke="#CD853F" stroke-width="2" fill="none"/>\n'
    svg += '<text x="265" y="190" class="l" text-anchor="middle" font-size="8">ATTEN</text>\n'
    svg += '<text x="265" y="215" class="vl" text-anchor="middle" font-size="7">100kΩ</text>\n'
    
    # To series resistor Rs
    svg += '<line x1="290" y1="200" x2="320" y2="200" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<path d="M320,200 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,-5 l5,5 l5,0" stroke="#CD853F" stroke-width="2" fill="none"/>\n'
    svg += '<text x="345" y="190" class="l" text-anchor="middle" font-size="8">Rs</text>\n'
    svg += '<text x="345" y="215" class="vl" text-anchor="middle" font-size="7">10kΩ</text>\n'
    
    # Node before clamping
    svg += '<line x1="370" y1="200" x2="400" y2="200" stroke="#333" stroke-width="1.5"/>\n'
    svg += '<circle cx="400" cy="200" r="3" fill="#0066CC"/>\n'
    
    # To MicroBrute (right)
    svg += '<line x1="400" y1="200" x2="520" y2="200" stroke="#333" stroke-width="1.5" marker-end="url(#arr)"/>\n'
    svg += '<text x="460" y="190" class="l" text-anchor="middle" font-size="8">To MicroBrute</text>\n'
    svg += '<text x="460" y="215" class="vl" text-anchor="middle" font-size="7">CV input node</text>\n'
    
    # CLAMPING DIODES - arranged vertically
    # Top diode (to +5V)
    svg += '<line x1="400" y1="200" x2="400" y2="120" stroke="#D44" stroke-width="1.5"/>\n'
    svg += '<line x1="400" y1="120" x2="380" y2="120" stroke="#D44" stroke-width="1.5"/>\n'
    # Diode symbol pointing up
    svg += '<polygon points="380,110 380,130 400,120" fill="none" stroke="#D44" stroke-width="1.5"/>\n'
    svg += '<line x1="380" y1="110" x2="380" y2="130" stroke="#D44" stroke-width="1.5"/>\n'
    # To +5V
    svg += '<line x1="380" y1="110" x2="380" y2="80" stroke="#D44" stroke-width="1.5"/>\n'
    svg += '<line x1="370" y1="80" x2="390" y2="80" stroke="#D44" stroke-width="2"/>\n'
    svg += '<text x="400" y="75" class="vl" fill="#D44" font-size="8">+5V</text>\n'
    svg += '<text x="415" y="125" class="vl" fill="#D44" font-size="7">BAT54S</text>\n'
    
    # Bottom diode (to GND)
    svg += '<line x1="400" y1="200" x2="400" y2="280" stroke="#44D" stroke-width="1.5"/>\n'
    svg += '<line x1="400" y1="280" x2="420" y2="280" stroke="#44D" stroke-width="1.5"/>\n'
    # Diode symbol pointing down
    svg += '<polygon points="420,270 420,290 400,280" fill="none" stroke="#44D" stroke-width="1.5"/>\n'
    svg += '<line x1="420" y1="270" x2="420" y2="290" stroke="#44D" stroke-width="1.5"/>\n'
    # To GND
    svg += '<line x1="420" y1="290" x2="420" y2="320" stroke="#44D" stroke-width="1.5"/>\n'
    svg += '<line x1="410" y1="320" x2="430" y2="320" stroke="#44D" stroke-width="2"/>\n'
    svg += '<line x1="414" y1="324" x2="426" y2="324" stroke="#44D" stroke-width="1.5"/>\n'
    svg += '<text x="445" y="325" class="vl" fill="#44D" font-size="8">GND</text>\n'
    
    # Notes box (compact)
    svg += '<rect x="50" y="360" width="500" height="80" fill="#E3F2FD" stroke="#2196F3" stroke-width="1" rx="4"/>\n'
    svg += '<text x="300" y="380" class="l" text-anchor="middle" font-size="9" fill="#0D47A1">Circuit Operation</text>\n'
    svg += '<text x="70" y="400" class="v" font-size="8">• 100kΩ input resistor limits current during faults</text>\n'
    svg += '<text x="70" y="415" class="v" font-size="8">• BAT54S dual Schottky clamps to +5V/GND (actually ~0.3V/5.3V)</text>\n'
    svg += '<text x="70" y="430" class="v" font-size="8">• 10kΩ series resistor + attenuator form voltage divider</text>\n'
    
    svg += '</svg>'
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    diagrams = [
        ("system_architecture_block", system_architecture_final),
        ("cv_control_flow", cv_control_flow_final),
        ("cv_input_protection_diagram", cv_input_protection_final),
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
