# MACROBRUTE Expander — Utility Circuit Schematics

All circuits powered from the Eurorack rack only (Behringer CP1A 16-pin bus, ±12 V; +5 V for the
Pico). No supply and no analog utility is cabled to the synth.
100nF ceramic bypass cap on every IC power pin pair.

**Scope (decided, audit section 1):** slew limiter, clock I/O, firmware clock dividers, 4 aux
outputs, a standalone LFO and a standalone Sample & Hold (rack-powered, no synth cabling), plus the
expander ends of the DB-9 lines (gate input, UART, CV outputs). Noise, attenuverter, buffered mult,
the CD4024 divider and the manual gate button are DROPPED: their old text is kept under
"Dropped modules (archive)" at the end of this file.

Sample & Hold: LF398 is the default; a CD4051 + TL072 + film-cap version is documented as an
owned-parts alternative (section 2b).

Expander width (17 HP vs about 20 HP) stays OPEN until the owner measures the blank (audit decision
e); no panel layout is defined here. Sources: back-feed and hum design note
(`docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md`, "BF"), `docs/DATASHEETS.md`, audit
(`docs/superpowers/reviews/2026-10-16-project-audit.md`). Nothing is built; derived values are
UNVERIFIED until measured.

---

## 1. Triangle/Square LFO (TL072 integrator + Schmitt trigger)

Standalone rack utility. The old ASCII drawing here was not a coherent netlist (audit S62) and is
replaced by the netlist below (from the prose that was the reliable part).

```
  TL072 A = Integrator
    +in (pin 3): GND via 100kΩ
    -in (pin 2): from the square output (TL072 B pin 7) via 10kΩ fixed (MANDATORY) + 1MΩ rate pot
    feedback: 1µF capacitor from out (pin 1) to -in (pin 2)
    output (pin 1): Triangle wave → TRIANGLE OUT jack (output series R: see below)

  TL072 B = Schmitt Trigger (comparator with hysteresis)
    +in (pin 5): 100kΩ from own output (pin 7), 100kΩ to GND  (thresholds ±Vsat/2)
    -in (pin 6): Triangle from TL072 A output (pin 1)
    output (pin 7): Square wave (±~10.5 V)

  Square output scaling:
    pin 7 ── 3.3kΩ ──┬── 1kΩ ── SQUARE OUT jack       (±5.25 V, audit N14)
                     3.3kΩ
                      │
                     GND
    (REVIEWED: 1.8kΩ was too hot, corrected to 3.3kΩ for ±5V target)

  TL072 supply: pin 8 = +12 V, pin 4 = -12 V (TI SLOS080W p5), 100nF each to GND.
```

**Rate range (derived, audit S60):** the triangle swings between the Schmitt thresholds (±5.25 V),
so each half-period is R × C and **T = 2RC**. With R = 1MΩ + 10kΩ and C = 1µF: T ≈ 2.0 s, about
**0.5 Hz** at the slow end; with the pot at 0 (10kΩ only): T = 20 ms, about **50 Hz**. The old
"0.04-40 Hz" was wrong. Not measured (E-27).

**10kΩ series resistor: mandatory** (audit S61). At pot = 0 it is the only limit on the current
from the Schmitt output into the integrator's virtual ground. Pot taper: rate goes as 1/R, so a
linear pot crowds the fast end; taper choice OPEN (owner).

**Parts:** 1µF film and 1MΩ pot are not owned (BF Q6). With an owned 100kΩ pot the range becomes
about 4.5-50 Hz (R = 110k to 10k). A slower range needs a larger film cap (for example 4.7-10 µF
for about 0.1-0.05 Hz at the slow end, audit S60); range switch: OPEN (owner).

**Open:** the connection map (section 10) and BF 1.1 list "TL072 integrator + CD40106 Schmitt" for
the LFO, while this file uses the second TL072 section as the Schmitt. The range above assumes the
TL072 Schmitt. Which one is built is OPEN (owner).

Triangle output series resistor and an LFO LED: TO DESIGN (follow the 1kΩ output rule used on the
square).

---

## 2. Sample & Hold (LF398)

Standalone rack utility (rack-powered, no synth cabling). Part: LF398N (DIP-8), not owned; buy
with a 10 nF film hold cap (BF Q1). Datasheet: TI SNOSBI3C (`docs/DATASHEETS.md` (a)).

LF398 PDIP-8 pinout (Pin Functions table, p3). The three older pinouts in the repo (this file,
`expander_stripboard.md`, the SVGs) were wrong; the LF398 has no "IN-" feedback pin (audit B13).

| Pin | Function | Connection |
|-----|----------|------------|
| 1 | V+ | +12 V, 100nF to GND |
| 2 | OFFSET ADJUST | Not connected; optional DC zeroing per p15 (1kΩ pot wiper, one end to V+, other end through a resistor to GND, about 0.6 mA) |
| 3 | INPUT | S&H IN jack (normalling: OPEN (owner), see below) |
| 4 | V- | -12 V, 100nF to GND |
| 5 | OUTPUT | S&H OUT jack. Output series R / buffer: TO DESIGN (the connection map lists a TL072 buffer) |
| 6 | Ch (hold capacitor) | 10 nF polystyrene or polypropylene film to GND |
| 7 | LOGIC REFERENCE | GND |
| 8 | LOGIC | From the trigger conditioner (TO DESIGN, below) |

**Supply:** ±5 V to ±18 V operating, ±18 V abs max (p1, p4): ±12 V from the rack is in range.

**Hold capacitor: 10 nF film** (genuine purchase, with the LF398). 0.01 µF is the characterised
value: hold step 1 mV typ, 2.5 mV max (p7); acquisition to 0.1 % about 20 µs (p5-p7). Use
polystyrene, polypropylene or Teflon for low dielectric absorption; mica and polycarbonate are not
nearly as good (p15). Never ceramic (the owned 1 nF is ceramic) or electrolytic.

**Leakage and droop:** leakage current into the hold capacitor 30 pA typ, 200 pA max (LF398-N,
25 °C, p7). With 10 nF that is about 3 mV/s typ, 20 mV/s max droop (derived as I / C, not a TI
figure). The old "3 pA, 3 mV/s with 1 nF" was wrong (audit S63); with 1 nF it would be 30-200 mV/s.

**Trigger: TO DESIGN** (audit S65). Constraints from the datasheet:
- Sample mode while LOGIC is high relative to LOGIC REFERENCE; hold while low (p14).
- Logic threshold 0.8 / 1.4 / 2.4 V min / typ / max (p5); logic input current 2 µA typ, 10 µA max (p5).
- Logic-to-reference differential abs max: the p4 table prints 7 V and -30 V. A +10 V rack gate
  applied directly would exceed +7 V, so a series resistor and clamp are needed (r4 suggests 10kΩ
  plus a clamp; values TO DESIGN). For proper logic operation one logic pin must stay at least 2 V
  below V+ and 3 V above V- (p4 note 4).
- Logic edges need at least 1 V/µs; an RC in front of LOGIC must keep that slope at the threshold
  (p15).
- Keep logic lines away from the hold capacitor: 1 pF of stray coupling with a 5 V swing adds
  0.5 mV hold step at 0.01 µF (p5).

**Normalling: OPEN (owner).** With noise dropped, S&H IN has nothing patched by default. r4
suggests IN normalled to the LFO triangle and TRIG to the clock through switched jacks; the owned
jack type is unknown (BF Q8).

### 2b. Owned-parts alternative: CD4051 switch + TL072 buffer (option)

LF398 stays the documented default. This option avoids buying the LF398 using owned parts (CD4051
Have 2, TL072 Have 6); the 10 nF film hold cap is still needed (not owned, BF Q1). Charge injection
and droop are UNVERIFIED (no figure taken from the datasheet for this use); bench-test before use.

```
  S&H IN ──[series R, TO DESIGN]── CD4051 Y0 (pin 13) ; COM (pin 3) ──┬── TL072 +IN (follower) ── OUT
                                                                     │
                                                              10 nF film ── GND
  CD4051 A (pin 11), B (pin 10), C (pin 9) = VSS  (selects Y0)
  CD4051 INH (pin 6): low = Y0 on (sample), high = all off (hold)  (truth table, Table 7-1)
  Supplies VDD (pin 16), VEE (pin 7), VSS (pin 8): TO DESIGN within the limits below
```

Datasheet constraints (TI SCHS047O; pinout p3 as in `docs/DATASHEETS.md` (c)):
- Supply V+ to V- at most 20 V abs max (p5), so the CD4051 cannot run from ±12 V (24 V). The
  supply pair, and therefore the usable CV range, is TO DESIGN.
- The analog signal may swing from VEE to VDD; address and INHIBIT logic levels are 0 = VSS and
  1 = VDD (p10). The trigger must therefore be conditioned to VSS / VDD levels and inverted so that
  a high gate gives INH low (sample): TO DESIGN.
- DC input on any control pin -0.5 V to VDD + 0.5 V, ±10 mA (p5).

The older CD4051 sketch (1 nF hold cap, 10 kΩ in, "INH inverted") is superseded by this section.

---

## 3. Slew Limiter (TL072 + diode steering)

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

Reading of the drawing (as in `expander_stripboard.md`, "Corrected topology"): the 1µF goes from
the junction of the two pot paths (the +in node) to GND, and -in is tied straight to the output
(unity follower); the cap is not in the feedback path.

Parts: 1N4148 (owned, kit contents UNVERIFIED), 1MΩ log pots (not owned, BF Q6), 1µF film timing cap (not owned;
a bipolar CV needs a non-polarised cap). Input range: TL072 common-mode about ±8 V on ±12 V rails
(TI SLOS080W p15; `CIRCUIT_REVIEW.md` section 10).

---

## 4. Clock I/O (CD4049UB buffers on Pico 3V3)

From BF 3.7. Both clock jacks and the Pico are in the rack domain; **no clock cable runs to the
synth** (audit N08). One owned CD4049UBE (Have, 3) provides four sections.

CD4049UB 16-pin pinout (TI SCHS046L p3): 1 VCC, 2 G (out of A), 3 A, 4 H (out of B), 5 B, 6 I (out
of C), 7 C, 8 VSS, 9 D, 10 J (out of D), 11 E, 12 K (out of E), 13 NC, 14 F, 15 L (out of F), 16 NC.

```
  Clock IN:  jack ──┬── 100kΩ ── GND   (pull-down at the jack)
                    └── 100kΩ series ── 4049 A in (pin 3) ; A out (pin 2) ── B in (pin 5) ;
                                        B out (pin 4) ── Pico GP21 (pin 27)

  Clock OUT: Pico GP22 (pin 29) ── 4049 C in (pin 7) ; C out (pin 6) ── D in (pin 9) ;
                                   D out (pin 10) ──[1kΩ]── CLK OUT jack

  4049 pin 1 VCC = Pico 3V3 (pin 36) ; pin 8 VSS = GND ; 100nF VCC-VSS
  Unused inputs E (pin 11) and F (pin 14) ── GND
```

The section-to-pin assignment above is one valid choice (any two sections in series per
direction work). Two inversions keep the clock polarity.

- The RP2040 pin only sees the 4049 output (0-3.3 V); RP2040 GPIO is not 5 V tolerant (RP2040
  datasheet Table 622, p615).
- Input over VCC: the TI sheet contradicts itself (p1 says VIH may exceed VCC; p17 says the inputs
  have clamp diodes to VCC). Treated as clamped: a +10 V input pushes at most
  (10 - 3.3 - 0.6) / 100k ≈ 61 µA into the 3V3 rail; -10 V pushes about 94 µA through the VSS
  clamp, far under the ±10 mA input clamp rating (p5). Bench checks BF BT-10, BT-11.
- Clock OUT mis-patch tolerance of the 4049 output (about 6 mA from ±10 V through 1kΩ) is
  UNVERIFIED (OPEN (owner), BF Q16).

---

## 5. Gate input from DB-9 A:1 (divider into the Pico)

From BF 3.5 (Provisional, audit recommendation, owner has not confirmed). A:1 carries the
breakout's CD40106 gate (0 / 5 V through 1kΩ on the MB side).

```
  DB-9 A:1 ──┬── GATE jack (tapped before the divider)
             └── 22kΩ ──┬── Pico GPIO, fault-tolerant pin (for example GP11; no firmware change yet)
                        │
                       33kΩ
                        │
                       GND
```

High level 5 V × 33k / (1k + 22k + 33k) = 2.95 V: above RP2040 VIH 2.0 V and below 3.63 V. No 5 V
net reaches a GPIO; no pull-up on the expander side. With the expander off and the synth on, the
pin sees 2.95 V through 13.6 kΩ (relies on the RP2040 fault-tolerant pad, BF 3.5, bench check BT-5).
The CD4049UBE is not used on this path.

---

## 6. UART to the LPC (DB-9 B:1 and B:6)

From BF 3.1. Pico GP0 (UART0 TX) → 1kΩ (expander) → B:1; B:6 → 1kΩ (expander) → Pico GP1 (UART0
RX). The MB side has its own 1kΩ per line (connection map section 5.4). No divider and no level
shifter (both ends 3.3 V). Firmware rule: GP0 stays an input until GP1 has read high. The LPC UART
choice (UART1 on LQFP pins 62 / 63) is UNVERIFIED until the Phase 0 continuity gate G1.

---

## 7. CV outputs to the MicroBrute (DB-9 B:3 VCA CV, B:5 Filter CV) — TO DESIGN

BF 3.3 fixes only the protection: each line leaves the expander through 10kΩ at the op-amp output;
the MB side has 100kΩ plus two BAT85 clamps and 1nF. The driving circuit (op-amp stage, level and
range, source of the CV) is not yet chosen: TO DESIGN. Optional firmware mute of these outputs
until the synth is seen powered: OPEN (owner), BF Q19.

---

## 8. Aux outputs (GP19, GP20, GP6, GP7) — TO DESIGN

Four firmware-programmable outputs (connection map section 10). The output stage (buffer, level,
PWM filter for PWM_CV mode, series resistor, trimmers) is not defined by the design note: TO DESIGN.
Trimmers: buy or use fixed resistors, OPEN (owner), BF Q7.

---

## Power Distribution

```
Eurorack 16-pin header (Behringer CP1A, QSG p15, p20; `docs/DATASHEETS.md` (f)):
  Pin 1-2:   -12V  @ 1 A  (pin 1 = red stripe)
  Pin 3-8:   GND
  Pin 9-10:  +12V  @ 1 A
  Pin 11-12: +5V   @ 0.5 A, shared with the whole rack
  Pin 13-16: not used on the CP1A (Doepfer A-100: CV / Gate) — leave unconnected

Protection (series Schottky per rail, justified against reverse insertion, audit N04):
  +12V ──[BAT85: anode at header, cathode at rail]──┬── +12V rail
                                                     │
                                         2-4× 10µF/63V + 100nF
                                                     │
  GND ───────────────────────────────────────────── GND (expander star, BF 4.1)
                                                     │
                                         2-4× 10µF/63V + 100nF
                                                     │
  -12V ──[BAT85: cathode at header, anode at rail]──┴── -12V rail

  +5V ──[BAT85 OR diode]──┬── Pico VSYS (pin 39)
                          │
                    10µF/63V + 100nF
                          │
                         GND
```

- 1N5817 (20 V part) and ferrite beads are not owned; BAT85 is (BF 1.2 budget: 1 for Pico VSYS,
  3 for the expander +12 / -12 / +5 V). The owned 1N5819 (40 V, 0.60 V max at 1 A) can replace the
  BAT85 on the ±12 V rails (same orientation), freeing BAT85 stock; on VSYS its drop at the Pico's
  current is UNVERIFIED (curve not read). 47µF and 100µF parts are not owned: owned 10µF / 63 V in
  parallel (BF 1.4). BAT85 drop on VSYS: about 4.2 V at 100 mA, inside VSYS 1.8-5.5 V (BF 1.2).
- The expander 78L05 is removed (audit S28): no remaining expander IC needs a separate 5 V. The
  CD4049UB runs from Pico 3V3; the LF398 and TL072 run from ±12 V.
- Whether the owner's bus slot carries +5 V: UNVERIFIED (BF BT-12). Keyed 16-pin header and
  ribbon: not owned (BF Q11).

---

## Component Totals (Expander, decided scope)

Status from BF section 1. Counts for TO DESIGN blocks (aux outputs, CV outputs, S&H trigger) are
not included.

| Component | Qty | Purpose | Status |
|-----------|-----|---------|--------|
| TL072CP | 2+ | LFO (2 sections), slew (1), spare | Have (6; allocation with the breakout OPEN, C10) |
| CD4049UBE | 1 | Clock IN / OUT buffers | Have (3) |
| LF398N | 1 | Sample & hold (default) | Missing (BF Q1); owned alternative CD4051 + TL072, section 2b |
| 10 nF polystyrene / polypropylene | 1 | S&H hold cap | Missing (BF Q1) |
| 1µF film | 2 | LFO timing, slew timing | Missing (BF Q6) |
| 1MΩ pot | 3 | LFO rate, slew rise, slew fall | Missing (BF Q6) |
| 100kΩ pot | — | Alternative for rate pots (10× range shift) | Have (4) |
| 1N4148 | 2 | Slew steering | Have (owner, kit UNVERIFIED) |
| 1N5819 | — | Alternative to BAT85 on the rack rails (40 V Schottky) | Have (10; kit UNVERIFIED) |
| BAT85 | 4 | Pico VSYS, +12 / -12 / +5 V | Have (10, budget BF 1.2) |
| 100kΩ | 5 | Clock IN (2), LFO Schmitt divider (2), integrator bias (1) | Have (kit, Q5) |
| 10kΩ | 4 | LFO series (1), slew input (1), CV outputs (2) | Have (kit) |
| 22kΩ, 33kΩ | 1 each | Gate divider | Have (kit) |
| 3.3kΩ | 2 | LFO square divider | Have (kit) |
| 1kΩ | 4 | Clock OUT, UART (2), LFO square out | Have (kit) |
| 100nF ceramic | ~8 | IC decoupling, rails | Have |
| 10µF/63V electrolytic | 6-10 | Rail and VSYS bulk | Have (10) |
| 3.5mm jacks | at least 16 | Panel (connection map section 10) | Have (25, type unknown, Q8) |
| 16-pin keyed header + ribbon | 1 | Rack power | Missing (Q11) |

---

## Dropped modules (archive)

DROPPED from the expander (audit section 1, S59; connection map section 10). Kept only as a record
of earlier ideas. Do not build from this section; its values were not re-checked.

### A1. White Noise Generator (Thomas Henry / Yusynth method) (DROPPED)

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

### A2. Clock Divider (CD4024 7-stage binary counter) (DROPPED: clock division is in Pico firmware; CD4024 pin numbers below UNVERIFIED)

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

### A3. Attenuverter (TL072) (DROPPED)

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

### A4. Buffered Multiple (1→3, TL074) (DROPPED)

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

### A5. Manual Gate Button (DROPPED: the tap button doubles as manual gate)

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

### A6. Old component totals (old scope, superseded)

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
