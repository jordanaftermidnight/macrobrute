"""Pico VSYS power-protection card -> schematics/pico_power_protection.svg.

Run from the repo root:  python3 -m tools.diagrams.pico_protection

Rack +5 V -> series Schottky -> bulk and 100 nF -> Pico VSYS (physical pin 39).
Values follow docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md (BF
1.2, 1.4) and docs/MACROBRUTE_CONNECTION_MAP.md section 10. Design values only:
nothing is built, and every stand-in or unmeasured figure carries a tag.
"""
import sys
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import PALETTE, Card, _t, diode, label_box, wire
from tools.diagrams.power_common import C_5V, box, cap_v, notes, tag

OUT = Path(__file__).resolve().parents[2] / "schematics" / "pico_power_protection.svg"

C_3V3, C_GND = PALETTE["p3v3"], PALETTE["gnd"]
W, H = 1140, 760

# --------------------------------------------------------------------- nets
# Parts: HDR (rack 16-pin header), D1 (series Schottky), C_BULK, C_100N, PICO, LOADS.
NETS = {
    "RACK_5V": [("HDR", "11"), ("HDR", "12"), ("D1", "A")],
    "VSYS": [("D1", "K"), ("C_BULK", "+"), ("C_100N", "1"), ("PICO", "VSYS")],
    "GND": [("HDR", "3"), ("HDR", "4"), ("HDR", "5"), ("HDR", "6"), ("HDR", "7"),
            ("HDR", "8"), ("C_BULK", "-"), ("C_100N", "2"), ("PICO", "GND"),
            ("LOADS", "GND")],
    "3V3": [("PICO", "3V3"), ("LOADS", "3V3")],
}
RAILS = {"RACK_5V": 5.0, "3V3": 3.3}

GND_Y = 470


def build():
    card = Card(W, H, "Pico Power Protection (VSYS from the rack +5 V)",
                "Series Schottky, bulk and 100 nF to VSYS (pin 39). Design values, nothing built yet")

    card.add('<g transform="translate(0,-50)">')
    # GND rail bar
    card.add(f'<rect x="30" y="{GND_Y}" width="1080" height="18" rx="4" fill="{C_GND}"/>'
             + _t(40, GND_Y + 13, "GND (expander star, rack 0 V)", 11, "start", "#fff", True))

    # rack source box
    card.add(box(40, 170, 130, 230, ["Rack 16-pin header", "Behringer CP1A"],
                 ["+5 V pins 11-12", "0.5 A shared", "GND pins 3-8"],
                 right=[("+5V", 230), ("GND", 380)]))

    # series diode D1, rack to VSYS node
    y5 = 230
    card.add(wire([(170, y5), (230, y5)], C_5V))
    card.add(wire([(260, y5), (700, y5)], C_5V, junctions=[(380, y5), (520, y5)]))
    card.add(diode(230, y5, "D1 1N5817"))
    card.add(tag(185, 252, "PROVISIONAL"))
    card.add(tag(185, 269, "OWNER-CONFIRM", "OWNER-CONFIRM 1N5819"))
    card.add(tag(185, 286, "UNVERIFIED", "UNVERIFIED 1N5819 part"))

    # shunt caps: bulk at 380, 100 nF at 520
    card.add(wire([(380, y5), (380, 300)], C_5V))
    card.add(wire([(380, 330), (380, GND_Y)], C_GND, junctions=[(380, GND_Y)]))
    card.add(cap_v(380, 300, "2-4x 10uF/63V", polar=True))
    card.add(wire([(520, y5), (520, 300)], C_5V))
    card.add(wire([(520, 330), (520, GND_Y)], C_GND, junctions=[(520, GND_Y)]))
    card.add(cap_v(520, 300, "100nF"))
    card.add(label_box(400, 208, "VSYS node"))
    card.add(tag(395, 345, "OPEN", "OPEN bulk count"))

    # rack GND to the bar
    card.add(wire([(170, 380), (200, 380), (200, GND_Y)], C_GND, junctions=[(200, GND_Y)]))

    # Pico block (used pins only)
    card.add(box(700, 170, 170, 230, ["Raspberry Pi Pico", "pins used"],
                 ["VSYS 1.8-5.5 V", "pin 39: rack 5 V in", "VBUS pin 40: USB only,", "not wired here", "3V3 OUT: under 300 mA"],
                 left=[("VSYS 39", y5), ("GND 38", 380)], right=[("3V3 OUT 36", y5)]))
    card.add(wire([(700, 380), (660, 380), (660, GND_Y)], C_GND, junctions=[(660, GND_Y)]))

    # 3V3 loads
    card.add(wire([(870, y5), (930, y5)], C_3V3))
    card.add(box(930, 170, 170, 130, ["3V3 loads"],
                 ["OLED 1.3in I2C", "encoder +", "I2C0 pull-ups", "CD4049UB VCC"],
                 left=[("3V3", y5), ("GND", 280)]))
    card.add(wire([(930, 280), (910, 280), (910, GND_Y)], C_GND, junctions=[(910, GND_Y)]))
    card.add(tag(930, 308, "UNVERIFIED", "UNVERIFIED actual load"))

    card.add("</g>")

    # info panels
    px = 30
    s1, b1 = notes(px, 460, 340, "Part choice (BF 1.2)", [
        "D1 is the 1N5817: a 20 V, 1 A Schottky, not 40 V (DATASHEETS (e)). VF 0.45 V max at 1 A "
        "(Diodes DS23001 p2). Fine for a 5 V rail.",
        ("1N5817 is not owned. Owned 1N5819 (40 V, x10, VF 0.60 V at 1 A on the series sheet) may "
         "stand in; owner to confirm.", "OWNER-CONFIRM"),
        ("The owned 1N5819 part and its datasheet are not verified.", "UNVERIFIED"),
        ("BAT85 can also stand in: about 4.2 V at VSYS and 100 mA, IF 200 mA max.", "PROVISIONAL"),
    ])
    s2, b2 = notes(390, 460, 340, "Supply limits", [
        "VSYS accepts 1.8 V to 5.5 V (Pico datasheet p9). An external 5 V is ORed into VSYS "
        "through a Schottky (p22): this chain is that arrangement.",
        "CP1A +5 V is 0.5 A in total, shared with every module in the rack (QSG p20).",
        ("Pico draw from VSYS: not measured.", "UNVERIFIED"),
        ("Rack +5 V present on the owner's bus slot (bench check BT-12).", "UNVERIFIED"),
    ])
    s3, b3 = notes(750, 460, 360, "Rules", [
        "Bulk: 2-4x owned 10uF/63V electrolytic in parallel, plus 100 nF (BF 1.4, CM section 10).",
        "No USB cable on the Pico while the rack powers it and the DB-9 cables are connected "
        "(BF 4.3). USB with rack 5 V is safe for the Pico (on-board VBUS Schottky, p21-22).",
        "Pico 3V3 OUT feeds the OLED, encoder and pull-ups: keep the load under 300 mA (p9).",
    ])
    card.add(s1 + s2 + s3)
    card.legend([(C_5V, "+5 V (rack)"), (C_3V3, "3V3 (Pico out)"), (C_GND, "GND")])
    return card


def render():
    return build().render()


def main():
    problems = validate_nets(NETS, RAILS)
    if problems:
        sys.exit("net problems:\n  " + "\n  ".join(problems))
    OUT.write_text(render())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
