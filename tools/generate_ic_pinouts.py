#!/usr/bin/env python3
"""Generate individual IC pinout diagrams for MACROBRUTE."""

import os


def generate_ic_pinout(name: str, pins_left: list, pins_right: list, package: str, 
                       description: str, color: str = "#2a2a2a") -> str:
    """Generate an individual IC pinout diagram."""
    
    width = 500
    height = 600
    
    # SVG Header
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
  <filter id="textshadow" x="-20%" y="-20%" width="140%" height="140%">
    <feFlood flood-color="white" flood-opacity="0.9" result="bg"/>
    <feMorphology in="SourceGraphic" operator="dilate" radius="1.5" result="dilated"/>
    <feComposite in="bg" in2="dilated" operator="in" result="shadow"/>
    <feMerge><feMergeNode in="shadow"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .title {{ font: bold 16px "SF Mono", Consolas, monospace; fill: #1a1a1a; filter: url(#textshadow); }}
    .subtitle {{ font: 11px "SF Mono", Consolas, monospace; fill: #555; filter: url(#textshadow); }}
    .label {{ font: bold 11px "SF Mono", Consolas, monospace; fill: #1a1a1a; filter: url(#textshadow); }}
    .value {{ font: 10px "SF Mono", Consolas, monospace; fill: #555; filter: url(#textshadow); }}
    .pin {{ font: 9px "SF Mono", Consolas, monospace; fill: #FFF; }}
    .pin-num {{ font: 10px "SF Mono", Consolas, monospace; fill: gold; font-weight: bold; }}
    .pin-func {{ font: 10px "SF Mono", Consolas, monospace; fill: #FFF; }}
  </style>
</defs>
<rect width="{width}" height="{height}" fill="#FEFEFE"/>
<text x="{width//2}" y="30" class="title" text-anchor="middle">{name}</text>
<text x="{width//2}" y="50" class="subtitle" text-anchor="middle">{package} - {description}</text>
'''
    
    # IC Body
    ic_x = 175
    ic_y = 80
    ic_w = 150
    pin_count = max(len(pins_left), len(pins_right))
    ic_h = pin_count * 35 + 40
    
    # Draw IC body
    svg += f'<rect x="{ic_x}" y="{ic_y}" width="{ic_w}" height="{ic_h}" fill="{color}" stroke="#1a1a1a" stroke-width="2" rx="5"/>\n'
    
    # Pin 1 indicator (notch)
    svg += f'<circle cx="{ic_x+15}" cy="{ic_y+15}" r="5" fill="gold"/>\n'
    svg += f'<text x="{ic_x+15}" y="{ic_y+30}" class="value" text-anchor="middle" fill="gold" font-size="8">Pin 1</text>\n'
    
    # IC Label
    svg += f'<text x="{ic_x+ic_w/2}" y="{ic_y+ic_h/2}" class="label" text-anchor="middle" fill="#FFF" font-size="14">{name}</text>\n'
    svg += f'<text x="{ic_x+ic_w/2}" y="{ic_y+ic_h/2+20}" class="value" text-anchor="middle" fill="#CCC" font-size="9">{package}</text>\n'
    
    # Left side pins (1 to N/2, top to bottom)
    for i, pin_func in enumerate(pins_left):
        pin_y = ic_y + 35 + i * 35
        pin_num = i + 1
        
        # Pin dot
        svg += f'<circle cx="{ic_x}" cy="{pin_y}" r="6" fill="#C0C0C0" stroke="#666" stroke-width="1"/>\n'
        
        # Pin number (outside)
        svg += f'<text x="{ic_x-12}" y="{pin_y+3}" class="pin-num" text-anchor="end">{pin_num}</text>\n'
        
        # Pin function (inside)
        if pin_func:
            svg += f'<text x="{ic_x+12}" y="{pin_y+3}" class="pin-func" font-size="8">{pin_func}</text>\n'
    
    # Right side pins (N to N/2+1, bottom to top)
    for i, pin_func in enumerate(pins_right):
        pin_y = ic_y + ic_h - 35 - i * 35
        pin_num = len(pins_left) + len(pins_right) - i
        
        # Pin dot
        svg += f'<circle cx="{ic_x+ic_w}" cy="{pin_y}" r="6" fill="#C0C0C0" stroke="#666" stroke-width="1"/>\n'
        
        # Pin number (outside)
        svg += f'<text x="{ic_x+ic_w+12}" y="{pin_y+3}" class="pin-num" text-anchor="start">{pin_num}</text>\n'
        
        # Pin function (inside)
        if pin_func:
            svg += f'<text x="{ic_x+ic_w-12}" y="{pin_y+3}" class="pin-func" text-anchor="end" font-size="8">{pin_func}</text>\n'
    
    # Pinout table below IC
    table_y = ic_y + ic_h + 40
    svg += f'<text x="{width//2}" y="{table_y}" class="label" text-anchor="middle" font-size="11">Complete Pinout Reference</text>\n'
    
    # Draw table
    all_pins = pins_left + list(reversed(pins_right))
    row_height = 20
    col_width = 200
    
    for i, func in enumerate(all_pins):
        row = i // 2
        col = i % 2
        x = 50 + col * col_width
        y = table_y + 25 + row * row_height
        pin_num = i + 1
        
        # Alternate row colors
        bg_color = "#F5F5F5" if row % 2 == 0 else "#FFFFFF"
        svg += f'<rect x="{x}" y="{y-12}" width="{col_width-10}" height="{row_height-2}" fill="{bg_color}" stroke="#DDD" stroke-width="0.5"/>\n'
        svg += f'<text x="{x+5}" y="{y}" class="value" font-size="9" font-weight="bold">{pin_num}.</text>\n'
        svg += f'<text x="{x+25}" y="{y}" class="value" font-size="9">{func or "NC"}</text>\n'
    
    # Footer
    svg += '</svg>'
    return svg


def main():
    """Generate all IC pinout diagrams."""
    output_dir = "/Users/jordan_after_midnight/Projects/music/macrobrute/schematics"
    
    ics = [
        ("TL074", "Quad Op-Amp", [
            "OUT1", "IN1-", "IN1+", "VCC+", "IN2+", "IN2-", "OUT2"
        ], [
            "OUT3", "IN3-", "IN3+", "GND", "IN4+", "IN4-", "OUT4"
        ], "DIP-14", "#2196F3"),
        
        ("TL072", "Dual Op-Amp", [
            "OUT1", "IN1-", "IN1+", "VCC-"
        ], [
            "VCC+", "IN2+", "IN2-", "OUT2"
        ], "DIP-8", "#4CAF50"),
        
        ("CD40106", "Hex Schmitt", [
            "1A", "1Y", "2A", "2Y", "3A", "3Y", "GND"
        ], [
            "VCC", "4Y", "4A", "5Y", "5A", "6Y", "6A"
        ], "DIP-14", "#FF9800"),
        
        ("CD4051", "8-Ch MUX", [
            "X4", "X6", "X", "X7", "X5", "INH", "VEE", "VSS"
        ], [
            "C", "B", "A", "X3", "X0", "X1", "X2", "VCC"
        ], "DIP-16", "#9C27B0"),
        
        ("CD4024", "7-Stage Counter", [
            "CLK", "RESET", "Q7", "Q6", "Q5", "Q4", "GND"
        ], [
            "VCC", "Q3", "Q2", "Q1", "NC", "NC", "NC"
        ], "DIP-14", "#E91E63"),
        
        ("CD4066", "Quad Switch", [
            "1A", "1B", "1C", "2C", "2B", "2A", "GND"
        ], [
            "VCC", "3A", "3B", "3C", "4C", "4B", "4A"
        ], "DIP-14", "#00BCD4"),
        
        ("LM358", "Dual Op-Amp", [
            "OUT1", "IN1-", "IN1+", "GND"
        ], [
            "IN2+", "IN2-", "OUT2", "VCC"
        ], "DIP-8", "#795548"),
        
    ]
    
    for name, desc, left_pins, right_pins, package, color in ics:
        filepath = os.path.join(output_dir, f"ic_pinout_{name.lower()}.svg")
        try:
            svg_content = generate_ic_pinout(name, left_pins, right_pins, package, desc, color)
            with open(filepath, 'w') as f:
                f.write(svg_content)
            print(f"Generated: ic_pinout_{name.lower()}.svg")
        except Exception as e:
            print(f"Failed {name}: {e}")
    
    print("All IC pinout diagrams generated!")


if __name__ == "__main__":
    main()
