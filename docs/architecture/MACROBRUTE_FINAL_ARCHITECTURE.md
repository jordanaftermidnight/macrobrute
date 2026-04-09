# MACROBRUTE Final Architecture

**Version:** Final  
**Date:** April 2026  
**Status:** Ready for CCLI Implementation

---

## DESIGN PHILOSOPHY (REVISED)

**MicroBrute = Synth Brain + Pico UI**  
**Expander = Patchbay + Utilities**  

The MicroBrute stays clean — only OLED, encoder, button, a few status LEDs, and 2-4 circuit bending switches. ALL patching happens at the Eurorack expander, which integrates with the larger system.

---

## PART 1: MICROBRUTE PANEL MODIFICATIONS (MINIMAL)

### What Goes ON the MicroBrute Panel

| Component | Location | Function | Drilling |
|-----------|----------|----------|----------|
| **1.3" OLED** | Left of oscillator (logo area) | BPM, mode, tuner, info | Rectangular cutout |
| **HW040 Encoder** | Adjacent to OLED | Menu scroll + select | 7mm hole |
| **Red Button** | Adjacent to encoder | Manual gate / tap tempo | 6mm hole |
| **LED 1** | Near OLED | Clock pulse indicator | 3mm hole |
| **LED 2** | Near OLED | Gate activity | 3mm hole |
| **LED 3** | Near OLED | Mode indicator | 3mm hole |

### Circuit Bending Switches (Optional, 2-4 positions)

Only add switches for mods you can't do via expander:

| Switch | Location | Function | Type |
|--------|----------|----------|------|
| **Brute Factor Bypass** | By volume knob | Disconnect feedback loop | SPST toggle |
| **VCA Drone** | By VCA/envelope | Open VCA fully | SPST toggle |
| **Sub Boost** | By sub knob | Bypass sub attenuator | SPST toggle |
| **Filter Input Starve** | By filter | Lo-fi mode | SPST toggle |

**Total panel drilling: 1 rectangular cutout + ~10 small holes**

### What Does NOT Go on MicroBrute Panel

- No audio jacks (all go to expander)
- No CV input jacks (all go to expander with attenuators)
- No CV output jacks (all go to expander via DB-9)
- No pots (expander has attenuators)

---

## PART 2: REAR PANEL — 2× DB-9 (18 Pins)

All signals route through rear-mounted DB-9 connectors to the expander.

### DB-9 A: OUTPUTS (MB → Expander)

| Pin | Signal | Source | Buffer? |
|-----|--------|--------|---------|
| 1 | **Gate Out** | TP83 → CD40106 | Yes |
| 2 | **Pitch CV Out** | DAC / rear | No (stock) |
| 3 | **Envelope Out** | Mod matrix tap | Buffer recommended |
| 4 | **LFO Out** | Mod matrix tap | Buffer recommended |
| 5 | **VCO Mix Out** | TP30 (UB6) | Buffer |
| 6 | **VCF Out** | TP19 | 1kΩ series |
| 7 | **Saw Out** | TP94 | 1kΩ series |
| 8 | **Square Out** | TP93 | 1kΩ series |
| 9 | **GND** | — | — |

### DB-9 B: INPUTS + POWER (Expander → MB)

| Pin | Signal | Destination | Protection |
|-----|--------|-------------|------------|
| 1 | **Filter CV In** | Summing node | 220kΩ on expander |
| 2 | **VCA CV In** | TP10/11 | Direct or 100kΩ |
| 3 | **Resonance CV In** | Vactrol | LED driver on expander |
| 4 | **Sync In** | VCO hard sync | Direct |
| 5 | **Gate In** | Gate circuit | Diode protection |
| 6 | **Ext Audio In** | Mixer | Direct or switched |
| 7 | **+12V** | PSU tap | Fused on expander |
| 8 | **-12V** | PSU tap | Fused on expander |
| 9 | **GND** | — | — |

### Signals NOT on DB-9 (Sacrificed for Pin Count)

| Signal | Alternative |
|--------|-------------|
| Triangle Out | Internal only, or add 3rd DB-9 later |
| Sub Out | Internal only, or body-mount jack |
| Metalizer Out | Internal only, or body-mount jack |
| Ultrasaw Out | Internal only |
| PWM CV In | Future expansion |
| Clock Out | Pico generates on expander side |
| Clock In | Pico receives on expander side |

**Note:** Clock I/O is handled by the Pico H, which can have separate wiring to the expander (3-4 wires outside DB-9, or use spare pins).

---

## PART 3: PICO H ARCHITECTURE

### Location

Inside MicroBrute, near digital board. Wires run to:
- Panel (OLED, encoder, button, LEDs)
- DB-9 area (clock signals if not in DB-9)
- Possibly LPC2361 UART (future)

### GPIO Assignments

| GPIO | Function | Notes |
|------|----------|-------|
| GP0 | UART TX → LPC2361 | Future, if firmware accessible |
| GP1 | UART RX ← LPC2361 | Future |
| GP2 | OLED SDA | I²C |
| GP3 | OLED SCL | I²C |
| GP4 | Encoder CLK | Rotation |
| GP5 | Encoder DT | Rotation |
| GP6 | Encoder SW | Push button |
| GP7 | Red Button | Manual gate / tap |
| GP8 | LED 1 (Clock) | PWM capable |
| GP9 | LED 2 (Gate) | PWM capable |
| GP10 | LED 3 (Mode) | PWM capable |
| GP11 | Clock Out | To expander |
| GP12 | Clock In | From expander |
| GP13 | Gate Mirror | Copy of gate for Pico |
| GP14-15 | Spare | Future |
| GP26-28 | ADC | If reading CV |

### Pico Firmware Functions

| Function | Priority | Status |
|----------|----------|--------|
| OLED display driver | High | Implement first |
| Encoder menu navigation | High | Basic menus |
| Clock generator (tap tempo) | High | Variable BPM |
| Clock input sync | High | Follow external |
| LED pulse indicators | Medium | Visual feedback |
| LPC2361 UART communication | Low | After CRP check |

---

## PART 4: EURORACK EXPANDER (36-42HP)

The expander is the main interface to your Eurorack system. It receives signals via DB-9, provides attenuated CV inputs, and generates utilities.

### Expander Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MACROBRUTE EXPANDER · 42HP                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  FROM MB (DB-9 A)                TO MB (DB-9 B)               ACTIVE UTILITIES │
│  ═══════════════                 ═══════════════              ════════════════ │
│                                                                                 │
│  CV OUTPUTS          AUDIO OUTPUTS        CV INPUTS (with pots)                │
│  ┌───┐┌───┐┌───┐    ┌───┐┌───┐┌───┐     ┌───┐┌───┐┌───┐┌───┐┌───┐            │
│  │GAT││PCH││ENV│    │MIX││VCF││SAW│     │FLT││VCA││RES││SYN││G.I│            │
│  │OUT││OUT││OUT│    │OUT││OUT││OUT│     │ CV││ CV││ CV││ IN││ N │            │
│  └───┘└───┘└───┘    └───┘└───┘└───┘     │ ○ ││ ○ ││ ○ ││   ││   │            │
│  ┌───┐              ┌───┐               └───┘└───┘└───┘└───┘└───┘            │
│  │LFO│              │SQR│               ATTENUATOR POTS ────────             │
│  │OUT│              │OUT│                                                     │
│  └───┘              └───┘               ┌───┐                                 │
│                                         │EXT│ External Audio In               │
│                                         │AUD│                                 │
│  ACTIVE CIRCUITS                        └───┘                                 │
│  ════════════════                                                             │
│                                                                                │
│  CLOCK SECTION         NOISE              LFO                 SAMPLE & HOLD   │
│  ┌───┐┌───┐┌───┐      ┌───┐              ┌───┐┌───┐          ┌───┐           │
│  │CLK││CLK││TAP│      │WHT│              │TRI││SQR│          │S&H│           │
│  │OUT││ IN││TMP│      │NOI│              │LFO││LFO│          │OUT│           │
│  └───┘└───┘└───┘      └───┘              └───┘└───┘          └───┘           │
│  ┌───┐┌───┐┌───┐                         ○ Rate              ○ Rate          │
│  │ ÷2││ ÷4││ ÷8│                                                             │
│  │OUT││OUT││OUT│      SLEW LIMITER       ATTENUVERTER        MULT            │
│  └───┘└───┘└───┘      ┌───┐┌───┐        ┌───┐┌───┐          ┌───┐┌───┐┌───┐ │
│  ○ ○ ○ LEDs           │SLW││SLW│        │A/V││A/V│          │1×3││OUT││OUT│ │
│                       │ IN││OUT│        │ IN││OUT│          │ IN││   ││   │ │
│                       └───┘└───┘        └───┘└───┘          └───┘└───┘└───┘ │
│                       ○ Time            ○ Amount                             │
│                                                                               │
│  ACTIVE                                                                       │
│  ┌───┐               INSERT SEND/RETURN (if wired)                           │
│  │MAN│ Manual        ┌───┐┌───┐ ┌───┐┌───┐                                   │
│  │GAT│ Gate          │VCF││VCF│ │MTL││MTL│ (Requires lifting resistors)      │
│  └───┘ Button        │SND││RTN│ │SND││RTN│                                   │
│                      └───┘└───┘ └───┘└───┘                                   │
│                                                                               │
│       ════ DB-9 A ════════════════  ════════ DB-9 B ════════════             │
│              (outputs)                    (inputs + power)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Expander Jack Count

| Section | Jacks | Pots | Notes |
|---------|-------|------|-------|
| CV Outputs (from MB) | 4 | 0 | Gate, Pitch, Env, LFO |
| Audio Outputs (from MB) | 4 | 0 | Mix, VCF, Saw, Square |
| CV Inputs (to MB) | 5 | 3 | Filter, VCA, Res + attenuators |
| Clock Section | 6 | 0 | Out, In, Tap, ÷2, ÷4, ÷8 |
| Noise | 1 | 0 | White noise |
| LFO | 2 | 1 | Tri, Square + Rate |
| S&H | 1 | 1 | Output + Rate |
| Slew | 2 | 1 | In, Out + Time |
| Attenuverter | 2 | 1 | In, Out + Amount |
| Mult | 3 | 0 | 1→3 buffered |
| Manual Gate | 1 | 0 | Button |
| **Total** | **31** | **7** | |

### Expander Parts

| Component | Qty | Function |
|-----------|-----|----------|
| TL074 | 3 | Buffers (12 channels) |
| TL072 | 2 | LFO, slew, S&H, attenuverter |
| CD4024 | 1 | Clock divider |
| CD4066 | 1 | S&H switch |
| CD40106 | 1 | Clock conditioning |
| 2N3904 | 2 | Noise source, LED drivers |
| 100kΩ pots (9mm) | 7 | Attenuators + utility controls |
| 3.5mm jacks | 31 | All I/O |
| LEDs (3mm) | 6 | Clock, gate, LFO indicators |
| DB-9 female | 2 | Cable connection |
| Momentary button | 1 | Manual gate |
| Power connector | 1 | Eurorack 10-pin or 16-pin |

---

## PART 5: INTERNAL CIRCUITS (Inside MicroBrute)

### Breakout PCB

A small PCB inside the MicroBrute to:
- Mount Pico H
- Buffer outputs (TL074)
- Condition CV inputs
- Drive LEDs
- Connect to DB-9

**Breakout PCB Contents:**

| Section | Components |
|---------|------------|
| Pico H mount | Pin headers or direct solder |
| Output buffers | 1× TL074 (4 channels) |
| Gate buffer | 1× CD40106 (1 section) |
| LED drivers | 3× 2N3904 + resistors |
| Vactrol driver | TL072 + current limit resistor |
| Power filtering | 100µF + 100nF caps |
| Connectors | Headers to OLED, encoder, DB-9 |

### Vactrol Circuit (For Resonance CV)

```
                     EXPANDER                          INSIDE MB
                 ┌─────────────┐                   ┌─────────────────┐
Resonance CV In ─┤             │                   │                 │
    ┌───┐        │   TL072     │    DB-9 B pin 3   │    VACTROL      │
    │   │────────┤   Buffer    ├───────────────────┤   ┌─────────┐   │
    │ ○ │ Pot    │   + LED     │                   │   │LED → LDR│   │
    │   │        │   Driver    │                   │   └────┬────┘   │
    └───┘        │             │                   │        │        │
                 │   1kΩ       │                   │   To RP13 path  │
                 │   limiting  │                   │   (parallel)    │
                 └─────────────┘                   └─────────────────┘
```

---

## PART 6: NANO DECISION

### Analysis

| Role | Pico Handles? | Nano Adds Value? |
|------|---------------|------------------|
| OLED | ✓ | No |
| Encoder | ✓ | No |
| Clock gen | ✓ | No |
| Clock input | ✓ | No |
| LED drive | ✓ | No |
| CV ADC (3 ch) | ✓ (GP26-28) | Maybe if >3 needed |
| Extra GPIO | ✓ (26 total) | No |
| LPC2361 UART | ✓ | No |

### Decision: PARK THE NANO

Start without Nano. Pico H handles everything planned. Add Nano later only if:
- You need >3 ADC channels
- You want hardware separation (CV processing offloaded)
- A specific future feature requires it

Keep Nano in parts bin for experiments.

---

## PART 7: LPC2361 FIRMWARE PLAN

### Phase 1: CRP Detection (First Priority)

**Hardware setup:**
```
PL2303HX          LPC2361
─────────         ─────────
TX  ───────────── P0.3 (RXD0)
RX  ───────────── P0.2 (TXD0)
GND ───────────── GND

P2.10 → GND (during reset for ISP entry)
```

**Procedure:**
```bash
# Install lpc21isp
sudo apt install lpc21isp

# Detect chip (assumes 12MHz crystal)
lpc21isp -detectonly dummy.hex /dev/ttyUSB0 115200 12000
```

**Expected results:**
- Part ID `0x1600F701` = LPC2361 confirmed
- Able to read memory = No CRP → DUMP IMMEDIATELY
- Error 19 = CRP1/CRP2 → Flash locked
- No response = CRP3 or wiring issue

### Phase 2: Based on CRP Level

| Level | Next Step |
|-------|-----------|
| No CRP | Dump 64KB flash, analyze in Ghidra |
| CRP1/2 | Capture SysEx during firmware update |
| CRP1/2 | Attempt voltage glitching (ChipWhisperer) |
| CRP3 | SysEx capture only path |

### Phase 3: If Firmware Obtained

- Load into Ghidra with ARM7TDMI settings
- Identify MIDI parser, DAC routines, sequencer
- Look for UART communication hooks
- Assess custom firmware feasibility

---

## PART 8: BUILD PHASES

### Phase 0: Preparation

- [ ] Open MicroBrute, photograph PCBs
- [ ] Probe test points (TP83, TP94, TP19, TP30, etc.)
- [ ] Test Pico H + OLED + encoder on breadboard
- [ ] Connect PL2303HX to LPC2361, check CRP
- [ ] Measure panel clearance for OLED cutout
- [ ] Design breakout PCB

### Phase 1: Internal Wiring (No Drilling Yet)

- [ ] Build breakout PCB with Pico, buffers, LED drivers
- [ ] Wire all test point taps (flying leads)
- [ ] Wire DB-9 connectors (loose, not mounted)
- [ ] Build vactrol, test resonance CV
- [ ] Test all signals with multimeter/scope
- [ ] Verify everything works before any drilling

### Phase 2: MicroBrute Panel

- [ ] Create drilling template (OLED cutout, encoder, button, LEDs, switches)
- [ ] Practice on scrap material
- [ ] Cut OLED window (clear plastic overlay option)
- [ ] Drill holes
- [ ] Mount OLED, encoder, button, LEDs
- [ ] Mount circuit bending switches
- [ ] Final wiring to breakout PCB

### Phase 3: Rear Panel

- [ ] Drill rear panel for 2× DB-9
- [ ] Mount DB-9 connectors
- [ ] Final wiring from breakout PCB to DB-9
- [ ] Build interconnect cable
- [ ] Test all signals pass through

### Phase 4: Expander Build

- [ ] Design expander PCB or layout perfboard
- [ ] Build buffer section (TL074 × 3)
- [ ] Build utility circuits (noise, LFO, clock div, S&H, slew)
- [ ] Build attenuator/attenuverter circuits
- [ ] Wire all jacks
- [ ] Mount in Eurorack panel (42HP)
- [ ] Connect via DB-9 cable
- [ ] Full system test

### Phase 5: Pico Firmware

- [ ] OLED driver + basic display
- [ ] Encoder menu system
- [ ] Clock generator (tap tempo)
- [ ] Clock input detection
- [ ] LED indicators
- [ ] (Optional) LPC2361 communication

### Phase 6: LPC2361 Investigation

- [ ] Complete CRP detection
- [ ] Attempt firmware extraction
- [ ] Analyze if successful
- [ ] Document findings

---

## PART 9: SIGNAL ROUTING SUMMARY

### What Goes Where

| Signal | Panel | DB-9 | Expander | Notes |
|--------|-------|------|----------|-------|
| **OUTPUTS** | | | | |
| Gate Out | — | A-1 | Jack | Buffered |
| Pitch CV Out | — | A-2 | Jack | Stock signal |
| Envelope Out | — | A-3 | Jack | Mod matrix tap |
| LFO Out | — | A-4 | Jack | Mod matrix tap |
| VCO Mix Out | — | A-5 | Jack | TP30, pre-filter |
| VCF Out | — | A-6 | Jack | TP19, post-filter |
| Saw Out | — | A-7 | Jack | TP94 |
| Square Out | — | A-8 | Jack | TP93 |
| **INPUTS** | | | | |
| Filter CV In | — | B-1 | Jack + Pot | With attenuator |
| VCA CV In | — | B-2 | Jack + Pot | With attenuator |
| Resonance CV In | — | B-3 | Jack + Pot | Vactrol driven |
| Sync In | — | B-4 | Jack | VCO hard sync |
| Gate In | — | B-5 | Jack | External trigger |
| Ext Audio In | — | B-6 | Jack | Mixer input |
| **POWER** | | | | |
| +12V | — | B-7 | — | To expander |
| -12V | — | B-8 | — | To expander |
| GND | — | A-9, B-9 | — | Reference |
| **CLOCK (Pico)** | | | | |
| Clock Out | — | Wire* | Jack | From Pico |
| Clock In | — | Wire* | Jack | To Pico |
| **UTILITIES** | | | | |
| Noise | — | — | Jack | Generated on expander |
| LFO (exp) | — | — | 2 Jacks | Generated on expander |
| Clock ÷2/÷4/÷8 | — | — | 3 Jacks | Generated on expander |
| S&H | — | — | Jack | Generated on expander |
| Slew | — | — | 2 Jacks | Generated on expander |
| **PANEL ONLY** | | | | |
| OLED | ✓ | — | — | Display |
| Encoder | ✓ | — | — | Navigation |
| Button | ✓ | — | — | Tap tempo / gate |
| LEDs | ✓ | — | — | Status |
| Switches | ✓ | — | — | Circuit bending |

*Clock signals: Either use 2 wires outside DB-9, or repurpose pins if you sacrifice other signals.

---

## PART 10: PARTS SUMMARY

### Already Have

| Item | Qty |
|------|-----|
| MicroBrute | 1 |
| Pico H | 1 |
| Arduino Nano | 1 (parked) |
| PL2303HX | 1 |
| 1.3" OLED | 1 |
| HW040 Encoder | 1 |
| Red button | 1 |
| DB-9 connectors | 2 sets |
| LEDs + LDRs | Many |
| IC kit (arriving) | 1 |
| 6U 84HP case | 1 |

### Need to Acquire

| Item | Qty | For |
|------|-----|-----|
| 3.5mm mono jacks | 35+ | Expander |
| SPST toggle switches | 4 | Panel |
| 100kΩ pots (9mm) | 8 | Expander |
| TL074 | 4 | Buffers (MB + Exp) |
| TL072 | 3 | Utilities |
| CD4024 | 2 | Clock divider |
| CD4066 | 2 | S&H |
| CD40106 | 2 | Buffers |
| 2N3904 | 10 | Various |
| Perfboard / PCB | 3 | Breakout + Expander |
| Heat shrink (8mm) | 1m | Vactrols |
| 22-24 AWG wire | Assorted | Wiring |
| Panel (42HP blank) | 1 | Expander |

---

## APPENDIX: CCLI TASK LIST

### Immediate Tasks

1. **Breakout PCB schematic** — Pico mount, buffers, LED drivers, connectors
2. **Breakout PCB layout** — Fit inside MicroBrute
3. **Panel drilling template** — OLED cutout + holes (SVG)
4. **Expander schematic** — Full circuit with all utilities
5. **Expander panel layout** — 42HP jack/pot positions (SVG)
6. **DB-9 wiring diagram** — Pin-to-signal mapping
7. **Pico firmware scaffold** — Basic structure

### Documentation to Generate

- Schematic PDFs
- Gerber files (if PCB)
- BOM with suppliers
- Wiring diagrams
- Firmware source

---

*End of Final Architecture Document*
