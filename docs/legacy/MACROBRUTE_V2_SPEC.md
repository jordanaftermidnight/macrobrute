# MACROBRUTE V2 — Complete System Specification
## Custom Firmware + Pico Expansion + Analog Mods

*Version 2.0 — Consolidated from all sessions*
*Project Lead: Jordan (Semitone Autonomy)*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Hardware Inventory](#2-hardware-inventory)
3. [IC Assignments](#3-ic-assignments)
4. [Pico + OLED Integration](#4-pico--oled-integration)
5. [Firmware Features (MI-Inspired)](#5-firmware-features-mi-inspired)
6. [Analog Modifications](#6-analog-modifications)
7. [Wiring Diagrams](#7-wiring-diagrams)
8. [Development Roadmap](#8-development-roadmap)
9. [Resource Budget](#9-resource-budget)
10. [Reference Links](#10-reference-links)

---

## 1. Project Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MACROBRUTE SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │      LPC2361 (Main Brain)       │   │      Pi Pico H (Expansion)      │  │
│  │      Custom Firmware            │   │      Display + Extras           │  │
│  │                                 │   │                                 │  │
│  │  • Keyboard matrix scanning     │   │  • 0.96" SSD1306 OLED           │  │
│  │  • 64-step sequencer engine     │   │  • UI state machine             │  │
│  │  • MI-style arpeggiator         │   │  • Clock output generation      │  │
│  │  • Weighted scale quantizer     │   │  • CV output (PWM+filter)       │  │
│  │  • Euclidean rhythm gating      │   │  • Pattern backup/restore       │  │
│  │  • Probability per step         │   │                                 │  │
│  │  • Turing Machine mode          │   │                                 │  │
│  │  • MIDI in/out                  │   │                                 │  │
│  │  • DAC: Pitch CV, Velocity CV   │   │                                 │  │
│  │                                 │   │                                 │  │
│  │  ARM7TDMI @ 72MHz               │   │  RP2040 @ 133MHz                │  │
│  │  128KB Flash / 34KB RAM         │   │  2MB Flash / 264KB RAM          │  │
│  └───────────────┬─────────────────┘   └─────────────────┬───────────────┘  │
│                  │         UART @ 115200                 │                  │
│                  └───────────────────────────────────────┘                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        ANALOG MODIFICATIONS                             ││
│  │  Tier 1: Output protection, VCA CV input, Portamento mod                ││
│  │  Tier 2: VCO mix out, Waveform breakouts, Metalizer I/O                 ││
│  │  Tier 3: Body contacts, Clock divider, MIDI Out                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Design Philosophy

- **Dual-processor architecture** — LPC2361 handles real-time synth control, Pico handles UI/display
- **Printf debugging** — No expensive JTAG required, uses ISP UART
- **Open source** — All code MIT licensed, contributor-friendly
- **Incremental build** — Can use Pico standalone before custom LPC firmware

---

## 2. Hardware Inventory

### Purchased/On Hand

| Item | Status | Notes |
|------|--------|-------|
| Raspberry Pi Pico H | ✅ Bought | Pre-soldered headers |
| PL2303HX USB-TTL 3.3V/5V | ✅ Bought | ISP programming |
| 0.96" SSD1306 OLED 128×64 I2C | ⏳ Ordered | Display |
| Joyo JF-33 Delay Pedal | ✅ On hand | Keep intact for now |

### IC Kit (New Purchase)

| IC | Qty | Package | Description |
|----|-----|---------|-------------|
| PC817c | 20 | DIP-4 | Photocoupler |
| ICL7660s | 2 | DIP-8 | Charge pump voltage converter |
| NE555 | 20 | DIP-8 | Timer/oscillator |
| LM358 | 10 | DIP-8 | Dual op-amp |
| LM324 | 10 | DIP-14 | Quad op-amp |
| JRC4558 | 10 | DIP-8 | Dual op-amp |
| LM393 | 10 | DIP-14 | Dual comparator |
| LM339 | 10 | DIP-8 | Quad comparator |
| NE5532 | 5 | DIP-8 | Low-noise dual op-amp |
| LM386m | 5 | DIP-8 | Audio power amplifier |
| TDA2030A | 2 | TO-220 | Power amplifier |
| TDA2822D | 5 | DIP-8 | Stereo amplifier |
| PT2399 | 3 | DIP-16 | Echo/delay processor |
| UC3842AN | 5 | DIP-8 | Current mode controller |
| UC3843AN | 5 | DIP-8 | Current mode controller |
| ULN2003AN | 5 | DIP-16 | Darlington array (7ch) |
| ULN2803APG | 5 | DIP-18 | Darlington array (8ch) |

**Sockets included:** DIP-4 ×2, DIP-8 ×7, DIP-14 ×3, DIP-16 ×3, DIP-18 ×2

### Previous Inventory (Confirmed)

| IC | Qty | Description |
|----|-----|-------------|
| CD4049UBE | 3 | Hex inverter/buffer |
| TL082CP | 2 | Dual JFET op-amp |
| TL074CN | 2 | Quad JFET op-amp |

### Passive Components (On Hand)

| Type | Values | Notes |
|------|--------|-------|
| Pots | B50K ×3, B10K ×4, B1M ×4 | Alpha-style |
| Jack sockets | Various | 3.5mm mono |
| Resistors | Assorted | Need to inventory |
| Capacitors | Assorted | Need to inventory |

---

## 3. IC Assignments

### Active ICs for MACROBRUTE

| IC | Qty Used | Subsystem | Function |
|----|----------|-----------|----------|
| **NE5532** | 1 | VCO Mix Output | Low-noise audio buffer |
| **TL074CN** | 1 | Waveform Breakouts | 4× buffers (Saw/Sq/Tri/Sub) |
| **TL082CP** | 1 | VCA CV Input | CV buffer/attenuator |
| **NE555** | 1-2 | Clock Output | Clock generator + optional divider |
| **LM393** | 1 | Gate Detection | Comparator for sync/trigger |
| **PC817** | 1 | MIDI Input | Optocoupler isolation |
| **CD4049UBE** | 1 | Waveshaping | Buffer/logic (circuit bending) |
| **ICL7660** | 1 | Power (if needed) | -5V from +5V for op-amp headroom |
| **LM386** | 1 | Body Contacts | High-gain amp for touch sensitivity |

**Total active ICs: 9-10**

### Reserved / Not Used

| IC | Reason |
|----|--------|
| PT2399 ×3 | Reserved for dual delay project |
| LM358 | TL082 preferred for CV work |
| LM324 | TL074 preferred for audio |
| LM339 | Have LM393, sufficient |
| JRC4558 | Reserved for delay project |
| ULN2003/2803 | Overkill for LEDs |
| UC3842/43 | SMPS controllers, not needed |
| TDA2030A/2822D | Power amps, not needed |

---

## 4. Pico + OLED Integration

### Hardware Configuration

```
┌──────────────────┐      ┌───────────────┐
│    Pico H        │      │  SSD1306 OLED │
│                  │      │   128×64 I2C  │
│  Pin 36 (3V3) ───┼──────┼── VCC         │
│  Pin 38 (GND) ───┼──────┼── GND         │
│  GP4 (Pin 6)  ───┼──────┼── SDA         │
│  GP5 (Pin 7)  ───┼──────┼── SCL         │
│                  │      └───────────────┘
│  GP0 (Pin 1)  ───┼────── TX → LPC2361 RX (P0.1)
│  GP1 (Pin 2)  ───┼────── RX ← LPC2361 TX (P0.0)
│                  │
│  GP2 (Pin 4)  ───┼────── Clock Out (3.5mm jack)
│  GP3 (Pin 5)  ───┼────── Gate indicator LED
│                  │
│  GP6-GP9      ───┼────── Encoder (optional, future)
└──────────────────┘
```

### Display Layout (128×64)

```
┌────────────────────────────────┐
│ BPM:120  ▶ PLAY   PATT:01      │  Line 0: Status bar
│ ════════════════════════════   │  Line 1: Divider
│ STEP: 05/64      C#3           │  Line 2: Position + Note
│ VEL:100  PROB:75%  RATCH:2     │  Line 3: Step params
│ [█ █ █ ░ █ ░ █ █ █ ░ █ █ ░ █]  │  Line 4-5: Pattern viz
│ [░ █ ░ █ ░ █ █ ░ █ █ ░ █ █ ░]  │
│ ════════════════════════════   │  Line 6: Divider
│ SCALE: MINOR    SWING: 60%     │  Line 7: Global params
└────────────────────────────────┘
```

### Pico Firmware Features

1. **Display driver** — SSD1306 I2C, 10fps refresh
2. **UART protocol** — Receive state from LPC2361
3. **Clock output** — PWM-based, 1-999 BPM
4. **Pattern visualization** — 16-step view with scroll
5. **Mode indicator** — Play/Stop/Record/Edit states
6. **Future: Encoder input** — Menu navigation

---

## 5. Firmware Features (MI-Inspired)

### Sequencer

| Feature | Stock | MACROBRUTE | Implementation |
|---------|-------|-----------|----------------|
| Steps | 8 | **64** | Extended struct |
| Patterns | 8 | **16** | Flash IAP storage |
| Directions | Fwd | **Fwd/Rev/Ping/Rand** | State machine |
| Swing | No | **0-75%** | Odd step delay |
| Probability | No | **Per-step 0-100%** | LFSR comparison |
| Ratchet | No | **1-8× per step** | Subdivision counter |
| Ties/Slides | Basic | **Per-step flags** | Step struct bits |
| Scale quantize | No | **40+ scales** | MI Braids quantizer |
| Euclidean | No | **Overlay gating** | LUT or Bjorklund |
| Motion record | No | **4 params** | 1 byte/step/param |

### Arpeggiator (Ported from MI Yarns)

```c
// NoteStack: 16-note polyphonic input tracking
typedef struct {
    uint8_t notes[16];
    uint8_t velocities[16];
    uint8_t size;
} NoteStack;

// Arp modes
typedef enum {
    ARP_UP,
    ARP_DOWN,
    ARP_UP_DOWN,
    ARP_DOWN_UP,
    ARP_RANDOM,
    ARP_AS_PLAYED,
    ARP_CHORD
} ArpMode;
```

- **Octave range:** 1-4 octaves
- **Rhythmic patterns:** 16 presets via bitmask
- **Euclidean mode:** Generate rhythm from k/n
- **Latch:** Hold notes after release

### Quantizer (Ported from MI Braids)

```c
// 7-bit sub-semitone resolution
// pitch = midi_note << 7 (128 values per semitone)

typedef struct {
    int16_t codebook[128];
    uint8_t num_notes;
    int16_t previous_note;  // For hysteresis
} Quantizer;

// Hysteresis: 56.25%/43.75% to prevent oscillation
```

**Included scales:**
- Western: Major, Minor (nat/harm/mel), Pentatonic, Blues
- Modes: Dorian, Phrygian, Lydian, Mixolydian, Locrian
- Exotic: Whole tone, Diminished, Augmented
- World: Hirajoshi, Iwato, Kumoi, Pelog, Slendro
- Indian: Bhairav, Marwa, Todi

### Euclidean Patterns

```c
// Runtime calculation (zero RAM):
static inline uint8_t euclid_hit(uint8_t pulses, uint8_t length, 
                                  uint8_t rotation, uint8_t step) {
    return ((pulses * ((step + rotation) % length)) % length) 
           + pulses >= length ? 1 : 0;
}
```

- **Length:** 1-64 steps
- **Pulses:** 0 to length
- **Rotation:** Shift pattern start

### Turing Machine (Generative Mode)

```c
typedef struct {
    uint16_t shift_register;  // 16-bit pattern
    uint8_t probability;      // 0=invert, 128=random, 255=lock
    uint8_t length;           // 2-16 active bits
} TuringMachine;

void turing_step(TuringMachine* tm) {
    uint8_t msb = (tm->shift_register >> (tm->length - 1)) & 1;
    if (random8() > tm->probability) msb ^= 1;
    tm->shift_register = (tm->shift_register << 1) | msb;
}
```

### Hidden Features / Easter Eggs

| Trigger | Feature |
|---------|---------|
| Hold Oct+ & Oct- @ boot | Recovery mode / factory reset |
| Knob position handshake + long press | Unlock alternate mode |
| Play specific note sequence | Hidden Turing Machine mode |
| All knobs to specific positions | Diagnostic / calibration mode |

---

## 6. Analog Modifications

### Tier 1 — Essential (Do First)

| Mod | Description | Components | Difficulty |
|-----|-------------|------------|------------|
| **Output Protection** | Prevent damage from hot-plugging | 10kΩ resistor, cut trace UB5 pin 5 | Easy |
| **VCA CV Input** | External amplitude control | 3.5mm jack, wire to TP10/TP11 | Easy |
| **Portamento on Ext CV** | Glide affects external CV | Reroute internal CV path | Medium |

### Tier 2 — High Value

| Mod | Description | Components | Difficulty |
|-----|-------------|------------|------------|
| **VCO Mix Output** | Buffered pre-filter output | NE5532, 3.5mm jack | Medium |
| **Waveform Breakouts** | Individual wave outputs | TL074CN, 4× 3.5mm jacks, 4× 1kΩ | Medium |
| **Metalizer Output** | Raw metalizer signal | 1kΩ, 3.5mm jack at TP109 | Easy |
| **Metalizer Input** | External signal into metalizer | Remove R216, switched jack | Medium |
| **VCO Master Volume** | Pre-filter level control | B100K pot replaces R76 | Medium |

**Waveform breakout points:**
- TP93 = Square
- TP94 = Saw
- TP102 = Sub
- TP124 = Triangle

### Tier 3 — Advanced

| Mod | Description | Components | Difficulty |
|-----|-------------|------------|------------|
| **Clock Output** | Sequencer clock to external gear | NE555 or Pico PWM, 3.5mm jack | Easy |
| **MIDI Out** | Send notes/clock | Wire to LPC2361 pin 82, DIN socket | Medium |
| **Velocity CV Output** | Hidden DAC output | Wire to Pin 7 connector | Easy |
| **Body Contacts** | Touch-sensitive chaos | Brass bolts, LM386 | Medium |
| **Clock Divider** | /2 /4 /8 outputs | CD4024 or 555 chain | Medium |

### Tier 4 — Circuit Bending

| Mod | Description | Notes |
|-----|-------------|-------|
| **Metalizer bypass switches** | Direct waveshaper control | Toggle switches |
| **LFO rate extension** | Wider range | Replace timing cap |
| **Filter FM amount** | More modulation depth | Pot in FM path |
| **Sequencer decoupling** | Separate seq from keyboard | Maffez Pedrobrute mod |

### Patch Point Summary

| Point | Signal | Direction |
|-------|--------|-----------|
| VCA CV | Amplitude control | Input |
| VCO Mix | Pre-filter audio | Output |
| Saw Out | Sawtooth wave | Output |
| Square Out | Square wave | Output |
| Triangle Out | Triangle wave | Output |
| Sub Out | Sub-oscillator | Output |
| Metalizer Out | Processed wave | Output |
| Metalizer In | External to metalizer | Input |
| Clock Out | Sequencer clock | Output |
| Velocity CV | Note velocity | Output |
| Gate Out | Note gate | Output |

---

## 7. Wiring Diagrams

### ISP Programming (LPC2361)

```
┌──────────────────┐      ┌───────────────────────┐
│   PL2303HX       │      │      LPC2361          │
│   USB-TTL        │      │   (MicroBrute MCU)    │
│                  │      │                       │
│  TX  ────────────┼──────┼── P0.1 (RXD0, Pin 47) │
│  RX  ────────────┼──────┼── P0.0 (TXD0, Pin 46) │
│  GND ────────────┼──────┼── GND                 │
│                  │      │                       │
│  (Do NOT connect │      │  ISP enable:          │
│   3.3V - board   │      │  P0.14 → GND @ reset  │
│   has own power) │      │                       │
└──────────────────┘      └───────────────────────┘

Flash command:
$ lpc21isp -control -verify firmware.hex /dev/ttyUSB0 115200 12000
```

### VCO Mix Output Buffer

```
                    +12V
                     │
                     R1 10k
                     │
           ┌─────────┴─────────┐
           │                   │
TP (mix)───┤2      NE5532    1├───┬──── Output Jack
           │   ┌───┤3         │   │     (tip)
           │   │   └──────────┘   C2
           │  R2                  100nF
           │  10k                 │
           │   │                 GND
          GND  └─── -12V            (sleeve)

R1: 10kΩ (bias)
R2: 10kΩ (bias)  
C2: 100nF (DC blocking)
```

### Waveform Breakout (One Channel)

```
Test Point ──── R 1kΩ ────┬──── 3.5mm Jack (tip)
(TP93/94/102/124)         │
                         GND (sleeve)

Repeat 4× using TL074CN quad op-amp for buffered version:

                    +12V
                     │
           ┌─────────┴─────────┐
TPxx ──────┤+                  ├───┬──── Jack
           │      TL074       │   │
    ┌──────┤-      (1/4)      │   R 1k
    │      └──────────────────┘   │
    │                            GND
    └─────────────────────────────┘
```

### Clock Output (NE555)

```
         +5V
          │
          R1 1k
          │
    ┌─────┴─────┐
    │     8   4 ├───+5V
    │           │
    │    NE555  │
    │           │
    │  7  6  2  │
    └──┬──┬──┬──┘
       │  │  │
       R2 │  │
       ├──┴──┤
       │     │
       C1    C2
       │     │
      GND   GND

       3 ──────── Clock Out Jack

R1: 1kΩ
R2: Pot 100kΩ (rate control)
C1: 10µF (timing)
C2: 100nF (timing - parallel for range)

For Pico PWM alternative:
GP2 ──── R 470Ω ──── 3.5mm Jack
```

### MIDI Input (Improved with PC817)

```
MIDI In       ┌─────────────────┐
DIN Socket    │                 │
              │     PC817       │
Pin 4 ──R1────┤1    ┌───┐    4├────+5V
(+)   220Ω    │    │LED│       │
              │    └───┘       │
Pin 5 ────────┤2             3├────┬──── To LPC2361 RXD
(data)        │    photo-     │    R2
              │    transistor │    4.7k
              └───────────────┘    │
                                  GND
Pin 2 ──────── GND

R1: 220Ω (current limit)
R2: 4.7kΩ (pull-up)
D1: 1N4148 across pins 1-2 (protection, optional)
```

### MIDI Output

```
LPC2361 Pin 82 (UART TX)
        │
        R1 220Ω
        │
        └──────────── MIDI Out Pin 5 (data)

+3.3V ─── R2 220Ω ─── MIDI Out Pin 4 (+)

GND ───────────────── MIDI Out Pin 2 (shield)
```

### Body Contacts

```
Touch Plate A ────┬──── R1 47k ────┐
                  │                │
Touch Plate B ────┘                │
                              ┌────┴────┐
                              │    3    │
                              │  LM386  ├─── To CV input
                 ┌────────────┤    2    │    or feedback path
                 │            └────┬────┘
                 C1                │
                 10µF              │
                 │                GND
                GND

R1: 47kΩ (current limit for safety)
C1: 10µF (input coupling)
```

---

## 8. Development Roadmap

### Phase 1: Hardware Validation (Week 1-2)

- [ ] Test Pico USB enumeration
- [ ] Test PL2303HX shows as /dev/ttyUSB0
- [ ] Wire Pico + OLED, verify I2C
- [ ] Write basic OLED test pattern

### Phase 2: Pico Firmware (Week 2-4)

- [ ] SSD1306 driver (I2C, framebuffer)
- [ ] Basic UI layout
- [ ] UART receive from serial terminal
- [ ] Clock output via PWM
- [ ] Protocol design for LPC communication

### Phase 3: LPC2361 Connection (Week 4-6)

- [ ] Connect ISP, verify communication
- [ ] Check CRP status (`mdw 0x1FC 1`)
- [ ] Dump original firmware (if CRP allows)
- [ ] Set up gcc-arm-none-eabi toolchain
- [ ] "Hello World" printf over UART

### Phase 4: Core Firmware (Week 6-12)

- [ ] Reverse-engineer keyboard matrix
- [ ] Implement DAC output
- [ ] Basic sequencer (8-step first)
- [ ] MIDI input parsing
- [ ] Extend to 64 steps
- [ ] Add pattern storage

### Phase 5: MI Features (Week 12-20)

- [ ] Port Braids quantizer
- [ ] Implement euclidean patterns
- [ ] Add probability per step
- [ ] Implement arpeggiator
- [ ] Add Turing Machine mode
- [ ] Ratcheting engine

### Phase 6: Analog Mods (Parallel)

- [ ] Tier 1 mods (protection, VCA CV)
- [ ] Tier 2 mods (breakouts, mix out)
- [ ] Tier 3 mods (clock out, MIDI out)
- [ ] Panel drilling / enclosure work

---

## 9. Resource Budget

### Flash Memory (128KB)

| Component | Size | Notes |
|-----------|------|-------|
| Bootloader/startup | ~2KB | Vectors, init |
| Core firmware | ~20KB | Drivers, main loop |
| Sequencer engine | ~8KB | State machine |
| MI algorithms | ~10KB | Quantizer, arp, euclidean |
| Scale tables | ~4KB | 40+ scales |
| Euclidean LUT | ~4KB | Pre-computed patterns |
| Pattern storage | ~8KB | 16 patterns × 512 bytes |
| **Total** | **~56KB** | **44% used** |

### RAM (34KB)

| Component | Size | Notes |
|-----------|------|-------|
| Stack | ~2KB | Call depth |
| Heap | ~1KB | Dynamic alloc |
| Sequencer state | ~1KB | Current pattern, position |
| MIDI buffers | ~512B | Ring buffers |
| Display buffer | ~1KB | Pico comm |
| Quantizer | ~256B | Codebook, state |
| Arpeggiator | ~128B | NoteStack |
| **Total** | **~6KB** | **18% used** |

### Estimated Power

| Component | Current |
|-----------|---------|
| LPC2361 | ~50mA |
| Pico | ~30mA |
| OLED | ~20mA |
| Op-amps | ~10mA |
| NE555 | ~5mA |
| **Total** | **~115mA** |

---

## 10. Reference Links

### Schematics & Documentation

- **MicroBrute Schematics:** https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- **Maffez Pedrobrute:** https://maffez.com/?page_id=2285
- **ModWiggler MicroBrute Thread:** https://modwiggler.com/forum/viewtopic.php?t=152071
- **MicroBrute Mods Thread:** https://modwiggler.com/forum/viewtopic.php?t=95459

### Firmware References

- **duesynth (Arduino MiniBrute):** https://github.com/ernesto-g/duesynth
- **MicroDude SysEx Editor:** https://github.com/dagargo/microdude
- **SysEx Protocol:** https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html
- **Mutable Instruments Eurorack:** https://github.com/pichenettes/eurorack
- **MIOS32 (NXP LPC ref):** https://github.com/midibox/mios32
- **Aciduino Sequencer:** https://github.com/midilab/aciduino

### LPC2361 Resources

- **LPC2361 Datasheet:** https://www.nxp.com/docs/en/data-sheet/LPC2361_62.pdf
- **lpc21isp Flasher:** https://github.com/capiman/lpc21isp

### MI Algorithm Sources

- **Braids Quantizer:** `eurorack/braids/quantizer.cc`
- **Yarns Arpeggiator:** `eurorack/yarns/part.cc`
- **Grids Patterns:** `eurorack/grids/pattern_generator.cc`
- **Stages Curves:** `eurorack/stages/segment_generator.cc`

---

## Appendix: Firmware Project Structure

```
/uberbrute-firmware
├── README.md
├── LICENSE (MIT)
├── Makefile
│
├── /src
│   ├── main.c
│   ├── config.h
│   ├── /core         (system.c, interrupts.c)
│   ├── /drivers      (uart, gpio, dac, adc, timer)
│   ├── /synth        (keyboard, sequencer, arpeggiator, clock)
│   ├── /midi         (parser, handler, output)
│   ├── /ui           (pico_comm, params)
│   └── /utils        (debug.h, ring_buffer, math_utils)
│
├── /include
│   └── lpc2361.h
│
├── /linker
│   └── lpc2361.ld
│
├── /startup
│   ├── startup.s
│   └── syscalls.c
│
├── /tools
│   ├── flash.sh
│   └── monitor.sh
│
└── /docs
    ├── hardware.md
    ├── debugging.md
    └── protocol.md
```

---

*Document version 2.0 — Last updated: April 2026*
*Continue development for full toolchain integration*
