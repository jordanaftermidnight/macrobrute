# MACROBRUTE — Phase 0 Starter BOM

The minimum kit to validate the Pico-side hardware on a breadboard,
**without touching the MicroBrute itself**. Wire it per
`schematics/phase0_breadboard.svg` and run `firmware/pico/test_hw.py` —
if every peripheral passes, you're ready for Phase 1.

If anything fails on the bench, fix it here. It will be 10× harder once
this is mounted inside the synth.

**Subtotal: ~$30 USD** (varies by source / shipping).

---

## What you actually need

| Qty | Part | Notes | ≈ USD |
|---|---|---|---|
| 1 | Raspberry Pi Pico **WH** | "WH" = wireless + headers pre-soldered. Plain "W" works too if you can solder headers. | $7 |
| 1 | 0.96″ SSD1306 OLED, I²C, 4-pin | Default address `0x3C`. The "main" display. | $4 |
| 1 | 0.91″ SSD1306 OLED 128×32, I²C, 4-pin | The "strip" display — set its address to `0x3D` via the on-module ADDR jumper *before* powering up alongside the main OLED. | $4 |
| 1 | KY-040 rotary encoder module | 5 pins (CLK, DT, SW, +, GND). On-board 10 kΩ pull-ups. | $2 |
| 1 | Tactile push button, 6 mm | Single-pole momentary. | $0.10 |
| 1 | Common-cathode RGB LED, 5 mm | Used as the status LED. | $0.50 |
| 3 | 220 Ω resistor, ¼ W | RGB LED current limiters (one per colour). | — |
| 2 | 1 kΩ resistor, ¼ W | Clock IN/OUT inline protection. | — |
| 2 | 3.5 mm mono panel jacks (or PCB-mount equivalent) | Clock IN + Clock OUT. Bench-only — no need to splash on Lumberg yet. | $1 |
| 1 | Half-size breadboard (400+ tie points) | Big enough to span the Pico across the centre channel. | $4 |
| ~30 | Solid-core jumper wires, 22 AWG | Mix of M-M and M-F. Pre-cut sets are fine. | $4 |
| 1 | USB cable, micro-B → USB-A or USB-C | Whatever your computer accepts. For Pico flash + power. | $2 |

**Optional but very helpful:**

| Qty | Part | Why |
|---|---|---|
| 1 | Multimeter (continuity + DC voltage) | You almost certainly already own one. Critical for verifying jumper paths before powering up. |
| 1 | USB-serial adapter (CP2102 / FT232) | Lets you watch Pico `print()` output in a terminal. Not required since the Pico's USB stays available, but nice for parallel debugging once the synth is wired. |
| 1 | 1× 4-pin pin header | If you want to terminate the rear I²C-Daisy expansion JST early. Skip for Phase 0. |

---

## What you do **not** need yet

Hold off on these until Phase 1+:

- Stripboard, IC sockets, TL072 / TL074 / CD40106 / CD4051, BAT54S, vactrol,
  10 µF / 100 nF caps, 1N5817 power diodes — that's the **Breakout Board**
  BOM in the full doc.
- Eurorack panel, M3 hardware, brass touch bolts, panel-mount jacks —
  that's **Panel Modifications** (Phase 3).
- 17 HP Eurorack panel, expander parts, ±12 V Eurorack PSU — that's
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
- [ ] Both OLEDs power up and draw their splash frame from
      `firmware/pico/test_hw.py`. If only one shows up, **check the
      strip-OLED ADDR jumper** — both ship at `0x3C` by default and one
      must be moved to `0x3D`.
- [ ] Encoder rotation increments / decrements a counter on the OLED.
- [ ] Encoder push button toggles the on-screen indicator.
- [ ] Tap button (GP12) registers as a separate input.
- [ ] RGB LED cycles red / green / blue when each colour is selected.
- [ ] Looping `Clk OUT` (GP22) → `Clk IN` (GP21) with a single 1 kΩ in
      series produces clean tick events on the OLED at the firmware's
      tap-tempo rate.

If all six pass, **stop here, commit your wiring photo to your build log,
and proceed to Phase 1**.

---

## Common Phase 0 gotchas

- **Both OLEDs on `0x3C`** — only one will be addressable; the other
  appears dead. Set the strip OLED to `0x3D` via its ADDR jumper before
  applying power.
- **Encoder jitter** — the KY-040 module already has 10 kΩ pulls and
  on-board caps but firmware *also* enables `Pin.PULL_UP` on GP13/14/15.
  That's intentional and fine. If you still see 2 ticks per detent, add
  the optional 100 nF + 10 kΩ RC filter shown in `pico_pinout.md`.
- **Common-anode RGB LED instead of common-cathode** — they look
  identical. With common-anode, "off" is +3.3 V on the GPIO and the LED
  is *always lit* until firmware drives the pin high. Verify the part
  with a multimeter (long lead = K = cathode for common-cathode).
- **Centre-channel jumpers across the Pico body** — the Pico straddles
  the breadboard centre channel. Jumpers from the encoder / tap to the
  Pico must route around the Pico, not over it; see the breadboard
  layout SVG for safe drop columns.
