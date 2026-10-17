"""Phase 0 net definitions shared by the wiring card and the breadboard card.

Part names: PICO, OLED, LED, R (series resistors), BTN, ENC, JACK_*, JUMPER.
Pin numbers come from FIRMWARE_ROLES, never retyped.
"""
from tools.hwdata.pico import FIRMWARE_ROLES as R


def gp(role):
    return f"GP{R[role]}"


# ------------------------------------------------------------------ nets
# Part names: PICO, OLED, LED, R (series resistors), BTN, ENC, JACK_*, JUMPER.
NETS = {
    "3V3": [("PICO", "3V3"), ("OLED", "VCC"), ("ENC", "+")],
    "GND": [("PICO", "GND"), ("OLED", "GND"), ("LED", "K"), ("BTN", "2"),
            ("ENC", "GND"), ("JACK_OUT", "S"), ("JACK_IN", "S")],
    # main OLED, 7-pin SPI module on SPI0 (module pin names D0 = SCK, D1 = MOSI)
    "OLED_SCK": [("PICO", gp("OLED_SCK")), ("OLED", "D0")],
    "OLED_MOSI": [("PICO", gp("OLED_MOSI")), ("OLED", "D1")],
    "OLED_DC": [("PICO", gp("OLED_DC")), ("OLED", "DC")],
    "OLED_RES": [("PICO", gp("OLED_RES")), ("OLED", "RES")],
    "OLED_CS": [("PICO", gp("OLED_CS")), ("OLED", "CS")],
    "LED_R": [("PICO", gp("LED_CLOCK")), ("R", "220_R.a")],
    "LED_R_A": [("R", "220_R.b"), ("LED", "R_A")],
    "LED_G": [("PICO", gp("LED_GATE")), ("R", "220_G.a")],
    "LED_G_A": [("R", "220_G.b"), ("LED", "G_A")],
    "LED_B": [("PICO", gp("LED_MODE")), ("R", "220_B.a")],
    "LED_B_A": [("R", "220_B.b"), ("LED", "B_A")],
    "BTN_TAP": [("PICO", gp("BTN_TAP")), ("BTN", "1")],
    "ENC_SW": [("PICO", gp("ENC_SW")), ("ENC", "SW")],
    "ENC_CLK": [("PICO", gp("ENC_CLK")), ("ENC", "CLK")],
    "ENC_DT": [("PICO", gp("ENC_DT")), ("ENC", "DT")],
    "CLOCK_OUT": [("PICO", gp("CLOCK_OUT")), ("R", "1K_OUT.a")],
    "CLOCK_OUT_JACK": [("R", "1K_OUT.b"), ("JACK_OUT", "T"), ("JUMPER", "A")],
    "CLOCK_IN": [("PICO", gp("CLOCK_IN")), ("R", "1K_IN.a"), ("JUMPER", "B")],
    "CLOCK_IN_JACK": [("R", "1K_IN.b"), ("JACK_IN", "T")],
}
RAILS = {"3V3": 3.3}

# Phase 0 bench caveats shown on both Phase 0 cards
CLOCK_IN_NOTE = ("CLOCK IN: loop-back only, no external signals", "(no CD4049UB on the bench)")
MISSING_PARTS = ("MISSING: RGB LED (Q12)", "MISSING: tactile button (Q12)",
                 "MISSING: half-size breadboard")
RGB_ORDER = "UNVERIFIED: RGB lead order R-K-G-B"
