# Diagram Redesign — Design Spec

Date: 2026-10-16
Status: draft, awaiting user review

## Goal

Replace the ~60 inconsistent, partly incorrect SVG diagrams with one coherent set that
can be built from at the bench and re-trusted after time away. The existing
`schematics/breakout_layout.svg` (stripboard layout) is the style template.

## Problems with current diagrams

- Two visual languages: the stripboard card is light and self-contained; the rest are
  dark and rely on the manual theme, so they are unreadable or low-contrast in places.
- Overlapping labels, clipped canvases (signal flow, power chain), pin labels that do
  not match their pins (interconnect wiring), cluttered inline notes.
- Content drift: diagrams disagree with each other and with docs (e.g. OLED size and
  driver, which power rail feeds what).

## Design

### Shared kit — `tools/diagram_kit.py`
- Palette tokens: +12V red, -12V purple, GND green, 3V3/5V orange, signal colours
  (audio blue, CV amber, gate green, clock purple). Light card, 1px border, title +
  subtitle header, legend footer. Fixed-width font, minimum 9px text.
- Glyphs: resistor, capacitor, diode, LED, jack, DIP IC with numbered pins, header,
  rail, wire with junction dot, knock-out label box (labels never overlap wires).
- Every card fits its viewBox: no horizontal scroll, no clipping.
- Self-contained colours (no dependence on manual theme) so it renders the same in
  dark and light manual themes.

### Single source of truth — pin table
- One data module (Pico GPIO map from `schematics/pico_pinout.md` and firmware,
  DB-9 A/B pinout from `docs/MACROBRUTE_CONNECTION_MAP.md`). Diagram scripts reference
  pins by name, never retype labels.
- Doc conflicts found during the work (e.g. OLED 1.3" SH1106 vs 0.96" SSD1306) are
  reported to the user and resolved explicitly, not guessed.

### Per-diagram generators
- One short script per diagram under `tools/diagrams/`, declaring parts and nets as
  data and emitting SVG into `schematics/`. Existing generator scripts are left until
  superseded, then removed in a cleanup commit.

### Validator — `tools/check_diagrams.py`
- Checks each diagram's nets against the pin table: no GPIO used twice, no floating
  pins, I2C addresses consistent, voltage/rail consistent. Non-zero exit on mismatch.

### Batch 1 — Phase 0 bench set
1. Phase 0 wiring schematic (Pico left, peripherals right, straight runs).
2. Phase 0 breadboard (top-down, numbered rows/columns like the stripboard view).
3. Pico pinout card.
4. Power regulation chain card.
5. Pico power protection card.

Later batches (each its own cycle): breakout + interconnect (interconnect wiring,
DB-9 map, signal flow, output buffer board, CV input protection); expander modules;
mods m01-m14.

### Visual sign-off
Before mass generation, one card (Phase 0 wiring schematic) is mocked up in the
Design desktop app for the user to approve the look. Approved style is then encoded in
the kit.

### Integration
- Regenerated SVGs overwrite files in `schematics/`; `tools/build_manual.py`
  re-embeds them into `Macrobrute Manual.html`.
- Small commits: kit, validator, then one commit per diagram or small group.

### Testing
- Render each SVG with `rsvg-convert`, inspect the PNG, and check in both manual
  themes. Run `tools/check_diagrams.py`.

## Out of scope
- Panel SVGs, KiCad files, firmware changes (diagram/doc conflicts are reported, not
  silently fixed in firmware).
