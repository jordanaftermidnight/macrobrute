# MACROBRUTE Complete Expansion System

## Design Philosophy

Transform the MicroBrute into a **fully semi-modular voice** with ALL I/O routed through a Eurorack expander panel. The MicroBrute becomes a dedicated synth brain — keyboard, sequencer, and core analog circuits — while the expander provides:

1. **All patchbay I/O** (replacing/duplicating rear panel)
2. **All new mod points** (CV ins, audio inserts, taps)
3. **On-board utilities** (LFO, noise, clock divider, S&H, etc.)
4. **Mod matrix controls** (attenuators, attenuverters)

---

## PART 1: MICROBRUTE SIGNAL FLOW & EVERY INTERCEPTION POINT

### Complete Signal Path

```
                                    ┌─────────────────────┐
                                    │    KEYBOARD/SEQ     │
                                    │   Gate + Pitch CV   │
                                    └──────────┬──────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          ▼                          │
                    │              ┌───────────────────────┐              │
                    │              │         VCO           │              │
                    │              │  ┌─────┬─────┬─────┐  │              │
                    │              │  │ SAW │ SQR │ TRI │  │              │
                    │              │  │     │     │ SUB │  │              │
                    │              │  └──┬──┴──┬──┴──┬──┘  │              │
                    │              └─────┼─────┼─────┼─────┘              │
                    │                    │     │     │                    │
                    │              ┌─────▼─────▼─────▼─────┐              │
                    │              │       ANIMATOR        │              │
                    │              │  (Ultrasaw/Metalizer) │              │
                    │              └───────────┬───────────┘              │
                    │                          │                          │
                    │              ┌───────────▼───────────┐              │
                    │              │        MIXER          │◄── Ext Audio │
                    │              │ (Waveform levels +    │              │
                    │              │  Brute Factor blend)  │              │
                    │              └───────────┬───────────┘              │
                    │                          │                          │
                    │              ┌───────────▼───────────┐              │
                    │              │   STEINER-PARKER VCF  │◄── Filter CV │
                    │              │   (LP/HP/BP/Notch)    │◄── Audio FM  │
                    │              └───────────┬───────────┘              │
                    │                          │                          │
                    │              ┌───────────▼───────────┐              │
                    │              │         VCA           │◄── VCA CV    │
                    │              └───────────┬───────────┘              │
                    │                          │                          │
                    │              ┌───────────▼───────────┐              │
                    │              │     BRUTE FACTOR      │              │
                    │              │   (Feedback loop)     │              │
                    │              └───────────┬───────────┘              │
                    │                          │                          │
                    │                          ▼                          │
                    │                    AUDIO OUTPUT                     │
                    └─────────────────────────────────────────────────────┘
```

---

## PART 2: ALL INTERCEPTION POINTS (ACTIVE + POTENTIAL)

### A. CV/GATE OUTPUTS (From MicroBrute)

| Signal | Source | Test Point | Status | Notes |
|--------|--------|------------|--------|-------|
| Pitch CV | DAC Ch A | TP34 / Rear panel | Stock | 1V/Oct, C1=0V |
| Gate Out | Q7-Q10 circuit | TP83 / Rear panel | Stock | 100kΩ source Z — BUFFER! |
| Velocity CV | DAC → U605A | **PT675** | **HIDDEN** | Firmware outputs, unused by Arturia |
| Aftertouch CV | DAC | Near PT675 | **HIDDEN** | Responds to MIDI AT only |
| Mod Wheel CV | DAC Ch C | TP39 | **HIDDEN** | Accessible, needs buffer |
| Envelope CV | Mod matrix | Front panel | Stock | 0 to +4.5V |
| LFO CV | Mod matrix | Front panel | Stock | ±5V |
| Keyboard CV (raw) | Pre-glide | TL062 input | Tap | Before portamento circuit |
| Keyboard CV (post-glide) | Post-glide | TL062 output | Tap | After portamento |

### B. AUDIO OUTPUTS (From MicroBrute)

| Signal | Source | Test Point | Series R | Notes |
|--------|--------|------------|----------|-------|
| Main Output | Final stage | Rear panel | — | Line level ±1.5V |
| VCO Mix (pre-filter) | UB6 pin 7 | TP30 | 1kΩ | Use unused op-amp half |
| VCF Output (post-filter) | Filter out | TP19 | 1kΩ | Before VCA |
| Sawtooth (raw) | VCO | TP94 | 1kΩ | ~10Vpp |
| Square (raw) | VCO | TP93 | 1kΩ | ~10Vpp |
| Triangle (raw) | VCO | TP124 | 1kΩ | Lower level |
| Sub Oscillator | Sub circuit | TP102 | 1kΩ | Affected by Sub knob |
| Metalizer Output | Wavefolder | TP109 | 1kΩ | Affected by Metal knob |
| Ultrasaw Output | Animator | TP119 | 1kΩ | Post-animator saw |
| Post-PWM Pulse | PWM shaper | TP122 | 1kΩ | Shaped pulse wave |

### C. CV INPUTS (To MicroBrute)

| Parameter | Injection Point | Series R | Method | Difficulty |
|-----------|-----------------|----------|--------|------------|
| Filter Cutoff | U8A summing node | 220kΩ | Add to existing CV sum | Easy |
| Filter FM (audio-rate) | Same summing node | 100kΩ | Parallel path | Easy |
| VCA Level | TP10 / TP11 | — | Direct injection | Easy |
| PWM Depth | R289 junction | 39kΩ | Add to PW summing | Medium |
| Pitch (additional) | U17b inverting input | 100kΩ | Linear FM | Medium |
| **Resonance** | RP13 / Q6 JFET | — | **Vactrol/OTA** | Hard |
| **Brute Factor** | Feedback path | — | **VCA in loop** | Hard |
| **Glide Rate** | Integrator R | — | **Vactrol** | Hard |
| **Metalizer Depth** | Mix circuit | — | **VCA/crossfader** | Hard |
| **LFO Rate** | — | — | **Digital (firmware)** | Impossible without FW mod |

### D. AUDIO INSERTS (Bidirectional)

| Insert Point | Resistor | Value | Location | Function |
|--------------|----------|-------|----------|----------|
| **VCF Insert** | R23 | 100kΩ | Front board | Break VCF→VCA path |
| **Metalizer Insert** | R216 | 120kΩ | Rear board | Inject into wavefolder |
| **Mixer Insert** | R76 area | — | Front board | Pre-filter injection |
| **Brute Factor Insert** | Feedback path | — | Front board | External in feedback loop |
| **VCA Insert** | Post-VCA | — | Front board | Effects loop |

### E. GATE/TRIGGER/SYNC

| Signal | Direction | Point | Method |
|--------|-----------|-------|--------|
| Gate In | Exp → MB | Rear panel / TP22 | Stock input exists |
| Gate Out | MB → Exp | TP83 | Needs buffer |
| VCO Hard Sync | Exp → MB | Sync TP | Documented mod |
| VCO Soft Sync | Exp → MB | Sync TP | Requires switch |
| LFO Reset | Exp → MB | — | Requires firmware mod |
| Sequencer Clock In | Exp → MB | Tap tempo | NPN to simulate tap |
| Clock Out | MB → Exp | Pico / 555 | Generate from tempo |

---

## PART 3: CIRCUIT BENDING & EXPERIMENTAL POINTS

### IC-Level Bend Points

The MicroBrute uses these ICs with potential bend opportunities:

| IC | Function | Bend Potential |
|----|----------|----------------|
| **TL062** (×6) | Dual op-amp, low power | Feedback loops, starving |
| **TL074** (×2) | Quad op-amp | CV summing mods |
| **CD4027** | Dual JK flip-flop | Sub oscillator division |
| **CD4011** | Quad NAND gate | Logic bending |
| **SN74HCT04D** | Hex inverter | Clock/logic bending |
| **LPC2361** | ARM7 MCU | Firmware replacement |
| **MCP4728** | Quad 12-bit DAC | Hidden CV outputs |

### Steiner-Parker Filter Mods (Based on Yusynth Improvements)

Yves Usson's improvements to the Steiner-Parker (which he designed into the MicroBrute) include:

1. **Scratchy resonance fix** — RP13 replacement
2. **Untamed auto-oscillation** — Feedback resistor mods
3. **Separate mode inputs** — LP/HP/BP can be driven independently
4. **Input overdrive** — Driving inputs hot creates distortion

**Potential filter mods:**
- Add separate LP/HP/BP audio inputs (not just mode switch)
- Resonance CV via vactrol parallel to RP13
- Filter FM dedicated input (100kΩ to summing node)
- Self-oscillation kill switch (disconnect feedback)

### Wavefolder/Metalizer Mods (Based on Yusynth Metalizer)

The MicroBrute metalizer is a simplified wavefolder. Yusynth's standalone Metalizer offers:

- VCA on input (voltage-controlled fold depth)
- Multiple fold stages
- CV control of fold amount

**Potential metalizer mods:**
- External audio input (R216 insert — documented)
- CV control of metalizer depth (requires VCA circuit)
- Feedback from metalizer output to input (chaos mode)
- Metalizer bypass switch

### Brute Factor Expansion

The Brute Factor is a feedback path from VCA output back to the mixer. Potential mods:

- **External feedback input** — Inject any signal into the feedback path
- **Feedback amount CV** — VCA in the feedback loop
- **Feedback filter** — LP/HP in feedback for tonal control
- **Cross-feedback** — Route other synth outputs into Brute Factor

---

## PART 4: ON-BOARD EXPANDER UTILITIES

These circuits live on the expander PCB, not inside the MicroBrute:

### Essential Utilities

| Utility | IC | Notes |
|---------|-----|-------|
| **Buffers (12×)** | 3× TL074 | All MB outputs need buffering |
| **Gate buffer** | CD40106 or LM393 | Clean up weak MB gate |
| **Attenuators (3×)** | 100kΩ pots | Filter, VCA, PWM CV inputs |

### Recommended Additions

| Utility | IC | Notes |
|---------|-----|-------|
| **Analog LFO** | TL072 + passives | Triangle/square, 0.1-50Hz |
| **White Noise** | 2N3904 reverse-biased | Thomas Henry circuit |
| **Clock Divider** | CD4024 | /2, /4, /8 from main clock |
| **Sample & Hold** | CD4066 + TL072 | Random CV generation |
| **Slew Limiter** | TL072 integrator | Portamento for any CV |
| **Attenuverter** | TL072 + pot | Invert/scale CVs |
| **Manual Gate** | Momentary switch | Trigger envelope manually |
| **Mult (1→3)** | TL074 section | Split any signal |

### Advanced Additions (Optional)

| Utility | IC | Notes |
|---------|-----|-------|
| **Resonance VCA** | LM13700 or vactrol | CV control of resonance |
| **Envelope Follower** | TL072 + rectifier | Extract CV from audio |
| **Comparator** | LM393 | Gate from audio threshold |
| **Ring Modulator** | AD633 or discrete | Classic effect |
| **Sub-harmonic Gen** | CD4024 | Octave-down from audio |

---

## PART 5: COMPLETE SIGNAL COUNT

### From MicroBrute (Outputs)

| Category | Signals |
|----------|---------|
| CV outputs (stock) | 3 (Pitch, Gate, Env) |
| CV outputs (mod matrix) | 1 (LFO) |
| CV outputs (hidden DAC) | 3 (Velocity, Aftertouch, Mod Wheel) |
| Audio outputs (stock) | 2 (Main L/R) |
| Audio outputs (new taps) | 8 (Mix, VCF, Saw, Sqr, Tri, Sub, Metal, Ultrasaw) |
| **Subtotal** | **17** |

### To MicroBrute (Inputs)

| Category | Signals |
|----------|---------|
| CV inputs (stock) | 2 (Pitch mod, Gate) |
| CV inputs (new) | 3 (Filter, VCA, PWM) |
| Audio inputs (stock) | 1 (Ext Audio) |
| Audio inserts | 2 (VCF, Metalizer) |
| Sync/trigger | 2 (Sync, Clock inject) |
| **Subtotal** | **10** |

### Power

| Rail | Signals |
|------|---------|
| +12V | 1 |
| -12V | 1 |
| GND | 8-10 |

### Expander-Generated (On-Board)

| Category | Signals |
|----------|---------|
| LFO outputs | 2 (Tri, Sqr) |
| Noise output | 1 |
| Clock divider | 3 (/2, /4, /8) |
| S&H output | 1 |
| **Subtotal** | **7** |

### Grand Total

| Direction | Count |
|-----------|-------|
| MB → Expander | 17 |
| Expander → MB | 10 |
| Power/Ground | ~12 |
| Expander-only | 7 |
| Spare | 4 |
| **TOTAL SIGNALS** | **~50** |

---

## PART 6: CONNECTOR STRATEGY

### DB-37 Is Not Enough

With ~50 signals, **two connectors** are required:

**Option A: 2× DB-25 (50 pins)**
- Proven (Moog VX-351 uses DB-25)
- Split by function: A = Outputs, B = Inputs + Power
- Easy to debug (can connect one at a time)

**Option B: DB-37 + DB-25 (62 pins)**
- DB-37: All audio + CV signals
- DB-25: Power, grounds, expansion, clock

**Option C: HD-50 (50 pins)**
- Single connector
- Smaller footprint than 2× DB-25
- Tighter pin pitch (harder to solder)

**Recommendation: 2× DB-25**

---

## PART 6B: MOD POTS ON EXPANDER PANEL

The expander panel should include **control pots** for modifications — not just patch points. This gives hands-on control without needing external modules.

### CV Input Attenuators (Essential)

| Control | Pot Value | Function |
|---------|-----------|----------|
| **Filter CV Amt** | 100kΩ lin | Scale incoming CV before summing to filter |
| **VCA CV Amt** | 100kΩ lin | Scale incoming CV for VCA control |
| **PWM CV Amt** | 100kΩ lin | Scale incoming CV for pulse width |
| **Resonance CV Amt** | 100kΩ lin | Scale CV for resonance (if vactrol mod done) |
| **Pitch FM Amt** | 100kΩ lin | Scale linear FM amount |

### Modification Controls (Bringing Internal Trimmers to Panel)

These replace or parallel internal components, giving external access:

| Control | Stock Location | Mod Method | Pot Value |
|---------|---------------|------------|-----------|
| **VCA Boost** | R28 (100kΩ) | Series pot + resistor | 50kΩ lin + 50kΩ fixed |
| **VCO Fine Tune (Extended)** | R309 (1MΩ) | Replace with 100kΩ | 100kΩ lin (panel) |
| **Brute Factor Blend** | Internal path | Crossfader circuit | 100kΩ lin |
| **Metalizer Mix** | After wavefolder | Dry/wet blend | 100kΩ log |
| **Filter Overdrive** | R23 (100kΩ) | Lower value = more drive | 100kΩ lin |
| **Sub Level Boost** | After sub circuit | Parallel amplifier | 50kΩ log |

### Expander Utility Controls

| Control | Function | Pot Value |
|---------|----------|-----------|
| **LFO Rate** | On-board analog LFO speed | 1MΩ lin |
| **LFO Depth** | On-board LFO output level | 100kΩ lin |
| **S&H Rate** | Sample clock speed | 1MΩ lin |
| **Slew Time** | Portamento for any CV | 1MΩ log |
| **Noise Level** | White noise output | 100kΩ log |
| **Attenuverter** | Invert/scale any CV | 100kΩ lin (center detent) |

### Switches on Panel

| Switch | Type | Function |
|--------|------|----------|
| **VCO Sync** | SPDT | Hard / Soft / Off |
| **Filter Mode** | 4-pos rotary | LP / HP / BP / Notch (bypass stock switch) |
| **LFO Wave** | SPDT | Triangle / Square |
| **Ext/Int Clock** | SPDT | Internal LFO / External clock for S&H |
| **Slew Mode** | SPDT | Linear / Exponential |
| **KB CV Bypass** | SPDT | Internal KB / External CV only |

---

## PART 6C: ADDITIONAL DISCOVERED MOD POINTS

From Maffez Pedrobrute and community research:

### VCO Section

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **Linear FM Input** | U17b inverting input | 100kΩ series resistor to summing node | Medium |
| **Exponential FM Depth** | U11b output | Attenuator before summing | Medium |
| **Tune Range Extend** | R309 (1MΩ) | Replace with 100kΩ | Easy |
| **Soft Sync Input** | TP_SOFTSYNC | Direct connection | Easy |
| **Hard Sync Input** | TP_HARDSYNC | Direct connection | Easy |
| **Square Phase Invert** | Op-amp swap | Rewire 4 resistors around op-amp | Hard |

### Mixer/Animator Section

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **VCO Mix Output (Buffered)** | UB6 unused half | Lift pin 5 from GND, connect to TP30, out via 1kΩ | Medium |
| **Animator Output** | TP119 | Direct tap via 1kΩ | Easy |
| **Pre-animator Saw** | Before animator circuit | Tap before processing | Easy |
| **PWM Duty Output** | TP122 | Direct tap via 1kΩ | Easy |
| **Waveform Level Boost** | Individual wave resistors | Reduce mixing resistor values | Medium |

### Filter Section (Steiner-Parker)

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **Filter FM (Audio Rate)** | Same as cutoff CV | Smaller series R (10-47kΩ) | Easy |
| **Separate LP Input** | Existing LP path | Switched jack normalled to internal | Medium |
| **Separate HP Input** | Existing HP path | Switched jack normalled to internal | Medium |
| **Separate BP Input** | Existing BP path | Switched jack normalled to internal | Medium |
| **Resonance CV** | RP13 / Q6 | Parallel vactrol (VTL5C3) | Hard |
| **Filter Insert** | R23 (100kΩ) | Remove, wire to switched jack | Medium |
| **Self-Oscillation Kill** | Resonance feedback | Series switch | Easy |
| **Diode Swap** | D1-D8 | 1N4148 → 1N270 (germanium) for warmer sound | Medium |

### VCA Section

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **VCA CV Input** | TP10 or TP11 | Direct connection | Easy |
| **VCA Boost Control** | R28 (100kΩ) | 50kΩ + 50kΩ pot in series | Easy |
| **VCA Insert** | Post-VCA, pre-output | Switched jack after VCA | Medium |
| **VCA Response Curve** | — | Different transistor matching | Hard |

### Brute Factor Section

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **External Feedback Input** | Feedback path | Inject signal into loop | Medium |
| **Feedback Amount CV** | — | VCA in feedback loop | Hard |
| **Feedback Filter** | — | LP/HP filter in loop | Hard |
| **Feedback Bypass** | — | Switch to disconnect | Easy |

### Metalizer Section

| Mod | Location | Method | Difficulty |
|-----|----------|--------|------------|
| **Metalizer Input Insert** | R216 (120kΩ) | Remove, wire to switched jack | Medium |
| **Metalizer Output** | TP109 | Direct tap via 1kΩ | Easy |
| **Metalizer CV Depth** | — | Add VCA before wavefolder stages | Hard |
| **Metalizer Dry/Wet** | — | Crossfader circuit after | Medium |
| **Metalizer Feedback** | Output → Input | Patch point for self-feedback | Easy |

### DAC Hidden Outputs

The MCP4728 quad DAC has channels beyond standard use:

| DAC Channel | Stock Use | Hidden Potential |
|-------------|-----------|------------------|
| **Ch A** | Pitch CV | — (essential) |
| **Ch B** | LFO → Mod Matrix | Tap directly for clean LFO |
| **Ch C** | Mod Wheel | **Full mod wheel CV out** (PT675 area) |
| **Ch D** | Velocity | **Velocity CV out** (firmware outputs this!) |

Additionally: **Aftertouch** responds to MIDI aftertouch and is output by firmware but unused by Arturia circuits.

### Notch Filter Mode (Undocumented)

The MicroBrute can do **notch filter** by shorting HP and LP inputs together:
- Wire HP input to LP input
- Results in notch (band-reject) response
- Can be switched: LP / HP / BP / Notch

---

## PART 7: PANEL LAYOUT (84HP)

With full I/O + mod pots + on-board utilities, **84HP** provides comfortable spacing:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MACROBRUTE EXPANDER · 84HP                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│  ┌─────────────────────┐  ┌─────────────────────────────┐  ┌───────────────────────────────────────┐ │
│  │    CV OUTPUTS       │  │      AUDIO OUTPUTS          │  │          WAVEFORM TAPS                │ │
│  │                     │  │                             │  │                                       │ │
│  │  ┌───┐┌───┐┌───┐   │  │  ┌───┐┌───┐┌───┐┌───┐     │  │  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐     │ │
│  │  │PCH││GAT││VEL│   │  │  │MIX││VCF││OUT││OUT│     │  │  │SAW││SQR││TRI││SUB││MTL││PWM│     │ │
│  │  │OUT││OUT││OUT│   │  │  │OUT││OUT││ L ││ R │     │  │  │OUT││OUT││OUT││OUT││OUT││OUT│     │ │
│  │  └───┘└───┘└───┘   │  │  └───┘└───┘└───┘└───┘     │  │  └───┘└───┘└───┘└───┘└───┘└───┘     │ │
│  │  ┌───┐┌───┐┌───┐   │  │                             │  │                                       │ │
│  │  │ENV││LFO││MOD│   │  │  INSERTS (Send/Return)      │  │  ANIMATOR                             │ │
│  │  │OUT││OUT││WHL│   │  │  ┌───┐┌───┐ ┌───┐┌───┐     │  │  ┌───┐                                │ │
│  │  └───┘└───┘└───┘   │  │  │VCF││VCF│ │MTL││MTL│     │  │  │USA│ Ultrasaw                       │ │
│  │  ┌───┐             │  │  │SND││RTN│ │SND││RTN│     │  │  │OUT│                                │ │
│  │  │AFT│ Aftertouch  │  │  └───┘└───┘ └───┘└───┘     │  │  └───┘                                │ │
│  │  │OUT│             │  │                             │  │                                       │ │
│  │  └───┘             │  │                             │  │                                       │ │
│  └─────────────────────┘  └─────────────────────────────┘  └───────────────────────────────────────┘ │
│                                                                                                      │
│  ┌──────────────────────────────────────────┐  ┌─────────────────────────────────────────────────┐  │
│  │           CV INPUTS + MOD POTS           │  │              GATE / SYNC / CLOCK               │  │
│  │                                           │  │                                                 │  │
│  │    FLT CV    VCA CV    PWM CV    RES CV   │  │  ┌───┐┌───┐┌───┐  ┌───┐┌───┐┌───┐┌───┐       │  │
│  │    ┌───┐     ┌───┐     ┌───┐     ┌───┐   │  │  │G.I││G.O││SYN│  │CLK││÷2 ││÷4 ││÷8 │       │  │
│  │    │ ○ │     │ ○ │     │ ○ │     │ ○ │   │  │  │ N ││OUT││ N │  │OUT││OUT││OUT││OUT│       │  │
│  │    └─┬─┘     └─┬─┘     └─┬─┘     └─┬─┘   │  │  └───┘└───┘└───┘  └───┘└───┘└───┘└───┘       │  │
│  │    ┌───┐     ┌───┐     ┌───┐     ┌───┐   │  │                                                 │  │
│  │    │   │     │   │     │   │     │   │   │  │  ┌───┐  ● ● ●                                  │  │
│  │    │IN │     │IN │     │IN │     │IN │   │  │  │MAN│  G L C  Gate/LFO/Clock LEDs             │  │
│  │    └───┘     └───┘     └───┘     └───┘   │  │  │GAT│                                         │  │
│  │                                           │  │  └───┘                                         │  │
│  │    LIN FM    EXT AUDIO  PITCH FM          │  │                                                 │  │
│  │    ┌───┐     ┌───┐     ┌───┐             │  │  SYNC MODE  ┌─────┐                             │  │
│  │    │ ○ │     │   │     │ ○ │             │  │  HARD│SOFT  │ OFF │                             │  │
│  │    └─┬─┘     │IN │     └─┬─┘             │  │  ────┴──────┴─────                              │  │
│  │    ┌───┐     └───┘     ┌───┐             │  │                                                 │  │
│  │    │IN │               │IN │             │  │                                                 │  │
│  │    └───┘               └───┘             │  │                                                 │  │
│  └──────────────────────────────────────────┘  └─────────────────────────────────────────────────┘  │
│                                                                                                      │
│  ┌──────────────────────────────────────────┐  ┌─────────────────────────────────────────────────┐  │
│  │         MODIFICATION CONTROLS            │  │           EXPANDER UTILITIES                    │  │
│  │                                           │  │                                                 │  │
│  │    VCA      TUNE     BRUTE    METAL      │  │  LFO ──────────────   NOISE ────   S&H ───────  │  │
│  │   BOOST    RANGE    BLEND    MIX        │  │                                                 │  │
│  │    ┌───┐    ┌───┐    ┌───┐    ┌───┐     │  │  RATE    DEPTH         LEVEL       RATE         │  │
│  │    │ ○ │    │ ○ │    │ ○ │    │ ○ │     │  │  ┌───┐    ┌───┐       ┌───┐       ┌───┐        │  │
│  │    └───┘    └───┘    └───┘    └───┘     │  │  │ ○ │    │ ○ │       │ ○ │       │ ○ │        │  │
│  │                                           │  │  └───┘    └───┘       └───┘       └───┘        │  │
│  │    SUB      DRIVE    ATTEN              │  │  ┌───┐┌───┐         ┌───┐       ┌───┐┌───┐     │  │
│  │   BOOST    (VCF)    -VERT               │  │  │TRI││SQR│         │NOI│       │IN ││OUT│     │  │
│  │    ┌───┐    ┌───┐    ┌───┐               │  │  │OUT││OUT│         │OUT│       └───┘└───┘     │  │
│  │    │ ○ │    │ ○ │    │ ○ │               │  │  └───┘└───┘         └───┘                      │  │
│  │    └───┘    └───┘    └───┘               │  │                                                 │  │
│  │                                           │  │  SLEW ────────────   MULT ────   ATTEN ──────  │  │
│  │    FILTER MODE                            │  │  TIME               (1→3)                      │  │
│  │    ┌─────────────────┐                   │  │  ┌───┐    ┌───┐     ┌───┐       ┌───┐┌───┐    │  │
│  │    │ LP │ HP │ BP │ N │                  │  │  │ ○ │    │ ○ │     │IN │       │ ○ ││OUT│    │  │
│  │    └─────────────────┘                   │  │  └───┘    └───┘     └───┘       └───┘└───┘    │  │
│  │                                           │  │  ┌───┐┌───┐       ┌───┐┌───┐                  │  │
│  │    KB CV BYPASS  ○ INT / EXT ○           │  │  │IN ││OUT│       │OUT││OUT│                  │  │
│  │                                           │  │  └───┘└───┘       └───┘└───┘                  │  │
│  └──────────────────────────────────────────┘  └─────────────────────────────────────────────────┘  │
│                                                                                                      │
│        ┌─────────────────────────────────────────────────────────────────────────────────┐          │
│        │                      ACTIVE CONNECTIONS                                         │          │
│        │               [═══ DB-25 A ═══]      [═══ DB-25 B ═══]                          │          │
│        │                  CV + AUDIO              INPUTS + PWR                           │          │
│        └─────────────────────────────────────────────────────────────────────────────────┘          │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Panel Element Count

| Category | Count |
|----------|-------|
| 3.5mm Jacks | ~48 |
| Pots (attenuators) | 6 |
| Pots (mod controls) | 6 |
| Pots (utilities) | 6 |
| Total Pots | 18 |
| LEDs | 4 |
| Switches (SPDT/rotary) | 5 |
| Buttons (momentary) | 1 |
| DB-25 connectors | 2 |

---

## PART 8: PHASED BUILD APPROACH

### Phase 1: Core I/O (Minimum Viable Expander)
- All CV outputs (buffered)
- All audio taps (buffered)
- Filter CV, VCA CV, PWM CV inputs (with attenuators)
- VCF insert, Metalizer insert
- Gate I/O (buffered)
- Clock out
- Single DB-25 connection

### Phase 2: Extended I/O
- Hidden DAC outputs (Velocity, Aftertouch, Mod Wheel)
- VCO sync input
- Additional waveform taps
- Second DB-25 connection

### Phase 3: On-Board Utilities
- Analog LFO (Tri/Sqr)
- White noise generator
- Clock divider (/2, /4, /8)
- Manual gate button

### Phase 4: Advanced
- Sample & Hold
- Slew limiter
- Attenuverter
- Buffered mult
- Resonance CV (vactrol circuit)

---

## PART 9: REFERENCE DESIGNS

### Yusynth Circuits to Study

These are directly relevant for expander design:

| Circuit | Relevance | Key Components | URL |
|---------|-----------|----------------|-----|
| **Steiner-Parker VCF** | Filter mod reference | 1N4148 diodes, matched transistors | yusynth.net/Modular/EN/STEINERVCF/ |
| **Wavefolder** | Metalizer CV mod reference | Matched diodes, TL074 | yusynth.net/Modular/EN/WAVEFOLDER/ |
| **Metalizer** | Standalone version with VCA control | BC547 matched pairs | yusynth.net (builders gallery) |
| **Simple VCA** | VCA circuit for mods | LM13700, TL074 | yusynth.net/Modular/EN/VCA/ |
| **ADSR** | Envelope circuit reference | 555/7555, TL074 | yusynth.net/Modular/EN/ADSR/ |
| **VC-LFO** | LFO for expander | 555/7555, TL074 | yusynth.net/Modular/EN/VCLFO/ |
| **Quadrature LFO** | Advanced LFO option | TL074, zener diodes | yusynth.net/Modular/EN/QUADLFO/ |
| **Noise + S&H** | Combined noise/S&H module | 2N3904, CD4066, TL072 | yusynth.net/Modular/EN/NOISE/ |
| **Ring Modulator** | For advanced expander | MC1496 or discrete | yusynth.net/Modular/EN/RINGMOD/ |
| **8 Random Gates** | Clock utilities | CD4024, CD4070, CD4051 | yusynth.net |

### Key Yusynth Techniques

**Noise Generation (Thomas Henry method):**
```
2N3904 reverse-biased B-E junction → 100kΩ → TL072 amplifier (gain ~100)
Output: ~10Vpp white noise
```

**Simple S&H:**
```
Input → CD4066 switch → 1nF capacitor → TL072 buffer
Clock: Schmitt trigger on gate input
Slew: RC integrator on output (variable R)
```

**Analog LFO (triangle core):**
```
TL074 integrator (pin 1-2) + Schmitt comparator (pin 5-7)
Rate: 1MΩ pot in integrator feedback
Outputs: Triangle (integrator), Square (comparator)
Range: 0.05Hz to 50Hz typical
```

**Slew Limiter:**
```
TL072 follower with diode-steered RC in feedback
Linear: Single R + C
Exponential: R + transistor current source
Separate up/down slew possible with dual diode steering
```

### Community Projects

| Project | Creator | Key Features | Notes |
|---------|---------|--------------|-------|
| **Pedrobrute** | Maffez | Full modularization, all inserts | Best reference for complete expansion |
| **MegaBrute** | Steven Oakley | MiniBrute 24+ I/O | Similar scope |
| **MicroBrute-Add-ons** | MKNielsen2000 | PCBs for noise, buffers | GitHub repository |
| **Leafcutter Mods** | Leafcutter John | MiniBrute classics | Attenuverter normalled to env |

### Relevant IC Techniques from Research

**Resonance CV via Vactrol:**
```
The MicroBrute uses PMBFJ111 JFET (RP13) for resonance control.
To add CV: VTL5C3 vactrol in parallel with RP13
CV → 10kΩ → LED side of vactrol
LDR side parallels the JFET
Result: CV opens resonance (higher V = more resonance)
```

**Notch Filter Mode:**
```
Short HP input to LP input (both through mixing resistors)
Results in band-reject response
Can be added as 4th position on filter mode switch
```

**Linear FM Injection:**
```
U17b is the pitch CV summing node (inverting op-amp)
Add 100kΩ series resistor from FM jack to pin 2
Signal adds linearly to pitch CV sum
For audio-rate FM, use smaller R (10-47kΩ) for deeper effect
```

**Phase-Correct Square Wave:**
```
Stock MicroBrute has phase issues between square and saw
Fix: Swap two inputs of comparator op-amp
Requires rewiring 4 resistors or lifting op-amp and rotating
Maffez documents this in detail
```

---

## PART 10: BILL OF MATERIALS (Expander Electronics)

### ICs
| Part | Qty | Function | Package |
|------|-----|----------|---------|
| TL074CN | 5 | Buffers (12 sections), LFO, S&H | DIP-14 |
| TL072CP | 3 | Noise amp, slew, attenuverter, spares | DIP-8 |
| CD40106 | 1 | Gate buffer (Schmitt trigger) | DIP-14 |
| CD4024 | 1 | Clock divider (/2, /4, /8, ...) | DIP-14 |
| CD4066 | 1 | S&H analog switch | DIP-14 |
| LM393 | 1 | Comparator (optional) | DIP-8 |
| MC1496 | 1 | Ring modulator (optional future) | DIP-14 |
| ICL7660 | 1 | -5V charge pump (if needed) | DIP-8 |
| **Total ICs** | **14** | | |

### Transistors
| Part | Qty | Function |
|------|-----|----------|
| 2N3904 | 4 | Noise source, misc NPN |
| 2N3906 | 2 | PNP for symmetrical circuits |
| BC547C | 4 | For matched pairs (optional) |
| VTL5C3 | 1 | Vactrol for resonance CV (optional) |

### Diodes
| Part | Qty | Function |
|------|-----|----------|
| 1N4148 | 20 | Signal diodes, clamps, steering |
| 1N4001 | 4 | Power protection |
| Zener 5.1V | 4 | LFO amplitude limiting |
| LED 3mm (various) | 6 | Gate, LFO, clock indicators |

### Potentiometers
| Part | Value | Qty | Type | Function |
|------|-------|-----|------|----------|
| Alpha 9mm | 100kΩ lin | 10 | Panel pot | CV attenuators, mod controls |
| Alpha 9mm | 100kΩ log | 4 | Panel pot | Audio levels, depth |
| Alpha 9mm | 1MΩ lin | 3 | Panel pot | LFO rate, S&H rate, slew |
| Alpha 9mm | 50kΩ lin | 1 | Panel pot | VCA boost |
| **Total pots** | | **18** | | |

### Resistors (1/4W metal film)
| Value | Qty | Primary Use |
|-------|-----|-------------|
| 1MΩ | 15 | Input bias for buffers |
| 100kΩ | 25 | General, mixing, attenuation |
| 47kΩ | 10 | Mixing, biasing |
| 10kΩ | 20 | General, LED current limit |
| 4.7kΩ | 10 | Biasing |
| 1kΩ | 20 | Output protection, LED current |
| 470Ω | 5 | LED brightness |
| 220kΩ | 5 | Filter CV summing |
| 39kΩ | 5 | PWM CV summing |
| **Assorted kit** | 1 | E24 values, 10-20 of each |

### Capacitors
| Value | Type | Qty | Use |
|-------|------|-----|-----|
| 100nF | Ceramic | 20 | IC decoupling |
| 10nF | Ceramic | 10 | Signal coupling |
| 1nF | Film | 5 | S&H hold capacitor |
| 100pF | Ceramic | 10 | High-freq filtering |
| 10µF | Electrolytic | 6 | Bulk decoupling |
| 100µF | Electrolytic | 4 | Power filtering |
| 1µF | Film | 4 | Audio coupling |
| 470pF | Ceramic | 4 | LFO timing |

### Connectors
| Part | Qty | Notes |
|------|-----|-------|
| DB-25 Female (panel mount) | 2 | Expander side |
| DB-25 Male (solder cup) | 2 | Cable side (to MicroBrute) |
| DB-25 Backshell | 4 | Strain relief |
| Thonkiconn PJ398SM | 50 | 3.5mm mono jacks |
| 16-pin Eurorack IDC header | 1 | Power from bus |
| 10-pin IDC header | 1 | Alternative power |
| IDC ribbon cable (16-pin) | 1m | Bus connection |
| JST-XH 2-pin | 4 | LED connections |
| Pin headers 2.54mm | 2 strips | Board interconnects |

### Switches
| Part | Qty | Function |
|------|-----|----------|
| SPDT mini toggle | 4 | Sync mode, LFO wave, slew mode, KB bypass |
| 4-position rotary | 1 | Filter mode (LP/HP/BP/N) |
| Momentary pushbutton | 1 | Manual gate |

### Panel Hardware
| Part | Qty | Notes |
|------|-----|-------|
| 84HP aluminum panel | 1 | Black anodized, PCBWay/JLCPCB |
| Knobs (soft-touch, 15mm) | 18 | Match MicroBrute aesthetic |
| Hex nuts (Thonkiconn) | 50 | Black anodized preferred |
| M3 standoffs (11mm) | 8 | PCB mounting |
| M3 screws | 20 | Various lengths |
| Eurorack rails + brackets | As needed | If mounting in case |

### Wire & Cable
| Part | Qty | Notes |
|------|-----|-------|
| 22AWG stranded (various colors) | 10m | Signal wiring |
| 24AWG stranded (red, black) | 5m | Power wiring |
| Shielded cable | 2m | Sensitive audio runs |
| DB-25 cable (M-F) | 2× 1m | Pre-made if preferred |
| Heat shrink assortment | 1 kit | Wire management |

### Estimated Costs (2026 prices, approximate)

| Category | Estimate |
|----------|----------|
| ICs | €15-20 |
| Transistors/Diodes | €5-10 |
| Pots (Alpha 9mm × 18) | €20-25 |
| Resistors/Capacitors | €15-20 |
| Connectors (jacks, DB-25, headers) | €35-45 |
| Switches | €10-15 |
| Panel (84HP, PCBWay) | €25-35 |
| Knobs | €15-20 |
| Wire/Cable | €10-15 |
| **TOTAL** | **€150-205** |

*Note: Excludes PCB fabrication if going that route vs stripboard.*

---

## Document Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 2026 | Initial complete expansion map |
