# MACROBRUTE

**Arturia MicroBrute Deep Modification Project**

Transform an Arturia MicroBrute into a fully semi-modular industrial/techno/IDM instrument through internal circuit mods, a Raspberry Pi Pico WH digital brain, a 17HP Eurorack expander, firmware reverse engineering, and three optional companion modules (JF-33 delay, DSO138 scope, EFFIGY Daisy DSP via I²C peer-pair bus).

## Documentation — start here

- 🛠 **[Build Plan](./docs/MACROBRUTE_BUILD_PLAN.md)** — canonical 7-phase roadmap from bench validation to full integration
- 🔌 **[Connection Map](./docs/MACROBRUTE_CONNECTION_MAP.md)** — every signal, pin, GPIO, and wire in the system
- 🤝 **[EFFIGY Bridge Protocol](./docs/MACROBRUTE_EFFIGY_BRIDGE.md)** — I²C peer-pair register map (shared contract with the EFFIGY DSP module)
- 🎛 **[Mod Selection](./docs/MACROBRUTE_MOD_SELECTION.md)** — the 12 panel mods + 6 touch bolts curated from 130+ audited
- 📇 **[Master Index](./docs/MACROBRUTE_INDEX.md)** — directory of all docs, firmware, schematics, and research
- 📖 **[Macrobrute Manual.html](./Macrobrute%20Manual.html)** — offline single-file build manual (~1.7MB, regenerated from all docs above via `tools/build_manual.py`)

## Project Scope

- **17HP Eurorack expander** — hosts the Pico WH, main 1.3" OLED, encoder, tap button, RGB LED, clock I/O, slew limiter, firmware clock divider, 4 programmable aux outputs
- **Strip OLED on MB panel** — 0.91" 128×32 SSD1306 in the silkscreen area, glanceable status (tempo, clock source, MIDI ch, pair status)
- **Panel modifications on MB** — strip OLED, 1 new Resonance CV jack, 3 toggles (Brute Factor bypass, drone, starve), 3 insert jacks (VCF, Metalizer, VCA CV), 6 brass touch bolts on body sides
- **Signal taps** — 10+ buffered waveform/CV outputs from internal test points
- **CV injection** — Filter and VCA via DB-9 B; Resonance via new MB panel jack
- **DB-9 interconnect** — 2× DB-9 carries audio outputs (DB-9 A) and digital + power + 2 essential CVs (DB-9 B: UART bridge + I²C0 bus + Filter CV + VCA CV + ±12V + GND)
- **Pico WH firmware** — main + strip OLED, encoder, clock gen/detect/divide, programmable aux outputs, tap tempo + manual gate, RGB LED, LPC2361 UART bridge, USB-MIDI, EFFIGY peer-pair bus
- **EFFIGY peer pair** — separate 24HP Daisy DSP module on a hidden 5-pin rear I²C header. When paired, MACROBRUTE owns clock, EFFIGY owns main menu, encoders share focus. Audio/CV stay on Eurorack patches; I²C carries control + telemetry only.
- **JF-33 analog delay** — Separate Eurorack module with CV-controlled delay time (optional, Phase 7A)
- **DSO138 oscilloscope** — Separate Eurorack module with input protection + CD4051 mux (optional, Phase 7B)
- **LPC2361 firmware RE** — ~98% complete via .mbf decryption. 43 SysEx commands mapped. Pico↔LPC UART bridge framed as `0xAA · type · counter · len · payload · xor_checksum`.
- **Power** — Behringer CP1A Eurorack PSU. Pico fed from +5V bus via 3-part filter (1N5817 + 100µF + 100nF). MicroBrute stock power untouched. ±12V passes through DB-9 B for MB-side op-amp buffers.
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
├── schematics/              # 8 ASCII circuit docs + ~60 SVGs (stripboards, pinouts, wiring)
├── kicad/                   # KiCad 8 schematic projects
│   ├── breakout/            #   Internal breakout PCB
│   ├── expander/            #   42HP Eurorack expander module
│   ├── jf33/                #   JF-33 CV control & level matching (Phase 7A)
│   └── dso_input/           #   DSO138 input protection & mux (Phase 7B)
├── panel/                   # Panel templates (SVG): MicroBrute + 42HP expander
└── tools/                   # Flash, RE, doc-build, diagram generators
    └── ghidra/              # Ghidra label tooling for LPC2361 analysis
```

## Hardware

### Already Have
MicroBrute, Pico WH, Arduino Nano (parked), PL2303HX USB-TTL, 1.3" SH1106 I²C OLED (primary), 0.96" SSD1306 + 16×2 1602 I²C LCD (fallbacks), HW040 encoder, 2× DB-9, LED/LDR kit, IC kit, JF-33 delay PCB, DSO138 scope kit, 6U 84HP Eurorack case

### Key Decisions
| Decision | Choice |
|----------|--------|
| Expander HP | **17HP** (87×128.5mm panel — fits user's pre-cut blank) |
| Connector | 2× DB-9 shielded (no aux cable — DB-9 B carries digital + power + 2 CVs) |
| Pico location | Inside the expander (not the MicroBrute case) |
| Main OLED | 1.3" SH1106 I²C @ 0x3C on expander panel; fallbacks 0.96" SSD1306, 16×2 1602 LCD |
| Strip OLED | 0.91" SSD1306 128×32 @ 0x3D on MB panel — shared I²C0 bus via DB-9 B |
| MIDI path | Pico ↔ LPC2361 UART bridge @ 115200 baud (XOR checksum) + USB-MIDI on Pico micro-USB |
| EFFIGY pair | 5-pin JST-XH rear header (SDA/SCL/INT/3V3/GND), I²C @ 100 kHz, addr 0x42 |
| Utilities (HW) | Slew limiter only — noise/S&H/mult/LFO/attenuverter dropped (user already has these) |
| Utilities (FW) | Clock divider + 4 programmable aux outputs (PWM-capable, Euclidean/random/passthrough) |
| Power | CP1A Eurorack +5V via 3-part filter → Pico VSYS · ±12V via DB-9 B → MB breakout · MB stock untouched |
| Nano | Parked — Pico handles everything |

## Current Status

| Area | Status | Files |
|------|--------|-------|
| Pico firmware | Complete — 14 MicroPython modules (config + main + display + strip_display + encoder + clock + clock_divider + aux_outputs + menu + leds + midi + usbmidi + effigy_bridge + test_hw) | `firmware/pico/` |
| LPC2361 firmware | Skeleton — 48 C files, XOR checksum framing aligned with Pico side | `firmware/lpc2361/` |
| Schematics | Complete — 8 ASCII docs + ~60 SVGs + 4 KiCad projects | `schematics/`, `kicad/` |
| Panel templates | 17HP expander + revised MB panel (strip OLED + Res CV) | `panel/` |
| EFFIGY bridge | Protocol spec authored (register map 0x00–0xFF, INT-driven events, pair negotiation, heartbeat watchdog). Pico-side skeleton in `effigy_bridge.py`. EFFIGY-side implementation pending. | `docs/MACROBRUTE_EFFIGY_BRIDGE.md`, `firmware/pico/effigy_bridge.py` |
| Circuit review | Complete — 13 sections reviewed, 5 corrections applied | `schematics/CIRCUIT_REVIEW.md` |
| Firmware RE | ~98% complete — .mbf cracked, 43 SysEx cmds + 427 fns mapped in Ghidra | `docs/research/mbf_analysis.md` |
| Mods & bending | Complete — 4 guides covering all techniques | `docs/mods/` |
| Touch plates | Designed — 8 bends, 6 to be selected after bench testing in Phase 0 | `docs/mods/touch_bend_specs.md` |
| Hardware build | Not started — Phase 0 bench validation next | — |

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

Dual-licensed:

- **Firmware, tools, and documentation** — [MIT](./LICENSE)
  - Covers `firmware/`, `tools/`, `docs/`
- **Hardware designs** — [CERN-OHL-S-2.0](./LICENSE-HARDWARE) (strongly reciprocal)
  - Covers `schematics/`, `kicad/`, `panel/` and hardware-specific content in `docs/`
  - Full license text bundled at [`LICENSES/CERN-OHL-S-2.0.txt`](./LICENSES/CERN-OHL-S-2.0.txt)

**Arturia firmware binaries** (`firmware/*.mbf`) remain © Arturia — included for interoperability research under EU Software Directive 2009/24/EC Art. 6. Not covered by either license above.
