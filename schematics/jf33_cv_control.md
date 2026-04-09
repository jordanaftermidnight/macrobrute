# JF-33 Analog Delay — CV Control & Eurorack Integration

## Overview

The Joyo JF-33 uses a PT2399 delay chip. This design adds:
1. CV control of delay time (NPN current sink)
2. CV control of feedback (via pot replacement or SSI2164 VCA)
3. Eurorack level matching (input attenuation, output amplification)
4. Anti-latch-up protection (CRITICAL)

---

## 1. Anti-Latch-Up Protection (BUILD THIS FIRST)

**If PT2399 pin 6 sees < 2kΩ to ground during power-on, it latches
permanently.** This circuit holds pin 6 high-impedance during startup.

```
                    +5V (from JF-33's 78L05)
                     │
                   100kΩ
                     │
  PT2399 pin 6 ──────┤
  (delay time)       │
                   BC337 Collector ──── CV control circuit (below)
                     │
                   BC337 Base ──[100kΩ]──┬── +5V
                     │                    │
                   BC337 Emitter         1µF (timing cap)
                     │                    │
                    GND                  GND

  Startup sequence:
    t=0: Power on. 1µF charges through 100kΩ.
         BC337 base near 0V → OFF → pin 6 sees only 100kΩ pull-up → SAFE.
    t≈100ms: Cap charges to ~0.63V. BC337 starts turning on.
    t≈500ms: BC337 fully saturated. CV control circuit connected.
    t≈1s: Fully operational.

  Time constant: 100kΩ × 1µF = 100ms (0.63V threshold)
  Full saturation: ~3-5 time constants = 300-500ms
```

**Testing:** Power cycle with no CV applied. If PT2399 produces normal
delay on first power-up, anti-latch-up is working.

---

## 2. Delay Time CV Control (NPN Current Sink)

Controls the current flowing out of PT2399 pin 6, which sets the
internal VCO frequency and thus the delay time.

```
                         Anti-latch-up
                         BC337 collector
                              │
  PT2399 Pin 6 ──────────────┤
                              │
                        ┌─────┴─────┐
                        │ TL072 A   │
  CV In ──[100kΩ]──┬────┤  +in      │
  (0-5V)           │    │           │── out ── [1kΩ] ── 2N3904 Base
                  pot   │  -in ◄────┤                     │
                 100kΩ  │           │               2N3904 Collector
                   │    └───────────┘                     │
                  GND         │                     [220Ω] (emitter R)
                              │                           │
                        1N4148 cathode ── pin 6          GND
                        1N4148 anode ── GND
                        (protection: prevents
                         reverse current into pin 6)

  Transfer function:
    V_cv (0-5V) → pot scales → TL072 buffer → 2N3904 sinks current
    I_pin6 = V_emitter / 220Ω
    At 5V CV (full): ~20mA (clamped by 220Ω) → ~35ms delay (shortest)
    At 0V CV: ~0mA → delay set by original timing resistor → ~600ms

  CRITICAL:
    - Max current through pin 6 must not exceed 5.4mA for normal operation
    - Change emitter R to 1kΩ for safer range (max ~5mA)
    - Or add 2.2kΩ in series with collector (limits total current)
```

**Corrected emitter resistor: 1kΩ** (max I = 5V/1kΩ = 5mA, within safe range)

---

## 3. Feedback CV Control

### Option A: Replace feedback pot with vactrol

```
  Original feedback pot connections:
    Lug 1 ── delay output
    Wiper ── feedback input
    Lug 3 ── GND

  Replace pot with:
    Delay output ──── Vactrol LDR ──── feedback input
                          │
    CV In ──[1kΩ]── Vactrol LED anode
                          │
                    Vactrol LED cathode
                          │
                       [1kΩ] (current limit)
                          │
                         GND

  Pro: Simple, isolated
  Con: Slow response (~50ms), nonlinear
```

### Option B: SSI2164 VCA (professional quality)

```
                         +5V
                          │
  Delay output ── [10kΩ] ── SSI2164 signal in (pin 1)
                              │
  CV In ── [33kΩ] ────────── SSI2164 CV in (pin 2)
  (0-5V)                      │ (control law: -33mV/dB)
                              │
  SSI2164 signal out (pin 3) ── [10kΩ] ── feedback input
                              │
                         SSI2164 V+ = +5V
                         SSI2164 GND = GND

  One SSI2164 has 4 VCA channels:
    Ch 1: Feedback amount
    Ch 2: Wet/dry mix
    Ch 3-4: Spare (use for tremolo, sidechain, etc.)
```

---

## 4. Eurorack Level Matching

### Input Attenuation (~20dB: 10Vpp → 1Vpp)

```
  Eurorack audio ──[100kΩ]──┬── to JF-33 input
  (±5V, 10Vpp)              │
                           10kΩ
                             │
                            GND

  Attenuation: 10k / (100k + 10k) = 0.091 → ~21dB
  Output: ~0.9Vpp (within PT2399's 1Vrms limit)
```

### Output Amplification (~20dB: ~0.5Vpp → 5Vpp)

```
                    +12V
                     │
               ┌─────┤
               │   ┌──┴──┐
  JF-33 out ───┤   │     │
    via 1µF    │   │TL072├─── Delay OUT jack
    AC couple  ├───┤+ A  │    (Eurorack level)
               │   │     │
               │   └──┬──┘
               │      │
             10kΩ   100kΩ (feedback)
             to GND   │
                      │
                    output

  Gain: 1 + (100k/10k) = 11 → ~21dB
  Output: ~5.5Vpp from 0.5Vpp input
```

### DC offset removal: 1µF cap at input (already shown above)

---

## 5. PT2399 Glitch/Bend Points

For switched circuit bending on the PT2399:

```
  Pin 6 ──[1MΩ]── Pin 8     Gentle warble / spatial effect
  Pin 6 ──[pot 0-1MΩ]── Pin 7   Variable glitch intensity
  Pin 7 ──[LED to GND]          Soft input limiter at ~2V

  Havoc switch (momentary):
    Feedback pot wiper ──[SPST momentary]── Delay output
    Effect: Instant 100% feedback → self-oscillation
    For CV control: Replace SPST with 2N7000 MOSFET gate
      Gate driven by Eurorack gate input via voltage divider

  Freeze/hold (experimental):
    Inject clock signal into pin 5 (VCO out) to lock the delay buffer
    Use 555 timer or Pico GPIO at ~10-50kHz
    CAUTION: This can damage the PT2399 if overdone
```

---

## 6. Power

```
  +12V (Eurorack) ── [7809] ── +9V ── JF-33 power input
                                │
                          100µF + 100nF
                                │
                               GND

  Current draw: ~40-60mA
  7809 dissipation: (12-9) × 0.06 = 0.18W (no heatsink needed)

  Note: JF-33 has onboard 78L05 for PT2399 5V supply.
  The 7809 feeds the 78L05, which handles PT2399 regulation.
```

---

## Component Summary

| Component | Qty | Purpose |
|-----------|-----|---------|
| TL072CP | 1 | CV buffer, output amp |
| SSI2164 | 1 | VCA for feedback/mix (optional) |
| 2N3904 | 1 | Current sink |
| BC337 | 1 | Anti-latch-up switch |
| 1N4148 | 2 | Protection diodes |
| 7809 | 1 | 9V regulator |
| 100kΩ | 4 | Attenuator, timing, bias |
| 10kΩ | 3 | Divider, gain |
| 1kΩ | 4 | Current limit, series protect |
| 220Ω / 1kΩ | 1 | Emitter resistor |
| 1µF film | 2 | AC coupling, anti-latch timing |
| 100µF electrolytic | 1 | Power filter |
| 100nF ceramic | 3 | Decoupling |
| 100kΩ pot | 1 | CV attenuator |
