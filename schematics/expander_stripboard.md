# MACROBRUTE Expander — Stripboard Layouts

Each utility circuit is built on a separate small stripboard for
independent testing, easy replacement, and flexible panel arrangement.
All boards share ±12V and GND from the Eurorack power bus via a
common power distribution board.

**Convention:** All diagrams show component side (top view, looking down).
Copper tracks run horizontally (left → right). "X" = track cut on copper side.

---

## Power Distribution Board

Central power rail board — all modules tap from this via pin headers.

**Board:** 30 × 20mm (8 rows × 12 cols)

```
  Component Side (top view)

  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    [──── 16-pin Eurorack header ────]    ← pins 1-8 on this row
   2    [──── (continued)                ]    ← pins 9-16
   3    D1>──FB──[47µF]──●──●──●──●──●──     +12V bus (● = test point/header)
   4    ─────────────────────────────────     GND bus
   5    D2>──FB──[47µF]──●──●──●──●──●──     -12V bus
   6    ──[78L05]─[10µF]─[100n]─●──●────     +5V bus (for digital ICs)
   7    ─────────────────────────────────     GND (doubled)
   8    ─────────────────────────────────     spare

  D1, D2: 1N5817 (reverse polarity protection)
  FB: 100Ω ferrite bead (EMI filtering)
  78L05: +12V → +5V regulator (CD4024, CD40106)
```

**Per-module connection:** 3-pin header (+12V, GND, -12V) or 4-pin
(+12V, GND, -12V, +5V) from power board to each module. Star topology
to avoid ground loops.

---

## Module 1: Buffered Multiple (1→3)

**Board:** 25 × 15mm (6 rows × 10 cols)
**ICs:** TL074 (1 of 4 sections used, 3 unity followers)
**Jacks:** 4 (1 input, 3 outputs)

```
  Row   1  2  3  4  5  6  7  8  9  10
   1    V+ ─────────────── 100n ── GND     Power + decoupling
   2    ────┤1     14├──── V- ── 100n ── GND
   3    IN──┤3  U1 12├─R──OUT3  ← +IN_D follower, 1kΩ output
   4    ────┤4  074 11├────────
   5    IN──┤5     10├─R──OUT2  ← +IN_C follower
   6    IN──┤7      8├─R──OUT1  ← OUT_C follower
           ↑              ↑
     All +IN pins       All -IN pins get feedback jumper from OUT

  Track cuts: Between cols 3-4 on rows 2-6 (DIP center gap)

  Jumper wires (component side):
    Pin 1 → Pin 2 (OUT_A → -IN_A)   — but A section unused here
    Pin 7 → Pin 6 (OUT_B → -IN_B)   — unused
    Pin 8 → Pin 9 (OUT_C → -IN_C)   ← OUTPUT 1
    Pin 12 → Pin 13 (OUT_D → -IN_D) ← OUTPUT 3 (note: pin 12 is +IN_D)

  Correction: For 3 followers, use sections B, C, D:
    Input → 3-way junction → pin 5, pin 10, pin 12
    Pin 7→6: OUT_B→-IN_B   → OUT 1
    Pin 8→9: OUT_C→-IN_C   → OUT 2
    Pin 14→13: OUT_D→-IN_D → OUT 3
    Section A unused (tie +IN_A pin 3 to GND)
```

**Build/test:** Apply a voltage (e.g., 2V from pot), verify all 3 outputs
match within ~5mV.

---

## Module 2: White Noise Generator

**Board:** 30 × 20mm (8 rows × 12 cols)
**ICs:** TL072 (1 section as amp)
**Transistor:** 2N3904 (avalanche noise source)

```
  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    V+ ──── 100n ── GND ── V- ── 100n ── GND    Power
   2    V+ ── 470k ── 470k ──┐                       Bias chain
   3                          ├── Q1 Base (2N3904)    Reverse-biased B-E
   4              [100pF]     │                       Optional HF boost
   5              Q1 Emitter ─┘── GND                 Noise source
   6    GND─100k─┤3  U1  8├─── V+                    TL072 section A
   7    ─100k────┤2  072  7├──(unused B)              -IN via 100k input
   8    ─4.7M────┤1      4├─── V- ── [10k]─ OUT      Output + series R
         ↑ feedback                    ↑
         pin1→pin2 via 4.7M           NOISE jack

  Track cuts: Between cols 5-6 on rows 6-8 (DIP gap, if placed cols 4-7)
  Also cut row 2 to isolate 470k chain segments

  Q1 2N3904: CUT THE COLLECTOR LEAD SHORT — prevents antenna pickup.
  Only Base and Emitter are connected. The avalanche effect occurs
  in the reverse-biased B-E junction at ~8-9V.

  Gain: 4.7MΩ / 100kΩ = 47× → ~5-8Vpp white noise
  Not all 2N3904s avalanche equally — test several, pick the noisiest.
```

---

## Module 3: Triangle/Square LFO

**Board:** 40 × 20mm (8 rows × 16 cols)
**ICs:** TL072 (both sections: integrator + Schmitt trigger)
**Pots:** 1MΩ (rate), 100kΩ (optional depth)
**Jacks:** 2 (triangle out, square out)

```
  Row   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
   1    V+ ── 100n ── GND ── V- ── 100n ── GND ─────────   Power
   2    ────────────────────────────────────────── LED ───   LFO indicator
   3    ┤1       8├── V+ ─────────────────────────────────
   4    ┤2  U1   7├── SQR_OUT ──[3.3k]──[3.3k]── SQR jack  ±5V scaled
   5    ┤3  072  6├─────────── 100k ──┐                     -IN_B
   6    ┤4       5├── 100k ── GND     └── SQR_OUT (hyst)    +IN_B hysteresis
   7    ── V- ────────────────────────────────────────────
   8    ── TRI_OUT jack ──────────────────────────────────

  Section A = Integrator:
    Pin 2 (-IN_A) ← 1µF ← Pin 1 (OUT_A) = feedback capacitor
    Pin 2 (-IN_A) ← 1MΩ rate pot ← Square output (pin 7)
    Pin 3 (+IN_A) → GND via 100kΩ (virtual ground)
    Pin 1 (OUT_A) = TRIANGLE output (~10Vpp)

  Section B = Schmitt Trigger (comparator with hysteresis):
    Pin 6 (-IN_B) ← Triangle from pin 1
    Pin 5 (+IN_B) ← voltage divider: 100kΩ from pin 7 (own output) + 100kΩ to GND
    Pin 7 (OUT_B) = SQUARE output (±~11V rail-to-rail)

  Square output scaling: 3.3kΩ + 3.3kΩ voltage divider → ±5V for Eurorack

  Rate: 1MΩ pot gives ~0.04 Hz to ~40 Hz
  Tip: Add 10kΩ in series with pot to limit maximum rate

  Track cuts: Between cols 4-5 on rows 3-7 (DIP center gap)
```

---

## Module 4: Clock Divider (/2, /4, /8)

**Board:** 30 × 15mm (6 rows × 12 cols)
**ICs:** CD4024 (7-stage binary counter), CD40106 (1 section for input conditioning)
**Power:** +5V (from power distribution 78L05)
**Jacks:** 4 (clock in, /2 out, /4 out, /8 out)

```
  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    +5V ── 100n ── GND ──────────────────    Power (+5V only)
   2    CLK_IN ── 120k ──┐── 100k ── GND         Voltage divider (10V→4.2V)
   3                     └── CD40106 ── pin 1     Input conditioning
   4    ──┤1     14├── +5V ── RST_BTN             CD4024
   5    ──┤3  024  7├── GND                       /2 → 1kΩ → jack + LED
   6    ──┤4      5├─────── ─── ─── ───           /4, /8 → 1kΩ → jacks + LEDs

  CD4024 pin connections:
    Pin 1  (CLK) ← CD40106 output (conditioned clock)
    Pin 2  (RST) ← 10kΩ to GND (hold LOW) + momentary to +5V (manual reset)
    Pin 3  (Q1)  → 1kΩ → /2 jack     + 1kΩ → LED → GND
    Pin 4  (Q2)  → 1kΩ → /4 jack     + 1kΩ → LED → GND
    Pin 5  (Q3)  → 1kΩ → /8 jack     + 1kΩ → LED → GND
    Pin 7  (VSS) → GND
    Pin 14 (VDD) → +5V

  CD40106 uses just 1 gate (pins 1/2). Tie unused inputs to GND or VDD.

  Track cuts: Standard DIP center gaps for both ICs
```

---

## Module 5: Sample & Hold

**Board:** 25 × 15mm (6 rows × 10 cols)
**ICs:** LF398
**Cap:** 1nF polystyrene (CRITICAL — never ceramic)
**Jacks:** 3 (signal in, clock/trigger in, S&H out)

```
  Row   1  2  3  4  5  6  7  8  9  10
   1    +12V ── 100n ── GND ── -12V ── 100n ── GND    Power
   2    ──────────────────────────────────── OUT jack
   3    ──┤5  LF398  7├── +12V
   4    ──┤6        3├── SIG_IN jack (via 10kΩ)
   5    ──┤1        8├── CLK_IN jack (logic/gate)
   6    ──┤4        2├── pin 5 feedback
              ↑
             V- = -12V

  LF398 pin connections:
    Pin 3 (IN+)  ← Signal input (via 10kΩ)
    Pin 2 (IN-)  ← feedback from pin 5 (output)
    Pin 5 (OUT)  → S&H output jack
    Pin 6 (HOLD) → 1nF POLYSTYRENE cap to GND
    Pin 8 (L/S)  ← Clock/trigger input
    Pin 7 (V+)   → +12V
    Pin 4 (V-)   → -12V
    Pin 1 (OFFS) → leave unconnected or 100kΩ to GND

  ⚠ CRITICAL: Use 1nF polystyrene or polypropylene for hold cap.
    Ceramic caps have voltage-dependent capacitance and high leakage.
    Electrolytic caps have extreme leakage. Either will cause excessive
    droop and make the S&H useless.
```

---

## Module 6: Slew Limiter

**Board:** 30 × 15mm (6 rows × 12 cols)
**ICs:** TL072 (1 section)
**Pots:** 2× 1MΩ (rise rate, fall rate) — or 1× 1MΩ for single-knob
**Jacks:** 2 (input, output)

```
  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    V+ ── 100n ── GND ── V- ── 100n ── GND         Power
   2    IN_jack ── 10kΩ ──┬── D1→ ── RISE_POT ──┐      Rise path
   3                      └── ←D2 ── FALL_POT ──┤      Fall path
   4                                              │
   5    ──┤3  U1  8├── V+                         │     TL072 section A
   6    ──┤2  072 7├── (unused)       ┌── 1µF ── GND   Timing cap
   7    ──┤1      4├── V-             │
   8    ── OUT_jack ──────────────────┘

  TL072 section A:
    Pin 3 (+IN) ← junction of rise/fall paths
    Pin 2 (-IN) ← pin 1 (output) via 1µF cap to GND (integrator)
    Pin 1 (OUT) → output jack + feedback to pin 2

  Wait — this is actually a follower with RC on the feedback:
    Pin 3 (+IN) ← input via diode-steered resistors
    Pin 2 (-IN) ← direct feedback from pin 1
    1µF cap from pin 3 junction to GND (not in feedback)

  Corrected topology (standard slew):
    Input ──[10kΩ]──┬──[D1 1N4148 →]──[RISE 1MΩ pot]──┐
                    └──[← D2 1N4148]──[FALL 1MΩ pot]──┤
                                                       ├── 1µF ── GND
                                                       │
                                                  TL072 +IN (pin 3)
                                                  TL072 -IN (pin 2) ← OUT (pin 1)
                                                  TL072 OUT (pin 1) → jack

  D1: 1N4148 — passes positive-going (rising) signals through RISE pot
  D2: 1N4148 reversed — passes negative-going (falling) through FALL pot
  1µF: timing capacitor (larger = slower maximum slew)

  Single-knob: Replace both diodes and pots with one 1MΩ pot

  Track cuts: Standard DIP center gap
```

---

## Module 7: Attenuverter (2 channels)

**Board:** 30 × 20mm (8 rows × 12 cols)
**ICs:** TL072 (both sections)
**Pots:** 2× 100kΩ center-detent (one per channel)
**Jacks:** 4 (2 inputs, 2 outputs)

```
  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    V+ ── 100n ── GND ── V- ── 100n ── GND         Power
   2    ──── 100kΩ Rf (feedback) ────                    Ch A feedback
   3    IN_A ── 100kΩ R1 ──┤2  U1  8├── V+              TL072
   4    POT_A wiper ───────┤3  072  7├── OUT_B ── jack   Ch B out
   5                       ┤1       6├──── 100kΩ Rf      Ch B feedback
   6    IN_B ── 100kΩ R1 ──┤        5├── POT_B wiper
   7    OUT_A ── jack      ┤4       ├── V-
   8                       └────────┘

  Per channel (inverting summer topology):
    Pot CW end  → Input (via 100kΩ)
    Pot CCW end → GND
    Pot wiper   → TL072 +IN

    -IN ← 100kΩ (R1) ← Input
    -IN ← 100kΩ (Rf) ← Output (feedback)

    CW: gain ≈ +1 (unity, non-inverted)
    Center: gain = 0 (signal nulled)
    CCW: gain ≈ -1 (inverted)

  Use matched 1% 100kΩ resistors for accurate null at center detent.

  Track cuts: Standard DIP center gap
```

---

## Module 8: Manual Gate Button

**Board:** 15 × 10mm (4 rows × 6 cols) — smallest module
**ICs:** None (or CD40106 if clean edges needed, shares with clock divider)
**Jacks:** 1 (gate out)

```
  Row   1  2  3  4  5  6
   1    +5V ── 10kΩ ── junction ── GATE_OUT jack
   2              SW (momentary) ── junction ── 1kΩ ── LED ── GND
   3    GND ── 10kΩ ── junction
   4    (empty)

  Without Schmitt trigger (simple but adequate):
    +5V ── 10kΩ ── junction ── 10kΩ ── GND
                     │
                   SW to GND (when pressed, pulls junction LOW)

  Wait — we want gate HIGH when pressed:
    GND ── 10kΩ pull-down ── junction ── GATE OUT jack (via 1kΩ)
                               │            │
                             SW to +5V     LED ── 470Ω ── GND
                             (pressed = +5V at junction)

  Or simpler:
    SW one leg → +5V
    SW other leg → junction
    junction → 10kΩ → GND (pull-down)
    junction → 1kΩ → GATE OUT jack
    junction → 1kΩ → LED → 470Ω → GND

  For clean edges: Route junction through CD40106 Schmitt gate first.
  Can share the CD40106 on the clock divider board (5 spare gates).
```

---

## Wiring Between Modules

All modules connect to the panel jacks via short wires. Signal routing
between modules and to DB-9 is done on the panel wiring side.

```
  Power bus board ──┬── Module 1 (Mult)
                    ├── Module 2 (Noise)
                    ├── Module 3 (LFO)
                    ├── Module 4 (Clock Div)
                    ├── Module 5 (S&H)
                    ├── Module 6 (Slew)
                    ├── Module 7 (Attenuverter)
                    └── Module 8 (Manual Gate)

  DB-9 A (inputs from MicroBrute) → buffer TL074 → panel jacks
  Panel jacks → patch cables → module inputs
  Module outputs → panel jacks → patch cables or DB-9 B (to MicroBrute)
```

---

## Build Order (recommended)

Build and test each module before starting the next.
Order follows Phase 4 of the build plan (easiest → hardest).

| # | Module | Test Signal | Expected Output |
|---|--------|-------------|-----------------|
| 1 | Buffered mult | Apply 2V DC | 3 copies at 2V ±5mV |
| 2 | Noise generator | Power on | ~5-8Vpp white noise on scope/headphones |
| 3 | LFO | Power on | Triangle + square, 0.04-40Hz |
| 4 | Clock divider | Feed 1Hz clock | /2 /4 /8 LEDs blink at expected rates |
| 5 | Sample & Hold | Noise → sig, clock → trig | Staircase waveform on scope |
| 6 | Slew limiter | Step input (0→5V) | Smooth ramp, rate set by pots |
| 7 | Attenuverter | Apply 5V DC | +5V, 0V, -5V as pot sweeps |
| 8 | Manual gate | Press button | Clean 5V pulse, LED lights |

---

## Expander Component Totals

| Component | Qty | Used In |
|-----------|-----|---------|
| TL074CN | 1 | Mult (1), spare sections for buffers |
| TL072CP | 2 | Noise (1 section), LFO (2 sections), Slew (1), Attenuverter (2) |
| CD4024BE | 1 | Clock divider |
| CD40106BE | 1 | Clock input conditioning + manual gate (shared) |
| LF398 | 1 | Sample & hold |
| 78L05 | 1 | +5V for CD4024/CD40106 |
| 2N3904 | 2 | Noise source + spare |
| 1N5817 | 2 | Power protection |
| 1N4148 | 6 | Slew steering (2), signal clamp (4) |
| BAT54S | 4 | Input protection |
| 1MΩ pot | 3 | LFO rate, slew rise, slew fall |
| 100kΩ center-detent pot | 2 | Attenuverter ch A + B |
| 100kΩ pot | 2 | Spare attenuators |
| 1µF film cap | 3 | LFO timing, slew timing, coupling |
| 1nF polystyrene | 1 | S&H hold cap |
| 100nF ceramic | 15 | IC decoupling (2 per IC × 7 ICs + spares) |
| 10µF electrolytic | 3 | Power bulk per board |
| 47µF electrolytic | 2 | Main power bus |
| LED 3mm | 6 | Clock div (3), LFO (1), gate (1), spare (1) |
| Thonkiconn PJ398SM | ~20 | All I/O jacks |
| Momentary pushbutton | 1 | Manual gate |
| Stripboard scraps | 8 | One per module |
