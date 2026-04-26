> ⚠️ **DEPRECATED — superseded by current docs.** This file reflects an
> earlier iteration (different connector, expander HP, or pin map). Kept
> for historical reference only. See `README.md`, `docs/MACROBRUTE_BUILD_PLAN.md`,
> and `docs/MACROBRUTE_CONNECTION_MAP.md` for the current authoritative spec.

# MACROBRUTE Project Handoff Document (Legacy)

**Project:** Arturia MicroBrute Deep Modification  
**Codename:** MACROBRUTE  
**Owner:** Jordan  
**Date:** April 2026  
**Status:** Planning → Design Phase

---

## PROJECT SCOPE SUMMARY

Transform the Arturia MicroBrute into a fully semi-modular industrial/techno/IDM instrument through:

1. **Panel modifications** — Jacks, switches, OLED, encoder on control panel
2. **Circuit bending** — IC-level mods, waveform manglers, feedback paths
3. **Yusynth/Maffez documented mods** — Filter, VCO, VCA, animator improvements
4. **DIY circuits** — Vactrols, buffers, attenuators, CV conditioning
5. **Eurorack expander** — Utilities, additional I/O, clock dividers
6. **Multi-brain digital** — Pico H (primary), Arduino Nano (secondary), LPC2361 (stock MCU)
7. **Firmware reverse engineering** — LPC2361 CRP bypass, custom firmware potential

**Guiding principle:** Everything stays within the MicroBrute body + rear DB-9 connectors + Eurorack expander. No side panel mods.

---

## PART 1: CONTROL PANEL LAYOUT

### 18 Panel Positions (Jacks OR Switches)

All modifications stay within the blue control panel area. Each position can be a **3.5mm jack**, **toggle switch**, **momentary button**, or **LED**.

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  ●●●●●              OSCILLATOR                        FILTER           MOD MATRIX  │
│  (1-5)         ┌───────────────────────────────┐   ┌───────────────┐               │
│  LOGO AREA     │                               │   │               │   ●●●●        │
│                │  Sub    Ultrasaw   PW   Metal │   │  Cutoff  Res  │  (15-18)      │
│ ┌──────┐       │   ●(6)      ●(7)       ●(8)   │   │               │   VOL AREA    │
│ │ OLED │ [ENC] │                               │   │  Mode ●● (9-10)               │
│ │ 1.3" │  ●    │  Overtone        ────────     │   │       FLT/RES │               │
│ └──────┘ BTN   │                               │   └───────────────┘               │
│                └───────────────────────────────┘                                   │
│   +            ┌───────────────────────────────┐   ┌───────────────┐  SEQUENCER    │
│   ═══          │  CONTROLS         LFO         │   │   ENVELOPE    │               │
│   PITCH        │                               │   │               │               │
│   ●(A)         │  Glide    Wave    Sync        │   │               │               │
│   ───          │          ●●(11-12)            │   │     VCA ●(14) │               │
│   MOD          │         LFO AREA              │   │               │               │
│   ●(B)         │                               │   │               │               │
│   ───          └───────────────────────────────┘   └───────────────┘               │
│                                                                                    │
│   A = By Pitch Wheel                                                               │
│   B = By Mod Wheel                                                                 │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### Position Assignments (To Be Finalized)

| Pos | Location | Type | Signal/Function | Notes |
|-----|----------|------|-----------------|-------|
| 1 | Logo area | Jack | Gate Out (buffered) | From CD40106 buffer |
| 2 | Logo area | Jack | Gate In | External trigger |
| 3 | Logo area | Jack | Clock Out | From Pico H |
| 4 | Logo area | Jack | Clock In | To Pico H |
| 5 | Logo area | Jack/Switch | Trigger / Sync Select | TBD |
| 6 | Sub↔Ultrasaw | Jack | Sub Out | TP102 via 1kΩ |
| 7 | Sub↔Ultrasaw | Switch | Sub Boost | Bypass sub level attenuator |
| 8 | PW↔Metalizer | Jack | Metalizer Out | TP109 via 1kΩ |
| 9 | Filter Mode | Jack | Filter CV In | Summing node, 220kΩ series |
| 10 | Filter Mode | Jack | Resonance CV In | Vactrol controlled |
| 11 | LFO↔Sync | Jack | LFO Out | Direct from mod matrix |
| 12 | LFO↔Sync | Jack | Sync In | VCO hard sync |
| 13 | — | — | (merged into other) | — |
| 14 | By VCA | Jack | VCA CV In | TP10/11, 0-5V |
| 15 | Vol area | Jack | Main L Out | Buffered |
| 16 | Vol area | Jack | VCF Out | TP19, post-filter |
| 17 | Vol area | Jack | VCO Mix Out | TP30, pre-filter |
| 18 | Vol area | Switch | Brute Factor Bypass | Disconnect feedback loop |
| A | Pitch wheel | Jack | Pitch CV In | External 1V/oct override |
| B | Mod wheel | Jack | Mod Wheel CV Out | DAC channel C tap |

### OLED + Encoder + Button Area

| Component | Location | Function |
|-----------|----------|----------|
| 1.3" OLED (SPI/I²C) | Left of oscillator section | Display BPM, mode, tuner, pattern info |
| HW040 Encoder | Adjacent to OLED | Menu navigation (rotate), select (press) |
| Red Button | Adjacent to encoder | Manual gate / tap tempo / mode toggle |
| Status LED(s) | Near OLED | Clock pulse, gate activity, mode indicator |

---

## PART 2: ACTIVE MODIFICATIONS BY CATEGORY

### Category A: Waveform Taps (Direct, Low Risk)

| Mod | Test Point | Series R | Destination | Difficulty |
|-----|------------|----------|-------------|------------|
| Sawtooth Out | TP94 | 1kΩ | Panel or DB-9 | Easy |
| Square Out | TP93 | 1kΩ | Panel or DB-9 | Easy |
| Triangle Out | TP124 | 1kΩ | Panel or DB-9 | Easy |
| Sub Out | TP102 | 1kΩ | Panel (pos 6) | Easy |
| Metalizer Out | TP109 | 1kΩ | Panel (pos 8) | Easy |
| Ultrasaw Out | TP119 | 1kΩ | Panel or DB-9 | Easy |
| PWM Out | TP122 | 1kΩ | Panel or DB-9 | Easy |
| VCO Mix Out | TP30 (UB6 pin 7) | 1kΩ | Panel (pos 17) | Medium |
| VCF Out | TP19 | 1kΩ | Panel (pos 16) | Easy |

### Category B: CV Injection Points (Medium Risk)

| Mod | Injection Point | Series R | CV Range | Difficulty |
|-----|-----------------|----------|----------|------------|
| Filter CV In | U8A summing node | 220kΩ | ±5V | Medium |
| VCA CV In | TP10 or TP11 | Direct or 100kΩ | 0-5V | Easy |
| Resonance CV | Vactrol parallel to RP13 | — | 0-5V | Medium |
| PWM CV In | PWM modulation input | 100kΩ | ±5V | Medium |
| Linear FM In | U17b inverting input | 100kΩ | ±5V | Medium |
| Pitch FM In | Expo converter input | 100kΩ | ±5V | Medium |

### Category C: Switches and Toggles

| Mod | Function | Switch Type | Location |
|-----|----------|-------------|----------|
| VCO Sync Mode | Hard / Soft / Off | SPDT or 3-pos | Panel (pos 5 or 12) |
| Filter Mode Extend | LP / HP / BP / Notch | 4-pos rotary or panel | Replaces stock switch |
| Brute Factor Bypass | Feedback on/off | SPDT | Panel (pos 18) |
| Sub Boost | Bypass sub attenuator | SPST | Panel (pos 7) |
| VCA Boost | Lower R28 value | SPST | Panel or internal |
| Keyboard CV Bypass | Int KB / Ext CV only | SPDT | Panel |
| LFO Retrigger | Retrigger on gate | SPST | Panel |

### Category D: Circuit Bending (High Risk, High Reward)

Reference: `microbrute_circuit_bending_guide.md`

| Mod | Target IC | Method | Sound Character |
|-----|-----------|--------|-----------------|
| Metalizer feedback | U16 | Output → input via pot+cap | Harsh harmonics, self-oscillation |
| Filter input starve | U8 | Series resistor + switch | Lo-fi, gated distortion |
| Cross-mod injection | U17 | Saw → filter CV path | Aggressive FM-like tones |
| Sub oscillator abuse | U15 | Feedback path | Distorted sub, octave glitches |
| Animator feedback | U14 | Ultrasaw → metalizer | Complex waveshaping |
| Power rail sag | — | Resistor in V+ path | Dying battery effect |

### Category E: Yusynth/Maffez Documented Mods

| Mod | Source | Description | Difficulty |
|-----|--------|-------------|------------|
| VCO Mix Buffer | Yusynth | Use unused UB6 half for buffered mix out | Medium |
| Phase-correct Square | Maffez | Swap 4 resistors at comparator | Hard |
| Extended Tune Range | Maffez | Replace R309 (1MΩ → 100kΩ) | Easy |
| Filter Diode Swap | Maffez | 1N4148 → 1N270 germanium | Medium |
| Resonance Self-Osc Kill | Yusynth | Series switch in feedback | Easy |
| VCA Boost | Yusynth | R28: 100kΩ → 50kΩ+50kΩ pot | Easy |
| Notch Filter Mode | Yusynth | Short HP + LP inputs | Easy |

### Category F: DIY Circuits to Build

| Circuit | Components | Purpose |
|---------|------------|---------|
| Gate Buffer | CD40106 (1 section) | Clean up weak TP83 gate |
| Audio Buffers | TL074 (quad) | Buffer all waveform taps |
| CV Input Buffers | TL072 | Protect injection points |
| Vactrol (Resonance) | LED + LDR + heat shrink | CV control of resonance |
| Vactrol (VCA) | LED + LDR + heat shrink | Secondary VCA CV path |
| CV Attenuators | 100kΩ pots | Scale incoming CV |
| Clock Buffer | CD40106 (1 section) | Clean clock signal |
| LED Drivers | 2N3904 + resistor | Status indicators |

---

## PART 3: REAR PANEL — 2× DB-9 CONNECTORS

### Confirmed: 2× DB-9 (18 Pins Total)

Rear panel mount, directly wired to internal taps and injection points.

**DB-9 A: Audio + CV Outputs**

| Pin | Signal | Source | Notes |
|-----|--------|--------|-------|
| 1 | Pitch CV Out | DAC / rear panel | Stock signal, normalized |
| 2 | Gate Out (Buffered) | CD40106 buffer | Not raw TP83 |
| 3 | Saw Out | TP94 via 1kΩ | Raw waveform |
| 4 | Square Out | TP93 via 1kΩ | Raw waveform |
| 5 | Sub Out | TP102 via 1kΩ | Affected by sub knob |
| 6 | VCO Mix Out | TP30 via buffer | Pre-filter |
| 7 | VCF Out | TP19 via 1kΩ | Post-filter, pre-VCA |
| 8 | GND | — | Shield/reference |
| 9 | GND | — | Shield/reference |

**DB-9 B: CV Inputs + Clock + Power**

| Pin | Signal | Destination | Notes |
|-----|--------|-------------|-------|
| 1 | Filter CV In | Summing node | 220kΩ series on expander side |
| 2 | VCA CV In | TP10/11 | 0-5V |
| 3 | Sync In | VCO sync point | Hard sync |
| 4 | Clock Out | Pico H GPIO | To expander |
| 5 | Clock In | Pico H GPIO | From expander/external |
| 6 | Gate In | Gate circuit | External trigger |
| 7 | +12V | PSU tap | Power to expander |
| 8 | -12V | PSU tap | Power to expander |
| 9 | GND | — | Power return |

---

## PART 4: EURORACK EXPANDER MODULE

### Scaled Design: ~24-30HP

With panel I/O handling many signals, expander focuses on:
1. **Utilities not possible on panel** (noise, S&H, slew)
2. **Clock division** (÷2, ÷4, ÷8)
3. **Duplicated I/O** for Eurorack integration
4. **Attenuator/attenuverter controls**

### Expander Block Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    MACROBRUTE EXPANDER · 24HP                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FROM MB (via DB-9 A)          ACTIVE CIRCUITS                   │
│  ┌───┐┌───┐┌───┐┌───┐        ┌──────────────────┐               │
│  │SAW││SQR││SUB││MIX│        │ Clock Divider    │               │
│  │OUT││OUT││OUT││OUT│        │ CD4024           │               │
│  └───┘└───┘└───┘└───┘        │ ┌───┐┌───┐┌───┐ │               │
│  ┌───┐┌───┐┌───┐             │ │÷2 ││÷4 ││÷8 │ │               │
│  │VCF││PCH││GAT│             │ └───┘└───┘└───┘ │               │
│  │OUT││OUT││OUT│             └──────────────────┘               │
│  └───┘└───┘└───┘                                                │
│                              ┌──────────────────┐               │
│  TO MB (via DB-9 B)          │ Noise Generator  │               │
│  ┌───┐┌───┐┌───┐┌───┐       │ 2N3904 + TL072   │               │
│  │FLT││VCA││SYN││GAT│       │ ┌───┐            │               │
│  │ CV││ CV││ IN││ IN│       │ │NOI│            │               │
│  │ ○ ││ ○ ││   ││   │       │ │OUT│            │               │
│  │att││att││   ││   │       │ └───┘            │               │
│  └───┘└───┘└───┘└───┘       └──────────────────┘               │
│                                                                  │
│  ACTIVE CIRCUITS             ┌──────────────────┐               │
│  ┌──────────────────┐        │ Sample & Hold    │               │
│  │ Analog LFO       │        │ CD4066 + TL072   │               │
│  │ TL072 integrator │        │ ┌───┐  ○ Rate    │               │
│  │ ┌───┐┌───┐ ○Rate │        │ │S&H│            │               │
│  │ │TRI││SQR│       │        │ │OUT│            │               │
│  │ └───┘└───┘       │        │ └───┘            │               │
│  └──────────────────┘        └──────────────────┘               │
│                                                                  │
│  ┌──────────────────┐        ┌──────────────────┐               │
│  │ Slew Limiter     │        │ Attenuverter     │               │
│  │ TL072 RC         │        │ TL072 + pot      │               │
│  │ ┌───┐┌───┐ ○Time │        │ ┌───┐┌───┐      │               │
│  │ │ IN││OUT│       │        │ │ IN││OUT│ ○    │               │
│  │ └───┘└───┘       │        │ └───┘└───┘      │               │
│  └──────────────────┘        └──────────────────┘               │
│                                                                  │
│  ACTIVE CIRCUITS             ACTIVE CIRCUITS                    │
│  ┌──────────────────┐        ┌──────────────────┐               │
│  │ Manual Gate      │        │ Mult 1→3         │               │
│  │ Momentary button │        │ Buffered         │               │
│  │     [●]          │        │ ┌───┐┌───┐┌───┐ │               │
│  │    ┌───┐         │        │ │ IN││OUT││OUT│ │               │
│  │    │OUT│         │        │ └───┘└───┘└───┘ │               │
│  └────┴───┴─────────┘        └──────────────────┘               │
│                                                                  │
│           ════ DB-9 A ══════  ══════ DB-9 B ══════              │
│                     (rear mount, directly on panel)              │
└──────────────────────────────────────────────────────────────────┘
```

### Expander Parts Summary

| Component | Qty | Function |
|-----------|-----|----------|
| TL074 | 2 | Buffers, LFO, slew, S&H |
| TL072 | 1 | Noise amp, attenuverter |
| CD4024 | 1 | Clock divider |
| CD4066 | 1 | S&H switch |
| CD40106 | 1 | Clock conditioning |
| 2N3904 | 1 | Noise source |
| 100kΩ pots | 4-6 | LFO rate, S&H rate, slew, attenuation |
| 3.5mm jacks | 20-24 | All I/O |
| LEDs | 4-6 | Clock, gate, LFO indicators |
| DB-9 female | 2 | Cable connection to MB |

---

## PART 5: MULTI-BRAIN DIGITAL ARCHITECTURE

### Three Processors

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MICROBRUTE INTERNALS                            │
│                                                                         │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐    │
│  │   LPC2361    │  UART?  │   Pico H     │  UART?  │  Arduino     │    │
│  │  (Stock MCU) │◄───────►│  (Primary)   │◄───────►│  Nano        │    │
│  │              │         │              │         │  (Secondary) │    │
│  │ • Keyboard   │         │ • OLED       │         │ • ADC (6ch)  │    │
│  │ • Sequencer  │         │ • Encoder    │         │ • Extra GPIO │    │
│  │ • MIDI I/O   │         │ • Clock gen  │         │ • CV read?   │    │
│  │ • DAC (CV)   │         │ • Clock I/O  │         │ • Expansion  │    │
│  │ • USB-MIDI   │         │ • Gate I/O   │         │              │    │
│  │              │         │ • LED drive  │         │              │    │
│  └──────────────┘         └──────────────┘         └──────────────┘    │
│         │                        │                        │             │
│         │                        │                        │             │
│         ▼                        ▼                        ▼             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    ANALOG SIGNAL PATH                            │   │
│  │   VCO → Animator → Mixer → VCF → VCA → Brute Factor → Output    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Pico H Responsibilities

| Function | GPIO | Notes |
|----------|------|-------|
| OLED SDA | GP4 | I²C data |
| OLED SCL | GP5 | I²C clock |
| Encoder CLK | GP6 | Rotation A |
| Encoder DT | GP7 | Rotation B |
| Encoder SW | GP8 | Push button |
| Red Button | GP9 | Manual gate / mode |
| Clock Out | GP10 | To panel jack + DB-9 |
| Clock In | GP11 | From panel jack + DB-9 |
| Gate Out | GP12 | Directly or buffered |
| Gate In | GP13 | From panel jack |
| LED 1 | GP14 | Clock pulse indicator |
| LED 2 | GP15 | Gate activity |
| LED 3 | GP16 | Mode indicator |
| LPC2361 TX | GP0 | UART to stock MCU (if accessible) |
| LPC2361 RX | GP1 | UART from stock MCU (if accessible) |

### Arduino Nano Responsibilities (TBD)

Potential roles:
1. **CV Input Reading** — 6× ADC channels for reading Eurorack CV
2. **Additional Gate Outputs** — Trigger/gate multiplication
3. **MIDI DIN Processing** — Offload from Pico if needed
4. **Dedicated Clock Processor** — Complex clock manipulation
5. **Expansion Bus** — Future I²C peripherals

**Decision:** Nano role finalized after Pico implementation proves out. May not be needed.

---

## PART 6: LPC2361 FIRMWARE REVERSE ENGINEERING

### Objective

Determine if LPC2361 firmware can be:
1. **Read** (for analysis)
2. **Modified** (for custom behavior)
3. **Communicated with** (Pico ↔ LPC2361 UART)

### Step 1: CRP Detection

**Hardware needed:**
- PL2303HX USB-TTL adapter (already have)
- Connection to LPC2361 UART0: P0.2 (TXD0), P0.3 (RXD0)
- ISP entry: P2.10 pulled LOW during reset

**Procedure:**
```bash
# Install lpc21isp
sudo apt install lpc21isp

# Connect and detect (assumes 12MHz crystal)
lpc21isp -detectonly dummy.hex /dev/ttyUSB0 115200 12000
```

**Expected responses:**
- Part ID `0x1600F701` = LPC2361 confirmed
- Read success = No CRP, proceed to dump
- Error 19 = CRP1 or CRP2, flash locked
- No response = CRP3 or wiring issue

### Step 2: Based on CRP Level

| CRP Level | Action |
|-----------|--------|
| No CRP | Dump entire 64KB flash immediately |
| CRP1/CRP2 | Attempt SysEx capture during firmware update |
| CRP1/CRP2 | Attempt voltage glitching (ChipWhisperer) |
| CRP3 | SysEx capture only viable path |

### Step 3: Firmware Analysis (If Obtained)

**Ghidra setup:**
- Language: `ARM:LE:32:v4t`
- Base address: `0x00000000`
- Load SVD for LPC23xx peripheral labels

**Targets to identify:**
- MIDI parser state machine
- DAC write routines (MCP4728 I²C)
- Sequencer data structures
- UART communication (potential Pico interface)
- IAP routines (for understanding update mechanism)

### Step 4: Custom Firmware (If CRP Bypassed)

**Development environment:**
```bash
# Install ARM toolchain
sudo apt install gcc-arm-none-eabi

# Clone reference library
git clone https://github.com/psas/liblpc23xx.git
```

**Linker script critical sections:**
- `.vectors` at 0x00000000
- `.crp` at 0x000001FC (set to 0xFFFFFFFF)
- Checksum at 0x00000014

---

## PART 7: BUILD PHASES

### Phase 0: Preparation (Before Any Soldering)

- [ ] Open MicroBrute, photograph both PCBs (top and bottom)
- [ ] Identify all test points on actual hardware
- [ ] Probe key test points with multimeter (TP83, TP94, TP19, etc.)
- [ ] Locate ISP UART pins (P0.2, P0.3) and ISP entry (P2.10)
- [ ] Test Pico H + OLED on breadboard
- [ ] Test HW040 encoder with Pico
- [ ] Connect PL2303HX to LPC2361, check CRP status

### Phase 1: Non-Destructive Taps

- [ ] Wire waveform taps (TP94, TP93, TP102, TP109) via 1kΩ to temporary flying leads
- [ ] Build gate buffer (CD40106) on perfboard
- [ ] Test buffered gate output
- [ ] Wire VCF out (TP19)
- [ ] Wire VCO mix out (TP30)
- [ ] Verify all signals with oscilloscope/multimeter

### Phase 2: CV Injection Points

- [ ] Build CV input buffer board (TL072/TL074)
- [ ] Wire filter CV injection (summing node + 220kΩ)
- [ ] Wire VCA CV injection (TP10/11)
- [ ] Build DIY vactrol for resonance CV
- [ ] Test resonance CV control
- [ ] Wire sync input

### Phase 3: Panel Modifications

- [ ] Create drilling template for panel positions
- [ ] Drill panel holes (practice on scrap first)
- [ ] Mount OLED + encoder + button
- [ ] Mount 3.5mm jacks (switched where needed)
- [ ] Mount toggle switches
- [ ] Wire all panel components to internal points
- [ ] Test each panel I/O

### Phase 4: Rear Connectors

- [ ] Drill rear panel for 2× DB-9
- [ ] Mount DB-9 connectors
- [ ] Wire DB-9 A (outputs)
- [ ] Wire DB-9 B (inputs + power)
- [ ] Build + test interconnect cable
- [ ] Verify all signals pass through

### Phase 5: Pico H Integration

- [ ] Mount Pico H inside MicroBrute (location TBD)
- [ ] Wire Pico to OLED, encoder, button
- [ ] Wire Pico to clock/gate jacks
- [ ] Write firmware: OLED display driver
- [ ] Write firmware: encoder menu navigation
- [ ] Write firmware: clock generator (tap tempo)
- [ ] Write firmware: clock input detection
- [ ] (Optional) Wire Pico UART to LPC2361, test communication

### Phase 6: Expander Build

- [ ] Design expander PCB or perfboard layout
- [ ] Build clock divider circuit (CD4024)
- [ ] Build noise generator (2N3904 + TL072)
- [ ] Build analog LFO (TL072)
- [ ] Build S&H (CD4066 + TL072)
- [ ] Build slew limiter
- [ ] Build attenuverter
- [ ] Wire all expander I/O
- [ ] Mount in Eurorack panel
- [ ] Connect to MicroBrute via DB-9 cable
- [ ] Full system test

### Phase 7: Circuit Bending (Optional, After Core Complete)

- [ ] Identify specific bends to implement
- [ ] Add switches for safe enable/disable
- [ ] Test each bend individually
- [ ] Document results

### Phase 8: Firmware Deep Dive (Parallel Track)

- [ ] Complete CRP detection
- [ ] Attempt firmware extraction (method depends on CRP)
- [ ] Analyze firmware in Ghidra (if obtained)
- [ ] Document MIDI parsing, DAC control
- [ ] Explore Pico ↔ LPC2361 communication
- [ ] (Stretch) Custom firmware modifications

---

## PART 8: HARDWARE INVENTORY

### Already Have

| Item | Qty | Status |
|------|-----|--------|
| MicroBrute | 1 | Target |
| Pico H | 1 | Primary brain |
| Arduino Nano | 1 | Secondary brain (role TBD) |
| PL2303HX USB-TTL | 1 | ISP connection |
| 1.3" OLED SPI/I²C | 1 | Display |
| 0.96" SSD1306 I²C | 1 | Backup display |
| HW040 Encoder | 1 | Menu navigation |
| Red button | 1 | Manual gate / mode |
| Black button | 1 | Spare |
| 2× DB-9 + mating | 2 sets | Rear connectors |
| LEDs (various) | Many | Indicators, vactrols |
| LDRs | Several | DIY vactrols |
| 6U 84HP Eurorack case | 1 | Expander home |
| IC kit (555, TL074, LM358, etc.) | 1 | Arriving |

### Need to Acquire

| Item | Qty | Priority | Notes |
|------|-----|----------|-------|
| 3.5mm mono jacks (PJ301M style) | 25+ | High | Panel + expander |
| Toggle switches (SPDT, SPST) | 5-10 | High | Panel mods |
| 100kΩ pots (9mm) | 10 | High | Attenuators |
| CD40106 | 2-3 | High | Buffers |
| CD4024 | 2 | High | Clock divider |
| CD4066 | 2 | High | S&H |
| 2N3904 | 5 | Medium | Noise, drivers |
| Heat shrink (8mm black) | 1m | Medium | Vactrols |
| Perfboard | 2-3 | Medium | Internal circuits |
| Hookup wire (22-24 AWG) | Assorted | Medium | Wiring |
| Panel drilling bits (6mm, 7mm) | 1 each | Medium | Jack holes |
| Eurorack panel (blank or custom) | 1 | Medium | Expander face |

---

## PART 9: TASK BREAKDOWN

### Immediate Tasks

1. **Create panel drilling template** — SVG with exact positions for all 18 panel points + OLED cutout + encoder hole
2. **Design internal wiring diagram** — Show all connections from test points to panel jacks to DB-9
3. **Buffer board schematic** — TL074 quad buffer for waveform taps
4. **CV input board schematic** — TL072 buffer + protection for injection points
5. **Vactrol resonance CV schematic** — Complete circuit with LED driver
6. **Pico H pinout diagram** — Final GPIO assignments
7. **Pico firmware scaffold** — Basic structure for OLED + encoder + clock

### Medium-Term Tasks

8. **Expander schematic** — Complete circuit for all utility sections
9. **Expander panel layout** — Jack and pot positions
10. **LPC2361 connection guide** — Physical location of ISP pins on MicroBrute PCB
11. **Ghidra project setup** — Script for auto-labeling LPC23xx peripherals
12. **Firmware analysis notes** — Document any findings from extraction

### Documentation to Maintain

- **MACROBRUTE_MASTER_PLAN.md** — High-level project overview
- **MACROBRUTE_REVISED_SPEC.md** — Current architecture decisions
- **MACROBRUTE_PROJECT_HANDOFF.md** — This document (project reference)
- **MACROBRUTE_BUILD_LOG.md** — Progress tracking, photos, notes
- **MACROBRUTE_FIRMWARE_NOTES.md** — LPC2361 RE findings

---

## PART 10: KEY RESOURCES

### Schematics and Documentation

| Resource | URL | Content |
|----------|-----|---------|
| Hackabrute Schematics | https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html | Full MB schematics |
| Maffez Pedrobrute | https://maffez.com/?page_id=2285 | Mod documentation |
| Yusynth Modules | https://yusynth.net/Modular/index_en.html | Utility circuit designs |
| LPC2361 Datasheet | https://www.nxp.com/docs/en/data-sheet/LPC2361_62.pdf | MCU reference |
| LPC23xx User Manual | https://www.keil.com/dd/docs/datashts/philips/lpc23xx_um.pdf | Detailed peripheral info |
| MicroBrute SysEx | https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html | Protocol reverse engineering |

### Code Repositories

| Repo | URL | Relevance |
|------|-----|-----------|
| MKNielsen2000 Add-ons | https://github.com/MKNielsen2000/MicroBrute-Add-ons | Community mods |
| liblpc23xx | https://github.com/psas/liblpc23xx | LPC peripheral library |
| Mutable Instruments | https://github.com/pichenettes/eurorack | Firmware patterns |
| lpc21isp | https://github.com/capiman/lpc21isp | ISP flash tool |
| microdude | https://github.com/dagargo/microdude | SysEx editor |
| ChipWhisperer | https://github.com/newaetech/chipwhisperer | Glitching (if needed) |

### Community

| Forum | URL | Thread |
|-------|-----|--------|
| ModWiggler | https://modwiggler.com/forum/viewtopic.php?t=152071 | MB mod thread |
| ModWiggler | https://modwiggler.com/forum/viewtopic.php?t=95459 | MB general thread |

---

## APPENDIX A: TEST POINT QUICK REFERENCE

| TP | Signal | Location (approx) | Notes |
|----|--------|-------------------|-------|
| TP83 | Gate | Near U605 | 100kΩ source Z — BUFFER |
| TP93 | Square | VCO section | ~10Vpp |
| TP94 | Saw | VCO section | ~10Vpp |
| TP102 | Sub | Sub section | Level affected by knob |
| TP109 | Metalizer | Animator section | Post-wavefolder |
| TP119 | Ultrasaw | Animator section | Post-animator |
| TP122 | PWM | PWM shaper | Pulse wave |
| TP124 | Triangle | VCO section | Lower level |
| TP19 | VCF Out | Filter section | Post-filter |
| TP30 | VCO Mix | UB6 area | Use unused op-amp half |
| TP10/11 | VCA CV | VCA section | 0-5V injection |
| TP34 | Pitch CV | DAC area | 1V/oct |
| PT675 | Velocity | DAC area | Hidden, may not be populated |

---

## APPENDIX B: VACTROL BUILD GUIDE

### Materials

- 5mm LED (red or orange preferred — slower response)
- LDR (GL5528 or similar: ~10kΩ light, ~1MΩ dark)
- 8mm black heat shrink tubing, ~25mm length
- Optional: small piece of white paper as light diffuser

### Assembly

```
1. Bend LED and LDR leads to face each other
2. Position LED face ~2-3mm from LDR face
3. (Optional) Insert small paper diffuser between
4. Slide heat shrink over assembly
5. Shrink with heat gun (not flame — uneven heating)
6. Verify light-tight seal
```

### Testing

```
LED off:  LDR should read >500kΩ (ideally >1MΩ)
LED on:   LDR should read <20kΩ (ideally <10kΩ)
```

### Characteristics

- **Attack time:** 5-20ms (LED brightens → LDR drops)
- **Release time:** 50-200ms (LED dims → LDR rises slowly)
- This asymmetric response is musically useful — natural "pluck" envelope

---

*End of Project Handoff Document (Legacy)*
