# MACROBRUTE — Reader Roadmap

A 1900 KB manual is a lot of doc. Here's how to triage it depending on
where you're standing right now.

---

## What this project is

The **MACROBRUTE** turns a stock Arturia MicroBrute into a deeply modified,
expander-paired hybrid synth:

- **Inside the MicroBrute:** a small buffer-only breakout board that taps the
  existing test points and adds jacks and touch bends. It is powered only from
  the synth (TP70/TP71/TP72). The Pico is not inside the MicroBrute.
  Optionally, a custom firmware on the stock LPC2361 to add a sequencer +
  arpeggiator over the existing engine.
- **Outside the MicroBrute:** a Eurorack expander module (17 HP or about 20 HP,
  width open) that hosts the Raspberry Pi Pico, display and controls, and pairs
  to the synth over 2× DB-9 on the MicroBrute rear panel (left of Pitch/Gate),
  exposing waveform outs, CV ins and utilities: slew limiter, LFO, S&H,
  firmware clock dividers and aux outs. Noise, mult and attenuverter stay out.

The endgame is **two boxes that talk to each other** — the synth keeps
working stock if the expander is unplugged.

---

## Reading paths

### → If you have never seen this project (10 min)

Read in this order — these are the only docs you need to get the shape:

1. **This page** — you're here.
2. **`MACROBRUTE_INDEX.md`** *(Section 1)* — the master index, project
   status, and "key decisions" table.
3. **`MACROBRUTE_MOD_SELECTION.md`** *(Section 2)* — the 14 curated mods +
   6 touch bolts, with rationale.
4. **`MACROBRUTE_BUILD_PLAN.md`** *(Section 2)* — 7-phase roadmap from
   bench validation to firmware load. Skim the phase headers, ignore the
   detail.
5. Skim a couple of schematic SVGs to get a feel for the visual style:
   *Interconnect Wiring* (Section 4) and *System Architecture* (Section 3).

That's it for the orientation pass. Don't try to read top-to-bottom.

### → If your MicroBrute is on the bench and you want to start (today)

Skip the planning docs and do **Phase 0 bench validation** first. It's
non-destructive, takes a weekend, and uses ~$30 of parts.

1. **Section 2 → Phase 0 starter BOM** — the minimal kit (Pico, one
   OLED, KY-040 encoder, breadboard, jumpers, RGB LED, a handful of
   resistors and 3.5 mm jacks). Check the Have column first; order only
   what is missing.
2. **Section 1 → "Phase 0 Bench Validation" section of the build plan** —
   the wiring + flash + test procedure.
3. **Section 4 → Phase 0 Breadboard Layout SVG** — what the wired-up
   breadboard should look like, with every jumper colour-coded.
4. **`firmware/pico/`** — copy `main.py`, `config.py`, and the peripheral
   modules onto the Pico. Then run `test_hw.py` for per-peripheral
   diagnostics (OLED draws a frame, encoder reports clicks, RGB LED cycles,
   etc.).

If Phase 0 works on the bench, you're ready for Phase 1 (the breakout
board build). If anything is flaky on the bench, fix it there — it will
be 10× harder to fix once it's inside the MicroBrute.

### → If you're picking this up mid-build

Find the most recent phase you finished, then:

- **`MACROBRUTE_BUILD_PLAN.md`** — re-read just that phase + the next one.
- **`MACROBRUTE_CONNECTION_MAP.md`** *(Section 3)* — the canonical wiring
  reference. Cross-check anything you wired against this.
- **`MACROBRUTE_TROUBLESHOOTING.md`** *(Section 9)* — common pitfalls
  organised by phase.
- **Section 5 → Breakout Board** — re-check stripboard layout + track
  cuts before you power up.

If you've been away for >2 weeks: also re-read the **Key Decisions** table
in `MACROBRUTE_INDEX.md` — pin assignments and connector choices have
been deliberately frozen, but it's worth double-checking nothing in your
notes contradicts the canonical map.

---

## Skill prerequisites

You'll be comfortable if you have:

- **Through-hole soldering** at 1.5 mm pad pitch (DIP-8 / DIP-14 ICs).
- **Basic multimeter use** — continuity, DC voltage, resistance.
- **Breadboarding** — comfortable wiring jumpers from a schematic.

Helpful but not required:

- Reading schematics (the manual has both schematic *and* breadboard views
  side-by-side for the touchier circuits).
- Python + MicroPython basics (Pico firmware is hackable but works as-is).
- ARM-bare-metal C (only if you want to touch the LPC2361 firmware
  itself — most builders never will).

If you've never soldered DIP packages: do the touch-test board first
(`schematics/touch_test_board.svg`). It's 10 cm × 5 cm, ~30 minutes of
soldering, and gives you a working circuit-bend rig at the end.

---

## Time + cost expectations

| Phase | Calendar | Active hours | Out-of-pocket |
|---|---|---|---|
| Phase 0 — bench validation | 1 week | 4–8 h | ~$30 starter BOM |
| Phase 1 — breakout board | 2 weeks | 12–20 h | ~$60 (board parts + ICs) |
| Phase 2 — internal wiring | 2 weeks | 8–14 h | ~$15 (wire + connectors) |
| Phase 3 — panel mods (irreversible) | 2 weeks | 10–18 h | ~$40 (jacks + toggles + bolts) |
| Phase 4 — expander build | 4 weeks (parallel) | 20–35 h | ~$80 (panel + parts) |
| Phase 5 — system integration | 2 weeks | 6–12 h | ~$10 (DB-9 cable) |
| Phase 6 — custom LPC firmware (optional) | open-ended | 10+ h | $0 |

Total: ~$250 of parts spread over ~12 weeks of evenings/weekends. The
project is deliberately incremental — it works at every phase boundary,
so you can stop at any point and still have a usable instrument.

---

## What's locked vs. still in flux

Locked (don't propose changes here without strong reason):

- **2× DB-9 connector** as the MB ↔ expander interface (confirmed by the owner; HD-15 was rejected;
  see Key Decisions in the Master Index for why).
- **Pico GPIO assignments** — `firmware/pico/config.py` is canonical; see
  `schematics/pico_pinout.md` and the connection map. 3 pins are free
  (GP26-28); GP2 and GP3 are the SPI main OLED, GP11 the gate input.
- **Power scheme** — split: the expander runs from the rack only, the
  breakout from the synth only; only ground is shared over the DB-9.
  No supply rail and no I²C cross the cable.

Still in flux (your input welcome):

- **Expander size** — 17 HP or about 20 HP, open until the owner measures
  the blank.
- BT-14: the main OLED (Keyestudio-clone IIC/SPI 1.3" V2.0, chip SH1106 and pin order owner-stated) works with its CS pin tied to GND
  and the DB-9 count are for the owner to confirm (BF Q22, Q9). The board is a
  Raspberry Pi Pico (any variant with the standard 40-pin layout; RP2040 electrical
  facts quoted here come from the RP2040 datasheet and were not checked against
  Pico 2/RP2350).
- LPC bridge UART (UART1 is the working assumption, UNVERIFIED until the
  Phase 0 continuity check).
- Resonance vactrol — owned, but the part number and LED rating are unread.
- Whether the 9th touch bolt (envelope retrigger, M11) makes the cut.
- Final mix of 6 panel touch bolts from the 8 documented bends.
- Whether the optional LPC2361 custom firmware ships with v1.

When in doubt, treat anything in the Master Index → "Key Decisions" table
as locked, and anything labelled **TBD** or **maybe** elsewhere in the
manual as open.

---

## Where to find things at a glance

The sidebar groups sections into three clusters:

- **PLAN (0–3)** — what you're building, why, and in what order. Read
  these first.
- **BUILD (4–8)** — every wiring diagram, stripboard, and panel cut.
  Reference during construction.
- **REFERENCE (9–12)** — IC pinouts, test points, glossary,
  troubleshooting, mod catalog, research notes, legacy archive.

If a doc isn't in any of those: it's an internal `.md` not surfaced in
the rendered manual. Browse `docs/` directly.
