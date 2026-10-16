# MACROBRUTE Breakout Board — Stripboard Layout

Mounts inside MicroBrute. Houses analog buffers, gate conditioning, CV-input clamps, the vactrol
driver (TO DESIGN) and the power input. Powered from the synth only (TP70 / TP71 / TP72). The Pico
is on the expander, not on this board (audit S12).

**Board:** 90 × 50mm stripboard, 20 rows × 28 cols, 2.54mm pitch (as drawn by
`tools/generate_layouts.py` → `breakout_layout.svg`, "LAY" below; the old "35 columns" figure was
wrong, audit B16)
**Tracks:** Horizontal copper strips (left → right)
**View:** All diagrams show COMPONENT SIDE (top view, looking down)

**Build status: do not build from this page or from LAY yet.** LAY is the reference geometry
(audit R3-08, conflict C14), but it still carries the defects listed under "LAY defects" below, and
the netlist on this page changes several circuits (gate stage, LED drivers removed, vactrol driver
TO DESIGN). Hole-level positions for the changed parts are TO DESIGN when the layout is regenerated
in a later diagram batch.

For pin-by-pin DIP layouts during the build, see `ic_pinout_reference.md` (pin tables checked
against the datasheets). For the spatial component placement, see the **MACROBRUTE — Breakout Board
Stripboard Layout** and **Zone Layout** SVGs in this section, with the caveat above.

---

## Track Cuts (Copper Side)

**Every DIP IC needs a track cut between its left and right pin columns
to prevent shorting opposite pins.** Use a 3mm drill bit twisted by hand
or a proper stripboard track cutter.

The old placement on this page (U1 at cols 5/8, U2 at cols 18/21 on rows 6-9, cuts only at cols
6-7 and 19-20) shorted nets: rows 6-9 had no cut between col 8 and col 18, so U1 pin 14 (OUT_D) met
U2 pin 1 (OUT_A), pin 13 met pin 2, pin 12 met pin 3, and U1 pin 11 (V-) met U2 pin 5 (+IN_B)
(audit B16). The placement below is LAY's, which has no such short.

### U1 — TL074 at rows 6-12, left col 10, right col 13

| Row | Cut At | Left Pin | Right Pin | Why |
|-----|-------------|----------|-----------|-----|
| 6 | cols 11, 12 | 1 OUT_A | 14 OUT_D | Different outputs |
| 7 | cols 11, 12 | 2 -IN_A | 13 -IN_D | Different feedback |
| 8 | cols 11, 12 | 3 +IN_A | 12 +IN_D | Different inputs |
| 9 | cols 11, 12 | 4 V+ | 11 V- | **CRITICAL: V+ vs V-** |
| 10 | cols 11, 12 | 5 +IN_B | 10 +IN_C | Different inputs |
| 11 | cols 11, 12 | 6 -IN_B | 9 -IN_C | Different feedback |
| 12 | cols 11, 12 | 7 OUT_B | 8 OUT_C | Different outputs |

Further LAY cuts: col 15 on rows 6, 8, 10, 12 (IC right pins vs headers); col 20 on rows 8, 10
(output headers vs right-side input resistors); cols 6 and 22 on rows 8, 10 (input 1kΩ in series).

### U2 — TL072 at rows 15-18, left col 22, right col 25

| Row | Cut At | Left Pin | Right Pin |
|-----|-------------|----------|-----------|
| 15 | cols 23, 24 | 1 OUT_A | 8 V+ |
| 16 | cols 23, 24 | 2 -IN_A | 7 OUT_B |
| 17 | cols 23, 24 | 3 +IN_A | 6 -IN_B |
| 18 | cols 23, 24 | 4 V- | 5 +IN_B |

Further LAY cuts: col 26 on row 15 (V+ vs the A:3 header); cols 19 on rows 17, 18 and col 21 on
row 18 (input 10kΩ in series; V- vs the LFO input).

### U3 — CD40106 at rows 13-19, left col 5, right col 8

| Row | Cut At | Left Pin | Right Pin |
|-----|-------------|----------|-----------|
| 13 | cols 6, 7, 9 | 1 IN_A | 14 VDD |
| 14 | cols 6, 7, 9 | 2 OUT_A | 13 IN_F |
| 15 | cols 6, 7, 9 | 3 IN_B | 12 OUT_F |
| 16 | cols 6, 7, 9 | 4 OUT_B | 11 IN_E |
| 17 | cols 6, 7, 9 | 5 IN_C | 10 OUT_E |
| 18 | cols 6, 7, 9 | 6 OUT_C | 9 IN_D |
| 19 | cols 6, 7, 9 | 7 VSS | 8 OUT_D |

Col 9 isolates the right-hand pins from the area to the right. Row 13 also has a cut at col 4
(TP83 series 10kΩ).

### Power-input cuts (LAY)

- **Row 3, cols 3 and 6:** +12V input pad (col 1) → D1 → series element → +12V rail.
- **Row 4, cols 3 and 6:** same for -12V. In LAY D2 is drawn in the same direction as D1, which is
  **backwards** for -12V (audit B15): see the power table below.
- Row 1 (+5V input, D3 1N5817, jumper to a "+5V/VSYS" pad on row 20) is removed: no 5 V comes from
  the synth and there is no Pico on this board.

---

## Wiring Table

### Power Connections

Rail protection part is OPEN (owner), audit conflict C12: a BAT85 per rail (as below) or a
4.7-10 Ω series resistor per rail. Ferrites and 100µF parts are not owned (BF 1.4, 1.5).

| From | To | Wire/Component |
|------|----|----------------|
| J_PWR pin 1 (+12V from TP70) | D1 **anode** (BAT85) | Header pin |
| D1 cathode | Row 3 (+12V_BRK rail) | On track |
| J_PWR pin 2 (-12V from TP71) | D2 **cathode** (BAT85) | Header pin: the cathode faces the -12 V source |
| D2 anode | Row 4 (-12V_BRK rail) | On track: the anode faces the load (audit B15) |
| J_PWR pin 3 (GND from TP72) | Row 5 (GND rail) | Header pin; TP72 star, own lead (audit N13) |
| Row 3 near U1 pin 4 | U1 pin 4 (V+) | Jumper, row 3 col 9 → row 9 col 9 (LAY) |
| Row 4 near U1 pin 11 | U1 pin 11 (V-) | Jumper, row 4 col 14 → row 9 col 14 (LAY) |
| Row 3 | U2 pin 8 (V+) | Jumper, row 3 col 25 → row 15 col 25 (LAY) |
| Row 4 | U2 pin 4 (V-) | Jumper, row 4 col 22 → row 18 col 22 (LAY) |
| Row 3 (+12V_BRK) | 78L05 pin 3 INPUT; pin 2 COMMON to GND; pin 1 OUTPUT = +5V_LOC | Provisional (BF 3.4); position TO DESIGN |
| +5V_LOC | U3 pin 14 (VDD) | Jumper |
| Row 5 (GND) | U3 pin 7 (VSS) | Jumper, row 5 col 5 → row 19 col 5 (LAY) |
| Row 3 and row 4 | 2-4× 10µF/63V each, to GND | Electrolytic, polarity: + to row 3; − to row 4 |
| Each IC V+ pin | 100nF to GND | Within 10mm of pin; needs its GND jumper (LAY lacks it) |
| Each IC V- pin | 100nF to GND | Within 10mm of pin; needs its GND jumper (LAY lacks it) |

There is no J_PWR +5V pin and no D3: nothing on this board takes 5 V from the synth.

### U1 — TL074 Buffer Connections

| Signal | MB Source | → | Buffer Input | → | Buffer Output | → | DB-9 A |
|--------|-----------|---|--------------|---|---------------|---|--------|
| Saw | TP94 | 1kΩ | U1 pin 3 (+IN_A) | follower | U1 pin 1 (OUT_A) | 1kΩ | Pin 7 |
| Square | TP93 | 1kΩ | U1 pin 5 (+IN_B) | follower | U1 pin 7 (OUT_B) | 1kΩ | Pin 8 |
| VCO Mix | TP30 | 1kΩ | U1 pin 10 (+IN_C) | follower | U1 pin 8 (OUT_C) | 1kΩ | Pin 5 |
| VCF Out | TP19 | 1kΩ | U1 pin 12 (+IN_D) | follower | U1 pin 14 (OUT_D) | 1kΩ | Pin 6 |

**Feedback (unity gain):** Jumper each output pin to its adjacent -IN pin:
- Pin 1 → Pin 2 (OUT_A → -IN_A)
- Pin 7 → Pin 6 (OUT_B → -IN_B)
- Pin 8 → Pin 9 (OUT_C → -IN_C)
- Pin 14 → Pin 13 (OUT_D → -IN_D)

The 1kΩ output resistor sits after this tap (outside the loop). LAY does not draw the four output
1kΩ resistors (audit S34); add them when the layout is regenerated.

**Bias:** 1MΩ from each +IN pin to GND (row 5), four in total (replaces 10MΩ, audit N11). LAY draws
only two, overlapping in column 7 (audit S34).

### U2 — TL072 Auxiliary Buffers

| Signal | Source | → | Buffer Input | → | Output | → | DB-9 A |
|--------|--------|---|--------------|---|--------|---|--------|
| Envelope | Mod matrix / TP5 | 10kΩ | U2 pin 3 (+IN_A) | follower | U2 pin 1 | 1kΩ | Pin 3 |
| LFO | Mod matrix | 10kΩ | U2 pin 5 (+IN_B) | follower | U2 pin 7 | 1kΩ | Pin 4 |

The output 1kΩ sits after the feedback tap (audit S36, R3-15); LAY has none.

**Triangle 2× gain and vactrol driver:** U2 has two sections and four jobs (env, LFO, triangle,
vactrol). The IC choice (2× TL072 or 2× TL074) is OPEN (owner), audit S17 / conflict C10. Triangle
circuit (to a body jack, not the DB-9): TP124 → 1kΩ → +IN; 100kΩ from OUT to -IN; 100kΩ from -IN
to GND; 1MΩ bias on +IN; OUT → 1kΩ → body jack (Gain = 1 + 100k/100k = 2×). Position TO DESIGN.

### U3 — CD40106 Gate Buffer

Provisional (BF 3.4). The old 10kΩ pull-up to +5V is removed (audit B14).

| Net | Connection |
|-----|------------|
| Gate in | TP83 → 10kΩ series → U3 pin 1 (IN_A); 1nF from pin 1 to GND at the pin; no pull-up |
| Inverter 1 → 2 | U3 pin 2 (OUT_A) → U3 pin 3 (IN_B) (row 14 left to row 15 left) |
| Gate out | U3 pin 4 (OUT_B) → 1kΩ → DB-9 A pin 1 |
| Unused inputs | U3 pins 5, 9, 11, 13 → GND (audit S34) |
| Unused outputs | U3 pins 6, 8, 10, 12 not connected |
| Supply | pin 14 VDD = +5V_LOC, pin 7 VSS = GND, 100nF VDD-VSS |

LAY changes needed: the "→ DB9A:1" header on row 14 (pin 2) moves to pin 4 via the 1kΩ; LAY's
"VCO" on gate B (100kΩ pin 3-4, 100nF pin 3-GND, outputs to "△ DB9A:9" and "□ DB9A:2") is deleted:
gate B is the second inverter, A:9 is GND and A:2 is Pitch (BF 2.3).

Expander side of A:1 (not on this board): gate jack, then 22kΩ / 33kΩ divider into a
fault-tolerant Pico GPIO (BF 3.5).

### LED Drivers — removed

Q1-Q3 (2N3904), their resistors and LEDs are removed (audit S12, R3-17). The RGB LED is on the
expander, driven from GP8-10. The 2N3904 is not owned.

### Vactrol Driver — TO DESIGN

The old 2N3904 driver is withdrawn: it switched the LED on/off at about 9 mA instead of giving a
continuous control, and took CV from DB-9 B pin 3, which is now VCA CV (audit S37). Replacement:
TL072 voltage-to-current stage, CV from the new MB panel jack. R_sense waits for the vactrol
marking (OPEN (owner), BF Q2). Constraints are listed in `breakout_pcb.md`, "Vactrol Driver".

### CV Input Clamps (DB-9 B:3 VCA CV, B:5 Filter CV)

Per line (BF 3.3): DB-9 B cup → 100kΩ → node; node → BAT85 (anode) to +12V_BRK (cathode); BAT85
anode at -12V_BRK, cathode at node; 1nF node to GND; node → TP10 (B:3) or TP26 (B:5). Position
TO DESIGN.

---

## Connector Headers

The old 12-pin J_PICO header (SPI OLED on GP16-20, "MIDI" on GP4/GP5) is removed: the Pico is on
the expander, and that map disagreed with `firmware/pico/config.py` (audit S12, R3-18).

| Header | Pins | Connects To |
|--------|------|-------------|
| J_PWR | 3 | +12V, -12V, GND from TP70 / TP71 / TP72 only |
| J_IN | 8 | Flying leads from MB test points |
| J_OUT | 9 | DB-9 A solder cups |
| J_CV_IN | to re-derive (audit N22) | DB-9 B solder cups: VCA CV (B:3), Filter CV (B:5), grounds |

LAY puts all headers on row 20 with no cuts, so every header pin would short (audit S34): add cuts
or mount the headers across the strips. The UART lines (B:1, B:6) do not use this board; they run
through the MB-side 1kΩ resistors to the LPC (connection map section 5.4).

---

## LAY defects (fix before building; audit S34, R3-09)

1. D2 drawn backwards for -12V (B15).
2. Row 20 has no cuts: J_PICO, J_OUT, J_IN and the +5V/VSYS pad short together. J_PICO and the
   +5V/VSYS pad are removed anyway.
3. Decoupling caps at U1 and U2 have no GND jumper; the U2 caps sit on row 15 (OUT_A strip) and an
   isolated V- hole, not on V+ / V-.
4. CD40106 unused inputs not tied.
5. Q1-Q3 share uncut strip segments with their resistors; they are removed.
6. Two of four bias resistors drawn, overlapping; value changes to 1MΩ.
7. No 1kΩ output resistors on the TL074 or TL072 outputs.
8. Gate B wired as an oscillator with outputs to A:9 and A:2 (wrong pins); single inverter on the
   gate; no 1kΩ at the gate output.
9. +5V input pad, D3 and the "+5V → U3 & Pico" zone: replaced by the local 78L05.

---

## Build & Test Order

1. **Solder DIP sockets** (U1, U2, U3) — do NOT insert ICs yet
2. **Make all track cuts** — verify each with multimeter continuity
3. **Power section:** Solder D1, D2 (check D2: cathode on the -12V header side), the bulk and
   decoupling caps, and the 78L05
4. **Test power:** Apply +12V/-12V only, measure at IC socket pins:
   - U1 socket: pin 4 = +12V_BRK, pin 11 = -12V_BRK, verify NO short between them
   - U2 socket: pin 8 = +12V_BRK, pin 4 = -12V_BRK
   - U3 socket: pin 14 = +5V_LOC, pin 7 = 0V
5. **Insert U1** (TL074): Solder feedback jumpers, input/output resistors,
   bias resistors. Test each channel with a signal source.
6. **Insert U2** (TL072): Same process for aux buffers.
7. **Insert U3** (CD40106): Solder gate conditioning components.
   Test with manual gate (touch the 10kΩ input end to +5V_LOC); scope TP83 high and low first (BF BT-5).
8. **CV clamps:** Solder the 100kΩ / BAT85 / 1nF networks; check the clamp diode orientation.
9. **Vactrol driver:** TO DESIGN; build and test on the bench before installing.
10. **Connector headers:** Solder J_IN, J_OUT, J_CV_IN last.

---

## Component Summary (this board only)

| Component | Qty | Notes |
|-----------|-----|-------|
| Stripboard 90×50mm | 1 | 20×28 holes as laid out (not on the owned list, Q13) |
| DIP-14 socket | 2 | U1 TL074, U3 CD40106 (Q13) |
| DIP-8 socket | 1-2 | U2 TL072 (×1 or ×2) (Q13) |
| TL074CN | 1 | Waveform buffers (Have) |
| TL072CP | 1-2 | Aux buffers, triangle, vactrol (Have; count OPEN, C10) |
| CD40106BE | 1 | Gate Schmitt trigger, two gates in series (Have) |
| 78L05 | 1 | +5V_LOC for U3 (Have; Provisional) |
| BAT85 | 6 | 2 rail protection (C12 OPEN), 4 CV clamps (Have) |
| 1kΩ resistor | 13 | 8 TL074 in/out, 2 env/LFO out, 1 gate out, 2 triangle |
| 10kΩ resistor | 3 | Gate input, env input, LFO input |
| 100kΩ resistor | 4 | 2 CV series, 2 triangle gain |
| 1MΩ resistor | 5 | +IN bias (4 TL074, 1 triangle) |
| 1nF ceramic | 3 | Gate pin 1, 2 CV nodes (Have) |
| 100nF ceramic | 6-8 | IC decoupling, 78L05 output (Have) |
| 10µF/63V electro | 4-8 | Rail bulk, 2-4 per rail (Have) |
| Vactrol driver parts | TO DESIGN | Vactrol Have, type unread (Q2) |
| Pin header 2.54mm | ~20 pins | J_PWR, J_IN, J_OUT, J_CV_IN (Q13) |
