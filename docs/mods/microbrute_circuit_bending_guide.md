# MicroBrute Circuit Bending Guide
## Body Contacts, Touch Points & Creative Short Circuits

---

## INTRODUCTION TO CIRCUIT BENDING THE MICROBRUTE

**What Makes the MicroBrute Special for Bending:**
- 100% analog signal path (no digital artifacts)
- Published schematics available (rare for commercial synths!)
- Robust design (harder to kill than digital toys)
- Test points already marked on PCB
- Decent component spacing for experimentation

**Important Distinction:**
Traditional circuit bending = random experimentation on toys
MicroBrute bending = informed experimentation on a well-documented analog synth

This means you can be much more strategic and less destructive.

---

## SAFETY FIRST

### What Makes This Safer Than Typical Bending:

**Advantages:**
- ±12V power supply (won't electrocute you like mains-powered gear)
- Well-designed circuit with protection
- Published schematics mean you know what you're touching

**Risks Still Present:**
- Can damage the unit permanently
- Voids warranty immediately
- Some circuits are more fragile than toy keyboards
- Heat-sensitive components (especially tempcos)

### Safe Probing Technique:

**DO:**
- Use 1kΩ-10kΩ safety resistors when first probing
- Probe with DRY fingers (moisture increases conductivity too much)
- Start with low-voltage areas (signal paths, not power rails)
- Document everything you find

**DON'T:**
- Touch power rails directly (±12V, +5V, +3.3V)
- Short anything to the CPU (LPC2361)
- Touch the tempco resistors or blue trimmers while playing
- Probe with screwdrivers held in sweaty hands initially
- Touch RAM/ROM chips (if present)

---

## PRIME BODY CONTACT CANDIDATES

### Category 1: PITCH MODULATION POINTS

These are the classic "touch vibrato" points where body capacitance affects oscillator frequency.

#### VCO Pitch Control Points:

**R309 (Tuning Resistor Area)**
- Location: Near blue trimmers on rear board
- Effect: Pitch variation/vibrato when touched
- Body Contact Strength: STRONG
- Implementation: Wire one side to bolt, other to ground
- Character: Smooth pitch wobble, good for industrial detuning

**Around the Tempcos (CAREFUL!)**
- Location: Near UB15 on rear board
- Effect: Temperature-sensitive pitch drift simulation
- Body Contact Strength: MEDIUM
- Warning: These are tuning components - touching changes base pitch
- Character: Slow, organic drift (like warming up)

**TP55 (Internal CV)**
- Location: Front board
- Effect: Modulates pitch via internal CV path
- Body Contact Strength: STRONG
- Works with: Portamento circuit (if modded)
- Character: Glitchy pitch jumps, works well with rapid tapping

#### LFO Speed Modulation:

**LFO Timing Components**
- Location: LFO section (check schematic)
- Effect: Changes LFO rate via body capacitance
- Body Contact Strength: MEDIUM-STRONG
- Character: Manual tremolo/vibrato speed control
- Perfect for: Live performance expression

---

### Category 2: FILTER MODULATION POINTS

Body contacts affecting the Steiner-Parker filter can create dynamic timbral changes.

#### Filter Cutoff Modulation:

**Filter CV Input Area**
- Location: Around filter cutoff CV circuit
- Effect: Sweeps filter cutoff via body capacitance
- Body Contact Strength: VARIES (depends on exact point)
- Character: Manual wah effect, very expressive

**Filter Resonance Circuit**
- Location: Resonance pot area
- Effect: Variable resonance/self-oscillation
- Body Contact Strength: MEDIUM
- Warning: Can get screamy fast!
- Character: From subtle emphasis to howling feedback

#### Brute Factor (Feedback) Points:

**Feedback Path Components**
- Location: Brute Factor circuit
- Effect: Variable feedback/distortion intensity
- Body Contact Strength: STRONG
- Character: From warm saturation to unstable chaos
- Industrial Gold: Touch-sensitive distortion!

---

### Category 3: METALIZER WAVEFOLDER POINTS

The metalizer is a 4-stage wavefolder - perfect for body contact exploration.

#### Folding Stage Capacitors:

**C107, C106, C111, C110**
- Location: Metalizer circuit (see maffez guide)
- Effect: Changes folding timbre/intensity
- Body Contact Strength: STRONG
- Character: Harmonic complexity changes, "crunchy" to "smooth"
- Multiple Contacts: Patch between different stages for wild results

**R216 Area (Metalizer Input)**
- Location: Triangle wave input to metalizer
- Effect: Input level modulation
- Body Contact Strength: MEDIUM
- Character: Drives wavefolder harder/softer

---

### Category 4: VCA/ENVELOPE MODULATION

#### VCA Control Points:

**R28 Area (VCA Envelope)**
- Location: Near VCA control circuit
- Effect: Modulates VCA response to envelope
- Body Contact Strength: MEDIUM
- Character: Dynamic amplitude "ducking" or boosting
- Live Use: Touch-sensitive volume control

**Envelope Generator Timing**
- Location: ADSR circuit capacitors
- Effect: Changes attack/decay/release times
- Body Contact Strength: VARIES
- Character: From plucky to slow swells
- Note: Multiple touch points for different stages

---

### Category 5: WAVEFORM MIX MODULATION

#### Oscillator Mix Points:

**Around UB6 (Waveform Mixer)**
- Location: Waveform mixer opamp area
- Effect: Changes balance of waveforms
- Body Contact Strength: MEDIUM-STRONG
- Character: Morphing timbre as you touch/release

**Individual Waveform Outputs (TP93, TP94, etc.)**
- Location: Test points on main board
- Effect: Loading/damping individual waveforms
- Body Contact Strength: WEAK-MEDIUM
- Character: Subtle timbral shifts

---

## ADVANCED BODY CONTACT TECHNIQUES

### Dual-Point Body Contacts (Patch Matrix)

Instead of point-to-ground, wire two interesting points to separate bolts and touch both simultaneously:

**Powerful Combinations:**

1. **LFO Speed + Filter Cutoff**
   - Creates coupled modulation
   - Touch one: LFO changes
   - Touch both: Filter tracks LFO rate changes

2. **Metalizer Stages Cross-Patching**
   - C107 bolt + C111 bolt
   - Tap between them for complex harmonics
   - Your body becomes the coupling capacitor

3. **VCO Pitch + VCA Level**
   - Pitch-sensitive amplitude
   - Touch-theremin effect
   - Great for drones

4. **Portamento + Envelope Decay**
   - Coupled slew behaviors
   - Organic-sounding glides

### Variable Resistance Body Contacts

Add components between touch point and circuit:

**Resistor + Body Contact:**
- 100kΩ in series: Subtle effect
- 10kΩ in series: Medium effect  
- 1kΩ in series: Strong effect but safer

**Potentiometer + Body Contact:**
- Wire pot between circuit point and touch bolt
- Dial in desired sensitivity
- Can "tune" the body contact response

**Capacitor + Body Contact:**
- Small caps (10pF-100pF): High-frequency response
- Medium caps (100pF-1nF): Mid-frequency response
- Larger caps (1nF-10nF): Low-frequency response
- Changes how your touch affects the circuit

---

## CREATIVE SHORT CIRCUITS (NON-BODY CONTACT)

These are traditional bending techniques - shorting points together via switches or pots.

### Clock/Timing Shorts

**LFO to Audio Rate:**
- Short around LFO timing resistor with low-value pot
- Creates audio-rate modulation
- Character: FM-style synthesis, ring mod effects

### Cross-Modulation Shorts

**VCO Hard Sync Abuse:**
- If you've added hard sync input, short sync input to various points
- Try: LFO output, envelope output, filter output (feedback!)
- Character: Chaotic, broken, glitchy

**Envelope to Filter + VCA Simultaneously:**
- Already normalled but add switch to disconnect one
- Allows independent envelope destinations
- Less "bent," more "flexible routing"

### Feedback Shorts

**VCO Mix Output → Filter Input:**
- If you've added buffered VCO out, short to filter input
- Creates feedback loop
- Add pot for control
- Character: Screaming resonance, runaway oscillation

**Metalizer Output → Metalizer Input:**
- Classic wavefolder feedback
- Very unstable, very industrial
- Character: Harmonic explosion

---

## SYSTEMATIC EXPLORATION METHODOLOGY

### Phase 1: Safe Discovery

1. **Build Test Probes:**
   - Two jeweler's screwdrivers
   - Hold one in each hand
   - Your body is the resistor (~10kΩ-1MΩ depending on moisture)

2. **Map Interesting Points:**
   - Touch PCB points while synth is playing
   - Note what affects pitch, timbre, volume
   - Mark promising points with marker

3. **Document Everything:**
   - Photo reference with numbered points
   - Spreadsheet of effects per point
   - Audio recordings of findings

### Phase 2: Safety Testing

1. **Use Safety Resistor (10kΩ):**
   - Wire between test leads
   - If something would fry, resistor burns first
   - Swap and continue

2. **Check Voltage Levels:**
   - Use multimeter
   - Avoid anything near power rails
   - Signal paths are safer

3. **Test Short Duration:**
   - Tap briefly, don't hold
   - Listen for distress (crackling, silence)
   - Back off if sounds wrong

### Phase 3: Implementation

1. **Choose Best Effects:**
   - Pick 5-8 favorite discoveries
   - Prioritize most expressive/useful

2. **Install Tactile Controls:**
   - Bolts/screws for body contacts
   - Switches for on/off shorts
   - Pots for variable shorts

3. **Label Clearly:**
   - What does each control do?
   - Settings that sound good
   - Danger zones to avoid

---

## BODY CONTACT HARDWARE OPTIONS

### Mounting Methods:

**Hex Bolts (Classic):**
- M3 or M4 threaded bolts
- Mount through drilled holes
- Secure with nut on inside
- Pro: Cheap, effective
- Con: Utilitarian look

**Drawer Knobs (Fancy):**
- Brass or copper drawer pulls
- More surface area
- Comfortable to touch
- Pro: Elegant appearance
- Con: More expensive

**Banana Jacks (Modular):**
- Standard banana jacks
- Patch to different points
- Ultimate flexibility
- Pro: Reconfigurable
- Con: Requires patch cables

**Copper Tape Strips:**
- Long strips of copper tape
- Touch different positions for different effects
- Can create "keyboard" of touch points
- Pro: Expressive, unique
- Con: Not durable

---

## SPECIFIC MICROBRUTE BEND RECOMMENDATIONS

### For Industrial/Techno (Your Genre):

**Priority Touch Points:**

1. **Metalizer Drive/Timbre Body Contacts**
   - 2-3 bolts on different folding stages
   - Touch during harsh basslines
   - Instant harmonic variation

2. **Filter Cutoff Sweep Contact**
   - Manual wah for aggressive filtering
   - Patch LFO to cutoff, touch to override
   - Live performance tool

3. **Brute Factor Intensity Contact**
   - Touch-sensitive distortion
   - From clean to destroyed in one touch
   - Perfect for breakdowns

4. **VCO Detune Contact**
   - Pitch instability on demand
   - Creates movement in drones
   - Analog "drift" simulation

5. **Dual-Point LFO Speed + Filter**
   - Coupled modulation madness
   - Creates complex, evolving textures
   - Very "industrial"

**Switches to Add:**

1. **Metalizer Feedback Loop**
   - Output to input short
   - ON/OFF switch with series pot
   - Controlled chaos

2. **Envelope Speed Switch**
   - Swap timing caps
   - Fast pluck / slow swell toggle
   - Performance switch

3. **LFO Range Switch**
   - Slow/Fast/Audio toggle
   - Low/mid/high value caps
   - Expands modulation range

---

## INTEGRATION WITH YOUR EXISTING MODS

### Combining Circuit Bending + Planned Mods:

**Synergy Opportunities:**

1. **Body Contacts + Portamento Mod:**
   - Touch point on portamento circuit
   - Variable glide time via body capacitance
   - Touch harder = faster glide

2. **Metalizer I/O + Feedback Bends:**
   - External processing through metalizer
   - Body contacts on metalizer stages
   - Feedback switch
   - = Ultimate industrial mangler

3. **VCO Mix Out + Filter Touch:**
   - Use buffered VCO out as external signal
   - Route to external filter
   - Body contact on external filter
   - Return to VCA insert

4. **Sequencer Decoupling + Pitch Bends:**
   - Internal sequencer running patterns
   - Touch pitch points doesn't affect sequence
   - Sequence stays stable, timbre goes wild

---

## DOCUMENTATION TEMPLATE

Use this to record your findings:

```
BODY CONTACT TEST SHEET
========================

Contact Point: _______________
PCB Location: _______________
Component Nearby: _______________

Effect on PITCH: [ ] None [ ] Slight [ ] Moderate [ ] Strong
Effect on TIMBRE: [ ] None [ ] Slight [ ] Moderate [ ] Strong
Effect on VOLUME: [ ] None [ ] Slight [ ] Moderate [ ] Strong
Effect on STABILITY: [ ] Stable [ ] Slight drift [ ] Unstable

Character Description:
_________________________________
_________________________________

Best Use Case:
_________________________________

Audio Sample File: _______________

Safety Notes:
_________________________________

INSTALLED: [ ] Yes [ ] No
Hardware Used: _______________
Panel Location: _______________
```

---

## TROUBLESHOOTING BENT MICROBRUTES

### Common Issues:

**Body Contact Has No Effect:**
- Check wire connections
- Ensure contact point is exposed metal
- Try different nearby points
- May need series resistor

**Effect Too Subtle:**
- Remove series resistor (if present)
- Try larger contact surface area
- Wet your fingers slightly
- Try different point on same circuit

**Effect Too Extreme/Unstable:**
- Add series resistor (10kΩ-100kΩ)
- Add series capacitor (10pF-100pF)
- Move to less sensitive point nearby
- Add on/off switch to disable

**Synth Crashes When Touched:**
- You've found a critical point
- Add larger safety resistor
- Mark as "do not touch"
- May be power-related

**Base Pitch Changed After Install:**
- Touched tempco or trimmer
- Re-tune using rear panel pot
- May need to adjust blue trimmers
- Document new tuning procedure

---

## INSPIRATION: SUCCESSFUL BENT SYNTHS

**Historical Reference:**
- Serge Tcherepnin's body contact experiments (1950s!)
- Thaddeus Cahill's Telharmonium (1897) - touch-sensitive
- Modern: Look Mum No Computer's circuit bent builds

**Commercial "Bent" Modules:**
- SynthTech E950 Circuit Bent VCO
  - Speak & Spell technology with controlled bending
  - Proves concept of "repeatable circuit bending"
  - Lattice filter coefficient modulation via CV

**MicroBrute-Specific:**
- Maffez's "Pedrobrute"
- Various Modwiggler builds
- Focus on metalizer enhancement

---

## FINAL THOUGHTS: PHILOSOPHY OF BENDING THE MICROBRUTE

### Why Bend a Modern Synth?

**Against Traditional Bending Ethos:**
- "Real" bending is random discovery
- Should be toys/cheap gear
- Shouldn't study schematics

**For Informed Exploration:**
- Arturia published schematics FOR THIS PURPOSE
- You own the instrument
- Knowledge reduces destructive mistakes
- Can still discover unexpected interactions

### The Sweet Spot:

**Informed Randomness:**
- Use schematics to identify safe/unsafe areas
- Random probe within safe areas
- Document systematically
- Implement best discoveries
- = Maximum creativity, minimum destruction

### For Your Setup:

Given your TD-3 and RD-9 modding experience, you understand analog circuits. The MicroBrute gives you a chance to explore **expressive, performance-oriented bending** rather than just making weird noises.

**Your Industrial/Techno Context:**
- Touch-sensitive distortion = performance tool
- Feedback switches = rhythmic chaos
- Coupled modulation = evolving textures
- Pitch instability = analog drift

This isn't "let's make a toy sound weird" - it's "let's add human-body expressiveness to an already great synth."

---

## RECOMMENDED STARTING POINTS

### First Three Body Contacts to Try:

1. **R309 Area (Pitch Touch)**
   - Easy to find (near blue trimmers)
   - Strong, predictable effect
   - Builds confidence

2. **Metalizer Stage (C111)**
   - Dramatic timbre change
   - Very industrial
   - Perfect for your genre

3. **Filter Cutoff CV Area**
   - Expressive
   - Useful in many contexts
   - Classic synth control

### First Switch Mod to Try:

**Metalizer Timbre Switch (from planned mods):**
- Already documented
- Safe circuit modification
- Immediate sonic payoff
- Gateway to feedback experiments

---

## RESOURCES & COMMUNITY

**Essential Reading:**
- Anti-Theory Circuit Bending Guide: http://www.anti-theory.com/soundart/circuitbend/
- Circuit Bending Wiki: https://circuitbending.miraheze.org/
- Maffez Pedrobrute: https://maffez.com/?page_id=2285

**Communities:**
- Modwiggler Circuit Bending Forum
- Reddit r/synthdiy
- Look Mum No Computer Discord

**Audio Examples:**
Search YouTube for:
- "circuit bent synthesizer"
- "body contact synth"
- "touch theremin"
- "microbrute mods"

---

*Document Version: 1.0*  
*For Jordan's MicroBrute Circuit Bending Exploration*  
*Companion to MicroBrute Modifications Guide*
