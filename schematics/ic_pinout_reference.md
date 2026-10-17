# MACROBRUTE — IC Pinout Reference

Pinouts for the ICs used in the MACROBRUTE project, checked against the datasheets in
`datasheets/` (see `docs/DATASHEETS.md` for files, revisions and page numbers). Page numbers are
PDF page numbers. Anything not checked against a datasheet is marked UNVERIFIED.

**Warning about the pinout SVGs in this section.** The drawings `ic_pinout_tl074.svg`,
`ic_pinout_tl072.svg`, `ic_pinout_cd40106.svg`, `ic_pinout_cd4051.svg` and `dip_pinout_reference.svg`
carry wrong pin labels (for example TL074 pin 11 drawn as GND and pins 8-14 swapped; TL072 pins 5
and 7 swapped; CD40106 right-hand inputs and outputs swapped; CD4051 right-hand side reversed; LF398
in `dip_pinout_reference.svg` wrong). They are redrawn in a later diagram batch. **Build from the
tables on this page, not from those drawings.**

---

## Op-Amps

### TL074 — Quad JFET-Input Op-Amp
Used for: MB breakout U1 waveform buffers (Saw, Square, Mix, VCF); owned x4.
- 14-pin PDIP (TI SLOS080W Fig 4-8, p8):

| Pin | Function | Pin | Function |
|-----|----------|-----|----------|
| 1 | 1OUT | 14 | 4OUT |
| 2 | 1IN- | 13 | 4IN- |
| 3 | 1IN+ | 12 | 4IN+ |
| 4 | VCC+ | 11 | VCC- |
| 5 | 2IN+ | 10 | 3IN+ |
| 6 | 2IN- | 9 | 3IN- |
| 7 | 2OUT | 8 | 3OUT |

- Supply: ±12 V here (VCC+ pin 4, VCC- pin 11); within the recommended range (p10-p11).
- TL07xC slew rate 8 V/µs min, 20 V/µs typ (p16); gain-bandwidth 5.25 MHz typ (3 MHz for NS/PS
  packages and M devices) (p15). Quiescent current 1.4 mA typ, 2.5 mA max per amplifier (p16).
- Common-mode range at ±15 V: ±11 V min (p15), i.e. keep inputs about 4 V inside each rail.

### TL072 — Dual JFET-Input Op-Amp
Used for: breakout env / LFO followers, triangle gain, vactrol driver (TO DESIGN); expander LFO,
slew limiter, S&H buffer; owned x6.
- 8-pin PDIP (TI SLOS080W Fig 4-5, p5): 1 1OUT, 2 1IN-, 3 1IN+, 4 VCC-, 5 2IN+, 6 2IN-, 7 2OUT,
  8 VCC+.
- Same family figures as the TL074 above (same datasheet).

### LM358 — Dual Op-Amp (Single Supply)
Used for: nothing in the decided design (owned x10, spare).
- 8-pin PDIP (TI SLOS068AB Table 4-1, p3): 1 OUT1, 2 IN1-, 3 IN1+, 4 V-, 5 IN2+, 6 IN2-, 7 OUT2,
  8 V+.
- Supply 3-30 V for LM358 / LM358A, 3-36 V for the B versions (p5); gain-bandwidth 0.7 MHz
  (1.2 MHz for B versions) (p2). The owned parts' version is UNVERIFIED.
- Common-mode range includes the negative rail; output swings near ground.

---

## Logic ICs

### CD40106 — Hex Schmitt Trigger Inverter
Used for: MB breakout gate conditioner (two gates in series); owned x3.
- 14-pin (TI SCHS097F p3); each output is the inverse of its input:

| Pin | Function | Pin | Function |
|-----|----------|-----|----------|
| 1 | A in | 14 | VDD |
| 2 | G = NOT A | 13 | F in |
| 3 | B in | 12 | L = NOT F |
| 4 | H = NOT B | 11 | E in |
| 5 | C in | 10 | K = NOT E |
| 6 | I = NOT C | 9 | D in |
| 7 | VSS | 8 | J = NOT D |

- Supply 3-18 V recommended, 20 V abs max (p4). Inputs -0.5 V to VDD + 0.5 V, ±10 mA (p4).
- VT+ at VDD 5 V: 2.2 / 2.9 / 3.6 V min / typ / max (p5-p6).
- Tie unused inputs to VSS or VDD.

### CD4049UB — Hex Inverting Buffer
Used for: expander Clock IN and Clock OUT buffers on Pico 3V3 (BF 3.7); owned x3.
- 16-pin (TI SCHS046L p3): 1 VCC, 2 G (out of A), 3 A, 4 H (out of B), 5 B, 6 I (out of C), 7 C,
  8 VSS, 9 D, 10 J (out of D), 11 E, 12 K (out of E), 13 NC, 14 F, 15 L (out of F), 16 NC.
- Supply 3-18 V recommended, 20 V abs max (p5-p6).
- Input above VCC: the sheet contradicts itself (p1 says VIH may exceed VCC for level conversion;
  p17 says the inputs have clamp diodes to VCC and must stay below VCC). The design treats the
  input as clamped (bench check BF BT-10).

### CD4051 — 8-Channel Analog Multiplexer/Demultiplexer
Used for: the owned-parts S&H alternative (`expander_circuits.md` section 2b); owned x2.
- 16-pin (TI SCHS047O p3): 1 Y4, 2 Y6, 3 COM (common in/out), 4 Y7, 5 Y5, 6 INH, 7 VEE, 8 VSS, 9 C,
  10 B, 11 A, 12 Y3, 13 Y0, 14 Y1, 15 Y2, 16 VDD.
- Supply V+ to V- 20 V abs max (p5): not ±12 V. DC input on control pins -0.5 V to VDD + 0.5 V,
  ±10 mA (p5).
- INH high turns all channels off (truth table, Table 7-1). Address and INH logic levels are
  0 = VSS, 1 = VDD; the analog signal may swing from VEE to VDD (p10).

### CD4024 — 7-Stage Ripple Counter
DROPPED from the design (clock division is in Pico firmware); not owned. The pin drawing in the
datasheet copy is not machine-readable, so no pinout is given here (UNVERIFIED).

### CD4066 — Quad Bilateral Switch
DROPPED from the design; not owned. On-state resistance 125 Ω typ at 15 V (TI SCHS051J p1); pinout
not checked for this page (UNVERIFIED).

---

## Analog Special Function

### LF398 — Sample and Hold
Used for: expander S&H (default; not owned, BF Q1).
- PDIP-8 (TI SNOSBI3C Pin Functions, p3): 1 V+, 2 OFFSET ADJUST, 3 INPUT, 4 V-, 5 OUTPUT,
  6 Ch (hold capacitor), 7 LOGIC REFERENCE, 8 LOGIC. TO-99 uses the same numbering; SOIC-14 is a
  different map.
- Supply ±5 V to ±18 V (p1, p4). Sample while LOGIC is high relative to LOGIC REFERENCE (p14).
- Leakage into the hold capacitor 30 pA typ, 200 pA max (LF398-N, p7). Hold cap: 10 nF
  polystyrene / polypropylene film (p15).

### 78L05 — 5 V Regulator
Used for: MB breakout +5V_LOC for the CD40106 (Provisional); owned x4.
- TO-92 (TI SLVS010X p3): 1 OUTPUT, 2 COMMON, 3 INPUT. The owned parts' maker is unknown; other
  makers' 78L05 pinouts are UNVERIFIED.
- Output up to 100 mA, quiescent current 3.8 mA (p1).

---

## Special Function

### PT2399 — Digital Delay IC
Used for: JF-33 spinoff only (not this build).
- Figures below are from older notes and were not re-read for this page (UNVERIFIED).
- Echo delay: 20ms–340ms (controlled by external resistor)
- Internal VCO for delay time control
- Supply: 5V (single supply)
- Mix, repeat, and output pins for flexible configuration
