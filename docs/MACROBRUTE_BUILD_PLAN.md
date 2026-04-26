# MACROBRUTE Comprehensive Build Plan

## Context

The MACROBRUTE project transforms an Arturia MicroBrute into a semi-modular industrial/techno instrument. ~130 files produced across multiple sessions: Pico MicroPython firmware (14 modules, complete), LPC2361 ARM7 C firmware skeleton (48 files), ASCII + KiCad schematics (4 sub-projects), stripboard SVG layouts (6 boards), panel SVGs, 4 mod/bending guides, .mbf encryption cracked + firmware decrypted, and research docs.

**Current status (2026-04-26):** Design phase complete after Phase D refresh. MicroBrute torn down + photographed. Firmware RE ~98% complete (43 SysEx commands, 107+ Ghidra labels). Pico firmware: 14 modules, including new effigy_bridge / clock_divider / aux_outputs / strip_display / usbmidi modules. BOM acquired (CD4024 dropped — clock division is firmware now). Stripboard layouts generated. Touch test board designed (8 circuit bends, pending bench-test selection). **Phase 0 bench validation is the next step — no physical build started yet.**

### Confirmed Decisions (April 2026, last reconciled 2026-04-26)

| Decision | Detail |
|----------|--------|
| Expander HP | **17HP** (87mm × 128.5mm panel — fits user's pre-cut blank) |
| Connector | **2× shielded DB-9** (no aux cable; DB-9 B carries digital + power + 2 essential CVs) |
| Pico location | Inside the 17HP expander (not the MicroBrute case) |
| OLED (primary) | **0.96" SSD1306** I²C on GP4/GP5 @ 0x3C — on the expander panel. Driver: `OLED_I2C` in `firmware/pico/display.py`. Same chip family as strip OLED. |
| OLED (strip) | **0.91" SSD1306 128×32** @ 0x3D on the MicroBrute panel — shared I²C0 bus via DB-9 B |
| OLED (fallbacks) | 1.3" SH1106 (set `OLED_CHIP="SH1106"` + `OLED_COL_OFFSET=2` — reserved for EFFIGY); 16×2 1602 I²C LCD (separate driver) |
| MIDI paths | (a) Pico ↔ LPC2361 UART bridge over DB-9 B @ 115200 baud, XOR-checksummed frame; (b) Pico USB-MIDI via micro-USB (TinyUSB MIDI class) |
| EFFIGY pair bus | 5-pin JST-XH rear header (SDA/SCL/INT/3V3/GND), I²C @ 100 kHz, target addr 0x42 — see `docs/MACROBRUTE_EFFIGY_BRIDGE.md` |
| Hardware utilities | **Slew limiter only** (TL072 + 2 diodes + pot). All others dropped. |
| Firmware utilities | Clock divider (3 outputs, GP16/17/18), 4 programmable aux outputs (GP19/20/6/7) — replaces planned CD4024 |
| RGB LED | Common-cathode on GP8/9/10 — R=clock tick, G=gate, B=mode/pair |
| Touch mods | 8 body-contact bends designed; bench-test in Phase 0 → pick 6 |
| JF-33 delay | **Separate Eurorack module (Phase 7A, optional)** — not inside expander |
| DSO138 scope | **Separate Eurorack module (Phase 7B, optional)** — LM7809 on hand for +9V regulation |
| EFFIGY DSP | **Separate Eurorack module (Phase 7C, optional)** — Daisy Seed peer, paired via I²C |
| PSU | **Behringer CP1A** Eurorack PSU (±12V + 5V on bus). Pico fed from +5V via 3-part filter (1N5817 + 100µF + 100nF). MicroBrute stock power untouched. |
| Migrated to MB panel | Resonance CV (new jack); reuse MB's existing back-panel Sync In / Gate In / Audio In |

---

## Phase 0: Bench Validation — non-destructive (Week 1)

**Goal:** Validate Pico firmware on breadboard, confirm OLED choice, locate test points.

### Tasks
- [ ] Flash Pico firmware (`tools/flash_pico.sh`). Run `test_hw.py` first for per-peripheral diagnostics.
- [ ] Confirm 1.3" SH1106 draws correctly. If artifacts: toggle `OLED_COL_OFFSET` (2↔0) or fall back to 0.96" SSD1306. LCD fallback requires a separate driver — defer unless both OLEDs fail.
- [ ] Breadboard integration: OLED + encoder + RGB LED + clock I/O + tap button
- [ ] MicroBrute inspection: locate TPs, measure panel gaps, photograph PCBs — **DONE** (teardown photos taken)
- [ ] LPC2361 ISP pin survey (visual only — locate P0.2, P0.3, P2.10 on PCB)
- [ ] Verify PL2303HX USB-TTL with serial loopback

### Toolchain Setup (macOS)
```
brew install lpc21isp             # already installed
brew install --cask ghidra        # installed: Ghidra 12.0.4
pip3 install pyserial mpremote
brew install arm-none-eabi-gcc    # installed: 15.2.0
```

### Test Checkpoint (Phase 0)
- [ ] Pico boots, OLED displays, encoder rotates, RGB LED cycles colors
- [ ] Serial port functional, toolchains installed
- [ ] TP locations mapped on MicroBrute PCB photos
- **Gate:** All firmware modules run on breadboard, TP locations mapped

---

### Component Orders (reference — BOM acquired)

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

## Phase 1: Breakout Board Build (Week 2-3)

**Goal:** Build breakout PCB on stripboard, verify all buffer channels and VCO.
**Layout:** `schematics/breakout_layout.svg` (generated from `tools/generate_layouts.py`)

### Tasks
- [ ] Cut tracks, solder DIP sockets (U1 TL074, U2 TL072, U3 CD40106)
- [ ] Power section: D1/D2/D3 (1N5817), FB1/FB2 (ferrite beads), bulk caps. Test rails under load.
- [ ] Insert ICs, decoupling caps, feedback jumpers, bias resistors
- [ ] Test each buffer channel with audio source (4× TL074 unity-gain followers)
- [ ] RGB LED driver: Q1 NPN for common cathode, R/G/B on GP8/9/10 via 3× resistors
- [ ] VCO circuit (CD40106 gate B): square + triangle outputs on DB-9 A pins 2 and 9
- [ ] CD4049UBE level shifter: 1 gate for gate mirror signal (5V→3.3V to Pico)
- [ ] Connector headers (J_PICO, J_OUT, J_IN)
- [ ] Bench test with Pico connected via J_PICO header

### Test Checkpoint
- [ ] All 4 buffer channels pass signal (play audio → measure output)
- [ ] VCO oscillates (square + triangle visible on scope)
- [ ] RGB LED responds to Pico (red=clock, green=gate, blue=mode, mixed colors)
- [ ] Gate mirror: CD40106 5V → CD4049UBE → 3.3V clean signal at Pico GPIO
- **Gate:** All buffer channels pass signal, VCO oscillates, LEDs respond

**STOP if any buffer channel fails — debug before proceeding.**

---

## Phase 1B: Touch Test Board Build (parallel with Phase 1)

**Goal:** Test all 8 circuit bends non-destructively before permanent installation.
**Layout:** `schematics/touch_test_board.svg` (generated from `tools/generate_layouts.py`)
**Specs:** `docs/mods/touch_bend_specs.md`

### Tasks
- [ ] Build 10×10 stripboard test board (8 channels)
- [ ] Wire 8 clip leads to MicroBrute PCB points:

| CH | Name | PCB Point | Safety R |
|----|------|-----------|----------|
| 1 | Pitch Shimmer | R309 area (near blue trimmers) | 10kΩ |
| 2 | Metalizer Crunch | C111 (wavefolder stage 3) | 4.7kΩ |
| 3 | Filter Wah | Filter CV input area (Steiner-Parker) | 22kΩ |
| 4 | Brute Distortion | Feedback path (Brute Factor) | 15kΩ |
| 5 | Envelope Decay | ADSR decay timing cap area | 33kΩ |
| 6 | Dual Harmonic Morph | C107 + C106 (wavefolder stages 1 & 2) | 10kΩ each |
| 7 | LFO Speed Throb | LFO timing resistor network | 47kΩ |
| 8 | Metalizer Feedback Gate | Metalizer output to input (series) | 1kΩ |

- [ ] Probe each touch bolt: dry fingers at 50% pressure, then full pressure
- [ ] Repeat with slightly damp fingers to map moisture sensitivity
- [ ] Record 10s audio clip per bend (baseline + touch effect)
- [ ] Rate musical usefulness vs stability/predictability
- [ ] Select top 6 for permanent panel installation

### Test Checkpoint
- [ ] 6+ bends produce musically useful, controllable results
- [ ] Safety resistors prevent damage at any touch pressure
- [ ] Higher-risk mods (4, 6, 8) stable with dry fingers
- **Gate:** 6+ bends produce musically useful results, top 6 selected for panel

---

## Phase 2: Internal Wiring (Week 3-5)

**Goal:** Wire all test points to breakout board, verify signals.
**Risk: HIGH** — soldering to MicroBrute PCB. Use 350°C iron, <2s per joint.

### 2.1 Wire Test Points (flying leads, 24AWG)
| Source | Series R | Destination |
|--------|----------|-------------|
| TP94 (Saw) | 1kΩ | TL074A +in |
| TP93 (Square) | 1kΩ | TL074B +in |
| TP30_MIXER_OUT (VCO Mix) | 1kΩ | TL074C +in |
| TP19 (VCF Out) | 1kΩ | TL074D +in |
| TP124 (Triangle) | 1kΩ | TL072 D +in (2x gain) |
| TP83 (Gate) | 10kΩ | CD40106 pin 1 |
| Env (mod matrix) | 10kΩ | TL072 A +in |
| LFO (mod matrix) | 10kΩ | TL072 B +in |

### 2.2 Wire Power Taps
- [ ] Solder to TP70 (+12V), TP71 (-12V), TP72 (GND)
- [ ] Mount breakout board on chassis wall (VHB tape or M2 standoffs)
- [ ] Mount Pico WH on/adjacent to breakout board
- [ ] Route wires along chassis ribs, secure with nylon ties
- [ ] Verify keyboard and wheels still move freely

### 2.3 Wire DB-9 A (outputs) — loose, not mounted yet
Buffer outputs → 1kΩ → DB-9 A pins per `schematics/wiring_diagram.md`

### 2.4 Build Vactrol
LED + LDR in sealed heat shrink. Test on breadboard first. Wire to TL072 C driver. LDR parallels RP13.

### Test Checkpoint
- [ ] All buffer outputs measurable with multimeter (play a note, see voltage swing)
- [ ] Gate output: 0V silent, 5V when key pressed
- [ ] DB-9 A pins show correct signals (continuity test)
- [ ] No shorts, no hum, Pico still boots
- **Gate:** Signal flows from MicroBrute TPs through breakout to J_OUT headers

---

## Phase 3: Panel Modifications — irreversible (Week 5-7)

**Goal:** Drill MicroBrute panel, mount OLED/encoder/RGB LED/touch bolts/DB-9.
**Template:** `panel/microbrute_panel_template.svg`
**Risk: MEDIUM** — drilling is irreversible. Practice on scrap first.

### Tasks
- [ ] Print 1:1 drilling template, tape to panel, verify clearances
- [ ] **Practice** on scrap material: OLED cutout (33×17mm), 7mm encoder, 5mm LED
- [ ] OLED: trim module PCB with Dremel (~32×25mm), cut 33×17mm panel window
- [ ] Encoder: 7mm hole, 10mm right of OLED window
- [ ] RGB LED: 1× 5mm hole (replaces 3 separate LEDs, saves 2 panel holes)
- [ ] Touch bolts: 6× 6mm holes for brass M3 bolts (selected from Phase 1B testing)
  - Spacing: 18-20mm horizontal between bolts to avoid accidental multi-touch
  - Labels: PITCH, CRUNCH, WAH, DISTORT, HARMONIC, GATE
- [ ] Wire touch bolts with safety resistors to PCB points (permanent solder)
- [ ] DB-9: 2× cutouts on rear panel flanks, solder-cup connectors
- [ ] Wire DB-9 A (9 outputs) and DB-9 B (9 inputs+power) to breakout headers
- [ ] Interior cable routing, strain relief

### Test Checkpoint
- [ ] OLED visible through cutout, displays correctly
- [ ] Encoder functional after panel installation
- [ ] RGB LED visible, color mixing works
- [ ] Touch bolts modify sound when touched (verify against Phase 1B results)
- [ ] DB-9 connectors secure, no pin shorts
- **Gate:** OLED displays through panel, encoder works, touch bolts modify sound, DB-9 signals measure correct

---

## Phase 4: Expander Build (Week 6-10, parallel with Phase 3)

**Goal:** Build all utility circuits, mount in 42HP panel, integrate via DB-9.
**Schematics:** `schematics/expander_circuits.md`, `kicad/expander/`

### Build Order (easiest → hardest, get sound early)

| Order | Circuit | ICs | Test Signal |
|-------|---------|-----|-------------|
| 1 | Buffered mult (1→3) | TL074 (or reuse Bastl passive mult) | Apply CV, verify 3 copies |
| 2 | Noise generator | 2N3904 avalanche + TL072 | Listen for white noise |
| 3 | LFO (tri + square) | TL072 | Scope: 0.04-40Hz waveforms |
| 4 | Clock divider (/2/4/8) | CD4024 + 78L05 | Feed clock, verify divisions |
| 5 | Sample & Hold | LF398 + CD4051 (1nF polystyrene cap) | Feed noise + clock, see staircase |
| 6 | Slew limiter | TL072 + 1N4148 diodes | Step input → smooth ramp |
| 7 | Attenuverter (2ch) | TL072 | Invert/scale CV |
| 8 | Manual gate button | Pushbutton + CD40106 | Press → 5V gate |

### Panel & Assembly
- [ ] Drill 42HP panel per `panel/expander_42hp.svg`
- [ ] Mount ~30 jacks, 8 pots, LEDs
- [ ] Wire Eurorack power (16-pin header → ±12V/GND)
- [ ] Wire DB-9 interconnect cable (2× DB-9, 18 conductors, <1m shielded)

### Test Checkpoint
- [ ] Each circuit works standalone on bench supply
- [ ] DB-9 cable passes all signals (continuity on 18 pins)
- [ ] Expander utilities modulate MicroBrute when connected
- **Gate:** Each module outputs correct signal on bench

---

## Phase 5: System Integration (Week 10-12)

**Goal:** Full system test — MicroBrute + breakout + Pico + expander, all connected.

### Integration Tests
- [ ] Connect expander via DB-9 shielded cables
- [ ] End-to-end signal flow: MB note → expander jack → oscilloscope
- [ ] CV injection: expander LFO → DB-9 B → filter cutoff sweeps
- [ ] Resonance CV: expander CV → vactrol → resonance sweeps
- [ ] Clock: Pico clock output → expander clock divider → /2/4/8
- [ ] Touch bolts: verify all 6 panel bolts still function after permanent install
- [ ] MIDI: Pico SysEx → MB parameter change (bend range, gate length)

### Ground Loop Audit
- [ ] Measure DC offset between MB and expander GND
- [ ] Listen for hum with headphones at max gain
- [ ] If hum: add 100nF ceramic cap in series with DB-9 GND pin
- [ ] Verify star ground at TP72
- [ ] DB-9 GND must be the ONLY ground connection between systems
- [ ] Do NOT connect Eurorack chassis ground to MicroBrute chassis
- [ ] Salvaged isolation transformer available for critical paths if needed

### Pico Firmware Polish
- [ ] Save/load preferences to flash (BPM, sync mode)
- [ ] Screensaver timeout (120s)
- [ ] Boot RGB LED test sequence (already in `leds.py`)
- [ ] Error handling for disconnected peripherals

### Test Checkpoint
- [ ] Full signal chain verified with oscilloscope or multimeter
- [ ] No ground loops, hum, or noise
- [ ] Pico menu fully operational, values persist across reboot
- [ ] All 18 DB-9 signals verified
- **Gate:** Full system operational, clean audio, no ground hum

---

## Phase 6A: LPC2361 ISP Setup (Week 12+)

**Goal:** Physical connection to LPC2361 for firmware development.
**Status:** Firmware RE ~98% complete via .mbf decryption path. ISP is for verification + future custom firmware.

### Completed (via .mbf decryption)
- [x] Cracked .mbf XOR cipher (key: `ArturiaminiBruteFirmware`, start index 4)
- [x] Extracted Intel HEX → 52.6KB ARM binary (v1.0.4.114)
- [x] Ghidra project: 427 functions, 107+ labels, 43 SysEx commands mapped
- [x] MIDI dispatcher, DAC pipeline, NRPN protocol, sequencer timing all documented
- [x] UART0 (0xE000C000): only 1 reference — safe for Pico bridge
- [x] 68.6KB free flash available for custom code

### Tasks
- [ ] Solder PL2303HX wires to LPC2361 UART0 pads (P0.2 TX, P0.3 RX)
- [ ] Identify P2.10 (ISP enable) — jumper to GND for bootloader entry
- [ ] Power cycle with P2.10 LOW, run: `lpc21isp -detectonly`
- [ ] Check CRP level (likely CRP3 = locked → use .mbf decryption path instead)
- **Gate:** Part ID detected OR CRP status confirmed

---

## Phase 6B: Ghidra Deep Analysis (parallel)

**Goal:** Complete remaining ~2% of firmware RE.

### Tasks
- [ ] Map remaining functions: parameter storage, calibration table format
- [ ] Trace UART0 initialization for Pico bridge compatibility
- [ ] Identify unused interrupt vectors for custom code injection
- [ ] MIDI traffic capture to confirm inferred parameter names
- [ ] Document findings in `docs/research/mbf_analysis.md`
- **Gate:** Key functions documented, UART bridge path clear

---

## Phase 6C: Pico ↔ LPC2361 UART Bridge

**Goal:** Bidirectional communication between Pico and MicroBrute CPU.

### Tasks
- [ ] Wire Pico GP0/GP1 to LPC2361 P0.2/P0.3
- [ ] Level shift: CD4049UBE gate for LPC 5V → Pico 3.3V (or 1kΩ+2kΩ divider)
- [ ] Custom LPC2361 code: init UART0 at 115200, accept queries from Pico
- [ ] Pico firmware: query internal state, display on OLED
- [ ] Eventually: preset recall, live parameter control from OLED menu
- **Gate:** Pico queries LPC2361, receives valid responses

---

## Phase 7: Advanced / Optional

### 7A: JF-33 Delay CV Integration
Build per `schematics/jf33_cv_control.md`:
- [ ] Anti-latch-up circuit (BC337 + RC, **build first**)
- [ ] Delay time CV (TL072 → 2N3904 current sink, 1kΩ emitter R)
- [ ] Eurorack level matching (input atten + output gain)

### 7B: DSO138 Oscilloscope — standalone Eurorack module (optional)
Build per `schematics/dso138_input_protection.md` as a **separate Eurorack module**, not inside the 42HP expander:
- [ ] Input protection (BAT54S clamps + 1kΩ series R)
- [ ] CD4051 signal multiplexer (8:1), channels: Saw, Square, VCO Mix, VCF, Gate, Envelope, LFO, External
- [ ] LM7809 power from +12V (on hand) — regulate to DSO138's +9V input
- [ ] 10HP panel: LCD display, input jack, channel select (rotary or 3-bit from Pico), probe clip
- [ ] Optional DLO-138 firmware (adds serial export)
- **Why separate:** Display needs its own panel real estate; better as a utility module than crammed into the MB panel or expander.

### 7C: Additional Touch Plates via Pico ADC
- [ ] Extend 6 panel bolts with Pico ADC (GP26-28) for CV output
- [ ] CD4051 multiplexed scanning (reuse DSO mux)
- [ ] PWM → RC filter → CV output

### 7D: Circuit Bending Switches
Per `docs/mods/deep_circuit_bending.md`:
- [ ] Brute Factor bypass toggle
- [ ] VCA drone toggle (+12V → 100kΩ → TP10)
- [ ] Power rail sag (10Ω series + 8.2V Zener clamp)
- [ ] Metalizer feedback loop (100kΩ pot)

### 7E: Custom LPC2361 Firmware
- [ ] Extended SysEx command set
- [ ] Parameter persistence (flash writes — currently volatile SRAM only)
- [ ] Custom calibration tables

---

## Critical Path

```
Phase 0 (bench validation) ──► Phase 1 (breakout board)
                                    │
                    Phase 1B ◄──────┤ (parallel: touch test board)
                    (touch test)    │
                         │          ▼
                         │   Phase 2 (internal wiring)
                         │          │
                         ▼          ▼
                    Touch results → Phase 3 (panel drilling — irreversible)
                                    │
                    Phase 4 ◄───────┘ (parallel: expander build)
                    (expander)      │
                         │          │
                         ▼          ▼
                    Phase 5 (system integration)
                         │
                         ▼
                    Phase 6A-C (LPC2361 firmware RE + bridge)
                         │
                         ▼
                    Phase 7 (advanced, optional)
```

**First sound: end of Phase 2 (~week 5)** — buffer outputs audible
**Full system: end of Phase 5 (~week 12)** — MB + expander integrated
**Custom firmware: Phase 6C** — Pico ↔ LPC2361 bridge operational

---

## Verification

After each phase, run the test checkpoints listed. The critical gates are:
- Phase 0: Pico + OLED + encoder all work on breadboard
- Phase 1: All buffer channels pass signal, VCO oscillates
- Phase 1B: 6+ touch bends produce musically useful results
- Phase 2: Buffer outputs measurable at DB-9 pins
- Phase 5: Full analog path verified, no hum, no ground loops

For firmware: `mpremote connect /dev/tty.usbmodem* run main.py` on Pico.
For LPC2361 (future): `make && ./tools/flash.sh build/macrobrute.hex`

---

## Key Reference Files

| Category | Files |
|----------|-------|
| Firmware (Pico) | `firmware/pico/` — 8 MicroPython modules |
| Firmware (LPC) | `firmware/lpc2361/` — 48 C files, ARM7 skeleton |
| Schematics | `schematics/` — 8 ASCII docs + 6 SVG stripboard layouts |
| KiCad | `kicad/` — 4 sub-projects (breakout, expander, jf33, dso_input) |
| Panel | `panel/` — 2 SVGs (MicroBrute panel + 42HP expander) |
| Touch mods | `docs/mods/touch_bend_specs.md` — 8 circuit bends with specs |
| Circuit review | `schematics/CIRCUIT_REVIEW.md` — all circuits reviewed and verified |
| RE analysis | `docs/research/mbf_analysis.md` — full firmware RE results |
| Tools | `tools/` — decrypt, encrypt, test suite (52 tests), Ghidra scripts |
