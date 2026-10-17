"""Pico 40-pin pinout and allocation card -> schematics/pico_pinout_diagram.svg.

Run from the repo root:  python3 -m tools.diagrams.pico_pinout

Pin numbers come from PICO_PHYSICAL_PIN and FIRMWARE_ROLES. The role of each
GP is checked against the GPIO table of docs/MACROBRUTE_CONNECTION_MAP.md
section 1 by tools/tests/test_pico_pinout.py. GP23/24/25/29 are RP2040
internal, not on the header, and are never drawn as usable.
"""
import sys
from pathlib import Path

from tools.check_diagrams import validate_nets
from tools.diagram_kit import (PALETTE, PICO_NAMES, Card, _line, _n, _t, pico_header,
                               pico_header_pins)
from tools.hwdata.pico import FIRMWARE_ROLES as R
from tools.hwdata.pico import PICO_PHYSICAL_PIN

OUT = Path(__file__).resolve().parents[2] / "schematics" / "pico_pinout_diagram.svg"

COL = {
    "uart0": PALETTE["audio"], "oled": "#12968f", "led": PALETTE["p12"],
    "button": PALETTE["cv"], "encoder": "#e0a458", "clkdiv": PALETTE["gate"],
    "aux": PALETTE["n12"], "clock_in": PALETTE["clock"], "clock_out": "#b57edc",
    "free": "#d9d9cc", "3v3": PALETTE["p3v3"], "5v": "#7a4b1e",
    "gnd": PALETTE["gnd"], "other": "#bdbdb0", "gate_in": "#b03a6f",
}
DARK_TEXT = {"free", "3v3", "encoder", "other", "clock_out", "gnd"}


def _role(gp, cat, func, direction, dest, short, status="Used"):
    return {"pin": PICO_PHYSICAL_PIN[gp], "cat": cat, "func": func, "dir": direction,
            "dest": dest, "short": short, "status": status}


ROLES = {}
ROLES[R["LPC_TX"]] = _role(R["LPC_TX"], "uart0", "UART0 TX to LPC2361", "OUT",
                           "DB-9 B:1 to LPC RXD1 (UNVERIFIED)", "UART0 TX")
ROLES[R["LPC_RX"]] = _role(R["LPC_RX"], "uart0", "UART0 RX from LPC2361", "IN",
                           "DB-9 B:6 from LPC TXD1 (UNVERIFIED)", "UART0 RX")
for _k, _f, _pin in (("OLED_SCK", "OLED SCK (SPI0 SCK)", "D0"),
                     ("OLED_MOSI", "OLED MOSI (SPI0 TX)", "D1"),
                     ("OLED_DC", "OLED DC", "DC"), ("OLED_RES", "OLED RES", "RES")):
    g = R[_k]
    ROLES[g] = _role(g, "oled", _f, "OUT", f"Main OLED {_pin} (expander)", _f.split(" (")[0])
for _n_, _c in (("LED_CLOCK", "R"), ("LED_GATE", "G"), ("LED_MODE", "B")):
    g = R[_n_]
    ROLES[g] = _role(g, "led", f"RGB LED {_c}", "OUT", f"RGB LED {_c} (expander panel)",
                     f"RGB LED {_c}")
ROLES[R["GATE_IN"]] = _role(R["GATE_IN"], "gate_in", "Gate input (PROVISIONAL)", "IN",
                            "DB-9 A:1 via 22k/33k divider", "Gate in")
ROLES[R["BTN_TAP"]] = _role(R["BTN_TAP"], "button", "Tap button", "IN", "Tap button (expander panel)",
                            "Tap button")
for _k, _lab in (("ENC_SW", "switch"), ("ENC_CLK", "CLK (A)"), ("ENC_DT", "DT (B)")):
    g = R[_k]
    ROLES[g] = _role(g, "encoder", f"Encoder {_lab}", "IN", "Encoder (expander panel)",
                     f"Encoder {_lab}")
for _i, g in enumerate(R["CLK_DIV_PINS"], 1):
    ROLES[g] = _role(g, "clkdiv", f"Clock divider out {_i}", "OUT",
                     f"Panel jack, divider {_i}", f"Clk div out {_i}")
for _i, g in enumerate(R["AUX_OUT_PINS"], 1):
    ROLES[g] = _role(g, "aux", f"Aux output {_i}", "OUT", f"Panel jack, aux {_i}",
                     f"Aux out {_i}")
ROLES[R["CLOCK_IN"]] = _role(R["CLOCK_IN"], "clock_in", "Clock input", "IN",
                             "CLK IN jack via CD4049UB", "Clock in")
ROLES[R["CLOCK_OUT"]] = _role(R["CLOCK_OUT"], "clock_out", "Clock output", "OUT",
                              "CLK OUT jack via CD4049UB", "Clock out")
for _g_ in (26, 27, 28):
    ROLES[_g_] = _role(_g_, "free", f"ADC{_g_ - 26} (free)", "IN",
                       "- (unassigned, not FT)", "ADC free", "Free")
ROLES = dict(sorted(ROLES.items()))

# fixed (non-GP) header pins: physical pin -> (category, short note)
FIXED = {
    36: ("3v3", "3V3 out"), 39: ("5v", "5 V in (VSYS)"), 40: ("5v", "VBUS"),
    37: ("other", "3V3_EN"), 30: ("other", "RUN"), 35: ("other", "ADC_VREF"),
    33: ("gnd", "AGND"),
}
POWER_ROWS = [
    ("3V3", 36, "3V3 out: OLED, encoder", "PWR"),
    ("VSYS", 39, "+5 V in via Schottky OR from rack", "PWR"),
    ("VBUS", 40, "USB 5 V, feeds VSYS via on-board Schottky", "PWR"),
    ("GND", "3,8,13,18,23,28,33,38", "Ground to expander star point", "-"),
]

# ------------------------------------------------------------------ nets
NETS = {
    "3V3": [("PICO", "3V3"), ("OLED", "VCC"), ("ENC", "+")],
    "CABLE_UART_TX": [("PICO", f"GP{R['LPC_TX']}"), ("R", "1K_EXP"), ("DB9", "B:1")],
    "CABLE_UART_RX": [("PICO", f"GP{R['LPC_RX']}"), ("R", "1K_EXP"), ("DB9", "B:6")],
}
for _g_, _r in ROLES.items():
    if _r["status"] == "Used" and _r["cat"] not in ("uart0", "gate_in"):
        NETS[f"GP{_g_}"] = [("PICO", f"GP{_g_}"), ("DEST", _r["dest"])]
# The gate mirror reaches the pin only through the 22k/33k divider (BF 3.5).
NETS["GATE_IN"] = [("PICO", f"GP{R['GATE_IN']}"), ("DIV", "22K_33K"), ("DB9", "A:1")]
RAILS = {"3V3": 3.3}

W, H = 1290, 724
OX, OY = 300, 96
TX = 656            # table left edge
ROW_H = 17


def _tag(px, py, text, cat, side):
    """Role-coloured pin tag drawn over the kit's black pin label."""
    tw = len(text) * 5.6 + 8
    x = px - 8 - tw if side == "L" else px + 8
    fg = "#222" if cat in DARK_TEXT else "#fff"
    return (f'<rect x="{_n(x)}" y="{_n(py - 6.5)}" width="{_n(tw)}" height="13" rx="2" '
            f'fill="{COL[cat]}" stroke="#444" stroke-width="0.8"/>'
            + _t(x + tw / 2, py + 3, text, 9, "middle", fg, True)), x, x + tw


def _flag(x, y, text, anchor="start"):
    w = len(text) * 5.6 + 8
    x0 = x if anchor == "start" else x - w
    return (f'<rect x="{_n(x0)}" y="{_n(y - 6.5)}" width="{_n(w)}" height="13" rx="2" '
            f'fill="#fff3cd" stroke="#b8860b" stroke-width="1"/>'
            + _t(x0 + w / 2, y + 3, text, 9, "middle", "#7a5200", True))


def _pin_cat(phys):
    gp = next((g for g, p in PICO_PHYSICAL_PIN.items() if p == phys), None)
    if gp is not None:
        return ROLES[gp]["cat"], ROLES[gp]["short"], f"GP{gp}"
    name = PICO_NAMES[phys - 1]
    if name == "GND":
        return "gnd", "Ground", name
    cat, note = FIXED[phys]
    return cat, note, name


def build():
    card = Card(W, H, "Raspberry Pi Pico 40-pin pinout and GPIO allocation",
                "Role colours from firmware/pico/config.py, table from the connection map section 1")
    pins = pico_header_pins(OX, OY)
    card.add(pico_header(OX, OY, "Pico (USB at top)"))
    over = []
    for phys in range(1, 41):
        cat, note, label = _pin_cat(phys)
        px, py = pins.xy(phys)
        side = "L" if phys <= 20 else "R"
        tag, x0, x1 = _tag(px, py, label, cat, side)
        over.append(tag)
        if side == "L":
            over.append(_t(x0 - 6, py + 3, note, 9, "end", PALETTE["text"]))
            fx = x0 - 6 - len(note) * 5.4 - 6
        else:
            over.append(_t(x1 + 6, py + 3, note, 9, "start", PALETTE["text"]))
            fx = x1 + 6 + len(note) * 5.4 + 6
        if label in ("GP0", "GP1"):
            over.append(_flag(fx, py, "UNVERIFIED", "end" if side == "L" else "start"))
    card.add("".join(over))

    # ---- allocation table
    ty = 62
    card.add(f'<rect x="{TX - 8}" y="{ty}" width="{W - TX - 14}" height="{ROW_H * (len(ROLES) + 1) + 6}" '
             f'rx="4" fill="#fff" stroke="{PALETTE["stroke"]}" stroke-width="1"/>')
    cols = {"gpio": TX, "pin": TX + 46, "func": TX + 84, "dir": TX + 290, "dest": TX + 330,
            "status": TX + 570}
    hy = ty + 14
    for key, txt in (("gpio", "GPIO"), ("pin", "Pin"), ("func", "Function"), ("dir", "Dir"),
                     ("dest", "Destination"), ("status", "Status")):
        card.add(_t(cols[key], hy, txt, 10, "start", PALETTE["title"], True))
    card.add(_line(TX - 4, hy + 5, W - 22, hy + 5, PALETTE["stroke"], 1))
    for i, (gp, r) in enumerate(ROLES.items()):
        y = hy + 5 + ROW_H * (i + 1) - 4
        card.add(f'<rect x="{TX - 4}" y="{y - 11}" width="5" height="14" fill="{COL[r["cat"]]}"/>')
        card.add(_t(cols["gpio"] + 4, y, f"GP{gp}", 9, "start", PALETTE["title"], True))
        card.add(_t(cols["pin"], y, r["pin"], 9))
        card.add(_t(cols["func"], y, r["func"], 9))
        card.add(_t(cols["dir"], y, r["dir"], 9))
        card.add(_t(cols["dest"], y, r["dest"], 9))
        card.add(_t(cols["status"], y, r["status"], 9, "start",
                    "#1a6b2a" if r["status"] == "Used" else "#8a5a00", True))

    # ---- power rows
    py0 = ty + ROW_H * (len(ROLES) + 1) + 30
    card.add(_t(TX - 4, py0 - 6, "Power and ground pins", 10, "start", PALETTE["title"], True))
    for i, (nm, pin, desc, d) in enumerate(POWER_ROWS):
        y = py0 + 12 + i * ROW_H
        cat = {"3V3": "3v3", "VSYS": "5v", "VBUS": "5v", "GND": "gnd"}[nm]
        card.add(f'<rect x="{TX - 4}" y="{y - 11}" width="5" height="14" fill="{COL[cat]}"/>')
        card.add(_t(cols["gpio"] + 4, y, nm, 9, "start", PALETTE["title"], True))
        card.add(_t(cols["pin"] + 2, y, pin, 9))
        card.add(_t(cols["func"] + 128, y, desc, 9))
    ny = py0 + 12 + len(POWER_ROWS) * ROW_H + 6
    card.add(_t(TX - 4, ny + 8, "3V3_EN, RUN, ADC_VREF, AGND: no connection in this design's "
                "allocation table", 9, "start", PALETTE["muted"]))

    # ---- notes (left, under the header)
    ny0 = OY + 20 * 14 + 22
    notes = [
        ("PWM slice note", [
            "GP26 shares PWM slice 5A with GP10 (RGB blue, 1 kHz):",
            "do not use GP26 as a PWM DAC while GP10 drives the LED.",
            "GP27 is slice 5B and follows GP10's 1 kHz slice frequency."]),
        ("Main OLED, Keyestudio IIC/SPI V2.0, SPI mode", [
            "Write-only (no MISO), 3V3 logic, powered from the 3V3 pin.",
            "7-pin SPI-only board; chip (SSD1306 or SH1106), pin order: UNVERIFIED.",
            "CS strapped to GND (no GPIO): PROVISIONAL (BT-14).",
            "No I2C on the expander, so no pull-ups. Driver: display.py."]),
        ("Not usable", [
            "GP23, GP24, GP25, GP29 are RP2040 internal: not on the header.",
            "Free: GP26-GP28 only (not fault tolerant). GP11 (fault tolerant)",
            "is the gate input, PROVISIONAL (BT-14): fallback GP27/GP28 + BT-5."]),
    ]
    y = ny0
    for title, lines in notes:
        h = 22 + 12 * len(lines)
        card.add(f'<rect x="30" y="{y}" width="560" height="{h}" rx="4" fill="#fff" '
                 f'stroke="{PALETTE["stroke"]}" stroke-width="1"/>'
                 + _t(40, y + 14, title, 10, "start", PALETTE["title"], True))
        for j, ln in enumerate(lines):
            card.add(_t(40, y + 27 + 12 * j, ln, 9, "start", PALETTE["text"]))
        y += h + 8

    card.legend([(COL["uart0"], "UART0 to LPC bridge"), (COL["oled"], "SPI0 main OLED"),
                 (COL["led"], "RGB LED"), (COL["button"], "Tap button"),
                 (COL["encoder"], "Encoder"), (COL["clkdiv"], "Clock divider out"),
                 (COL["aux"], "Aux out"), (COL["clock_in"], "Clock in"),
                 (COL["clock_out"], "Clock out"), (COL["gate_in"], "Gate in"),
                 (COL["free"], "Free"),
                 (COL["3v3"], "3V3"), (COL["5v"], "5 V (VSYS, VBUS)"),
                 (COL["gnd"], "GND"), (COL["other"], "Not used")])
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
