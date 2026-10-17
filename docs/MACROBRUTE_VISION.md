# What You're Building

Two mockups of the finished hardware, so you have a target image in your
head before you read another 1900 KB of detail. The expander (17 or about 20 HP, open)
(panel) and the modified MicroBrute (additions in their final positions)
— rendered as they'd look assembled.

These are *visualizations*, not drilling templates. For 1:1 mm drilling
guides, see `panel/expander_17hp.svg` and `panel/microbrute_panel_template.svg`.

---

## The expander module (17 or about 20 HP, open)

The expander is a self-contained Eurorack module that pairs to the
modified MicroBrute over a 2× DB-9 cable. It hosts the main 1.3″ 7-pin SPI OLED (chip UNVERIFIED),
the rotary encoder, the tap button, the RGB status LED, all clock I/O,
the analogue slew limiter, a standalone LFO, a standalone Sample & Hold,
the firmware clock dividers and the four firmware-assignable aux outputs.
Its width is open (17 HP or about 20 HP) until the blank is measured.

Power comes from the Eurorack bus (the CP1A; it needs ±12 V and +5 V from the rack, since the Pico runs from bus +5 V) —
the synth's stock power is untouched, and no supply rail crosses the
DB-9 cable; only ground is shared.

## The modified MicroBrute panel

The synth keeps every stock control. The mod adds: two DB-9 connectors on
the rear panel, left of the Pitch/Gate section (dimensions still to be
measured), a row of new 3.5 mm jacks for the panel inserts and the Phase-2
mod additions, five SPDT toggles down the right side, and six brass touch
bolts along the front edge for circuit bending. The seventh "GND" bolt
provides the always-touched return path. The 0.91″ strip OLED idea is
dropped.

If you unplug the breakout, every stock control still works exactly as
Arturia shipped — the mods are *in addition to*, not *instead of*.
