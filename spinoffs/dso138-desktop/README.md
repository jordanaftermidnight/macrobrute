# DSO138 Desktop Oscilloscope (spinoff)

**Status:** speculative — desktop build, will not be a Eurorack module.

The DSO138 kit will live on the bench as a desktop scope rather than a
Eurorack module. The earlier Eurorack analog front-end design (CD4051 mux +
TL072 buffer + LM7809 +9V regulation) is preserved here for reference but
will likely be simplified for desktop use.

> This is a **MACROBRUTE spinoff**. It does not belong in the MACROBRUTE
> manual or BOM.

## What's in this folder

| Path | Contents |
|------|----------|
| `kicad/dso_input/` | Early KiCad schematic for input protection + 8-channel mux |
| `schematics/dso138_input_protection.md` | Input protection design notes |
| `schematics/dso138_analog_frontend.svg` | 8-channel mux + ±5V clamp + LM7809 power |

## What was designed

- **Input protection:** 8 jacks → 100 kΩ series + BAT54S ±5V clamp per channel
  → CD4051 8-ch mux → TL072 buffer → DSO138 BNC. ±5V rails for clamps via
  LM78L05 + 79L05.
- **Power:** LM7809 from +12V Eurorack rail produces +9V for the DSO138 kit.
- **Panel:** 10HP Eurorack with LCD cutout + 8 input jacks + 3 toggles for
  mux address.

## Why it moved off the Eurorack plan

- DSO138 LCD bezel and button panel don't fit ergonomically next to other
  modules on a 10HP face.
- A desktop scope is more useful for bench debugging than a rack-mounted one.
- The Eurorack mux is a bigger ask (8 jacks + ±5V clamps + +9V regulator)
  than warranted by how often you'd actually need to scope eight signals
  simultaneously vs. probing one at a time.

## Desktop build (rough)

- Mount the DSO138 kit in a small enclosure with a single BNC input.
- Drop the CD4051 mux entirely — use a probe.
- Power from 9V wall wart (or +12V Eurorack via LM7809 if it lives next to
  the rack).

The Eurorack-style design is preserved in this folder in case it ever gets
revived.
