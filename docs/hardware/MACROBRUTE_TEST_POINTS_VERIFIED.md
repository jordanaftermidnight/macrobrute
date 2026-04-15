# MACROBRUTE — Verified Test Point Reference

Source: Yves Usson (Yusynth) official schematics, Maffez documentation,
ModWiggler community, PCB photo analysis (April 2026).

---

## Board Identification

| Physical Marking | Schematic Name | Revision | Function |
|------------------|----------------|----------|----------|
| CU17001 "MicroBrute 1 Analog Board" | Analog.SchDoc (13 sheets) | VERSION B2 | VCF, VCA, envelope, mixer, glide, controls |
| CU17002 "MicroBrute 1 Rear Board" | RearBoard (20+ sheets) | VERSION B3 | VCO, metalizer, sub osc, LPC2361, DAC, MIDI, USB, power |

---

## Power Rails (Front / Analog Board)

Power enters the front board via **P4**, a 6-pin JST connector fed from the
rear board. L1 (10uH) + C44 (47nF) filter +3V3ARM into +3V3ANA.

| TP | Signal | Location | Notes |
|----|--------|----------|-------|
| **TP69** | Power area | Front board, near P4 | **UNVERIFIED — Use Caution** Likely +3V3ARM or +3V3ANA |
| **TP70** | **+12V (A+12)** | Front board, near P4 | Confirmed from schematic + photo |
| **TP71** | **-12V (A-12)** | Front board, near P4 | Confirmed from schematic + photo |
| **TP72** | **GND** | Front board, near P4 | Confirmed from schematic + photo |
| **TP73** | Power area | Front board, near P4 | **UNVERIFIED — Use Caution** Likely second GND or +5V |
| TP56 | +5VNUM | Rear board | Digital rail (per original doc) |

### P4 Connector (6-pin JST, white — inter-board power)

| Pin | Signal |
|-----|--------|
| 1-2 | A+12 (+12V) |
| 3-4 | A-12 (-12V) |
| 5 | +3V3ARM |
| 6 | GND |

---

## Steiner-Parker VCF (Front Board — FilterSteiner.SchDoc)

| TP | Signal | Function |
|----|--------|----------|
| **TP15** | Filter_HP_in | High-pass input from mode switch (COM1/TS3A pin A1) |
| **TP16** | Filter_BP_in | Band-pass input from mode switch (pin B1) |
| **TP17** | FilterSelectorAudioIn | Audio entering filter (near R37, 10K) |
| **TP18** | Filter_LP_in | Low-pass input from mode switch (pin C1) |
| **TP19** | **Filter Out** | VCF output — U9A (TL062CDT) output, via C14 (47pF) |
| **TP20** | Diode ladder output | D6-D17 ladder end, to U9A pin 2 |
| TP21 | Diode ladder base | Near C16/C22 (filter core) |
| **TP22** | Resonance tuning | Resonance circuit, near R52 (27K), RP13A/B |
| **TP23** | U8B output | Filter control/tuning section |
| **TP24** | CV summing node | Where Env_CV + LFO_CV + ExtCV + ModWheel + Aftertouch + Pitch_CV sum (R53-R66 area) |
| **TP25** | Cutoff pot tap | RP14A/B (Cutoff, 50K Lin) connection |
| **TP26** | Misc Cutoff Input | Via R67 (220K) — **CV injection point for expander** |
| **TP27** | Misc Cutoff Input | Via R68 (220K) — spare CV input |
| **TP28** | Misc Cutoff Input | Via R71 (220K) — spare CV input |
| **TP29** | Tracking pot tap | RP15A (Tracking, 50K Lin), R72 (300K) |

---

## VCA (Front Board — VCA.SchDoc)

Uses U7A-D (TL074CD) + Q3A/Q3B (BC847BS matched pair) + Q4 (BC847C).

| TP | Signal | Function |
|----|--------|----------|
| **TP9** | VCA output area | Near C7 (10pF), R17 (47K), R21 (47K) |
| **TP10** | **CV1** | VCA CV input A (via R25, 100K) |
| **TP11** | **CV2** | VCA CV input B (via R30, 100K) |
| **TP12** | Misc Amplitude Input | Extra VCA CV (via R33, 100K) |
| **TP13** | Misc Amplitude Input | Extra VCA CV (via R34, 100K) |
| **TP14** | Misc Amplitude Input | Extra VCA CV (via R35, 100K) |

---

## Waveform Mixer (Front Board — Mixer.SchDoc)

Summing amplifier U6A (TL062CDT). R76 (40.2K) feedback. "Virtual Zero" summing node.

| TP | Signal | Function |
|----|--------|----------|
| **TP30** | **AudioOut (TP30_MIXER_OUT)** | Waveform mixer output, pre-filter. Label says "Filter Out" on schematic but signal goes TO filter. |
| **TP31** | ExtAudio_in | External audio input (pot on rear board) |

---

## Envelope (Front Board — Envelope1.SchDoc)

ICM7555CBA timer + Q1 (MMBF170 MOSFET). Attack/Decay/Sustain/Release
via SP1-SP4 slide pots (10K Log, except Sustain = 10K Lin).

| TP | Signal | Function |
|----|--------|----------|
| **TP5** | **Envelope 2 Out** | Envelope output — U1A (TL062CDT) out |

---

## Gate & Trigger (Front Board — GateToTrig.SchDoc)

Gate from MCU → differentiator → trigger pulse for envelope.

| TP | Signal | Function |
|----|--------|----------|
| **TP56** | **Gate In** | Gate signal entering front board from LPC2361 |
| **TP57** | Env_Trig | Trigger pulse output to envelope (Q7 BC847C collector) |

---

## Glide / Portamento (Front Board — Glide.SchDoc)

U5A/U5B (TL062CDT). RP16A (200K Log) = speed pot. C38 (4.7uF Ceramic) = timing cap.

| TP | Signal | Function |
|----|--------|----------|
| **TP53** | **Glide_out** | Portamento output — U5B (TL062CDT) out, goes to VCO |
| **TP54** | U5A output | Intermediate glide signal |
| **TP55** | KeyFollow_CV in | Pitch CV entering glide circuit (U5A pin 2) |

---

## Critical Waveform Outputs (Rear Board)

All outputs ~10Vpp. **Buffering required** — direct wiring causes oscillator loading.

| TP | Signal | Location | Notes |
|----|--------|----------|-------|
| **TP93** | Square (raw) | Near sub divider | Hardest to solder — SMT resistor nearby |
| **TP94** | Sawtooth (raw) | Sub/5th section | Phase inverted vs line out |
| **TP102** | Sub oscillator | Sub/5th section | Affected by Sub>Fifth knob |
| **TP124** | Triangle (raw) | SawToTriangle | Quieter than other waveforms |

### Post-Waveshaper Outputs (Rear Board)

| TP | Signal | Notes |
|----|--------|-------|
| TP109 | Metalizer raw (pre-mix) | Before level pot |
| TP110 | Metalizer final (post-mix) | After level pot |
| TP119 | Sawtooth 10Vpp | Post-SawAnimator |
| TP122 | Pulse/Square 10Vpp | Post-PWM control |

---

## Gate Section (Rear Board)

| TP | Signal |
|----|--------|
| TP22 | External gate input |
| TP27 | Gate to microcontroller |
| TP82 | Internal gate bus |
| **TP83** | **Gate from microcontroller** (100k source Z — needs buffer) |
| TP84 | External gate output |

---

## DAC Section (Rear Board)

| TP | Signal |
|----|--------|
| TP34 | DAC Channel A output |
| TP37 | DAC Channel B output |
| TP38 | DAC control (LDAC/RDY) |
| TP39 | DAC Channel C output |
| TP40 | DAC Channel D output |
| TP41 | DAC VREF |
| TP42 | DAC_ChannelD (CV output) |

---

## CV Shaping (Rear Board)

| TP | Signal |
|----|--------|
| TP43 | CV_KeyFollow |
| TP44 | CV_ModWheel |
| TP45 | LFO_Fine tuning |
| TP46 | LFO_Coarse tuning |

---

## Audio I/O (Rear Board)

| TP | Signal |
|----|--------|
| TP47 | External audio input (post-opamp) |
| TP48 | Headphones output |
| TP49 | Master output |

---

## Sub Oscillator Section (Rear Board)

| TP | Signal |
|----|--------|
| TP90 | VCO block interconnect |
| TP91 | Sub oscillator divider output |
| TP92 | Sub oscillator section |
| TP95 | Buffered triangle wave |
| TP96 | Triangle input |
| TP97 | /Sub (inverted sub, CD4027 Q) |
| TP98-TP100 | Sub section reference points |
| TP101 | 5th output signal |

---

## Metalizer Section (Rear Board)

| TP | Signal |
|----|--------|
| TP103-TP108 | Metalizer folding stages |
| TP109 | Metalizer raw output (pre-mix) |
| TP110 | Metalizer final output (post-mix) |

---

## Saw Animator Section (Rear Board)

| TP | Signal |
|----|--------|
| TP111-TP118 | Saw Animator circuit points |
| TP113, TP117 | Internal sine wave 500mVpp |
| TP119 | Sawtooth 10Vpp output |

---

## Pulse Width Section (Rear Board)

| TP | Signal |
|----|--------|
| TP120 | Pulse generation stage |
| TP121 | Pulse width control wiper |
| TP122 | Pulse/Square 10Vpp centered |
| TP123 | Pulse 20Vpp centered (full-swing) |

---

## Triangle Converter (Rear Board)

| TP | Signal |
|----|--------|
| TP124 | Triangle 10Vpp centered |
| TP125 | Raw saw input to triangle converter |
| TP141 | 5V precision reference (+-0.05V) |

---

## LFO Section (Rear Board)

| TP | Signal |
|----|--------|
| TP21 | LFO PWM output (near Bourns 3006P trimmers, T6 area) |
| TP85 | LFO waveform CV |

---

## Calibration Trimmers (Rear Board)

Located near T6, left side of rear board. Visible in photos as blue upright
rectangular components.

| Component | Type | Value | Function |
|-----------|------|-------|----------|
| Bourns 3006P | Multi-turn trimmer | 22K (marking: 223) | VCO fine tuning / tracking |
| Bourns 3006P | Multi-turn trimmer | 50K (marking: 503) | VCO coarse calibration |
| Tan/olive trimmer | Unconfirmed | TBD | Third calibration point (type uncertain from photos) |

R309 (1M) is in the surrounding resistor cluster (R308, R313, R315, R319,
R322, R324, R327, R328). This is the target area for touch bend #1
(Pitch Shimmer).

---

## Brute Factor / Output (Front Board — BruteFactor.SchDoc)

Feedback loop: Audio_Out → RP8A (25K Lin) → "Feedback to Mixer" → mixer summing node.
U1A (TL062CDT) = feedback/output stage. U1B = spare (unused, decoupled only).

| TP | Signal | Function |
|----|--------|----------|
| **TP1** | Audio_In | Signal entering Brute Factor stage |
| **TP2** | Audio_Out | Post-Brute Factor, pre-master volume |
| **TP3** | VCA_Master_out | After master volume pot (RP6A/B, 25K Log) |
| **TP4** | BruteFactor feedback | Feedback signal tap (RP8A, 25K Lin) |

---

## Envelope Destination (Front Board — EnvDest.SchDoc)

Envelope routing/scaling. U3B (TL062CDT) = inverter. R10/R13 = **NotMounted**
(unpopulated factory pads). D4/D5 (TS4148RY) = diode limiter on filter path.

| TP | Signal | Function |
|----|--------|----------|
| **TP6** | **Env1** | Raw envelope signal, pre-scaling |
| **TP7** | **Env × FilterAmt** | Envelope scaled by RP11A (Filter Env Amt, 100K Lin) → FilterMod |
| **TP8** | **Env × Amt** | General envelope amount → EnvAmtOut (via RP12A, 10K Lin) |

---

## Mod Matrix Patchbay (Front Board — PatchBay.SchDoc)

8 normalled switching jacks. When nothing plugged in, "Default" signal flows.
Inserting cable breaks normal and substitutes external signal.

| Jack | Label | Normal (Default) | Mod Signal |
|------|-------|------------------|------------|
| J7 | Sub_In | SubDefault | SubMod |
| J8 | Pitch_In | PitchDefault | PitchMod |
| J10 | SawAnim_In | SawAnimDefault | SawAnimMod |
| J11 | Filter_In | FilterDefault | FilterMod |
| J14 | Metal_In | MetalDefault | MetalMod |
| J13 | PW_In | PWDefault | PWMod |
| J9 | LFO_out | LFOOutputDefault | LFOOutputJack |
| J12 | Env_out | EnvOutputDefault | EnvOutputJack |

---

## Unidentified (Need Remaining Schematic Sheets or Probing)

Visible on front board back but not in the 10 sheets reviewed so far.
Likely in Connectors, DigitalLand, VCO-Pots, or Switches/Pots sheets.

| TP | Photo Location | Likely Section |
|----|----------------|----------------|
| TP63 | Near L1 inductor | Filtered +3V3ANA rail or power monitor |
| TP65 | Center-lower area | DigitalLand or Connectors |
| TP66 | Center-lower area | DigitalLand or Connectors |
| TP67 | Center-lower area | DigitalLand or Connectors |
| TP68 | Center-lower area | DigitalLand or Connectors |

---

## JTAG Interface (Rear Board)

| Detail | Value |
|--------|-------|
| Label | **P1_JTAG** |
| Type | **20-pin shrouded IDC** (2x10, standard ARM JTAG) |
| Location | Immediately left of LPC2361 QFP-100 |
| State | Populated with pins |

Standard 20-pin ARM JTAG pinout:
- Odd pins: VTref, nTRST, TDI, TMS, TCK, RTCK, TDO, RESET, DBGRQ, DBGACK
- Even pins: All GND (except pin 2 = nSRST)

Note: UART0 pins (P0.2/TXD0, P0.3/RXD0) are NOT on the JTAG header —
they are separate pads near the QFP.

---

## KEYBOARD Connector (Rear Board Back)

White FPC connector labeled "KEYBOARD" on rear board solder side.
Adjacent test point pads for keyboard scanning signals (TP5-TP20 range
visible, associated with DAC and key scanning).

---

## References

- https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- https://maffez.com/?page_id=2285
- https://modwiggler.com/forum/viewtopic.php?t=152071
- https://github.com/MKNielsen2000/MicroBrute-Add-ons
- PCB photos: IMG_6986-7025 (April 2026 teardown)
