# MACROBRUTE: Comprehensive Modification Research 

**Project:** Arturia MicroBrute Deep Modification  
**Codename:** MACROBRUTE  
**Date:** April 2026  
**Purpose:** Complete technical reference for all subsystems

---

## Overview

The MACROBRUTE project transforms an Arturia MicroBrute into a semi-modular industrial instrument through internal sound mods, a custom Eurorack expander, CV-controlled delay, integrated oscilloscope, Raspberry Pi Pico digital control, and a DB-9 interconnect system. This report consolidates every technical detail needed across all eight subsystems.

---

## Area 1: MicroBrute Internal Modifications

### 1A. Maffez/Pedrobrute Sound Enhancement Mods

**Waveform mix level boost (R76):**
- Replace R76 (near IC UB6) with B100K linear potentiometer
- Allows 0 to 2× stock level
- At lower settings reduces "mushiness" when all waveforms are fully up
- At higher settings intentionally overloads filter input

**Square wave phase correction:**
- Two inputs of relevant opamp are swapped by rewiring four resistors
- Eliminates destructive interference when mixing square with saw/triangle
- Subjective — some users prefer the phased character

**VCA boost (R28):**
- Replace R28 (100kΩ) with 50kΩ resistor + 50kΩ pot in series
- Increases VCA control signal amplitude
- WARNING: Do NOT reduce R23 for increased drive — causes undesirable distortion

**Filter insert (R23):**
- Remove R23 (100kΩ), wire through switched 3.5mm jack with 100kΩ resistor
- Creates send/return insert between VCO section and VCA
- Signal passes normally when no jack inserted

**Metalizer output tap (TP109):**
- Wire via 1kΩ series resistor to output jack
- Provides separate wave-folded triangle output

**Fine-tune range expansion (R309):**
- Replace R309 (1MΩ) with 100kΩ
- Dramatically widens fine-tune pot sweep

**Portamento time reduction (C38):**
- Replace C38 (4.7µF electrolytic) with 470nF film box capacitor
- Shorter portamento and finer control

**Unused opamp buffer (UB6 pin 5):**
- Remove ground from pin 5 of UB6
- Repurpose spare opamp as general-purpose buffer

### 1B. Yusynth/Hackabrute Modifications

**VCA CV input:**
- Add jack socket to inject external CV into VCA control path
- Enables tremolo, external envelope control, theremin-style volume
- Setup: VCA switch to Env position, Env Amt full, all ADSR sliders up

**Internal calibration trimmers:**

| Trimmer | Board | Function |
|---------|-------|----------|
| T1 | Rear | Pitch CV gain |
| T2 | Rear | Pitch CV offset |
| T5 | Rear | Saw offset (affects PW range, triangle shape) |
| T6 | Rear | VCO offset |
| T7 | Rear | Saw amplitude (affects sub/5th range, triangle shape) |
| T8 | Rear | VCO slope |
| T2 | Front | Filter resonance range |
| T3 | Front | Filter cutoff range |

**Linear FM input:**
- Connect jack via 100kΩ resistor to inverting input of U17(b) opamp
- Adds FM capability to VCO

### 1C. Touch/Body Contact Modifications

**Touch control circuit (pitch):**
```
+5V ──[R_fixed 100kΩ]──┬── to Pitch CV input
                        │
                  [R_skin (touch plates)]
                        │
                       GND
```
- Dry touch (~1MΩ) yields ~4.5V
- Firm moist touch (~100kΩ) yields ~2.5V
- Use TL072 non-inverting amplifier with offset to scale to 0–5V
- Always include 100kΩ–1MΩ pull-down for untouched state

**Touch plate construction:**
- Brass thumbtacks or bolts (classic circuit-bending)
- Copper-clad PCB pads with ENIG gold finish (best reliability)
- Minimum spacing: 3–5mm between two-contact plates, ≥10mm between separate touch points
- Use shielded cable from plates to circuit board

**Enable/disable switching:**
- CD4066B quad bilateral analog switch
- On-resistance ~5Ω, operates 3–18V
- 10kΩ pull-down on each control pin for defined OFF state
- For click-free switching: 47kΩ + 10µF RC network on control pin

**Circuit bending safety:**
- Only bend battery-powered devices
- Safe points: data bus lines, clock divider outputs, downstream of CPU
- Never touch: CPU power pins, OS ROM chips, crystal oscillator pins, write-enable pins
- Always install momentary reset button
- Use series limiting resistors (start high, decrease until effect)

### 1D. Test Points and Signal Taps

**Raw VCO waveform test points (rear PCB):**

| Test Point | Signal | Notes |
|-----------|--------|-------|
| TP93 | Square wave | Raw, pre-PWM shaping |
| TP94 | Sawtooth | Raw; phase inverted relative to main output |
| TP102 | Sub oscillator | Sub-octave output |
| TP124 | Triangle | Raw, pre-metalizer |

**Shaped waveform outputs (front PCB):**

| Test Point | Signal | Notes |
|-----------|--------|-------|
| TP109 | Metalizer output | Folded triangle; tap via 1kΩ series resistor |
| TP119 | Ultrasaw output | Phase-shifted saw ensemble effect |
| TP122 | PWM output | Pulse-width modulated square |

**Power supply test points:**
- TP70 (+12V), TP71 (-12V), TP72 (GND)
- Use to power add-on boards

**CRITICAL WARNING:**
- Wiring test points directly to output jacks causes loading and signal degradation
- A buffered output board using op-amp voltage followers is ESSENTIAL
- Always use 1kΩ series resistors when tapping test points

---

## Area 2: DSO130 Oscilloscope Integration

### 2A. Specifications

- MCU: STM32F103C8
- ADC: 12-bit, up to 1 MSPS, 1024-point record length
- Analog front end: TL084 quad JFET op-amp + ICL7660 negative voltage generator
- Input bandwidth: 0–200 kHz
- Maximum input: 50 Vpk with protection
- Input impedance: ~1 MΩ on higher sensitivity ranges
- Power: 9V DC at ~120–130 mA
- Display: 2.4" TFT (320×240, ILI9341 controller)

### 2B. Modifications for Synth Use

**Input protection for ±12V Eurorack:**
1. 1kΩ series resistor (½W) — limits fault current to 12mA
2. BAT54S dual Schottky clamp — turns on at ~380mV
3. Optional SMBJ5.0A TVS diode for transient spikes

**Input scaling circuit:**
- TL072 inverting amplifier
- Maps ±10V to ADC's 0–3.3V range with 1.65V offset
- Input through 100kΩ to summing junction
- 47kΩ to +1.65V bias
- 47kΩ feedback resistor

**Firmware alternatives:**
- DLO-138: Dual analog + dual digital channels, serial data output
- DSO303 upgrade: Replace MCU with STM32F303CB + AD8054 op-amp for 24 MSPS effective

### 2C. Signal Multiplexing

**CD4051B 8:1 analog multiplexer:**
- 125Ω on-resistance at VDD=15V
- 0.2pF feedthrough capacitance
- Break-before-make switching
- 3–20V supply range

**For bipolar Eurorack signals:**
- Use dual supply: VDD=+5V, VSS=0V, VEE=−12V
- Control pins (A, B, C) reference VSS
- 3.3V Pico GPIO works directly with 74HC4051 variant

**Buffer requirements:**
- Buffer each mux input with TL074 voltage follower
- Buffer output with TL072 before feeding DSO130
- 1kΩ series resistors on each input for isolation
- 0.1µF bypass caps on all power pins
- Tie unused channels to ground through 10kΩ resistors

---

## Area 3: Joyo JF-33 Analog Delay Integration

### 3A. Circuit Analysis

**Despite "Analog" name, uses PT2399 digital delay chip:**
- Sigma-delta modulation with 44Kbit internal RAM
- Supporting ICs: SA571D compander (NE571-type), RC4558 dual op-amp
- Power: ~40–60mA from 9V DC
- PT2399 runs internally on 5V via on-board regulator
- Safe input level: ~0.5–1Vrms (1.4–2.8Vpp)
- True bypass via 3PDT footswitch

### 3B. CV Control of Delay Parameters

**Delay time (Pin 6):**
- Pin 6 holds nominal 2.5V
- External resistor to ground controls VCO frequency
- Formula: Pin 6 current (mA) = 28.65 / (Delay_ms − 29.70)
- Range: 50µA (600ms) to 5.4mA (35ms)

**CV control methods:**

1. **NPN current sink:**
   - Op-amp drives 2N3904 transistor as current sink on pin 6
   - Include 1N4148 protection diode (cathode to pin 6)
   - Limit max current to 3mA
   - WARNING: Can destroy PT2399 without current limiting

2. **Vactrol (LED+LDR):**
   - Replace timing resistor with vactrol's LDR
   - Complete electrical isolation
   - Slow response (~5ms attack, 50ms+ release)
   - Only suitable for slower modulation

3. **JFET voltage-controlled resistor:**
   - 2N5457 or 2N5458 on pin 6
   - Faster than vactrol, simpler than current sink
   - Limited resistance range

**CRITICAL: Anti-latch-up circuit:**
- If pin 6 resistance drops below 2kΩ during power-on, PT2399 latches up PERMANENTLY
- Use BC337 transistor with 100kΩ + 1µF RC network (~1s time constant)
- Keep pin 6 high-impedance during startup, then release

**Feedback CV control:**
- SSI2164 quad VCA for professional solution
- Control law: −33mV/dB (exponential)
- Use one channel for feedback, one for wet/dry mix

### 3C. Eurorack Level Matching

**Input attenuation (~20dB):**
- Resistive divider: 100kΩ + 10kΩ (~10:1)

**Output amplification (~20dB):**
- TL072 non-inverting amplifier
- Gain ~11 (100kΩ feedback, 10kΩ to ground)
- AC-couple with 1µF to remove DC offset

**Power:**
- JF-33's internal 78L05 accepts up to +35V input
- Feed +12V directly from Eurorack rail
- Verify all electrolytic caps rated ≥16V

### 3D. Touch/Glitch Modifications

**PT2399 bend points (pins 6, 7, 8):**
- Pin 6: Clock frequency for pitch-shifting/time-stretching
- Pin 7: Unpredictable glitchy artifacts when loaded
- Pin 8: Warble and spatial effects
- 1MΩ resistor between pin 6 and pin 8 creates gentle warble

**Havoc self-oscillation switch:**
- Momentary SPST shorting across feedback pot
- For Eurorack: Replace with 2N7000 MOSFET or CD4066 controlled by gate input

**Safety:**
- Never apply voltage >5.5V directly to any PT2399 pin
- Never feed Eurorack-level signals (10Vpp) directly in
- Green LED from pin 7 (anode) to ground acts as soft input limiter at ~2V

---

## Area 4: Eurorack Expander Utility Circuits

### 4A. Core Utility Circuits

**White/pink noise generator:**
- Reverse-biased 2N3904 base-emitter junction in avalanche breakdown
- Cut off collector lead to prevent EMI antenna effect
- Bias through two 470kΩ resistors in series from +12V
- Amplify with TL074 inverting stage at gain ~46–100×
- Pink noise filter (National Semiconductors "Audio Handbook"):
  - 12kΩ+47nF, 6.8kΩ+100nF, 3.9kΩ+220nF, 2.2kΩ+470nF, 1kΩ+1µF
  - Requires makeup gain of 10–20×

**Triangle/square LFO:**
- TL072-based integrator + Schmitt trigger
- Timing cap 1µF with 1M linear rate pot gives ~0.04–40 Hz range
- Schmitt trigger uses 100kΩ divider resistors (thresholds at ±Vsat/2)
- Triangle output ~10Vpp (Eurorack compatible)
- Square output needs scaling through 1.8kΩ voltage divider to ±5V

**Clock divider (CD4024):**
- 7-stage binary ripple counter (/2 through /128)
- Clocked on falling edge (pin 1), reset on active-HIGH (pin 2)
- Power from regulated +5V (78L05 from +12V rail)
- Input conditioning via TL072 comparator with +110mV threshold
- Voltage divide to 5V through 120kΩ + 100kΩ
- Each output gets 1kΩ series resistor + LED indicator

**Sample and hold:**
- LF398 dedicated S&H IC (better than CD4066 approach)
- Hold capacitor: 1nF polystyrene (low leakage critical — never electrolytics)
- Output buffer: JFET op-amp (TL07x) — pA-range input bias minimizes droop (~3mV/s)
- Clock conditioning via CD4093 Schmitt trigger NAND gate

**Slew limiter:**
- Two diodes (1N4148) in anti-parallel
- Separate 1M log pots for independent rise/fall control
- Timing cap 1µF for up to 1s slew
- Use TL062 (not TL072 — misbehaves at voltage extremes)
- 220Ω minimum resistance in series with pots

**Attenuverter:**
- Single op-amp (TL072/TL074)
- Matched 100kΩ resistors (R1 = R2 = Rf)
- 100K linear pot
- Fully CW = +1 gain; center = 0V; fully CCW = −1 gain

**Buffered multiple:**
- TL074 quad op-amp provides 4 unity-gain followers
- 1kΩ output resistors inside feedback loop
- Default TL074 offset (~3mV max) = ~3.6 cents pitch error
- For critical V/Oct: use TLE2074 (~0.1mV offset)

**Manual gate button:**
- Momentary SPST switch
- 10kΩ pull-up to +12V, 10kΩ pull-down to ground
- Produces ~5V gate
- LED with 1kΩ current-limiting resistor
- Follow with CD40106 Schmitt trigger for clean edges

### 4B. CV Input Conditioning and Vactrols

**CV input protection:**
- 1kΩ–10kΩ series resistor on every input jack
- BAT85 Schottky diodes clamping to ±12V rails

**Vactrol construction:**
- 5mm red LED (lowest Vf ~1.5V, best LDR response)
- PGM5539 or GL5528 CdS photoresistor
- Slide face-to-face into 6mm heat-shrink tubing, heat-seal
- Wrap in black electrical tape for light blocking
- Response: ~1–5ms ON, ~5–50ms+ OFF
- Note: CdS is RoHS-restricted in EU but available for hobbyist use

### 4C. Panel Layout

**Eurorack dimensions:**
- 1 HP = 5.08mm
- Panel height: 128.5mm
- Mounting hole spacing: 122.5mm center-to-center

**Component spacing:**
- Thonkiconn PJ398SM jacks: minimum 12.7mm, comfortable at 15–16mm
- 9mm pots: minimum 15mm, Doepfer standard 20mm vertical

**Panel fabrication:**
- FR4 PCB panels from JLCPCB/PCBWay at ~$2–5 each
- Black solder mask with white silkscreen is standard
- For DSO130: Cut rectangular opening, mount display PCB behind with M3 standoffs

---

## Area 5: Power Isolation and Signal Protection

### 5A. Separate Power, Shared Signal Ground

**MicroBrute power:**
- 12V DC, 1A external
- Internal: ±12V, +5V, +3.3V
- −12V rail typically limited to ~100mA
- DO NOT draw additional current from internal rails for expander

**Architecture:**
- Completely separate power supplies
- MicroBrute from its own 12V adapter
- Eurorack expander from Eurorack bus
- Only signal ground connects through DB-9

**Expander power entry protection:**
- 1N5817 Schottky diodes (series, reverse polarity)
- Bourns MF-R050 polyfuses (resettable overcurrent)
- Murata BLM21PG221SN1 ferrite beads (RFI filtering)
- 47µF + 100nF decoupling per rail
- Connect grounds at one point only (star grounding via dedicated DB-9 pin)

### 5B. Signal Protection

**ESD protection at DB-9:**
- SP0504BAHTG 4-channel TVS arrays (5V standoff, 30pF capacitance)
- Place within 2–3mm of connector pads
- For lower capacitance on audio: PESD5V0S1BL (<1pF per line)

**Audio/CV over-voltage:**
- 1kΩ series resistor + BAT54S Schottky clamp to rails on every input
- Every I/O should survive indefinite short to ±12V

**Buffer op-amp selection:**
- TL074: Best single-chip solution for most buffering (4 channels, ~$0.40)
- NE5532: For DB-9 cable drive — stronger output (~38mA vs 10mA), lower noise

**Gate level conversion:**
- 5V→3.3V: SN74LVC1G17 single Schmitt trigger (inputs tolerate 5V at 3.3V supply)
- 3.3V→5V: 74HCT14 at 5V supply (HCT thresholds ~1.4V recognize 3.3V as HIGH)

---

## Area 6: Raspberry Pi Pico H Integration

### 6A. OLED Display and Menu System

**Use 1.3" SH1106 SPI OLED:**
- SPI runs 10–40 MHz on Pico
- Full 128×64 frame refresh: ~1–2ms (vs ~20ms for I2C)
- SH1106 supports RAM read-back for cursor highlighting

**SPI wiring:**
- GP18→SCK, GP19→MOSI, GP16→CS, GP17→DC, GP20→RST, 3V3→VCC

**Rotary encoder:**
- Use `micropython-rotary` by Mike Teachman (interrupt-driven)
- Hardware debounce: 10kΩ + 100nF RC filter on each encoder pin

**Menu structure:**
- 4–5 visible items per screen (12–16px per line)
- Scroll indicator, cursor via `>` prefix or inverted bar
- Menu stack for back-navigation
- Encoder rotate = up/down, push = select/enter, long-press = back

### 6B. Clock Generation and Detection

**PIO-based clock generation:**
- PIO runs independently at up to 125MHz
- Unaffected by interrupts or CPU load
- At 1MHz PIO frequency (1µs resolution), error at 300 BPM is 0.0005%
- Period(µs) = 60,000,000 / BPM
- Gate width typically 5–10ms

**Output level shifting:**
- Pico GPIO outputs 3.3V
- For 5V Eurorack gates: 74AHCT125 quad buffer
- For 10V gates: TL072 non-inverting amplifier at gain ~3

**External clock detection:**
- GPIO interrupt on rising edge measures inter-edge period
- Rolling median filter (8 samples) rejecting outliers >2× or <0.5× current average
- Input conditioning: voltage divider + 74HC14 Schmitt trigger

**Tap tempo:**
- Rolling window of 8 taps with 2-second timeout reset
- Hardware debounce: 10kΩ + 100nF
- 50ms software debounce minimum between taps

### 6C. Communication with MicroBrute's LPC2361

**SysEx protocol (fully reverse-engineered by Jakub Matraszek):**
- Arturia manufacturer ID: 0x00 0x20 0x6B
- Device ID: 0x05
- Operations: Identity request/response, parameter read, parameter set

**Set State command format:**
```
F0 00 20 6B 05 01 [counter] 01 [param_code] [value] F7
```

**14 controllable parameters:**
- Note priority, velocity response, play mode, sequencer retrigger
- Step size, LFO key retrig, envelope legato, gate length
- Sync mode, bend range, MIDI channels

**Hardware:**
- LPC2361 operates at 3.3V — directly compatible with Pico GPIO
- MIDI at 31250 baud over UART1 (GP4 TX, GP5 RX)
- Send SysEx to MicroBrute's standard MIDI IN — no hardware modification needed

**Recommended GPIO allocation:**

| Function | GPIO | Interface |
|----------|------|-----------|
| OLED (CS, DC, SCK, MOSI, RST) | GP16-20 | SPI0 |
| Rotary encoder (CLK, DT, SW) | GP14, GP15, GP13 | IRQ |
| MIDI OUT/IN | GP4 (TX), GP5 (RX) | UART1 |
| Clock output | GP22 | PIO SM0 |
| Clock input | GP21 | IRQ/PIO |
| Tap tempo button | GP12 | IRQ |

---

## Area 7: LPC2361 Firmware Extraction

### 7A. Code Read Protection Levels

**CRP word at flash address 0x1FC:**

| Level | Magic Value | JTAG | ISP Read | ISP Write | Erase |
|-------|-----------|------|----------|-----------|-------|
| CRP1 | 0x12345678 | Disabled | Disabled | Partial | Full chip |
| CRP2 | 0x87654321 | Disabled | Disabled | Disabled | All sectors only |
| CRP3 | 0x43218765 | Disabled | Disabled | Disabled | ISP entry disabled |

**CRP3 is effectively permanent** — NXP cannot restore CRP3-locked parts.

**IAP (In-Application Programming) has NO restrictions under ANY CRP level.**

**To determine active CRP level:**
- Connect to ISP via UART0 (pull P2.10 low during reset, send "?" for auto-baud)
- Test progressively restricted ISP commands

### 7B. Voltage Glitching Bypass

**Principle:**
- Brief voltage drop (~100–110ns) during bootloader's CRP check
- Corrupts read value, doesn't match any magic value
- Defaults to unlocked state

**Tools:**
- Pico Glitcher (~$15): Raspberry Pi Pico + findus Python library
- ChipWhisperer-Lite (~$300): Professional platform with Tutorial A9
- ChipJabber Unplugged (~$50): Analog glitcher kit

**Equipment needed:**
- Glitching device
- USB-to-UART adapter (3.3V)
- Oscilloscope
- Physical access to Vcc, UART0, RESET, and P2.10 pins

### 7C. Firmware Capture via SysEx

**Arturia delivers updates via MIDI Control Center over USB-MIDI:**
- Latest firmware: v1.0.4.114 (144.73 KB as .mbf file)
- File size exceeds 64 KB flash — suggests headers, checksums, MIDI 7-bit encoding, likely encryption

**Capture tools:**
- Wireshark + USBPcap
- MIDI-OX (Windows)
- SysEx Librarian (Mac)
- amidi (Linux)

**Analysis tools:**
- Ghidra (free, excellent ARM support)
- IDA Pro
- Flash maps to 0x00000000, SRAM to 0x40000000

---

## Area 8: DB-9 Interconnect Design

### 8A. Pin Assignment

| Pin | Signal | Direction |
|-----|--------|-----------|
| 1 | Audio Out (MicroBrute) | MB → Expander |
| 2 | CV Pitch (1V/Oct) | MB → Expander |
| 3 | Gate Out | MB → Expander |
| 4 | LFO Out | MB → Expander |
| **5** | **Signal Ground** | **Shared** |
| 6 | Audio In (to MicroBrute) | Expander → MB |
| 7 | CV In (Filter/Mod) | Expander → MB |
| 8 | Gate/Trigger In | Expander → MB |
| 9 | Envelope Out / Aux | MB → Expander |
| Shell | Chassis/Shield Ground | Both ends |

**No power rails cross the DB-9 — only signal ground.**

### 8B. Cable Construction

- Use Amphenol double-shielded cables (CS-DSPMDB09MF series)
- Keep cable length under 3 meters for unbalanced audio/CV
- Use gold-plated contacts for frequent mating cycles

**Hot-plug warning:**
- Never connect/disconnect while powered
- TVS arrays and series resistors at both ends mitigate risk

---

## Implementation Priority

### Phase 1 — Foundation:
1. MicroBrute sound mods (R76 mix boost, R28 VCA boost, square phase correction)
2. Buffered test point taps (TP93/94/102/124)
3. DB-9 connector installation with protection circuits
4. Expander power supply and protection

### Phase 2 — Core Expander:
5. Noise generator, LFO, clock divider, sample & hold
6. CD4051 signal multiplexer for oscilloscope
7. DSO130 Eurorack mounting with input protection
8. Basic Pico firmware (OLED menu, clock generation, MIDI SysEx bridge)

### Phase 3 — Delay Integration:
9. JF-33 removal from enclosure and Eurorack mounting
10. Level matching circuits
11. CV control of delay time (NPN current sink with anti-latch-up)
12. CV control of feedback (SSI2164 VCA)

### Phase 4 — Advanced:
13. Touch plate construction and CV circuits with CD4066 switching
14. Pico advanced firmware (clock detection, multiplication, tap tempo)
15. LPC2361 CRP level determination and potential glitching
16. Touch/glitch mods for PT2399 delay circuit

---

## Key References

### MicroBrute
- Maffez Pedrobrute: https://maffez.com/?page_id=2285
- Yusynth/Hackabrute: https://hackabrute.yusynth.net/MICROBRUTE/
- MKNielsen2000 Add-ons: https://github.com/MKNielsen2000/MicroBrute-Add-ons
- Matraszek SysEx RE: https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html
- MicroDude editor: https://github.com/dagargo/microdude

### DSO130/138
- DLO-138 firmware: https://github.com/ardyesp/DLO-138
- DSO-238 firmware: https://github.com/barty32/DSO-238

### PT2399 Delay
- ElectroSmash PT2399 Analysis: https://www.electrosmash.com/pt2399-analysis
- Ryan Williams VC-Echo: http://www.sdiy.org/destrukto/vc-echo.html

### Eurorack DIY
- N8 Synthesizers: https://www.n8synth.co.uk/diy-eurorack/
- Exploding Shed Eurorack Dimensions: https://www.exploding-shed.com/synth-diy-guides/standards-of-eurorack/

### Pico
- EuroPi: https://github.com/Allen-Synthesis/EuroPi
- micropython-rotary: https://github.com/miketeachman/micropython-rotary
- Pico OLED examples: https://github.com/raspberrypi/pico-micropython-examples

### LPC2361
- ChipWhisperer: https://github.com/newaetech/chipwhisperer
- lpc21isp: https://github.com/capiman/lpc21isp
