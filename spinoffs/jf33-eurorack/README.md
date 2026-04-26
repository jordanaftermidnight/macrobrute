# JF-33 DIY Eurorack Delay (spinoff)

**Status:** speculative — no PCB built yet, parts on hand.

A DIY Eurorack delay module loosely inspired by the **JF-33** (Maffez/Pedrobrute
flavour). PT2399-based, 5–600 ms delay range, CV-controlled time, level
matching for Eurorack 10 Vpp.

> This is a **MACROBRUTE spinoff**. It does not belong in the MACROBRUTE
> manual or BOM. Build it as an independent project; if it grows past the
> stub stage, graduate it to its own repository via `git subtree split`.

## What's in this folder

| Path | Contents |
|------|----------|
| `kicad/jf33/` | Early KiCad schematic (CV control + level matching) |
| `schematics/jf33_cv_control.md` | Integration notes for CV-to-time control |
| `schematics/jf33_integration_schematic.svg` | Full Eurorack adapter wiring |
| `schematics/pt2399_cv_control_schematic.svg` | 2N3904 current-sink CV stage with anti-latch-up |
| `schematics/ic_pinout_pt2399.svg` | PT2399 reference pinout |
| `docs/pt2399_dso138_findings.md` | Original RE notes (PT2399 portion) |

## Design summary (from the work that was done)

- **Audio path:** Eurorack 10 Vpp → ÷6 attenuator → 10 µF coupling → JF-33 PCB
  (PT2399 + 4× NE5532) → 10 µF coupling → TL072 ×6 gain → output jack.
- **CV-to-delay-time:** 0–5 V CV → attenuator pot → 2N3904 current-sink biases
  the PT2399 timing-cap resistor (Rt). CV=0 → long delay, CV=+5 → short.
  100 Ω + 1N4148 anti-latch-up on PT2399 pin 6 is mandatory.
- **Power:** Eurorack +12V → 1N5817 + ferrite + 100 µF + 100 nF → LM78L05 → +5V
  for the PT2399 VCC.
- **Bypass:** SPDT toggle swaps OUT between dry input and wet output.
- **Panel:** 8HP Eurorack — IN, OUT, CV jacks; feedback, mix, CV-amount pots;
  bypass switch.

## Parts on hand

PT2399 ICs, NE5532 op-amps, distortion chips for the wavefolder/saturation
stage, passives. PCB not yet ordered.

## Open questions

- Final PCB layout (route the JF-33 board into a Eurorack form factor).
- Whether to integrate a wavefolder distortion stage between the dry and wet
  paths (user has the chips for it).
- Front-panel hardware sourcing.

## Rebuilding after PCB fab

When this graduates: `git subtree split --prefix=spinoffs/jf33-eurorack -b jf33`,
then push that branch to a new repo. The MACROBRUTE side keeps moving forward
without the spinoff in its way.
