# Arturia MicroBrute Modifications Guide
## Comprehensive Mod Documentation & BOM

Based on extensive research from the modding community, particularly Maffez's "Pedrobrute" and various community contributions.

---

## TABLE OF CONTENTS

1. [Essential Test Point Breakouts](#1-essential-test-point-breakouts)
2. [Oscillator Modifications](#2-oscillator-modifications)
3. [Metalizer/Wavefolder Enhancement](#3-metalizerwavefolder-enhancement)
4. [Filter & VCA Modifications](#4-filter--vca-modifications)
5. [Portamento/CV Routing Improvements](#5-portamentocv-routing-improvements)
6. [LFO Modifications](#6-lfo-modifications)
7. [Sequencer Decoupling](#7-sequencer-decoupling)
8. [Protection & Reliability](#8-protection--reliability)
9. [Advanced Modifications](#9-advanced-modifications)
10. [Complete Bill of Materials](#10-complete-bill-of-materials)

---

## CRITICAL RESOURCES

**Schematics:** http://hackabrute.yusynth.net/index_en.php  
**Modwiggler Thread:** https://modwiggler.com/forum/viewtopic.php?t=152071  
**Maffez Guide:** https://maffez.com/?page_id=2285

**WARNING:** All modifications VOID your warranty. Arturia's designer Yves Usson has published schematics specifically to enable modding.

---

## 1. ESSENTIAL TEST POINT BREAKOUTS

### Basic Waveform Outputs (Easiest Mod)
These are the most popular and straightforward modifications - adding output jacks for internal waveforms.

#### MicroBrute Test Points:
- **TP93** = Square VCO
- **TP94** = Saw VCO  
- **TP102** = Sub Oscillator
- **TP124** = Triangle VCO

#### LFO Outputs (requires MiniBrute reference but similar on Micro):
- PT34 = Saw LFO
- PT32 = Triangle LFO
- PT35 = Sine LFO
- PT33 = Square LFO
- PT130 = Random LFO
- PT176 = Selected LFO

**Implementation:**
- Wire each test point via a 1kΩ resistor to a 3.5mm mono jack
- Use switched jacks if you want normalled routing
- Shallow panel-mount jacks work best (space is tight)

**Components per output:**
- 1x 3.5mm mono jack (switched or non-switched)
- 1x 1kΩ resistor (1/4W)
- Wire (22-24 AWG)

---

## 2. OSCILLATOR MODIFICATIONS

### 2.1 Variable VCO Master Volume

**Purpose:** Control overall waveform mix level while maintaining individual ratios. Allows you to boost signal into filter for resonance character changes or attenuate for cleaner sounds.

**Implementation:**
1. Locate R76 (near UB6 on main PCB)
2. Remove R76 (original value typically 100kΩ)
3. Install B100K potentiometer in its place
4. Mount pot in accessible location

**Range:** From zero to 2x original maximum level

**Audio Benefits:**
- Prevent waveform "mushing" when all levels are up
- Controlled filter input overload for resonance changes
- Better gain staging with external effects

**Components:**
- 1x B100K linear potentiometer
- Panel-mount hardware

---

### 2.2 Buffered VCO Mix Output

**Purpose:** Provides a clean buffered output of the VCO mix before the filter, enabling external filter insertion.

**Implementation:**
1. Remove opamp UB6 from PCB
2. Scratch copper from PCB terminal at pin 5 (disconnect ground)
3. Reinstall UB6
4. Connect UB6 pin 5 to TP30
5. Connect UB6 pin 7 via 1kΩ resistor to new output jack

**Alternative:** If too fiddly, use an additional TL072 or similar opamp as unity-gain buffer

**Components:**
- 1x 1kΩ resistor
- 1x 3.5mm jack
- Optional: TL072 opamp if using external buffer

---

### 2.3 VCO Hard Sync Input

**Purpose:** Allows external oscillator to hard sync the MicroBrute's VCO for classic sync sounds.

**Implementation:**
Well documented in community - adds sync input jack. Exact implementation available in Yves Usson's documentation.

**Components:**
- 1x 3.5mm jack
- Supporting resistors/components per schematic

---

### 2.4 Square Wave Phase Fix

**Purpose:** Fixes phase cancellation issues when mixing square with other waveforms (inherited from MiniBrute design).

**Background:** Factory design has phase issues causing square wave to disappear when saw is added.

**Implementation (Advanced - SMD work required):**
1. Remove UB15 from rear board (above blue trimmers)
2. Cut trace between UB15 pin 6 and R293-R295 junction
3. Cut trace between UB15 pin 5 and R298-R300 junction  
4. Reinstall UB15
5. Solder R293-R295 junction to UB15 pin 5
6. Solder R298-R300 junction to UB15 pin 6

**Effect:** Square wave remains audible when saw is mixed in

**Skill Level:** Advanced (requires precise SMD work)

---

### 2.5 Increased Tuning Range

**Purpose:** Wider sweep range on rear panel tuning pot, especially useful with external CV converters.

**Implementation:**
1. Locate R309 (1MΩ, near blue trimmers)
2. Replace with 100kΩ resistor

**Effect:** Much wider tuning range while maintaining fine control

**Components:**
- 1x 100kΩ resistor (1/4W)

---

## 3. METALIZER/WAVEFOLDER ENHANCEMENT

The Metalizer is a 4-stage wavefolder that can be extensively modded for external use and timbral variation.

### 3.1 Metalizer Input Boost Switch

**Purpose:** Variable input gain to drive the wavefolder harder or softer.

**Implementation:**
1. Wire 100kΩ resistor to ON/ON switch
2. Wire switch across R216 for parallel operation

**Alternative Approaches:**
- Switch between 120kΩ and 75kΩ attenuation
- Use variable pot instead (B100K)
- For extreme boost, reduce R216 to 20kΩ

**Components:**
- 1x ON/ON toggle switch
- 1x 100kΩ resistor (or values for preferred switching)

---

### 3.2 Metalizer Timbre Switch

**Purpose:** Changes the folding character by affecting capacitor values in the folding stages.

**Implementation:**
1. Wire 30kΩ resistor to ON/ON switch
2. Wire switch across C111

**Advanced Options:**
- Additional switches for C107, C106, C110
- Replace R203, R201, R225, R224 (all 120kΩ) with series combination of:
  - 20kΩ fixed resistor
  - B100K pot
  - Gives variable timbre control per stage

**Components:**
- 1x ON/ON toggle switch  
- 1x 30kΩ resistor
- Optional: Multiple switches + resistors for other stages

---

### 3.3 Metalizer Input Insert

**Purpose:** Allows patching external signals through the wavefolder.

**Implementation:**
1. Remove R216 (120kΩ)
2. Wire left terminal to NC lug of switched jack
3. Wire tip lug via 120kΩ resistor to right terminal

**Use Cases:**
- Process external VCOs
- Feedback patches
- Use with different filters

**Components:**
- 1x 3.5mm switched jack
- 1x 120kΩ resistor

---

### 3.4 Metalizer Output

**Purpose:** Direct output from wavefolder for external routing.

**Implementation:**
- Wire TP109 via 1kΩ resistor to output jack

**Components:**
- 1x 3.5mm jack
- 1x 1kΩ resistor

---

## 4. FILTER & VCA MODIFICATIONS

### 4.1 VCA Signal Input Insert

**Purpose:** Insert point before VCA to use external filters while keeping MicroBrute's envelope and VCA.

**Implementation:**
1. Remove R23 (100kΩ)
2. Wire filter-side terminal to NC lug of switched jack
3. Wire tip lug via 100kΩ resistor to other terminal

**Workflow:** VCO Out → External Filter → VCA Insert → VCA/Envelope

**Components:**
- 1x 3.5mm switched jack
- 1x 100kΩ resistor

---

### 4.2 Enhanced VCA Gate/Envelope Control

**Purpose:** Increase VCA response to gate/envelope without driving audio input harder.

**Implementation:**
1. Remove R28 (100kΩ)
2. Install series combination:
   - 50kΩ fixed resistor
   - B50K potentiometer

**Effect:** Variable boost of VCA control voltage

**Components:**
- 1x 50kΩ resistor
- 1x B50K potentiometer

---

### 4.3 VCA CV Input (ESSENTIAL MOD)

**Purpose:** External voltage control of VCA - already designed in, just needs jack!

**Implementation:**
- Install 3.5mm jack in designated location
- All circuit components already present

**Credit:** Yves Usson (original designer)

**Components:**
- 1x 3.5mm jack

---

## 5. PORTAMENTO/CV ROUTING IMPROVEMENTS

### 5.1 Portamento on External CV (HIGHLY RECOMMENDED)

**Purpose:** Stock MicroBrute only applies portamento to internal keyboard/sequencer. This mod routes external CV through portamento circuit.

**Side Effect:** Plugging external CV bypasses internal sequencer/keyboard notes while gates continue - perfect for "gated" rhythmic sequences.

**Implementation:**

**Step 1 - Disconnect Portamento:**
- Identify and cut appropriate traces (see schematic)

**Step 2 - Disconnect CV Input Socket:**
- Prepare switching configuration

**Step 3 - Rewire Internal CV (TP55):**
- Connect TP55 to porta circuit input

**Step 4 - LFO Routing:**
- For LFO hard-wired to pitch: connect to tip lug
- For switchable LFO (stock behavior): connect to NC lug

**Advanced Integration:** Can be combined with sequencer decoupling for full CV/Gate separation.

---

### 5.2 Reduced Portamento Time

**Purpose:** Stock portamento time is too long; this provides more useful short glides.

**Implementation:**
- Replace C38 (4.7µF) with 470nF film capacitor

**Effect:** ~10x faster maximum portamento time with better control in short range

**Components:**
- 1x 470nF film box capacitor

---

## 6. LFO MODIFICATIONS

### 6.1 LFO Audio Rate Mod

**Research Note:** The MicroBrute UFO edition mentions "audio-rate operation" as a feature, suggesting this capability exists in hardware. The standard MicroBrute has a higher maximum LFO rate than the MiniBrute but can be pushed further.

**Potential Approaches:**
1. Replace timing capacitor for higher frequency range
2. Add switch for LFO speed ranges (slow/fast/audio)
3. Add overdrive/boost to LFO output

**Status:** Specific component values need verification from community experimentation

---

## 7. SEQUENCER DECOUPLING

### Full Sequencer/Keyboard Output Separation (ADVANCED)

**Purpose:** Use internal sequencer to control external synths while playing MicroBrute via external CV/Gate. Both operate independently.

**Concept:** 
- Sequencer + Keyboard → CV/Gate outputs only
- MicroBrute sound engine → External CV/Gate inputs only
- Switching happens automatically when jacks are inserted

**Pitch CV:** Already handled by portamento mod above

**Gate Separation (Complex):**

**Background:** Internal gate is post-CPU, external gate input is pre-CPU, requiring circuit redesign.

**Step 1 - Convert Gate Input to Switching Socket:**
1. Remove gate input jack
2. Remove copper from NC lug (both PCB sides)
3. Reinstall jack

**Step 2 - Rewire Internal Gate Bus:**
1. Cut trace between TP82 and ziff connector
2. Wire TP82 to NC lug of gate input jack

**Step 3 - Rebuild External Gate Input Circuit:**
1. Remove R155 and R156
2. Wire their lower terminals together
3. Lift Q7 collector from PCB

**Step 4 - Add NPN-PNP Transistor Switch:**
1. Install new PNP transistor
2. PNP collector → TP56 (front board)
3. PNP base via 22kΩ → Q7 collector  
4. PNP emitter via 10kΩ → +12V

**Components:**
- 1x PNP transistor (2N3906 or similar)
- 1x 22kΩ resistor
- 1x 10kΩ resistor

**Skill Level:** Expert (significant circuit modification)

---

## 8. PROTECTION & RELIABILITY

### Main Output Protection (RECOMMENDED)

**Problem:** Original design has no protection between output jack and opamp input. Load on output can damage output circuit.

**Credit:** Tony Allgood solution (reminiscent of ARP designs)

**Implementation:**
1. Cut trace between UB5 pin 5 and output socket
2. Wire output socket tip lug via 10kΩ resistor to UB5 pin 5
3. Route wire the "long way" around PCB to avoid squeezing

**Effect:** Prevents output circuit damage from short circuits or excessive loads

**Components:**
- 1x 10kΩ resistor (1/4W)

---

## 9. ADVANCED MODIFICATIONS

### 9.1 MIDI Out Mod

**Purpose:** Send MIDI from MicroBrute (sequencer/keyboard) to other devices.

**Implementation:**
- Yellow: DIN pin 5 to LPC2361 pin 82
- Red: DIN pin 4 to 3.3V with 100Ω in series
- Black: DIN pin 2 to ground

**Considerations:**
- LPC2361 pin 82 is tiny - requires precise SMD soldering
- Optional buffering recommended
- This is a semi-official mod

**Components:**
- 1x 5-pin DIN MIDI jack
- 1x 100Ω resistor
- Wire suitable for SMD work

---

### 9.2 Sine Wave Shaper (Experimental)

**Concept:** Test point at VCO triangle shaper could be tapped for sine shaping.

**Status:** Experimental - may require voltage attenuation before routing back to line in

---

### 9.3 Through-Zero PWM (Advanced)

**Status:** Mentioned in community as "interesting" modification but not fully documented

**Potential:** Enhanced pulse width modulation characteristics

---

### 9.4 Linear FM Input (Advanced)

**Concept:** Breakout point for linear FM modulation

**Status:** Test points exist; requires external passive attenuator box for optimal results

---

## 10. COMPLETE BILL OF MATERIALS

### Basic Breakout Package
For simple test point outputs:

**Jacks & Connectors:**
- 8x 3.5mm mono jacks (shallow panel-mount)
- 4x 3.5mm switched jacks

**Resistors (1/4W):**
- 12x 1kΩ
- 4x 10kΩ  
- 4x 100kΩ
- 4x 120kΩ

**Wire:**
- 22-24 AWG stranded hookup wire (multiple colors)

---

### Intermediate Mod Package
Includes VCO, Metalizer, VCA basics:

**Potentiometers:**
- 1x B100K (VCO master volume)
- 1x B50K (VCA envelope boost)

**Switches:**
- 2x ON/ON SPDT toggle
- Panel mounting hardware

**Resistors:**
- 1x 30kΩ (metalizer timbre)
- 1x 50kΩ (VCA mod)
- Various values from Basic Package

**Capacitors:**
- 1x 470nF film box (portamento timing)

**Jacks:**
- All from Basic Package plus:
- 4x additional switched jacks

---

### Advanced Mod Package
Full modification suite:

**Everything from Intermediate Package plus:**

**Transistors:**
- 1x PNP transistor (2N3906 or equivalent)
- Heatshrink tubing

**Additional Resistors:**
- 1x 22kΩ
- 1x 100kΩ (tuning range)
- Multiple values for metalizer stages

**Additional Components:**
- 1x 5-pin DIN connector (MIDI out)
- 1x 100Ω resistor (MIDI)
- SMD rework tools/supplies

**Optional Opamp:**
- 1x TL072 (if using external VCO buffer)
- IC socket

---

### Tools Required

**Essential:**
- Soldering iron (temperature controlled, fine tip)
- Solder (60/40 or lead-free)
- Desoldering braid/pump
- Wire strippers
- Flush cutters
- Small Phillips screwdrivers
- Multimeter

**Recommended:**
- SMD soldering iron tip
- Helping hands/PCB holder
- Magnification (loupe or microscope)
- Continuity tester
- Panel drilling template tools

**Advanced:**
- Hot air rework station (for SMD work)
- Precision tweezers
- Flux pen
- PCB cleaning supplies

---

## MODIFICATION PRIORITY RECOMMENDATIONS

### For Industrial/Techno (Your Genre):

**Tier 1 - Essential:**
1. VCA CV Input (trivial install, huge expansion)
2. Portamento on External CV (critical for sequencing)
3. Main Output Protection (reliability)
4. Metalizer Input Insert (processing external sources)

**Tier 2 - High Value:**
5. Buffered VCO Mix Output (external filter experiments)
6. VCO Master Volume (gain staging, resonance control)
7. Metalizer Output (modular integration)
8. Basic waveform breakouts (TP93, TP94, TP102, TP124)

**Tier 3 - Nice to Have:**
9. Metalizer Timbre/Boost switches (sound design)
10. Enhanced VCA Envelope Control (dynamic control)
11. Reduced Portamento Time (faster sequences)
12. VCA Input Insert (filter experimentation)

**Tier 4 - Advanced:**
13. Square Wave Phase Fix (if you notice the issue)
14. Sequencer Decoupling (dual synth scenarios)
15. MIDI Out (if integrating with MIDI-only gear)

---

## PRACTICAL IMPLEMENTATION NOTES

### Physical Placement Challenges:

The MicroBrute has very high function-to-space ratio. Consider:

**Side Panel Mounting:**
- Easier to access than top panel
- Less interference with internal components
- Good for frequently-used I/O

**Front Panel (if removing audio in):**
- Remove audio in jack and knob
- Provides premium real estate
- Good for main I/O additions

**Rear Panel:**
- Less convenient but more protected
- Good for "set and forget" mods

**Keyboard Removal (Extreme):**
- Some modders remove entire keyboard section
- Creates massive space for controls
- Also removes now-useless octave buttons/LEDs
- Only for desktop/modular use

### Testing Procedure:

After each mod:
1. Visual inspection for shorts/cold joints
2. Continuity testing
3. Power-on test (no audio connections)
4. Audio output test (low volume)
5. Full functionality test
6. Documentation of settings

### Common Mistakes to Avoid:

1. **Shallow jacks required** - Standard jacks hit internal components
2. **Trace cutting** - Double-check before cutting any traces
3. **Heat damage** - Keep iron time on pads minimal
4. **Wire gauge** - Too thick won't fit, too thin breaks easily  
5. **Ground loops** - Star grounding for audio paths
6. **Testing incrementally** - Don't do all mods at once

---

## INTEGRATION WITH YOUR SETUP

Given your current rig (Push 3, TD-3, RD-9):

### MicroBrute as Modular Expander:
- VCO outs → External processing
- Metalizer → Shared wavefolder for all synths
- VCA CV in ← Envelope from RD-9
- Sequencer out → Control TD-3 via MIDI out mod

### With Push 3 Standalone:
- MicroBrute audio in → Push 3 inputs for sampling
- Push 3 CV → MicroBrute CV/Gate ins
- Metalizer for mangling Push 3 audio
- VCO as additional oscillator bank

### Industrial Sound Design:
- Metalizer boost/timbre for harsh textures
- External filters through VCA insert
- VCO mix output to external distortion
- Parallel processing multiple synths through metalizer

---

## RESOURCES & COMMUNITY

**Essential Sites:**
- Maffez Synth Mods: https://maffez.com
- Hack-a-Brute (Yves Usson): http://hackabrute.yusynth.net
- Modwiggler Thread: https://modwiggler.com/forum/viewtopic.php?t=152071

**Video Guides:**
- FluxWithIt basic mod tutorial: https://fluxwithit.com/minibrutemod/

**Support:**
- Modwiggler DIY forum
- Arturia user forums
- Reddit r/synthdiy

---

## SAFETY & LEGAL

**Warranty:** All modifications void warranty immediately

**Safety:**
- Always power off before opening
- Disconnect all cables
- Discharge any capacitors
- Work in well-ventilated area
- Use ESD precautions

**Liability:**
- Modifications are at your own risk
- Arturia provides schematics but no support for mods
- Improper modifications can damage the unit
- Some mods require advanced skills

---

## FUTURE EXPANSION IDEAS

Based on your TD-3 and RD-9 modding experience:

1. **Arduino Integration:**
   - Similar to your TD-3 work
   - Enhanced sequencer features
   - Additional LFO sources
   - Preset management

2. **Eurorack Panel:**
   - Full modular integration
   - Dedicated I/O panel
   - Professional look
   - Easy reconfiguration

3. **External Modulation Board:**
   - Additional envelope generators
   - More LFOs
   - Sample & hold
   - Voltage processing

4. **MIDI Enhancement:**
   - Full MIDI I/O
   - MIDI CC control of all parameters
   - Program change for presets
   - MIDI clock integration

---

## FINAL THOUGHTS

The MicroBrute is exceptionally mod-friendly thanks to Arturia publishing full schematics. Start with simple breakout mods to build confidence, then progress to circuit modifications.

Given your experience modding the TD-3 and RD-9, you're well-equipped to tackle these mods. The metalizer enhancement and CV routing improvements will significantly expand the MicroBrute's capabilities in your industrial/techno setup.

**Recommended Starting Point:**
1. VCA CV input (5 minutes, huge impact)
2. Basic waveform breakouts (1-2 hours, very useful)
3. Portamento mod (2-3 hours, essential for external sequencing)
4. Output protection (30 minutes, prevents future damage)

**Next Steps:**
1. Metalizer I/O and controls
2. VCO modifications
3. Advanced routing mods
4. Consider custom front panel design

Good luck with your build!

---

*Document Version: 1.0*  
*Compiled from community resources, personal mods, and manufacturer documentation*  
*For Jordan's MicroBrute modification project - January 2026*
