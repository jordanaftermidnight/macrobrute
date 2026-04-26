> ⚠️ **DEPRECATED — superseded by current docs.** This file reflects an
> earlier iteration (different connector, expander HP, or pin map). Kept
> for historical reference only. See `README.md`, `docs/MACROBRUTE_BUILD_PLAN.md`,
> and `docs/MACROBRUTE_CONNECTION_MAP.md` for the current authoritative spec.

# MACROBRUTE MASTER PLAN
## Complete Project Documentation: Hardware Mods, Firmware Development & Expansion Controller

**Project Codename:** MACROBRUTE  
**Author:** jordanaftermidnight  
**Version:** 2.0 — March 2026  
**Goal:** Build the most extensively modified and documented MicroBrute in existence

---

# TABLE OF CONTENTS

1. [Project Architecture Overview](#part-1-project-architecture-overview)
2. [Phase Timeline](#part-2-phase-timeline)
3. [Analog Modifications Checklist](#part-3-analog-modifications-checklist)
4. [Custom Firmware (MACROBRUTE OS)](#part-4-custom-firmware-überbrute-os)
5. [Pi Pico Expansion Controller](#part-5-pi-pico-expansion-controller)
6. [OLED Display Integration](#part-6-oled-display-integration)
7. [Wiring Plan & Test Points](#part-7-wiring-plan--test-points)
8. [Complete Bill of Materials](#part-8-complete-bill-of-materials)
9. [Development Environment Setup](#part-9-development-environment-setup)
10. [Safety & Recovery Procedures](#part-10-safety--recovery-procedures)

---

# PART 1: PROJECT ARCHITECTURE OVERVIEW

## System Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MACROBRUTE SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    STOCK MICROBRUTE HARDWARE                         │   │
│  │  ┌─────────────────┐              ┌────────────────────────────────┐ │   │
│  │  │    LPC2361      │    DAC/CV    │      Analog Circuitry          │ │   │
│  │  │  ARM7TDMI-S     │◄────────────►│  VCO → Wavefolder → Mixer     │ │   │
│  │  │                 │    GPIO      │  → Steiner-Parker VCF → VCA   │ │   │
│  │  │  CUSTOM         │              │  → Brute Factor → Output      │ │   │
│  │  │  FIRMWARE       │              │                                │ │   │
│  │  │  (MACROBRUTE OS) │              │  LFO, ADSR, Sub-Osc, PWM      │ │   │
│  │  └────────┬────────┘              └────────────────────────────────┘ │   │
│  │           │                                                          │   │
│  │     JTAG  │  UART                                                    │   │
│  │   (debug) │  (comms)                                                 │   │
│  └───────────┼─────────────────────────────────────────────────────────┘   │
│              │                                                             │
│              ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    EXPANSION CONTROLLER                              │   │
│  │  ┌─────────────────┐              ┌────────────────────────────────┐ │   │
│  │  │  Raspberry Pi   │◄────────────►│   2.08" OLED SH1122           │ │   │
│  │  │     Pico        │     SPI      │   256×64 Grayscale            │ │   │
│  │  │                 │              │   (Logo Area Mount)            │ │   │
│  │  │  - Display Ctrl │              └────────────────────────────────┘ │   │
│  │  │  - CV Outputs   │              ┌────────────────────────────────┐ │   │
│  │  │  - MIDI Thru    │     PWM→CV   │   4× CV Outputs (0-10V)        │ │   │
│  │  │  - Clock Gen    │─────────────►│   Precision filtered PWM       │ │   │
│  │  └─────────────────┘              └────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALOG MODIFICATIONS                              │   │
│  │  • Waveform breakouts (Saw, Tri, Pulse, Sub)                        │   │
│  │  • Metalizer insert + output + timbre switches                      │   │
│  │  • VCA CV input + insert                                            │   │
│  │  • VCO master volume                                                │   │
│  │  • Portamento speed mod                                             │   │
│  │  • MIDI Out                                                         │   │
│  │  • Body contacts (8 points)                                         │   │
│  │  • White noise generator                                            │   │
│  │  • Sample & Hold                                                    │   │
│  │  • Clock divider                                                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why This Architecture?

**LPC2361 stays soldered** — No risky QFP100 removal. Custom firmware is loaded via JTAG/ISP reflash.

**Pi Pico as co-processor** — Handles display, additional CV outputs, MIDI processing. Communicates with LPC2361 via UART.

**Analog mods are independent** — Work regardless of firmware state. The synth remains playable even if firmware development hits issues.

---

# PART 2: PHASE TIMELINE

## Overview

| Phase | Focus | Duration | Dependencies |
|-------|-------|----------|--------------|
| 0 | Documentation & Sourcing | 2 weeks | None |
| 1 | Analog Mods (Tier 1-2) | 2 weeks | BOM arrives |
| 2 | JTAG Connection & Analysis | 1 week | J-Link arrives |
| 3 | Firmware Extraction/CRP Check | 1-7 days | Phase 2 |
| 4 | Pi Pico Integration | 2 weeks | Pico + OLED arrive |
| 5 | Basic Custom Firmware | 3 weeks | Phase 3 |
| 6 | Analog Mods (Tier 3-4) | 2 weeks | Phase 1 complete |
| 7 | Advanced Firmware Features | 2 months | Phase 5 |
| 8 | Body Contacts & Bending | 1 week | Any time |
| 9 | Panel Fabrication | 2 weeks | All mods planned |
| 10 | Integration & Testing | 2 weeks | All phases |

**Estimated Total:** 4-6 months for full completion

---

## Phase 0: Documentation & Sourcing (2 weeks)

### Tasks
- [ ] Download all schematics from hackabrute.yusynth.net
- [ ] High-resolution photos of both PCBs (front and back, both boards)
- [ ] Map all test points against schematic
- [ ] Identify all unpopulated component footprints
- [ ] Order components (consolidate into 3-4 orders for shipping efficiency)
- [ ] Set up firmware development environment
- [ ] Create project repository structure

### Deliverables
- PCB photo documentation with annotations
- Test point map spreadsheet
- Component orders placed
- Development environment ready

---

## Phase 1: Analog Mods — Foundation (2 weeks)

### Tier 1 — Essential Mods (do first)

| # | Modification | Difficulty | Components |
|---|--------------|------------|------------|
| 1.1 | **Output Protection** | Easy | 10kΩ resistor |
| 1.2 | **VCA CV Input** | Easy | 3.5mm jack (switched) |
| 1.3 | **Portamento on External CV** | Medium | Reroute internal CV |

### Tier 2 — High Value Mods

| # | Modification | Difficulty | Components |
|---|--------------|------------|------------|
| 2.1 | **Buffered VCO Mix Output** | Medium | Uses unused UB6 opamp half |
| 2.2 | **VCO Master Volume** | Medium | B100K pot (replaces R76) |
| 2.3 | **Metalizer Output** | Easy | 1kΩ resistor, 3.5mm jack |
| 2.4 | **Waveform Breakouts** | Easy | 4× 1kΩ, 4× 3.5mm jacks |
| 2.5 | **Metalizer Input Insert** | Medium | Remove R216, switched jack |

### Test Points for Waveform Breakouts

| Signal | Test Point | Series Resistor |
|--------|------------|-----------------|
| Square | TP93 | 1kΩ |
| Sawtooth | TP94 | 1kΩ |
| Sub-Oscillator | TP102 | 1kΩ |
| Triangle | TP124 | 1kΩ |
| Metalizer Out | TP109 | 1kΩ |

---

## Phase 2: JTAG Connection & Analysis (1 week)

### Hardware Setup

The MicroBrute's LPC2361 has a **fully populated JTAG header** — extremely rare. Most manufacturers remove this post-production.

**JTAG Pinout (LPC2361 LQFP100):**

| Function | LPC2361 Pin | Wire Color |
|----------|-------------|------------|
| TMS | Pin 72 | Yellow |
| TCK | Pin 71 | Orange |
| TDI | Pin 68 | Green |
| TDO | Pin 53 | Blue |
| TRST | Pin 54 | Purple |
| GND | Any GND | Black |
| 3.3V | Near regulator | Red |

### Software Setup

```bash
# Install ARM toolchain
sudo apt install gcc-arm-none-eabi gdb-multiarch openocd

# Verify installation
arm-none-eabi-gcc --version
openocd --version
```

### OpenOCD Configuration (lpc2361_microbrute.cfg)

```tcl
# LPC2361 MicroBrute Configuration
source [find interface/jlink.cfg]
transport select jtag

# LPC2361 is ARM7TDMI-S
set CHIPNAME lpc2361
set CPUTAPID 0x4f1f0f0f

source [find target/lpc2000.cfg]

# Flash configuration: 64KB internal flash
# LPC2000 v2 silicon, 12MHz crystal, calculate checksum
flash bank lpc2361.flash lpc2000 0x0 0x10000 0 0 $_TARGETNAME lpc2000_v2 12000 calc_checksum

# Work area in SRAM
$_TARGETNAME configure -work-area-phys 0x40000000 -work-area-size 0x8000 -work-area-backup 0

# Adapter speed
adapter speed 500
```

### First Connection Test

```bash
# Start OpenOCD
openocd -f lpc2361_microbrute.cfg

# In another terminal, connect via telnet
telnet localhost 4444

# Test commands
> halt
> reg
> mdw 0x0 16        # Read first 64 bytes of flash
> mdw 0x1FC 1       # READ CRP STATUS - CRITICAL!
```

### CRP Status Check

The LPC2361's Code Read Protection (CRP) is stored at flash address **0x1FC**:

| CRP Value | Level | Meaning |
|-----------|-------|---------|
| `0xFFFFFFFF` | **None** | ✅ JACKPOT - Full access |
| `0x12345678` | CRP1 | JTAG disabled, partial ISP |
| `0x87654321` | CRP2 | JTAG disabled, full erase only |
| `0x43218765` | CRP3 | ⚠️ BRICK RISK - No recovery |

**If CRP is not enabled (0xFFFFFFFF):**
```
> dump_image microbrute_firmware_backup.bin 0x0 0x10000
```

**If CRP is enabled:** See Phase 3 for bypass options.

---

## Phase 3: Firmware Extraction / CRP Bypass (1-7 days)

### If CRP is NOT enabled (best case)

1. Dump firmware: `dump_image microbrute_original.bin 0x0 0x10000`
2. Create multiple backups on different media
3. Proceed to disassembly

### If CRP IS enabled (likely)

**Option A: Voltage Glitching Attack**

CRP bypass was demonstrated at RECON Brussels 2017 by Chris Gerlinsky. The attack uses precise voltage glitches during the CRP check routine.

**Required:**
- ChipWhisperer Lite (~€200) OR
- Custom glitcher (FPGA-based, ~€50 DIY)

**Success rate:** ~30-60% per attempt, typically successful within a few hours.

**Option B: Accept CRP and Start Fresh**

If CRP bypass is not feasible:
1. Full erase via ISP (destroys original firmware)
2. Write custom firmware from scratch
3. Original Arturia functionality is lost
4. Can restore via Arturia's USB update if you have the update file

**Option C: Hybrid Approach (Recommended)**

1. Keep original firmware on LPC2361
2. Use Pi Pico for all new features
3. LPC2361 continues running stock firmware
4. Pico intercepts MIDI, generates CV, drives display
5. Full functionality, zero CRP risk

---

## Phase 4: Pi Pico Integration (2 weeks)

### Hardware Assembly

1. Solder headers to Pi Pico
2. Build CV output filter boards (4 channels)
3. Wire OLED display
4. Create main wiring harness with JST connectors
5. Mount Pico inside MicroBrute case
6. Cut OLED window in logo area

### Pico Firmware Architecture

```
/uberbrute-pico
├── src/
│   ├── main.c                 # Main loop, initialization
│   ├── display.c              # OLED rendering (SH1122 driver)
│   ├── display.h
│   ├── cv_output.c            # PWM→CV generation (4 channels)
│   ├── cv_output.h
│   ├── midi_handler.c         # MIDI interception/processing
│   ├── midi_handler.h
│   ├── uart_protocol.c        # LPC2361 ↔ Pico communication
│   ├── uart_protocol.h
│   ├── ui_screens.c           # Display screen layouts
│   └── ui_screens.h
├── lib/
│   ├── pico_sdk/
│   └── u8g2/                   # Graphics library for SH1122
├── CMakeLists.txt
└── README.md
```

### Pin Assignment

| Function | GPIO | Physical Pin |
|----------|------|--------------|
| UART TX → LPC2361 | GP0 | Pin 1 |
| UART RX ← LPC2361 | GP1 | Pin 2 |
| OLED SCK | GP18 | Pin 24 |
| OLED MOSI | GP19 | Pin 25 |
| OLED CS | GP17 | Pin 22 |
| OLED DC | GP16 | Pin 21 |
| OLED RST | GP20 | Pin 26 |
| CV Out 1 | GP10 | Pin 14 |
| CV Out 2 | GP11 | Pin 15 |
| CV Out 3 | GP12 | Pin 16 |
| CV Out 4 | GP13 | Pin 17 |
| ADC In 1 | GP26 | Pin 31 |
| ADC In 2 | GP27 | Pin 32 |

---

## Phase 5: Basic Custom Firmware (3 weeks)

### Development Approach

**If original firmware was extracted:**
1. Disassemble with Ghidra
2. Identify key functions (sequencer, MIDI, DAC)
3. Patch existing firmware
4. Test incrementally

**If starting from scratch:**
1. Use libopencm3 or bare metal C
2. Port peripheral drivers from LPC2000 SDK
3. Implement minimum viable functionality first

### Minimum Viable Firmware Checklist

- [ ] Keyboard scanning works
- [ ] DAC outputs correct pitch CV
- [ ] Gate output works
- [ ] MIDI input works (note on/off, CC)
- [ ] Sequencer plays back
- [ ] USB enumerates (optional for initial version)

### Memory Map (LPC2361)

| Region | Start | Size | Contents |
|--------|-------|------|----------|
| Flash | 0x00000000 | 64KB | Firmware code |
| SRAM | 0x40000000 | 34KB | Variables, stack |
| Boot ROM | 0x7FFFE000 | 8KB | ISP bootloader |
| APB Peripherals | 0xE0000000 | — | GPIO, UART, etc. |

### Linker Script (lpc2361.ld)

```ld
MEMORY
{
    flash (rx)  : ORIGIN = 0x00000000, LENGTH = 64K
    sram (rwx)  : ORIGIN = 0x40000000, LENGTH = 34K
}

SECTIONS
{
    .text : {
        KEEP(*(.vectors))
        *(.text*)
        *(.rodata*)
    } > flash

    .data : {
        *(.data*)
    } > sram AT > flash

    .bss : {
        *(.bss*)
        *(COMMON)
    } > sram
}
```

---

## Phase 6: Analog Mods — Advanced (2 weeks)

### Tier 3 — Sound Design Mods

| # | Modification | Components |
|---|--------------|------------|
| 3.1 | Metalizer Input Boost Switch | 100kΩ resistor, SPDT switch |
| 3.2 | Metalizer Timbre Switches (4) | 30kΩ resistors, 4× SPDT switches |
| 3.3 | Reduced Portamento Time | 470nF film cap (replaces C38) |
| 3.4 | VCA Input Insert | Remove R23, switched jack |
| 3.5 | Enhanced VCA Envelope | 50kΩ + B50K pot (replaces R28) |
| 3.6 | Extended Tuning Range | 100kΩ (replaces R309 1MΩ) |

### Tier 4 — Advanced Mods

| # | Modification | Components |
|---|--------------|------------|
| 4.1 | Square Wave Phase Fix | Swap UB15 inputs |
| 4.2 | Sequencer Decoupling | 2N3906, 22kΩ, 10kΩ |
| 4.3 | MIDI Out | DIN socket, 100Ω |
| 4.4 | White Noise Generator | BC547, TL072, capacitors |
| 4.5 | Sample & Hold | CD4066, 100nF, TL072 |
| 4.6 | Clock Divider | CD4017, CD4024 |

---

## Phase 7: Advanced Firmware Features (2 months)

### Feature Roadmap

**Sequencer Enhancements:**
- [ ] 64-step sequences (vs stock 8)
- [ ] 128-step pattern chains
- [ ] Per-step probability (0-100%)
- [ ] Ratcheting (1-8 repeats per step)
- [ ] Swing amount (0-75%)
- [ ] Euclidean rhythm generator
- [ ] Polyrhythmic mode (3:4, 5:4, etc.)

**CV Modes:**
- [ ] Quantizer (selectable scales)
- [ ] Arpeggiator (up, down, up-down, random)
- [ ] CV recorder (record and playback)
- [ ] Portamento curves (linear, exponential, S-curve)
- [ ] Glide per step

**MIDI Enhancements:**
- [ ] Full CC mapping (all 127)
- [ ] NRPN support
- [ ] MIDI clock output
- [ ] MPE support
- [ ] SysEx patch storage
- [ ] Program change → sequence select

**Utilities:**
- [ ] On-board tuner (via ADC)
- [ ] Scale selection (chromatic, major, minor, modes)
- [ ] Clock divider outputs
- [ ] Trigger generator on unused GPIO

### Communication Protocol (LPC2361 ↔ Pico)

**UART: 115200 baud, 8N1**

```c
// Message format: [CMD] [LENGTH] [DATA...] [CHECKSUM]

// Commands from LPC2361 to Pico (display updates)
#define CMD_CLEAR        0x01
#define CMD_TEXT         0x02  // + X, Y, length, string
#define CMD_BAR          0x03  // + X, Y, W, H, value (0-255)
#define CMD_SEQ_STEP     0x04  // + 16 bytes step data
#define CMD_NOTE         0x05  // + note_num, velocity
#define CMD_PARAM        0x06  // + param_id, value
#define CMD_BPM          0x07  // + bpm (uint16)
#define CMD_MODE         0x08  // + mode_id

// Commands from Pico to LPC2361 (control)
#define CMD_PICO_READY   0x80
#define CMD_CV_REQUEST   0x81  // Request CV value for display
#define CMD_MIDI_THRU    0x82  // + MIDI bytes to forward
#define CMD_CLOCK_TICK   0x83  // External clock tick
```

---

## Phase 8: Body Contacts & Circuit Bending (1 week)

### Prime Touch Points

| Location | Effect | Intensity |
|----------|--------|-----------|
| R309 area | Pitch variation/vibrato | Strong |
| TP55 (Internal CV) | Glitchy pitch jumps | Medium |
| Filter cutoff CV | Manual wah | Medium |
| Brute Factor circuit | Touch-sensitive distortion | Strong |
| C107, C106, C111 | Metalizer timbre | Strong |
| R28 area | VCA response | Subtle |

### Installation

1. Drill 8× M4 holes in top panel
2. Install brass bolts with nylon insulating washers
3. Wire each bolt to designated circuit point via 22AWG stranded
4. Optional: Add 100kΩ pot in series for variable intensity

### Advanced: Dual-Point Interactions

Wire pairs of contacts together through a resistor to create coupled modulation:
- LFO Speed + Filter Cutoff → Cross-modulation
- Metalizer stages → Touch-controlled wavefolding

---

## Phase 9: Panel Fabrication (2 weeks)

### New Panel Elements

| Element | Quantity | Location |
|---------|----------|----------|
| 3.5mm jacks | 16 | Side panel or rear |
| Pots | 7 | Near related controls |
| Toggle switches | 6 | Metalizer area |
| OLED window | 1 | Logo area (80×15mm) |
| Body contacts | 8 | Top panel |
| MIDI DIN | 1 | Rear panel |

### Options

1. **Custom metal panel** — CNC or laser cut, powder coated
2. **3D printed panel** — PETG for durability
3. **Acrylic overlay** — Clear or smoked
4. **Drill existing panel** — Most practical for iterative changes

### OLED Window Construction

1. Mark logo area outline from inside
2. Drill corner holes
3. Cut with Dremel rotary tool
4. File edges smooth
5. Install 3D-printed bezel
6. Cover with 0.5mm polycarbonate sheet
7. Mount OLED behind with double-sided tape

---

## Phase 10: Integration & Testing (2 weeks)

### System Test Checklist

**Analog Section:**
- [ ] All waveform outputs present and correct
- [ ] VCA CV responds to external voltage
- [ ] Metalizer insert works (wet/dry switching)
- [ ] Output protection doesn't affect tone
- [ ] Body contacts produce desired effects

**Digital Section:**
- [ ] OLED displays correctly
- [ ] Pico communicates with LPC2361
- [ ] CV outputs calibrated (1V/octave if used for pitch)
- [ ] MIDI input/output/thru all function

**Firmware:**
- [ ] Keyboard scanning works
- [ ] Sequencer plays back correctly
- [ ] All MIDI functions work
- [ ] No crashes or hangs after hours of use

### Calibration Procedure

1. **CV Output Calibration** (Pico PWM→CV)
   - Connect to tuner or oscilloscope
   - Adjust trimmer for correct range (0-10V)
   - Verify linearity across range

2. **Pitch CV Tracking** (if custom firmware)
   - Use MIDI note 36 (C2) as reference
   - Verify octave intervals: 36→48→60→72

3. **Gate Timing**
   - Verify gate rises within 1ms of note-on
   - Verify gate falls within 1ms of note-off

---

# PART 3: ANALOG MODIFICATIONS CHECKLIST

## Complete Mod List with Status Tracking

### Tier 1 — Essential (Week 1)

| # | Mod | Status | Notes |
|---|-----|--------|-------|
| 1.1 | Output Protection (10kΩ) | ☐ | Cut trace UB5 pin 5, wire via resistor |
| 1.2 | VCA CV Input | ☐ | Wire TP10/TP11 to 3.5mm jack |
| 1.3 | Portamento on Ext CV | ☐ | Reroute CV through pitch socket |

### Tier 2 — High Value (Week 2)

| # | Mod | Status | Notes |
|---|-----|--------|-------|
| 2.1 | VCO Mix Output (buffered) | ☐ | Repurpose unused UB6 half |
| 2.2 | VCO Master Volume | ☐ | B100K pot replaces R76 |
| 2.3 | Metalizer Output | ☐ | TP109 → 1kΩ → jack |
| 2.4 | Saw Output | ☐ | TP94 → 1kΩ → jack |
| 2.5 | Triangle Output | ☐ | TP124 → 1kΩ → jack |
| 2.6 | Square Output | ☐ | TP93 → 1kΩ → jack |
| 2.7 | Sub Output | ☐ | TP102 → 1kΩ → jack |
| 2.8 | Metalizer Input Insert | ☐ | Remove R216, switched jack |

### Tier 3 — Sound Design (Week 5)

| # | Mod | Status | Notes |
|---|-----|--------|-------|
| 3.1 | Metalizer Boost | ☐ | 100kΩ across R216 + switch |
| 3.2 | Metalizer Timbre 1 | ☐ | 30kΩ across C111 + switch |
| 3.3 | Metalizer Timbre 2 | ☐ | 30kΩ across C107 + switch |
| 3.4 | Metalizer Timbre 3 | ☐ | 30kΩ across C106 + switch |
| 3.5 | Metalizer Timbre 4 | ☐ | 30kΩ across C110 + switch |
| 3.6 | Fast Portamento | ☐ | 470nF replaces C38 (4.7µF) |
| 3.7 | VCA Insert | ☐ | Remove R23, switched jack |
| 3.8 | VCA Boost | ☐ | 50kΩ + B50K replaces R28 |
| 3.9 | Extended Tuning | ☐ | 100kΩ replaces R309 (1MΩ) |

### Tier 4 — Advanced (Week 6)

| # | Mod | Status | Notes |
|---|-----|--------|-------|
| 4.1 | Square Phase Fix | ☐ | Swap UB15 inputs |
| 4.2 | Seq Decoupling | ☐ | 2N3906 + resistors |
| 4.3 | MIDI Out | ☐ | LPC2361 pin 82 → DIN socket |
| 4.4 | White Noise | ☐ | BC547 avalanche + buffer |
| 4.5 | Sample & Hold | ☐ | CD4066 + cap + opamp |
| 4.6 | Clock Divider | ☐ | CD4017 + CD4024 |

### Body Contacts (Week 7)

| # | Location | Effect | Status |
|---|----------|--------|--------|
| B1 | R309 area | Pitch bend | ☐ |
| B2 | TP55 | CV glitch | ☐ |
| B3 | Filter CV | Manual wah | ☐ |
| B4 | Brute Factor | Distortion touch | ☐ |
| B5 | C111 | Metalizer mod | ☐ |
| B6 | C107 | Metalizer mod | ☐ |
| B7 | R28 area | VCA touch | ☐ |
| B8 | Spare | TBD | ☐ |

---

# PART 4: CUSTOM FIRMWARE (MACROBRUTE OS)

## LPC2361 Specifications

| Parameter | Value |
|-----------|-------|
| Core | ARM7TDMI-S (32-bit RISC) |
| Flash | 64KB |
| SRAM | 34KB |
| Max Clock | 72 MHz |
| UARTs | 4 |
| I2C | 3 buses |
| SPI | 2 |
| ADC | 10-bit, 8 channels |
| DAC | 10-bit, 1 channel |
| GPIO | 70 pins |
| Debug | JTAG (populated!) |

## Code Read Protection (CRP)

**Address:** 0x1FC (in flash)

| Value | Level | Effect |
|-------|-------|--------|
| 0xFFFFFFFF | None | Full JTAG/ISP access ✅ |
| 0x12345678 | CRP1 | JTAG disabled, partial ISP |
| 0x87654321 | CRP2 | JTAG disabled, erase only |
| 0x43218765 | CRP3 | **BRICK RISK** — Avoid! |

## Development Toolchain

### Required Software

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install gcc-arm-none-eabi gdb-multiarch openocd \
    build-essential cmake git python3 python3-pip

# Flash Magic (NXP official ISP programmer)
# Download from: https://www.flashmagictool.com/

# Ghidra (for disassembly)
# Download from: https://ghidra-sre.org/
```

### JTAG Adapter Options

| Adapter | Price | Notes |
|---------|-------|-------|
| J-Link EDU Mini | €20 | Recommended — excellent OpenOCD support |
| Black Magic Probe | €60 | Built-in GDB server |
| FT2232H Breakout | €15 | DIY option, more setup |
| ST-Link V2 Clone | €5 | May work with adapter, not ideal |

## Firmware Structure

```
/uberbrute-firmware
├── src/
│   ├── main.c                 # Main entry, system init
│   ├── startup.s              # Vector table, reset handler
│   ├── syscalls.c             # Newlib syscall stubs
│   ├── drivers/
│   │   ├── gpio.c/h           # GPIO configuration
│   │   ├── uart.c/h           # UART for MIDI + Pico comms
│   │   ├── dac.c/h            # 10-bit DAC for pitch CV
│   │   ├── adc.c/h            # ADC for keyboard matrix
│   │   ├── timer.c/h          # System tick, PWM
│   │   └── ssp.c/h            # SPI if needed
│   ├── synth/
│   │   ├── keyboard.c/h       # Matrix scanning
│   │   ├── sequencer.c/h      # Step sequencer engine
│   │   ├── midi.c/h           # MIDI parser and handler
│   │   ├── cv_engine.c/h      # CV/Gate generation
│   │   └── arpeggiator.c/h    # Arp patterns
│   ├── ui/
│   │   ├── pico_protocol.c/h  # Communication with Pico
│   │   └── params.c/h         # Parameter storage
│   └── utils/
│       ├── ring_buffer.c/h    # MIDI/UART buffering
│       └── math_utils.c/h     # Pitch tables, etc.
├── include/
│   └── lpc2361.h              # Register definitions
├── linker/
│   └── lpc2361.ld             # Memory layout
├── Makefile
└── openocd.cfg
```

## Key Functions to Implement

### Keyboard Scanning

```c
// The keyboard is a matrix scanned by the MCU
// Need to reverse engineer the exact pin mapping
void keyboard_scan(void) {
    for (int col = 0; col < NUM_COLS; col++) {
        // Drive column low
        gpio_set(col_pins[col], 0);
        
        // Read all rows
        for (int row = 0; row < NUM_ROWS; row++) {
            uint8_t pressed = !gpio_get(row_pins[row]);
            // Update key state machine
            key_update(row * NUM_COLS + col, pressed);
        }
        
        // Release column
        gpio_set(col_pins[col], 1);
    }
}
```

### DAC Output for Pitch CV

```c
// LPC2361 has 10-bit DAC on pin P0.26
// 0-1023 maps to 0-3.3V (buffered to 0-10V externally)
void dac_set_cv(uint16_t value) {
    // DAC register at 0xE006C000
    LPC_DAC->DACR = (value & 0x3FF) << 6;
}

// MIDI note to DAC value (1V/octave, 12-bit resolution scaled to 10-bit)
uint16_t note_to_dac(uint8_t note) {
    // Middle C (note 60) = ~2V = ~620 DAC counts
    // Each semitone = 1/12 V = ~8.5 counts
    return (uint16_t)(note * 8.5f + offset);
}
```

### Sequencer Core

```c
typedef struct {
    uint8_t note;          // MIDI note number
    uint8_t velocity;      // 0-127
    uint8_t gate_length;   // 0-100%
    uint8_t probability;   // 0-100%
    uint8_t ratchet;       // 1-8 repeats
    uint8_t flags;         // Tie, rest, etc.
} SequencerStep;

typedef struct {
    SequencerStep steps[128];
    uint8_t length;
    uint8_t current_step;
    uint16_t tempo_bpm;
    uint8_t swing;
} Sequencer;

void sequencer_tick(Sequencer* seq) {
    SequencerStep* step = &seq->steps[seq->current_step];
    
    // Check probability
    if (random_percent() <= step->probability) {
        // Play note
        dac_set_cv(note_to_dac(step->note));
        gate_on();
        
        // Schedule gate off based on gate_length
        timer_schedule(calculate_gate_time(step->gate_length), gate_off);
    }
    
    // Advance step
    seq->current_step = (seq->current_step + 1) % seq->length;
}
```

## Recovery Methods

### Method 1: JTAG Reflash

```bash
# Connect via OpenOCD
openocd -f lpc2361_microbrute.cfg

# In telnet session
> halt
> flash write_image erase firmware.bin 0x0
> reset run
```

### Method 2: ISP via UART

If JTAG is disabled (CRP1/CRP2), use In-System Programming:

1. Connect UART to P0.0 (TXD0) and P0.1 (RXD0)
2. Pull ISP enable pin low during reset
3. Use Flash Magic software to reprogram

### Method 3: USB DFU (Arturia Method)

If all else fails:
1. Download Arturia firmware update
2. Use Arturia's update tool
3. Original firmware restored

---

# PART 5: PI PICO EXPANSION CONTROLLER

## Why Pi Pico?

| Feature | Benefit |
|---------|---------|
| Dual-core 133MHz | One core for display, one for I/O |
| 264KB SRAM | Large frame buffer |
| Native USB | Debug without UART |
| 16 PWM channels | Multiple CV outputs |
| PIO | Custom protocols |
| $4 | Cheaper than alternatives |

## Pico Development Setup

```bash
# Install Pico SDK
cd ~
git clone https://github.com/raspberrypi/pico-sdk.git
cd pico-sdk
git submodule update --init

# Set environment variable
echo 'export PICO_SDK_PATH=~/pico-sdk' >> ~/.bashrc
source ~/.bashrc

# Install build tools
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi
```

## Display Driver (SH1122)

```c
// SH1122 256x64 grayscale OLED initialization
void sh1122_init(void) {
    // Reset
    gpio_put(OLED_RST, 0);
    sleep_ms(10);
    gpio_put(OLED_RST, 1);
    sleep_ms(10);
    
    // Init sequence
    sh1122_cmd(0xAE);        // Display off
    sh1122_cmd(0x40);        // Start line 0
    sh1122_cmd(0xA0);        // Remap
    sh1122_cmd(0xC8);        // COM scan direction
    sh1122_cmd(0x81);        // Contrast
    sh1122_cmd(0x80);        // Medium contrast
    sh1122_cmd(0xA4);        // Normal display
    sh1122_cmd(0xA6);        // Non-inverted
    sh1122_cmd(0xAF);        // Display on
}

// Draw text using U8g2 library
void display_text(uint8_t x, uint8_t y, const char* str) {
    u8g2_DrawStr(&u8g2, x, y, str);
}

// Sequencer step display
void display_sequencer(Sequencer* seq) {
    for (int i = 0; i < 16; i++) {
        uint8_t x = i * 16;
        uint8_t height = seq->steps[i].note / 2;
        
        // Highlight current step
        if (i == seq->current_step) {
            u8g2_DrawBox(&u8g2, x, 64-height, 14, height);
        } else {
            u8g2_DrawFrame(&u8g2, x, 64-height, 14, height);
        }
    }
}
```

## CV Output Generation

```c
// PWM to CV conversion
// PWM at 1.9kHz, 16-bit resolution → filtered to analog

void cv_init(void) {
    // Configure PWM on GP10-13
    for (int i = 0; i < 4; i++) {
        gpio_set_function(CV_PINS[i], GPIO_FUNC_PWM);
        uint slice = pwm_gpio_to_slice_num(CV_PINS[i]);
        
        // 125MHz / 65536 ≈ 1907 Hz
        pwm_set_wrap(slice, 65535);
        pwm_set_enabled(slice, true);
    }
}

void cv_set(uint8_t channel, uint16_t value) {
    // value: 0-65535 maps to 0-3.3V (scaled to 0-10V by opamp)
    pwm_set_gpio_level(CV_PINS[channel], value);
}

// Convert voltage to PWM value
// For 10V range with 3.03x opamp gain
uint16_t voltage_to_pwm(float volts) {
    float pico_volts = volts / 3.03;  // Scale down
    return (uint16_t)(pico_volts / 3.3 * 65535);
}
```

---

# PART 6: OLED DISPLAY INTEGRATION

## Recommended Display: 2.08" SH1122 256×64

| Parameter | Value |
|-----------|-------|
| Controller | SH1122 |
| Resolution | 256×64 pixels |
| Colors | 16-level grayscale |
| Interface | SPI (required for speed) |
| Module PCB | 75.5 × 19.35 mm |
| Active Area | 51.18 × 12.78 mm |
| Price | €8-15 |

## Mounting in Logo Area

**Logo cutout:** ~80 × 15 mm

**Fit analysis:** The active area (51 × 13 mm) fits easily. The PCB (75.5 × 19.35 mm) is slightly too tall — solutions:

1. **Trim PCB edge** (if header on one side)
2. **Recess into case** (angle mount)
3. **Use COG bare panel** (60.5 × 19 mm) with FPC adapter

## Display Content Ideas

### Performance Mode
```
┌──────────────────────────────────────────────────┐
│ SEQ:03  BPM:120  ▶   C#3  GATE ████████░░        │
└──────────────────────────────────────────────────┘
```

### Sequencer Edit
```
┌──────────────────────────────────────────────────┐
│ ▓▓ ░░ ▓▓ ░░ ▓░ ▓▓ ░░ ▓▓  STEP:05 C#3 VEL:100   │
└──────────────────────────────────────────────────┘
```

### Parameter Edit
```
┌──────────────────────────────────────────────────┐
│ CUTOFF  ███████████████░░░░░░░░░░░░  65%        │
└──────────────────────────────────────────────────┘
```

### Tuner
```
┌──────────────────────────────────────────────────┐
│          ◄────●────►  A4  +5¢                   │
└──────────────────────────────────────────────────┘
```

---

# PART 7: WIRING PLAN & TEST POINTS

## MicroBrute Test Point Map

### VCO Section (Rear Board)

| TP | Signal | Purpose |
|----|--------|---------|
| TP93 | Square wave | VCO output |
| TP94 | Sawtooth wave | VCO output |
| TP102 | Sub oscillator | Sub/fifth output |
| TP124 | Triangle wave | VCO output |
| TP109 | Metalizer out | Post-wavefolder |

### Control Section

| TP | Signal | Purpose |
|----|--------|---------|
| TP10/TP11 | VCA CV | Pre-wired for CV injection |
| TP30 | VCO mix | Pre-filter waveform mix |
| TP55 | Pitch CV | Post-portamento |
| TP56 | Gate (front) | Internal gate |
| TP82 | Gate (rear) | Post-CPU gate |

### Power Rails (Rear Board)

| TP | Rail | Notes |
|----|------|-------|
| TP70 | +12V | Analog positive |
| TP71 | -12V | Analog negative |
| TP72 | GND | Ground reference |
| Near regulator | +3.3V | Digital rail |
| PSU-DIGITAL | +5V | USB/digital rail |

## Pi Pico Wiring Diagram

```
                    MICROBRUTE                              PI PICO
                    ─────────                              ────────
                    
    Power Section                                          
    ─────────────                                          
    +5V (PSU-DIGITAL) ───[1N5817]──────────────────────── VSYS (Pin 39)
    GND ──────────────────────────────────────────────── GND (Pin 38)
    
    UART Communication (if custom firmware)
    ────────────────────────────────────────
    LPC2361 UART TX ──────────[1kΩ]─────────────────── GP1 RX (Pin 2)
    LPC2361 UART RX ──────────[1kΩ]─────────────────── GP0 TX (Pin 1)
    
    OLED Display (SPI)
    ────────────────
                                     ┌──────────────── SCK  GP18 (Pin 24)
                                     │ ┌────────────── MOSI GP19 (Pin 25)
    3V3 (from Pico) ─────────────────┼─┼───────────── VCC
    GND ─────────────────────────────┼─┼───────────── GND
                                     │ │ ┌────────── CS   GP17 (Pin 22)
    OLED Module ◄────────────────────┴─┴─┼────────── DC   GP16 (Pin 21)
                                         └────────── RST  GP20 (Pin 26)
    
    CV Outputs (PWM → RC Filter → Opamp)
    ─────────────────────────────────────
    GP10 (Pin 14) ──[10k]─┬─[10k]─┬─[TL072+]──── CV OUT 1 (0-10V)
                         1µF    100nF
                         GND     GND
    
    GP11 (Pin 15) ──[same circuit]──────────────── CV OUT 2
    GP12 (Pin 16) ──[same circuit]──────────────── CV OUT 3
    GP13 (Pin 17) ──[same circuit]──────────────── CV OUT 4
    
    Analog Inputs (optional - for tuner, etc.)
    ─────────────────────────────────────────
    Audio tap ──[voltage divider]────────────── GP26 ADC0 (Pin 31)
    CV monitor ──[voltage divider]───────────── GP27 ADC1 (Pin 32)
```

## MIDI Out Wiring (LPC2361)

```
    LPC2361 Pin 82 (UART TX) ───────────────────┐
                                                │
    +3.3V ──────[100Ω]─────────────────────────┐│
                                               ││
                                          DIN-5│Socket (panel mount)
                                               ││
                                    Pin 4 ─────┘│
                                    Pin 5 ──────┘
                                    Pin 2 ───── GND
```

**Note:** Pin 82 is TINY (0.5mm pitch QFP). Requires:
- Fine tip soldering iron
- Magnification (3.5x minimum)
- Flux
- 0.5mm or thinner solder

---

# PART 8: COMPLETE BILL OF MATERIALS

## Summary by Section

| Section | Subtotal |
|---------|----------|
| Pi Pico Expansion Controller | ~€90 |
| Analog Modifications | ~€52 |
| Firmware Development Tools | ~€85 |
| Tools (if buying all new) | ~€365 |
| **Components Only Total** | **~€227** |
| **With Tools Total** | **~€592** |

---

## Firmware Development Tools BOM

### JTAG Debugger

| # | Component | Qty | Price | Source |
|---|-----------|-----|-------|--------|
| 1 | **J-Link EDU Mini** | 1 | €20 | Segger/Mouser |
| 2 | 10-pin JTAG cable (1.27mm) | 1 | €2 | AliExpress |
| 3 | 10-pin IDC header (1.27mm) | 2 | €1 | AliExpress |

### ISP/Recovery (backup method)

| # | Component | Qty | Price | Source |
|---|-----------|-----|-------|--------|
| 4 | USB-TTL adapter (3.3V, CP2102) | 1 | €3 | AliExpress |
| 5 | Dupont jumper wires | 1 pack | €2 | AliExpress |

### CRP Bypass (optional, if needed)

| # | Component | Qty | Price | Source |
|---|-----------|-----|-------|--------|
| 6 | ChipWhisperer Lite | 1 | €200 | NewAE Technology |

*Note: CRP bypass only needed if Code Read Protection is enabled. Check first!*

### Development Hardware

| # | Component | Qty | Price | Source |
|---|-----------|-----|-------|--------|
| 7 | Breadboard (for prototyping) | 1 | €3 | Amazon |
| 8 | Logic analyzer (8ch, 24MHz) | 1 | €10 | AliExpress |
| 9 | Second MicroBrute (for comparison) | 1 | Optional | Used market |

### Software (Free)

- gcc-arm-none-eabi (ARM GNU Toolchain)
- OpenOCD
- GDB
- Ghidra (for disassembly)
- Flash Magic (NXP ISP tool)
- VSCode with Cortex-Debug extension

**Firmware Tools Subtotal: ~€40 minimum, ~€240 with CRP bypass kit**

---

## Pi Pico Expansion BOM (Full Detail)

### Core Hardware (~€34)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 1 | Raspberry Pi Pico (standard) | 1 | €4 | €4 | Pimoroni |
| 2 | 2.08" OLED SH1122 256×64 | 1 | €10 | €10 | AliExpress |
| 3 | J-Link EDU Mini | 1 | €20 | €20 | Segger |

### Connectors & Cables (~€17)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 4 | JST-PH 2.0mm 4-pin kit | 5 | €0.30 | €1.50 | AliExpress |
| 5 | JST-PH 2.0mm 6-pin kit | 3 | €0.40 | €1.20 | AliExpress |
| 6 | 10-pin JTAG cable 1.27mm | 1 | €2 | €2 | AliExpress |
| 7 | 28AWG silicone wire (8 colors) | 1 | €8 | €8 | AliExpress |
| 8 | 22AWG wire (red/black) | 1 | €4 | €4 | AliExpress |

### Power & Protection (~€3)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 9 | 1N5817 Schottky diode | 2 | €0.10 | €0.20 | TME |
| 10 | Ferrite bead 600Ω@100MHz | 4 | €0.15 | €0.60 | TME |
| 11 | 100nF MLCC 0805 | 10 | €0.05 | €0.50 | TME |
| 12 | 10µF MLCC 0805 | 4 | €0.15 | €0.60 | TME |
| 13 | BAT54S dual Schottky | 2 | €0.20 | €0.40 | TME |
| 14 | 3.3V Zener BZX84C3V3 | 2 | €0.10 | €0.20 | TME |

### CV Output Circuit (~€8)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 15 | 10kΩ resistor 1% 0805 | 12 | €0.02 | €0.24 | TME |
| 16 | 1µF film capacitor | 4 | €0.30 | €1.20 | TME |
| 17 | 100nF film capacitor | 4 | €0.15 | €0.60 | TME |
| 18 | TL072 dual op-amp DIP-8 | 2 | €0.50 | €1.00 | TME |
| 19 | DIP-8 socket | 2 | €0.15 | €0.30 | TME |
| 20 | 100kΩ trimmer Bourns 3296 | 4 | €0.80 | €3.20 | Mouser |

### Level Shifting (~€1.50)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 21 | BSS138 N-MOSFET SOT-23 | 4 | €0.15 | €0.60 | TME |
| 22 | 10kΩ resistor 0805 | 8 | €0.02 | €0.16 | TME |
| 23 | 1kΩ resistor 0805 | 10 | €0.02 | €0.20 | TME |
| 24 | 100Ω resistor 0805 | 2 | €0.02 | €0.04 | TME |

### Mounting (~€16)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 25 | M2x6mm brass standoff | 4 | €0.20 | €0.80 | AliExpress |
| 26 | M2x4mm screw | 8 | €0.05 | €0.40 | AliExpress |
| 27 | 3M VHB 5952 tape | 1 | €5 | €5 | Amazon |
| 28 | Kapton tape 10mm | 1 | €3 | €3 | Amazon |
| 29 | Heat shrink assortment | 1 | €4 | €4 | Amazon |
| 30 | Polycarbonate sheet 0.5mm | 1 | €3 | €3 | Amazon |

### Optional Expansion (~€12)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 31 | MCP4725 I2C DAC breakout | 2 | €3 | €6 | AliExpress |
| 32 | PT8211 I2S DAC | 1 | €1.50 | €1.50 | AliExpress |
| 33 | Copper tape (EMI shield) | 1 | €4 | €4 | Amazon |

---

## Analog Modifications BOM (Full Detail)

### Jacks (~€8)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 1 | Thonkiconn PJ398SM switched | 8 | €0.50 | €4 | Thonk |
| 2 | Thonkiconn PJ301M-12 | 8 | €0.40 | €3.20 | Thonk |
| 3 | Jack nuts | 16 | €0.05 | €0.80 | Thonk |

### Potentiometers (~€8)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 4 | B100K 9mm pot | 3 | €0.80 | €2.40 | Tayda |
| 5 | B50K 9mm pot | 2 | €0.80 | €1.60 | Tayda |
| 6 | B10K 9mm pot | 2 | €0.80 | €1.60 | Tayda |
| 7 | Knobs (6mm D-shaft) | 7 | €0.30 | €2.10 | Tayda |

### Switches (~€4)

| # | Component | Qty | Unit | Total | Source |
|---|-----------|-----|------|-------|--------|
| 8 | SPDT ON-ON toggle | 4 | €0.60 | €2.40 | Tayda |
| 9 | SPST momentary button | 2 | €0.30 | €0.60 | Tayda |
| 10 | DPDT ON-ON toggle | 1 | €0.80 | €0.80 | Tayda |

### Resistors (~€2)

| # | Value | Qty | Total | Purpose |
|---|-------|-----|-------|---------|
| 11 | 100Ω | 5 | €0.10 | MIDI |
| 12 | 1kΩ | 15 | €0.30 | Buffers |
| 13 | 2.2kΩ | 5 | €0.10 | Various |
| 14 | 10kΩ | 20 | €0.40 | Protection |
| 15 | 22kΩ | 10 | €0.20 | Gate mod |
| 16 | 47kΩ | 10 | €0.20 | Various |
| 17 | 100kΩ | 20 | €0.40 | Mixing |
| 18 | 120kΩ | 4 | €0.08 | Metalizer |
| 19 | 1MΩ | 5 | €0.10 | Various |
| 20 | 30kΩ | 4 | €0.08 | Metalizer |

### Capacitors (~€5)

| # | Value | Type | Qty | Total | Purpose |
|---|-------|------|-----|-------|---------|
| 21 | 470nF | Film | 2 | €0.50 | Portamento |
| 22 | 100nF | Ceramic | 20 | €0.60 | Decoupling |
| 23 | 10nF | Film | 10 | €1.00 | Various |
| 24 | 1µF | Film | 4 | €1.20 | S&H |
| 25 | 10µF | Electrolytic | 10 | €0.80 | Power |
| 26 | 100µF | Electrolytic | 4 | €0.48 | Power |
| 27 | 4.7µF | Film | 1 | €0.40 | Spare |

### Semiconductors (~€10)

| # | Component | Qty | Unit | Total | Purpose |
|---|-----------|-----|------|-------|---------|
| 28 | TL072 DIP-8 | 4 | €0.45 | €1.80 | Buffers |
| 29 | TL074 DIP-14 | 2 | €0.60 | €1.20 | Processing |
| 30 | LM13700 DIP-16 | 2 | €1.50 | €3.00 | VCA/VCO |
| 31 | CD4066 DIP-14 | 2 | €0.40 | €0.80 | S&H |
| 32 | CD4017 DIP-16 | 1 | €0.35 | €0.35 | Clock div |
| 33 | CD4024 DIP-14 | 1 | €0.35 | €0.35 | Clock div |
| 34 | BC547 NPN | 5 | €0.08 | €0.40 | Noise |
| 35 | BC557 PNP | 5 | €0.08 | €0.40 | Various |
| 36 | 2N3906 PNP | 2 | €0.10 | €0.20 | Seq decoup |
| 37 | 1N4148 diode | 20 | €0.03 | €0.60 | Protection |

### IC Sockets (~€2)

| # | Type | Qty | Unit | Total |
|---|------|-----|------|-------|
| 38 | DIP-8 socket | 6 | €0.10 | €0.60 |
| 39 | DIP-14 socket | 4 | €0.12 | €0.48 |
| 40 | DIP-16 socket | 4 | €0.15 | €0.60 |

### Body Contacts (~€5)

| # | Component | Qty | Unit | Total |
|---|-----------|-----|------|-------|
| 41 | M4x20mm brass bolt | 8 | €0.15 | €1.20 |
| 42 | M4 brass nut | 8 | €0.08 | €0.64 |
| 43 | M4 nylon washer | 16 | €0.05 | €0.80 |
| 44 | B100K pot (variable) | 2 | €0.80 | €1.60 |

### MIDI Out (~€2)

| # | Component | Qty | Unit | Total |
|---|-----------|-----|------|-------|
| 45 | 5-pin DIN socket | 1 | €1.00 | €1.00 |
| 46 | 6N138 optocoupler | 1 | €0.80 | €0.80 |

### Prototyping (~€12)

| # | Component | Qty | Unit | Total |
|---|-----------|-----|------|-------|
| 47 | Stripboard 100×50mm | 3 | €1.50 | €4.50 |
| 48 | Breadboard 830pt | 1 | €3 | €3 |
| 49 | Male headers 40-pin | 5 | €0.20 | €1.00 |
| 50 | Female headers 40-pin | 5 | €0.25 | €1.25 |
| 51 | M3x8mm standoff | 10 | €0.15 | €1.50 |
| 52 | M3x6mm screw | 20 | €0.03 | €0.60 |

---

# PART 9: DEVELOPMENT ENVIRONMENT SETUP

## Linux Workstation (Recommended)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# ARM toolchain
sudo apt install gcc-arm-none-eabi gdb-multiarch

# Build tools
sudo apt install build-essential cmake git

# OpenOCD (JTAG/SWD debugger)
sudo apt install openocd

# Ghidra dependencies
sudo apt install openjdk-17-jdk

# Download Ghidra
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.1_build/ghidra_11.0.1_PUBLIC_20240130.zip
unzip ghidra_11.0.1_PUBLIC_20240130.zip

# VSCode
sudo snap install code --classic

# Install VSCode extensions
code --install-extension marus25.cortex-debug
code --install-extension ms-vscode.cpptools

# Pico SDK
git clone https://github.com/raspberrypi/pico-sdk.git ~/pico-sdk
cd ~/pico-sdk && git submodule update --init
echo 'export PICO_SDK_PATH=~/pico-sdk' >> ~/.bashrc
```

## Project Repository Structure

```
/uberbrute-project
├── /firmware-lpc2361           # Custom MicroBrute firmware
│   ├── /src
│   ├── /include
│   ├── /linker
│   ├── Makefile
│   └── openocd.cfg
│
├── /firmware-pico              # Pi Pico expansion firmware
│   ├── /src
│   ├── /lib
│   ├── CMakeLists.txt
│   └── pico_sdk_import.cmake
│
├── /hardware
│   ├── /schematics             # MicroBrute schematics (reference)
│   ├── /pcb-photos             # Annotated PCB documentation
│   ├── /panel-design           # Custom panel CAD files
│   └── /wiring-diagrams        # Connection diagrams
│
├── /docs
│   ├── mod-guides/             # Individual mod documentation
│   ├── firmware-notes/         # Reverse engineering notes
│   └── calibration/            # Calibration procedures
│
├── /original-firmware          # Backed up factory firmware
│   └── microbrute_v1.x.bin
│
├── /tools
│   ├── openocd-configs/
│   └── scripts/
│
└── README.md
```

## OpenOCD Launch Configuration

**launch.json (VSCode):**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug LPC2361",
            "type": "cortex-debug",
            "request": "launch",
            "servertype": "openocd",
            "cwd": "${workspaceRoot}",
            "executable": "${workspaceRoot}/firmware-lpc2361/build/uberbrute.elf",
            "configFiles": [
                "${workspaceRoot}/tools/openocd-configs/lpc2361_microbrute.cfg"
            ],
            "svdFile": "${workspaceRoot}/tools/svd/LPC2361.svd",
            "runToMain": true
        }
    ]
}
```

---

# PART 10: SAFETY & RECOVERY PROCEDURES

## Before Starting Any Work

1. **Photo everything** — Document original state
2. **Backup firmware** — If CRP allows, dump before any changes
3. **Have recovery plan** — Know how to restore functionality
4. **Work incrementally** — One mod at a time, test between each

## Power Safety

- Always disconnect power before soldering
- Wait 30 seconds for capacitors to discharge
- Verify no voltage before touching circuit

## Critical Components — Do Not Damage

| Component | Risk | Recovery |
|-----------|------|----------|
| LPC2361 | Dead synth | Replace IC (~€10) but requires SMD rework |
| VCO transistors | No oscillator | Identify and replace specific transistor |
| Power regulators | No power | Replace regulator |
| DAC output opamp | No CV | Replace opamp |

## Emergency Recovery Procedures

### If Output Dies

1. Check output protection mod first
2. Verify opamp supply voltages (±12V present?)
3. Check for shorts to ground
4. Trace signal with oscilloscope from VCO → output

### If No Sound At All

1. Verify all power rails:
   - +12V at TP70
   - -12V at TP71
   - +5V at PSU-DIGITAL
   - +3.3V near LPC2361
2. Check VCO oscillating (scope on TP93/94)
3. Check gate voltage (scope on TP56)
4. Check VCA response

### If Firmware Corrupted

**Method 1: ISP Recovery (always available)**
1. Connect USB-TTL adapter to:
   - P0.0 (TXD0) → RX
   - P0.1 (RXD0) → TX
   - GND → GND
2. Ground ISP enable pin during power-up
3. Use Flash Magic to reprogram
4. Load factory firmware or new custom firmware

**Method 2: USB DFU (Arturia method)**
1. Download Arturia firmware update
2. Run Arturia's update utility
3. Follow on-screen instructions
4. Factory firmware restored

### If Pi Pico Crashes

1. Hold BOOTSEL button while connecting USB
2. Pico appears as mass storage
3. Drag new .uf2 firmware file to drive
4. Pico automatically reboots

### Worst Case: Replace LPC2361

If the MCU is truly dead (very rare):
1. Order LPC2361FBD100 from Mouser (~€10)
2. Remove old chip with hot air station (careful!)
3. Clean pads with flux and wick
4. Align new chip, tack corners
5. Solder all pins carefully
6. Clean flux residue
7. Reprogram via ISP

**This requires SMD rework skills** — the backup plan, not Plan A.

---

# APPENDIX A: SUPPLIER QUICK REFERENCE

| Supplier | Best For | Notes |
|----------|----------|-------|
| **TME** (tme.eu) | ICs, passives | Fast EU shipping, Lithuanian interface |
| **Mouser** (mouser.co.uk) | Precision parts | Free >€50, huge selection |
| **Thonk** (thonk.co.uk) | Jacks, pots, knobs | Eurorack specialist |
| **Tayda** (tayda.com) | Budget passives | 2-3 week shipping |
| **AliExpress** | Pico, OLED, wire | Quality varies, 2-4 weeks |
| **Pimoroni** | Pi Pico | Fast UK shipping |
| **Segger** | J-Link EDU Mini | Official source |

---

# APPENDIX B: ESSENTIAL LINKS

- **MicroBrute Schematics:** https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- **Maffez Pedrobrute:** https://maffez.com/?page_id=2285
- **ModWiggler Thread:** https://modwiggler.com/forum/viewtopic.php?t=152071
- **LPC2361 Datasheet:** https://www.nxp.com/docs/en/data-sheet/LPC2361_62.pdf
- **LPC2300 User Manual:** https://www.keil.com/dd/docs/datashts/philips/lpc23xx_um.pdf
- **Pico SDK:** https://github.com/raspberrypi/pico-sdk
- **U8g2 Graphics Library:** https://github.com/olikraus/u8g2
- **OpenOCD:** https://openocd.org/
- **Ghidra:** https://ghidra-sre.org/

---

**Document Version:** 2.0  
**Last Updated:** March 2026  
**Project:** MACROBRUTE  
**Author:** jordanaftermidnight

*"The MicroBrute is just the beginning. What we build is the MACROBRUTE."*
