# MACROBRUTE — Pico WH GPIO Pinout (Final)

Matches `firmware/pico/config.py` and `docs/MACROBRUTE_CONNECTION_MAP.md` section 1.
Pico variant: the docs say Pico WH; UNVERIFIED, owner to confirm.

## Phase 0 Bench-Validation Wiring

The two Phase 0 diagrams, `schematics/phase0_wiring_schematic.svg` and `schematics/phase0_breadboard.svg` (not embedded in this file), show the same Phase 0 circuit two ways:

- **Schematic** (`phase0_wiring_schematic.svg`) — flat view, elbow-routed nets, useful for understanding *what* connects to *what*.
- **Breadboard layout** (`phase0_breadboard.svg`) — top-down view with the Pico straddling the centre channel and jumper paths colour-coded; useful for actually wiring it on the bench.

Phase 0 covers: **one OLED on I²C0** (main display at `0x3C`; the 0.91″ strip OLED is dropped). Main OLED baseline (owner, 2026-10-17): the owner's 1.3″ 4-pin I²C module, controller likely SH1106 (UNVERIFIED); a 1.3″ 7-pin SPI module is a spare. `config.py` and the display driver still describe a 0.96″ SSD1306; that change is a firmware task · KY-040 rotary encoder · tap button · RGB LED (3× 220 Ω) · clock IN/OUT (1 kΩ inline). Power comes from USB; +3V3 and GND are bridged to both top and bottom breadboard rails so peripherals can pull from the closer side.

## Pin Assignment Table

| GPIO | Pin# | Function | Interface | Direction | Notes |
|------|------|----------|-----------|-----------|-------|
| GP0 | 1 | LPC2361 TX | UART0 | Out | Pico Bridge → LPC2361 RXD1 (P0.16, pin 63; UNVERIFIED until the Phase 0 continuity check) |
| GP1 | 2 | LPC2361 RX | UART0 | In | Pico Bridge ← LPC2361 TXD1 (P0.15, pin 62; UNVERIFIED) |
| GP2 | 4 | Free, reserved | — | — | config.py still names it I²C1 SDA for the shelved EFFIGY code |
| GP3 | 5 | Free, reserved | — | — | config.py still names it I²C1 SCL for the shelved EFFIGY code |
| GP4 | 6 | OLED SDA | I2C0 | In/Out | Main OLED (0x3C; 1.3″ I²C module, controller UNVERIFIED), the only device on I2C0 |
| GP5 | 7 | OLED SCL | I2C0 | Out | Main OLED (0x3C); code runs 400 kHz |
| GP6 | 9 | Aux output 3 | GPIO/PWM3A | Out | Programmable aux jack |
| GP7 | 10 | Aux output 4 | GPIO/PWM3B | Out | Programmable aux jack |
| GP8 | 11 | LED Clock | PWM4A | Out | Pulse on each clock tick |
| GP9 | 12 | LED Gate | PWM4B | Out | Gate activity indicator |
| GP10 | 14 | LED Mode | PWM5A | Out | Mode indicator |
| GP11 | 15 | Free, reserved | — | — | config.py still names it EFFIGY INT (shelved); candidate gate input |
| GP12 | 16 | Tap Button | GPIO | In | Pull-up, active LOW |
| GP13 | 17 | Encoder SW | GPIO | In | Pull-up, active LOW, IRQ |
| GP14 | 19 | Encoder CLK | GPIO | In | Pull-up, IRQ on edges |
| GP15 | 20 | Encoder DT | GPIO | In | Pull-up |
| GP16 | 21 | Clock divider out 1 | GPIO | Out | Default ÷2 |
| GP17 | 22 | Clock divider out 2 | GPIO | Out | Default ÷4 |
| GP18 | 24 | Clock divider out 3 | GPIO | Out | Default ÷8 |
| GP19 | 25 | Aux output 1 | GPIO/PWM1B | Out | Programmable aux jack |
| GP20 | 26 | Aux output 2 | GPIO/PWM2A | Out | Programmable aux jack |
| GP21 | 27 | Clock In | GPIO | In | External clock, IRQ rising; jack reaches it only through 100kΩ + CD4049UB (connection map section 4) |
| GP22 | 29 | Clock Out | GPIO | Out | Plain GPIO driven from a Timer (no PIO); to the jack through CD4049UB + 1kΩ |
| GP26 | 31 | ADC0 | ADC | In | Free (PWM slice 5A shared with GP10) |
| GP27 | 32 | ADC1 | ADC | In | Free |
| GP28 | 34 | ADC2 | ADC | In | Free |

## Peripheral Allocation

| Peripheral | Usage | Pins |
|------------|-------|------|
| UART0 | LPC2361 Pico Bridge (115200 baud) | GP0, GP1 |
| I2C0 | Main OLED display (0x3C; config.py says SSD1306, owner module likely SH1106, UNVERIFIED) | GP4, GP5 |
| GPIO (Timer) | Clock output | GP22 |
| GPIO | Clock input, clock divider outputs | GP21; GP16, GP17, GP18 |
| GPIO/PWM | Aux outputs (PWM at 20 kHz in PWM_CV mode) | GP19, GP20, GP6, GP7 |
| ADC | Free | GP26-28 |
| PWM4 | LEDs (clock, gate) | GP8, GP9 |
| PWM5 | LED (mode) | GP10 |

## Free GPIO

6 free pins (owner decision, 2026-10-17):

| GPIO | Pin# | Type | Note |
|------|------|------|------|
| GP2 | 4 | Digital, fault tolerant | Was EFFIGY I²C1 SDA (shelved) |
| GP3 | 5 | Digital, fault tolerant | Was EFFIGY I²C1 SCL (shelved) |
| GP11 | 15 | Digital, fault tolerant | Was EFFIGY INT (shelved); candidate gate input |
| GP26 | 31 | ADC0, not fault tolerant | PWM slice 5A shared with GP10 |
| GP27 | 32 | ADC1, not fault tolerant | — |
| GP28 | 34 | ADC2, not fault tolerant | — |

GP6, GP7, GP16, GP17, GP18, GP19 and GP20 are NOT free: they are the aux outputs and clock divider outputs above.
GP23, GP24, GP25 and GP29 are RP2040-internal and not exposed on the header.

## I²C1 EFFIGY / Daisy Seed Expansion — SHELVED

SHELVED (2026-10-17): the EFFIGY pairing is kept as an idea for another project and is not part
of this build. No rear JST-XH header is fitted; GP2, GP3 and GP11 are free (table above).

## USB-MIDI (micro-USB)

Pico enumerates as a USB-MIDI class device over its micro-USB port via
TinyUSB. Orthogonal to the LPC2361 bridge — gives the DAW/computer a MIDI
port named "Macrobrute Pico". Firmware hook: `firmware/pico/usbmidi.py` (to
be implemented).

Important: Pico does **not** drive 5-pin DIN MIDI at 31250 baud. The stock
DIN jack goes to the LPC2361 via 6N138 optocoupler (unchanged).

## Hardware Debounce

External RC filter on encoder pins (recommended):
```
  Each of GP13, GP14, GP15:
    Pin ──[10kΩ]──┬── Pico GPIO (with internal pull-up)
                   │
                 100nF
                   │
                  GND
```

Tap button GP12: Same RC filter.
