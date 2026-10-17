"""Canonical Raspberry Pi Pico pin data. Firmware config.py is the source of truth for roles."""
import ast
from pathlib import Path

PICO_PHYSICAL_PIN = {
    0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
    10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
    18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34,
}
# GPIOs brought out on the 40-pin header (GP23-25 and GP29 are board-internal).
# "Usable" means exposed, not free: free = PICO_USABLE_GP minus FIRMWARE_ROLES.
PICO_USABLE_GP = frozenset(PICO_PHYSICAL_PIN)

FIRMWARE_ROLES = {
    "LPC_TX": 0, "LPC_RX": 1,
    "OLED_SCK": 2, "OLED_MOSI": 3,
    "OLED_DC": 4, "OLED_RES": 5,
    "AUX_OUT_PINS": (19, 20, 6, 7),
    "LED_CLOCK": 8, "LED_GATE": 9, "LED_MODE": 10,
    "GATE_IN": 11, "BTN_TAP": 12,   # OLED CS is strapped to GND (BT-14)
    "ENC_SW": 13, "ENC_CLK": 14, "ENC_DT": 15,
    "CLK_DIV_PINS": (16, 17, 18),
    "CLOCK_IN": 21, "CLOCK_OUT": 22,
}


def load_firmware_gpio(config_path):
    """Return {NAME: int | tuple[int]} for literal assignments in config.py."""
    out = {}
    tree = ast.parse(Path(config_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            try:
                val = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
            if name and isinstance(val, (int, tuple)):
                out[name] = val
    return out
