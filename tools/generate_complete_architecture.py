#!/usr/bin/env python3
"""Generate complete System Architecture with all DB-9 signals."""

import os


def system_architecture_complete():
    """Complete System Architecture with all DB-9 A and DB-9 B signals."""
    width, height = 1100, 800
    
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
  .pin {{ font: 7px sans-serif; fill: gold; text-anchor: middle; }}
</style>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="550" y="25" class="t" text-anchor="middle">MACROBRUTE System Architecture (Complete)</text>
<text x="550" y="45" class="st" text-anchor="middle">All DB-9 A Outputs + DB-9 B Inputs/Power</text>
'''
    
    C_MICRO = "#2196F3"
    C_DB9A = "#FF9800"
    C_DB9B = "#FF5722"
    C_PICO = "#9C27B0"
    C_TOUCH = "#673AB7"
    C_EXPAND = "#4CAF50"
    C_POWER = "#CC0000"
    
    # Section headers
    svg += '<text x="120" y="70" class="v" font-weight="bold" font-size="11" fill="#333">MICROBRUTE</text>\n'
    svg += '<text x="500" y="70" class="v" font-weight="bold" font-size="11" fill="#333">DB-9 INTERFACE</text>\n'
    svg += '<text x="900" y="70" class="v" font-weight="bold" font-size="11" fill="#333">EXPANDER</text>\n'
    
    # === MICROBRUTE CORE (Left Column) ===
    micro_blocks = [
        ("VCO", "Osc", 85, C_MICRO),
        ("VCF", "Filter", 135, C_MICRO),
        ("VCA", "Amp", 185, C_MICRO),
        ("LFO", "LFO", 235, C_MICRO),
        ("ENV", "Envelope", 285, C_MICRO),
    ]
    
    micro_y = {}
    for name, sub, y, color in micro_blocks:
        svg += f'<rect x="50" y="{y}" width="110" height="40" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="105" y="{y+17}" class="l" font-size="10">{name}</text>\n'
        svg += f'<text x="105" y="{y+32}" class="l" font-size="8">{sub}</text>\n'
        micro_y[name] = y + 20
    
    # === DB-9 A OUTPUTS (Center-Top) ===
    # Box for DB-9 A with pin listing
    svg += f'<rect x="380" y="80" width="160" height="240" fill="{C_DB9A}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="100" class="l" font-size="12">DB-9 A</text>\n'
    svg += f'<text x="460" y="115" class="l" font-size="9">OUTPUTS →</text>\n'
    
    # DB-9 A Pins (left to right: 5,4,3,2,1 on top, 9,8,7,6 on bottom)
    db9a_pins = [
        ("5:Mix", 130), ("4:LFO", 150), ("3:Env", 170), ("2:Pitch", 190), ("1:Gate", 210),
        ("9:GND", 250), ("8:Sqr", 270), ("7:Saw", 290), ("6:VCF", 310),
    ]
    for pin, y in db9a_pins:
        svg += f'<text x="460" y="{y}" class="pin" font-size="7">{pin}</text>\n'
    
    # === DB-9 B INPUTS + POWER (Center-Bottom) ===
    svg += f'<rect x="380" y="340" width="160" height="280" fill="{C_DB9B}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="360" class="l" font-size="12">DB-9 B</text>\n'
    svg += f'<text x="460" y="375" class="l" font-size="9">← INPUTS</text>\n'
    
    # DB-9 B Pins
    db9b_pins = [
        ("1:Filt CV", 400), ("2:VCA CV", 420), ("3:Res", 440), ("4:Sync", 460), ("5:Gate In", 480),
        ("6:Ext Audio", 510), ("7:+12V", 540), ("8:-12V", 560), ("9:GND", 580),
    ]
    for pin, y in db9b_pins:
        color = "#FF6B6B" if "12V" in pin else "gold"
        svg += f'<text x="460" y="{y}" class="pin" font-size="7" fill="{color}">{pin}</text>\n'
    
    # === CONTROL SECTION (Center, below DB-9) ===
    svg += f'<rect x="400" y="640" width="120" height="50" fill="{C_PICO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="665" class="l" font-size="10">Pico W</text>\n'
    svg += f'<text x="460" y="680" class="l" font-size="8">Control</text>\n'
    pico_y = 665
    
    svg += f'<rect x="400" y="705" width="120" height="40" fill="{C_TOUCH}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="460" y="723" class="l" font-size="10">Touch</text>\n'
    svg += f'<text x="460" y="737" class="l" font-size="8">4-Point</text>\n'
    touch_y = 725
    
    # === EXPANDER MODULES (Right Column) ===
    exp_blocks = [
        ("Noise", "Gen", 85, C_EXPAND),
        ("LFO", "Free", 135, C_EXPAND),
        ("S&H", "Sample", 185, C_EXPAND),
        ("Clock", "Div /2/4/8", 235, C_EXPAND),
        ("Slew", "Glide", 285, C_EXPAND),
        ("Atten", "CV Scale", 335, C_EXPAND),
    ]
    
    exp_y = {}
    for name, sub, y, color in exp_blocks:
        svg += f'<rect x="920" y="{y}" width="110" height="40" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
        svg += f'<text x="975" y="{y+17}" class="l" font-size="10">{name}</text>\n'
        svg += f'<text x="975" y="{y+32}" class="l" font-size="8">{sub}</text>\n'
        exp_y[name] = y + 20
    
    # === ALL CONNECTIONS WITH ELBOW ROUTING ===
    
    # DB-9 A OUTPUTS (MicroBrute → DB-9 A)
    # Pin 7: Saw
    svg += f'<path d="M160,{micro_y["VCO"]} L270,{micro_y["VCO"]} L270,290 L380,290" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="220" y="285" class="vl" font-size="6">Saw→P7</text>\n'
    
    # Pin 8: Square
    svg += f'<path d="M160,{micro_y["VCO"]} L275,{micro_y["VCO"]} L275,270 L380,270" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="280" y="265" class="vl" font-size="6">Sqr→P8</text>\n'
    
    # Pin 6: VCF
    svg += f'<path d="M160,{micro_y["VCF"]} L280,{micro_y["VCF"]} L280,310 L380,310" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="240" y="305" class="vl" font-size="6">VCF→P6</text>\n'
    
    # Pin 5: Mix
    svg += f'<path d="M160,{micro_y["VCA"]} L285,{micro_y["VCA"]} L285,130 L380,130" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="240" y="125" class="vl" font-size="6">Mix→P5</text>\n'
    
    # Pin 4: LFO
    svg += f'<path d="M160,{micro_y["LFO"]} L290,{micro_y["LFO"]} L290,150 L380,150" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="245" y="145" class="vl" font-size="6">LFO→P4</text>\n'
    
    # Pin 3: Envelope
    svg += f'<path d="M160,{micro_y["ENV"]} L295,{micro_y["ENV"]} L295,170 L380,170" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="250" y="165" class="vl" font-size="6">Env→P3</text>\n'
    
    # Pin 2: Pitch CV
    svg += f'<path d="M160,{micro_y["VCO"]} L300,{micro_y["VCO"]} L300,190 L380,190" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="255" y="185" class="vl" font-size="6">Pitch→P2</text>\n'
    
    # Pin 1: Gate
    svg += f'<path d="M160,{micro_y["ENV"]} L305,{micro_y["ENV"]} L305,210 L380,210" stroke="{C_MICRO}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="260" y="205" class="vl" font-size="6">Gate→P1</text>\n'
    
    # DB-9 A → Expander (Audio/CV distribution)
    # Pin 7 (Saw) to Noise Gen
    svg += f'<path d="M540,290 L730,290 L730,{exp_y["Noise"]} L920,{exp_y["Noise"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="730" y="200" class="vl" font-size="6">Saw→Noise</text>\n'
    
    # Pin 4 (LFO) to Expander LFO
    svg += f'<path d="M540,150 L710,150 L710,{exp_y["LFO"]} L920,{exp_y["LFO"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="710" y="145" class="vl" font-size="6">LFO→LFO</text>\n'
    
    # Pin 3 (Env) to S&H Clock
    svg += f'<path d="M540,170 L700,170 L700,{exp_y["S&H"]} L920,{exp_y["S&H"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="700" y="180" class="vl" font-size="6">Env→S&H</text>\n'
    
    # Pin 2 (Pitch) to Clock (Sync)
    svg += f'<path d="M540,190 L690,190 L690,{exp_y["Clock"]} L920,{exp_y["Clock"]}" stroke="{C_DB9A}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="690" y="215" class="vl" font-size="6">Pitch→Clock</text>\n'
    
    # DB-9 B INPUTS (Expander → MicroBrute)
    # Pin 1: Filter CV from LFO
    svg += f'<path d="M920,{exp_y["LFO"]} L750,{exp_y["LFO"]} L750,400 L540,400" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="750" y="300" class="vl" font-size="6">LFO→FiltCV</text>\n'
    
    # Pin 2: VCA CV from S&H
    svg += f'<path d="M920,{exp_y["S&H"]} L760,{exp_y["S&H"]} L760,420 L540,420" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="760" y="310" class="vl" font-size="6">S&H→VCACV</text>\n'
    
    # Pin 3: Resonance from Clock
    svg += f'<path d="M920,{exp_y["Clock"]} L770,{exp_y["Clock"]} L770,440 L540,440" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="770" y="340" class="vl" font-size="6">Clock→Res</text>\n'
    
    # Pin 4: Sync from Clock
    svg += f'<path d="M920,{exp_y["Clock"]} L780,{exp_y["Clock"]} L780,460 L540,460" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="780" y="425" class="vl" font-size="6">Clock→Sync</text>\n'
    
    # Pin 5: Gate In from Clock
    svg += f'<path d="M920,{exp_y["Clock"]} L790,{exp_y["Clock"]} L790,480 L540,480" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="790" y="445" class="vl" font-size="6">Clock→GateIn</text>\n'
    
    # Pin 6: Ext Audio from Noise
    svg += f'<path d="M920,{exp_y["Noise"]} L800,{exp_y["Noise"]} L800,510 L540,510" stroke="{C_EXPAND}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="800" y="145" class="vl" font-size="6">Noise→ExtAudio</text>\n'
    
    # DB-9 B → MicroBrute (Modulation paths)
    # Filter CV to VCF
    svg += f'<path d="M380,400 L320,400 L320,{micro_y["VCF"]+10} L160,{micro_y["VCF"]+10}" stroke="{C_DB9B}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="320" y="275" class="vl" font-size="6">→Filter</text>\n'
    
    # VCA CV to VCA
    svg += f'<path d="M380,420 L330,420 L330,{micro_y["VCA"]+10} L160,{micro_y["VCA"]+10}" stroke="{C_DB9B}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="330" y="325" class="vl" font-size="6">→VCA</text>\n'
    
    # Resonance to VCF
    svg += f'<path d="M380,440 L340,440 L340,{micro_y["VCF"]+20} L160,{micro_y["VCF"]+20}" stroke="{C_DB9B}" stroke-width="2" fill="none" marker-end="url(#arr)"/>\n'
    svg += f'<text x="340" y="425" class="vl" font-size="6">→Res</text>\n'
    
    # Control signals (dashed)
    svg += f'<path d="M520,{pico_y} L800,{pico_y} L800,{exp_y["Slew"]} L920,{exp_y["Slew"]}" stroke="{C_PICO}" stroke-width="2" stroke-dasharray="5,3" fill="none"/>\n'
    svg += f'<text x="800" y="480" class="vl" font-size="6">GPIO</text>\n'
    
    svg += f'<path d="M520,{touch_y} L810,{touch_y} L810,{exp_y["Atten"]} L920,{exp_y["Atten"]}" stroke="{C_TOUCH}" stroke-width="2" stroke-dasharray="5,3" fill="none"/>\n'
    svg += f'<text x="810" y="520" class="vl" font-size="6">Touch</text>\n'
    
    # === LEGEND ===
    svg += '<rect x="50" y="630" width="320" height="150" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>\n'
    svg += '<text x="210" y="655" class="v" font-weight="bold" font-size="10">DB-9 A OUTPUTS (9 pins)</text>\n'
    
    legend_a = [
        "1: Gate", "2: Pitch CV", "3: Envelope", "4: LFO",
        "5: Mix", "6: VCF Out", "7: Saw", "8: Square", "9: GND"
    ]
    for i, txt in enumerate(legend_a):
        y = 675 + (i % 5) * 18
        x = 70 if i < 5 else 200
        svg += f'<text x="{x}" y="{y}" class="v" font-size="8">• {txt}</text>\n'
    
    # DB-9 B Legend
    svg += '<rect x="400" y="630" width="320" height="150" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>\n'
    svg += '<text x="560" y="655" class="v" font-weight="bold" font-size="10">DB-9 B INPUTS + POWER (9 pins)</text>\n'
    
    legend_b = [
        "1: Filter CV", "2: VCA CV", "3: Resonance", "4: Sync", "5: Gate In",
        "6: Ext Audio", "7: +12V", "8: -12V", "9: GND"
    ]
    for i, txt in enumerate(legend_b):
        y = 675 + (i % 5) * 18
        x = 420 if i < 5 else 550
        color = "#CC0000" if "12V" in txt else "#333"
        svg += f'<text x="{x}" y="{y}" class="v" font-size="8" fill="{color}">• {txt}</text>\n'
    
    svg += '<rect x="750" y="630" width="300" height="150" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>\n'
    svg += '<text x="900" y="655" class="v" font-weight="bold" font-size="10">EXPANDER MODULES</text>\n'
    
    exp_list = [
        "• Noise Gen (audio)", "• LFO (free-running)", "• S&H (sample & hold)",
        "• Clock Div (/2/4/8)", "• Slew Limiter", "• Attenuverter (1→3)"
    ]
    for i, txt in enumerate(exp_list):
        svg += f'<text x="770" y="{675 + i*18}" class="v" font-size="8">{txt}</text>\n'
    
    svg += '</svg>'
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    try:
        svg = system_architecture_complete()
        with open(f"{out}/system_architecture_block.svg", 'w') as f:
            f.write(svg)
        print("Generated: system_architecture_block.svg (Complete)")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
