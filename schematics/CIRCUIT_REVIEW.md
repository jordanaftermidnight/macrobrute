# MACROBRUTE Circuit Design Review

Systematic review of all circuit designs for correctness, safety, and reliability.

Updated against the project audit (`docs/superpowers/reviews/2026-10-16-project-audit.md`) and the
back-feed and hum design note (`docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md`, "BF").
Nothing is built; a "CORRECT" status below means the reasoning checks out on paper, not a bench
result. Sections 6 and 8 cover dropped circuits; sections 11-12 cover the JF-33 spinoff.

---

## 1. Breakout PCB — Power Supply

### Issue: Diode direction for -12V
**Status:** CORRECTED (audit B15, S74; the old text here said both "cathode toward the load" and
"anode toward load")
- One rule: on +12 V the diode anode faces TP70 and the cathode the breakout rail; on -12 V the
  **cathode faces TP71 / the -12 V source and the anode faces the breakout rail (the load)**.
- Check: in normal operation current flows from the breakout -12V_BRK rail into TP71, so the diode
  conducts anode (rail) to cathode (TP71). A positive voltage on TP71 reverse-biases it and is blocked.
- Part: owned BAT85 per rail, or a 4.7-10 Ω series resistor instead: OPEN (owner), audit conflict
  C12; an owned 1N5819 (40 V) per rail is a third option. The 1N5817 is not owned and is a 20 V
  part (`docs/DATASHEETS.md` (e)); the owned 1N5819 serves wherever a 1N5817 was drawn.

### Issue: Pico power from +5V rail
**Status:** REMOVED (audit S12, B09)
- The Pico is on the expander and takes rack +5 V through a Schottky OR diode into VSYS
  (connection map section 10). Nothing on the breakout takes 5 V from the synth; no synth 5 V or
  3V3 is tapped.
- The breakout's only 5 V is a local 78L05 from +12V_BRK for the CD40106 gate stage (Provisional,
  BF 3.4).

### Issue: Ferrite bead values
**Status:** REMOVED
- Ferrite beads are not owned and are omitted (BF 1.5). Bulk is 2-4 owned 10 µF / 63 V per rail
  (BF 1.4); where extra filtering is wanted, 10 Ω + 10 µF.

---

## 2. Output Buffers (TL074)

### Issue: Input bias path
**Status:** CORRECTED (audit N11)
- TL074 non-inverting followers need a DC bias path on the input.
- MicroBrute test points are DC-coupled; the bias resistor only defines the input when a tap lead
  is disconnected.
- **Decision:** 1MΩ to GND (replaces 10MΩ: an open input floats less and picks up less mains hum).

### Issue: TL074 output current
**Status:** CORRECT, cable figure corrected
- Output into the cable through a 1kΩ isolation resistor placed after the feedback tap (stable
  arrangement, audit R3-15 / N09). Maximum peak output ±12 V min into 10 kΩ at ±15 V supplies
  (TI SLOS080W p15).
- Cable capacitance is UNVERIFIED (the old "~20pF/m" is low; 50-100 pF/m is more usual, audit
  R3-14). Working cable length 1 m, UNVERIFIED until BF BT-6 measures the cable.

### Issue: TL074 slew rate vs audio bandwidth
**Status:** CORRECT
- TL07xC slew rate: 8 V/µs min, 20 V/µs typ (TI SLOS080W p16; the old "13 V/µs" was not from this sheet)
- For 10Vpp at 20kHz: required slew = 2π × 20000 × 5 = 0.63V/µs
- 8 V/µs >> 0.63 V/µs — no slew limiting in the audio band

### Issue: Input common-mode range
**Status:** OPEN (audit N10)
- Linear input range is about 4 V inside each rail (SLOS080W p11, p15), about ±8 V here. Saw and
  square peaks are UNVERIFIED (E-19): scope TP94 / TP93 / TP30 / TP19 and add a 2:1 divider if
  peaks exceed about ±8 V.

---

## 3. Gate Buffer (CD40106)

### Issue: Input can never read low
**Status:** CORRECTED (audit B14, Provisional per BF 3.4)
- The old stage put a 10kΩ pull-up to +5V on pin 1 with TP83 (100kΩ source) through 10kΩ. With
  TP83 low the pin sat at 5 V × 110k / 120k = 4.58 V, above VT+, so the input read high in both
  states.
- New stage: TP83 → 10kΩ → pin 1, 1nF to GND at the pin, no pull-up; pin 2 → pin 3 (second
  inverter, so A:1 follows TP83 polarity, audit S33); pin 4 → 1kΩ → DB-9 A:1; unused inputs
  5, 9, 11, 13 to GND (audit S34). VDD = +5V_LOC from a local 78L05.

### Issue: Input voltage range and threshold
**Status:** OPEN (E-09)
- CD40106 input abs max -0.5 V to VDD + 0.5 V, ±10 mA (TI SCHS097F p4).
- VT+ at VDD 5 V: 2.2 / 2.9 / 3.6 V min / typ / max (p5-p6). TP83 must exceed 3.6 V high for a
  guaranteed trigger. TP83's level is UNVERIFIED; scope it first (BF BT-5). If it is 3.3 V logic the
  stage must be redesigned: OPEN (owner), BF Q15 (no synth 3V3 tap, audit B09).
- The old "10kΩ+10kΩ divider" suggestion is withdrawn: halving the input would make triggering
  less certain, not more.

### Issue: Output level and the Pico
**Status:** CORRECTED (BF 3.5, Provisional)
- 0 / 5 V gate through 1kΩ. On the expander the gate jack is tapped before a 22kΩ / 33kΩ divider
  that feeds a fault-tolerant Pico GPIO at about 2.95 V high. No 5 V net reaches a GPIO. The
  CD4049UBE is not used on the gate path (its inputs clamp to VCC, TI SCHS046L p17).

---

## 4. Vactrol Driver

### Issue: Transistor driver works as a switch
**Status:** WRONG — withdrawn, replacement TO DESIGN (audit S37, R3-12)
- The old circuit (TL072 → 1kΩ → 2N3904 base, LED in the collector) had no collector supply as
  drawn. With LED + R from +12 V to the collector, the LED current is fixed at about
  (12 - 2 - 0.2) / 1k ≈ 9 mA once the base passes about 0.8 V: on/off, not a continuous resonance
  control. The base had no protection against negative TL072 swings.
- The earlier "Final value: 1kΩ confirmed" and "base current 4.3 mA, saturated: CORRECT" entries
  are withdrawn.
- Replacement: a linear voltage-to-current stage, TO DESIGN: an op-amp stage (+IN = CV; output →
  LED anode; LED cathode → R_sense → GND; R_sense node → -IN; I = V_CV / R_sense) or an op-amp
  driving an owned transistor (2N3904 etc., kit contents UNVERIFIED) as a current sink. R_sense depends on the owned vactrol's LED rating,
  unread (OPEN (owner), BF Q2). CV comes from the new MB panel jack, not DB-9 B pin 3 (now VCA CV).

### Issue: Vactrol response asymmetry
**Status:** BY DESIGN
- LED on-time: ~1-5ms, LDR off-time: ~5-50ms (typical vactrol figures; the owned part is
  UNVERIFIED)
- This asymmetric response is musically useful (natural attack/release)
- For faster response: use photodiode instead of LDR (but loses
  the musical character)

---

## 5. CV Input Protection (DB-9 B Filter CV and VCA CV)

### Issue: Clamp voltage, series resistor and back-feed
**Status:** CORRECTED (audit B17, S39; BF 3.3)
- The old entry (1kΩ series, BAT54S to ±12 V, "±12.3 V, 12 mA, within absolute max") is withdrawn,
  and so are the other drawn versions (±5 V clamp with a -5 V rail that does not exist; BAT54S to
  +5 V / GND "-0.3 / +5.3 V"). A +5 V / GND clamp would clip legitimate CV into the synth's ±12 V
  summing node; 1kΩ lets milliamps into the unpowered breakout rails.
- One circuit per line (B:3 VCA CV → TP10, B:5 Filter CV → TP26): 10kΩ at the expander output,
  cable, 100kΩ on the MB board, then BAT85 to +12V_BRK and from -12V_BRK (two owned BAT85 per line),
  1nF to GND, then the injection point.
- Synth off, expander on: at most (10 - 0.24) / 110k ≈ 89 µA into the unpowered rail. Bounded,
  not zero (acceptance BF BT-3).
- CV depth with the extra 100kΩ: UNVERIFIED (E-18, BT-4); fallback 47kΩ.

---

## 6. Noise Generator

> **DROPPED (archive).** The noise generator is out of the expander scope (audit section 1, S59);
> the rack's existing noise module covers it. Kept for reference only.

### Issue: 2N3904 selection
**Status:** CORRECT with note
- Not all 2N3904s avalanche at the same voltage
- Typical B-E breakdown: 6-8V
- With 2x 470kΩ from +12V: junction sees ~9.4V (divider with ~1MΩ total)
  → should exceed breakdown
- **If no noise:** Try different 2N3904 samples or increase bias voltage
  (single 220kΩ instead of 2x 470kΩ)

### Issue: Noise level
**Status:** CORRECT
- Gain of 47x (4.7MΩ/100kΩ) gives ~5-8Vpp output
- Adequate for Eurorack (~10Vpp standard, noise is typically quieter)

---

## 7. LFO

### Issue: Integrator output swing
**Status:** CORRECT
- TL072 saturates at approximately ±(Vcc-1.5V) = ±10.5V
- Schmitt trigger thresholds at ±Vsat/2 ≈ ±5.25V
- Triangle amplitude: peak-to-peak = 2 × 5.25V ≈ 10.5Vpp
- Eurorack compatible (10Vpp standard)

### Issue: Square output level
**Status:** CORRECT
- Raw square: ±10.5V (~21Vpp) — TOO HOT for Eurorack
- Voltage divider (1.8kΩ + 3.3kΩ) scales to ±3.6V (~7.2Vpp)
- **Correction:** For ±5V standard, use 2.2kΩ + 3.3kΩ:
  Vout = ±10.5 × 3.3/(2.2+3.3) = ±6.3V — still slightly hot
- Better: 3.3kΩ + 3.3kΩ: ±5.25V — closer to standard
- **Recommendation:** Use 3.3kΩ + 3.3kΩ divider, then a 1kΩ series output resistor (audit N14).

### Issue: Rate range
**Status:** CORRECTED (audit S60, S61)
- With thresholds at ±Vsat/2 the triangle swings ±5.25 V, so each half-period is R × C and
  T = 2RC (derived from the component values, not measured; E-27).
- R = 1MΩ pot + 10kΩ, C = 1µF: slow end T ≈ 2.0 s (about 0.5 Hz); pot at 0: T = 20 ms (about 50 Hz).
  The old "0.04-40 Hz" was wrong.
- The 10kΩ series resistor is mandatory: at pot = 0 it is the only thing limiting the current from
  the Schmitt output into the integrator.
- Parts: 1µF film and 1MΩ pots are not owned (BF Q6); an owned 100kΩ pot makes the range about 10×
  faster.
- Open: the connection map and BF 1.1 name a CD40106 as the LFO Schmitt, while this review and
  `expander_circuits.md` use the second TL072 section. Which one is used is OPEN (owner); the
  range above assumes the TL072 version.

---

## 8. Clock Divider (CD4024)

> **DROPPED (archive).** Clock division is done in Pico firmware (GP16-18); the CD4024 is not
> owned (audit S59, BF 1.1). Kept for reference only. The expander's Clock IN uses 100kΩ + a
> CD4049UB buffer on Pico 3V3 instead (BF 3.7).

### Issue: 5V logic with Eurorack levels
**Status:** CORRECT
- Input conditioning via 120kΩ + 100kΩ divider: scales 10V → ~4.2V
- CD40106 Schmitt trigger at +5V cleans signal
- Output 1kΩ series resistors protect against shorts

### Issue: Reset pin
**Status:** CORRECT
- Pin 2 (RST) pulled LOW via 10kΩ → counter runs freely
- Optional momentary button to +5V for manual reset
- **Add 100nF cap** across reset button for debounce

---

## 9. Sample & Hold (LF398)

### Issue: Hold capacitor selection
**Status:** CORRECTED (audit S63, B13; datasheet TI SNOSBI3C, `docs/DATASHEETS.md` (a))
- Hold capacitor: **10 nF polystyrene or polypropylene film** (0.01 µF is the characterised value,
  p7). Not owned: buy with the LF398 (BF Q1).
- Low dielectric absorption: polystyrene, polypropylene or Teflon; mica and polycarbonate are not
  nearly as good (p15). The owned 1 nF ceramic is not used here.
- **NEVER use electrolytic** (leakage)
- Leakage into the hold capacitor: 30 pA typ, 200 pA max (LF398-N, 25 °C, p7). Droop with 10 nF:
  about 3 mV/s typ, 20 mV/s max (derived as I / C, not a TI figure). The old "3 pA / 1 nF = 3 mV/s"
  used a wrong leakage figure.
- Hold step 1 mV typ, 2.5 mV max at 0.01 µF (p7); acquisition to 0.1 % about 20 µs at 0.01 µF.

### Issue: Pinout and trigger
**Status:** CORRECTED / TO DESIGN
- PDIP-8 pinout (p3): 1 V+, 2 OFFSET ADJUST, 3 INPUT, 4 V-, 5 OUTPUT, 6 Ch, 7 LOGIC REFERENCE,
  8 LOGIC. There is no "IN-" feedback pin; the three older pinouts in the repo are wrong (B13).
- Sample when LOGIC is high relative to LOGIC REFERENCE, hold when low (p14). Logic threshold
  1.4 V typ (p5); logic edges need at least 1 V/µs (p15); the logic-to-reference differential
  limit is printed on p4. Trigger conditioning from a rack gate is required (audit S65): TO DESIGN.
- Owned-parts alternative to buying the LF398: a CD4051 channel as the switch, a TL072 follower and
  the same 10 nF film cap (`expander_circuits.md` section 2b). It cannot run from ±12 V (CD4051
  V+ to V- 20 V abs max); charge injection UNVERIFIED. LF398 stays the default.

---

## 10. Slew Limiter

### Issue: TL072 rail-to-rail behavior
**Status:** NEEDS ATTENTION
- TL072 input common-mode range: -(Vcc-4V) to +(Vcc-1.5V)
- At ±12V: -8V to +10.5V → can't handle full ±10V Eurorack signals
- Datasheet: at ±15 V the common-mode range is ±11 V min, -12 to +15 V typ (TI SLOS080W p15),
  so about ±8 V min on ±12 V rails.
- **Recommendation:** For full ±10V range, consider:
  1. TL062 (lower power but same range) — NOT better; not owned
  2. Add 10kΩ input attenuator (halve signal to ±5V) — simple fix
  3. Use OPA2134 (rail-to-rail output, wider input) — not owned
- **Simplest fix:** Accept ±8V range (adequate for most CV signals)
- Parts: 1N4148 steering diodes are owned (owner, kit contents UNVERIFIED); 1MΩ pots are not (BF Q6).

---

## 11. JF-33 Anti-Latch-Up

### Issue: Timing
**Status:** CORRECT
- RC = 100kΩ × 1µF = 100ms
- BC337 reaches saturation at ~3-5τ = 300-500ms
- PT2399 datasheet requires >100ms startup delay
- 300ms provides adequate margin

### Issue: BC337 saturation voltage
**Status:** CORRECT
- BC337 Vce(sat) ≈ 0.3V at 100mA
- At ~5-10mA collector current (PT2399 pin 6): Vce(sat) < 0.1V
- Negligible effect on delay time control accuracy

---

## 12. JF-33 Delay Time CV

### Issue: Emitter resistor value
**Status:** CORRECTED
- Originally showed 220Ω → max 22.7mA (WOULD DESTROY PT2399)
- Corrected to 1kΩ → max 5mA (within PT2399 safe operating range)
- PT2399 datasheet: pin 6 current range 50µA to 5.4mA
- At 1kΩ emitter R: 0-5V CV → 0-5mA → full delay range covered

### Issue: 1N4148 protection
**Status:** CORRECT
- Diode prevents reverse current if CV goes negative
- Cathode to pin 6, anode to ground
- Also protects 2N3904 collector from reverse bias

---

## 13. Power Distribution

### Issue: Reverse polarity protection
**Status:** CORRECTED
- Two separate supplies (split power): the breakout from TP70 / TP71 / TP72, the expander from the
  rack 16-pin header. No supply crosses the DB-9 cable.
- Series Schottky per rail on the expander header (justified against reverse insertion, audit N04);
  on the breakout a BAT85, an owned 1N5819 or a 4.7-10 Ω resistor per rail (OPEN (owner), C12). 1N5817 is not owned
  (20 V part); owned BAT85 is used (BF 1.2). -12 V diode: cathode to the source, anode to the rail.
- Ferrite beads not owned (omitted); bulk 2-4 owned 10µF / 63 V per rail instead of 47µF / 100µF.

### Issue: Power budget
**Status:** NOT VERIFIED (audit S18, H5). The old table (TL074 × 3, CD4024, LF398 ~5 mA, 6 LEDs,
78L05, "Total +12V ~102mA") matched neither board and is withdrawn.
- Datasheet figure: TL07x quiescent current 1.4 mA typ, 2.5 mA max per amplifier (TI SLOS080W
  p16). LF398 supply current is not quoted in `docs/DATASHEETS.md` (E-06).
- Reviewer estimates, UNVERIFIED until recomputed: breakout about 35 / 60 mA typ / worst on +12 V;
  expander about 25-55 mA on +12 V and 75-150 mA on +5 V (r2).
- Rack: CP1A gives +12 V 1 A, -12 V 1 A, +5 V 0.5 A shared with every module (CP1A QSG p20).
  Synth rail capacity for the breakout load: UNVERIFIED (E-04).

---

## Summary of Corrections Needed

| Circuit | Issue | Fix |
|---------|-------|-----|
| Breakout -12V diode | Orientation stated two ways | Cathode to TP71, anode to rail (B15) |
| Gate buffer | Pull-up held input high | No pull-up, 2 inverters, 1kΩ out, 22k/33k on expander (B14) |
| CV input protection | Five conflicting circuits | 100kΩ + 2× BAT85 to ±12V_BRK + 1nF (B17) |
| Vactrol driver | Transistor switch, not linear | TL072 V-to-I stage, TO DESIGN (S37, Q2) |
| Output buffers | 10MΩ bias, 1kΩ position | 1MΩ bias; 1kΩ after the feedback tap |
| LFO square output | Divider ratio too hot | Change 1.8kΩ to 3.3kΩ |
| LFO range | 0.04-40 Hz wrong | About 0.5-50 Hz; 10kΩ series mandatory (S60, S61) |
| S&H | Pinout, hold cap, droop | Datasheet pinout; 10 nF film; trigger TO DESIGN (B13, S63, S65) |
| Delay time CV emitter R | Was 220Ω | Already corrected to 1kΩ |
| Slew limiter | TL072 input range | Accept ±8V or add attenuator |
| Power budget | Old, not reproducible | NOT VERIFIED; recompute (S18) |

Several items above stay OPEN or TO DESIGN; nothing here is bench-verified.


