# MACROBRUTE Circuit Design Review

Systematic review of all circuit designs for correctness, safety, and reliability.

---

## 1. Breakout PCB — Power Supply

### Issue: Diode direction for -12V
**Status:** CORRECT
- 1N5817 cathode toward the load (breakout board).
- For -12V, the diode is oriented with anode toward load (reverse polarity protection).
- Polarity verified: diode blocks positive voltage on -12V rail.

### Issue: Pico power from +5V rail
**Status:** CORRECT with caveat
- 1N5817 drop: ~0.3V → Pico VSYS sees ~4.7V
- Pico VSYS range: 1.8-5.5V → 4.7V is fine
- **Caveat:** If MicroBrute +5V rail is loaded, voltage could sag.
  Monitor with multimeter before committing. If <4.2V, power Pico from
  +12V via 7805 instead.

### Issue: Ferrite bead values
**Status:** ACCEPTABLE
- 100Ω ferrite beads at ~100MHz provide adequate RF filtering
- At DC/audio frequencies, resistance is negligible (<1Ω)

---

## 2. Output Buffers (TL074)

### Issue: Input bias path
**Status:** NEEDS CORRECTION
- TL074 non-inverting followers need a DC bias path on the input.
- 10MΩ to GND shown in schematic — this is correct for AC-coupled signals.
- But MicroBrute test points are DC-coupled (waveforms centered on 0V or
  with DC offset). The 10MΩ could be omitted for DC-coupled signals.
- **Decision:** Keep 10MΩ — it doesn't affect DC signals meaningfully
  (10MΩ >> 1kΩ series R) and provides a defined state if input disconnected.

### Issue: TL074 output current
**Status:** CORRECT
- TL074 max output: ±10mA (short-circuit protected to ±25mA)
- With 1kΩ output resistor driving a DB-9 cable (~20pF/m capacitance),
  load current is negligible at audio frequencies.
- Adequate for 1-3m cable lengths.

### Issue: TL074 slew rate vs audio bandwidth
**Status:** CORRECT
- TL074 slew rate: 13V/µs
- For 10Vpp at 20kHz: required slew = 2π × 20000 × 5 = 0.63V/µs
- 13V/µs >> 0.63V/µs — no slew limiting up to ~400kHz

---

## 3. Gate Buffer (CD40106)

### Issue: Input voltage range
**Status:** NEEDS ATTENTION
- CD40106 powered at +5V, max input Vin = VDD+0.5 = 5.5V
- TP83 gate is generated from keyboard/CPU circuit, typically 0-3.3V or 0-5V
- **Verify on actual hardware** that TP83 doesn't exceed 5V
- If it does, add a voltage divider: 10kΩ+10kΩ (halves signal to 0-2.5V)

### Issue: Output level
**Status:** CORRECT
- CD40106 at +5V outputs 0/5V gates
- 5V gates are Eurorack-compatible (trigger threshold typically ~2.5V)

---

## 4. Vactrol Driver

### Issue: LED current limit
**Status:** CORRECTED in schematic
- Original design showed 100Ω → ~98mA (WAY too high for LED)
- Corrected to 1kΩ → ~10mA
- Most 5mm LEDs rated 20mA max continuous
- 10mA gives good vactrol response without LED degradation
- **Final value: 1kΩ confirmed.**

### Issue: TL072 driving 2N3904 base
**Status:** CORRECT
- TL072 output → 1kΩ → 2N3904 base
- At 5V CV: base current = (5-0.7)/1k = 4.3mA → 2N3904 saturated
- Collector current ~10mA through LED+1kΩ
- TL072 output capability: ±10mA — adequate

### Issue: Vactrol response asymmetry
**Status:** BY DESIGN
- LED on-time: ~1-5ms, LDR off-time: ~5-50ms
- This asymmetric response is musically useful (natural attack/release)
- For faster response: use photodiode instead of LDR (but loses
  the musical character)

---

## 5. CV Input Protection (BAT54S clamp)

### Issue: Clamp voltage vs rail voltage
**Status:** CORRECT
- BAT54S forward drop: ~0.3V
- Clamped to ±12V rails → max signal = ±12.3V
- MicroBrute op-amps run on ±12V → ±12.3V is within absolute max
- 1kΩ series R limits fault current to 12mA at worst case

---

## 6. Noise Generator

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
- **Recommendation:** Use 3.3kΩ + 3.3kΩ divider.

---

## 8. Clock Divider (CD4024)

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
**Status:** CRITICAL
- 1nF polystyrene specified — CORRECT
- **NEVER use ceramic** (piezoelectric effect causes microphonics)
- **NEVER use electrolytic** (massive leakage → instant droop)
- Polystyrene or polypropylene film only
- Expected droop: ~3mV/s with LF398 (3pA bias current / 1nF)

---

## 10. Slew Limiter

### Issue: TL072 rail-to-rail behavior
**Status:** NEEDS ATTENTION
- TL072 input common-mode range: -(Vcc-4V) to +(Vcc-1.5V)
- At ±12V: -8V to +10.5V → can't handle full ±10V Eurorack signals
- **Recommendation:** For full ±10V range, consider:
  1. TL062 (lower power but same range) — NOT better
  2. Add 10kΩ input attenuator (halve signal to ±5V) — simple fix
  3. Use OPA2134 (rail-to-rail output, wider input) — drop-in compatible
- **Simplest fix:** Accept ±8V range (adequate for most CV signals)

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
**Status:** CORRECT
- 1N5817 Schottky on each rail (0.3V drop, 1A rated)
- Ferrite beads for HF noise rejection
- 47µF + 100nF per rail (bulk + local decoupling)

### Issue: Power budget
**Status:** VERIFIED
- TL074 × 3: ~8mA each = 24mA
- TL072 × 2: ~3.6mA each = 7.2mA
- CD4024: ~0.1mA
- CD40106: ~0.1mA
- LF398: ~5mA
- LEDs × 6: ~10mA each = 60mA
- 78L05: quiescent ~5mA
- **Total +12V: ~102mA**
- **Total -12V: ~35mA** (op-amps only)
- Eurorack bus typically provides 500mA+ per rail → well within budget

---

## Summary of Corrections Needed

| Circuit | Issue | Fix |
|---------|-------|-----|
| LFO square output | Divider ratio too hot | Change 1.8kΩ to 3.3kΩ |
| Vactrol LED R | Was 100Ω | Already corrected to 1kΩ |
| Delay time CV emitter R | Was 220Ω | Already corrected to 1kΩ |
| Clock divider reset | No debounce | Add 100nF across button |
| Slew limiter | TL072 input range | Accept ±8V or add attenuator |

All critical safety issues (anti-latch-up, current limiting, protection
diodes, power isolation) are correctly addressed.


