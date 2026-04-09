# MACROBRUTE Expander — Utility Circuit Schematics

All circuits powered from Eurorack ±12V bus.
100nF ceramic bypass cap on every IC power pin pair.

---

## 1. White Noise Generator (Thomas Henry / Yusynth method)

```
        +12V
         │
       470kΩ
         │
       470kΩ
         │
    ┌────┴────── 2N3904 Collector (cut off — no wire)
    │
    ├──── 2N3904 Base ────────────┐
    │                              │
    │    2N3904 Emitter            │
    │         │                    │
    │       [100pF] (optional HF boost)
    │         │                    │
    │        GND                  100kΩ (to TL072 -in)
    │                              │
    │                        ┌─────┴─────┐
    │                        │  TL072 A  │
    │                        │    -in ◄──┤── 4.7MΩ feedback
    │                        │    +in ── GND (via 100kΩ bias)
    │                        │    out ───┤
    │                        └───────────┘
    │                              │
    │                            [10kΩ]
    │                              │
    └──────────────────────────── NOISE OUT jack
```

**How it works:** 2N3904 base-emitter junction reverse-biased at ~8-9V
causes avalanche breakdown, generating broadband white noise (~5-10µVrms).
TL072 amplifies ~46-100x (set by 4.7MΩ/100kΩ ratio).

**Component values:**
- 2N3904: Cut collector lead short (prevents antenna effect)
- R_bias: 2x 470kΩ in series from +12V to base
- R_input: 100kΩ
- R_feedback: 4.7MΩ (gain = 47x)
- C_filter: 100pF across emitter-base (optional)
- Output ~5-8Vpp white noise

---

## 2. Triangle/Square LFO (TL072 integrator + Schmitt trigger)

```
           ┌──────────────────────────────────────────────┐
           │                                              │
           │    ┌─────────────────┐                       │
           │    │                 │                       │
           │    │   1µF (timing)  │                       │
           │    │    ┌────┤       │                       │
           │    │    │    │       │                       │
     ┌─────┴────┴────┤    │  ┌────┴────┐                  │
     │               │    │  │ TL072 A │                  │
     │          +in ──┤    └──┤  -in   │                  │
     │          (GND) │       │  out ──┼── TRIANGLE OUT   │
     │               │       └────────┘                  │
     │               │                                    │
     │         1MΩ Rate Pot                               │
     │          ┌────┤                                    │
     │          │    │                                    │
     │    ┌─────┴────┴───┐                                │
     │    │              │                                │
     │    │   TL072 B    │                                │
     │    │   +in ── ┬── │                                │
     │    │          │   │                                │
     │    │   -in ── ┼── │                                │
     │    │   out ───┤   │                                │
     │    └──────────┘   │                                │
     │         │         │                                │
     │         │       100kΩ (to +in from junction)       │
     │         │       100kΩ (to GND from +in)            │
     │         │         │                                │
     │         └─────────┼── SQUARE OUT (via 1.8kΩ divider)
     │                   │                                │
     └───────────────────┴────────────────────────────────┘
```

Simplified description:
```
  TL072 A = Integrator
    +in: virtual ground (GND via 100kΩ)
    -in: from square output via 1MΩ Rate pot
    feedback: 1µF capacitor
    output: Triangle wave (~10Vpp)

  TL072 B = Schmitt Trigger (comparator with hysteresis)
    +in: voltage divider from own output (100kΩ/100kΩ = ±Vsat/2 thresholds)
    -in: Triangle from TL072 A output
    output: Square wave (±~11V)

  Square output scaling:
    ±11V → voltage divider (3.3kΩ + 3.3kΩ) → ±5.25V Eurorack standard
    (REVIEWED: 1.8kΩ was too hot, corrected to 3.3kΩ for ±5V target)
```

**Rate range:** 1MΩ pot → ~0.04 Hz to ~40 Hz
**For wider range:** Add 10kΩ in series with pot (minimum rate limit)

---

## 3. Clock Divider (CD4024 7-stage binary counter)

```
                    +5V (from 78L05)
                     │
                   100nF
                     │
              ┌──────┴──────┐
              │    CD4024    │
  Clock In ───┤ pin 1 (CLK) │
              │              │
  +5V via ────┤ pin 2 (RST) │── 10kΩ to GND (keep LOW unless reset)
  momentary   │              │
  button      │ pin 3  Q1 ──┼── /2  OUT ──[1kΩ]── jack
              │ pin 4  Q2 ──┼── /4  OUT ──[1kΩ]── jack
              │ pin 5  Q3 ──┼── /8  OUT ──[1kΩ]── jack
              │ pin 6  Q4 ──┼── /16 (spare)
              │ pin 9  Q5 ──┼── /32 (spare)
              │ pin 11 Q6 ──┼── /64 (spare)
              │ pin 12 Q7 ──┼── /128 (spare)
              │              │
              │ pin 14 VDD ──┤── +5V
              │ pin 7  VSS ──┤── GND
              └──────────────┘

  Clock input conditioning:
  Eurorack gate (0-10V) ──[120kΩ]──┬──[100kΩ to GND]── ~4.2V max
                                    │
                                  CD40106 Schmitt ── CD4024 CLK
```

**LED indicators per output:**
```
  Q_out ──[1kΩ]── LED anode ── LED cathode ── GND
```

**Power:** CD4024 runs on +5V. Use 78L05 from +12V:
```
  +12V ──[78L05]──┬── +5V
                   │
                 100nF + 10µF
                   │
                  GND
```

---

## 4. Sample & Hold (LF398 or CD4066 + TL072)

### Using LF398 (preferred):
```
                    +12V
                     │
              ┌──────┴──────┐
  Signal In ──┤ pin 3 (IN+) │
              │ pin 2 (IN-) ├── output feedback
              │              │
  Clock ──────┤ pin 8 (L/S) │
  (gate)      │              │
              │ pin 5 (OUT) ├──┬── S&H OUT jack
              │              │  │
              │ pin 6 (HOLD)│  1nF polystyrene cap
              │              │  │
              │ pin 1 (OFF) │ GND
              │ pin 4 (V-)  │── -12V
              │ pin 7 (V+)  │── +12V
              └──────────────┘

  Hold capacitor: 1nF polystyrene (CRITICAL — low leakage)
  Never use ceramic or electrolytic — excessive droop
```

### Using CD4066 (simpler but more droop):
```
  Signal In ──[10kΩ]── CD4066 signal pin ──┬── TL072 follower ── S&H OUT
                                            │
  Clock ────── CD4066 control pin          1nF polystyrene
                                            │
                                           GND
```

**S&H Rate:** Use a separate astable (CD40106 oscillator) or tap clock divider.

---

## 5. Slew Limiter (TL072 + diode steering)

```
                          1MΩ log pot (RISE)
  Input ──[10kΩ]──┬──────[D1 1N4148 →]──────────┐
                   │                               │
                   │      1MΩ log pot (FALL)       │
                   └──────[← D2 1N4148]───────────┤
                                                   │
                                                   │
                                              ┌────┴────┐
                                              │ TL072 A │
                                         +in ─┤         ├── OUT
                                              │  -in ◄──┤
                                              └─────────┘
                                                   │
                                                  1µF (timing cap)
                                                   │
                                                  GND
```

**Separate rise/fall:** D1 passes positive-going signals through RISE pot,
D2 passes negative-going through FALL pot. Each pot independently controls
the slew rate for that direction.

**Single-pot version:** Replace both diodes and pots with single 1MΩ pot.

**Range:** 1µF cap → up to ~1s slew at max resistance

---

## 6. Attenuverter (TL072)

```
                    100kΩ (Rf)
              ┌────────────────────┐
              │                    │
  Input ──[100kΩ R1]──┬── TL072 -in    out ── OUTPUT
                       │         │
                      Pot wiper  │
                       │         │
            ┌──────────┤         │
            │    100kΩ center-detent pot
            │          │
            ├── to +in (GND via 100kΩ)
            │
     Pot CW end ── Input (via 100kΩ)
     Pot CCW end ── GND
```

Simplified: This is a differential amplifier topology.
- Pot fully CW: gain = +1 (non-inverted)
- Pot center: gain = 0 (signal nulled)
- Pot fully CCW: gain = -1 (inverted)

**Use matched 1% resistors (100kΩ) for accurate null at center.**

---

## 7. Buffered Multiple (1→3, TL074)

```
  INPUT ──┬── TL074 A (+in, feedback to -in) ── OUT 1
          │
          ├── TL074 B (+in, feedback to -in) ── OUT 2
          │
          └── TL074 C (+in, feedback to -in) ── OUT 3

  Each output has 1kΩ series resistor (inside feedback loop for stability).
```

**DC accuracy:** TL074 offset = ~3mV max = ~3.6 cents pitch error.
Acceptable for most uses. For critical V/Oct, use OPA4171 (~0.15mV).

---

## 8. Manual Gate Button

```
                    +12V
                     │
                   10kΩ (pull-up)
                     │
  Momentary SW ──────┤──── CD40106 input ──── GATE OUT jack
                     │                          │
                   10kΩ (pull-down)            [1kΩ]
                     │                          │
                    GND                        LED ── GND (via 470Ω)
```

**Without SW pressed:** Junction at ~6V (divider), Schmitt LOW → 0V out
**SW pressed:** Junction pulled to ~10V, Schmitt HIGH → +5V out

Clean edges, LED indicates gate state.

---

## Power Distribution

```
Eurorack 16-pin header:
  Pin 1-4:   -12V
  Pin 5-8:   GND
  Pin 9-12:  +12V
  Pin 13-14: +5V (if available from bus)
  Pin 15-16: CV/Gate (unused)

Protection:
  +12V ──[1N5817]──[ferrite]──┬── +12V rail
                               │
                          47µF + 100nF
                               │
  GND ─────────────────────── GND rail
                               │
                          47µF + 100nF
                               │
  -12V ──[1N5817]──[ferrite]──┬── -12V rail

  78L05 for +5V (CD4024, CD40106):
  +12V rail ──[78L05]──┬── +5V
                        │
                    10µF + 100nF
                        │
                       GND
```

---

## Component Totals (Expander)

| Component | Qty | Purpose |
|-----------|-----|---------|
| TL074CN | 3 | Buffers (8ch), mult (3ch), spare |
| TL072CP | 2 | Noise amp, LFO, slew, attenuverter |
| CD4024BE | 1 | Clock divider |
| CD40106BE | 1 | Gate/clock conditioning |
| LF398 | 1 | Sample & hold |
| 78L05 | 1 | +5V regulator |
| 2N3904 | 2 | Noise source, spare |
| 1N5817 | 2 | Reverse polarity protection |
| 1N4148 | 6 | Slew steering, clamp |
| BAT54S | 4 | Input protection |
| 100kΩ 1% | 20 | Attenuverter, mixing, bias |
| 1kΩ | 15 | Output series, LED current |
| 470kΩ | 2 | Noise bias |
| 4.7MΩ | 1 | Noise gain |
| 1MΩ pot | 3 | LFO rate, S&H rate, slew |
| 100kΩ pot | 4 | Attenuators (3), attenuverter |
| 1µF film | 3 | LFO timing, slew timing, coupling |
| 1nF polystyrene | 1 | S&H hold cap |
| 100nF ceramic | 15 | IC decoupling |
| 10µF electrolytic | 3 | Bulk decoupling |
| 47µF electrolytic | 2 | Power filtering |
| LED 3mm | 6 | Clock, gate, LFO indicators |
| Thonkiconn | 31 | All jacks |
| Momentary button | 1 | Manual gate |
