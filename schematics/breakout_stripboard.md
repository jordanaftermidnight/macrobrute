# MACROBRUTE Breakout Board — Stripboard Layout

Mounts inside MicroBrute. Houses analog buffers, gate conditioning,
LED drivers, vactrol driver, and power supply. Pico H connects via
pin headers (mounted separately with standoffs or VHB tape).

**Board:** 90 × 50mm stripboard (20 rows × 35 cols, 2.54mm pitch)
**Tracks:** Horizontal copper strips (left → right)
**View:** All diagrams show COMPONENT SIDE (top view, looking down)

For pin-by-pin DIP layouts during the build, see the **DIP IC Pinout Reference**
SVG (TL074 / TL072 / CD40106 plus the regulator and transistor) in this manual.
For the spatial component placement on the stripboard itself, see the
**MACROBRUTE — Breakout Board Stripboard Layout** and **Zone Layout** SVGs in
this section — they replace the ASCII overview that previously lived here.

---

## Track Cuts (Copper Side)

**Every DIP IC needs a track cut between its left and right pin columns
to prevent shorting opposite pins.** Use a 3mm drill bit twisted by hand
or a proper stripboard track cutter.

### U1 — TL074 at rows 6-12, left col 5, right col 8

| Row | Cut Between | Left Pin | Right Pin | Why |
|-----|-------------|----------|-----------|-----|
| 6 | cols 6-7 | 1 OUT_A | 14 OUT_D | Different outputs |
| 7 | cols 6-7 | 2 -IN_A | 13 -IN_D | Different feedback |
| 8 | cols 6-7 | 3 +IN_A | 12 +IN_D | Different inputs |
| 9 | cols 6-7 | 4 V+ | 11 V- | **CRITICAL: V+ vs V-** |
| 10 | cols 6-7 | 5 +IN_B | 10 +IN_C | Different inputs |
| 11 | cols 6-7 | 6 -IN_B | 9 -IN_C | Different feedback |
| 12 | cols 6-7 | 7 OUT_B | 8 OUT_C | Different outputs |

### U2 — TL072 at rows 6-9, left col 18, right col 21

| Row | Cut Between | Left Pin | Right Pin |
|-----|-------------|----------|-----------|
| 6 | cols 19-20 | 1 OUT_A | 8 V+ |
| 7 | cols 19-20 | 2 -IN_A | 7 OUT_B |
| 8 | cols 19-20 | 3 +IN_A | 6 -IN_B |
| 9 | cols 19-20 | 4 V- | 5 +IN_B |

### U3 — CD40106 at rows 13-19, left col 5, right col 8

| Row | Cut Between | Left Pin | Right Pin |
|-----|-------------|----------|-----------|
| 13 | cols 6-7 | 1 IN_A | 14 VDD |
| 14 | cols 6-7 | 2 OUT_A | 13 IN_F |
| 15 | cols 6-7 | 3 IN_B | 12 OUT_F |
| 16 | cols 6-7 | 4 OUT_B | 11 IN_E |
| 17 | cols 6-7 | 5 IN_C | 10 OUT_E |
| 18 | cols 6-7 | 6 OUT_C | 9 IN_D |
| 19 | cols 6-7 | 7 VSS | 8 OUT_D |

### Additional Track Cuts

- **Row 3, between cols 2-3:** Isolate power input header from rail
  (diode + ferrite go between them)
- **Row 4, between cols 2-3:** Same for -12V
- **Rows 13-19, col 4:** Isolate U3 input section from U1 area

---

## Wiring Table

### Power Connections

| From | To | Wire/Component |
|------|----|----------------|
| J_PWR pin 1 (+12V from TP70) | D1 anode (1N5817) | Header pin |
| D1 cathode | FB1 (100Ω ferrite) | On track |
| FB1 | Row 3 (+12V rail) | On track |
| Row 3 near U1 pin 4 | U1 pin 4 (V+) | Jumper wire, row 3 → row 9 col 5 |
| Row 4 (-12V rail) | U1 pin 11 (V-) | Jumper wire, row 4 → row 9 col 8 |
| J_PWR pin 2 (-12V from TP71) | D2 anode (1N5817) | Header pin |
| D2 cathode | FB2 (100Ω ferrite) | On track |
| FB2 | Row 4 (-12V rail) | On track |
| J_PWR pin 3 (+5V from MB) | D3 anode (1N5817) | Header pin |
| D3 cathode | J_PICO VSYS + U3 VDD | Wire to row 13 col 8 (VDD) |
| J_PWR pin 4 (GND from TP72) | Row 5 (GND rail) | Header pin |
| Row 3, near col 30 | 100µF/25V (+) | Electrolytic to GND |
| Row 4, near col 30 | 100µF/25V (-) | Electrolytic to GND |
| Each IC V+ pin | 100nF to GND | Place within 10mm of pin |
| Each IC V- pin | 100nF to GND | Place within 10mm of pin |

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

**Bias:** 10MΩ from each +IN pin to GND (row 5). Provides DC bias path.

### U2 — TL072 Auxiliary Buffers

| Signal | Source | → | Buffer Input | → | Output | → | DB-9 A |
|--------|--------|---|--------------|---|--------|---|--------|
| Envelope | Mod matrix | 10kΩ | U2 pin 3 (+IN_A) | follower | U2 pin 1 | — | Pin 3 |
| LFO | Mod matrix | 10kΩ | U2 pin 5 (+IN_B) | follower | U2 pin 7 | — | Pin 4 |

**Triangle 2× gain:** If using U2 section B for triangle instead of LFO:
- TP124 → 1kΩ → U2 pin 5 (+IN_B)
- 100kΩ from U2 pin 7 (OUT_B) to pin 6 (-IN_B) — feedback
- 100kΩ from pin 6 (-IN_B) to GND — gain resistor
- Gain = 1 + 100k/100k = 2×

**Design choice:** With only 2 op-amp sections in U2, pick 2 of the 3
functions (env, LFO, triangle). To do all 3 + vactrol driver, add a
second TL072 (the BOM includes 2 for the breakout). Mount at rows 10-13,
cols 18-21.

### U3 — CD40106 Gate Buffer

| Signal | Source | → | Input | → | Output | → | DB-9 A |
|--------|--------|---|-------|---|--------|---|--------|
| Gate | TP83 | 10kΩ series | U3 pin 1 (IN_A) | Schmitt | U3 pin 2 (OUT_A) | direct | Pin 1 |

Additional components at U3 pin 1:
- 10kΩ pull-up to +5V (clean logic level)
- 100nF to GND (noise filter)

### LED Drivers (Q1-Q3, 2N3904 NPN)

```
  +3.3V ──[470Ω]── LED(+) ── LED(-) ──── Q Collector
                                           │
  Pico GPIO ──[1kΩ]──── Q Base            │
                                           │
                         Q Emitter ────── GND
```

| LED | GPIO | Pico Pin | Q | Function |
|-----|------|----------|---|----------|
| LED1 (Clock) | GP8 | Pin 11 | Q1 | Clock tick flash |
| LED2 (Gate) | GP9 | Pin 12 | Q2 | Gate activity |
| LED3 (Mode) | GP10 | Pin 14 | Q3 | Mode indicator |

**R_base:** 1kΩ (I_b ≈ 2.6mA, saturates 2N3904)
**R_led:** 470Ω for dim (~2mA), 220Ω for bright (~5mA)

### Vactrol Driver

Receives CV from expander via DB-9 B pin 3. Drives vactrol LED to
modulate resonance (LDR parallels RP13).

```
  DB-9 B pin 3 ──[1kΩ]── U2_spare +IN (follower)
                                    │
                                   OUT ──[1kΩ]── 2N3904 Base
                                                    │
                                                 Collector
                                                    │
                                              Vactrol LED (+)
                                                    │
                                              Vactrol LED (-)
                                                    │
                                                 [1kΩ] (current limit)
                                                    │
                                                   GND

  Max LED current: (12 - 2 - 0.7) / 1k ≈ 9mA (safe for vactrol)
  Vactrol LDR: solder in parallel with RP13 inside MicroBrute
```

---

## J_PICO Pin Header (12-pin, row 20, cols 25-35)

Connect to Pico H via ribbon cable or individual wires.

| Pin | Signal | Pico GPIO | Pico Physical Pin |
|-----|--------|-----------|-------------------|
| 1 | OLED SCK | GP18 | 24 |
| 2 | OLED MOSI | GP19 | 25 |
| 3 | OLED CS | GP17 | 22 |
| 4 | OLED DC | GP16 | 21 |
| 5 | OLED RST | GP20 | 26 |
| 6 | ENC CLK | GP14 | 19 |
| 7 | ENC DT | GP15 | 20 |
| 8 | ENC SW | GP13 | 17 |
| 9 | MIDI TX | GP4 | 6 |
| 10 | MIDI RX | GP5 | 7 |
| 11 | +3.3V | 3V3 OUT | 36 |
| 12 | GND | GND | 38 |

Button (GP12), Clock Out (GP22), Clock In (GP21) wire directly from
Pico to their destinations — not through this header.

---

## Build & Test Order

1. **Solder DIP sockets** (U1, U2, U3) — do NOT insert ICs yet
2. **Make all track cuts** — verify each with multimeter continuity
3. **Power section:** Solder D1-D3, ferrites, bulk caps, decoupling caps
4. **Test power:** Apply +12V/-12V/+5V, measure at IC socket pins:
   - U1 socket: pin 4 = +12V, pin 11 = -12V, verify NO short between them
   - U2 socket: pin 8 = +12V, pin 4 = -12V
   - U3 socket: pin 14 = +5V, pin 7 = 0V
5. **Insert U1** (TL074): Solder feedback jumpers, input/output resistors,
   bias resistors. Test each channel with a signal source.
6. **Insert U2** (TL072): Same process for aux buffers.
7. **Insert U3** (CD40106): Solder gate conditioning components.
   Test with manual gate (touch wire to +5V through 10kΩ).
8. **LED drivers:** Solder Q1-Q3 + resistors. Test from Pico GPIO.
9. **Vactrol driver:** Build and test on bench before installing.
10. **Connector headers:** Solder J_IN, J_OUT, J_PICO last.

---

## Component Summary (this board only)

| Component | Qty | Notes |
|-----------|-----|-------|
| Stripboard 90×50mm | 1 | 20×35 holes |
| DIP-14 socket | 2 | U1 TL074, U3 CD40106 |
| DIP-8 socket | 1-2 | U2 TL072 (×1 or ×2) |
| TL074CN | 1 | Waveform buffers |
| TL072CP | 1-2 | Aux buffers + vactrol |
| CD40106BE | 1 | Gate Schmitt trigger |
| 2N3904 | 3 | LED drivers |
| 1N5817 | 3 | Power protection |
| Ferrite bead 100Ω | 2 | Power filtering |
| 1kΩ resistor | 12 | Input/output/current limit |
| 10kΩ resistor | 3 | Gate pull-up + input |
| 10MΩ resistor | 4 | +IN bias to GND |
| 100kΩ 1% resistor | 2 | Triangle gain (if used) |
| 220-470Ω resistor | 3 | LED current limit |
| 100nF ceramic | 6 | IC decoupling |
| 100µF/25V electro | 2 | Power bulk |
| BAT54S | 3 | CV input protection (DB-9 B) |
| 3mm LED | 3 | Clock, gate, mode |
| Pin header 2.54mm | ~30 pins | J_PWR, J_IN, J_OUT, J_PICO |
