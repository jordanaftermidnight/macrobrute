# MACROBRUTE — Pico WH GPIO Pinout (Final)

Matches `firmware/pico/config.py`. All assignments verified against
RP2040 datasheet for peripheral conflicts.

## Phase 0 Bench-Validation Wiring

The two diagrams above show the same Phase 0 circuit two ways:

- **Schematic** — flat view, elbow-routed nets, useful for understanding *what* connects to *what*.
- **Breadboard layout** — top-down view with the Pico straddling the centre channel and jumper paths colour-coded; useful for actually wiring it on the bench.

Phase 0 covers: 0.96″ SSD1306 OLED · KY-040 rotary encoder · tap button · RGB LED (3× 220 Ω) · clock IN/OUT (1 kΩ + 5 V1 zener clamp on IN). Power comes from USB; +3V3 and GND are bridged to both top and bottom breadboard rails so peripherals can pull from the closer side.

## Pin Assignment Table

| GPIO | Pin# | Function | Interface | Direction | Notes |
|------|------|----------|-----------|-----------|-------|
| GP0 | 1 | LPC2361 TX | UART0 | Out | Pico Bridge → LPC2361 RXD1 (P0.16) |
| GP1 | 2 | LPC2361 RX | UART0 | In | Pico Bridge ← LPC2361 TXD1 (P0.15) |
| GP4 | 6 | OLED SDA | I2C0 | In/Out | 0.96″ SSD1306 main (0x3C) + 0.91″ SSD1306 strip (0x3D) — shared bus |
| GP5 | 7 | OLED SCL | I2C0 | Out | 0.96″ SSD1306 main (0x3C) + 0.91″ SSD1306 strip (0x3D) — shared bus |
| GP8 | 11 | LED Clock | PWM4A | Out | Pulse on each clock tick |
| GP9 | 12 | LED Gate | PWM4B | Out | Gate activity indicator |
| GP10 | 14 | LED Mode | PWM5A | Out | Mode indicator |
| GP12 | 16 | Tap Button | GPIO | In | Pull-up, active LOW |
| GP13 | 17 | Encoder SW | GPIO | In | Pull-up, active LOW, IRQ |
| GP14 | 19 | Encoder CLK | GPIO | In | Pull-up, IRQ on edges |
| GP15 | 20 | Encoder DT | GPIO | In | Pull-up |
| GP21 | 27 | Clock In | GPIO/PIO | In | External clock, IRQ rising |
| GP22 | 29 | Clock Out | PIO | Out | Clock output to expander |
| GP26 | 31 | ADC0 | ADC | In | Spare — CV reading |
| GP27 | 32 | ADC1 | ADC | In | Spare |
| GP28 | 34 | ADC2 | ADC | In | Spare |

## Peripheral Allocation

| Peripheral | Usage | Pins |
|------------|-------|------|
| UART0 | LPC2361 Pico Bridge (115200 baud) | GP0, GP1 |
| I2C0 | OLED display (SSD1306, 0x3C main + 0x3D strip) | GP4, GP5 |
| PIO SM0 | Clock output | GP22 |
| ADC | CV reading (spare) | GP26-28 |
| PWM4 | LEDs (clock, gate) | GP8, GP9 |
| PWM5 | LED (mode) | GP10 |

## Free GPIO

| GPIO | Pin# | Available For |
|------|------|---------------|
| GP2 | 4 | **I2C1 SDA — Daisy Seed expansion (rear JST-XH header)** |
| GP3 | 5 | **I2C1 SCL — Daisy Seed expansion (rear JST-XH header)** |
| GP6 | 9 | General purpose — expansion |
| GP7 | 10 | General purpose — expansion |
| GP11 | 15 | General purpose — expansion |
| GP16 | 21 | Free |
| GP17 | 22 | Free |
| GP18 | 24 | Free |
| GP19 | 25 | Free |
| GP20 | 26 | Free |

Potential uses for GP16–GP20: SD card (SPI), extra encoders, expansion header, SPI DAC.

## I²C1 Daisy Seed Expansion (rear header)

The Pico exposes I²C1 on GP2/GP3 to a rear-mounted 4-pin JST-XH header on the
expander (not panel-visible — accessed with the case open). This lets a Daisy
Seed module attach as an I²C peripheral for DSP offload (granular, reverb,
wavetable) while the Pico handles UI/clock.

| JST pin | Signal | Pico side | Notes |
|---------|--------|-----------|-------|
| 1 | SDA   | GP2 (pin 4) | 4.7kΩ pull-up to 3.3V on Pico side |
| 2 | SCL   | GP3 (pin 5) | 4.7kΩ pull-up to 3.3V on Pico side |
| 3 | +3.3V | Pico 3V3 pin 36 | Only used for header pull-ups; Daisy has its own rail |
| 4 | GND   | Star ground @ TP72 | Shared reference |

Addresses: OLED @ 0x3C (I²C0) · Daisy @ 0x42 by convention (I²C1) · MPR121 (if
fitted) @ 0x5A. Bus length < 30cm at 100kHz.

## USB-MIDI (micro-USB)

Pico WH enumerates as a USB-MIDI class device over its micro-USB port via
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
