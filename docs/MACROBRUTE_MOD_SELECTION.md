# MACROBRUTE — Curated Mod Selection

130+ mods audited from Yusynth schematics, Maffez, ModWiggler, community
research, and original schematic analysis. Curated for industrial/techno.

---

## BUILD — MicroBrute Body (6 controls + 6 touch bolts)

### Panel Jacks

| # | Mod | Type | Wiring | Why Build |
|---|-----|------|--------|-----------|
| B1 | **VCF Insert** | 3.5mm switched | Remove R23 (100K). Tip=VCA side, Ring=VCF side, Sleeve=GND. Normal: signal passes through jack. Inserted: breaks VCF→VCA chain. | Route external effects/filters into the VCA. Essential for semi-modular. |
| B2 | **Metalizer Insert** | 3.5mm switched | Remove R216 (120K). Tip=wavefolder input, Ring=triangle output. Normal: triangle feeds wavefolder. Inserted: external signal through wavefolder. | Feed external audio through the metalizer wavefolder. Unique textures. |
| B3 | **VCA CV Input** | 3.5mm mono | Wire to TP10 (CV1, 100K series R already in circuit). Direct injection. | External VCA control: tremolo, sidechain ducking, dynamics from expander. |

### Panel Toggles

| # | Mod | Type | Wiring | Why Build |
|---|-----|------|--------|-----------|
| B4 | **Envelope Bypass** | SPDT mini toggle | Bridge D4+D5 (TS4148RY) in EnvDest circuit. OFF=stock (clipped env). ON=full-range envelope to filter. | Removes limiter diodes — much deeper filter sweeps. One toggle, huge impact. |
| B5 | **Metalizer Boost** | SPDT mini toggle | Switch R216 between stock 120K and 20K alternate. Drives wavefolder input harder. | More aggressive metalizer harmonics at lower knob positions. Industrial essential. |
| B6 | **VCA Drone** | SPDT mini toggle | +12V → 100K → TP10 (VCA CV). Holds VCA open regardless of envelope/gate. | Drone mode — VCA stays open for continuous sound. Essential for ambient/industrial textures. |

### Touch Bolts (6 from 8 tested)

| # | Name | PCB Point | Safety R | Effect |
|---|------|-----------|----------|--------|
| T1 | **PITCH** | R309 area (rear, near Bourns 3006P trimmers) | 10K | Pitch vibrato/detune via body capacitance |
| T2 | **CRUNCH** | C111 (wavefolder stage 3) | 4.7K | Sweeps metalizer folding intensity |
| T3 | **WAH** | Filter CV input area (Steiner-Parker) | 22K | Manual filter sweep |
| T4 | **DISTORT** | Brute Factor feedback path | 15K | Variable feedback/self-oscillation |
| T5 | **HARM** | C107+C106 (wavefolder stages 1+2, dual bolt) | 10K each | Cross-coupled harmonics — touch both |
| T6 | **GATE** | Metalizer output→input (feedback) | 1K | Closes metalizer feedback loop on touch |

Selection after breadboard testing (Phase A). If any of these underperform,
swap in from reserves: #5 Envelope Decay (33K) or #7 LFO Speed (47K).

---

## BUILD — Internal / Breakout Board

| # | Mod | Component | Location | Notes |
|---|-----|-----------|----------|-------|
| I1 | **Output protection** | 10K resistor | R1 position (BruteFactor.SchDoc) | Tony Allgood design — prevents opamp damage from shorts |
| I2 | **8-channel buffer** | 2x TL074 | Breakout stripboard | Followers for: Saw(TP94), Sqr(TP93), Tri(TP124), Sub(TP102), Mix(TP30_MIXER_OUT), VCF(TP19), Env(TP6), LFO(TP21) |
| I3 | **Gate buffer** | CD40106 | Breakout stripboard | TP83 → Schmitt trigger → 5V gate out |
| I4 | **Level shifter** | CD4049UBE | Breakout stripboard | 5V→3.3V for Pico GPIO inputs |
| I5 | **Vactrol driver** | TL072 + 2N3904 + vactrol | Breakout stripboard | CV→LED→LDR for Brute Factor CV control via DB-9 B |
| I6 | **Spare op-amp** | U1B (TL062CDT pins 5-7) | On MicroBrute PCB | Repurpose as buffer — saves a TL074 channel on breakout |
| I7 | **Filter CV inject** | Wire to TP26 | Internal wiring | "Misc Cutoff Input" via existing 220K (R67) |
| I8 | **VCA CV inject** | Wire to TP12 | Internal wiring | "Misc Amplitude Input" via existing 100K (R33) |
| I9 | **Brute Factor CV** | Vactrol across RP8A/B | Internal wiring | Expander CV controls feedback amount |

---

## BUILD — Expander (17HP Eurorack — 87 × 128.5 mm)

The expander is now minimal. Most utilities have been moved off it because
the user already has equivalent modules in the rack. See
`MACROBRUTE_CONNECTION_MAP.md §10` for the canonical layout.

### Hardware utility on the expander

| Circuit | IC | Key Components | Panel Controls |
|---------|----|---------------|----------------|
| Slew limiter | TL072 (1 section) | 2× 1N4148 (rise/fall steering), 1µF timing cap | 1× 1MΩ rate pot, 2 jacks (in, out) |

### Firmware-only utilities (no analog hardware)

| Function | Pico GPIO | Notes |
|----------|-----------|-------|
| Clock divider | GP16, GP17, GP18 | Configurable ratios — defaults ÷2 ÷4 ÷8. Replaces CD4024 chip. |
| Programmable aux outputs ×4 | GP19, GP20, GP6, GP7 | Modes: TAP_DIV / EUCLID / RANDOM / PASSTHRU / PWM_CV. PWM-capable. |
| Tap button (with manual gate hold) | GP12 | Short = tempo, long = gate. Replaces standalone manual-gate circuit. |

### Dropped from this build (covered by user's existing rack modules)

| Originally planned | What replaces it |
|--------------------|------------------|
| White noise | NOISE module already in rack |
| LFO (tri+sqr) | Tryfelo (3 general-purpose LFOs) |
| Sample & Hold | RND CV module |
| Attenuverter 2ch | MMI Matrix mixer covers attenuvert routing |
| Buffered mult | '07 MULT module |
| Manual gate button | Folded into the tap button (long-hold mode) |
| Clock divider chip | Moved to firmware (GP16/17/18) |

### Patchbay (from DB-9)

**DB-9 A outputs (8 signals + GND):**
SAW, SQR, TRI, SUB, MIX, VCF, ENV, LFO → 8 jacks

**DB-9 B inputs (6 signals + power + GND):**
- Filter CV In (with attenuator pot)
- VCA CV In (with attenuator pot)
- Resonance CV In (vactrol)
- Sync In
- Gate In
- Ext Audio In

**Additional:** Clock Out (from Pico, separate wire), Gate Out (from Schmitt)

---

## BUILD — Tier 2 (Breadboard Test, Build If Good)

| # | Mod | Test Method | Decision Point |
|---|-----|------------|----------------|
| T1 | **Pico DAC → Filter (TP27)** | MCP4728 output via 220K to filter CV node | Does the 0-3.3V range produce audible sweeps? |
| T2 | **Pico DAC → VCA (TP13)** | MCP4728 output via 100K to VCA node | Clean gating/tremolo without clicks? |
| T3 | **R10/R13 populate** | Probe NotMounted pads, try various R values | Does it enable envelope inversion for filter? |
| T4 | **Metalizer feedback pot** | 100K pot between TP109 and metalizer input | More controllable than touch bolt feedback? |

---

## DOCUMENT ONLY — Not Building

### High Skill / High Risk

| Mod | Risk | Why Skip | Source |
|-----|------|----------|--------|
| Square wave phase fix | SMD rework on UB15 | Tiny components, easy to damage traces | mods_guide.md |
| Power rail sag ("dying battery") | LPC2361 corruption below ~8V | Cool effect but brick risk too high | deep_circuit_bending.md |
| LPC2361 clock manipulation | Brick risk | Varactor on crystal — any mistake kills MCU | deep_circuit_bending.md |
| MIDI out (pin 82) | SMD damage | LPC2361 pin is microscopic | mods_guide.md |

### Separate Projects (Phase 7)

| Mod | Why Defer | Source |
|-----|-----------|--------|
| PT2399 clock injection | JF-33 is a separate build | deep_circuit_bending.md |
| PT2399 VDD starving | JF-33 is a separate build | deep_circuit_bending.md |
| PT2399 reference manipulation | JF-33 is a separate build | deep_circuit_bending.md |
| DSO138 DAC output | Needs custom STM32 firmware | pt2399_dso138_findings.md |
| DSO138 trigger output | Separate integration project | pt2399_dso138_findings.md |
| Multi-PT2399 cascade/parallel | Advanced, needs dedicated board | deep_circuit_bending.md |

### Low Priority / Covered by Other Mods

| Mod | Why Skip | Alternative |
|-----|----------|-------------|
| VCO master volume (R76 replace) | Nice but not critical | Mix knobs already control levels |
| VCA envelope boost (R28) | Covered by VCA CV input (B3) | External CV does this better |
| Sub osc waveform mod | Low techno utility | Sub output already available via DB-9 |
| Portamento on ext CV | Complex trace surgery | Can do later if needed |
| Reduced portamento (C38→470nF) | Easy to do later | 5-minute mod anytime |
| VCA CV offset (BigCranberry) | VCA CV input is simpler | B3 covers this use case |
| R309 tuning range | Easy to do later | 5-minute resistor swap |
| Through-zero PWM | Experimental, undocumented | Standard PWM is fine |
| Sequencer decoupling | Expert-level rewiring | Pico can handle external sequencing |
| LFO audio rate | Digital LFO — impossible | Expander LFO is analog, can go faster |
| Velocity CV (PT675) | Needs custom LPC firmware | Phase 6C+ territory |
| Filter mode rotary | Stock switch exists | Already has LP/BP/HP select |

---

## Breadboard Test Protocol

**Equipment:** Double breadboard 11"x16", clip leads, multimeter, audio cable.

| Phase | What | Duration | Pass Criteria |
|-------|------|----------|---------------|
| A | Touch bends (8ch) | 1 session | 6+ bends produce musical effects |
| B | Buffers + level shift | 1 session | Clean pass-through, no oscillation |
| C | CV injection (filter, VCA) | 1 session | Smooth sweep, no clicks |
| D | Vactrol + Brute Factor | 1 session | CV-controlled feedback works |
| E | Insert mod simulation | 1 session | Signal passes, external inject works |
| F | Toggle mods (D4/D5, boost, drone) | 1 session | Each toggle has audible effect |
| G | Pico integration | 1-2 sessions | OLED, DAC, clock all functional |

**Go/No-Go:** Document results per phase. Only stripboard what passes.
Take 10s audio recordings of each mod for reference.

---

## Component Checklist (New Parts Needed)

| Component | Qty | For | On Hand? |
|-----------|-----|-----|----------|
| 3.5mm switched jacks | 3 | B1 VCF ins, B2 MTL ins, B3 VCA CV | Yes (20+) |
| SPDT mini toggles | 3 | B4 env bypass, B5 MTL boost, B6 drone | Check |
| M3 brass bolts + nuts | 6 | Touch bolts | Check |
| 100K resistor | 2 | B6 drone (VCA), B1 VCF insert replacement | Yes |
| 120K resistor | 1 | B2 MTL insert replacement | Yes |
| 20K resistor | 1 | B5 metalizer boost alternate | Yes |
| 10K resistor | 1 | I1 output protection | Yes |
| Vactrol (VTL5C3 or similar) | 1 | I5/I9 Brute Factor CV | Check |
| Clip leads | 10+ | Breadboard testing | Check |

---

## Signal Flow Summary (Post-Mod)

```
VCO (rear board)
  ├── TP94 Saw ──→ Buffer ──→ DB-9 A ──→ Expander SAW jack
  ├── TP93 Sqr ──→ Buffer ──→ DB-9 A ──→ Expander SQR jack
  ├── TP124 Tri ──→ Buffer ──→ DB-9 A ──→ Expander TRI jack
  ├── TP102 Sub ──→ Buffer ──→ DB-9 A ──→ Expander SUB jack
   └── Mixer ──→ TP30_MIXER_OUT ──→ Buffer ──→ DB-9 A ──→ Expander MIX jack
         │
         ▼
  [B5 MTL BOOST toggle] ──→ Metalizer
         │
         ├── [B2 MTL INSERT jack] ◄── external signal
         │
         ▼
  Steiner-Parker VCF ◄── TP26 Filter CV inject ◄── DB-9 B ◄── Expander
         │
         ├── TP19 ──→ Buffer ──→ DB-9 A ──→ Expander VCF jack
         │
         ├── [B1 VCF INSERT jack] ◄── external signal
         │
         ├── [B4 ENV BYPASS toggle] (D4/D5) ──→ deeper env sweeps
         │
         ▼
  VCA ◄── TP12 VCA CV inject ◄── DB-9 B ◄── Expander
   │  ◄── [B3 VCA CV jack] ◄── external CV
   │  ◄── [B6 DRONE toggle] ◄── +12V via 100K
   │
   ├── Brute Factor ◄── [I9 Vactrol CV] ◄── DB-9 B ◄── Expander
   │       │
   │       └── TP4 feedback tap
   │
   ├── TP6 Env ──→ Buffer ──→ DB-9 A ──→ Expander ENV jack
   │
   └── Audio Out ──→ [I1 10K protection] ──→ Master/HP

Touch bolts: 6x brass M3 on panel, wired through safety R to PCB points
Gate: TP83 ──→ CD40106 ──→ CD4049UBE ──→ Pico + DB-9 A
LFO: TP21 ──→ Buffer ──→ DB-9 A ──→ Expander LFO jack
```

---

## References

- Yusynth schematics: https://hackabrute.yusynth.net
- Maffez Pedrobrute: https://maffez.com/?page_id=2285
- ModWiggler thread: https://modwiggler.com/forum/viewtopic.php?t=152071
- Project test points: docs/hardware/MACROBRUTE_TEST_POINTS_VERIFIED.md
- Touch bend specs: docs/mods/touch_bend_specs.md
- Circuit review: schematics/CIRCUIT_REVIEW.md
- Wiring diagram: schematics/wiring_diagram.md
