# MACROBRUTE Comprehensive Build Plan

## Context

The MACROBRUTE project transforms an Arturia MicroBrute into a semi-modular industrial/techno instrument. Four sessions of work have produced 105+ files: Pico MicroPython firmware (8 modules, reviewed), LPC2361 ARM7 C firmware skeleton (48 files), ASCII + KiCad schematics (4 sub-projects), panel SVGs, 4 mod/bending guides, .mbf encryption cracked + firmware decrypted, and research docs. All documentation and design work is complete. **Nothing has been built yet.**

### Phase Reorder (2026-04-09)

Original order assumed physical access to MicroBrute throughout. Revised order front-loads software work:

| Priority | Phase | Status |
|----------|-------|--------|
| 1 | Phase 0: Toolchain setup | **Audited** — install commands ready |
| 2 | Phase 6A: .mbf decrypt / firmware RE | **DONE** — cipher cracked, firmware decrypted |
| 3 | Phase 1: Pico firmware bring-up | **Code reviewed** — 4 bugs fixed, ready for hardware |
| 4 | Phase 0: Hardware validation | Needs physical access |
| 5 | Phase 2: Internal wiring | Needs physical access |
| 6 | Phase 3: Panel mods | Needs physical access |
| 7 | Phase 4: Expander build | **BOM verified** — needs IC inventory check |
| 8 | Phase 5: System integration | After all above |

### IC Inventory Check Needed

Before ordering, verify which of these are already in the IC kit:
TL074×4, TL072×5, CD4024×1, CD4051×1, CD40106×2, LF398×1, 2N3904×8, BC337×1, 1N4148×8, 1N5817×6, BAT54S×9, 78L05×1, 7809×2

---

## Phase 0: Preparation (Week 1)

**Goal:** Validate hardware, set up toolchains, order components.

### Hardware Validation
- Open MicroBrute, photograph PCBs at high resolution
- Probe test points (TP83/93/94/19/30/10/11) with multimeter — verify signals exist
- Test Pico H: blink onboard LED, verify serial at 115200
- Breadboard: Pico + OLED (SPI: GP16-20) + encoder (GP13-15) + button (GP12)
- Verify PL2303HX USB-TTL with serial loopback

### Toolchain Setup (macOS)
```
brew install lpc21isp
brew install --cask ghidra
pip3 install pyserial mpremote
```

### Component Orders (2 batches, ship in parallel)

**Batch 1 — ICs + Passives (TME/Mouser, ~€70-85, 3-5 days):**

*ICs:*
| Component | Qty | Package | Used In |
|-----------|-----|---------|---------|
| TL074CN | 4 | DIP-14 | Breakout (1), Expander (3) |
| TL072CP | 5 | DIP-8 | Breakout (1), Expander (2), JF-33 (1), DSO (1) |
| CD4024BE | 1 | DIP-14 | Expander (clock divider) |
| CD4051BE | 1 | DIP-16 | DSO mux (shared with touch plates) |
| CD40106BE | 2 | DIP-14 | Breakout (1), Expander (1) |
| LF398N | 1 | DIP-8 | Expander (S&H) |
| 78L05 | 1 | TO-92 | Expander (+5V for CD4024) |
| 7809 | 2 | TO-220 | JF-33 (1), DSO (1) |

*Semiconductors:*
| Component | Qty | Package | Used In |
|-----------|-----|---------|---------|
| 2N3904 | 8 | TO-92 | Breakout LEDs (3), Expander noise (2), JF-33 (1), spare (2) |
| BC337 | 1 | TO-92 | JF-33 (anti-latch-up) |
| 1N4148 | 10 | DO-35 | Expander (6), JF-33 (2), spare (2) |
| 1N5817 | 6 | DO-41 | Breakout power (3), Expander power (2), spare (1) |
| BAT54S | 9 | SOT-23 | Breakout (3), Expander (4), DSO (1), spare (1) |

*Resistors (1/4W metal film):*
| Value | Qty | Used In |
|-------|-----|---------|
| 470Ω | 3 | Breakout LED current limiting |
| 1kΩ | 40 | Output series, LED base, input isolation (all boards) |
| 10kΩ | 15 | Pull-ups, dividers, gate circuit, bias (all boards) |
| 47kΩ | 2 | DSO feedback/bias |
| 100kΩ | 25 | Mixing, feedback, attenuators, timing (all boards) |
| 470kΩ | 2 | Expander noise bias |
| 1MΩ | 1 | Touch plate discharge |
| 4.7MΩ | 1 | Expander noise feedback |
| 10MΩ | 4 | Breakout TL074 input bias |

*Capacitors:*
| Value | Qty | Type | Used In |
|-------|-----|------|---------|
| 100nF | 35 | Ceramic (C0G/X7R) | IC decoupling, filtering (all boards) |
| 1nF | 1 | **Polystyrene** | Expander S&H hold cap (critical — never ceramic) |
| 1µF | 5 | Film (polyester) | LFO/slew timing, AC coupling, anti-latch |
| 10µF | 3 | Electrolytic 16V+ | Expander bulk decoupling |
| 47µF | 2 | Electrolytic 25V | Expander power filtering |
| 100µF | 4 | Electrolytic 25V | Breakout (2), JF-33 (1), DSO (1) |

*Misc passives:*
| Component | Qty | Notes |
|-----------|-----|-------|
| Ferrite bead 100Ω | 2 | Axial, breakout power lines |
| DIP-14 socket | 2 | TL074, CD40106 |
| DIP-8 socket | 2 | TL072, LF398 |
| DIP-16 socket | 1 | CD4051 |
| LED 3mm (red/green) | 6 | Expander indicators (clock, gate, LFO, dividers) |

**Batch 2 — Jacks + Pots + Hardware (Thonk + AliExpress, ~€60-80):**

*Thonk:*
| Component | Qty | Notes |
|-----------|-----|-------|
| Thonkiconn PJ398SM | 16 | Standard Eurorack mono jacks |
| Thonkiconn PJ301M | 15 | Compact Eurorack mono jacks |
| 100kΩ linear pot (9mm) | 5 | Expander attenuators (4), JF-33 CV (1) |
| 1MΩ log pot (9mm) | 3 | LFO rate, S&H rate, slew rate |
| Knobs (19mm, aluminum) | 12 | For all pots |
| 42HP blank panel | 1 | Anodized aluminum |

*AliExpress:*
| Component | Qty | Notes |
|-----------|-----|-------|
| 22AWG wire spool | 2 | Red + black, 10m each |
| Pin headers 2.54mm | 2 strips | Male + female |
| SPST toggle switch | 4 | Circuit bending (Phase 6E) |
| DB-9 solder-cup male | 2 | Rear panel interconnect |
| M2/M3 standoffs + screws | 1 kit | Nylon/brass assortment |
| Heat shrink assortment | 1 set | 2:1 ratio |
| Momentary pushbutton | 1 | Expander manual gate |
| Eurorack 16-pin power header | 1 | IDC + ribbon cable |
| Brass bolts M6×20 + washers | 4+4 | Touch plates (Phase 6D, optional) |

**Estimated total: €135-175** (excluding tools)

### Test Checkpoint
- [ ] Pico boots, OLED displays, encoder rotates, LEDs blink
- [ ] Serial port functional, toolchains installed

---

## Phase 1: Pico Firmware Bring-Up (Week 2-3)

**Goal:** Validate all 8 firmware modules on breadboard before touching the MicroBrute.
**Files:** `firmware/pico/` (config.py, display.py, encoder.py, clock.py, menu.py, midi.py, leds.py, main.py)

### Tasks
1. Flash `main.py` to Pico, verify boot banner on OLED
2. Test encoder: rotation moves menu cursor, push selects, long-press backs out
3. Test clock: tap tempo on GP12 button, verify BPM calculation, LED pulse on GP8
4. Test external clock input on GP21 (wire from function generator or second Pico)
5. Test MIDI SysEx output on GP4 (UART1, 31250 baud) — verify with MIDI monitor
6. Full menu navigation: Clock > BPM adjust, MIDI > bend range, Info screen

### Test Checkpoint
- [ ] All menu items navigate correctly
- [ ] Tap tempo accurate within ±2 BPM
- [ ] Clock output (GP22) frequency matches displayed BPM
- [ ] 3 LEDs respond (clock pulse, gate, mode)

**STOP if any module fails — debug before proceeding.**

---

## Phase 2: Internal Wiring — No Drilling (Week 3-5)

**Goal:** Build breakout PCB, wire all test points, verify signals through DB-9.
**Risk: HIGH** — soldering to MicroBrute PCB. Use 350°C iron, <2s per joint.

### 2.1 Build Breakout PCB (perfboard)
Assemble on stripboard (~60×40mm):
- Mount Pico H via pin headers (removable)
- TL074 #1: 4 unity-gain followers for TP94/93/30/19 (`schematics/breakout_pcb.md`)
- TL072 #2: triangle 2x gain buffer + envelope/LFO followers + vactrol driver
- CD40106: gate Schmitt trigger for TP83
- 3× 2N3904 LED drivers (GP8/9/10 → 220Ω → LED)
- Power: +12V/−12V via 1N5817 + ferrite + 100µF/100nF from TP70/71/72
- Pico power: +5V via 1N5817 → VSYS

### 2.2 Wire Test Points (flying leads, 24AWG)
| Source | Series R | Destination |
|--------|----------|-------------|
| TP94 (Saw) | 1kΩ | TL074A +in |
| TP93 (Square) | 1kΩ | TL074B +in |
| TP30 (VCO Mix) | 1kΩ | TL074C +in |
| TP19 (VCF Out) | 1kΩ | TL074D +in |
| TP124 (Triangle) | 1kΩ | TL072 D +in (2x gain) |
| TP83 (Gate) | 10kΩ | CD40106 pin 1 |
| Env (mod matrix) | 10kΩ | TL072 A +in |
| LFO (mod matrix) | 10kΩ | TL072 B +in |

### 2.3 Wire DB-9 A (outputs) — loose, not mounted yet
Buffer outputs → 1kΩ → DB-9 A pins per `schematics/wiring_diagram.md`

### 2.4 Build Vactrol
LED + LDR in sealed heat shrink. Test on breadboard first. Wire to TL072 C driver. LDR parallels RP13.

### Test Checkpoint
- [ ] All buffer outputs measurable with multimeter (play a note, see voltage swing)
- [ ] Gate output: 0V silent, 5V when key pressed
- [ ] DB-9 A pins show correct signals (continuity test)
- [ ] No shorts, no hum, Pico still boots

---

## Phase 3: Panel Mods (Week 5-7)

**Goal:** Drill MicroBrute panel, mount OLED/encoder/button/LEDs/switches.
**Template:** `panel/microbrute_panel_template.svg`
**Risk: MEDIUM** — drilling is irreversible. Practice on scrap first.

### Tasks
1. Print 1:1 drilling template, tape to panel, verify clearances
2. **Practice** on scrap material: OLED cutout (33×17mm), 7mm encoder, 3mm LEDs
3. Center punch, pilot drill (2mm), step drill / Dremel for cutouts
4. Mount components: OLED (standoffs), encoder (threaded), button, LEDs, toggles
5. Wire panel components to breakout PCB ribbon cables
6. Mount DB-9 connectors on rear panel (drill 2 cutouts)
7. Route clock wires (GP21/22) through rear panel grommet

### Test Checkpoint
- [ ] OLED visible through cutout, displays correctly
- [ ] Encoder, button, LEDs all functional after panel installation
- [ ] DB-9 connectors secure, no pin shorts

---

## Phase 4: Expander Build (Week 6-10, parallel with Phase 3)

**Goal:** Build all utility circuits, mount in 42HP panel, integrate via DB-9.
**Schematics:** `schematics/expander_circuits.md`, `kicad/expander/`

### Build Order (easiest → hardest, get sound early)

| Order | Circuit | ICs | Test Signal |
|-------|---------|-----|-------------|
| 1 | Buffered mult (1→3) | TL074 | Apply CV, verify 3 copies |
| 2 | Noise generator | 2N3904 + TL072 | Listen for white noise |
| 3 | LFO (tri + square) | TL072 ×2 | Scope: 0.04-40Hz waveforms |
| 4 | Clock divider (/2/4/8) | CD4024 + 78L05 | Feed clock, verify divisions |
| 5 | Sample & Hold | LF398 | Feed noise + clock, see staircase |
| 6 | Slew limiter | TL072 + diodes | Step input → smooth ramp |
| 7 | Attenuverter (2ch) | TL072 | Invert/scale CV |
| 8 | Manual gate button | Pushbutton + logic | Press → 5V gate |

### Panel & Assembly
- Drill 42HP panel per `panel/expander_42hp.svg`
- Mount ~30 jacks, 8 pots, LEDs
- Wire Eurorack power (16-pin header → ±12V/GND)
- Wire DB-9 interconnect cable (2× DB-9, 18 conductors, <1m)

### Test Checkpoint
- [ ] Each circuit works standalone on bench supply
- [ ] DB-9 cable passes all signals (continuity on 18 pins)
- [ ] Expander utilities modulate MicroBrute when connected

---

## Phase 5: System Integration (Week 10-12)

**Goal:** Full system test — MicroBrute + breakout + Pico + expander, all connected.

### Integration Tests
1. **Analog path:** Play MB note → Gate/Pitch/Saw/Square appear at expander jacks
2. **CV injection:** Expander LFO → DB-9 B → filter cutoff sweep heard on MB
3. **Resonance CV:** Expander CV → vactrol → resonance sweeps
4. **Clock sync:** Pico clock output → expander clock divider → /2/4/8 gates
5. **Touch plates:** (if built) brass bolts on panel → ADC → CV output
6. **MIDI:** Pico SysEx → MB parameter change (bend range, gate length)

### Pico Firmware Polish
- Save/load preferences to flash (BPM, sync mode)
- Screensaver timeout (120s)
- Startup LED test sequence
- Error handling for disconnected peripherals

### Test Checkpoint
- [ ] Full signal chain verified with oscilloscope or multimeter
- [ ] No ground loops, hum, or noise
- [ ] Pico menu fully operational, values persist across reboot
- [ ] All 18 DB-9 signals verified

---

## Phase 6: Advanced / Optional (Week 12+)

### 6A: LPC2361 Firmware RE — PARTIALLY COMPLETE

**.mbf decryption is DONE** (2026-04-09). Firmware binary extracted and ready for analysis.

Completed:
- [x] Cracked .mbf XOR cipher (key: `ArturiaminiBruteFirmware`, start index 4)
- [x] Extracted Intel HEX → 52.6KB ARM binary (v1.0.4.114)
- [x] Decryption tool: `tools/mbf_decrypt.py`
- [x] Peripheral usage map, function count (~327 Thumb), entry point 0x2184
- [x] Identified C++ runtime (Keil/IAR toolchain)

Remaining:
1. **Install Ghidra** (`brew install --cask ghidra`)
2. **Load firmware binary**: `ARM:LE:32:v4t`, base `0x2000`, entry `0x2184`
3. **Install SVD-Loader**, load LPC23xx SVD for peripheral labels
4. **Map key functions**: MIDI SysEx handler, DAC output, sequencer, parameter tables
5. **Optional:** Connect PL2303HX to UART0, check for debug output
6. **Optional:** PicoEMP EMFI — only needed for bootloader area access

### 6B: JF-33 Delay CV Integration
Build per `schematics/jf33_cv_control.md`:
1. Anti-latch-up circuit (BC337 + RC, **build first**)
2. Delay time CV (TL072 → 2N3904 current sink, 1kΩ emitter R)
3. Eurorack level matching (input atten + output gain)
4. Optional: SSI2164 feedback CV

### 6C: DSO138 Integration
Build per `schematics/dso130_input_protection.md`:
1. Input protection (BAT54S clamps)
2. CD4051 signal multiplexer (6 inputs)
3. 7809 power from +12V
4. Optional: flash DLO-138 firmware for serial export

### 6D: Touch Plates
Build per `schematics/touch_plates.md`:
1. 4 brass bolts on MB panel or expander
2. 10kΩ pull-ups → Pico ADC (GP26-28)
3. CD4051 multiplexed scanning (reuse DSO mux)
4. PWM → RC filter → CV output

### 6E: Circuit Bending Switches
Per `docs/mods/deep_circuit_bending.md`:
1. Brute Factor bypass toggle
2. VCA drone toggle (+12V → 100kΩ → TP10)
3. Power rail sag (10Ω series + 8.2V Zener clamp)
4. Metalizer feedback loop (100kΩ pot)

---

## Critical Path

```
Phase 0 (order parts) ──► Phase 1 (Pico breadboard)
         │                        │
         │                        ▼
         │                 Phase 2 (internal wiring)
         │                        │
         ▼                        ▼
   Parts arrive ──────► Phase 3 (panel drilling)
                                  │
                    Phase 4 ◄─────┘ (parallel)
                    (expander)    │
                         │        │
                         ▼        ▼
                    Phase 5 (system integration)
                         │
                         ▼
                    Phase 6 (advanced, optional)
```

**First sound: end of Phase 4 (~week 10)**
**Full system: end of Phase 5 (~week 12)**

---

## Verification

After each phase, run the test checkpoints listed. The critical gates are:
- Phase 1: Pico + OLED + encoder all work on breadboard
- Phase 2: Buffer outputs measurable at DB-9 pins
- Phase 5: Full analog path verified, no hum

For firmware: `mpremote connect /dev/tty.usbmodem* run main.py` on Pico.
For LPC2361 (future): `make && ./tools/flash.sh build/macrobrute.hex`
