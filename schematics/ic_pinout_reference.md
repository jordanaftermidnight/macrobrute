# MACROBRUTE — IC Pinout Reference

Pinout diagrams for all ICs used in the MACROBRUTE project.
Each diagram shows the DIP pinout with function labels.

---

## Op-Amps

### TL074 — Quad JFET-Input Op-Amp
Used for: 8-channel audio buffer (2× TL074), CV conditioning
- 4 independent op-amps per chip
- Supply: ±12V (VCC+ pin 4, VCC- pin 11)
- Unity-gain bandwidth: 3 MHz
- Slew rate: 13 V/μs

### TL072 — Dual JFET-Input Op-Amp
Used for: Envelope/LFO buffer, expander utility circuits
- 2 independent op-amps per chip
- Same supply and specs as TL074 (dual version)

### LM358 — Dual Op-Amp (Single Supply)
Used for: LED driver circuits, low-side current sensing
- Single supply: 3V–32V
- Output swings to ground (no negative rail needed)
- Lower bandwidth than TL07x (1 MHz)

---

## Logic ICs

### CD40106 — Hex Schmitt Trigger Inverter
Used for: Gate buffer (TP83 → 5V gate out), clock conditioning, touch sensor cleanup
- 6 independent Schmitt triggers
- Supply: 3V–15V
- Hysteresis ensures clean switching on slow edges

### CD4051 — 8-Channel Analog Multiplexer/Demultiplexer
Used for: CV routing, signal switching
- 8 channels (Y0–Y7) → common I/O (Z)
- 3-bit address select (A, B, C)
- Supply: VDD (+5V to +15V), VEE (negative rail for bipolar signals), VSS (GND)
- INH pin disables all channels when HIGH

### CD4024 — 7-Stage Ripple Counter
Used for: Clock divider (/2, /4, /8, /16, /32, /64, /128)
- 7 binary counter stages
- Supply: 3V–15V
- Reset pin (R) clears all outputs
- Clock on falling edge

### CD4066 — Quad Bilateral Switch
Used for: Analog signal switching, sample & hold
- 4 independent SPST switches
- Supply: 3V–15V
- Control pins: HIGH = switch ON, LOW = switch OFF
- ON resistance: ~80Ω at 15V supply

---

## Special Function

### PT2399 — Digital Delay IC
Used for: JF-33 CV-controlled delay module
- Echo delay: 20ms–340ms (controlled by external resistor)
- Internal VCO for delay time control
- Supply: 5V (single supply)
- Mix, repeat, and output pins for flexible configuration
