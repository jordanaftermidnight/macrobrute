# Diagram Batches 2 to 5 Roadmap

> **For agentic workers:** This is a roadmap, not a task-by-task plan. Each section below becomes its own plan (written with superpowers:writing-plans) when its owner decisions land. Steps use checkbox syntax once expanded.

**Goal:** Sequence the follow-up diagram and design batches after the Phase 0 batch (Tasks 1-14 of `docs/superpowers/plans/2026-10-16-project-review-and-diagram-redesign.md`), each reusing `tools/diagram_kit.py`, `tools/check_diagrams.py` and the `tools/diagrams/*` generator pattern (one module per card: `NETS` dict, `OUT` path, `python3 -m tools.diagrams.<name>`, a matching `tools/tests/test_<name>.py` that pins the nets, XML validity, 9 px text floor, forbidden-text absence and the review fixes).

**Sources read for this roadmap:** `docs/superpowers/reviews/2026-10-16-project-audit.md`, `docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md` (BF), `docs/superpowers/reviews/2026-10-17-archive-notes.md`, `tools/diagrams/power_chain.py`, `tools/diagram_kit.py`, `tools/check_diagrams.py`, `tools/build_manual.py` (`SVG_MAP`).

## Global Constraints

- Canonical pin source is `firmware/pico/config.py`; `docs/MACROBRUTE_CONNECTION_MAP.md` must agree with it (its own header says so).
- DECIDED (2026-10-16): connector stays 2x DB-9 (HD-15/VGA rejected: cable shorts pins 6-8 to GND; no DB-25 on hand). Both mount on the MicroBrute rear panel where the Arturia "A" logo is, between the MicroBrute name and the Kensington slot, to the left of the Pitch/Gate section. Dimensions UNVERIFIED until the user measures the panel.
- DECIDED: power is split. The expander is powered only from the Eurorack rack. The MicroBrute-side breakout (onboard mods) is powered only from the synth. No supply rail crosses the DB-9 cable, so DB-9 B pins 7/8 are freed; only a shared ground (pin 9) joins the two systems.
- DECIDED: the expander gains an LFO and a Sample & Hold. They are standalone rack utilities (no synth cabling), powered from the rack.
- The LPC bridge UART and the "spare GPIO" claim must be settled with evidence, not assumption (Task 3).
- DECIDED (owner answers, 2026-10-17): (a) rear panel, left of Pitch/Gate, confirmed; (b) the EFFIGY I2C pairing is SHELVED (rear JST-XH header, GP2/GP3/GP11, `EFFIGY_BRIDGE.md`, `effigy_bridge.py`: archive as an idea for another project, do not design around it); (c) the 0.91" strip OLED is DROPPED, so I2C0 serves only the 0.96" main OLED on the expander and NO I2C crosses the DB-9; (d) DB-9 B therefore carries UART TX/RX, Filter CV, VCA CV and grounds only: the final map is derived in Task 4b with the grounds-between-CV-and-digital rule; (e) expander width stays open until the owner measures the blank, so plan 17 HP and 20 HP layouts; (f) the TD3-project OLED/Arduino reuse idea is SCRAPPED; baseline stays Pico + 0.96" SSD1306; the owner HAS the KY-040 encoder and some vactrols (type/marking still to be read off them); (g) freed GPIOs GP2, GP3, GP11 plus GP26-28 give 6 spare Pico pins (resolves audit conflict C9).
- DECIDED (owner, 2026-10-17, later): connector CONFIRMED as 2x DB-9 (the VGA HD-15 line in a pasted inventory was an error; DB-9s are not freed for another project). OLED: the owner HAS two 1.3" OLEDs, one 7-pin SPI and one 4-pin I2C; the 0.96" SSD1306 may not have arrived. Baseline main OLED = the 1.3" 4-pin I2C module (chip, probably SH1106, UNVERIFIED: read the marking; the firmware already has an SH1106 driver and OLED_COL_OFFSET=2), the SPI one is spare/dev. A 1.3" display is larger than the 0.96" panel cutout, which also bears on the open expander width. Kit parts owned (from the owner's pasted inventory of the assortment kit, card contents UNVERIFIED): 2N3904, 2N3906, S8050, S8550, 2N5401, 2N5551 (10+ each), 1N4148 25+, 1N5819 x10 (40 V Schottky: usable as the Pico VSYS diode in place of the unowned 1N5817), 1N5822 x5, 1N270 x2. A CD4051 channel as the S&H switch (owned-parts alternative to buying an LF398) is an option to evaluate (charge injection UNVERIFIED).
- OWNED IC ASSORTMENT (from the owner's photo, 2026-10-17; the owner has further ICs not yet listed): PT2399 x3, LM393 x10, ICL7660S x2, PC817 optocoupler x20, UC3842AN x5, LM339 x10, NE555 x20, UC3843AN x5, NE5532 x5, LM358 x10, UL2003AN x5, LM386 x5, LM324 x10, ULN2803APG x5, TDA2030A x2, TDA2822D x5, JRC4558 x10. Add these to the owned-parts inventory. Opportunities to evaluate: NE5532/JRC4558 for audio/S&H sections, PC817 to galvanically isolate the UART across the cable (needs datasheet check of PC817 speed versus 115200 baud; the bridge baud is firmware-chosen so a lower rate such as 38400 is possible), ICL7660S for a negative rail.
- DESIGN RULE, owned parts only: every circuit uses parts the user already owns (status "Have" in `docs/hardware/MACROBRUTE_BOM.md` and the shopping list). Anything not owned is flagged with an owned-part alternative proposed; no design may require a new purchase without the user's approval.
- DESIGN RULE, back-feed: the expander (rack-powered) and the synth breakout/LPC (synth-powered) can be on at different times. Every digital line crossing the DB-9 cable (UART TX/RX, I2C SDA/SCL, any clock/gate) gets a series resistor, and the design must ensure no current can flow into an unpowered IC's input protection diodes or power it parasitically, whichever side is powered first or alone. Values chosen from owned resistors and justified (drive current, I2C rise time, UART edge rate).
- DESIGN RULE, hum: no audible mains hum or ground-loop noise. Single-point ground (shared only through DB-9 pin 9, star at TP72), shield drain tied at one end, audio/CV lines interleaved with ground, digital lines kept away from analog pins, and an owned-parts fallback ladder for if hum still appears (100 nF in series with ground, small series resistor, the owned isolation transformer on audio).
- Never add `Co-Authored-By` lines to commits or any file (user's global rule).
- Do not mention music genre in any new or edited document. Task 5 removes existing mentions.
- Diagram cards are self-contained light cards (own palette), fixed-width font, minimum 9px text, no clipped canvas, labels in knock-out boxes.
- Docs conflicts are reported to the user and resolved explicitly; never silently picked.
- No hardware is built yet; no step may assume measured values. Mark anything unverified "UNVERIFIED".
- Do not touch the untracked `MicroBrute_v1.0.4.114.bin.c/.h` files.

## Pattern every batch follows

1. `tools/diagrams/<card>.py` defines `NETS` (and rails), builds a `Card`, calls `validate_nets`, writes to `schematics/` or `panel/`.
2. `tools/tests/test_<card>.py` pins nets against `docs/MACROBRUTE_CONNECTION_MAP.md` and the BF note, and asserts the review fixes.
3. New kit glyphs get a test in `tools/tests/test_diagram_kit.py` (pin offsets via `*_pins` helpers, as for `resistor_pins`, `db9_pins`).
4. New validator rules get a test in `tools/tests/test_check_diagrams.py`.
5. `tools/build_manual.py` `SVG_MAP` is updated only when a new card replaces an old path; the manual build must report, not skip, a missing SVG.
6. Gates per card: `python3 -m pytest tools/tests -q`, `python3 tools/check_docs.py` exits 0, `rsvg-convert` render check, then an owner visual review. Commit with a plain message, no trailers.

Status words used below: DECIDED (in Global Constraints), OPEN (owner has not answered), UNVERIFIED (no evidence yet). Nothing OPEN or UNVERIFIED is treated as fact in any card; such values are drawn with an "UNVERIFIED" tag, as `power_chain.py` does.

## Old generators and SVGs that the batches supersede

These scripts still emit archived or defective SVGs if re-run (see `docs/superpowers/reviews/2026-10-17-archive-notes.md`). None is to be re-run for the manual; each card below says which output it replaces. Retiring a script means moving it to an archive folder in the same commit that lands its replacement card and updates `SVG_MAP`; nothing is deleted before then.

| Script | Still emits (relevant to these batches) | Replaced by |
|---|---|---|
| `tools/generate_schematics.py` | `db9_connector_diagram.svg`, `signal_flow_overview.svg`, `cv_input_protection_diagram.svg`, `esd_protection_schematic.svg`, `cv_control_flow.svg`, `lfo_schematic.svg`, `sah_schematic.svg`, `slew_limiter_schematic.svg`, `expander_power_distribution.svg`, `system_architecture_block.svg`, `wiring_overview.svg`, the `mod_m*.svg` set; also holds the 0.96 inch OLED references | Batches A, B, D |
| `tools/generate_circuit_schematics_v2.py` | circuit schematics of the old expander scope | Batches A, B |
| `tools/generate_layouts.py` | `breakout_layout.svg` (audit S34: row 20 has no cuts so J_PICO, J_OUT, J_IN pads short; decoupling caps without ground jumpers; unused CD40106 inputs not tied; Q1-Q3 share uncut segments), `expander_lfo.svg`, `expander_sah.svg`, `expander_slew.svg`, mod stripboards | Batches A, B, D |
| `tools/generate_cv_bus_diagram.py`, `generate_wiring_diagrams.py`, `generate_clean_architecture.py`, `generate_complete_architecture.py`, `generate_zone_layout.py`, `generate_final_fixes.py`, `generate_fixed_schematics.py`, `generate_clean_diagrams*.py`, `generate_diagrams_v3.py` | older duplicates of the SVGs above (`cv_control_flow`, `wiring_cv_protection`, `system_architecture_block`, `zone_layout_stripboard`) | Batch A |

Old SVGs found by `grep` to still show DB-9 B (some with supply rails, which contradicts the split-power decision; each must be checked, not assumed): `schematics/interconnect_wiring.svg`, `db9_connector_diagram.svg`, `breakout_layout.svg`, `esd_protection_schematic.svg`, `cv_control_flow.svg`, `signal_flow_overview.svg`, `system_architecture_block.svg`, `testpoints_map.svg`, `expander_power_distribution.svg`, `wiring_cv_protection.svg`, `wiring_overview.svg`, `wiring_power_distribution.svg`, `wiring_vactrol_driver.svg`, `vactrol_full_schematic.svg`, `zone_layout_stripboard.svg`, `panel/expander_finished_panel.svg`, `schematics/archive/manual_gate_button_schematic.svg`. Pico-side cards already regenerated (`pico_pinout_diagram.svg`, `power_regulation_diagram.svg`) mention it correctly. Panel files `panel/expander_17hp.svg` and `panel/expander_finished_panel.svg` still carry the 0.96 inch OLED cut-out, which is now OPEN (Q22).

## Bench checks referenced

BF defines BT-1 to BT-13 (UART edges, UART back-feed, CV back-feed, CV depth, gate, cable capacitance, DB-9 geometry, shield continuity, hum and crosstalk, CD4049UB input, clock IN, bus +5 V, PC817 baud). The checks named G1-G5 in the brief are NOT defined under that name in the audit, the BF note or the plan (searched); until the owner points to their definition they are treated as UNVERIFIED and no card cites them. Every card below carries a "Bench" tag naming the BT items that gate its numbers. No hardware is built; every value that a BT item would measure is drawn as UNVERIFIED.

---

## Batch A: Breakout and interconnect (2x DB-9 link, split power)

**Goal.** Redraw everything that touches the cable and the synth-side breakout so each card shows: DB-9 A (8 signals plus ground, order as in CM, BF section 2.3), DB-9 B (UART TX/RX, Filter CV, VCA CV and grounds only, BF section 2.2), no supply on either cable, ground joined only through the cable grounds with the star at TP72, shield drained at the MicroBrute end (BF rule, fallback in ladder step 3). Cards: interconnect wiring, DB-9 map, signal flow, output buffer board, CV input protection, plus the synth-side breakout stripboard layout.

**Inputs and owner decisions still needed.**
- OPEN Q9: DB-9 count, gender and flange of the owned connectors (4 panel connectors plus 2 cables are needed; count UNVERIFIED). Geometry stays UNVERIFIED until BT-7.
- OPEN Q10: insulating shoulder washers for the expander-side shells, or the alternative shield rule.
- OPEN Q14: keep the DB-9 A order or adopt a re-order, decided by BT-9.
- OPEN Q15: gate stage if TP83 is 3.3 V logic (UNVERIFIED, E-09); decision 3 (78L05 on the breakout) is Provisional.
- OPEN Q19 (CV mute) and Q20 (PC817 UART at 4800-9600 baud; UNVERIFIED until BT-13).
- OPEN C12: series diode or series resistor on the breakout rails; Q3 (BAT85 stock exactly used; 1N4148 or 1N5819 as provisional substitutes, recheck BT-2, BT-3, BT-5).
- Audit decision 7 (LPC bridge UART) stays open until the continuity check; the UART pair is drawn as provisional.
- Owned parts only: the LF398 (Q1) is not owned, so no card in this batch may need it.
- Bench tags: BT-1, BT-2, BT-3, BT-4, BT-5, BT-6, BT-7, BT-8, BT-9, BT-10, BT-11, BT-12.

**Supersedes.** `interconnect_wiring.svg`, `db9_connector_diagram.svg`, `signal_flow_overview.svg`, `output_buffer_board.svg`, `cv_input_protection_diagram.svg`, `esd_protection_schematic.svg`, `breakout_layout.svg` (defective, see table), `cv_control_flow.svg`, `system_architecture_block.svg`, `expander_power_distribution.svg`, `wiring_*.svg`, `zone_layout_stripboard.svg`; generators `generate_schematics.py`, `generate_circuit_schematics_v2.py`, `generate_layouts.py` (breakout part), the `generate_cv_bus_diagram.py` family. `SVG_MAP` lines in `tools/build_manual.py` at the matching paths.

**Task outline.**
1. Kit: add glyphs to `tools/diagram_kit.py` with `*_pins` helpers and tests: `opamp(x, y, label)` (triangle, inverting/non-inverting pins), `transistor(x, y, label, kind)` (NPN/PNP for 2N3904/2N3906), `cable_pair(x, y, label)` (shielded cable with drain end marked), `star_ground(x, y, label)` (TP72 star), `test_point(x, y, label)`, `stripboard(x, y, rows, cols, cuts)` for layouts (hole grid, track cuts, jumpers), `trimmer(x, y, label)`.
2. Validator rules in `tools/check_diagrams.py` with tests: no supply-named net (`P12`, `N12`, `P5`, `3V3`) may contain a `DB9_*` endpoint; every `CABLE_*` digital net has a series `R`; a second ground path between synth and rack is rejected (only `DB9_A:9`, `DB9_B:2/4/7/8/9` join the stars); shield drain nets have exactly one grounded end; an op-amp output driving a cable needs a series `R`; a part not in an owned set (new `tools/hwdata/owned.py`, read from the BOM "Have" rows) is flagged.
3. `tools/hwdata/db9.py`: the A and B pin maps from CM and BF as data, with a test that diffs it against `docs/MACROBRUTE_CONNECTION_MAP.md` (extend `tools/check_docs.py`).
4. `tools/diagrams/db9_map.py` -> `schematics/db9_connector_diagram.svg` (face view, numbers as moulded, UNVERIFIED tag on geometry until BT-7). Test: pins match `hwdata/db9.py`.
5. `tools/diagrams/interconnect.py` -> `schematics/interconnect_wiring.svg`. Test: no supply on cable, one ground join.
6. `tools/diagrams/signal_flow.py` -> `schematics/signal_flow_overview.svg` (audio blue, CV amber, gate green, UART in a distinct colour from the kit palette).
7. `tools/diagrams/output_buffer.py` -> `schematics/output_buffer_board.svg` (op-amp follower + 1k per output, per BF).
8. `tools/diagrams/cv_input_protection.py` -> `schematics/cv_input_protection_diagram.svg` (Clock IN 100k + 4049 stage, BT-10 and BT-11 tags; CV back-feed resistors 10k + 100k + 1 nF per BF with the BT-3 and BT-4 UNVERIFIED tags).
9. `tools/diagrams/breakout_layout.py` -> `schematics/breakout_layout.svg` using the stripboard glyph; a test asserts every track has cuts where pads would otherwise short, every decoupling cap has a ground jumper, and unused CD40106 inputs are tied (the S34 defects as regression tests).
10. Update `SVG_MAP`, move retired generators and old SVGs to an archive folder, rebuild the manual, run `check_docs.py`, render-check, owner review. Record each card's open items in its footer as UNVERIFIED.

---

## Batch B: Expander modules (LFO, Sample & Hold, slew, panel, stripboards)

**Goal.** Schematic, stripboard layout and panel for the rack-powered expander: LFO and S&H (DECIDED) plus the slew limiter, fed from the rack header only (CM section 5.3, `power_chain.py` rack side).

**Inputs and owner decisions still needed.**
- OPEN (E-22, E-23): width 17 HP versus about 20 HP; plan both layouts. A 1.3 inch OLED is larger than the 0.96 inch cut-out, which bears on width.
- OPEN Q22: main OLED chip marking (SH1106 likely, UNVERIFIED) and whether the 0.96 inch SSD1306 arrived.
- OPEN Q1: LF398N and hold capacitor are not owned. Owned alternative to evaluate: one CD4051 channel as the S&H switch with an owned op-amp buffer; charge injection and droop are UNVERIFIED and need a bench test before the card is final. No purchase without approval.
- OPEN Q6: LFO timing capacitor and 1M pots (not owned?) versus a different range with owned parts.
- OPEN Q2: vactrol marking and LED forward-current rating, needed for the V-to-I driver; vactrols are owned, type unknown.
- OPEN Q4 (1N4148 stock), Q5 (resistor values present), Q7 (aux-out trimmers), Q8 (jack type), Q12 (RGB LED, tactile button), Q13 (stripboard, sockets, wire); KY-040 encoder is owned.
- Owned ICs worth evaluating: NE5532, JRC4558, LM358, LM324, LM393, NE555, ICL7660S (negative rail option). Nothing is assumed suitable until checked against `docs/DATASHEETS.md`.
- Pico spare pins: GP2, GP3, GP11, GP26-28 (DECIDED, g). Any module using them must go through `FIRMWARE_ROLES`.
- Bench tags: BT-3, BT-4, BT-9, and a new S&H droop/charge-injection check to be defined in the Batch B plan (not in BF yet).

**Supersedes.** `schematics/lfo_schematic.svg`, `sah_schematic.svg`, `slew_limiter_schematic.svg`, `expander_lfo.svg`, `expander_sah.svg`, `expander_slew.svg`, `schematics/expander_stripboard.md` and `expander_circuits.md` (mixed files still holding dropped modules), `panel/expander_17hp.svg`, `panel/expander_finished_panel.svg` (0.96 inch OLED, DB-9 B supply labels), `kicad/expander` (owner decision pending: redraw or archive). Generators: `generate_schematics.py`, `generate_layouts.py`, `generate_circuit_schematics_v2.py`.

**Task outline.**
1. Kit glyphs: `pot(x, y, label)`, `ic_symbol` variants reuse `dip` for CD4051/NE5532/LM358 with tested pin tables in `tools/hwdata/ics.py` (pin numbers from `docs/DATASHEETS.md`), `rgb_led`, `encoder`, `panel_hole(x, y, d, label)` and `panel_outline(hp)` for panel cards (Eurorack 5.08 mm/HP, 128.5 mm height; hole sizes owned-part based, UNVERIFIED until measured), `vactrol(x, y, label)`.
2. Validator: rack-only supply check (expander nets use only `P12_RACK`, `N12_RACK`, `P5_RACK`, `GND`); every op-amp has decoupling on both rails; Pico GP assignments must be in `FIRMWARE_ROLES`; owned-parts rule from Batch A.
3. `tools/diagrams/lfo.py`, `sah.py`, `slew.py` -> schematic cards with UNVERIFIED tags on timing/range.
4. `tools/diagrams/expander_stripboard.py` -> one stripboard card per module plus a combined board if it fits (uses `stripboard`, tracks cut list as data, test for shorts as in Batch A task 9).
5. `tools/diagrams/expander_panel.py` -> `panel/expander_17hp.svg` and `panel/expander_20hp.svg` from one jack/pot/encoder list; a test asserts no overlap and minimum spacing (spacing figure UNVERIFIED, set from measured parts).
6. Update `SVG_MAP`, archive old files, rebuild manual, checks, owner review. Final width choice recorded after the owner decides.

---

## Batch C: MicroBrute rear-panel drill and layout (`panel/microbrute_rear_panel.svg`)

**Goal.** A 1:1 printable drill template for the two DB-9 connectors on the MicroBrute rear panel, left of the Pitch/Gate section (DECIDED, owner a).

**Blocked on.** Owner caliper measurements, audit decision 6 (list items 1-7: W_total, H_face, T_panel; X and Z positions of every rear feature; surface and ribs; depth behind the panel; connector flange, hole spacing, hole diameter, body, cup and nut dimensions; nearby case screws and PCB posts). Also needed: an owner photo of the rear face square-on with a scale (conflict C5 evidence, E-20). Known so far: hole spacing 24.99 mm and a size 9 cut-out of 19.74 x 11.18 mm from the Spectrum Control drawing; the owner's "24.5 x 11 mm" cut-out does not match either drawing; flange size, body depth and gender stay UNVERIFIED. Side-by-side needs about 62-71 mm free width (UNVERIFIED), stacked needs about 36 mm height and 39 mm width (UNVERIFIED). BT-7 and BT-8 apply. Whether the rear panel is plastic is UNVERIFIED.

**Supersedes.** Nothing existing: no rear-panel template exists (`panel/microbrute_panel_template.svg` covers the top panel). `panel/microbrute_finished_panel.svg` is kept as is.

**Task outline.** (Start only after the measurement sheet is in the repo.)
1. Add `docs/superpowers/reviews/2026-10-xx-rear-panel-measurements.md` as the data record (values entered by the owner, each marked measured or not).
2. `tools/hwdata/microbrute_rear.py`: measured dimensions as data; every missing value is `None` and makes the generator refuse to emit a drill hole.
3. Kit: `drill_hole(x, y, d)`, `panel_cutout(x, y, w, h)`, `dimension_line(...)`, `ruler_scale(mm)` with tests that the SVG user unit is exactly 1 mm so a 1:1 print is checkable (a 100 mm scale bar in the card).
4. `tools/diagrams/microbrute_rear_panel.py` -> `panel/microbrute_rear_panel.svg`; tests: two connectors do not overlap each other or features, margins at least the measured wall minimum, holes inside the free area.
5. Validator rule: panel cards list each hole with source "measured" or refuse to render.
6. Owner prints, tapes on, drills a scrap piece first, then confirms; only then add to `SVG_MAP` and the manual.

---

## Batch D: Mods m01 to m14 diagrams

**Goal.** Regenerate the fourteen mod schematics and the four stripboard cards with the kit, keeping all tap points tied to `docs/hardware/MACROBRUTE_TEST_POINTS_VERIFIED.md` and the mod docs in `docs/mods/`.

**Inputs and owner decisions still needed.**
- Every tap point and component value must trace to TPV or a datasheet row; any that does not is drawn UNVERIFIED (audit sections 2 and 5 hold the open items; read them again when the plan is written).
- Mods that route through the breakout depend on Batch A decisions (CV back-feed values, rail diodes C12, gate stage Q15).
- Owned-parts check per mod (Q5, Q18: further components not yet listed by the owner).
- OPEN: the vactrol-based mods need Q2.
- Touch-plate and test-board cards (`touch_plate_*.svg`, `touch_test_board.svg`) are optional additions; decide with the owner.
- Bench tags: BT-3, BT-4, BT-9 where a mod injects into the synth; mod-specific bench checks are to be defined in the Batch D plan.

**Supersedes.** `schematics/mod_m01_triangle_gain.svg` through `mod_m14_vco_bias_starve.svg` (14 files) and the four `*_stripboard.svg` (m02, m04, m08, m12); emitting generators `generate_schematics.py` and `generate_layouts.py`; `SVG_MAP` lines 109-126 and the description entries around lines 334-393 in `tools/build_manual.py`.

**Task outline.**
1. Kit: extra glyphs only as needed (`switch(x, y, label)`, `pot`, `jumper_wire`, `cap_polar`), each with a pin helper and test; reuse Batch A `opamp`, `transistor`, `stripboard`.
2. `tools/hwdata/mods.py`: per-mod data (tap points, parts, owned status) checked against TPV and `docs/mods/*.md` by a test in `tools/tests/`.
3. `tools/diagrams/mods_common.py` for the shared frame (synth-side tap legend, power from TP70/TP71/TP72 only).
4. One module per mod (`mod_m01.py` ... `mod_m14.py`), each with a nets test; do them in groups of three or four, with an owner visual check after each group.
5. Stripboard generators for m02, m04, m08, m12 using the Batch A shorts/cuts test.
6. Update `SVG_MAP`, archive the old SVGs and the generators, rebuild the manual, run all checks.

---

## Recommended order

1. Batch A first. It fixes the cards that still contradict the split-power decision, and its glyphs (op-amp, transistor, stripboard) and validator rules are reused by B and D. Start with kit and validator tasks (1-3), then the DB-9 map and interconnect cards, because the owner can review those without hardware.
2. Batch B next; start the LFO/S&H/slew schematics now and leave panel width and the S&H switch choice for the owner decisions. Both panel widths are drawn from one data list.
3. Batch D after A, in groups, since the mods reuse Batch A's glyphs and need no new owner decisions beyond the ones listed.
4. Batch C whenever the caliper sheet arrives; it is independent of the others and can be done in a short session. It must not start earlier.
5. Archive retired generators and SVGs at the end of each batch, not all at once, so the manual never loses a card without its replacement.

## Firmware follow-ups (not diagrams)

- Set `OLED_CHIP = "SH1106"` and `OLED_COL_OFFSET = 2` in `firmware/pico/config.py` once the owner has read the 1.3 inch module marking (Q22; SH1106 is probable, UNVERIFIED). Keep the SSD1306 values documented for the 0.96 inch module.
- Fix the `firmware/pico/display.py` docstring: it still says the primary target is the 0.96 inch SSD1306 and refers to the strip OLED.
- Remove the dropped code: `firmware/pico/strip_display.py` (0.91 inch strip OLED, dropped), and the shelved EFFIGY and DAISY code (`firmware/pico/effigy_bridge.py`, `DAISY_*` entries in `config.py`, `tools/check_effigy_bridge_sync.py`, `tools/sync_effigy_constants.py`). Archive rather than delete if the owner wants the idea kept for another project.
- `firmware/pico/test_hw.py`: remove the strip OLED references and update the primary OLED wording to the baseline module.
- I2C speed: code runs I2C0 at 400 kHz (`display.py`), older docs say 100 kHz for a cable run that no longer exists; settle the doc text (CM already notes the mismatch) and confirm 400 kHz works with the actual module on the bench.
- GP2, GP3, GP11 roles: currently tied to the shelved EFFIGY header in `config.py`; reassign as spare in `config.py` and `FIRMWARE_ROLES`, then regenerate the Pico pinout card and the CM table in the same commit.
