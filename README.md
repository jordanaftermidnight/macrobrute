# MACROBRUTE

**Arturia MicroBrute Deep Modification Project**

Transform an Arturia MicroBrute into a fully semi-modular instrument through internal circuit mods, a Raspberry Pi Pico digital brain on a Eurorack expander (17 HP or about 20 HP, width open), and firmware reverse engineering. The EFFIGY Daisy DSP I²C pairing is shelved (kept as an idea for another project). Two earlier-design companion modules (JF-33 delay, DSO138 scope) live as spinoffs under `spinoffs/` — out of the canonical build.

> **Status (2026-10-17):** design stage, nothing built. The docs were reconciled against `docs/superpowers/reviews/2026-10-16-project-audit.md`; `docs/MACROBRUTE_CONNECTION_MAP.md` is the authority for pins and wiring. Anything not proven is marked UNVERIFIED.

## Documentation — start here

- 🛠 **[Build Plan](./docs/MACROBRUTE_BUILD_PLAN.md)** — canonical 7-phase roadmap from bench validation to full integration
- 🔌 **[Connection Map](./docs/MACROBRUTE_CONNECTION_MAP.md)** — every signal, pin, GPIO, and wire in the system
- 🤝 **[EFFIGY Bridge Protocol](./docs/MACROBRUTE_EFFIGY_BRIDGE.md)** — SHELVED: I²C peer-pair register map, archived as an idea for another project
- 🎛 **[Mod Selection](./docs/MACROBRUTE_MOD_SELECTION.md)** — the 12 panel mods + 6 touch bolts curated from 130+ audited
- 📇 **[Master Index](./docs/MACROBRUTE_INDEX.md)** — directory of all docs, firmware, schematics, and research
- 📖 **Macrobrute Manual** — offline single-file build manual (~2.5 MB, regenerated from all docs above via `tools/build_manual.py`): [rendered view](https://htmlpreview.github.io/?https://github.com/jordanaftermidnight/macrobrute/blob/main/Macrobrute%20Manual.html) · [download / raw source](./Macrobrute%20Manual.html)
  GitHub does not render .html files, it shows their source; htmlpreview.github.io is a third-party viewer that renders the file from this repo.

## Project Scope

- **Eurorack expander (17 HP or about 20 HP, width open until the blank is measured)** — hosts the Pico, main OLED (the owner's Keyestudio-clone IIC/SPI 1.3" V2.0 board in SPI mode; chip SSD1306 or SH1106, UNVERIFIED), HW-040 encoder, tap button, RGB LED, clock I/O, firmware clock dividers, 4 programmable aux outputs, and three analog utilities: slew limiter, LFO and Sample & Hold (standalone, rack power only). Noise, mult and attenuverter stay out.
- **Panel modifications on MB** — 1 new Resonance CV jack, 3 toggles (Brute Factor bypass, drone, starve), 3 insert jacks (VCF, Metalizer, VCA CV), 6 brass touch bolts on body sides (selected from 8 designed candidates after Phase 0 bench testing), and the 2× DB-9 on the rear panel left of Pitch/Gate. The 0.91" strip OLED is dropped.
- **Signal taps** — 10+ buffered waveform/CV outputs from internal test points
- **CV injection** — Filter and VCA via DB-9 B; Resonance via new MB panel jack
- **DB-9 interconnect** — 2× shielded DB-9 on the MB rear panel (left of Pitch/Gate; dimensions UNVERIFIED). DB-9 A carries 8 audio/CV/gate outputs + GND. DB-9 B carries UART TX, UART RX, Filter CV, VCA CV and grounds only. **No supply rail and no I²C cross the cable.**
- **Pico firmware** — main OLED, encoder, clock gen/detect/divide, programmable aux outputs, tap tempo + manual gate, RGB LED, LPC2361 UART bridge, USB-MIDI (not used while the DB-9 cables are connected)
- **EFFIGY peer pair — SHELVED.** Kept as an idea for another project; nothing is designed around it. GP2 and GP3, which it used, are now the main OLED's SCK and MOSI; GP11 is the gate input.
- **Norns Shield (anticipated, not designed)** — see `docs/MACROBRUTE_NORNS_BRIDGE.md`; its EFFIGY half is shelved.
- **LPC2361 firmware RE** — ~98% complete via .mbf decryption. 43 SysEx commands mapped. Pico↔LPC UART bridge framed as `0xAA · type · counter · len · payload · xor_checksum`.
- **Power** — split. The expander runs only from the Behringer CP1A rack supply (Pico VSYS from rack +5 V through a Schottky OR diode + bulk + 100 nF; CP1A +5 V is 0.5 A shared). The MB-side breakout runs only from the synth (TP70 +12 V, TP71 -12 V, TP72 GND). Only ground is shared across the cable. MicroBrute stock power untouched.
- **Circuit bending** — 6 touch bolts + 3 toggle mods + 3 panel jacks (curated from 130+ mods)

## Repository Structure

```
macrobrute/
├── docs/
│   ├── hardware/            # BOM, shopping list, pinouts
│   ├── firmware/            # LPC2361 investigation guide, firmware project docs
│   ├── mods/                # Modification guides, circuit bending (4 docs)
│   ├── research/            # Firmware RE findings, .mbf analysis
│   └── legacy/              # Earlier spec revisions and archived research
├── firmware/
│   ├── pico/                # Pico MicroPython firmware (15 .py files: 14 modules + 1 generated)
│   ├── lpc2361/             # LPC2361 ARM7 C firmware skeleton (48 files)
│   │   ├── src/             #   core, drivers, synth, midi, ui, utils
│   │   ├── include/         #   LPC2361 register definitions
│   │   ├── startup/         #   ARM vector table, syscalls
│   │   ├── linker/          #   Memory layout (128KB flash, 34KB SRAM)
│   │   └── tools/           #   flash.sh, monitor.sh
│   └── *.mbf                # Arturia firmware files (encrypted, under analysis)
├── schematics/              # 9 markdown circuit docs + 74 SVGs (stripboards, pinouts, wiring); several are STALE until regenerated
├── kicad/                   # KiCad 8 schematic projects
│   ├── breakout/            #   Internal breakout PCB
│   └── expander/            #   Eurorack expander module (STALE: old 42 HP scope, audit S58)
├── panel/                   # Panel files (SVG): MicroBrute template, finished-panel mockups, 17 HP expander
├── spinoffs/                # Companion projects out of canonical scope
│   ├── jf33-eurorack/       #   DIY PT2399 delay (speculative)
│   └── dso138-desktop/      #   DSO138 desktop scope (speculative)
└── tools/                   # Flash, RE, doc-build, diagram generators
    └── ghidra/              # Ghidra label tooling for LPC2361 analysis
```

## Hardware

### Already Have
MicroBrute, Raspberry Pi Pico (any variant with the standard 40-pin layout; RP2040 electrical facts quoted here come from the RP2040 datasheet and were not checked against Pico 2/RP2350), Arduino Nano (parked, no role), PL2303HX USB-TTL, Keyestudio-clone IIC/SPI 1.3" 128×64 OLED V2.0 (main baseline, used in SPI mode; 7 pins (owner confirmed); chip and order of the 7 pins UNVERIFIED), GME12864-11 0.96" OLED (arrived; spare / dev alternative; interface, chip and pin order UNVERIFIED), an earlier 4-pin I²C 1.3" OLED (wired into a TD-3, not available), 0.91" 128×32 SSD1306 (spare, strip OLED dropped), 16×2 1602 I²C LCD (fallback), HW040 encoder, DB-9 connectors ("several", count and gender UNVERIFIED), some vactrols, LED/LDR kit, IC kit and IC assortment, resistor kit, 6U 84HP Eurorack case, Behringer CP1A PSU. The full Have/Missing list is in `docs/hardware/MACROBRUTE_BOM.md`. (Spinoff parts — PT2399 + distortion ICs for JF-33 DIY, DSO138 kit for desktop scope — see `spinoffs/`.)

### Key Decisions
| Decision | Choice |
|----------|--------|
| Expander HP | **OPEN: 17 HP or about 20 HP** — the repo panel file is 87×128.5 mm, UNVERIFIED against the A-100 spec; owner measures the blank, both layouts are planned |
| Connector | 2× DB-9 shielded on the MB rear panel, left of Pitch/Gate (CONFIRMED by the owner; HD-15/VGA rejected). DB-9 B = UART TX/RX, Filter CV, VCA CV, grounds |
| Pico location | Inside the expander (not the MicroBrute case) |
| Main OLED | **Keyestudio-clone IIC/SPI 1.3" V2.0 board in SPI mode** on SPI0 (SCK GP2, MOSI GP3, DC GP4, RES GP5; CS tied to GND, PROVISIONAL (BT-14)), write-only, on the expander panel (owner ruling, 2026-10-17); 7 pins (owner confirmed, SPI only); chip SSD1306 or SH1106 and the order of the 7 pins are UNVERIFIED (read the silkscreen and chip marking). Firmware: `display.py` (`OLED_SPI`); for SH1106 set `OLED_CHIP="SH1106"`, `OLED_COL_OFFSET=2`. Larger than the 0.96" cutout, bears on the open expander width. |
| Strip OLED | **Dropped.** No I²C is used on the expander or crosses the DB-9 cable |
| MIDI path | Pico ↔ LPC2361 UART bridge @ 115200 baud (XOR checksum), LPC UART1 P0.15/P0.16 UNVERIFIED pending the continuity check; USB-MIDI on the Pico micro-USB, not used while the DB-9 cables are connected |
| EFFIGY pair | **Shelved** |
| Utilities (HW) | Slew limiter, LFO and Sample & Hold (standalone, rack power only). Noise, mult and attenuverter stay out |
| Utilities (FW) | Clock divider + 4 programmable aux outputs (PWM-capable, Euclidean/random/passthrough) |
| Power | Split: expander from the CP1A only (Pico VSYS via a Schottky OR diode); MB breakout from TP70/TP71/TP72 only; no supply on the cable; MB stock untouched |
| Nano | Parked — no role |

## Current Status

| Area | Status | Files |
|------|--------|-------|
| Pico firmware | 15 `.py` files (14 modules + the generated `_effigy_constants.py`, which serves the shelved EFFIGY code). Untested on hardware — Phase 0 bench validation next. | `firmware/pico/` |
| LPC2361 firmware | Skeleton — 48 C files, XOR checksum framing aligned with Pico side | `firmware/lpc2361/` |
| Schematics | Drawn at the old scope in places: 9 markdown docs + 74 SVGs + 2 KiCad projects, several STALE (audit section 2); redraw follows the audit | `schematics/`, `kicad/` |
| Panel files | 17 HP expander file (width open) + MB top-panel template; the strip OLED is dropped and no rear-panel template exists yet | `panel/` |
| EFFIGY bridge | **Shelved** (owner decision, 2026-10-17); archived as an idea for another project. | `docs/MACROBRUTE_EFFIGY_BRIDGE.md`, `firmware/pico/effigy_bridge.py` |
| Circuit review | Superseded in places by the 2026-10-16 audit (power budget, diode orientation) | `schematics/CIRCUIT_REVIEW.md`, `docs/superpowers/reviews/` |
| Firmware RE | ~98% complete — .mbf cracked, 43 SysEx cmds + 427 fns mapped in Ghidra | `docs/research/mbf_analysis.md` |
| Mods & bending | Complete — 4 guides covering all techniques | `docs/mods/` |
| Touch plates | 8 bends designed, 6 to be selected after Phase 0 bench testing — selection has not happened yet | `docs/mods/touch_bend_specs.md` |
| Hardware build | Not started — Phase 0 bench validation next | — |

## Resources

- [Hackabrute Schematics](https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html)
- [Maffez Pedrobrute](https://maffez.com/?page_id=2285)
- [MicroBrute SysEx RE](https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html)
- [MKNielsen2000 Add-ons](https://github.com/MKNielsen2000/MicroBrute-Add-ons)
- [DLO-138 Firmware](https://github.com/ardyesp/DLO-138)
- [Elektroid](https://github.com/dagargo/elektroid) — Open source MicroBrute device manager
- [EuroPi](https://github.com/Allen-Synthesis/EuroPi)
- [PicoEMP](https://github.com/newaetech/chipshouter-picoemp) — EMFI tool for CRP bypass

## License

Dual-licensed:

- **Firmware, tools, and documentation** — [MIT](./LICENSE)
  - Covers `firmware/`, `tools/`, `docs/`
- **Hardware designs** — [CERN-OHL-S-2.0](./LICENSE-HARDWARE) (strongly reciprocal)
  - Covers `schematics/`, `kicad/`, `panel/` and hardware-specific content in `docs/`
  - Full license text bundled at [`LICENSES/CERN-OHL-S-2.0.txt`](./LICENSES/CERN-OHL-S-2.0.txt)

**Arturia firmware binaries** (`firmware/*.mbf`) remain © Arturia — included for interoperability research under EU Software Directive 2009/24/EC Art. 6. Not covered by either license above.
