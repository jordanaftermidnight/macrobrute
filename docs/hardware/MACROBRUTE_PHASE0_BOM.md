# MACROBRUTE — Phase 0 Starter BOM

The minimum kit to validate the Pico-side hardware on a breadboard,
**without modifying the MicroBrute** (the gate checks below only probe it, with
no soldering). Wire it per
`schematics/phase0_breadboard.svg` and run `firmware/pico/test_hw.py` —
if every peripheral passes, you're ready for Phase 1.

If anything fails on the bench, fix it here. It will be 10× harder once
this is mounted inside the synth.

**Subtotal: ~$30 USD** (varies by source / shipping), before the Have column: most of this kit is already owned (Pico, OLED, KY-040, resistor kit, jacks).

---

## What you actually need

| Qty | Part | Have? | Notes | ≈ USD |
|---|---|---|---|---|
| 1 | Raspberry Pi Pico (Pico / Pico H / Pico WH) | Have; **variant owner to confirm** (BF Q21) | "WH" = wireless + headers pre-soldered; nothing here uses wireless. A Pico without soldered headers needs headers soldered for the breadboard. | $7 |
| 1 | 1.3″ OLED, SPI, 7-pin (chip SSD1306 or SH1106 and pin order UNVERIFIED: read the module) | Have (owner ruling, 2026-10-17, BF Q22) | The "main" display, SPI0 write-only: SCK GP2 (D0), MOSI GP3 (D1), DC GP4, RES GP5, CS GP11, power from the Pico 3V3. Needs an SPI driver (firmware follow-up); for SH1106 also `OLED_CHIP="SH1106"`, `OLED_COL_OFFSET=2`. The 4-pin I²C 1.3″ module is in a TD-3 (not available); the 0.96″ SSD1306 may not have arrived and is an alternative only (I²C would need re-pinning). | $4 |
| 1 | KY-040 rotary encoder module | Have | 5 pins (CLK, DT, SW, +, GND). On-board 10 kΩ pull-ups. | $2 |
| 1 | Tactile push button, 6 mm | Missing (BF Q12) | Single-pole momentary. | $0.10 |
| 1 | Common-cathode RGB LED, 5 mm | Missing (BF Q12) | Used as the status LED. | $0.50 |
| 3 | 220 Ω resistor, ¼ W | Have (kit; values to confirm, BF Q5) | RGB LED current limiters (one per colour). | — |
| 2 | 1 kΩ resistor, ¼ W | Have (kit; values to confirm) | Clock IN/OUT series resistors for the loop-back test. Not input protection: CLOCK IN is loop-back only, no external signals (no CD4049UB on the bench). | — |
| 2 | 3.5 mm mono panel jacks (or PCB-mount equivalent) | Have (25 owned, type unknown, BF Q8) | Clock IN + Clock OUT. Bench-only. | $1 |
| 1 | Half-size breadboard (400+ tie points) | Not on the owned list | Big enough to span the Pico across the centre channel. | $4 |
| ~30 | Solid-core jumper wires, 22 AWG | Not on the owned list | Mix of M-M and M-F. Pre-cut sets are fine. | $4 |
| 1 | USB cable, micro-B → USB-A or USB-C | Not on the owned list | Whatever your computer accepts. For Pico flash + power. | $2 |

The 0.91″ strip OLED is **dropped** and is no longer part of the kit (it stays a spare).

**Optional but very helpful:**

| Qty | Part | Why |
|---|---|---|
| 1 | Multimeter (continuity + DC voltage) | You almost certainly already own one. Critical for verifying jumper paths before powering up. |
| 1 | USB-serial adapter (CP2102 / FT232) | Lets you watch Pico `print()` output in a terminal. Not required since the Pico's USB stays available, but nice for parallel debugging once the synth is wired. |
| 1 | Caliper (0.1 mm) | For the D-sub geometry check below and the later rear-panel measurements. |
| 1 | Oscilloscope probe / scope | For the TP83 level and the optional 31250-baud check on LPC pin 85. A meter alone gives the DC level of TP83 only. |

---

## What you do **not** need yet

Hold off on these until Phase 1+:

- Stripboard, IC sockets, TL072 / TL074 / CD40106, BAT85 clamps, vactrol,
  10 µF / 100 nF caps, rail-protection diodes — that's the **Breakout Board**
  BOM in the full doc.
- Eurorack panel, M3 hardware, brass touch bolts, panel-mount jacks —
  that's **Panel Modifications** (Phase 3).
- Eurorack panel (17 HP or about 20 HP, width open), expander parts, ±12 V Eurorack PSU — that's
  **Expander Build** (Phase 4).
- 5-pin DIN MIDI sockets, 6N138 optocouplers — only matters when you
  reach the MIDI Bridge phase.

If you order the full BOM in one go, you'll have a pile of parts you
won't touch for weeks. The Phase 0 starter kit is deliberately a
weekend's worth of parts.

---

## Bench-validation checklist

After wiring the breadboard per `schematics/phase0_breadboard.svg`:

- [ ] Pico powered from USB; on-board green LED is solid.
- [ ] The main OLED powers up and draws its splash frame (needs the SPI
      driver, a firmware follow-up; `test_hw.py` still checks the old I²C
      module). If it stays blank, check the module pin order (UNVERIFIED),
      D0/D1 (SCK/MOSI), DC, RES and CS, then VCC/GND (BF Q22).
- [ ] Encoder rotation increments / decrements a counter on the OLED.
- [ ] Encoder push button toggles the on-screen indicator.
- [ ] Tap button (GP12) registers as a separate input.
- [ ] RGB LED cycles red / green / blue when each colour is selected.
- [ ] Looping `Clk OUT` (GP22) → `Clk IN` (GP21) with a single 1 kΩ in
      series produces clean tick events on the OLED at the firmware's
      tap-tempo rate.

If all six pass, the breadboard part of Phase 0 is done. Then do the MicroBrute
gate checks below before Phase 1 and record each result: they decide what the
later phases may assume.

---

## Common Phase 0 gotchas

- **Encoder jitter** — the KY-040 module already has 10 kΩ pulls and
  on-board caps but firmware *also* enables `Pin.PULL_UP` on GP13/14/15.
  That's intentional and fine. If you still see 2 ticks per detent, add
  the optional 100 nF + 10 kΩ RC filter shown in `pico_pinout.md`.
- **No second OLED and no I²C** — the strip OLED is dropped and the main OLED is SPI, so there is no address and no I²C scan to run.
- **Common-anode RGB LED instead of common-cathode** — they look
  identical. With common-anode, "off" is +3.3 V on the GPIO and the LED
  is *always lit* until firmware drives the pin high. Verify the part
  with a multimeter (long lead = K = cathode for common-cathode).
- **Centre-channel jumpers across the Pico body** — the Pico straddles
  the breadboard centre channel. Jumpers from the encoder / tap to the
  Pico must route around the Pico, not over it; see the breadboard
  layout SVG for safe drop columns.

---

## Phase 0 gate checks on the MicroBrute

These are probe-only checks on the open synth (no soldering). Source: audit
`docs/superpowers/reviews/2026-10-16-project-audit.md` (decision 7, E-01 to E-05, E-09) and the
back-feed and hum design note `docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md` ("BF").
Datasheet pin numbers: `docs/DATASHEETS.md`. Record every result (a number or "not found") in the
build log. Anything not measured stays UNVERIFIED in the docs.

### G1. LPC bridge UART continuity (gate before any Phase 6 bridge work)

Rear board CU17002 "Rear Board B3", **power off**, multimeter in continuity mode. Pin numbers are
LPC2361 LQFP-100 (data sheet Rev. 03, Table 3). **Never probe pins 96 and 97**: they are VDD(3V3)
and VSS, not UART pins (the older docs were wrong).

- [ ] 1. Locate the LPC2361 LQFP-100 (right of the P1_JTAG header) and count from the pin-1 dot.
- [ ] 2. Probe pin 62 (P0.15 / TXD1) and pin 63 (P0.16 / RXD1) against nearby pads and vias. Record whether each goes to a pad that can take a wire, and whether it also goes to anything else (SPI to a shift register or DAC, an LED driver, a connector). The stock firmware uses SSP0/SPI, which shares these pins.
- [ ] 3. Same for pin 98 (P0.2 / TXD0) and pin 99 (P0.3 / RXD0), and check the claim of "separate pads near the QFP" in `MACROBRUTE_TEST_POINTS_VERIFIED.md` (UNVERIFIED, audit S09, E-03). These are the ISP UART.
- [ ] 4. Trace the 6N138 output (pin 6, 4.7 kΩ pull-up) to the LPC. Expected: pin 85 (P4.29, RXD3), the stock MIDI UART (UART3 per the disassembly; audit E-02).
- [ ] 5. Optional, synth powered and a MIDI source connected: scope pin 85 for 31250 baud; check pins 62/63 and 98/99 idle at 3.3 V.
- [ ] 6. Record the result. **Only after it passes may a doc say UART1 (or UART0) is confirmed.** Until then every doc keeps "UART1, P0.15/P0.16, pins 62/63, UNVERIFIED".

### G2. TP83 logic level

- [ ] Measure the high and the low level of TP83 (gate from the microcontroller, 100 kΩ source impedance, buffer needed): synth on, key pressed and released; scope with a 10× probe preferred (audit E-09, BF BT-5 first part).
- [ ] Record. If the high level is below 3.6 V, a CD40106 powered from 5 V is **not guaranteed** to trigger (VT+ at VDD 5 V is 2.2 / 2.9 / 3.6 V min / typ / max, TI SCHS097F p5-p6) and the gate stage must be redesigned: owner question BF Q15. Do not tap the synth's +3V3ARM.

### G3. Synth rail drop and current margin (TP70 / TP71)

- [ ] Read the MicroBrute wall-adapter label (voltage, current, class II symbol; audit E-04, N06) and write it down.
- [ ] With the synth on and idle, meter TP70 (+12 V) and TP71 (-12 V) against TP72 (GND). Record both. This is the baseline for the Phase 2 loaded check.
- [ ] The breakout load estimate is about 35 mA typical / 60 mA worst case on +12 V and 15 / 30 mA on -12 V (audit E-04, UNVERIFIED). The Phase 2 acceptance is rails within about 100 mV of the unloaded baseline with no extra ripple on TP70/TP71, measured with the breakout connected, before the DB-9 is wired.
- [ ] Do not load TP141 (the 5 V precision reference). TP56 "+5VNUM" and P4 pin 5 (+3V3ARM) are not supply taps (audit B09, E-05).

### G4. D-sub neighbour geometry (BF BT-7)

- [ ] Caliper the owner's DB-9 insert (or obtain the exact connector's drawing): pin numbering as moulded on the insert, row offset, flange width and height, hole spacing (the generic drawing says 24.99 mm, Spectrum Control p1), D-body width and height, body depth, solder-cup length, gender.
- [ ] Confirm or correct the neighbour table in BF 2.1 (top row pins 1-5, bottom row pins 6-9, offset half a pitch: pin 6 between 1 and 2, 7 between 2 and 3, 8 between 3 and 4, 9 between 4 and 5). The DB-9 B map (each CV pin with only ground neighbours) depends on it.
- [ ] Count the owned DB-9 connectors and note gender (BF Q9; 4 panel connectors are needed in total).

### G5. Optional rack checks

- [ ] CP1A bus slot: meter pins 11-12 for +5 V (BF BT-12, audit E-14). Note: the +5 V pins are 11-12, not 13-14 (pins 13-16 are not used on the CP1A).

### Optional alternative: PC817 isolated UART (BF 3.9)

Not part of the decided design and not required in Phase 0. If BT-2 (UART back-feed) fails or the bridge can live at low baud, the owned PC817 (10-20, owner to confirm; photo label x20) can isolate each UART direction. It does **not** work at 115200 or 38400; 9600 is marginal and 4800 the realistic rate, all UNVERIFIED until BT-13. It also needs an MB-side collector supply (BF Q20). Read the rank mark on the owned part if you try it.

### Bench tests BT-1 to BT-13 (names only)

Definitions, pass criteria and what each settles are in BF section 6.2. They run when the matching hardware exists.

| ID | Name |
|---|---|
| BT-1 | UART edge rate at each receiver pin, real cable, 1k + 1k |
| BT-2 | UART back-feed (each side off in turn, rails and pin current) |
| BT-3 | CV back-feed (both CV outputs at maximum, synth off) |
| BT-4 | CV depth with and without the 100k |
| BT-5 | Gate: TP83 levels, CD40106 output, Pico GPIO node, S2 pin current |
| BT-6 | Cable capacitance (LCR meter) |
| BT-7 | DB-9 insert geometry (caliper) — also G4 above |
| BT-8 | Shell and shield continuity (MB shell to TP72; expander shell to panel and rack 0 V) |
| BT-9 | Hum and gate-to-Pitch crosstalk |
| BT-10 | CD4049UB input clamp behaviour |
| BT-11 | Clock IN overvoltage through the 100k and 4049 |
| BT-12 | CP1A bus slot +5 V on pins 11-12 — also G5 above |
| BT-13 | PC817 UART baud and CTR rank (only if the alternative is considered) |
