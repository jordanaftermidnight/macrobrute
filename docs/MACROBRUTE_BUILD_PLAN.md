# MACROBRUTE Comprehensive Build Plan

## Context

The MACROBRUTE project transforms an Arturia MicroBrute into a semi-modular instrument paired with a Eurorack expander. About 260 tracked files (263 on 2026-10-17): Pico MicroPython firmware (15 `.py` files: 14 modules plus the generated `_effigy_constants.py`), LPC2361 ARM7 C firmware skeleton (48 files), schematic docs (9 `.md`) and KiCad projects (breakout, expander), stripboard and diagram SVGs (83 SVGs repo-wide), panel SVGs, mod/bending guides, .mbf encryption cracked + firmware decrypted, and research docs.

**Current status (2026-10-17):** Design stage. This plan was reconciled against the project audit (`docs/superpowers/reviews/2026-10-16-project-audit.md`), the back-feed and hum design note (`docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md`, cited as "BF") and the connection map (`docs/MACROBRUTE_CONNECTION_MAP.md`, the authority for pins and wiring). The owner's own build plan comes after this redraft, so sections that still predate the decisions are marked **STALE** rather than redesigned. Firmware RE ~98% complete (43 SysEx commands, 107+ Ghidra labels). Pico firmware: `firmware/pico/config.py` is the canonical pin source. Stripboard layouts exist but several are stale (audit B16, S34). Touch test board designed (8 circuit bends, pending bench-test selection). **Phase 0 bench validation is the next step — no physical build started yet.**

### Confirmed Decisions (owner answers 2026-10-16 and 2026-10-17; reconciled 2026-10-17)

Source: audit sections 1a and 1b, BF, and `docs/MACROBRUTE_CONNECTION_MAP.md` (the authority). Anything not proven stays UNVERIFIED.

| Decision | Detail |
|----------|--------|
| Expander HP | **OPEN: 17 HP or about 20 HP.** The repo panel file `panel/expander_17hp.svg` is 87 mm wide with mounting holes 79 mm apart, both UNVERIFIED against the A-100 spec (audit S53, E-22). The owner measures the blank first; plan both layouts. Depth behind the panel UNVERIFIED (E-23). |
| Connector | **2× shielded DB-9** (HD-15/VGA rejected: the cable shorts pins 6-8 to GND; no DB-25). Both mount on the **MicroBrute rear panel, left of the Pitch/Gate section** (owner decision a). Panel dimensions, free area and depth UNVERIFIED until the owner measures (audit E-20, E-21). DB-9 A = outputs; DB-9 B = UART TX, UART RX, Filter CV, VCA CV and grounds only. Pin maps: CM sections 2 and 3 (from BF 2.2 and 2.3). |
| Power | **Split.** The expander is powered only from the rack (CP1A); the MicroBrute-side breakout only from the synth (TP70 +12 V, TP71 -12 V, TP72 GND). **No supply rail crosses the DB-9 cable; only ground is shared.** |
| Pico location | Inside the expander (not the MicroBrute case). Pico variant: the docs say Pico WH; UNVERIFIED, owner to confirm (BF Q21). |
| OLED (primary) | **0.96" SSD1306** I²C on GP4/GP5 @ 0x3C — on the expander panel. Driver: `OLED_I2C` in `firmware/pico/display.py`. Size, controller and interface (I²C vs SPI) of the owned module UNVERIFIED, owner to confirm (BF Q22). |
| OLED (strip) | **DROPPED** (owner decision c). I²C0 serves only the main OLED, on the expander. **No I²C crosses the DB-9 cable.** |
| OLED (fallbacks) | 1.3" SH1106 (set `OLED_CHIP="SH1106"` + `OLED_COL_OFFSET=2`); 16×2 1602 I²C LCD (separate driver). |
| MIDI paths | (a) Pico ↔ LPC2361 UART bridge over DB-9 B pins 1 and 6 @ 115200 baud, XOR-checksummed frame; LPC-side UART is **UART1 (P0.15/P0.16, pins 62/63), UNVERIFIED** until the Phase 0 continuity check; (b) Pico USB-MIDI via micro-USB (TinyUSB MIDI class), not used while the DB-9 cables are connected (BF 4.3). |
| EFFIGY pair bus | **SHELVED** (owner decision b): kept as an idea for another project; nothing is designed around it. GP2, GP3, GP11 are free, reserved. |
| Hardware utilities | **Slew limiter, LFO, Sample & Hold** (standalone rack utilities, rack power only, no synth cabling). Noise, mult and attenuverter stay out. S&H uses an LF398 (not owned) and a film hold capacitor (not owned). |
| Firmware utilities | Clock divider (3 outputs, GP16/17/18), 4 programmable aux outputs (GP19/20/6/7) — replaces the dropped CD4024. Clock I/O on the expander only. |
| RGB LED | Common-cathode on GP8/9/10 — R=clock tick, G=gate, B=mode (the old "pair" meaning is shelved). On the expander. |
| Touch mods | 8 body-contact bends designed; bench-test in Phase 0 → pick 6 |
| JF-33 delay | **Moved to `spinoffs/jf33-eurorack/`** — DIY PT2399 delay; not part of the canonical MACROBRUTE build |
| DSO138 scope | **Moved to `spinoffs/dso138-desktop/`** — desktop scope; not a Eurorack module |
| EFFIGY DSP | **SHELVED** (see above). `docs/MACROBRUTE_EFFIGY_BRIDGE.md` and `firmware/pico/effigy_bridge.py` are archived as an idea. |
| Norns Shield | **Anticipated only, not designed.** See `docs/MACROBRUTE_NORNS_BRIDGE.md`; its EFFIGY half is shelved and no I²C pins are reserved for it. |
| PSU | **Behringer CP1A** Eurorack PSU: -12 V @ 1 A (pins 1-2), +12 V @ 1 A (pins 9-10), +5 V @ 0.5 A (pins 11-12), GND pins 3-8, pins 13-16 not used (CP1A QSG p15, p20). Whether the owner's bus slot carries +5 V: UNVERIFIED (BF BT-12). Pico VSYS takes rack +5 V through a Schottky OR diode + bulk + 100 nF; the 1N5817 is a 20 V part and is not owned (an owned BAT85 can stand in, BF 1.2). MicroBrute stock power untouched. |
| Migrated to MB panel | Resonance CV (new jack); reuse MB's existing back-panel Sync In / Gate In / Audio In |
| Owned parts | Every circuit uses parts marked Have in `docs/hardware/MACROBRUTE_BOM.md`; anything else is flagged with an owned alternative (BF section 1). |

---

> **Badge legend:** each phase heading shows its state and reversibility.
> [[VERIFIED]] built and tested on this rig · [[UNTESTED]] designed, not
> yet built · [[DRAFT]] still in design.
> [[REVERSIBLE]] no irreversible changes to the synth ·
> [[DESTRUCTIVE]] involves panel cuts or trace cuts — plan accordingly.

---

## Phase 0: Bench Validation — non-destructive (Week 1) [[UNTESTED]] [[REVERSIBLE]]

**Goal:** Validate Pico firmware on breadboard, confirm the OLED module (size, controller, interface: owner to confirm, BF Q22), locate test points, and pass the gate checks on the MicroBrute that later phases depend on (LPC UART pins, TP83 level, synth rail margin, DB-9 geometry). Full procedures: `docs/hardware/MACROBRUTE_PHASE0_BOM.md`.

### Wiring reference
The breadboard layout for Phase 0 lives in `schematics/pico_pinout.md` and is rendered as two diagrams:

- **`phase0_wiring_schematic.svg`** — flat schematic, elbow-routed nets, useful for understanding what connects to what.
- **`phase0_breadboard.svg`** — top-down breadboard view, jumper paths colour-coded by net (red=+3V3, dark=GND, blue=I²C0, green=GPIO, orange=RGB drive, purple=clock).

Both match `firmware/pico/config.py` exactly, except that the strip OLED may still be drawn in the diagrams: it is **dropped** (ignore it; the diagrams are redrawn later). Pin map covered: **one OLED on I²C0**, GP4/GP5 — the 0.96″ SSD1306 main display at `0x3C` (later mounted on the expander panel). KY-040 encoder on GP14/GP15/GP13 (firmware enables `Pin.PULL_UP` on all three), tap button on GP12 (active-LOW, `Pin.PULL_UP`), RGB LED (common cathode) R/G/B on GP8/GP9/GP10 via 220 Ω, clock OUT on GP22, clock IN on GP21 (`Pin.PULL_DOWN`, IRQ on rising edge).

### Tasks
- [ ] Flash Pico firmware (`tools/flash_pico.sh`). Run `test_hw.py` first for per-peripheral diagnostics — should detect the main OLED at `0x3C`. (`test_hw.py` also accepts `0x3D`; ignore that, the strip OLED is dropped.)
- [ ] Confirm the main OLED draws its boot splash. If a display is blank: check SDA/SCL not swapped, then VCC vs GND polarity. A 7-pin module is SPI, not I²C (BF Q22): stop and tell the owner, the driver and pins change.
- [ ] Breadboard integration per the diagrams above: OLED + KY-040 encoder + tap button + RGB LED + clock IN/OUT
- [ ] Self-loopback test: jumper GP22 → 1 kΩ → GP21 to confirm the firmware clock generator and IRQ-driven clock-in count match
- [ ] MicroBrute inspection: locate TPs, measure panel gaps, photograph PCBs — **DONE** (teardown photos taken)
- [ ] LPC2361 ISP pin survey (visual only — locate P0.2, P0.3, P2.10 on PCB). This feeds the UART continuity gate below
- [ ] Verify PL2303HX USB-TTL with serial loopback

### Phase 0 gate checks on the MicroBrute (probe only, no soldering)
Full procedures, pass criteria and the owner's recording sheet: `docs/hardware/MACROBRUTE_PHASE0_BOM.md`. Each result is recorded before the phase that depends on it starts.
- [ ] **LPC UART continuity probe** (gate before any Phase 6 bridge work): LPC2361 LQFP-100 pins 62/63 (P0.15/P0.16), pins 98/99 (the ISP UART), and 6N138 output to pin 85 (P4.29, expected). Rear board CU17002, power off, continuity mode. Procedure from audit decision 7. Never probe pins 96/97 (VDD(3V3) and VSS)
- [ ] **TP83 logic level**: measure the high and low level of the gate test point (audit E-09). A 5 V CD40106 is only guaranteed to trigger above 3.6 V
- [ ] **Synth rail margin**: adapter label, TP70/TP71 against TP72, baseline for the Phase 2 loaded check (audit E-04)
- [ ] **D-sub neighbour geometry** (BF BT-7): caliper the owner's DB-9 insert and confirm the row offset and neighbour table
- [ ] Optional: CP1A +5 V on bus pins 11-12 (BF BT-12); PC817 isolated-UART alternative noted, not required (BF 3.9)
- [ ] Bench tests BT-1 to BT-13 are listed in the Phase 0 BOM file (names only; definitions and pass criteria in BF section 6.2). They run when the matching hardware exists, not all in Phase 0

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
- [ ] LPC UART continuity result, TP83 level, synth rail baseline and D-sub geometry recorded
- **Gate:** All firmware modules run on breadboard, TP locations mapped, and the four MicroBrute gate checks recorded. Only after the UART continuity check passes may any doc say a bridge UART is confirmed

---

### Component Orders (STALE reference — do not order from this section)

**STALE (2026-10-17):** the tables below predate the decisions above and the owned-parts inventory. They still list CD4024, 2N3904, BC337-class parts, 1N5817 as a 40 V part, ferrite beads, 100 µF parts, a 42 HP panel and similar items that the audit marks as dropped, wrong or not owned. The current sources are the Have/Missing columns in `docs/hardware/MACROBRUTE_BOM.md` and the missing-parts list in `docs/hardware/MACROBRUTE_SHOPPING_LIST.md` (from BF section 1).

**Batch 1 — ICs + Passives (TME/Mouser, ~€70-85, 3-5 days):**

*ICs:*
| Component | Qty | Package | Used In |
|-----------|-----|---------|---------|
| TL074CN | 4 | DIP-14 | Breakout (1), Expander (3) |
| TL072CP | 3 | DIP-8 | Breakout (1), Expander slew (1), spare (1) — JF-33/DSO moved to spinoffs |
| ~~CD4024BE~~ | — | DIP-14 | **Dropped** — clock division is firmware |
| CD4051BE | 1 | DIP-16 | DSO mux (shared with touch plates) |
| CD40106BE | 2 | DIP-14 | Breakout (1), Expander (1) |
| LF398N | 1 | DIP-8 | Expander (S&H) |
| 78L05 | 1 | TO-92 | Breakout-local +5 V for the CD40106 only (Provisional, BF 3.4); owned x4. The expander takes rack +5 V, not a 78L05 |
| ~~7809~~ | ~~2~~ | TO-220 | **Dropped** — moved to spinoffs (`jf33-eurorack`, `dso138-desktop`) |

*Semiconductors:*
| Component | Qty | Package | Used In |
|-----------|-----|---------|---------|
| 2N3904 | 5 | TO-92 | Breakout LEDs (3), vactrol driver (1), spare (1) |
| ~~BC337~~ | — | TO-92 | **Dropped** (was for JF-33 anti-latch-up — now in spinoffs) |
| 1N4148 | 8 | DO-35 | Pico filter (1), slew steering (2), gate buffer (1), spare (4) |
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
| 100µF | 3 | Electrolytic 25V | Breakout (2), Pico power filter (1) |

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
| 100kΩ linear pot (9mm) | 4 | Expander attenuators (4) |
| 1MΩ log pot (9mm) | 3 | LFO rate, S&H rate, slew rate |
| Knobs (19mm, aluminum) | 12 | For all pots |
| Expander blank panel (width OPEN: 17 HP or about 20 HP) | 1 | Anodized aluminum |

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

## Phase 1: Breakout Board Build (Week 2-3) [[UNTESTED]] [[REVERSIBLE]]

**Goal:** Build the buffer-only breakout board on stripboard and verify all buffer channels. The Pico, RGB LED and its drivers live on the expander, not on this board (CM section 9, audit S12).
**Layout:** `schematics/breakout_layout.svg` (generated from `tools/generate_layouts.py`). **STALE:** this layout and `schematics/breakout_stripboard.md` still hold the old Pico/J_PICO/VSYS/Q1-Q3 design and have template defects (audit B16, S34); do not build from them until regenerated. The IC list and headers in CM section 9 are the reference.

### Tasks
- [ ] Cut tracks, solder DIP sockets (U1 TL074, U2 TL072, U3 CD40106)
- [ ] Power section, fed only from TP70/TP71/TP72 (no Pico, no VSYS): rail protection per CM 5.3 (open choice, audit C12: an owned BAT85 per rail or a 4.7-10 Ω series resistor), bulk from 2-4× owned 10 µF/63 V in parallel per rail, no ferrite beads. If a diode is used on -12 V its **cathode goes to the TP71 / -12 V side and its anode to the breakout rail** (audit B15). Test rails under load.
- [ ] Insert ICs, decoupling caps, feedback jumpers, bias resistors
- [ ] Test each buffer channel with audio source (4× TL074 unity-gain followers)
- [ ] Gate stage: CD40106, TP83 → 10 kΩ → pin 1 with 1 nF to GND, no pull-up, two gates in series so A:1 follows TP83 polarity, then 1 kΩ to DB-9 A:1; unused inputs tied to GND. Local +5 V from an owned 78L05 off +12V_BRK. Provisional (BF 3.4); TP83 level UNVERIFIED (E-09). The Square output is DB-9 A:8 from a TL074 follower; the triangle is not on the DB-9 (body jack, CM 12A).
- [ ] No RGB LED driver, no VCO circuit and no CD4049 level shifter on this board. The gate reaches the Pico through a 22k/33k divider on the expander (BF 3.5).
- [ ] Connector headers (J_PWR, J_IN, J_OUT, J_CV_IN per CM section 9)
- [ ] Bench test the breakout alone with a signal generator and a scope; the Pico is not connected to this board

### Test Checkpoint
- [ ] All 4 buffer channels pass signal (play audio → measure output)
- [ ] Gate stage follows a test square wave with the correct polarity; with TP83 at 3.3 V the CD40106 at 5 V may not trigger (VT+ up to 3.6 V, UNVERIFIED level), see BF Q15
- [ ] Rails measured with the board loaded (synth rail drop and current margin, audit E-04)
- **Gate:** All buffer channels pass signal and the gate stage behaves

**STOP if any buffer channel fails — debug before proceeding.**

---

## Phase 1B: Touch Test Board Build (parallel with Phase 1) [[UNTESTED]] [[REVERSIBLE]]

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

### 1C: Triangle Output Gain (M01 — Phase 1 add)
While the breakout PCB is open, change the TL074 D follower's feedback
network to give the triangle waveform 2× gain — restores level parity with
saw and square. Trivial mod (one resistor swap), full details in
`docs/mods/macrobrute_mod_catalog.md` § M01.

- [ ] Replace 16kΩ feedback R with 33kΩ (gain becomes ~2.06×)
- [ ] Verify triangle pp matches saw/square on a scope
- **Gate:** Triangle level within ±1 dB of saw/square at the DB-9 A jack

---

## Phase 2: Internal Wiring (Week 3-5) [[UNTESTED]] [[REVERSIBLE]]

**Goal:** Wire all test points to breakout board, verify signals.
**Risk: HIGH** — soldering to MicroBrute PCB. Use 350°C iron, <2s per joint.

### 2.1 Wire Test Points (flying leads, 24AWG)
| Source | Series R | Destination |
|--------|----------|-------------|
| TP94 (Saw) | 1kΩ | TL074A +in |
| TP93 (Square) | 1kΩ | TL074B +in |
| TP30_MIXER_OUT (VCO Mix) | 1kΩ | TL074C +in |
| TP19 (VCF Out) | 1kΩ | TL074D +in |
| TP124 (Triangle) | 1kΩ | TL072 +in (2x gain) → body jack, not the DB-9 (a TL072 has two sections: IC choice open, audit S17) |
| TP83 (Gate) | 10kΩ, 1 nF to GND, no pull-up | CD40106 pin 1 |
| Env (mod matrix) | 10kΩ | TL072 A +in |
| LFO (mod matrix) | 10kΩ | TL072 B +in |

### 2.2 Wire Power Taps
- [ ] Solder to TP70 (+12V), TP71 (-12V), TP72 (GND): the breakout takes power only from these. No synth 5 V or 3V3 is tapped (audit B09)
- [ ] Check the synth's +/-12 V margin with the breakout connected before wiring the DB-9 (audit E-04): rails within about 100 mV of unloaded, no extra ripple on TP70/TP71
- [ ] Mount breakout board on chassis wall (VHB tape or M2 standoffs). No Pico inside the MicroBrute
- [ ] Route wires along chassis ribs, secure with nylon ties
- [ ] Verify keyboard and wheels still move freely

### 2.3 Wire DB-9 A (outputs) — loose, not mounted yet
Buffer outputs → series R → DB-9 A pins per `docs/MACROBRUTE_CONNECTION_MAP.md` section 2 (`schematics/wiring_diagram.md` is STALE: it still routes ±12 V over DB-9 B pins 7/8, audit B03)

### 2.4 Build Vactrol
LED + LDR in sealed heat shrink. Test on breadboard first. Wire to TL072 C driver. LDR parallels RP13.

### Test Checkpoint
- [ ] All buffer outputs measurable with multimeter (play a note, see voltage swing)
- [ ] Gate output: low when silent, high when a key is pressed (high level UNVERIFIED, E-09)
- [ ] DB-9 A pins show correct signals (continuity test)
- [ ] No shorts, no hum
- **Gate:** Signal flows from MicroBrute TPs through breakout to J_OUT headers

---

## Phase 3: Panel Modifications — irreversible (Week 5-7) [[UNTESTED]] [[DESTRUCTIVE]]

**Goal:** Drill the MicroBrute panels and mount the touch bolts, panel jacks/toggles and the 2× DB-9. The OLED, encoder, tap button and RGB LED are on the expander (Phase 4), not on the MicroBrute.
**Template:** `panel/microbrute_panel_template.svg` covers the top panel only. No rear-panel template exists; draw one after the owner's caliper measurements (audit decision 6).
**Risk: MEDIUM** — drilling is irreversible. Practice on scrap first.

### Tasks
- [ ] Print 1:1 drilling template, tape to panel, verify clearances
- [ ] **Practice** on scrap material: jack holes, toggle holes, touch-bolt holes, and the DB-9 cut-outs
- [ ] Touch bolts: 6× 6mm holes for brass M3 bolts (selected from Phase 1B testing)
  - Spacing: 18-20mm horizontal between bolts to avoid accidental multi-touch
  - Labels: PITCH, CRUNCH, WAH, DISTORT, HARMONIC, GATE
- [ ] Wire touch bolts with safety resistors to PCB points (permanent solder)
- [ ] DB-9: 2× cutouts on the **rear panel, left of the Pitch/Gate section** (where the Arturia "A" logo is), solder-cup connectors. All dimensions UNVERIFIED until measured (audit E-20, E-21); mounting-hole spacing 24.99 mm per the Spectrum Control drawing, owner's part unconfirmed. Shells to TP72 with a short lead at this end only; braid bonded here (CM section 11)
- [ ] Wire DB-9 A (8 signals + GND) and DB-9 B (UART TX/RX, Filter CV, VCA CV, grounds; no supply, no I²C) to the breakout headers per CM sections 2 and 3. The UART wires are installed here but unused until Phase 6C (audit N17)
- [ ] Interior cable routing, strain relief

### Test Checkpoint
- [ ] Touch bolts modify sound when touched (verify against Phase 1B results)
- [ ] DB-9 connectors secure, no pin shorts
- **Gate:** touch bolts modify sound, DB-9 signals measure correct

### 3.X: Phase 2 mod additions

While the MicroBrute case is open, add the 13 Phase 2 mods documented in
`docs/mods/macrobrute_mod_catalog.md` (M02–M14). Recommended sequence
(safest → most invasive):

| Build group | Mods | Notes |
|-------------|------|-------|
| **Safe injects (no PCB cuts)** | M06 PWM CV, M09 PWM self-mod normalled, M03 sine extract, M11 9th touch bolt, M14 safe bias starve | All tap high-Z nodes; only solder leads |
| **Toggles** | M05 selfosc kill, M07 pitch starve, M10 brute extreme, M13 sync→env, M08 sub-harmonic enable | SPDT/SPST in series with existing nets |
| **Breadboard then install** | M02 active soft sync, M12 ARG audio-rate gate | Both use LM393 — bench-test stability before committing |
| **Most invasive** | M04 metalizer VCA (LM13700), M08 sub-harmonic divider (74HC74) | Both need a small stripboard sub-PCB; cuts/inserts in audio path |

Per-mod parts list and wiring detail: `docs/mods/macrobrute_mod_catalog.md`.

**Gate:** all Phase 2 mods bench-tested, then panel-installed; sound check
on every mod; no regressions to Phase 1/3 baseline.

---

## Phase 4: Expander Build (Week 6-10, parallel with Phase 3) [[UNTESTED]] [[REVERSIBLE]]

**Goal:** Build the expander: Pico, display and controls, clock I/O, firmware dividers and aux outputs, and the analog utilities (slew limiter, LFO, Sample & Hold); mount in the Eurorack panel and link to the MicroBrute through the 2× DB-9. Width OPEN: 17 HP or about 20 HP.
**Schematics:** `schematics/expander_circuits.md`, `kicad/expander/`. **STALE:** both still describe the old scope (noise, attenuverter, mult, CD4024, 42 HP; audit S58, S59). The decided scope is in CM section 10.

### Build Order (easiest → hardest, get sound early)

| Order | Circuit | ICs | Test Signal |
|-------|---------|-----|-------------|
| 1 | Pico, display, encoder, tap button, RGB LED | Pico + SSD1306 (see Phase 0) | Firmware runs from the rack +5 V (VSYS via the Schottky OR diode, BF 1.2) |
| 2 | Clock I/O buffers | CD4049UBE (owned x3) on Pico 3V3 | BF BT-11: GP21 stays within 0-3.3 V |
| 3 | Firmware dividers and aux outputs | none (GP16/17/18, GP19/20/6/7) | Scope the 3 divider and 4 aux outputs |
| 4 | Slew limiter | TL072 + 1N4148 diodes (1N4148 not owned, BF Q4) | Step input → smooth ramp |
| 5 | LFO (tri + square) | TL072 + CD40106 | Scope. Range about 0.5-50 Hz with 1 MΩ / 1 µF (derived, UNVERIFIED, audit S60, E-27); 10 kΩ integrator series R is mandatory |
| 6 | Sample & Hold | LF398 (not owned) + 10 nF film hold cap (not owned) + TL072 buffer | Pinout and droop: DATASHEETS (a). Trigger conditioning required (audit S65), design open |

### Panel & Assembly
- [ ] Drill the panel per `panel/expander_17hp.svg` (87 mm file, UNVERIFIED) or a 20 HP layout still to be drawn; no LFO or S&H controls are on the panel file yet (audit S54)
- [ ] Mount at least 16 jacks and 2 pots, the OLED, encoder, tap button and RGB LED (audit S52)
- [ ] Wire Eurorack power (16-pin keyed header: -12 V pins 1-2, GND 3-8, +12 V 9-10, +5 V 11-12; red stripe on pin 1). Powers the expander only
- [ ] Wire the DB-9 interconnect: two shielded 9-conductor cables (not ribbon), 1 m working maximum (UNVERIFIED until BF BT-6, BT-1), braid bonded at the MicroBrute end only, expander-side shells isolated from the panel with insulating washers (BF 4.2)

### Test Checkpoint
- [ ] Each circuit works standalone on bench supply
- [ ] DB-9 cables pass all conductors (continuity per CM sections 2 and 3: A = 8 signals + GND; B = UART x2, 2 CVs, 5 grounds)
- [ ] An expander CV output modulates the MicroBrute when connected (CV source circuit not yet chosen, BF 3.3)
- **Gate:** Each module outputs correct signal on bench

---

## Phase 5: System Integration (Week 10-12) [[UNTESTED]] [[REVERSIBLE]]

**Goal:** Full system test — MicroBrute + breakout + Pico + expander, all connected.

### Integration Tests
- [ ] Connect expander via DB-9 shielded cables
- [ ] End-to-end signal flow: MB note → expander jack → oscilloscope
- [ ] CV injection: expander CV output → DB-9 B:5 → filter cutoff sweeps; B:3 → VCA. Check the depth (BF BT-4). The LFO and S&H are rack-only and are patched by jack, not over the cable
- [ ] Resonance CV: patch a CV into the new MicroBrute-panel Resonance jack → vactrol → resonance sweeps (no cable pin)
- [ ] Clock: Pico clock output → firmware dividers → /2 /4 /8 on the expander jacks
- [ ] Touch bolts: verify all 6 panel bolts still function after permanent install
- [ ] MIDI: Pico SysEx → MB parameter change (bend range, gate length). Needs the Phase 6C bridge; USB-MIDI from the Pico is not used while the DB-9 cables are connected (BF 4.3)

### Ground Loop Audit
- [ ] Measure DC offset between MB and expander GND
- [ ] Listen for hum with headphones at max gain
- [ ] If hum: work the fallback ladder in CM section 11 / BF 4.5 (the old "100 nF in series with the DB-9 GND pin" fix is withdrawn: it removes the DC ground reference, audit S23)
- [ ] Verify star ground at TP72 and at the expander
- [ ] The DB-9 ground conductors (A:9; B:2, 4, 7, 8, 9) must be the ONLY ground connection between systems
- [ ] No USB cable on the Pico while the DB-9 cables are connected; flash and debug with them unplugged (BF 4.3)
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
- [ ] All DB-9 conductors verified by continuity; the two UART lines stay unused until Phase 6C
- **Gate:** Full system operational, clean audio, no ground hum

---

## Phase 6A: LPC2361 ISP Setup (Week 12+) [[DRAFT]] [[REVERSIBLE]]

**Goal:** Physical connection to LPC2361 for firmware development.
**Status:** Firmware RE ~98% complete via .mbf decryption path. ISP is for verification + future custom firmware.

### Completed (via .mbf decryption)
- [x] Cracked .mbf XOR cipher (key: `ArturiaminiBruteFirmware`, start index 4)
- [x] Extracted Intel HEX → 52.6KB ARM binary (v1.0.4.114)
- [x] Ghidra project: 427 functions, 107+ labels, 43 SysEx commands mapped
- [x] MIDI dispatcher, DAC pipeline, NRPN protocol, sequencer timing all documented
- [x] UART0 (0xE000C000): one reference in the disassembly, inside the UART3 RX error path. The earlier "safe for the Pico bridge" claim is **withdrawn** (UNVERIFIED): stock MIDI uses UART3 (0xE007C000, init at 0x3D88), UART0 is the ISP port, UART1/UART2 had no literal references (not exhaustive) (audit B01, S06)
- [x] 68.6KB free flash available for custom code

### Tasks
- [ ] Solder PL2303HX wires to LPC2361 UART0 pads (P0.2 TX = pin 98, P0.3 RX = pin 99; the "separate pads near the QFP" claim in `MACROBRUTE_TEST_POINTS_VERIFIED.md` is UNVERIFIED, audit S09). Not pins 96/97: those are VDD(3V3) and VSS
- [ ] Identify P2.10 (ISP enable) — jumper to GND for bootloader entry
- [ ] Power cycle with P2.10 LOW, run: `lpc21isp -detectonly`
- [ ] Check CRP level (likely CRP3 = locked → use .mbf decryption path instead)
- **Gate:** Part ID detected OR CRP status confirmed

---

## Phase 6B: Ghidra Deep Analysis (parallel) [[DRAFT]] [[REVERSIBLE]]

**Goal:** Complete remaining ~2% of firmware RE.

### Tasks
- [ ] Map remaining functions: parameter storage, calibration table format
- [ ] Trace the UART initialisation code (stock MIDI is UART3 per the disassembly) and confirm which UART is free for the Pico bridge (UART1 is the working assumption, UNVERIFIED)
- [ ] Identify unused interrupt vectors for custom code injection
- [ ] MIDI traffic capture to confirm inferred parameter names
- [ ] Document findings in `docs/research/mbf_analysis.md`
- **Gate:** Key functions documented, UART bridge path clear

---

## Phase 6C: Pico ↔ LPC2361 UART Bridge [[DRAFT]] [[REVERSIBLE]]

**Goal:** Bidirectional communication between Pico and MicroBrute CPU.

### Tasks
- [ ] Gate: the Phase 0 continuity check (UART pins 62/63 and 98/99, 6N138 output to pin 85) has passed and is recorded. Only then may the docs say a bridge UART is confirmed
- [ ] Wire Pico GP0/GP1 → DB-9 B:1 / B:6 with 1 kΩ at each end → LPC2361 UART1: P0.16/RXD1 (pin 63) and P0.15/TXD1 (pin 62), **UNVERIFIED** until the continuity check. Fall back to the ISP UART (pins 98/99) only if those pins are taken and the ISP conflict is handled
- [ ] No level shifter and no divider: both ends are 3.3 V (audit S30). Firmware rule: GP0 stays an input until GP1 has read high (BF 3.1). Bench checks BF BT-1 and BT-2; PC817-isolated alternative in BF 3.9
- [ ] Custom LPC2361 code: init the chosen UART at 115200, accept queries from Pico
- [ ] Pico firmware: query internal state, display on OLED
- [ ] Eventually: preset recall, live parameter control from OLED menu
- **Gate:** Pico queries LPC2361, receives valid responses

---

## Phase 7: Advanced / Optional [[DRAFT]]

### 7A: EFFIGY DSP module pair-up — SHELVED
Owner decision b (2026-10-17): the EFFIGY I²C pairing is shelved as an idea for
another project. No rear JST-XH header is fitted, GP2/GP3/GP11 are free, and
nothing is designed around it. `docs/MACROBRUTE_EFFIGY_BRIDGE.md`,
`firmware/pico/effigy_bridge.py` and `tools/sync_effigy_constants.py` are
archived as they are.

### 7B: Norns Shield ii bridge (anticipated, not designed)
Three-module chain Norns → MACROBRUTE → EFFIGY (the EFFIGY half is shelved, 7A). MACROBRUTE would host an
ii-compatible target on a separate front-of-rack I²C bus (suggested address
0x60). See `docs/MACROBRUTE_NORNS_BRIDGE.md` — covers translator command split,
ii address allocation, pull-up topology, hardware conflict (RP2040 has only
2 HW I²C peripherals — ii target needs PIO-based I²C on spare GPIOs).

### 7C: Additional touch plates via Pico ADC
- [ ] Extend the 6 selected panel bolts with Pico ADC (GP26–28) for CV output
- [ ] CD4051 multiplexed scanning if more than 3 channels needed
- [ ] PWM → RC filter → CV output (reuses the aux-output PWM machinery)

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
- Phase 1: All buffer channels pass signal, gate stage behaves
- Phase 1B: 6+ touch bends produce musically useful results
- Phase 2: Buffer outputs measurable at DB-9 pins
- Phase 5: Full analog path verified, no hum, no ground loops

For firmware: `mpremote connect /dev/tty.usbmodem* run main.py` on Pico.
For LPC2361 (future): `make && ./tools/flash.sh build/macrobrute.hex`

---

## Key Reference Files

| Category | Files |
|----------|-------|
| Firmware (Pico) | `firmware/pico/` — 15 `.py` files (14 modules + generated `_effigy_constants.py`); `config.py` is the canonical pin source |
| Firmware (LPC) | `firmware/lpc2361/` — 48 C files, ARM7 skeleton |
| Schematics | `schematics/` — 9 markdown docs + SVGs (83 SVGs repo-wide, 74 under `schematics/`); several are STALE until regenerated |
| KiCad | `kicad/` — 2 sub-projects (breakout, expander). JF-33 and DSO138 KiCad work moved to `spinoffs/`. |
| Panel | `panel/` — 4 SVGs (MicroBrute top-panel template, two finished-panel mockups, 17 HP expander file) |
| Touch mods | `docs/mods/touch_bend_specs.md` — 8 circuit bends with specs |
| Circuit review | `schematics/CIRCUIT_REVIEW.md` — STALE in places (audit S18, B15); the audit report supersedes it |
| Audit and design notes | `docs/superpowers/reviews/2026-10-16-project-audit.md`, `docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md`, `docs/DATASHEETS.md` |
| RE analysis | `docs/research/mbf_analysis.md` — full firmware RE results |
| Tools | `tools/` — decrypt, encrypt, doc/firmware checker (`tools/check_docs.py`) with tests in `tools/tests/` (17 tests on 2026-10-17; the earlier "52 tests" figure is UNVERIFIED), Ghidra scripts |
