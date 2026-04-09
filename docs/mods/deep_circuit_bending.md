# Deep Circuit Bending — PT2399, DSO138, MicroBrute

Advanced experimental modifications beyond the standard mod guide.

---

## PT2399 Deep Bending

### Pin 5 Clock Injection (Buffer Freeze)

Pin 5 outputs the internal VCO clock (2-25MHz range). Injecting an
external clock overrides this, allowing direct control of the sampling
rate and enabling buffer freeze effects.

```
  External clock source (Pico GP22, 555 timer, or LFO)
    │
  [10kΩ] (series limiting)
    │
  PT2399 Pin 5 (VCO output)
    │
  [100pF] (coupling cap, blocks DC)
    │
  clock source GND
```

**Frequencies:**
- Normal operation: ~40-120kHz (set by pin 6 timing R)
- Freeze: stop external clock → delay buffer holds last sample
- Glitch: sweep clock 1-100kHz → pitch-shifted artifacts
- Audio rate (100Hz-10kHz): bitcrusher/sample-rate-reduction effect

**WARNING:** Overdrive or DC on pin 5 can permanently damage the PT2399.
Always use series resistor and coupling cap.

### VDD Starving (Voltage Sag)

Reducing the PT2399's supply voltage below 5V introduces
progressive degradation:

```
  +5V (from 78L05)
    │
  [pot 1kΩ] (variable dropper)
    │
  PT2399 VDD (pin 1)
    │
  [100µF] (local bypass, prevents oscillation)
    │
  GND
```

| VDD | Effect |
|-----|--------|
| 5.0V | Normal operation |
| 4.5V | Slight pitch drop, warm distortion |
| 4.0V | Noticeable pitch shift, lofi character |
| 3.5V | Heavy distortion, clock errors, glitch |
| 3.0V | Barely functional, extreme artifacts |
| <2.5V | Latch-up risk — avoid |

**CV control:** Replace pot with 2N3904 + op-amp voltage regulator
to control VDD from a CV input (0-5V → 3-5V VDD).

### Pin 9/10 Reference Manipulation

Pins 9 and 10 are internal voltage references (~VDD/2).
Loading or offsetting these introduces asymmetric distortion.

```
  PT2399 Pin 9 ──[100kΩ pot]── GND
  Effect: Shifts bias point of internal comparators
  Character: Asymmetric clipping, even-harmonic distortion
  
  PT2399 Pin 10 ──[100kΩ pot]── GND
  Effect: Similar but affects different stage
  Character: Odd-harmonic emphasis
```

### Pin 4 Digital Ground Isolation

JimY (ModWiggler) discovered that isolating Pin 4 (digital ground)
from Pin 1 (analog ground) with separate returns improves sync
stability in multi-chip configurations.

### MOSFET Pin 6 Control (Peter Vis)

Peter Vis documented using a 2N7000 MOSFET with RC timing
(100kR x 47uF = 4.7s startup delay) on Pin 6 for glitch-free
startup while achieving true 31.3ms minimum delay. Combines
anti-latch-up protection with full range access.

### Multi-PT2399 Configurations

**Cascade (longer delay):**
```
  Input → PT2399 #1 (delay out) → PT2399 #2 (delay out) → Output
  Total delay: sum of both (up to ~1.2 seconds)
  Quality degrades on second chip (noise accumulates)
```

**Parallel (chorus/doubling — "Three PT2399s in a Trench Coat"):**
```
  Input ──┬── PT2399 #1 (short delay, ~10-30ms) ──┬── Mixer → Output
          │                                         │
          ├── PT2399 #2 (slightly different delay) ──┤
          │                                         │
          └── PT2399 #3 (third delay time) ──────────┘
  
  Slight detuning between chips creates dense reverb/chorus
  Shared power rail naturally locks clocks (JimY technique)
  PLL sync via 74HC4046 comparing VCO outputs (advanced)
```

---

## DSO138/DSO130 Deep Mods

### DAC Output for Function Generator

The STM32F103 on the DSO138 has a 12-bit DAC (PA4).
With alternative firmware, it can output waveforms.

```
  STM32 PA4 (DAC output, normally unused)
    │
  [1kΩ] (isolation)
    │
  TL072 buffer (+in)
    │
  Output → function generator jack
  
  Firmware mod: generate sine/square/triangle/noise
  on PA4 while displaying on screen
```

**Note:** Requires custom firmware modification. Stock firmware
does not expose DAC functionality.

### Trigger Output for Clock Generation

The trigger output (normally just for scope sync) can be
repurposed as a clock/gate generator:

```
  DSO138 trigger output (3.3V logic)
    │
  [1kΩ]
    │
  2N3904 base
    │
  Collector ── +5V via 10kΩ pull-up
    │
  Output → clock jack (0/5V)
  
  Emitter → GND
```

Set trigger mode to "auto" with desired threshold for
rhythm-synchronized clock derived from audio input.

### Serial Data Export

The DSO138 Mini has a serial output that can stream ADC samples:

```
  DSO138 Mini serial TX (3.3V TTL)
    │
  USB-TTL adapter (CP2102 or similar)
    │
  Computer: depau/dso138mini-viewer (Python)
  
  Streams: raw ADC samples at ~1Msps
  Use for: data logging, FFT analysis, recording waveforms
```

### DLO-138 Alternative Firmware Features

The DLO-138 firmware adds:
- Better trigger stability
- Larger buffer (with DMA optimization)
- Serial protocol for remote control
- Faster sweep rates
- DLO-138-SPI variant for SPI-connected displays

---

## MicroBrute Deep Bending

### Steiner-Parker Filter Mode Switching

The MicroBrute's Steiner-Parker filter has LP/HP/BP inputs.
Only LP is normally used. Adding switches to route the signal
to different inputs creates additional filter modes.

```
  VCO Mix ──[SPDT switch]──┬── LP input (pin X, stock)
                            ├── HP input (pin Y)
                            └── BP input (pin Z)
  
  Or use 3-position rotary switch for panel mount
  
  Identify pins from hackabrute schematic:
  Look for the 3 input resistors to the Steiner-Parker opamp
```

**Effect:** HP mode: thin, nasal. BP mode: vocal, resonant peak.
Combined modes possible with multi-pole switches.

### Metalizer Feedback Loop

```
  Metalizer output (U_metalizer pin out)
    │
  [pot 100kΩ]
    │
  Metalizer input (via buffer or direct)
  
  Effect: Wavefolder feeds back into itself
  Character: Explosive harmonics at high feedback
  WARNING: Can produce very loud signals — use attenuator
```

### VCA Drone Mod (Gate Hold)

```
  VCA control point (TP10 or TP11)
    │
  [SPST toggle switch]
    │
  +12V via [100kΩ] voltage divider
    │
  This holds the VCA open regardless of envelope/gate
  
  Better version: add pot to control drone level:
  +12V ──[100kΩ]──[pot 100kΩ]── TP10/11
```

### Power Rail Sag ("Dying Battery")

```
  Internal +12V rail (after protection diode)
    │
  [SPST switch] → bypass (normal operation)
    │
  [pot 10Ω + 2× 1N5817 series] → sag path
    │
  When engaged: drops ~0.5-2V from rails
  Effect: All oscillators detune, filter response changes
  Character: "Dying battery" / tape warble aesthetic
  
  WARNING: Too much sag can corrupt LPC2361 firmware
  Keep minimum rail voltage > 8V
  Add Zener diode clamp to prevent going below 8V:
  [8.2V Zener cathode → rail, anode → GND]
```

### Sub Oscillator Waveform Mod

The sub oscillator is derived from the main VCO via a flip-flop
(divider). The waveform can be altered:

```
  Sub osc output (from divider)
    │
  [RC filter: series R + shunt C to GND]
  R = 10kΩ, C = 1nF → rounds square to pseudo-sine
  
  Or:
  Sub osc → [wavefolder circuit] → modified sub output
  
  Or:
  Add second flip-flop stage for -2 octave sub
  (CD4013 dual D flip-flop, ~$0.30)
```

### Hidden Test Point Functions

Beyond documented test points, the PCB has additional
accessible nodes worth investigating:

| Point | Location | Suspected Function |
|-------|----------|-------------------|
| TP55 | Front board | Internal CV bus |
| TP56 | Near VCA | VCA offset trim |
| TP10/11 | VCA section | VCA CV injection |
| R309 area | Near trimmers | Tuning circuit |
| UB6 pin 5 | Mixer IC | VCO mix pre-filter |
| C107-C111 | Metalizer | Wavefolder stages |

### LPC2361 Clock Manipulation (Experimental)

**WARNING:** High risk of bricking. For research only.

```
  LPC2361 crystal (12MHz)
    │
  If crystal is removable (socketed):
    Replace with 10-14MHz crystal → changes sequencer tempo base
    Or use oscillator module for variable clock
    
  If crystal is soldered:
    Add varactor diode in parallel with crystal load caps
    Apply CV to varactor → slight frequency pulling (~±0.1%)
    Effect: Subtle timing drift, like analog clock wobble
```

---

## Cross-Device Bending

### PT2399 Delay Fed by MicroBrute Feedback

```
  MicroBrute Brute Factor output (if accessible)
    │
  [pot 100kΩ] (level control)
    │
  PT2399 input (via JF-33 mod)
    │
  PT2399 output → MicroBrute external audio input
  
  Creates: delay + distortion feedback loop
  Control: Brute Factor knob + delay time CV
  Character: Self-oscillating chaos, industrial textures
```

### DSO138 as CV Visualizer + Trigger Source

```
  Signal from MicroBrute test point → DSO138 input (via protection)
  DSO138 trigger output → clock divider → sequencer clock
  
  Visual feedback of waveform on scope
  Audio-derived clock for rhythmic synchronization
```
