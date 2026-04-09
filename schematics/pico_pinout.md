# MACROBRUTE — Pico H GPIO Pinout (Final)

Matches `firmware/pico/config.py`. All assignments verified against
RP2040 datasheet for peripheral conflicts.

```
                        ┌──────────────────┐
              UART0 TX  │ GP0          VBUS │ ── USB 5V (not used)
  LPC2361 ◄── UART0 RX │ GP1          VSYS │ ── +5V from MB (via 1N5817)
                        │ GND           GND │
                        │ GP2          3V3E │
                        │ GP3          3V3O │ ── 3.3V out → OLED, encoder
           MIDI TX ──── │ GP4  UART1   GP28 │   ADC2 (spare)
           MIDI RX ──── │ GP5  UART1   GND  │
                        │ GND          GP27 │   ADC1 (spare)
                        │ GP6          GP26 │   ADC0 (spare)
                        │ GP7          RUN  │
        LED Clock ──── │ GP8          GP22 │ ── Clock Out (PIO)
         LED Gate ──── │ GP9          GND  │
         LED Mode ──── │ GP10         GP21 │ ── Clock In (IRQ)
                        │ GP11         GP20 │ ── OLED RST
       Tap Button ──── │ GP12         GP19 │ ── OLED MOSI (SPI0 TX)
        Enc. SW   ──── │ GP13         GP18 │ ── OLED SCK (SPI0 SCK)
        Enc. CLK  ──── │ GP14         GND  │
        Enc. DT   ──── │ GP15         GP17 │ ── OLED CS (SPI0 CSn)
                        │ GND          GP16 │ ── OLED DC
                        │              ● ● │   DEBUG (SWD)
                        └──────────────────┘
```

## Pin Assignment Table

| GPIO | Pin# | Function | Interface | Direction | Notes |
|------|------|----------|-----------|-----------|-------|
| GP0 | 1 | LPC2361 TX | UART0 | Out | Future — firmware RE |
| GP1 | 2 | LPC2361 RX | UART0 | In | Future — firmware RE |
| GP4 | 6 | MIDI TX | UART1 | Out | 31250 baud, SysEx to MB |
| GP5 | 7 | MIDI RX | UART1 | In | 31250 baud |
| GP8 | 11 | LED Clock | PWM4A | Out | Pulse on each clock tick |
| GP9 | 12 | LED Gate | PWM4B | Out | Gate activity indicator |
| GP10 | 14 | LED Mode | PWM5A | Out | Mode indicator |
| GP12 | 16 | Tap Button | GPIO | In | Pull-up, active LOW |
| GP13 | 17 | Encoder SW | GPIO | In | Pull-up, active LOW, IRQ |
| GP14 | 19 | Encoder CLK | GPIO | In | Pull-up, IRQ on edges |
| GP15 | 20 | Encoder DT | GPIO | In | Pull-up |
| GP16 | 21 | OLED DC | GPIO | Out | Data/Command select |
| GP17 | 22 | OLED CS | SPI0 CSn | Out | Chip select |
| GP18 | 24 | OLED SCK | SPI0 SCK | Out | SPI clock |
| GP19 | 25 | OLED MOSI | SPI0 TX | Out | SPI data |
| GP20 | 26 | OLED RST | GPIO | Out | Display reset |
| GP21 | 27 | Clock In | GPIO/PIO | In | External clock, IRQ rising |
| GP22 | 29 | Clock Out | PIO | Out | Clock output to expander |
| GP26 | 31 | ADC0 | ADC | In | Spare — CV reading |
| GP27 | 32 | ADC1 | ADC | In | Spare |
| GP28 | 34 | ADC2 | ADC | In | Spare |

## Peripheral Allocation

| Peripheral | Usage | Pins |
|------------|-------|------|
| UART0 | LPC2361 comms (future) | GP0, GP1 |
| UART1 | MIDI I/O | GP4, GP5 |
| SPI0 | OLED display | GP16-20 |
| PIO SM0 | Clock output | GP22 |
| ADC | CV reading (spare) | GP26-28 |
| PWM4 | LEDs (clock, gate) | GP8, GP9 |
| PWM5 | LED (mode) | GP10 |

## Unused GPIOs

| GPIO | Available For |
|------|---------------|
| GP2, GP3 | I2C0 (SDA/SCL) — could drive second OLED or I2C DAC |
| GP6, GP7 | General purpose — future expansion |
| GP11 | General purpose |

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
