#!/usr/bin/env python3
"""Generate clean System Architecture with grouped signals."""

import os


def system_architecture_clean():
    """Clean System Architecture with grouped signal channels."""
    width, height = 1100, 700
    
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
<text x="550" y="25" class="t" text-anchor="middle">MACROBRUTE System Architecture</text>
<text x="550" y="45" class="st" text-anchor="middle">Grouped Signal Channels (All DB-9 Pins)</text>
'''
    
    C_MICRO = "#2196F3"
    C_DB9A = "#FF9800"
    C_DB9B = "#FF5722"
    C_PICO = "#9C27B0"
    C_TOUCH = "#673AB7"
    C_EXPAND = "#4CAF50"
    C_AUDIO = "#E91E63"
    C_CV = "#9C27B0"
    
    # Section headers
    svg += '<text x="120" y="70" class="v" font-weight="bold" font-size="11" fill="#333">MICROBRUTE</text>\n'
    svg += '<text x="500" y="70" class="v" font-weight="bold" font-size="11" fill="#333">INTERFACE</text>\n'
    svg += '<text x="900" y="70" class="v" font-weight="bold" font-size="11" fill="#333">EXPANDER</text>\n'
    
    # === MICROBRUTE (Left) ===
    # Grouped into functional blocks with clear separation
    
    # Audio Output Group
    svg += f'<rect x="50" y="85" width="110" height="90" fill="{C_AUDIO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="105" class="l" font-size="10">AUDIO OUT</text>\n'
    svg += f'<text x="105" y="122" class="l" font-size="7">Saw, Sqr, VCF</text>\n'
    svg += f'<text x="105" y="135" class="l" font-size="7">Mix (Ultrafaux)</text>\n'
    svg += f'<text x="105" y="148" class="l" font-size="7">Pins: 5,6,7,8</text>\n'
    audio_y = 130
    
    # CV Output Group
    svg += f'<rect x="50" y="190" width="110" height="90" fill="{C_CV}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="210" class="l" font-size="10">CV OUT</text>\n'
    svg += f'<text x="105" y="227" class="l" font-size="7">Pitch, Gate</text>\n'
    svg += f'<text x="105" y="240" class="l" font-size="7">LFO, Envelope</text>\n'
    svg += f'<text x="105" y="253" class="l" font-size="7">Pins: 1,2,3,4</text>\n'
    cv_out_y = 235
    
    # Synth Blocks (inputs)
    svg += f'<rect x="50" y="300" width="110" height="70" fill="{C_MICRO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="325" class="l" font-size="10">VCF</text>\n'
    svg += f'<text x="105" y="342" class="l" font-size="7">Filter CV In</text>\n'
    svg += f'<text x="105" y="355" class="l" font-size="7">Resonance In</text>\n'
    vcf_y = 335
    
    svg += f'<rect x="50" y="385" width="110" height="60" fill="{C_MICRO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="105" y="410" class="l" font-size="10">VCA</text>\n'
    svg += f'<text x="105" y="427" class="l" font-size="7">VCA CV In</text>\n'
    vca_y = 415
    
    # === DB-9 SECTIONS (Center) ===
    
    # DB-9 A - Audio Outputs
    svg += f'<rect x="320" y="100" width="130" height="70" fill="{C_DB9A}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="385" y="125" class="l" font-size="11">DB-9 A</text>\n'
    svg += f'<text x="385" y="145" class="l" font-size="8">AUDIO →</text>\n'
    svg += f'<text x="385" y="158" class="l" font-size="7">Pins 5,6,7,8</text>\n'
    db9a_audio_y = 135
    
    # DB-9 A - CV Outputs
    svg += f'<rect x="320" y="200" width="130" height="70" fill="{C_DB9A}" stroke="#1a1a1a" stroke-width="2" rx="4" opacity="0.8"/>\n'
    svg += f'<text x="385" y="225" class="l" font-size="11">DB-9 A</text>\n'
    svg += f'<text x="385" y="245" class="l" font-size="8">CV / GATE →</text>\n'
    svg += f'<text x="385" y="258" class="l" font-size="7">Pins 1,2,3,4</text>\n'
    db9a_cv_y = 235
    
    # DB-9 B - CV Inputs
    svg += f'<rect x="320" y="310" width="130" height="80" fill="{C_DB9B}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="385" y="335" class="l" font-size="11">DB-9 B</text>\n'
    svg += f'<text x="385" y="355" class="l" font-size="8">← CV INPUTS</text>\n'
    svg += f'<text x="385" y="372" class="l" font-size="7">Filt, VCA, Res</text>\n'
    svg += f'<text x="385" y="385" class="l" font-size="7">Sync, Gate, Ext</text>\n'
    db9b_cv_y = 350
    
    # DB-9 B - Power
    svg += f'<rect x="320" y="410" width="130" height="60" fill="#CC0000" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="385" y="435" class="l" font-size="11">DB-9 B</text>\n'
    svg += f'<text x="385" y="455" class="l" font-size="8">POWER</text>\n'
    svg += f'<text x="385" y="468" class="l" font-size="7">+12V, -12V, GND</text>\n'
    power_y = 440
    
    # Control
    svg += f'<rect x="320" y="510" width="130" height="50" fill="{C_PICO}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="385" y="535" class="l" font-size="10">Pico W</text>\n'
    svg += f'<text x="385" y="550" class="l" font-size="8">Control</text>\n'
    pico_y = 535
    
    svg += f'<rect x="320" y="580" width="130" height="40" fill="{C_TOUCH}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="385" y="598" class="l" font-size="10">Touch</text>\n'
    svg += f'<text x="385" y="612" class="l" font-size="8">4-Point</text>\n'
    touch_y = 605
    
    # === EXPANDER (Right) ===
    
    # Audio Input Section
    svg += f'<rect x="880" y="100" width="130" height="90" fill="{C_EXPAND}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="945" y="125" class="l" font-size="10">AUDIO IN</text>\n'
    svg += f'<text x="945" y="142" class="l" font-size="7">Noise Gen</text>\n'
    svg += f'<text x="945" y="155" class="l" font-size="7">LFO (Free)</text>\n'
    svg += f'<text x="945" y="168" class="l" font-size="7">S&H, Clock</text>\n'
    svg += f'<text x="945" y="181" class="l" font-size="7">From DB-9 A</text>\n'
    exp_audio_y = 145
    
    # CV Output Section
    svg += f'<rect x="880" y="210" width="130" height="120" fill="{C_EXPAND}" stroke="#1a1a1a" stroke-width="2" rx="4" opacity="0.8"/>\n'
    svg += f'<text x="945" y="235" class="l" font-size="10">CV / GATE OUT</text>\n'
    svg += f'<text x="945" y="255" class="l" font-size="7">LFO → Filter CV</text>\n'
    svg += f'<text x="945" y="272" class="l" font-size="7">S&H → VCA CV</text>\n'
    svg += f'<text x="945" y="289" class="l" font-size="7">Clock → Res/Sync</text>\n'
    svg += f'<text x="945" y="306" class="l" font-size="7">Clock → Gate In</text>\n'
    svg += f'<text x="945" y="323" class="l" font-size="7">To DB-9 B</text>\n'
    exp_cv_y = 270
    
    # Modulation Section
    svg += f'<rect x="880" y="350" width="130" height="100" fill="{C_EXPAND}" stroke="#1a1a1a" stroke-width="2" rx="4"/>\n'
    svg += f'<text x="945" y="375" class="l" font-size="10">MODULATION</text>\n'
    svg += f'<text x="945" y="395" class="l" font-size="7">Slew Limiter</text>\n'
    svg += f'<text x="945" y="412" class="l" font-size="7">Attenuverter</text>\n'
    svg += f'<text x="945" y="429" class="l" font-size="7">(Pico Control)</text>\n'
    exp_mod_y = 400
    
    # === CONNECTIONS - Clean bus-style routing ===
    
    # 1. AUDIO BUS (Blue/Pink) - MicroBrute Audio → DB-9 A Audio → Expander Audio In
    # Main audio bus line
    svg += f'<line x1="160" y1="{audio_y}" x2="250" y2="{audio_y}" stroke="{C_AUDIO}" stroke-width="4"/>\n'
    svg += f'<text x="205" y="{audio_y-8}" class="bus-label" font-size="7">Audio Bus</text>\n'
    svg += f'<text x="205" y="{audio_y+12}" class="vl" font-size="6">Saw,Sqr,VCF,Mix</text>\n'
    # To DB-9 A
    svg += f'<line x1="250" y1="{audio_y}" x2="250" y2="{db9a_audio_y}" stroke="{C_AUDIO}" stroke-width="4"/>\n'
    svg += f'<line x1="250" y1="{db9a_audio_y}" x2="320" y2="{db9a_audio_y}" stroke="{C_AUDIO}" stroke-width="4" marker-end="url(#arr)"/>\n'
    # To Expander
    svg += f'<line x1="450" y1="{db9a_audio_y}" x2="550" y2="{db9a_audio_y}" stroke="{C_DB9A}" stroke-width="3"/>\n'
    svg += f'<line x1="550" y1="{db9a_audio_y}" x2="550" y2="{exp_audio_y}" stroke="{C_DB9A}" stroke-width="3"/>\n'
    svg += f'<line x1="550" y1="{exp_audio_y}" x2="880" y2="{exp_audio_y}" stroke="{C_DB9A}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="650" y="{exp_audio_y-8}" class="vl" font-size="7">Audio→Expander</text>\n'
    
    # 2. CV OUT BUS (Purple) - MicroBrute CV/Gate → DB-9 A CV → Expander
    svg += f'<line x1="160" y1="{cv_out_y}" x2="270" y2="{cv_out_y}" stroke="{C_CV}" stroke-width="4"/>\n'
    svg += f'<text x="215" y="{cv_out_y-8}" class="bus-label" font-size="7">CV/Gate Bus</text>\n'
    svg += f'<text x="215" y="{cv_out_y+12}" class="vl" font-size="6">Pitch,LFO,Env,Gate</text>\n'
    # To DB-9 A
    svg += f'<line x1="270" y1="{cv_out_y}" x2="270" y2="{db9a_cv_y}" stroke="{C_CV}" stroke-width="4"/>\n'
    svg += f'<line x1="270" y1="{db9a_cv_y}" x2="320" y2="{db9a_cv_y}" stroke="{C_CV}" stroke-width="4" marker-end="url(#arr)"/>\n'
    # To Expander (for modulation)
    svg += f'<line x1="450" y1="{db9a_cv_y}" x2="580" y2="{db9a_cv_y}" stroke="{C_DB9A}" stroke-width="3" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="580" y1="{db9a_cv_y}" x2="580" y2="{exp_cv_y}" stroke="{C_DB9A}" stroke-width="3" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="580" y1="{exp_cv_y}" x2="880" y2="{exp_cv_y}" stroke="{C_DB9A}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="680" y="{exp_cv_y-8}" class="vl" font-size="7">CV→Expander</text>\n'
    
    # 3. CV IN BUS (Green) - Expander CV → DB-9 B CV → MicroBrute VCF/VCA
    svg += f'<line x1="880" y1="{exp_cv_y+20}" x2="720" y2="{exp_cv_y+20}" stroke="{C_EXPAND}" stroke-width="4"/>\n'
    svg += f'<text x="800" y="{exp_cv_y+12}" class="bus-label" font-size="7">CV Out Bus</text>\n'
    svg += f'<text x="800" y="{exp_cv_y+32}" class="vl" font-size="6">LFO,S&H,Clock</text>\n'
    # To DB-9 B
    svg += f'<line x1="720" y1="{exp_cv_y+20}" x2="720" y2="{db9b_cv_y}" stroke="{C_EXPAND}" stroke-width="4"/>\n'
    svg += f'<line x1="720" y1="{db9b_cv_y}" x2="450" y2="{db9b_cv_y}" stroke="{C_EXPAND}" stroke-width="4" marker-end="url(#arr)"/>\n'
    # To MicroBrute (split to VCF and VCA)
    svg += f'<line x1="320" y1="{db9b_cv_y}" x2="260" y2="{db9b_cv_y}" stroke="{C_DB9B}" stroke-width="3"/>\n'
    # To VCF
    svg += f'<line x1="260" y1="{db9b_cv_y}" x2="260" y2="{vcf_y}" stroke="{C_DB9B}" stroke-width="3"/>\n'
    svg += f'<line x1="260" y1="{vcf_y}" x2="160" y2="{vcf_y}" stroke="{C_DB9B}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="210" y="{vcf_y-8}" class="vl" font-size="7">Filter CV</text>\n'
    # To VCA
    svg += f'<line x1="260" y1="{db9b_cv_y}" x2="275" y2="{db9b_cv_y}" stroke="{C_DB9B}" stroke-width="3"/>\n'
    svg += f'<line x1="275" y1="{db9b_cv_y}" x2="275" y2="{vca_y}" stroke="{C_DB9B}" stroke-width="3"/>\n'
    svg += f'<line x1="275" y1="{vca_y}" x2="160" y2="{vca_y}" stroke="{C_DB9B}" stroke-width="3" marker-end="url(#arr)"/>\n'
    svg += f'<text x="220" y="{vca_y-8}" class="vl" font-size="7">VCA CV</text>\n'
    
    # 4. POWER BUS (Red) - DB-9 B Power → Expander
    svg += f'<line x1="450" y1="{power_y}" x2="650" y2="{power_y}" stroke="#CC0000" stroke-width="5"/>\n'
    svg += f'<text x="550" y="{power_y-10}" class="bus-label" font-size="8" fill="#CC0000">POWER BUS ±12V</text>\n'
    svg += f'<line x1="650" y1="{power_y}" x2="650" y2="{exp_audio_y+20}" stroke="#CC0000" stroke-width="5"/>\n'
    svg += f'<line x1="650" y1="{exp_audio_y+20}" x2="880" y2="{exp_audio_y+20}" stroke="#CC0000" stroke-width="5" marker-end="url(#arr)"/>\n'
    svg += f'<text x="750" y="{power_y+15}" class="vl" font-size="7" fill="#CC0000">Power to Expander</text>\n'
    
    # 5. CONTROL BUS (Purple dashed)
    svg += f'<line x1="450" y1="{pico_y}" x2="700" y2="{pico_y}" stroke="{C_PICO}" stroke-width="2" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="700" y1="{pico_y}" x2="700" y2="{exp_mod_y}" stroke="{C_PICO}" stroke-width="2" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="700" y1="{exp_mod_y}" x2="880" y2="{exp_mod_y}" stroke="{C_PICO}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="620" y="{pico_y-8}" class="vl" font-size="7">GPIO Control</text>\n'
    
    svg += f'<line x1="450" y1="{touch_y}" x2="750" y2="{touch_y}" stroke="{C_TOUCH}" stroke-width="2" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="750" y1="{touch_y}" x2="750" y2="{exp_mod_y+20}" stroke="{C_TOUCH}" stroke-width="2" stroke-dasharray="5,3"/>\n'
    svg += f'<line x1="750" y1="{exp_mod_y+20}" x2="880" y2="{exp_mod_y+20}" stroke="{C_TOUCH}" stroke-width="2" marker-end="url(#arr)"/>\n'
    svg += f'<text x="620" y="{touch_y+12}" class="vl" font-size="7">Touch Sense</text>\n'
    
    # === LEGEND ===
    svg += '<rect x="50" y="650" width="1000" height="40" fill="#F5F5F5" stroke="#999" stroke-width="1" rx="4"/>\n'
    
    legend_items = [
        (C_AUDIO, "Audio Bus (Saw, Sqr, VCF, Mix)"),
        (C_CV, "CV/Gate Bus (Pitch, LFO, Env, Gate)"),
        (C_DB9A, "DB-9 A → Expander"),
        (C_EXPAND, "Expander → DB-9 B"),
        ("#CC0000", "Power Bus (±12V, GND)"),
    ]
    
    for i, (color, txt) in enumerate(legend_items):
        x = 70 + i * 200
        svg += f'<rect x="{x}" y="{660}" width="20" height="14" fill="{color}" stroke="#333" rx="2"/>\n'
        svg += f'<text x="{x+28}" y="{672}" class="v" font-size="8">{txt}</text>\n'
    
    svg += '</svg>'
    return svg


def main():
    out = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    try:
        svg = system_architecture_clean()
        with open(f"{out}/system_architecture_block.svg", 'w') as f:
            f.write(svg)
        print("Generated: system_architecture_block.svg (Clean)")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
