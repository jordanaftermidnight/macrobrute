# MACROBRUTE

**Arturia MicroBrute Deep Modification Project**

Transform an Arturia MicroBrute into a fully semi-modular industrial/techno/IDM instrument through internal circuit mods, a Raspberry Pi Pico H digital brain, Eurorack expander module, integrated oscilloscope, CV-controlled delay, and firmware reverse engineering.

## Project Scope

- **Panel modifications** — OLED display, rotary encoder, status LEDs, circuit bending switches
- **Signal taps** — 10+ buffered waveform/CV outputs from internal test points
- **CV injection** — Filter, VCA, resonance (vactrol), sync, PWM inputs
- **Eurorack expander** (~42HP) — Full patchbay, LFO, noise, clock divider, S&H, slew, attenuverter
- **DB-9 interconnect** — 2x DB-9 (18 pins) connecting MicroBrute to expander
- **Pico H firmware** — OLED menu, clock gen/detect, tap tempo, MIDI SysEx bridge
- **DSO130 oscilloscope** — Integrated with signal multiplexer and input protection
- **JF-33 analog delay** — CV control of delay time and feedback, Eurorack level matching
- **LPC2361 firmware RE** — CRP detection, potential dump/analysis/modification
- **Circuit bending** — Touch plates, body contacts, IC-level bend switches

## Repository Structure

```
macrobrute/
├── docs/                    # Project documentation
│   ├── architecture/        # System design, signal maps, research
│   ├── hardware/            # BOM, shopping list, pinouts
│   ├── firmware/            # LPC2361 firmware project docs
│   ├── mods/                # Modification guides, circuit bending
│   └── legacy/              # Earlier spec revisions
├── firmware/
│   ├── pico/                # Pico H MicroPython firmware
│   └── lpc2361/             # LPC2361 C firmware (if CRP bypassed)
├── schematics/              # Circuit designs (ASCII + KiCad)
├── panel/                   # Panel templates (SVG)
└── tools/                   # Flash scripts, utilities
```

## Hardware

### Already Have
MicroBrute, Pico H, Arduino Nano, PL2303HX USB-TTL, 1.3" OLED, HW040 encoder, 2x DB-9, LED/LDR kit, IC kit, DSO130 (built), JF-33 delay PCB, 6U 84HP Eurorack case

### Key Decisions
| Decision | Choice |
|----------|--------|
| Connector | 2x DB-9 (18 pins total) |
| Panel mods | Minimal — OLED, encoder, button, LEDs, 2-4 switches |
| All patching | Via Eurorack expander |
| Expander size | ~42HP |
| Power | Separate supplies, signal ground only via DB-9 |
| Nano | Parked — Pico handles everything |

## Resources

- [Hackabrute Schematics](https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html)
- [Maffez Pedrobrute](https://maffez.com/?page_id=2285)
- [MicroBrute SysEx RE](https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html)
- [MKNielsen2000 Add-ons](https://github.com/MKNielsen2000/MicroBrute-Add-ons)
- [PT2399 Analysis](https://www.electrosmash.com/pt2399-analysis)
- [DLO-138 Firmware](https://github.com/ardyesp/DLO-138)
- [EuroPi](https://github.com/Allen-Synthesis/EuroPi)

## License

Hardware designs: CERN-OHL-S-2.0
Firmware: MIT
