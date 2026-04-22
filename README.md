# MACROBRUTE

**Arturia MicroBrute Deep Modification Project**

Transform an Arturia MicroBrute into a fully semi-modular industrial/techno/IDM instrument through internal circuit mods, a Raspberry Pi Pico WH digital brain, a 42HP Eurorack expander, firmware reverse engineering, and two optional companion modules (JF-33 delay, DSO138 scope).

## Documentation — start here

- 🛠 **[Build Plan](./docs/MACROBRUTE_BUILD_PLAN.md)** — canonical 7-phase roadmap from bench validation to full integration
- 🔌 **[Connection Map](./docs/MACROBRUTE_CONNECTION_MAP.md)** — every signal, pin, GPIO, and wire in the system
- 🎛 **[Mod Selection](./docs/MACROBRUTE_MOD_SELECTION.md)** — the 12 panel mods + 6 touch bolts curated from 130+ audited
- 📇 **[Master Index](./docs/MACROBRUTE_INDEX.md)** — directory of all docs, firmware, schematics, and research
- 📖 **[Macrobrute Manual.html](./Macrobrute%20Manual.html)** — offline single-file build manual (~1.7MB, regenerated from all docs above via `tools/build_manual.py`)

## Project Scope

- **Panel modifications** — OLED display, rotary encoder, status LEDs, circuit bending switches
- **Signal taps** — 10+ buffered waveform/CV outputs from internal test points
- **CV injection** — Filter, VCA, resonance (vactrol), sync, PWM inputs
- **Eurorack expander** (~42HP) — Full patchbay, LFO, noise, clock divider, S&H, slew, attenuverter
- **DB-9 interconnect** — 2x DB-9 (18 pins) connecting MicroBrute to expander
- **Pico WH firmware** — OLED menu, clock gen/detect, tap tempo, MIDI SysEx bridge
- **OLED menu** — 1.3" SH1106 I²C 128×64 for BPM, clock status, and menu system
- **JF-33 analog delay** — Separate Eurorack module with CV-controlled delay time (optional, Phase 7)
- **DSO138 oscilloscope** — Separate Eurorack module with input protection + CD4051 mux (optional, Phase 7)
- **LPC2361 firmware RE** — ~98% complete via .mbf decryption. 43 SysEx commands mapped. Pico↔LPC UART bridge planned.
- **Circuit bending** — 6 touch bolts + 3 toggle mods + 3 panel jacks (curated from 130+ mods)

## Repository Structure

```
macrobrute/
├── docs/
│   ├── architecture/        # System design, signal maps, research
│   ├── hardware/            # BOM, shopping list, pinouts
│   ├── firmware/            # LPC2361 investigation guide, firmware project docs
│   ├── mods/                # Modification guides, circuit bending (4 docs)
│   ├── research/            # Firmware RE findings, .mbf analysis, PT2399/DSO138
│   └── legacy/              # Earlier spec revisions
├── firmware/
│   ├── pico/                # Pico WH MicroPython firmware (9 modules)
│   ├── lpc2361/             # LPC2361 ARM7 C firmware skeleton (48 files)
│   │   ├── src/             #   core, drivers, synth, midi, ui, utils
│   │   ├── include/         #   LPC2361 register definitions
│   │   ├── startup/         #   ARM vector table, syscalls
│   │   ├── linker/          #   Memory layout (128KB flash, 34KB SRAM)
│   │   └── tools/           #   flash.sh, monitor.sh
│   └── *.mbf                # Arturia firmware files (encrypted, under analysis)
├── schematics/              # Circuit designs — ASCII schematics (7 docs)
├── kicad/                   # KiCad 8 schematic projects
│   ├── breakout/            #   Internal breakout PCB
│   ├── expander/            #   42HP Eurorack expander module
│   ├── jf33/                #   JF-33 CV control & level matching
│   └── dso_input/           #   DSO138 input protection & mux
├── panel/                   # Panel templates (SVG)
└── tools/                   # Flash scripts, utilities
```

## Hardware

### Already Have
MicroBrute, Pico WH, Arduino Nano (parked), PL2303HX USB-TTL, 1.3" SH1106 I²C OLED (primary), 0.96" SSD1306 + 24×2 I²C LCD (fallbacks), HW040 encoder, 2× DB-9, LED/LDR kit, IC kit, JF-33 delay PCB, DSO138 scope kit, 6U 84HP Eurorack case

### Key Decisions
| Decision | Choice |
|----------|--------|
| Connector | 2x DB-9 (18 pins total) |
| Panel mods | Minimal — OLED, encoder, button, LEDs, 2-4 switches |
| All patching | Via Eurorack expander |
| Expander size | ~42HP |
| Power | Separate supplies, signal ground only via DB-9 |
| Nano | Parked — Pico handles everything |

## Current Status

| Area | Status | Files |
|------|--------|-------|
| Pico firmware | Complete — 9 MicroPython modules (untested on HW) | `firmware/pico/` |
| LPC2361 firmware | Skeleton — 48 C files, needs ARM toolchain | `firmware/lpc2361/` |
| Schematics | Complete — 7 ASCII docs + 4 KiCad projects | `schematics/`, `kicad/` |
| Panel templates | Complete — MB panel + 42HP expander SVGs | `panel/` |
| Circuit review | Complete — 13 sections reviewed, 5 corrections | `schematics/CIRCUIT_REVIEW.md` |
| Firmware RE | ~98% complete — .mbf cracked, 43 SysEx cmds + 427 fns mapped in Ghidra | `docs/research/mbf_analysis.md` |
| Mods & bending | Complete — 4 guides covering all techniques | `docs/mods/` |
| Touch plates | Complete — resistive + capacitive + MPR121 designs | `schematics/touch_plates.md` |

## Resources

- [Hackabrute Schematics](https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html)
- [Maffez Pedrobrute](https://maffez.com/?page_id=2285)
- [MicroBrute SysEx RE](https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html)
- [MKNielsen2000 Add-ons](https://github.com/MKNielsen2000/MicroBrute-Add-ons)
- [PT2399 Analysis](https://www.electrosmash.com/pt2399-analysis)
- [DLO-138 Firmware](https://github.com/ardyesp/DLO-138)
- [Elektroid](https://github.com/dagargo/elektroid) — Open source MicroBrute device manager
- [EuroPi](https://github.com/Allen-Synthesis/EuroPi)
- [PicoEMP](https://github.com/newaetech/chipshouter-picoemp) — EMFI tool for CRP bypass

## License

Hardware designs: CERN-OHL-S-2.0
Firmware: MIT
