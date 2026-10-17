"""Phase 0 bench-validation wiring card -> schematics/phase0_wiring_schematic.svg.

Run from the repo root:  python3 -m tools.diagrams.phase0_wiring

Everything is 3.3 V logic on a breadboard. Pin numbers come from
FIRMWARE_ROLES / PICO_PHYSICAL_PIN, never retyped. Nothing crosses the DB-9
cable in Phase 0, so the cable-line series-resistor rule of the validator
does not apply here.
"""
import sys
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import (PALETTE, Card, _dot, _line, _n, _t, jack, jack_pins,
                               label_box, pico_header, pico_header_pins, resistor,
                               resistor_pins, wire)
from tools.hwdata.pico import FIRMWARE_ROLES as R
from tools.hwdata.pico import PICO_PHYSICAL_PIN
from tools.diagrams.phase0_nets import (CLOCK_IN_NOTE, CS_NOTE, MISSING_PARTS, NETS, RAILS,  # noqa: F401
                                        RGB_ORDER, gp)
from tools.diagrams.power_common import box

OUT = Path(__file__).resolve().parents[2] / "schematics" / "phase0_wiring_schematic.svg"


C_3V3, C_GND = PALETTE["p3v3"], PALETTE["gnd"]
C_SPI, C_LED = PALETTE["audio"], PALETTE["p12"]
C_GPIO, C_CLK = PALETTE["cv"], PALETTE["clock"]

W, H = 920, 810
XR = 320            # right edge of the left-hand parts (signal pins)
XL = 170            # left edge of boxed parts (power pins)
BUS_3V3, BUS_GND = 55, 95
RAIL_TOP, RAIL_BOT = 70, 640
OX, OY = 460, 140   # Pico header origin (pin 1)


def _led_left(ox, oy, color):
    """LED glyph flowing right to left: anode at ox+30, cathode at ox."""
    out = (_line(ox, oy, ox + 30, oy)
           + f'<path d="M{_n(ox + 22)},{_n(oy - 7)} L{_n(ox + 22)},{_n(oy + 7)} '
             f'L{_n(ox + 9)},{_n(oy)} Z" fill="{color}" stroke="#222" stroke-width="1"/>'
           + _line(ox + 8, oy - 7, ox + 8, oy + 7, "#222", 2)
           + _line(ox + 12, oy - 9, ox + 6, oy - 15, color, 1.2)
           + _line(ox + 17, oy - 6, ox + 11, oy - 12, color, 1.2))
    return out + _dot(ox, oy) + _dot(ox + 30, oy)


def _button(x, y):
    """Push button: GND terminal at x, signal terminal at x+90."""
    return (_line(x, y, x + 20, y) + _line(x + 70, y, x + 90, y)
            + _line(x + 20, y, x + 66, y - 13, "#222", 2)
            + f'<circle cx="{_n(x + 20)}" cy="{_n(y)}" r="3" fill="#222"/>'
            + f'<circle cx="{_n(x + 70)}" cy="{_n(y)}" r="3" fill="#222"/>'
            + _dot(x, y) + _dot(x + 90, y))


def _gp_tag(px, py, text, side):
    """Opaque tag over a Pico pin label so the wire never crosses the text."""
    tw = len(text) * 5.4
    x = px - 10 - tw - 3 if side == "L" else px + 7
    tx = px - 10 if side == "L" else px + 10
    return (f'<rect x="{_n(x)}" y="{_n(py - 6.5)}" width="{_n(tw + 6)}" height="13" rx="2" '
            f'fill="{PALETTE["label_bg"]}" stroke="{PALETTE["stroke"]}" stroke-width="0.8"/>'
            + _t(tx, py + 3, text, 9, "end" if side == "L" else "start", PALETTE["title"], True))


def _tag(x, y, text):
    """Amber tag for anything not verified."""
    w = len(text) * 5.6 + 10
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="14" rx="3" fill="#fff3cd" '
            f'stroke="#c96a00" stroke-width="1"/>'
            + _t(x + 5, y + 10.5, text, 9, "start", "#7a4100", True))


def _missing(x, y, text):
    """Red tag for a part that is not owned."""
    w = len(text) * 5.6 + 10
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="14" rx="3" fill="#fde2e1" '
            f'stroke="#b3261e" stroke-width="1"/>'
            + _t(x + 5, y + 10.5, text, 9, "start", "#8c1d18", True))


def build():
    card = Card(W, H, "Phase 0 - Pico Bench Validation (wiring)",
                "Breadboard bench check, 3V3 logic only, one part group per peripheral")
    pins = pico_header_pins(OX, OY)

    def pp(role):
        return pins.xy(PICO_PHYSICAL_PIN[R[role]])

    def phys(n):
        return pins.xy(n)

    # rails
    card.add(f'<rect x="30" y="{RAIL_TOP}" width="860" height="18" rx="4" fill="{C_3V3}"/>'
             + _t(40, RAIL_TOP + 13, "3V3 rail (3.3 V)", 11, "start", "#222", True))
    card.add(f'<rect x="30" y="{RAIL_BOT}" width="860" height="18" rx="4" fill="{C_GND}"/>'
             + _t(40, RAIL_BOT + 13, "GND rail", 11, "start", "#fff", True))

    card.add(pico_header(OX, OY, "Raspberry Pi Pico (40-pin)"))

    # ---- target rows (left-hand parts)
    # OLED box pins sit level with their header pins, so the SPI wires run straight
    spi = ("OLED_SCK", "OLED_MOSI", "OLED_DC", "OLED_RES")
    spi_y = {role: pp(role)[1] for role in spi}
    led_y = {"LED_CLOCK": 292, "LED_GATE": 344, "LED_MODE": 396}
    btn_y = 468
    enc_y = {"ENC_SW": 515, "ENC_CLK": 555, "ENC_DT": 595}
    order = [(k, y, C_LED) for k, y in led_y.items()]
    order += [("BTN_TAP", btn_y, C_GPIO)] + [(k, y, C_GPIO) for k, y in enc_y.items()]
    # downward jogs: later (lower) pins use jog columns further right so wires never cross
    jog = {"LED_CLOCK": 344, "LED_GATE": 352, "LED_MODE": 360,
           "BTN_TAP": 368, "ENC_SW": 376, "ENC_CLK": 384, "ENC_DT": 392}
    wires = []
    for role in spi:
        px, py = pp(role)
        wires.append(wire([(px, py), (XR, py)], C_SPI))
    for role, ty, col in order:
        px, py = pp(role)
        wires.append(wire([(px, py), (jog[role], py), (jog[role], ty), (XR, ty)], col))

    # ---- OLED, Keyestudio-clone IIC/SPI module in SPI mode; CS is strapped to the GND bus (no GPIO)
    pin_name = {"OLED_SCK": "D0 SCK", "OLED_MOSI": "D1 MOSI", "OLED_DC": "DC", "OLED_RES": "RES"}
    card.add(box(XL, 148, XR - XL, 96,
                  ["1.3in OLED, Keyestudio", "IIC/SPI V2.0, SPI mode"], ["SPI0"],
                  left=[("VCC", 168), ("GND", 208), ("CS", 228)],
                  right=[(pin_name[r], spi_y[r]) for r in spi]))
    wires.append(wire([(XL, 168), (BUS_3V3, 168)], C_3V3))
    wires.append(wire([(XL, 208), (BUS_GND, 208)], C_GND))
    wires.append(wire([(XL, 228), (BUS_GND, 228)], C_GND))
    card.add(_tag(XL, 96, "UNVERIFIED: OLED pin order")
             + _tag(XL + 170, 96, "UNVERIFIED: OLED chip"))

    # ---- RGB LED, common cathode, 220 ohm per channel
    card.add(f'<rect x="205" y="262" width="127" height="166" rx="6" fill="none" '
             f'stroke="{PALETTE["stroke"]}" stroke-width="1" stroke-dasharray="5 4"/>'
             + _t(205, 258, "RGB LED, common cathode", 11, "start", PALETTE["title"], True))
    chan = {"LED_CLOCK": ("R", C_LED), "LED_GATE": ("G", PALETTE["gate"]),
            "LED_MODE": ("B", PALETTE["audio"])}
    gnd_junc = [(BUS_GND, 208), (BUS_GND, 228)]
    for role, y in led_y.items():
        name, lc = chan[role]
        card.add(resistor(XR, y, "220Ω", anchor="b"))
        card.add(_led_left(220, y, lc))
        card.add(label_box(220 + 15 - (len(f"LED {name}") * 6.2 + 6) / 2, y + 13, f"LED {name}"))
        ra = resistor_pins(XR, y, anchor="b").xy("a")
        wires.append(wire([ra, (250, y)], C_LED))
        wires.append(wire([(220, y), (BUS_GND, y)], C_GND))
        gnd_junc.append((BUS_GND, y))

    # ---- tap button
    card.add(_button(230, btn_y)
             + label_box(232, btn_y - 32, "Tap button, PULL_UP"))
    wires.append(wire([(230, btn_y), (BUS_GND, btn_y)], C_GND))
    gnd_junc.append((BUS_GND, btn_y))

    # ---- KY-040 encoder
    card.add(box(XL, 500, XR - XL, 115, ["KY-040 rotary encoder"], ["PULL_UP on", "SW CLK DT"],
                  left=[("+", 525), ("GND", 585)], right=[(n, y) for n, y in
                  (("SW", enc_y["ENC_SW"]), ("CLK", enc_y["ENC_CLK"]), ("DT", enc_y["ENC_DT"]))]))
    wires.append(wire([(XL, 525), (BUS_3V3, 525)], C_3V3))
    wires.append(wire([(XL, 585), (BUS_GND, 585)], C_GND))
    gnd_junc.append((BUS_GND, 585))

    # ---- power buses
    wires.append(wire([(BUS_3V3, RAIL_TOP + 18), (BUS_3V3, 525)], C_3V3,
                      junctions=[(BUS_3V3, 168), (BUS_3V3, 525)]))
    wires.append(wire([(BUS_GND, 208), (BUS_GND, RAIL_BOT)], C_GND,
                      junctions=gnd_junc + [(BUS_GND, RAIL_BOT)]))

    # ---- right side: 3V3 and GND from the Pico, clock block
    v3x, v3y = phys(36)
    wires.append(wire([(v3x, v3y), (600, v3y), (600, RAIL_TOP + 18)], C_3V3,
                      junctions=[(600, RAIL_TOP + 18)]))
    gx, gy = phys(23)
    BUS_R = 840
    wires.append(wire([(gx, gy), (BUS_R, gy)], C_GND, junctions=[(BUS_R, gy)]))

    out_y, in_y = 220, 300
    ox_px, ox_py = pp("CLOCK_OUT")
    in_px, in_py = pp("CLOCK_IN")
    rout_a = resistor_pins(620, out_y).xy("a")
    rout_b = resistor_pins(620, out_y).xy("b")
    rin_a = resistor_pins(620, in_y).xy("a")
    rin_b = resistor_pins(620, in_y).xy("b")
    jo = jack_pins(760, out_y).as_dict()
    ji = jack_pins(760, in_y).as_dict()
    wires.append(wire([(ox_px, ox_py), (565, ox_py), (565, out_y), rout_a], C_CLK))
    wires.append(wire([rout_b, jo["tip"]], C_CLK, junctions=[(700, out_y)]))
    wires.append(wire([(in_px, in_py), (600, in_py), (600, in_y), rin_a], C_CLK))
    wires.append(wire([rin_b, ji["tip"]], C_CLK))
    jumper = wire([(700, out_y), (700, 260), (600, 260), (600, in_y)], C_CLK,
                  junctions=[(600, in_y)]).replace("<polyline", '<polyline stroke-dasharray="6 4"', 1)
    wires.append(jumper)
    wires.append(wire([jo["sleeve"], (BUS_R, out_y)], C_GND))
    wires.append(wire([ji["sleeve"], (BUS_R, in_y)], C_GND))
    wires.append(wire([(BUS_R, out_y), (BUS_R, RAIL_BOT)], C_GND,
                      junctions=[(BUS_R, out_y), (BUS_R, in_y), (BUS_R, RAIL_BOT)]))

    # order: wires over header, then tags, then glyphs on top of wire ends
    card.add("".join(wires))
    for role in spi + ("LED_CLOCK", "LED_GATE", "LED_MODE",
                       "BTN_TAP", "ENC_SW", "ENC_CLK", "ENC_DT"):
        x, y = pp(role)
        card.add(_gp_tag(x, y, f"GP{R[role]}", "L"))
    for role in ("CLOCK_OUT", "CLOCK_IN"):
        x, y = pp(role)
        card.add(_gp_tag(x, y, f"GP{R[role]}", "R"))
    card.add(_gp_tag(v3x, v3y, "3V3", "R"))
    card.add(_gp_tag(gx, gy, "GND", "R"))

    card.add(resistor(620, out_y, "1kΩ") + resistor(620, in_y, "1kΩ"))
    co, ci = gp("CLOCK_OUT"), gp("CLOCK_IN")
    card.add(jack(760, out_y, f"CLOCK OUT ({co})") + jack(760, in_y, f"CLOCK IN ({ci})"))
    card.add(label_box(613, 243, "test jumper"))
    card.add(_t(620, 160, f"Loop-back test: {co} > 1k > {ci}", 10,
                "start", PALETTE["muted"]))

    # bench caveats: clock-in protection is absent on the bench, unowned parts
    cy = 470
    for i, line in enumerate(CLOCK_IN_NOTE):
        card.add(_tag(600, cy + 18 * i, line))
    for i, line in enumerate(MISSING_PARTS):
        card.add(_missing(600, cy + 46 + 18 * i, line))
    card.add(_tag(600, cy + 46 + 18 * len(MISSING_PARTS), RGB_ORDER))
    card.add(_tag(600, cy + 64 + 18 * len(MISSING_PARTS), CS_NOTE))
    card.add(_tag(600, cy + 82 + 18 * len(MISSING_PARTS), "SPI-only 7-pin header (owner confirmed)"))

    # note box
    card.add(f'<rect x="30" y="676" width="560" height="52" rx="4" fill="#fff" '
             f'stroke="{PALETTE["stroke"]}" stroke-width="1"/>'
             + _t(40, 692, "Phase 0 bench validation, 3V3 logic only. Run firmware/pico/test_hw.py per-peripheral.",
                  10, "start", PALETTE["text"])
             + _t(40, 720, "test_hw.py's OLED test draws through display.OLED_SPI. GP11 (gate input) is unused here.",
                  10, "start", PALETTE["muted"])
             + _t(40, 706, "OLED chip and the order of its 7 pins are UNVERIFIED: read the board first.",
                  10, "start", PALETTE["muted"]))

    card.legend([(C_3V3, "3V3 supply"), (C_GND, "GND"), (C_SPI, "SPI0 main OLED"),
                 (C_LED, "RGB LED drive"), (C_GPIO, "Button and encoder"),
                 (C_CLK, "Clock in and out")])
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
