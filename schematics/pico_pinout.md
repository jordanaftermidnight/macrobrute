# MACROBRUTE — Pico H GPIO Pinout (Final)

Matches `firmware/pico/config.py`. All assignments verified against
RP2040 datasheet for peripheral conflicts.

## Pin Assignment Table

| GPIO | Pin# | Function | Interface | Direction | Notes |
|------|------|----------|-----------|-----------|-------|
| GP0 | 1 | LPC2361 TX | UART0 | Out | Pico Bridge → LPC2361 RXD1 (P0.16) |
| GP1 | 2 | LPC2361 RX | UART0 | In | Pico Bridge ← LPC2361 TXD1 (P0.15) |
| GP4 | 6 | OLED SDA | I2C0 | In/Out | SSD1306 0.91" display |
| GP5 | 7 | OLED SCL | I2C0 | Out | SSD1306 0.91" display |
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
| I2C0 | OLED display (SSD1306, 0x3C) | GP4, GP5 |
| PIO SM0 | Clock output | GP22 |
| ADC | CV reading (spare) | GP26-28 |
| PWM4 | LEDs (clock, gate) | GP8, GP9 |
| PWM5 | LED (mode) | GP10 |

## Free GPIO (Previously SPI OLED)

| GPIO | Pin# | Available For |
|------|------|---------------|
| GP2 | 4 | I2C1 (SDA) — second I2C bus |
| GP3 | 5 | I2C1 (SCL) — second I2C bus |
| GP6 | 9 | General purpose — expansion |
| GP7 | 10 | General purpose — expansion |
| GP11 | 15 | General purpose — expansion |
| GP16 | 21 | Was OLED DC — now free |
| GP17 | 22 | Was OLED CS — now free |
| GP18 | 24 | Was OLED SCK — now free |
| GP19 | 25 | Was OLED MOSI — now free |
| GP20 | 26 | Was OLED RST — now free |

Potential uses for GP16-GP20: SD card (SPI), extra encoders, expansion header, SPI DAC.

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
