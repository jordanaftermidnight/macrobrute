# MACROBRUTE Internal Breakout PCB — Schematic

Mounts inside MicroBrute. A buffer-only board powered from the synth (TP70 / TP71 / TP72):
output buffers, gate conditioner, CV-input clamps, the vactrol driver (TO DESIGN) and the DB-9
connections. The Pico, OLED, encoder, tap button and RGB LED live on the expander, not here
(connection map section 9; audit S12).

Status: design values only, nothing is built. Values come from the back-feed and hum design note
(`docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md`, "BF" below) and the audit
(`docs/superpowers/reviews/2026-10-16-project-audit.md`). Items marked Provisional follow the audit
recommendation and wait for the owner. Anything not proven by a datasheet is UNVERIFIED.

## Power Supply (from MicroBrute rails)

The breakout takes power **only** from TP70 / TP71 / TP72. No supply crosses the DB-9 cable, and
no synth 5 V or 3V3 is tapped (TP56 is "per original doc" only, TP141 is the 5 V precision
reference, P4 pin 5 is the LPC's own +3V3ARM; audit B09).

```
MicroBrute +12V (TP70) ──[D1 BAT85: anode at TP70, cathode at rail]──┬── +12V_BRK
                                                                     │
                                                     2-4× 10µF/63V ──┤── 100nF at each IC V+ pin
                                                                     │
                                                                    GND (TP72 star)

MicroBrute -12V (TP71) ──[D2 BAT85: cathode at TP71, anode at rail]──┬── -12V_BRK
                                                                     │
                                                     2-4× 10µF/63V ──┤── 100nF at each IC V- pin
                                                                     │
                                                                    GND (TP72 star)

+12V_BRK ── 78L05 pin 3 (INPUT) ; pin 2 (COMMON) ── GND ; pin 1 (OUTPUT) ──┬── +5V_LOC (U3 CD40106 only)
                                                                          100nF
                                                                           │
                                                                          GND
```

- **Diode rule (one rule, audit B15):** on +12 V the anode faces TP70 and the cathode the rail; on
  -12 V the **cathode faces TP71 / the -12 V source and the anode faces the breakout rail (load)**.
  Either way the diode conducts in normal operation and blocks a reversed supply.
- **Rail protection part: OPEN (owner), audit conflict C12.** Option 1: one owned BAT85 per rail as
  drawn (uses 2 of the 10 owned BAT85; BF 1.2). Option 2: a 4.7-10 Ω series resistor per rail
  instead, which frees two BAT85 for hum-ladder step 4 (BF 4.5, Q3). Option 3: an owned 1N5819
  (40 V / 1 A Schottky, 0.60 V max at 1 A, `docs/DATASHEETS.md` (e); owned x10 (owner, kit card contents UNVERIFIED)) per
  rail, same orientation rule; this also frees two BAT85. The 1N5817 in older drawings is a 20 V
  part (not 40 V) and is not owned; the 1N5819 serves where the docs wanted a 1N5817.
- BAT85 drop: 400 mV at 10 mA, 800 mV at 100 mA (BAT85 p2-p3), so the rails sit roughly 0.4-0.7 V
  inside ±12 V at the expected load. Breakout load and synth rail capacity are UNVERIFIED (audit E-04).
- Bulk: 100µF parts are not owned; use 2-4 owned 10µF / 63 V in parallel per rail (BF 1.4).
  Ferrite beads are not owned and are omitted (BF 1.5).
- **+5V_LOC (Provisional, BF 3.4):** owned 78L05 from +12V_BRK, for the CD40106 only. TO-92 pinout
  1 OUTPUT, 2 COMMON, 3 INPUT (TI SLVS010X p3; the owned parts' maker is unknown, so check the
  marking). The TI sheet states no external capacitor is needed for stability (p1); the 100nF is
  local decoupling. Dropout 1.7 V typ, quiescent 3.8 mA (BF 3.4).

## Output Buffer Board (TL074 #1 — 4 channels)

Buffers waveform test point taps. Unity-gain voltage followers prevent
loading the MicroBrute's internal circuits.

```
                    +12V_BRK
                       │
                 ┌─────┤
                 │   ┌──┴──┐
  TP94 (Saw) ────┤   │     │
       via 1kΩ   ├───┤+ TL074├──┬──[1kΩ]── DB-9 A pin 7 (Saw Out)
                 │   │  A   │   │
                 │   └──┬──┘   │
                 │      │       │
                 └──────┼───────┘ (feedback: op-amp output pin → inverting input,
                        │          taken BEFORE the 1kΩ output resistor)
                    -12V_BRK

  TP93 (Square) ──1kΩ──┤+  TL074 B├──[1kΩ]── DB-9 A pin 8 (Square Out)
  TP30 (VCO Mix)──1kΩ──┤+  TL074 C├──[1kΩ]── DB-9 A pin 5 (VCO Mix Out)
  TP19 (VCF Out)──1kΩ──┤+  TL074 D├──[1kΩ]── DB-9 A pin 6 (VCF Out)
```

Each channel:
```
  Test Point ──[1kΩ]──┬──[TL074 +in]
                      │
                     1MΩ to GND (bias)

  TL074 out pin ──┬── TL074 -in   (feedback at the output pin)
                  │
                [1kΩ]  (output isolation, outside the loop)
                  │
               DB-9 A pin
```

**Component values per channel:**
- R_series: 1kΩ (input protection / isolation)
- R_bias: 1MΩ to GND (replaces 10MΩ: an open input floats less and picks up less hum; audit N11)
- R_output: 1kΩ after the feedback tap (stable into the cable; audit S36, R3-15)
- C_decouple: 100nF ceramic per supply pin

Input level: the TL074 linear common-mode range is about 4 V inside each rail (TI SLOS080W p11,
p15), so about ±8 V on these rails. Saw / square / mix / VCF peaks are UNVERIFIED (audit N10, E-19):
scope TP94 / TP93 / TP30 / TP19 first and add a 2:1 input divider if peaks exceed about ±8 V.

## Gate Buffer (CD40106 Schmitt Trigger)

Provisional (audit recommendation, owner has not confirmed; BF 3.4 and 3.5). TP83 has 100kΩ
source impedance. The old 10kΩ pull-up to +5V is removed: with TP83 low it held pin 1 at about
5 V × 110k / 120k = 4.58 V, above VT+, so the input could never read low (audit B14).

```
  TP83 (Gate) ──[10kΩ]──┬─── U3 pin 1 (input A)        no pull-up
                         │
                        1nF (owned; at the pin)
                         │
                        GND

  U3 pin 2 (output A) ──── U3 pin 3 (input B)          second inverter: A:1 follows TP83 polarity
  U3 pin 4 (output B) ──[1kΩ]── DB-9 A pin 1 (Gate Out)

  U3 pins 5, 9, 11, 13 (unused inputs) ── GND          (audit S34)
  U3 pin 14 VDD = +5V_LOC (78L05)
  U3 pin 7  VSS = GND
  100nF decoupling VDD to VSS
```

Expander side of A:1 (BF 3.5, Provisional): A:1 → gate jack (tapped here) → 22kΩ → node →
33kΩ to GND; node → Pico GP11, a fault-tolerant GPIO (`GATE_IN`; PROVISIONAL (BT-14): the OLED CS pin is tied to GND so GP11 can take this input, CM 12G). High
level 5 V × 33k / (1k + 22k + 33k) = 2.95 V. No 5 V net reaches a Pico GPIO. The CD4049UBE is not
on the gate path: it sits on the expander as the clock buffer (BF 3.7).

**Output:** 0 / +5V_LOC gate through 1kΩ. Open item: the CD40106 needs TP83 above VT+ (2.2 / 2.9 /
3.6 V min / typ / max at VDD 5 V, TI SCHS097F p5-p6). TP83's level is UNVERIFIED (E-09); if it is
3.3 V logic this stage must be redesigned (OPEN (owner), BF Q15; no synth 3V3 tap allowed).
RC at pin 1: (100k + 10k) × 1 nF ≈ 0.11 ms.

## Envelope & LFO Taps (from mod matrix)

These signals are available at the front panel mod matrix connections.
Buffer with U2 TL072 (not a second TL074; connection map section 9).

```
  Envelope (mod matrix / TP5) ──[10kΩ]──┤+ TL072 A follower├──[1kΩ]── DB-9 A pin 3
  LFO (mod matrix)            ──[10kΩ]──┤+ TL072 B follower├──[1kΩ]── DB-9 A pin 4
```

The 1kΩ sits after the feedback tap (audit S36, R3-15). Source choice for the envelope (TP5 vs
mod matrix) and the meaning of TP21 are UNVERIFIED (audit N23, E-17).

## Triangle Buffer (with 2x Gain)

Research confirmed TP124 (triangle) is inherently quieter than other
waveform outputs. Instead of a unity follower, use a non-inverting
amplifier with 2x gain to match levels with saw/square. The output goes to a
body jack: DB-9 A has no free pin (connection map section 5.1; audit S35).

```
  TP124 (Triangle) ──[1kΩ]──┬── TL072 section (+in)
                             │         │
                            1MΩ       out ──┬── [1kΩ] ── body jack
                             │              │
                            GND       -in ──┴── 100kΩ (Rf, feedback from the output pin)
                                       │
                                     100kΩ (Rg, to GND)

  Gain = 1 + Rf/Rg = 1 + 100k/100k = 2x
  Gain accuracy follows the resistor-kit tolerance (1 % parts are not owned, BF Q5).
```

Op-amp sections: U2 (TL072) has two sections but four jobs (env, LFO, triangle, vactrol driver).
U1/U2: TL074C or TL072IP, both owned (×4 / ×6); final op-amp count and split chosen at breakout layout (audit S17 / C10).

## LED Drivers — removed

Removed (audit S12, R3-17): the RGB LED and its drive are on the expander (Pico GP8-10, connection
map sections 1 and 10), so nothing on the breakout drives an LED. (The 2N3904 is now owned, but that
does not change where the LED lives.)

## Vactrol Driver (Resonance CV) — TO DESIGN

Finding (audit S37, R3-12): the old drawing used a TL072 driving a 2N3904 base through 1kΩ with the
vactrol LED in the collector. As drawn no supply reached the collector; with the sensible reading
(LED + R from +12 V to the collector) the LED current is fixed at about (12 - 2 - 0.2) / 1k ≈ 9 mA
once the base is above about 0.8 V, so the vactrol works as an on/off switch, not a continuous
resonance control. The base had no protection against negative TL072 swings, and the CV came from
DB-9 B pin 3, which is now VCA CV (BF 2.2). The old circuit is withdrawn.

Replacement: a linear voltage-to-current stage, **TO DESIGN** until the vactrol marking is read.
Constraints (r3 R3-12, BF 1.1, Q2):

- Topology: either an op-amp stage (TL072 section, +IN = CV, output → vactrol LED anode, LED
  cathode → R_sense → GND, R_sense node → -IN, so I_LED = V_CV / R_sense) or a transistor current
  sink driven by the op-amp with emitter feedback. The owner has 2N3904 / 2N3906 / S8050 / S8550
  (owner, kit card contents UNVERIFIED), so either is possible; the choice is TO DESIGN. A bare saturated switch (the old
  circuit) is not acceptable.
- R_sense depends on the owned vactrol's LED forward-current rating: the vactrol type and marking
  are unread (OPEN (owner), BF Q2). No value is given here until then.
- CV source: the new 3.5 mm resonance jack on the MicroBrute panel (connection map section 3,
  "Migrated to MB panel"), not the DB-9. Input protection on that jack: series resistor plus clamps
  to ±12V_BRK as for the B CV lines (below); values TO DESIGN.
- Negative CV must not reverse-bias the LED: an anti-parallel diode across the LED (r3 suggested a
  BAT85, all 10 of which are allocated, BF 1.2; an owned 1N4148 (owner, kit card contents UNVERIFIED) can serve).
- Op-amp section: assigned with the op-amp split at breakout layout (C10).
- LDR side: the vactrol LDR in parallel with RP13 (resonance JFET path), as in the old docs;
  UNVERIFIED against the synth schematic.

## CV Input Protection (DB-9 B inputs)

One circuit for both B CV lines (audit B17, BF 3.3). Lines: **B:3 VCA CV → TP10** and
**B:5 Filter CV → TP26** (BF 2.2). The expander adds 10kΩ at its op-amp output; the MB board adds:

```
  DB-9 B pin 3 or 5 ──[100kΩ]──┬────────────── to injection point (TP10 for B:3, TP26 for B:5)
                               │
                               ├── BAT85 anode at node, cathode to +12V_BRK
                               ├── BAT85 anode at -12V_BRK, cathode at node
                               └── 1nF (owned) ── GND
```

- The clamps hold the node within about one BAT85 drop of the breakout rails. The old ±5 V clamp,
  the "-0.3 V / +5.3 V" BAT54S clamp and the 1kΩ / "±12.3 V, 12 mA" text are withdrawn: a +5 V /
  GND clamp would clip legitimate CV into the synth's ±12 V summing node, and 1kΩ lets about 4-10 mA
  into the unpowered breakout rails (audit B17, S39). BAT54S is not owned; BAT85 is (two per line).
- Back-feed (BF 3.3): with the synth off and the expander on, at most (10 - 0.24) / 110k ≈ 89 µA
  flows into the unpowered breakout rail. Bounded, not zero; acceptance is BT-3 (unpowered rails
  below about 0.3 V).
- CV depth: whether the synth's own 220kΩ (TP26, R67) and 100kΩ (TP10, R25) sit after these points
  is UNVERIFIED (E-18); the extra 100kΩ may cut depth (BT-4). Fallback 47kΩ, then repeat BT-3.
- 1nF with 100kΩ gives a 0.1 ms time constant (about 1.6 kHz corner).

The UART lines (B:1 TX, B:6 RX) go from the DB-9 B cups through the MB-side 1kΩ resistors to the
LPC (connection map section 5.4); they do not use the breakout's op-amps. The LPC pins (UART1,
LQFP 62 / 63) are UNVERIFIED until the Phase 0 continuity gate G1.

## Pico H Mounting — removed

Removed (audit S12, R3-18). The Pico, OLED, encoder, tap button, RGB LED and clock I/O are on the
expander (connection map sections 1, 4 and 10). No Pico header, VSYS path or 3V3 rail on the breakout.

## PCB Size Estimate

- ~60mm x 40mm (fits inside MicroBrute near digital board); the stripboard version is
  90 × 50 mm (`breakout_stripboard.md`). Free space inside the synth is UNVERIFIED.
- Single-sided perfboard adequate
- Mount with VHB tape or M2 standoffs

## Component Summary

Ownership from BF section 1 (Have / Missing). Resistor-kit values are Have but the exact values in
the kit are still to confirm (BF Q5).

| Component | Qty | Package | Status |
|-----------|-----|---------|--------|
| TL074CN | 1 | DIP-14 | Have |
| TL072CP | 1-2 (count chosen at breakout layout, C10) | DIP-8 | Have (6) |
| CD40106 | 1 | DIP-14 | Have |
| 78L05 | 1 (Provisional) | TO-92 | Have |
| BAT85 | 6 (2 rails, 4 CV clamps) | DO-34 axial | Have (10, budget BF 1.2) |
| 1kΩ | 15 (8 TL074 in/out, 2 env/LFO out, 1 gate out, 2 UART MB side, 2 triangle) | 1/4W | Have (kit) |
| 10kΩ | 3 (gate in, env in, LFO in) | 1/4W | Have (kit) |
| 100kΩ | 4 (2 CV series, 2 triangle gain) | 1/4W | Have (kit) |
| 220Ω | 1 (A:2 pitch series) | 1/4W | Have (kit) |
| 1MΩ | 5 (+IN bias) | 1/4W | Have (kit) |
| 1nF ceramic | 3 (gate pin 1, 2 CV nodes) | — | Have (5) |
| 100nF ceramic | 6-8 | — | Have |
| 10µF/63V electrolytic | 4-8 (2-4 per rail) | — | Have (10) |
| Vactrol driver parts | TO DESIGN | — | Vactrol Have (type unread, Q2) |
| DIP-14 socket | 2 | — | Not on the owned list (Q13) |
| DIP-8 socket | 1-2 | — | Not on the owned list (Q13) |
| Pin headers | various | 2.54mm | Not on the owned list (Q13) |
| DB-9 solder-cup | 2 | — | Have (count, gender UNVERIFIED, Q9) |
