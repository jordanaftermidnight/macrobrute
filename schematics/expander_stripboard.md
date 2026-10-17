# MACROBRUTE Expander — Stripboard Layouts

Each utility circuit is built on a separate small stripboard for
independent testing, easy replacement, and flexible panel arrangement.
All boards share ±12V and GND from the Eurorack power bus via a
common power distribution board. Rack power only; nothing here is cabled to the synth except the
DB-9 lines handled in `expander_circuits.md` sections 5-7.

**Scope (decided):** LFO, Sample & Hold and slew limiter boards, plus the clock I/O buffer and the
gate divider (stripboard layouts for those two: TO DESIGN). Buffered mult, noise, CD4024 clock
divider, attenuverter and manual gate are DROPPED; their old layouts are kept under
"Dropped modules (archive)" at the end. Circuits and datasheet sources: `expander_circuits.md`.
Expander width (17 vs about 20 HP) stays OPEN; no panel layout is defined here. The grids below are
sketches; hole-level layouts are redrawn in a later diagram batch.

**Convention:** All diagrams show component side (top view, looking down).
Copper tracks run horizontally (left → right). "X" = track cut on copper side.

---

## Power Distribution Board

Central power rail board — all modules tap from this via pin headers.

**Board:** 30 × 20mm (8 rows × 12 cols)

```
  Component Side (top view)

  Row   1  2  3  4  5  6  7  8  9 10 11 12
   1    [──── 16-pin Eurorack header ────]    ← odd pins
   2    [──── (continued)                ]    ← even pins
   3    D1>──[10µF ×2-4]──●──●──●──●──●──     +12V bus (● = test point/header)
   4    ─────────────────────────────────     GND bus (expander star)
   5    <D2──[10µF ×2-4]──●──●──●──●──●──     -12V bus
   6    D3>──[10µF]─[100n]─●── Pico VSYS ──    +5V (Pico only)
   7    ─────────────────────────────────     GND (doubled)
   8    ─────────────────────────────────     spare

  Header pins (Behringer CP1A, QSG p15, p20): 1-2 -12V (pin 1 = red stripe), 3-8 GND,
  9-10 +12V, 11-12 +5V (0.5 A shared with the rack), 13-16 not used (leave unconnected).
  D1: BAT85, anode at header +12V, cathode at the +12V bus.
  D2: BAT85, cathode at header -12V, anode at the -12V bus (the cathode faces the source).
  D3: BAT85 OR diode, rack +5V to Pico VSYS (BF 1.2).
```

The old drawing (1-4 -12V, 5-8 GND, 9-12 +12V, 13-14 +5V; 1N5817 and 100Ω ferrite; 47µF; a 78L05
for CD4024 / CD40106) is withdrawn: the pin map was wrong (audit S27), 1N5817 and ferrites are not
owned, and no remaining expander IC needs a separate 5 V (audit S28). Bulk uses owned 10µF / 63 V
parts in parallel (BF 1.4).

**Per-module connection:** 3-pin header (+12V, GND, -12V) from the power board to each module.
Star topology to avoid ground loops (all grounds meet at the expander star, BF 4.1).

---

## Module 1: Triangle/Square LFO

**Board:** 40 × 20mm (8 rows × 16 cols)
**ICs:** TL072 (both sections: integrator + Schmitt trigger)
**Pots:** 1MΩ (rate; not owned, BF Q6), 100kΩ (optional depth)
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
    Pin 2 (-IN_A) ← 10kΩ fixed ← 1MΩ rate pot ← Square output (pin 7)
    Pin 3 (+IN_A) → GND via 100kΩ (virtual ground)
    Pin 1 (OUT_A) = TRIANGLE output (~10Vpp)

  Section B = Schmitt Trigger (comparator with hysteresis):
    Pin 6 (-IN_B) ← Triangle from pin 1
    Pin 5 (+IN_B) ← voltage divider: 100kΩ from pin 7 (own output) + 100kΩ to GND
    Pin 7 (OUT_B) = SQUARE output (±~11V rail-to-rail)

  Square output scaling: 3.3kΩ + 3.3kΩ voltage divider → ±5V for Eurorack
    (pin 7 → 3.3kΩ → tap → 3.3kΩ → GND; tap → 1kΩ → SQR jack; the grid draws them in a line)

  Rate (derived, T = 2RC; audit S60): 1MΩ pot + 10kΩ with 1µF gives about 0.5 Hz to 50 Hz
  (the old "0.04-40 Hz" was wrong). Not measured (E-27).
  REQUIRED (audit S61): 10kΩ fixed resistor in series with the rate pot, between the square
  output and pin 2. Hole position TO DESIGN (not drawn in the grid above).
  1µF film and 1MΩ pot are not owned (BF Q6); the 3.3k square output also gets a 1kΩ series
  resistor before the jack (audit N14).

  Track cuts: Between cols 4-5 on rows 3-7 (DIP center gap)
```

---

## Module 2: Sample & Hold

**Board:** 25 × 15mm (6 rows × 10 cols)
**ICs:** LF398N (DIP-8; not owned, BF Q1)
**Cap:** 10 nF polystyrene or polypropylene film (not owned, buy with the LF398; never ceramic)
**Jacks:** 3 (signal in, trigger in, S&H out)

Owned-parts alternative to the LF398: CD4051 switch + TL072 buffer + 10 nF film cap
(`expander_circuits.md` section 2b; charge injection UNVERIFIED; layout TO DESIGN).

The old grid and pin list here were wrong (OUT = 5 but V+ = 7, an invented "IN-" feedback pin,
no LOGIC REFERENCE; audit B13). Stripboard placement is TO DESIGN; the pin connections below are
from the TI datasheet (SNOSBI3C p3; `docs/DATASHEETS.md` (a)):

```
  LF398 pin connections:
    Pin 1 (V+)              → +12V, 100nF to GND
    Pin 2 (OFFSET ADJUST)   → not connected (optional DC zeroing per datasheet p15)
    Pin 3 (INPUT)           ← Signal input jack
    Pin 4 (V-)              → -12V, 100nF to GND
    Pin 5 (OUTPUT)          → S&H output jack (series R / buffer TO DESIGN)
    Pin 6 (Ch)              → 10 nF FILM cap to GND
    Pin 7 (LOGIC REFERENCE) → GND
    Pin 8 (LOGIC)           ← trigger conditioner (TO DESIGN): high = sample, low = hold (p14)

  CRITICAL: hold cap polystyrene, polypropylene or Teflon (low dielectric absorption, p15).
    Ceramic and electrolytic caps are unsuitable. Keep the trigger wiring away from pin 6:
    stray logic coupling adds hold step (p5).
  Leakage 30 pA typ / 200 pA max (p7) → about 3 / 20 mV/s droop with 10 nF (derived).
  A rack gate must not go straight to pin 8: the p4 logic-to-reference limit is printed as 7 V
  (see expander_circuits.md section 2).
```

---

## Module 3: Slew Limiter

**Board:** 30 × 15mm (6 rows × 12 cols)
**ICs:** TL072 (1 section)
**Pots:** 2× 1MΩ (rise rate, fall rate) — or 1× 1MΩ for single-knob (1MΩ pots and the 1µF film cap are not owned, BF Q6; 1N4148 owned, kit UNVERIFIED)
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

## Module 4: Clock I/O buffer (CD4049UB) — layout TO DESIGN

Circuit: `expander_circuits.md` section 4 (BF 3.7). One CD4049UBE (Have) on Pico 3V3: Clock IN
jack → 100kΩ pull-down + 100kΩ series → two sections → GP21; GP22 → two sections → 1kΩ → CLK OUT
jack; unused inputs to GND. No stripboard layout yet.

---

## Module 5: Gate divider (DB-9 A:1) — layout TO DESIGN

Circuit: `expander_circuits.md` section 5 (BF 3.5, Provisional). A:1 → gate jack; A:1 → 22kΩ →
node → 33kΩ to GND; node → a fault-tolerant Pico GPIO. Can sit on the Pico sub-board.

---

## Wiring Between Modules

All modules connect to the panel jacks via short wires. Signal routing
between modules is done on the panel wiring side.

```
  Power bus board ──┬── Module 1 (LFO)
                    ├── Module 2 (S&H)
                    ├── Module 3 (Slew)
                    └── Module 4 (Clock I/O buffer; CD4049UB on Pico 3V3, not on the ±12V bus)

  DB-9 A (from MicroBrute) → panel jacks directly (no expander IC on lines 2-8, BF 2.3);
                             A:1 also → gate divider → Pico GPIO
  Expander CV driver (TO DESIGN) → 10kΩ → DB-9 B:3 / B:5 (to MicroBrute)
  Pico GP0 / GP1 → 1kΩ each → DB-9 B:1 / B:6 (UART)
```

If an A line is later normalled into an expander circuit (slew, S&H), it enters through at least
100kΩ (BF 3.6).

---

## Build Order (recommended)

Build and test each module before starting the next.

| # | Module | Test Signal | Expected Output |
|---|--------|-------------|-----------------|
| 1 | Power board | Rack power, no modules | +12V / -12V / +5V present at the bus; BF BT-12 for +5V |
| 2 | LFO | Power on | Triangle + square; range about 0.5-50 Hz with 1MΩ + 10kΩ and 1µF (derived, E-27) |
| 3 | Slew limiter | Step input (0→5V) | Smooth ramp, rate set by pots |
| 4 | Clock I/O buffer | ±10V square into CLK IN | GP21 stays within 0-3.3V; 3V3 unchanged (BF BT-11) |
| 5 | Sample & Hold | LFO → sig, clock → trig (after the trigger conditioner exists) | Staircase waveform on scope |

---

## Expander Component Totals

See `expander_circuits.md`, "Component Totals (Expander, decided scope)", for the part list with
owned status. The old totals here (TL074 mult, CD4024, 78L05, 2N3904, 1N5817, BAT54S, attenuverter
pots, 1nF hold cap) were for the old scope and are withdrawn.

---

## Dropped modules (archive)

DROPPED from the expander (audit section 1, S59). Kept only as a record of earlier layouts. Do not
build from this section; its values were not re-checked.

### A1. Buffered Multiple (1→3) (DROPPED)

Dropped: the rack's existing multiple covers it.

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

### A2. White Noise Generator (DROPPED)

Dropped: the rack's existing noise module covers it.

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

### A3. Clock Divider (/2, /4, /8) (DROPPED)

Dropped: clock division is in Pico firmware (GP16-18); the CD4024 is not owned. CD4024 pin numbers below are UNVERIFIED (the datasheet copy's pin drawing is not machine-readable).

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

### A4. Attenuverter (2 channels) (DROPPED)

Dropped: the rack's existing mixer covers the routing role.

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

### A5. Manual Gate Button (DROPPED)

Dropped: the tap button on the expander doubles as a manual gate.

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

