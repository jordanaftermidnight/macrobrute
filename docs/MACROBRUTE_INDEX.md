# MACROBRUTE Project — Master Index

**Project:** Arturia MicroBrute Deep Modification  
**Codename:** MACROBRUTE  
**Date:** April 2026  
**Status:** Ready for CCLI Handoff

---

## Document Hierarchy

### PRIMARY REFERENCE (Start Here)

| Document | Purpose | Lines |
|----------|---------|-------|
| `MACROBRUTE_COMPREHENSIVE_RESEARCH.md` | **Complete technical research** — all component values, circuits, pinouts, protocols | ~800 |
| `MACROBRUTE_FINAL_ARCHITECTURE.md` | **Current system design** — panel layout, DB-9 pinout, build phases | ~520 |
| `MACROBRUTE_CCLI_HANDOFF.md` | **Original CCLI handoff** — detailed specs before expander expansion | ~680 |

### SUBSYSTEM DOCUMENTS

| Document | Covers |
|----------|--------|
| `MACROBRUTE_COMPLETE_EXPANSION_MAP.md` | All signal taps, CV injection points, circuit bending locations |
| `MACROBRUTE_FIRMWARE_PROJECT.md` | LPC2361 firmware project structure + code snippets |
| `MACROBRUTE_BOM.md` | Bill of materials with part numbers |
| `MACROBRUTE_SHOPPING_LIST.md` | What to buy, what's already owned |

### SCHEMATICS (`../schematics/`)

| Document | Covers |
|----------|--------|
| `breakout_pcb.md` | Internal PCB: buffers, gate, LEDs, vactrol, CV protection |
| `expander_circuits.md` | Noise, LFO, clock divider, S&H, slew, attenuverter, mult |
| `jf33_cv_control.md` | PT2399 anti-latch-up, delay time CV, feedback CV, level matching |
| `dso130_input_protection.md` | Input protection, CD4051 mux, power |
| `wiring_diagram.md` | Complete signal flow: test points → DB-9 → expander |
| `pico_pinout.md` | Pico H GPIO assignments and peripheral allocation |
| `touch_plates.md` | Resistive, capacitive, MPR121 touch interfaces |
| `CIRCUIT_REVIEW.md` | Systematic review of all 13 circuit sections |

### RESEARCH (`research/`)

| Document | Covers |
|----------|--------|
| `firmware_re_findings.md` | CRP bypass methods, tools, KeyStep RE reference, open source tools |
| `mbf_analysis.md` | .mbf file encryption analysis: 360-byte block structure, differential, binary strings |
| `pt2399_dso138_findings.md` | Bergman BMC 83, CD2399 clone, DLO-138 firmware, serial export |
| `additional_mods_findings.md` | Soft sync broken, triangle 2x gain, VCA offset, through-zero PWM |

### MODS (`mods/`)

| Document | Covers |
|----------|--------|
| `microbrute_mods_guide.md` | Standard mods: test point breakouts, oscillator, filter, portamento |
| `microbrute_circuit_bending_guide.md` | Body contacts, touch points, creative short circuits |
| `deep_circuit_bending.md` | Advanced: PT2399 deep bends, DSO138 exploitation, cross-device |
| `ultimate_microbrute_project.md` | Comprehensive project overview |

### FIRMWARE

| Location | Covers |
|----------|--------|
| `firmware/lpc2361_investigation_guide.md` | Step-by-step ISP connection, CRP detection, Ghidra setup |
| `firmware/MACROBRUTE_FIRMWARE_PROJECT.md` | LPC2361 C firmware reference (code in `firmware/lpc2361/`) |
| `../firmware/pico/` | 8 MicroPython modules: display, encoder, clock, menu, midi, leds, main, config |
| `../firmware/lpc2361/` | 48 C files: drivers, synth, midi, Pico comm, ARM startup, Makefile |

### KICAD (`../kicad/`)

| Project | Covers |
|---------|--------|
| `breakout/` | Internal breakout PCB schematic |
| `expander/` | 42HP Eurorack expander module |
| `jf33/` | JF-33 delay CV control & level matching |
| `dso_input/` | DSO138 input protection & CD4051 multiplexer |

### LEGACY/REFERENCE (May Have Outdated Info)

| Document | Notes |
|----------|-------|
| `MACROBRUTE_MASTER_PLAN.md` | Early planning document |
| `MACROBRUTE_V2_SPEC.md` | Earlier spec revision |
| `MACROBRUTE_REVISED_SPEC.md` | DB-9 correction (from DB-25 hallucination) |
| `MACROBRUTE_EXPANDER_DB37_PINOUT.md` | **OBSOLETE** — predates DB-9 decision (moved here from `docs/hardware/`) |

---

## Key Decisions Summary

| Decision | Choice |
|----------|--------|
| Project name | MACROBRUTE (renamed from ÜBERBRUTE) |
| Connector | 2× DB-9 (18 pins total) |
| Panel mods | Minimal — OLED, encoder, button, LEDs, 2-4 switches |
| Body jacks | 4 positions: Envelope Out, LFO Out, Ultrasaw Out, PWM Out |
| All patching | Via Eurorack expander |
| Expander size | ~50HP (includes DSO130 + JF-33 delay) |
| Power isolation | Separate supplies, signal ground only via DB-9 |
| Nano | Parked — Pico handles everything |
| Scope signal select | 6-position rotary switch |

---

## Hardware Summary

### Already Have
- MicroBrute
- Pico H
- Arduino Nano (parked)
- PL2303HX USB-TTL
- 1.3" OLED (SPI/I²C)
- 0.96" SSD1306 I²C (ordered)
- HW040 encoder
- 2× DB-9 connectors
- LEDs + LDRs
- IC kit (NE555×20, LM358×10, etc.)
- DSO130 oscilloscope kit (built)
- Joyo JF-33 delay PCB (extracted)
- 6U 84HP Eurorack case

### Need to Acquire
- 3.5mm mono jacks (35+)
- SPST toggle switches (4-6)
- 100kΩ pots 9mm (8+)
- 6-position rotary switch
- TL074 (4), TL072 (3)
- CD4024 (2), CD4066 (2), CD4051 (1)
- CD40106 (2)
- 2N3904 (10)
- SSI2164 (1) — for delay CV control
- Perfboard / PCB blanks
- 42-50HP Eurorack panel blank
- Heat shrink 6mm black (for vactrols)

---

## Build Phases

### Phase 0: Preparation
- [ ] Open MicroBrute, photograph PCBs
- [ ] Probe test points with multimeter
- [ ] Breadboard Pico + OLED + encoder
- [ ] Connect PL2303HX to LPC2361, check CRP level
- [ ] Measure panel clearance for OLED cutout

### Phase 1: Internal Wiring (No Drilling)
- [ ] Build breakout PCB (Pico mount, buffers, LED drivers)
- [ ] Wire test point taps (flying leads)
- [ ] Wire DB-9 connectors (loose)
- [ ] Build vactrol, test resonance CV
- [ ] Test all signals

### Phase 2: MicroBrute Panel
- [ ] Create drilling template
- [ ] Cut OLED window
- [ ] Drill holes (encoder, button, LEDs, switches)
- [ ] Mount components
- [ ] Final wiring

### Phase 3: Rear Panel
- [ ] Drill for 2× DB-9
- [ ] Mount connectors
- [ ] Build interconnect cable
- [ ] Test signal pass-through

### Phase 4: Expander Build
- [ ] Design/layout expander PCB
- [ ] Build buffer section (TL074 × 3)
- [ ] Build utilities (noise, LFO, clock div, S&H, slew)
- [ ] Install DSO130 with input protection
- [ ] Install JF-33 with level matching + CV control
- [ ] Wire all jacks
- [ ] Mount in panel

### Phase 5: Pico Firmware
- [ ] OLED driver + basic display
- [ ] Encoder menu system
- [ ] Clock generator (tap tempo)
- [ ] Clock input detection
- [ ] LED indicators
- [ ] MIDI SysEx bridge

### Phase 6: Advanced
- [ ] Touch plate construction
- [ ] Circuit bending switches
- [ ] LPC2361 investigation
- [ ] Delay glitch mods

---

## CCLI Task Queue

### Immediate (Schematics)
1. Breakout PCB schematic — Pico mount, buffers, LED drivers
2. Panel drilling template SVG
3. Expander main schematic
4. DSO130 input protection circuit
5. JF-33 CV control circuit (with anti-latch-up)

### Documentation
6. Wiring diagrams (internal + DB-9)
7. Pico GPIO pinout diagram
8. Expander panel layout (50HP)

### Firmware
9. Pico firmware scaffold (MicroPython)
10. OLED menu system
11. Clock gen/detect module

### Research
12. LPC2361 ISP pin locations on physical PCB
13. Ghidra project setup for ARM7TDMI

---

## File Locations

All documents are in:
- `/mnt/user-data/outputs/MACROBRUTE_*.md`
- `/mnt/user-data/outputs/MACROBRUTE_BOM.docx`

Previous session transcripts:
- `/mnt/transcripts/` (see journal.txt)

---

## Key Resources

### MicroBrute
- Schematics: https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- Maffez Pedrobrute: https://maffez.com/?page_id=2285
- ModWiggler thread: https://modwiggler.com/forum/viewtopic.php?t=152071
- MKNielsen2000 Add-ons: https://github.com/MKNielsen2000/MicroBrute-Add-ons
- SysEx RE: https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html

### DSO130/138
- DLO-138 firmware: https://github.com/ardyesp/DLO-138

### PT2399/Delay
- ElectroSmash analysis: https://www.electrosmash.com/pt2399-analysis
- VC-Echo design: http://www.sdiy.org/destrukto/vc-echo.html

### LPC2361
- Datasheet: https://www.nxp.com/docs/en/data-sheet/LPC2361_62.pdf
- User manual: https://www.keil.com/dd/docs/datashts/philips/lpc23xx_um.pdf
- lpc21isp: https://github.com/capiman/lpc21isp
- ChipWhisperer: https://github.com/newaetech/chipwhisperer

### Eurorack DIY
- Yusynth modules: https://yusynth.net/Modular/index_en.html
- N8 Synthesizers: https://www.n8synth.co.uk/diy-eurorack/

### Pico
- EuroPi: https://github.com/Allen-Synthesis/EuroPi
- micropython-rotary: https://github.com/miketeachman/micropython-rotary
