# What You're Building

Two mockups of the finished hardware, so you have a target image in your
head before you read another 1900 KB of detail. The 17 HP expander
(panel) and the modified MicroBrute (additions in their final positions)
— rendered as they'd look assembled.

These are *visualizations*, not drilling templates. For 1:1 mm drilling
guides, see `panel/expander_17hp.svg` and `panel/microbrute_panel_template.svg`.

---

## The 17 HP expander module

The expander is a self-contained Eurorack module that pairs to the
modified MicroBrute over a 2× DB-9 cable. It hosts the main 0.96″ OLED,
the rotary encoder, the tap button, the RGB status LED, all clock I/O,
the analogue slew limiter, and the four firmware-assignable aux outputs.

Power comes from the Eurorack bus (CP1A or any standard ±12 V supply) —
the synth's stock power is untouched.

## The modified MicroBrute panel

The synth keeps every stock control. The mod adds: a 0.91″ strip OLED in
place of the existing brand silkscreen, a row of new 3.5 mm jacks for the
panel inserts and the Phase-2 mod additions, five SPDT toggles down the
right side, and six brass touch bolts along the front edge for circuit
bending. The seventh "GND" bolt provides the always-touched return path.

If you unplug the breakout, every stock control still works exactly as
Arturia shipped — the mods are *in addition to*, not *instead of*.
