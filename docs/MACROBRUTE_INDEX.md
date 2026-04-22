# MACROBRUTE — Master Index

**Project:** Arturia MicroBrute Deep Modification
**Status:** Design + firmware RE complete. Hardware build: 0% (bench validation next).
**Last reconciliation:** 2026-04-22

---

## Start Here

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview, status matrix, hardware summary |
| `MACROBRUTE_BUILD_PLAN.md` | **Canonical roadmap** — 7 phases, bench → integration |
| `MACROBRUTE_CONNECTION_MAP.md` | **Canonical wiring** — every signal, pin, and mod |
| `MACROBRUTE_MOD_SELECTION.md` | Curated 12 mods + 6 touch bolts from 130+ audited |
| `Macrobrute Manual.html` | Single-file rendered build manual (built from `tools/build_manual.py`) |

## Key Decisions (authoritative)

| Decision | Choice |
|----------|--------|
| Connector | 2× DB-9 (18 pins total) — VGA HD-15 rejected |
| OLED | **1.3" SH1106 I²C** on GP4 (SDA) / GP5 (SCL). Fallbacks: 0.96" SSD1306 I²C, 16×2 1602 I²C LCD |
| MIDI path | **Pico ↔ LPC2361 UART bridge** over UART0 (GP0/GP1) @ 115200 baud. No direct 31250-baud MIDI from Pico. |
| CD4051 replaces CD4066 | Unavailable locally (Kaunas) |
| RGB LED (common cathode) | GP8=R/clock, GP9=G/gate, GP10=B/mode. Replaces 3 discrete LEDs. |
| CD4049UBE | 5V→3.3V level shifting (CD40106 → Pico) |
| Touch mods | 6 body-contact bends (PITCH, CRUNCH, WAH, DISTORT, HARM, GATE), selected from 8 tested |
| Panel jacks | 3 (VCF insert, Metalizer insert, VCA CV in) |
| Panel toggles | 3 (Envelope bypass, Metalizer boost, VCA drone) |
| Expander size | **42HP** |
| JF-33 delay | **Separate Eurorack module** (Phase 7A, optional) |
| DSO138 oscilloscope | **Separate Eurorack module** (Phase 7B, optional) |
| Power | Separate supplies, signal ground only via DB-9 |

---

## Document Map

### Primary (current)
- `docs/MACROBRUTE_BUILD_PLAN.md` — 7-phase build plan
- `docs/MACROBRUTE_CONNECTION_MAP.md` — full wiring reference
- `docs/MACROBRUTE_MOD_SELECTION.md` — mod curation
- `docs/MACROBRUTE_FIRMWARE_MOD_PLAN.md` — LPC2361 custom firmware plan

### Architecture & Research
- `docs/architecture/MACROBRUTE_COMPLETE_EXPANSION_MAP.md` — every tap/inject/bend point
- `docs/architecture/MACROBRUTE_COMPREHENSIVE_RESEARCH.md` — component/circuit research
- `docs/research/mbf_analysis.md` — .mbf firmware decryption + Ghidra findings (43 SysEx cmds, 427 fns)
- `docs/research/firmware_re_findings.md` — CRP bypass methods, tools
- `docs/research/pt2399_dso138_findings.md` — delay + scope deep dive
- `docs/research/additional_mods_findings.md` — soft sync, triangle gain, VCA offset, PWM

### Hardware
- `docs/hardware/MACROBRUTE_BOM.md` — bill of materials
- `docs/hardware/MACROBRUTE_SHOPPING_LIST.md` — what to buy
- `docs/hardware/MACROBRUTE_TEST_POINTS_VERIFIED.md` — verified TPs with photos

### Schematics (`schematics/`)
- `CIRCUIT_REVIEW.md` — systematic review of all 13 circuit sections + corrections
- `breakout_pcb.md` + `breakout_stripboard.md` + `breakout_layout.svg` — internal PCB
- `expander_circuits.md` + `expander_stripboard.md` + per-module SVGs (LFO, noise, clock, S&H, slew, attenuverter)
- `jf33_cv_control.md` — PT2399 anti-latch-up + CV control (Phase 7A)
- `dso138_input_protection.md` — DSO138 protection + CD4051 mux (Phase 7B)
- `touch_plates.md` + `touch_test_board.svg` — 8-channel test board → 6 final bolts
- `pico_pinout.md` + `pico_pinout_diagram.svg` — Pico WH GPIO allocation
- `lpc2361_pinout_diagram.svg` — LPC2361 pinout (documented pins + RE gaps flagged)
- `db9_connector_diagram.svg` — full 18-pin DB-9 A/B interconnect map
- `power_regulation_diagram.svg` — Eurorack → breakout → Pico/expander rail chain
- `testpoints_map.svg` — 18 MicroBrute test points (waveforms, CV, gate, power, touch bends)
- `wiring_diagram.md` + `wiring_*.svg` — complete signal flow

### Firmware
- `firmware/pico/` — MicroPython modules: main, config, display (SH1106), encoder, clock, menu, midi (LPC bridge), leds, test_hw
- `firmware/lpc2361/` — C skeleton (48 files): drivers, synth, midi, ui, utils, ARM startup, Makefile
- `firmware/*.hex / *.bin / *.mbf` — Arturia firmware (decrypted + encrypted forms)
- `firmware/labels_export.csv` + `tools/ghidra/` — Ghidra label tooling
- `docs/firmware/lpc2361_investigation_guide.md` — ISP connection + CRP check procedure
- `docs/firmware/MACROBRUTE_FIRMWARE_PROJECT.md` — C firmware reference

### KiCad (`kicad/`)
- `breakout/` — internal breakout PCB schematic
- `expander/` — 42HP Eurorack expander module
- `jf33/` — JF-33 delay CV control (Phase 7A)
- `dso_input/` — DSO138 input protection (Phase 7B)

### Panel (`panel/`)
- `microbrute_panel_template.svg` — MB drilling template
- `expander_42hp.svg` — expander panel layout

### Mods (`docs/mods/`)
- `touch_bend_specs.md` — 8 circuit bends with specs (select 6)
- `microbrute_mods_guide.md` — standard mods reference
- `microbrute_circuit_bending_guide.md` — body contacts, shorts
- `deep_circuit_bending.md` — advanced techniques
- `ultimate_microbrute_project.md` — comprehensive overview

### Tools (`tools/`)
- `mbf_decrypt.py` / `mbf_encrypt.py` — XOR cipher, roundtrip verified (52 tests)
- `build_manual.py` — generates `Macrobrute Manual.html`
- `flash_pico.sh` — Pico firmware deploy wrapper
- `generate_*.py` — schematic/diagram SVG generators
- `analyze_firmware.py` + `ghidra_label_firmware.py` + `LabelMicroBruteFirmware.java` — legacy RE helpers
- `ghidra/` — current Ghidra labeling toolchain

### Legacy (`docs/legacy/`) — superseded, kept for reference
- `MACROBRUTE_FINAL_ARCHITECTURE.md` — pre-reconciliation architecture draft (Apr 15)
- `MACROBRUTE_PROJECT_HANDOFF.md` — early handoff doc
- `MACROBRUTE_EXPANDER_DB37_PINOUT.md` — obsolete DB-37 design (pre-DB-9 decision)
- `MACROBRUTE_MASTER_PLAN.md` — early planning
- `MACROBRUTE_V2_SPEC.md` / `MACROBRUTE_V2_COMPLETE_SPEC.md` — earlier spec revisions
- `MACROBRUTE_REVISED_SPEC.md` — DB-9 correction from DB-25

---

## Build Phase Summary

See `MACROBRUTE_BUILD_PLAN.md` for task-level detail.

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Bench validation (Pico + OLED + encoder on breadboard) | Not started |
| 1 | Breakout PCB stripboard build | Not started |
| 1B | Touch test board (8 bends → pick 6) | Not started |
| 2 | Internal wiring to MicroBrute test points | Not started |
| 3 | Panel drilling (OLED cutout, encoder, RGB LED, touch bolts, DB-9) | Not started |
| 4 | 42HP expander build (all utilities) | Not started |
| 5 | System integration + ground-loop audit | Not started |
| 6 | LPC2361 UART bridge + custom firmware | Firmware RE ~98% done; hardware bridge pending |
| 7A | JF-33 delay module (optional, separate) | Not started |
| 7B | DSO138 scope module (optional, separate) | Not started |

---

## External Resources

- Hackabrute schematics: https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- Maffez Pedrobrute: https://maffez.com/?page_id=2285
- MicroBrute SysEx RE (Matraszek): https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html
- Elektroid (open-source MB device manager): https://github.com/dagargo/elektroid
- DLO-138 firmware: https://github.com/ardyesp/DLO-138
- PT2399 analysis: https://www.electrosmash.com/pt2399-analysis
- EuroPi: https://github.com/Allen-Synthesis/EuroPi
- lpc21isp: https://github.com/capiman/lpc21isp
