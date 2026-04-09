# THE ULTIMATE MICROBRUTE PROJECT
## Deep Modding, Circuit Bending & Hardware Hacking Blueprint

**Project Codename:** ÜBERBRUTE  
**Target:** Build the most extensively modified MicroBrute ever documented  
**Author:** Jordan (jordanaftermidnight)  
**Started:** March 2026

---

## PROJECT PHILOSOPHY

This isn't just "adding a few jacks." This is a **complete exploration** of the MicroBrute's potential:

1. **Exploit every unpopulated component footprint**
2. **Access unused opamp sections**
3. **Leverage the fully-populated JTAG interface**
4. **Full signal path modularization**
5. **Circuit bending with body contacts**
6. **Create new circuits using existing PCB real estate**
7. **Firmware exploration via LPC2361**

**Goal:** Surpass Maffez's "Pedrobrute" and MegaBrute as the definitive MicroBrute modification reference.

---

## PART 1: HARDWARE ARCHITECTURE DEEP DIVE

### The MicroBrute PCB Layout

The MicroBrute uses a **two-board design:**

**FRONT BOARD (User Interface):**
- VCO pots and sliders
- Filter section
- Envelope section
- VCA section
- Mod matrix patchbay
- Brute Factor control
- Portamento

**REAR BOARD (Signal Processing):**
- VCO core and waveshapers
- Metalizer circuit
- Saw animator (Ultrasaw)
- Sub-oscillator/5th
- LFO and PWM
- DAC (for sequencer CV)
- MIDI interface
- USB interface
- **LPC2361 ARM7 microcontroller**
- **JTAG interface (FULLY POPULATED!)**
- Power supply sections
- Audio output stage
- CV/Gate I/O

### Key ICs to Understand:

| IC | Function | Notes |
|----|----------|-------|
| LPC2361 | ARM7 MCU | Controls sequencer, MIDI, USB, keyboard scanning |
| Various TL07x | Opamps | Waveform mixing, buffering, filtering |
| Various transistors | VCA, VCO core | BJT-based analog circuits |

---

## PART 2: UNPOPULATED COMPONENT ANALYSIS

### Why Unpopulated Footprints Exist:

1. **Design iteration** - Arturia tested variations
2. **Cost reduction** - Removed non-essential features
3. **Future-proofing** - Planned features that didn't ship
4. **Filter network options** - Alternative frequency responses
5. **Debug/test points** - Factory calibration

### Strategy for Unpopulated Components:

**STEP 1: Full PCB Mapping**
- Photograph both sides of both boards at high resolution
- Create overlay with schematic sections
- Identify all unpopulated footprints
- Cross-reference with schematics
- Document component designators

**STEP 2: Circuit Analysis**
For each unpopulated footprint:
- Trace where it connects
- Determine what circuit section it belongs to
- Analyze what function it would serve if populated
- Calculate appropriate component values

**STEP 3: Categorize Modifications**
- Category A: Direct population (add missing component)
- Category B: Value modification (different values than intended)
- Category C: Repurposing (use footprint for different function)

### Known Unpopulated Areas to Investigate:

**VCO Section:**
- Additional waveshaping capacitors
- Filter networks for waveform conditioning
- Potential second VCO sync input?

**Filter Section:**
- Steiner-Parker filter has known unpopulated options
- Resonance limiting resistors
- Alternative filter character components

**LFO Section:**
- Range extension components
- Waveform shaping networks
- Audio rate modification components

**Power Section:**
- Additional filtering capacitors
- Protection diodes (some may be unpopulated)
- Voltage reference options

**Output Section:**
- Buffer configurations
- Protection networks
- Level adjustment components

---

## PART 3: UNUSED OPAMP SECTIONS

The MicroBrute uses dual and quad opamp packages (TL072, TL074). Often one section goes unused.

### Confirmed Unused Opamps:

**UB6 - Waveform Mixer Area:**
- One opamp section unused
- Currently configured as voltage follower (input to GND)
- **Maffez's mod:** Repurpose as VCO mix output buffer
- **Your expansion:** Use as additional CV processor, mixer stage, or buffer

**Other Potential Unused Sections:**
(Need to verify with schematic cross-reference)
- Check every TL07x package
- Map pin usage vs schematic
- Identify unused halves/quarters

### Applications for Unused Opamps:

1. **Additional buffers** - Isolate sensitive circuit points
2. **CV mixers** - Sum multiple CV sources
3. **Inverting amplifiers** - Create inverted CV/audio
4. **Active filters** - Additional tone shaping
5. **Comparators** - Waveshaping, gate generation
6. **Sample and hold** - With external cap/switch

---

## PART 4: THE LPC2361 & JTAG EXPLORATION

### About the LPC2361:

**Specifications:**
- ARM7TDMI-S core (32-bit RISC)
- 64KB Flash program memory
- 34KB SRAM
- Up to 72 MHz clock
- In-System Programming (ISP)
- In-Application Programming (IAP)
- 10-bit ADC and DAC
- 4x UARTs, SPI, I2C
- 70 GPIO pins
- **JTAG interface for debugging**

**What it does in MicroBrute:**
- Scans keyboard
- Runs step sequencer
- Handles MIDI I/O
- Handles USB communication
- Controls DAC for pitch CV output
- Generates gate signals
- Handles mod wheel
- Configuration storage

### JTAG Interface (FULLY POPULATED!)

**This is HUGE.** Most manufacturers remove JTAG after production to prevent reverse engineering. Arturia left it populated!

**JTAG Capabilities:**
- Read/write CPU registers
- Read/write memory
- Flash programming
- Hardware breakpoints
- Real-time debugging
- Firmware extraction (if not protected)

**Required Tools:**
- JTAG adapter (J-Link, Black Magic Probe, or cheap FT2232-based)
- OpenOCD (free, open source)
- ARM toolchain (gcc-arm-none-eabi)
- Flash Magic (NXP's official programmer)

### Firmware Exploration Strategy:

**Phase 1: Non-Invasive Analysis**
1. Connect JTAG adapter
2. Attempt to read chip ID (verify connectivity)
3. Check if Code Read Protection (CRP) is enabled
4. If CRP disabled: Extract firmware binary

**Phase 2: Firmware Analysis (if extracted)**
1. Disassemble with Ghidra or IDA
2. Identify:
   - Sequencer logic
   - MIDI handling routines
   - USB descriptors
   - Configuration storage
   - Calibration routines
   - Unused GPIO assignments

**Phase 3: Potential Modifications**
- Custom sequencer behavior
- Extended MIDI CC mapping
- Additional CV output modes
- Clock output from spare GPIO
- Custom arpeggiator patterns
- User-defined LFO sync divisions

**CRITICAL WARNINGS:**
- **BACKUP FIRMWARE FIRST** (if extraction possible)
- Code Read Protection may prevent reading
- Wrong flash writes = bricked synth
- Have recovery plan (ISP via UART)
- Arturia updates via USB may overwrite changes

### MIDI Out Mod (Already Documented):

The MIDI Out mod accesses the LPC2361 UART:
- Yellow: DIN pin 5 → LPC2361 pin 82 (TX)
- Red: DIN pin 4 → 3.3V via 100Ω
- Black: DIN pin 2 → Ground

**Pin 82 is tiny!** Requires:
- Fine-tipped soldering iron
- Magnification
- Steady hands
- Flux
- Fine solder (0.5mm or less)

---

## PART 5: FULL SIGNAL PATH MODULARIZATION

### The Vision:

Convert the MicroBrute from a semi-modular synth to a **fully modular architecture** where every circuit block can be:
- Bypassed
- Rerouted
- Fed external signals
- Output to external processing

### Circuit Blocks to Modularize:

**1. VCO Section**
```
INPUTS:
- External pitch CV (already exists, but improve)
- Hard sync input (add)
- Linear FM input (add)
- Soft sync input (advanced)

OUTPUTS:
- Raw sawtooth (buffered)
- Raw triangle (buffered)
- Raw pulse (buffered)
- Sub oscillator (buffered)
```

**2. Waveform Mixer**
```
INPUTS:
- External audio to mix (via switched jack)

OUTPUTS:
- Buffered VCO mix (pre-filter)
- Individual waveforms (as above)

CONTROLS:
- VCO master volume (replaces R76)
```

**3. Metalizer (Wavefolder)**
```
INPUTS:
- External audio input (insert)
- CV for fold amount (add)
- Timbre CV (advanced)

OUTPUTS:
- Metalizer output (post-fold)

CONTROLS:
- Input boost switch/pot
- Timbre switch(es) for each stage
- Feedback amount (insert loop)
```

**4. Filter (Steiner-Parker)**
```
INPUTS:
- External audio input (insert)
- Filter FM (already exists via mod matrix)
- External CV (already exists)

OUTPUTS:
- Lowpass out (direct tap)
- Bandpass out (direct tap)
- Highpass out (direct tap)

CONTROLS:
- Resonance character mods
- Self-oscillation stability
```

**5. VCA**
```
INPUTS:
- External audio input (insert) - DONE (existing mod)
- External CV input - DONE (Yves Usson mod)

OUTPUTS:
- Pre-VCA tap
- VCA direct out

CONTROLS:
- VCA boost pot
- Initial level expansion
```

**6. Envelope Generator**
```
OUTPUTS:
- Envelope out (already on mod matrix)
- Inverted envelope (add)
- End-of-cycle trigger (add, from comparator)

CONTROLS:
- Stage time range extensions
- Retrigger options
```

**7. LFO**
```
OUTPUTS:
- All waveforms (individual outs)
- Square for sync/gate

CONTROLS:
- Audio rate mod
- Sync to external clock
- One-shot mode
```

**8. Sequencer/CV**
```
OUTPUTS:
- Pitch CV (exists)
- Gate (exists)
- Clock out (ADD - critical missing feature!)
- Trigger out (ADD)
- Reset out (ADD)

INPUTS:
- External clock (via MIDI currently, add analog)
- Reset in (add)
- Run/stop gate (add)
```

---

## PART 6: ADVANCED BODY CONTACT SYSTEM

### Beyond Basic Touch Points:

**Concept: Touch Synthesizer Integration**

Create a **performance-oriented touch interface** using multiple body contacts wired to:
- Patch matrix (switchable destinations)
- Variable resistance networks
- Capacitor coupling for different response

### The "Neural Interface" Mod:

**Hardware:**
- 8-12 brass touch points mounted on custom panel
- Internal patch matrix (analog switch IC like CD4066)
- Destination selection via DIP switches or rotary

**Destinations:**
1. VCO pitch
2. Filter cutoff
3. LFO rate
4. Resonance
5. Metalizer stages (multiple)
6. VCA level
7. Envelope times
8. Brute Factor

**Enhancements:**
- Pressure-sensitive (via photoresistor + LED in enclosure)
- Wet/dry sensing (humidity affects response)
- Dual-point interactions (touch two for combined effect)

---

## PART 7: PHYSICAL MODIFICATIONS

### Panel/Enclosure Options:

**Option A: Retain Original Form Factor**
- Add jacks to sides
- Replace audio-in with mod controls
- Use micro switches internally
- Shallow panel-mount jacks only

**Option B: Extended Rear Panel**
- Custom rear panel plate
- All I/O accessible
- Keeps front clean
- Room for power LED mods

**Option C: Desktop Rackmount Conversion**
- Remove keyboard
- Create 19" or custom rackmount
- Full modular patchbay exposed
- Eurorack power integration possible

**Option D: Eurorack Module Conversion**
- Most extreme
- PCBs rehouse in Eurorack format
- Remove keyboard entirely
- Full modular compatibility
- Preserves unique MicroBrute sound

### Control Placement Strategy:

**Priority 1 Controls (Most Used):**
- VCO mix level pot
- Metalizer input boost
- VCA CV attenuator
- LFO rate fine control

**Priority 2 Controls (Performance):**
- Body contact array
- Feedback switches
- Range toggles

**Priority 3 Controls (Set and Forget):**
- Internal trimmers
- DIP switches for routing options
- Jumpers for permanent mods

---

## PART 8: NEW CIRCUITS TO ADD

### Using Unused PCB Real Estate:

**1. White Noise Generator**
The MicroBrute has NO noise source. Add one!

**Simple Transistor Noise:**
```
Components:
- 1x BC547 (or similar NPN)
- 1x 100K resistor
- 1x 10nF capacitor
- Opamp buffer (use unused section)

Principle: Reverse-bias transistor junction for avalanche noise
Location: Near unused opamp area
Output: To mod matrix or dedicated jack
```

**2. Sample & Hold**
MicroBrute has random LFO but no S&H. Add one!

**Simple S&H:**
```
Components:
- 1x CD4066 analog switch (or single JFET)
- 1x 100nF polystyrene cap
- 1x opamp buffer (unused section)

Trigger: LFO square, gate, or external
Input: Noise source or any CV
Output: Stepped random CV
```

**3. Slew Limiter**
The portamento is limited. Add external slew!

**Simple Slew:**
```
Components:
- 1x 100K pot
- 1x 1µF capacitor
- 1x opamp buffer

Function: Variable lag on any CV
Great for: External pitch CV, filter CV smoothing
```

**4. Clock Divider**
MicroBrute sequencer has no clock out. Fix this!

**4017 Decade Counter Divider:**
```
Components:
- 1x CD4017 decade counter
- 1x CD4024 binary counter
- Resistors for reset configuration

Outputs: /2, /4, /8, /16 clock divisions
Bonus: Use 4017 outputs for trigger sequencing
```

**5. Voltage-Controlled LFO Rate**
Make LFO rate voltage-controllable!

**Mod Options:**
- Replace timing resistor with VCA (LM13700)
- Add external CV attenuator
- Sum with existing rate pot

---

## PART 9: COMPLETE MODIFICATION CHECKLIST

### Phase 1: Foundation (Essential)
- [ ] Photograph and document entire PCB (both sides, both boards)
- [ ] Acquire and study official schematics
- [ ] Map all unpopulated footprints
- [ ] Identify unused opamp sections
- [ ] Add output protection (10K at output)
- [ ] Add VCA CV input (Yves Usson mod)
- [ ] Basic waveform breakouts (TP93, TP94, TP102, TP124)

### Phase 2: Core Routing Mods
- [ ] Portamento on external CV mod
- [ ] VCO master volume pot (R76 replacement)
- [ ] Buffered VCO mix output (UB6 repurpose)
- [ ] Hard sync input
- [ ] Metalizer input insert
- [ ] Metalizer output
- [ ] VCA input insert
- [ ] LFO output jack
- [ ] Square wave phase fix

### Phase 3: Enhanced Control
- [ ] Metalizer input boost (switch or pot)
- [ ] Metalizer timbre switches (per-stage)
- [ ] Extended tuning range (R309)
- [ ] Reduced portamento time (C38)
- [ ] VCA envelope boost (R28)

### Phase 4: Sequencer & CV
- [ ] MIDI Out mod
- [ ] Clock output mod (research required)
- [ ] Gate output normalling options
- [ ] Sequencer/keyboard decoupling (advanced)

### Phase 5: New Circuits
- [ ] White noise generator
- [ ] Sample & hold
- [ ] Clock divider
- [ ] Additional CV processing

### Phase 6: Body Contacts & Bending
- [ ] Map all touch-sensitive points
- [ ] Install 4-8 body contact points
- [ ] Dual-point interaction system
- [ ] Variable resistance networks

### Phase 7: JTAG/Firmware (Advanced)
- [ ] Connect JTAG adapter
- [ ] Check CRP status
- [ ] Backup firmware (if possible)
- [ ] Analyze code structure
- [ ] Identify modification opportunities
- [ ] Implement custom firmware changes

### Phase 8: Physical Build
- [ ] Design custom panel(s)
- [ ] Install all jacks and controls
- [ ] Wire everything
- [ ] Full system test
- [ ] Document final configuration

---

## PART 10: BILL OF MATERIALS (MASTER LIST)

### Jacks (3.5mm Mono):
| Qty | Type | Purpose |
|-----|------|---------|
| 4 | Non-switched | Waveform outputs |
| 6 | Switched | Insert points |
| 4 | Non-switched | CV outputs |
| 2 | Switched | External inputs |

### Potentiometers:
| Qty | Value | Type | Purpose |
|-----|-------|------|---------|
| 1 | B100K | Linear | VCO mix level |
| 1 | B50K | Linear | VCA boost |
| 1 | B100K | Linear | Metalizer input |
| 2 | B100K | Linear | CV attenuators |

### Switches:
| Qty | Type | Purpose |
|-----|------|---------|
| 3 | SPDT ON-ON | Metalizer timbre |
| 2 | SPDT ON-ON | Input boost |
| 1 | SPST momentary | Reset/trigger |
| 1 | DPDT | Routing options |

### Resistors (1/4W):
| Value | Qty | Purpose |
|-------|-----|---------|
| 1K | 10 | Output buffers |
| 10K | 5 | Protection, mixing |
| 22K | 2 | Gate mod |
| 47K | 4 | Various |
| 100K | 10 | Mixing, CV |
| 120K | 2 | Metalizer insert |

### Capacitors:
| Value | Type | Qty | Purpose |
|-------|------|-----|---------|
| 470nF | Film | 1 | Portamento speed |
| 100nF | Ceramic | 10 | Decoupling |
| 10nF | Film | 5 | Various |
| 10µF | Electrolytic | 2 | Power |

### ICs:
| Part | Qty | Purpose |
|------|-----|---------|
| TL072 | 2 | Additional buffers |
| CD4066 | 1 | Analog switching |
| CD4017 | 1 | Clock divider |
| BC547 | 2 | Noise, comparator |
| 2N3906 | 1 | Gate mod |

### Body Contact Hardware:
- 8x M4 brass bolts
- 8x M4 brass nuts
- 8x insulating washers
- Copper wire (stranded, 22AWG)

### JTAG Tools:
- 1x J-Link EDU Mini (~$20) OR
- 1x Black Magic Probe (~$60) OR
- 1x FT2232H breakout (~$15)
- 10-pin JTAG cable

### Misc:
- 22-24 AWG stranded wire (multiple colors)
- Heat shrink tubing
- Hot glue
- Solder (60/40 or lead-free)
- Flux
- Kapton tape

---

## PART 11: DOCUMENTATION STANDARDS

### For Each Modification:

1. **Before Photo** - Original state
2. **Schematic Section** - Relevant circuit portion
3. **Modification Diagram** - What changes
4. **Component Values** - Exact specifications
5. **Procedure Steps** - Numbered instructions
6. **After Photo** - Completed mod
7. **Audio/Video Demo** - Working demonstration
8. **Troubleshooting** - Common issues

### File Naming Convention:
```
UBERBRUTE_[SECTION]_[MOD-NAME]_v[VERSION].[EXT]

Examples:
UBERBRUTE_VCO_MasterVolume_v1.0.md
UBERBRUTE_METALIZER_InputInsert_v1.2.md
UBERBRUTE_JTAG_FirmwareDump_v0.1.md
```

### Repository Structure:
```
/uberbrute-project
├── /docs
│   ├── /schematics (annotated)
│   ├── /pcb-photos
│   └── /mod-guides
├── /firmware
│   ├── /original (backup)
│   ├── /modified
│   └── /tools
├── /hardware
│   ├── /panel-designs
│   ├── /bom
│   └── /wiring-diagrams
├── /media
│   ├── /audio-demos
│   └── /video-demos
└── README.md
```

---

## PART 12: RESEARCH TASKS

### Immediate Actions:

1. **Download all MicroBrute schematics**
   - https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
   - Front board: All pages
   - Rear board: All pages
   - Component layouts

2. **Create high-res PCB documentation**
   - Both boards
   - Both sides
   - Macro shots of IC areas
   - Detail shots of unpopulated areas

3. **Cross-reference schematics with PCB**
   - Mark every unpopulated footprint
   - Trace connections
   - Calculate missing component values

4. **JTAG Investigation**
   - Locate JTAG header pinout
   - Determine voltage levels (likely 3.3V)
   - Plan first connection attempt

5. **Community Research**
   - Modwiggler MicroBrute thread (all pages)
   - Maffez site (complete study)
   - Hack-a-Brute site (complete study)
   - Contact advanced modders for insights

### Questions to Answer:

- [ ] What is the exact function of each unpopulated footprint?
- [ ] Which opamp sections are truly unused?
- [ ] Is the LPC2361 code read protected?
- [ ] What GPIO pins are unused on the MCU?
- [ ] Can clock be derived from existing MCU outputs?
- [ ] What modifications conflict with each other?
- [ ] What is maximum current draw for additions?
- [ ] Can Eurorack power be safely integrated?

---

## PART 13: SAFETY & RECOVERY

### Before Starting:

1. **Full backup documentation** of unmodified state
2. **Identify all critical circuits** that could brick the synth
3. **Plan recovery procedures** for each modification
4. **Keep original components** (don't throw anything away)

### Emergency Recovery:

**If output dies:**
- Check output protection mod
- Verify opamp supply voltages
- Check for shorts to ground

**If no sound at all:**
- Verify power rails (+12V, -12V, +5V, +3.3V)
- Check VCO is oscillating (scope on TP)
- Verify VCA is responding to gate

**If firmware corrupted:**
- LPC2361 has ISP (In-System Programming) via UART
- Connect UART to P0.0 (TXD0) and P0.1 (RXD0)
- Use Flash Magic to reload
- Boot mode pins may need grounding

**If keyboard doesn't work:**
- MCU scanning issue
- Check ziff connector seated properly
- Verify MCU power

---

## CONCLUSION

This project will take months, possibly longer. But the result will be:

**The most comprehensively documented and extensively modified MicroBrute in existence.**

Every modification will be:
- Fully documented
- Reversible where possible
- Photographed
- Demonstrated with audio/video
- Shared with the community

**This is not just a mod project - it's a complete exploration of what the MicroBrute platform can become.**

---

## NEXT STEPS

1. **Order JTAG adapter** (recommend Black Magic Probe or J-Link EDU Mini)
2. **Download and print all schematics**
3. **Create PCB photo documentation**
4. **Begin unpopulated component mapping**
5. **Start with simple, reversible mods** (VCA CV, output protection)
6. **Document everything from day one**

---

*Document Version: 1.0*  
*Project Start Date: March 2026*  
*For Jordan's Ultimate MicroBrute Build*

**"The MicroBrute is just the beginning. What we build is the ÜBERBRUTE."**
