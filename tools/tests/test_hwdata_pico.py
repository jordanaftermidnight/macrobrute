from pathlib import Path
from tools.hwdata.pico import (
    PICO_PHYSICAL_PIN, PICO_USABLE_GP, FIRMWARE_ROLES, load_firmware_gpio,
)

CONFIG = Path(__file__).resolve().parents[2] / "firmware/pico/config.py"

def test_physical_pins_match_pico_datasheet():
    assert PICO_PHYSICAL_PIN[0] == 1 and PICO_PHYSICAL_PIN[1] == 2
    assert PICO_PHYSICAL_PIN[4] == 6 and PICO_PHYSICAL_PIN[22] == 29
    assert PICO_PHYSICAL_PIN[28] == 34

def test_unexposed_gpios_are_not_usable():
    assert not ({23, 24, 25, 29} & PICO_USABLE_GP)

def test_firmware_roles_match_config_py():
    cfg = load_firmware_gpio(CONFIG)
    for role, gp in FIRMWARE_ROLES.items():
        assert cfg[role] == gp, role

def test_no_gpio_assigned_twice():
    flat = []
    for gp in FIRMWARE_ROLES.values():
        flat.extend(gp if isinstance(gp, tuple) else (gp,))
    assert len(flat) == len(set(flat))


def test_main_oled_is_spi0_on_the_decided_pins():
    # owner ruling 2026-10-17: 7-pin SPI 1.3" OLED is the baseline main display
    assert FIRMWARE_ROLES["OLED_SCK"] == 2 and FIRMWARE_ROLES["OLED_MOSI"] == 3
    assert FIRMWARE_ROLES["OLED_CS"] == 11
    assert FIRMWARE_ROLES["OLED_DC"] == 4 and FIRMWARE_ROLES["OLED_RES"] == 5
    assert not any(k.startswith("DAISY") or k in ("OLED_SDA", "OLED_SCL")
                   for k in FIRMWARE_ROLES)
