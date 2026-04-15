#!/usr/bin/env python3
"""Generate improved system diagrams for MACROBRUTE."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from tools.generate_schematics import SchematicRenderer, Point

def elbow_wire(x1, y1, x2, y2, color="#1a1a1a", width=1.5):
    """Generate elbow/bent line path."""
    # Simple L-shaped elbow
    mid_x = x1 + (x2 - x1) * 0.7
    path = f'M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}'
    return f'<path d="{path}" stroke="{color}" stroke-width="{width}" fill="none"/>'

def generate_signal_flow():
    """High-level signal flow overview."""
    r = SchematicRenderer(800, 600, "Signal Flow Overview", "Complete MACROBRUTE Architecture")
    
    # Sections
    sections = [
        ("MicroBrute", 50, 100, 150, 400, "#E8D5A3"),
        ("Breakout", 250, 150, 100, 300, "#C4A265"),
        ("DB-9", 400, 200, 80, 200, "#2a2a2a"),
        ("Expander", 550, 100, 200, 400, "#E8D5A3"),
    ]
    
    for name, x, y, w, h, color in sections:
        r.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#333" stroke-width="2" rx="4"/>')
        r.elements.append(f'<text x="{x+w//2}" y="{y-10}" class="label" text-anchor="middle">{name}</text>')
    
    # Signal labels
    signals = ["Saw", "Sqr", "Mix", "VCF", "Gate", "Pitch", "Env", "LFO"]
    for i, sig in enumerate(signals):
        y = 220 + i * 22
        # From MB to Breakout
        r.elements.append(elbow_wire(200, y, 250, y))
        # From Breakout to DB-9
        r.elements.append(elbow_wire(350, y, 400, y))
        # From DB-9 to Expander
        r.elements.append(elbow_wire(480, y, 550, y))
        # Label
        r.elements.append(f'<text x="{375}" y="{y+3}" class="value" font-size="8" text-anchor="middle">{sig}</text>')
    
    # Module boxes in expander
    mods = [("Noise", 130), ("LFO", 170), ("S&H", 210), ("Clock", 250), ("Slew", 290), ("Atten", 330), ("Scope", 370), ("Delay", 410)]
    for name, y in mods:
        r.elements.append(f'<rect x="{570}" y="{y}" width="160" height="30" fill="#4A90D9" rx="2"/>')
        r.elements.append(f'<text x="{650}" y="{y+20}" class="label" text-anchor="middle" fill="#FFF" font-size="9">{name}</text>')
    
    return r.render()

def main():
    os.makedirs("schematics", exist_ok=True)
    
    diagrams = [
        ("wiring_signal_flow.svg", generate_signal_flow),
    ]
    
    for filename, generator in diagrams:
        try:
            with open(f"schematics/{filename}", 'w') as f:
                f.write(generator())
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Error: {filename}: {e}")

if __name__ == "__main__":
    main()
