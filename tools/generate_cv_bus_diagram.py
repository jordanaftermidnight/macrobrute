#!/usr/bin/env python3
"""Generate CV Control Flow with clean bus-style routing."""

import os


def cv_control_flow_bus():
    """CV Control Flow - Clean bus architecture like System Architecture."""
    width, height = 1000, 600
    
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
  .bus-label {{ font: bold 9px sans-serif; fill: #333; text-anchor: middle; }}
</style>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="500" y="25" class="t" text-anchor="middle">CV Control Flow</text>
<text x="500" y="45" class="st" text-anchor="middle">Modulation Matrix - Grouped Signal Buses</text>
'''
    
    C_MOD = "#9C27B0"
    C_DEST = "#2196F3"
    C_INPUT = "#FF9800"
    C_EXPAND = "#4CAF50"
    
    # Headers
    svg += '<text x="120" y="75" class="v" font-weight="bold" font-size="10" fill="#333">SOURCES</text>\n'
    svg += '<text x="500" y="75" class="v" font-weight="bold" font-size="10" fill="#333">DESTINATIONS</text>\n'
    svg += '<text x="850" y="75" class="v" font-weight="bold" font-size="10" fill="#333">EXTERNAL INPUTS</text>\n'
    
    # === SOURCES - Grouped by Function ===
    
    # Internal Modulation Bus (LFO + Envelope + Mod Wheel)
    svg += f'<rect x="50" y="85" width="110" height="100" fill="{C_MOD}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="110" class="l" font-size="10">MODULATION</text>\n'
    svg += f'<text x="105" y="130" class="l" font-size="7">LFO (0-5V △)</text>\n'
    svg += f'<text x="105" y="145" class="l" font-size="7">Envelope (ADSR)</text>\n'
    svg += f'<text x="105" y="160" class="l" font-size="7">Mod Wheel (0-5V)</text>\n'
    svg += f'<text x="105" y="178" class="l" font-size="6">→ Pitch, Filter, VCA</text>\n'
    mod_y = 135
    
    # Pitch CV Bus
    svg += f'<rect x="50" y="200" width="110" height="60" fill="{C_MOD}" stroke="#1a1a1a" stroke-width="2" rx="4" opacity="0.8"/>\n'
    svg += f'<text x="105" y="225" class="l" font-size="10">PITCH CV</text>\n'
    svg += f'<text x="105" y="242" class="l" font-size="7">1V/octave</text>\n'
    svg += f'<text x="105" y="255" class="l" font-size="6">→ Pitch (VCO)</text>\n'
    pitch_y = 230
    
    # Expander Modulation Bus
    svg += f'<rect x="50" y="280" width="110" height="80" fill="{C_EXPAND}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="305" class="l" font-size="10">EXPANDER MOD</text>\n'
    svg += f'<text x="105" y="325" class="l" font-size="7">Exp LFO (Free)</text>\n'
    svg += f'<text x="105" y="342" class="l" font-size="7">Exp S&H</text>\n'
    svg += f'<text x="105" y="355" class="l" font-size="6">→ Resonance</text>\n'
    exp_y = 320
    
    # === DESTINATIONS (Center) ===
    
    dests = [
        ("Pitch", "VCO Freq", 95, C_DEST),
        ("Filter", "Cutoff", 145, C_DEST),
        ("Resonance", "Peak", 195, C_DEST),
        ("VCA", "Amplitude", 245, C_DEST),
        ("PWM", "Width", 295, C_DEST),
        ("Metalizer", "Harm", 345, C_DEST),
    ]
    
    dst_y = {}
    for name, sub, y, color in dests:
        svg += f'<rect x="450" y="{y}" width="90" height="38" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="495" y="{y+16}" class="l" font-size="10">{name}</text>\n'
        svg += f'<text x="495" y="{y+30}" class="l" font-size="7">{sub}</text>\n'
        dst_y[name] = y + 19
    
    # === EXTERNAL INPUTS (Right) ===
    
    inputs = [
        ("Filter CV", "85", C_INPUT),
        ("VCA CV", "130", C_INPUT),
        ("Res CV", "175", C_INPUT),
        ("Gate In", "220", C_INPUT),
        ("Sync", "265", C_INPUT),
    ]
    
    inp_y = {}
    for name, y_str, color in inputs:
        y = int(y_str)
        svg += f'<rect x="820" y="{y}" width="100" height="35" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="870" y="{y+15}" class="l" font-size="9">{name}</text>\n'
        svg += f'<text x="870" y="{y+28}" class="l" font-size="7">DB-9 B</text>\n'
        inp_y[name] = y + 17
    
    # === BUS CONNECTIONS - Clean Grouped Routing ===
    
    # 1. MODULATION BUS (Purple) - LFO/Env/Wheel → Multiple Destinations
    # Main modulation bus line
    svg += f'<line x1="160" y1="{mod_y}" x2="280" y2="{mod_y}" stroke="{C_MOD}" stroke-width="4"/>\n'
    svg += f'<text x="220" y="{mod_y-10}" class="bus-label" font-size="7">Modulation Bus</text>\n'
    svg += f'<text x="220" y="{mod_y+12}" class="vl" font-size="6">LFO, Env, Wheel</text>\n'
    
    # Bus branches to destinations with clean routing
    # To Pitch
    svg += f'<line x1="280" y1="{mod_y}" x2="280" y2="{dst_y["Pitch"]}" stroke="{C_MOD}" stroke-width="3"/>\n'
    svg += f'<line x1="280" y1="{dst_y["Pitch"]}" x2="450" y2="{dst_y["Pitch"]}" stroke="{C_MOD}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="320" y="{dst_y["Pitch"]-8}" class="vl" font-size="6">LFO→Pitch</text>\n'
    svg += f'<text x="320" y="{dst_y["Pitch"]+10}" class="vl" font-size="6">Wheel→Pitch</text>\n'
    
    # To Filter
    svg += f'<line x1="285" y1="{mod_y}" x2="285" y2="{dst_y["Filter"]}" stroke="{C_MOD}" stroke-width="3"/>\n'
    svg += f'<line x1="285" y1="{dst_y["Filter"]}" x2="450" y2="{dst_y["Filter"]}" stroke="{C_MOD}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="325" y="{dst_y["Filter"]-8}" class="vl" font-size="6">LFO→Filter</text>\n'
    svg += f'<text x="325" y="{dst_y["Filter"]+10}" class="vl" font-size="6">Env→Filter</text>\n'
    
    # To VCA
    svg += f'<line x1="290" y1="{mod_y}" x2="290" y2="{dst_y["VCA"]}" stroke="{C_MOD}" stroke-width="3"/>\n'
    svg += f'<line x1="290" y1="{dst_y["VCA"]}" x2="450" y2="{dst_y["VCA"]}" stroke="{C_MOD}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="330" y="{dst_y["VCA"]-8}" class="vl" font-size="6">LFO→VCA</text>\n'
    svg += f'<text x="330" y="{dst_y["VCA"]+10}" class="vl" font-size="6">Env→VCA</text>\n'
    
    # 2. PITCH CV BUS - Direct to Pitch only
    svg += f'<line x1="160" y1="{pitch_y}" x2="380" y2="{pitch_y}" stroke="{C_MOD}" stroke-width="3" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="380" y1="{pitch_y}" x2="380" y2="{dst_y["Pitch"]}" stroke="{C_MOD}" stroke-width="3" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="380" y1="{dst_y["Pitch"]}" x2="450" y2="{dst_y["Pitch"]}" stroke="{C_MOD}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="270" y="{pitch_y-8}" class="vl" font-size="6">Pitch CV→VCO</text>\n'
    
    # 3. EXPANDER MOD BUS (Green) - To Resonance
    svg += f'<line x1="160" y1="{exp_y}" x2="300" y2="{exp_y}" stroke="{C_EXPAND}" stroke-width="3"/>\n'
    svg += f'<text x="230" y="{exp_y-8}" class="vl" font-size="7">Expander Mod</text>\n'
    svg += f'<text x="230" y="{exp_y+10}" class="vl" font-size="6">ExpLFO, ExpS&H</text>\n'
    svg += f'<line x1="300" y1="{exp_y}" x2="300" y2="{dst_y["Resonance"]}" stroke="{C_EXPAND}" stroke-width="3"/>\n'
    svg += f'<line x1="300" y1="{dst_y["Resonance"]}" x2="450" y2="{dst_y["Resonance"]}" stroke="{C_EXPAND}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="340" y="{dst_y["Resonance"]-8}" class="vl" font-size="6">Exp→Res</text>\n'
    
    # 4. EXTERNAL INPUTS BUS (Orange) - From DB-9 B
    # Filter CV
    svg += f'<line x1="820" y1="{inp_y["Filter CV"]}" x2="680" y2="{inp_y["Filter CV"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="680" y1="{inp_y["Filter CV"]}" x2="680" y2="{dst_y["Filter"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="680" y1="{dst_y["Filter"]}" x2="540" y2="{dst_y["Filter"]}" stroke="{C_INPUT}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="750" y="{dst_y["Filter"]-10}" class="vl" font-size="6">Ext→Filter</text>\n'
    
    # VCA CV
    svg += f'<line x1="820" y1="{inp_y["VCA CV"]}" x2="700" y2="{inp_y["VCA CV"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="700" y1="{inp_y["VCA CV"]}" x2="700" y2="{dst_y["VCA"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="700" y1="{dst_y["VCA"]}" x2="540" y2="{dst_y["VCA"]}" stroke="{C_INPUT}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="760" y="{dst_y["VCA"]-10}" class="vl" font-size="6">Ext→VCA</text>\n'
    
    # Res CV
    svg += f'<line x1="820" y1="{inp_y["Res CV"]}" x2="720" y2="{inp_y["Res CV"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="720" y1="{inp_y["Res CV"]}" x2="720" y2="{dst_y["Resonance"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="720" y1="{dst_y["Resonance"]}" x2="540" y2="{dst_y["Resonance"]}" stroke="{C_INPUT}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="770" y="{dst_y["Resonance"]+15}" class="vl" font-size="6">Ext→Res</text>\n'
    
    # Gate In → PWM
    svg += f'<line x1="820" y1="{inp_y["Gate In"]}" x2="740" y2="{inp_y["Gate In"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="740" y1="{inp_y["Gate In"]}" x2="740" y2="{dst_y["PWM"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="740" y1="{dst_y["PWM"]}" x2="540" y2="{dst_y["PWM"]}" stroke="{C_INPUT}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="780" y="{dst_y["PWM"]-10}" class="vl" font-size="6">Gate→PWM</text>\n'
    
    # Sync → Metalizer
    svg += f'<line x1="820" y1="{inp_y["Sync"]}" x2="760" y2="{inp_y["Sync"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="760" y1="{inp_y["Sync"]}" x2="760" y2="{dst_y["Metalizer"]}" stroke="{C_INPUT}" stroke-width="3"/>\n'
    svg += f'<line x1="760" y1="{dst_y["Metalizer"]}" x2="540" y2="{dst_y["Metalizer"]}" stroke="{C_INPUT}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="800" y="{dst_y["Metalizer"]-10}" class="vl" font-size="6">Sync→Metal</text>\n'
    
    # === NOTES ===
    svg += '<rect x="50" y="410" width="900" height="170" fill="#FFF3E0" stroke="#FF9800" stroke-width="1" rx="4"/>\n'
    svg += '<text x="500" y="435" class="v" font-weight="bold" font-size="10" fill="#E65100">CV Routing Notes</text>\n'
    
    notes = [
        ("Modulation Bus:", "LFO + Envelope + Mod Wheel all route to Pitch, Filter, VCA (summing at destination)", 455),
        ("Pitch CV:", "Keyboard pitch + external pitch sources sum at VCO frequency input", 480),
        ("Expander Mod:", "Free-running LFO and S&H from expander module route to Resonance", 505),
        ("External CVs:", "From DB-9 B: Filter CV, VCA CV, Res CV go directly to their destinations", 530),
        ("Gate/Sync:", "Gate In → PWM, Sync → Metalizer (for hard sync effects)", 555),
    ]
    
    for label, txt, y in notes:
        svg += f'<text x="70" y="{y}" class="v" font-size="8" fill="#E65100">{label}</text>\n'
        svg += f'<text x="155" y="{y}" class="v" font-size="8">{txt}</text>\n'
    
    svg += '</svg>'
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    try:
        svg = cv_control_flow_bus()
        with open(f"{out}/cv_control_flow.svg", 'w') as f:
            f.write(svg)
        print("Generated: cv_control_flow.svg (Bus style)")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
