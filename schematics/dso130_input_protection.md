# DSO138 Input Protection & Signal Multiplexer

> **⚠️ PROPOSED DESIGN — NOT IMPLEMENTED**
>
> This section documents an alternative design approach that was considered but **not used** in the final MACROBRUTE build.
>
> **Reason for exclusion:** DB-9 connector limitations (insufficient pins for oscilloscope integration) and aesthetic concerns (preferring a clean expander panel over additional front-panel displays).
>
> The final design uses the **OLED display** (SH1122 256x64) for signal visualization instead. See [Control & Interface](/#cat-control) section for the implemented solution.

---

## Input Protection (Eurorack ±12V → DSO138 safe range)

The DSO138's ADC accepts 0-3.3V. Eurorack signals can reach ±10V.
This circuit scales and offsets the input.

### Protection + Scaling Circuit

```
  Eurorack Signal ──[1kΩ ½W]──┬── BAT54S to ±5V rails (clamp)
  (±10V max)                   │
                               │
                         ┌─────┴─────┐
                    100kΩ│  TL072 A  │
                    from │   -in     │
                    input│           │── out ──── to CD4051 input
                         │   +in     │
                         └─────┬─────┘
                               │
                         47kΩ  │  47kΩ (feedback)
                         to    │
                        +1.65V │
                        bias   │
                               │
                         Voltage divider:
                         +3.3V ──[10kΩ]──┬──[10kΩ]── GND
                                         │
                                       +1.65V bias

  Transfer function:
    V_out = 1.65 - (V_in × 47k/100k)
    +10V in → 1.65 - 4.7 = clamped at 0V (BAT54S catches)
    -10V in → 1.65 + 4.7 = clamped at 3.3V
    Useful range: ±3.5V → 0 to 3.3V

  For ±5V range (most useful):
    V_out = 1.65 - (V_in × 47k/100k)
    +5V → 0.3V,  -5V → 3.0V
    Full ADC range used.
```

### CD4051 Signal Multiplexer (6-input selector)

Select which signal feeds the oscilloscope. Controlled by Pico
or a 6-position rotary switch.

```
                              +5V
                               │
                         ┌─────┴─────┐
  Signal 0 (Saw) ──[1kΩ]─┤ X0  COM  ├── out ──[TL072 buffer]── DSO138 IN
  Signal 1 (Sqr) ──[1kΩ]─┤ X1       │
  Signal 2 (Mix) ──[1kΩ]─┤ X2       │
  Signal 3 (VCF) ──[1kΩ]─┤ X3       │
  Signal 4 (LFO) ──[1kΩ]─┤ X4       │
  Signal 5 (Env) ──[1kΩ]─┤ X5       │
  (spare)         ──[10kΩ to GND]─┤ X6  │
  (spare)         ──[10kΩ to GND]─┤ X7  │
                         │         │
  Select A ──────────────┤ A       │
  Select B ──────────────┤ B       │
  Select C ──────────────┤ C       │
  INH ── GND             │ INH     │
                         │ VDD=+5V │
                         │ VEE=GND │
                         │ VSS=GND │
                         └─────────┘
```

**Selection with 6-position rotary switch:**
```
  Position → A B C
  0 (Saw)    0 0 0
  1 (Sqr)    1 0 0
  2 (Mix)    0 1 0
  3 (VCF)    1 1 0
  4 (LFO)    0 0 1
  5 (Env)    1 0 1

  Rotary switch common → GND
  Position contacts → pull-up 10kΩ to +5V, active LOW to CD4051 address pins
```

**Or with Pico GPIO:** 3 GPIOs directly to A, B, C.

### DSO138 Power

```
  +12V Eurorack ──[7809 regulator]── +9V ── DSO138 power input
                                      │
                                   100µF + 100nF
                                      │
                                     GND

  DSO138 current draw: ~120-130mA at 9V
  7809 dissipation: (12-9) × 0.13 = 0.39W (fine without heatsink)
```

### Mounting

- DSO138 PCB dimensions: ~85mm x 65mm
- Mount behind panel with M3 standoffs (11mm)
- Cut rectangular window in panel for 2.4" TFT display
- Display window: ~38mm x 50mm (verify against your DSO138 build)
