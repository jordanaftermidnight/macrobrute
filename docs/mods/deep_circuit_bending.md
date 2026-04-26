# Deep Circuit Bending — MicroBrute

Advanced experimental modifications beyond the standard mod guide.
PT2399 and DSO138 deep-bend material moved to `spinoffs/jf33-eurorack/docs/`
and `spinoffs/dso138-desktop/docs/` respectively.

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

