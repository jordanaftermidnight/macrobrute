# PT2399 Deep Bending

Extracted from MACROBRUTE `docs/mods/deep_circuit_bending.md` because
the JF-33-style PT2399 delay is now a MACROBRUTE spinoff, not part
of the canonical build.

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


## Cross-device bending — PT2399 + MicroBrute

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
