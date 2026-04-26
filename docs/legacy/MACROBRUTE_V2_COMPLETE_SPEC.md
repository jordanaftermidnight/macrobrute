> ⚠️ **DEPRECATED — superseded by current docs.** This file reflects an
> earlier iteration (different connector, expander HP, or pin map). Kept
> for historical reference only. See `README.md`, `docs/MACROBRUTE_BUILD_PLAN.md`,
> and `docs/MACROBRUTE_CONNECTION_MAP.md` for the current authoritative spec.

# MACROBRUTE V2 — Complete System Specification
## Custom Firmware + Pico Expansion + Analog Mods

*Transforming an Arturia MicroBrute into a Mutable Instruments-grade monosynth*

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Hardware Configuration](#hardware-configuration)
3. [Firmware Feature Set](#firmware-feature-set)
4. [Mutable Instruments Algorithms](#mutable-instruments-algorithms)
5. [Generative & Modular Features](#generative--modular-features)
6. [Hidden Features & Easter Eggs](#hidden-features--easter-eggs)
7. [OLED Display System](#oled-display-system)
8. [Pico Expansion Controller](#pico-expansion-controller)
9. [Analog Modifications](#analog-modifications)
10. [Communication Protocol](#communication-protocol)
11. [Development Roadmap](#development-roadmap)
12. [Resource Budget](#resource-budget)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MACROBRUTE SYSTEM OVERVIEW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │      LPC2361 (Main Brain)       │   │      Pi Pico H (Expansion)      │  │
│  │      Custom Firmware            │   │      Display + Extras           │  │
│  │                                 │   │                                 │  │
│  │  • Keyboard matrix scanning     │   │  • 0.96" SSD1306 OLED           │  │
│  │  • 64-step sequencer engine     │   │  • UI state machine             │  │
│  │  • MI-style arpeggiator         │   │  • Encoder reading (optional)   │  │
│  │  • Weighted scale quantizer     │   │  • Clock output generation      │  │
│  │  • Euclidean rhythm gating      │   │  • CV output (via PWM+filter)   │  │
│  │  • Probability per step         │   │  • USB MIDI host (future)       │  │
│  │  • Ratcheting engine            │   │  • Pattern backup/restore       │  │
│  │  • Turing Machine mode          │   │                                 │  │
│  │  • MIDI in/out                  │   │                                 │  │
│  │  • DAC: Pitch CV, Velocity CV   │   │                                 │  │
│  │  • Gate output                  │   │                                 │  │
│  │  • LFO generation               │   │                                 │  │
│  │                                 │   │                                 │  │
│  │  ARM7TDMI @ 72MHz               │   │  RP2040 dual-core @ 133MHz      │  │
│  │  128KB Flash / 34KB RAM         │   │  2MB Flash / 264KB RAM          │  │
│  └───────────────┬─────────────────┘   └─────────────────┬───────────────┘  │
│                  │                                       │                  │
│                  │         UART @ 115200 baud            │                  │
│                  └───────────────────────────────────────┘                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        ANALOG MODIFICATIONS                             ││
│  │                                                                         ││
│  │  Tier 1: Output protection, VCA CV input, Portamento on ext CV          ││
│  │  Tier 2: VCO mix out, Waveform breakouts, Metalizer I/O                 ││
│  │  Tier 3: Body contacts, White noise, S&H, Clock divider, MIDI Out       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dual-Processor Philosophy

The architecture separates concerns:

| Processor | Role | Why |
|-----------|------|-----|
| **LPC2361** | Real-time synth control | Direct hardware access, minimal latency |
| **Pico H** | UI/Display, expansion | Faster CPU, more RAM, easier development |

This allows:
- Stock MicroBrute functionality preserved (Phase 1)
- Pico can run standalone as "external brain" initially
- Custom LPC2361 firmware unlocks full potential (Phase 3)
- Either can be updated independently

---

## Hardware Configuration

### Currently Purchased

| Item | Price | Status |
|------|-------|--------|
| Raspberry Pi Pico H | ~€5 | ✅ Bought |
| PL2303HX USB-TTL 3.3V/5V | €2.90 | ✅ Bought |
| 0.96" SSD1306 OLED 128×64 I2C | ~€3 | ⏳ Ordered |

### Pico Wiring (SSD1306 OLED)

```
┌──────────────────┐      ┌───────────────┐
│    Pico H        │      │  SSD1306 OLED │
│                  │      │   128×64 I2C  │
│  Pin 36 (3V3) ───┼──────┼── VCC         │
│  Pin 38 (GND) ───┼──────┼── GND         │
│  GP4 (Pin 6)  ───┼──────┼── SDA         │
│  GP5 (Pin 7)  ───┼──────┼── SCL         │
└──────────────────┘      └───────────────┘
```

### ISP Wiring (LPC2361)

```
┌──────────────────┐      ┌───────────────────────┐
│   PL2303HX       │      │      LPC2361          │
│   USB-TTL        │      │   (MicroBrute MCU)    │
│                  │      │                       │
│  TX  ────────────┼──────┼── P0.1 (RXD0, Pin 47) │
│  RX  ────────────┼──────┼── P0.0 (TXD0, Pin 46) │
│  GND ────────────┼──────┼── GND                 │
│                  │      │                       │
│  (Don't connect  │      │  ISP enable:          │
│   3.3V - board   │      │  P0.14 → GND @ reset  │
│   has own power) │      │                       │
└──────────────────┘      └───────────────────────┘
```

**ISP Flash Command:**
```bash
lpc21isp -control -verify firmware.hex /dev/ttyUSB0 115200 12000
```

### Component Inventory (On Hand)

| Part | Qty | MACROBRUTE Use |
|------|-----|---------------|
| CD4049UBE | 3 | Logic buffer, waveshaping |
| TL082CP | 2 | Dual op-amp (TL072 equiv) |
| TL074CN | 2 | Quad op-amp |
| Arduino Pro Micro | 1 | Reserved for ML-303 |
| SMH1602A 16×2 LCD | 1 | Reserved for ML-303 |
| B50K pots | 3 | CV attenuators |
| B10K pots | 4 | Mixing, fine control |
| B1M pots | 4 | Portamento, touch sensitivity |
| Joyo JF-33 | 1 | PT2399 delay — keep intact |
| Jack sockets | many | Breakouts |

---

## Firmware Feature Set

### Sequencer Features

| Feature | Stock | MACROBRUTE | Notes |
|---------|-------|-----------|-------|
| Steps | 8 | **64** | Pattern chains for 256+ |
| Patterns stored | 8 | **16** | In flash via IAP |
| Directions | Fwd | **Fwd/Rev/Ping/Random** | Per-pattern setting |
| Step resolution | Fixed | **1/4 to 1/64** | Including triplets |
| Swing | No | **Yes, 0-75%** | Delays odd steps |
| Probability | No | **Yes, per-step 0-100%** | MI-style |
| Ratchet | No | **Yes, 1-8× per step** | Burst generator |
| Rest/Tie/Accent | Basic | **Full flags per step** | Like TB-303 |
| Slide | Basic | **Adjustable glide time** | Per-step enable |
| Scale quantize | No | **Yes, 40+ scales** | MI Braids quantizer |
| Euclidean gating | No | **Yes** | Overlay on sequence |
| Motion recording | No | **Yes, 4 params** | Record knob moves |
| Conditional trigs | No | **Yes, Elektron-style** | A:B, FILL, 1ST |

### Arpeggiator Features (Ported from MI Yarns)

| Feature | Description |
|---------|-------------|
| **Directions** | Up, Down, Up-Down, Down-Up, Random, As-Played, Chord |
| **Octave range** | 1-4 octaves |
| **Rhythmic patterns** | 16 preset patterns via bitmask |
| **Euclidean mode** | Generate arp rhythm from k/n parameters |
| **Latch** | Hold notes after release |
| **Note priority** | Low, High, Last, First |

### MIDI Features

| Feature | Description |
|---------|-------------|
| MIDI In | Note, CC, Clock, Start/Stop |
| MIDI Out | Requires hardware mod (Pin 82) |
| Clock sync | External/Internal with PLL tracking |
| Clock output | New! Via Pico or dedicated jack |
| MIDI Thru | Software thru option |
| CC mapping | All params mappable |
| SysEx | Pattern dump/load, config |
| Velocity CV | Hardware exists, unused by Arturia — we enable it |

---

## Mutable Instruments Algorithms

All algorithms below are MIT-licensed, ported from `github.com/pichenettes/eurorack`.

### 1. Braids Quantizer

**Source:** `braids/quantizer.cc`

The gold standard for pitch quantization:
- 7-bit sub-semitone resolution (128 values per semitone)
- Binary search against codebook for O(log n) performance
- Hysteresis at 56.25%/43.75% to prevent oscillation
- ~1KB code, 128 bytes RAM, ~20 cycles per quantization

```c
// Pitch representation: pitch = midi_note << 7
// Quantizer finds nearest scale degree with hysteresis

typedef struct {
    int16_t codebook[128];  // Note values in scale
    uint8_t num_notes;      // Notes in codebook
    int16_t previous_note;  // For hysteresis
} Quantizer;

int16_t quantize(Quantizer* q, int16_t pitch);
```

**Included scales:**
- Chromatic, Major, Minor (natural/harmonic/melodic)
- Pentatonic (major/minor), Blues
- Dorian, Phrygian, Lydian, Mixolydian, Locrian
- Whole tone, Diminished, Augmented
- Hirajoshi, Iwato, Kumoi, Pelog, Slendro
- Bhairav, Marwa, Todi
- Microtonal: Just intonation, Pythagorean, various ET systems

### 2. Marbles Weighted Quantizer

**Source:** `marbles/random/quantizer.h`

Extension of Braids quantizer with musical weighting:

```c
// Each scale degree has a weight (0-255) encoding importance
// Higher weight = note appears at lower quantization amounts

const uint8_t major_weights[12] = {
    255,  // Root (always present)
    16,   // b2
    128,  // 2
    16,   // b3
    192,  // 3 (major third, important)
    64,   // 4
    8,    // b5
    224,  // 5 (fifth, very important)
    16,   // b6
    96,   // 6
    32,   // b7
    160   // 7
};
```

A single knob morphs from "root only" → "pentatonic" → "full chromatic".

### 3. Yarns Arpeggiator

**Source:** `yarns/part.cc`, `edges/note_stack.h`

Complete arpeggiator with:

```c
typedef struct {
    uint8_t notes[16];      // Held notes
    uint8_t velocities[16]; // Per-note velocity
    uint8_t size;           // Current note count
    // Linked list for note priority
} NoteStack;

typedef struct {
    NoteStack stack;
    uint8_t arp_note;       // Current note index
    uint8_t arp_octave;     // Current octave offset
    int8_t arp_direction;   // +1 or -1
    uint8_t arp_step;       // For rhythmic patterns
    uint16_t pattern;       // 16-bit rhythm bitmask
} Arpeggiator;
```

Rhythmic patterns stored as bitmasks:
- `0xFFFF` = every step
- `0x8888` = every 4th step
- `0xAAAA` = every other step
- etc.

### 4. Euclidean Pattern Generator

**Source:** `yarns/part.cc` lookup table approach

Pre-computed lookup table (4KB flash) for instant euclidean patterns:

```c
// Index: (length-1)*32 + fill
// Returns: bitmask for pattern
extern const uint16_t lut_euclidean[32 * 32];

// Or runtime Bjorklund (zero RAM):
static inline uint8_t euclid_hit(uint8_t pulses, uint8_t length, 
                                  uint8_t rotation, uint8_t step) {
    return ((pulses * ((step + rotation) % length)) % length) 
           + pulses >= length ? 1 : 0;
}
```

Parameters:
- **Length:** 1-32 (or 64 with runtime calc)
- **Pulses:** How many hits
- **Rotation:** Shift pattern start

### 5. Grids Topographic Sequencing

**Source:** `grids/pattern_generator.cc`

25 pattern "nodes" on 5×5 grid, interpolated for infinite variations:

```c
// Each node: 32 steps × 3 instruments = 96 bytes
// Total: 25 nodes × 96 bytes = 2.4KB flash

// Bilinear interpolation between 4 surrounding nodes
uint8_t interpolate(uint8_t a, uint8_t b, uint8_t c, uint8_t d,
                    uint8_t frac_x, uint8_t frac_y) {
    uint8_t ab = U8Mix(a, b, frac_x);
    uint8_t cd = U8Mix(c, d, frac_x);
    return U8Mix(ab, cd, frac_y);
}
```

**For MACROBRUTE:** Repurpose for melodic patterns — store note offsets instead of drum hits. Two knobs morph between melodic "feels."

### 6. Stages Envelope Curves

**Source:** `stages/segment_generator.cc`

WarpPhase function for musically useful curves:

```c
// Convert linear phase to curved output
// curve: -128 (log) to +127 (exp), 0 = linear
int32_t warp_phase(int32_t phase, int8_t curve) {
    if (curve == 0) return phase;
    
    int32_t a = curve * curve;  // Always positive
    if (curve > 0) {
        // Exponential: slow start, fast end
        return (int32_t)(((int64_t)(1 + a) * phase) / (1 + ((a * phase) >> 16)));
    } else {
        // Logarithmic: fast start, slow end
        int32_t inv = 65535 - phase;
        return 65535 - (int32_t)(((int64_t)(1 + a) * inv) / (1 + ((a * inv) >> 16)));
    }
}
```

### 7. ONE_POLE Smoothing

**Source:** `stmlib/dsp/dsp.h`

The single most reusable primitive — used everywhere:

```c
// Fixed-point one-pole lowpass filter
// coeff = 0 (no change) to 65535 (instant)
#define ONE_POLE_Q16(out, in, coeff) do { \
    int32_t _err = (in) - (out); \
    (out) += (int32_t)(((int64_t)(coeff) * _err) >> 16); \
} while(0)
```

Uses:
- Parameter smoothing (anti-zipper)
- Portamento/glide
- Slew limiting
- Simple filtering

---

## Generative & Modular Features

### Turing Machine (Shift Register Sequencer)

**Concept:** Music Thing Modular's brilliant generative sequencer

```c
typedef struct {
    uint16_t shift_register;  // 16-bit pattern state
    uint8_t probability;      // 0=invert all, 128=random, 255=lock
    uint8_t length;           // 2-16 active bits
} TuringMachine;

void