# MACROBRUTE Mod Catalog (v2 — Phase 1 + Phase 2 additions)

**Status:** 2026-04-27. Authoritative per-mod documentation for the
synth-enhancement and circuit-bent additions agreed during the Phase E
review. Each entry is self-contained: parts list, wiring, panel position,
safety notes, and a pointer to the schematic figure (if one exists).

This catalog complements the existing mod set (B1–B6 panel jacks/toggles,
T1–T8 touch bolts, I1–I9 internal mods on the breakout PCB). It does **not**
replace `MACROBRUTE_MOD_SELECTION.md` — that file is the high-level
curation/triage doc; this is the build-detail counterpart.

| Phase | # mods | Theme |
|-------|-------|-------|
| Phase 1 (immediate, breakout PCB-side) | 1 | Restore tonal balance |
| Phase 2 — synth-nature enhancements | 5 | Expand the MicroBrute's voice |
| Phase 2 — circuit-bent additions | 8 | Glitch / break / re-route |

> **Safety convention:** every mod that injects current into a node uses a
> series resistor sized so a hard short-to-rail caps current at safe
> levels (≤1 mA into LPC2361 pins, ≤10 mA into op-amp outputs). Where the
> mod taps a digital rail or DAC, the safety analysis is called out
> explicitly.

> **Badge legend:** each mod heading shows its current state and reversibility.
> [[VERIFIED]] built and tested · [[BUILT]] built but not fully tested ·
> [[UNTESTED]] designed, not yet built · [[DRAFT]] design in progress.
> [[REVERSIBLE]] no PCB cuts — undo by unsoldering · [[DESTRUCTIVE]] involves
> a trace cut or panel hole, plan accordingly.

---

## Phase 1 — Restore tonal balance

### M01. Triangle output gain ×2 [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M01 |
| Effect | Restores level parity between triangle and saw/square. Stock TP124 is ~2–3 dB quieter than the other waveform taps. |
| Affects | Triangle output buffer in the breakout PCB (TL074 section D, see `schematics/wiring_output_buffer.svg`). |
| Parts | 1× 33 kΩ resistor (replaces existing 16 kΩ feedback R) |
| PCB cuts | None — feedback resistor swap on the breakout |
| Panel work | None |
| Schematic | `schematics/mod_m01_triangle_gain.svg` |
| Safety | Trivial — single passive change |

**Wiring**: in the TL074 D non-inverting follower stage, replace the
feedback resistor (Rf in the unity-gain config — 16 kΩ in the original
buffer) with a 33 kΩ + 16 kΩ ground leg to make the stage 2× gain
(`A = 1 + Rf/Rg`). Net result: TP124 → DB-9 A pin matches saw/square level.

---

## Phase 2 — Synth-nature enhancements

### M02. Active soft sync [[UNTESTED]] [[DESTRUCTIVE]]

| Field | Value |
|---|---|
| Mod ID | M02 |
| Effect | Working soft sync — the stock MicroBrute soft-sync circuit has a documented design bug (missing capacitor + non-functional comparator), this replaces it with an active LM393 comparator that produces clean phase-resync pulses. |
| Affects | VCO sync input. Adds a panel toggle to switch between hard sync (stock) and the new active soft sync. |
| Parts | LM393 comparator, 2× 100 kΩ, 1× 10 kΩ, 1× 100 nF, 1× 1N4148, 1× SPDT toggle |
| PCB cuts | 1 trace cut (sync input) |
| Panel work | 1× 6.2 mm hole for the SPDT toggle |
| Schematic | `schematics/mod_m02_soft_sync.svg` |
| Stripboard | `schematics/mod_m02_soft_sync_stripboard.svg` |
| Safety | LM393 is open-collector; 10 kΩ pull-up to +5V limits sink current |

**Wiring**: the stock sync input goes through the new SPDT toggle. Position
A = direct to VCO sync (stock hard-sync behaviour). Position B = via the
LM393 comparator network → produces a soft-sync edge that re-phases the
VCO without forcing it. The comparator threshold is set by a 100k/100k
divider biased mid-rail; hysteresis comes from the diode + 10 kΩ in the
feedback path.

### M03. Sine extraction + buffer [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M03 |
| Effect | Adds a clean sine output. Taps the triangle wave-shaper just past the diode-clipper stage, where the signal is approximately sinusoidal; buffered + attenuated to standard Eurorack 10 Vpp. |
| Affects | New panel jack on the MicroBrute (next to the existing waveform jacks). |
| Parts | 1× TL074 spare section (already on the breakout — the spare op-amp from I6), 2× 10 kΩ (input + feedback), 1× 1 µF (DC block), 1× 6 mm panel jack |
| PCB cuts | None — tap point is high-impedance |
| Panel work | 1× 6 mm hole for new jack |
| Schematic | `schematics/mod_m03_sine_extract.svg` |
| Safety | Taps a high-Z node; even a hard short to GND only loads the existing buffer |

**Tap point**: the diode-shaper output node feeding the existing triangle
buffer (called out in `pt_124_area` on the rear PCB). The shaper produces
a quasi-sine that reads visually as 'rounded triangle' on a scope. A
unity-gain TL074 buffer prevents loading the original signal path.

### M04. Metalizer CV depth (VCA) [[UNTESTED]] [[DESTRUCTIVE]]

| Field | Value |
|---|---|
| Mod ID | M04 |
| Effect | CV-controllable wavefolder intensity. Inserts an LM13700 OTA into the Metalizer feedback loop so a CV input modulates how much the wavefolded signal feeds back. Turns Metalizer from a knob-only static effect into a dynamic modulation source. |
| Affects | Metalizer feedback path. New panel CV jack + amount pot. |
| Parts | LM13700 (1 OTA section), 1× 100 kΩ CV input R, 1× 10 kΩ control R, 1× 100 kΩ panel pot, 1× 6 mm jack, 4× 0.1 µF decoupling |
| PCB cuts | 1 cut (break Metalizer feedback loop, insert VCA) |
| Panel work | 1× 6 mm jack + 1× 7 mm pot hole |
| Schematic | `schematics/mod_m04_metalizer_vca.svg` |
| Stripboard | `schematics/mod_m04_metalizer_vca_stripboard.svg` |
| Safety | LM13700 needs ±12V — already available on the breakout |

**Wiring**: cut the Metalizer feedback trace at the documented point in
`docs/architecture/MACROBRUTE_COMPLETE_EXPANSION_MAP.md`; re-route through
the OTA's signal input. CV (0–5 V from expander or panel jack) feeds the
OTA control current via a 100 kΩ resistor; CV at +5 V → full feedback,
CV at 0 V → muted. The amount pot manually offsets the CV bias.

### M05. Filter self-oscillation kill switch [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M05 |
| Effect | An SPST toggle that breaks the Steiner-Parker filter feedback loop. With the switch open, the filter cannot self-oscillate at high resonance settings — gives a clean percussive filter mode useful for plucks and gated tones. |
| Affects | Filter resonance feedback path. |
| Parts | 1× SPST toggle, 1× 10 kΩ resistor |
| PCB cuts | None — toggle is wired in series with existing feedback path via solder leads |
| Panel work | 1× 6.2 mm toggle hole |
| Schematic | `schematics/mod_m05_filter_selfosc_kill.svg` |
| Safety | Passive switch on a low-current node |

**Wiring**: lift one leg of the resonance feedback resistor; place the
SPST toggle in series. Closed = stock behaviour (resonance can self-osc).
Open = no feedback path → resonance peaks but doesn't oscillate.

### M06. PWM CV input [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M06 |
| Effect | Direct CV injection into the PWM summing node — gives external CV control over pulse width. Stock has a PWM knob but no CV input. |
| Affects | PWM summing node (R289 junction). |
| Parts | 1× 39 kΩ series resistor, 1× 6 mm jack |
| PCB cuts | None — direct injection |
| Panel work | 1× 6 mm jack hole |
| Schematic | `schematics/mod_m06_pwm_cv.svg` |
| Safety | 39 kΩ series limits current to ±0.13 mA at ±5 V CV — well below LPC2361 DAC node ratings |

**Wiring**: tap the PWM summing node (R289 area on the front board);
solder a 39 kΩ resistor in series with a new panel jack. CV at 0 V leaves
the PWM at its knob position; CV swings shift it.

---

## Phase 2 — Circuit-bent additions

### M07. Pitch CV starve toggle [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M07 |
| Effect | An SPDT toggle that introduces a current draw on the VCO pitch CV — pitch becomes unstable, drifty, glitchy. Iconic "broken synth" texture without actually breaking anything. |
| Affects | VCO pitch summing node. |
| Parts | 1× SPDT toggle, 1× 470 Ω resistor (current limit) |
| PCB cuts | None — toggle taps an existing node |
| Panel work | 1× 6.2 mm toggle hole |
| Schematic | `schematics/mod_m07_pitch_starve.svg` |
| Safety | 470 Ω + the LPC2361 DAC's internal series impedance keeps current well below 10 mA even on a hard pull |

**Wiring**: SPDT centre = pitch CV node. Position A = open (stock).
Position B = via 470 Ω → GND. The voltage drop on the pitch summing
network produces a slow oscillator drift that's musically interesting.

### M08. Sub-harmonic divider [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M08 |
| Effect | Generates a sub-octave of the square wave via a 74HC74 D-flip-flop. Mixes back into the audio path through a small pot. |
| Affects | Square output → /2 divider → mix. |
| Parts | 1× 74HC74 (dual flip-flop), 1× 10 kΩ mix pot, 1× SPDT enable, 4× 0.1 µF decoupling, 1× 1 µF AC coupling |
| PCB cuts | None — taps square output, sums into mixer pre-VCF |
| Panel work | 1× 7 mm pot + 1× 6.2 mm SPDT toggle |
| Schematic | `schematics/mod_m08_subharmonic.svg` |
| Stripboard | `schematics/mod_m08_subharmonic_stripboard.svg` |
| Safety | 74HC74 is +5V logic — runs from existing breakout +5V rail |

**Wiring**: square out → 1× Schmitt buffer (use spare CD40106 gate) →
74HC74 clock input → Q output → 10 kΩ pot → AC-coupled mixer summing
node. The sub adds a 1 octave-down square that grits up the bass — pair
with circuit bend T6 (gate feedback) for big metallic textures.

### M09. PWM self-modulation normalled jack [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M09 |
| Effect | A switching jack: with no plug, the saw output internally feeds the PWM CV input — produces metallic FM-ish PWM textures by default. Plugging a cable into the PWM CV jack (M06) breaks the loop. |
| Affects | PWM CV input (M06's jack); cooperative with M06. |
| Parts | 1× 6 mm switching (normalled) jack — replaces M06's plain jack, 1× 100 kΩ series R |
| PCB cuts | None |
| Panel work | None additional (re-uses the M06 jack hole) |
| Schematic | `schematics/mod_m09_pwm_selfmod.svg` |
| Safety | 100 kΩ series limits saw → PWM crossfeed |

**Wiring**: the switching jack's "normal" contact carries an internal
saw-tap (via 100 kΩ R). Tip is the M06 PWM CV input. Plug inserted →
breaks the saw → PWM internal connection, lets external CV take over.

### M10. Brute Factor "extreme" toggle [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M10 |
| Effect | SPDT bypasses the internal limiting resistor on the Brute Factor feedback path. Position B = stock. Position A = unlimited feedback — the Brute Factor can self-oscillate and explode. |
| Affects | Brute Factor feedback loop. |
| Parts | 1× SPDT toggle, 1× wire jumper across the limit R |
| PCB cuts | None — solder leads to existing R |
| Panel work | 1× 6.2 mm toggle hole |
| Schematic | `schematics/mod_m10_brute_extreme.svg` |
| Safety | **Output level can spike** when "extreme" is engaged. Panel-mark accordingly. |

**Wiring**: SPDT position A shorts the existing limit resistor, position B
leaves it in circuit. Use a 1 kΩ series R inline between the SPDT and the
feedback path to prevent dead-short transients during switching.

### M11. 9th touch bolt — envelope retrigger [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M11 |
| Effect | Adding a 9th brass M3 bolt to the existing touch-plate cluster. Touching it injects a brief gate pulse that retriggers the envelope. Body-controlled rhythmic glitch. |
| Affects | Envelope gate input. |
| Parts | 1× M3 brass bolt + nut, 1× 100 kΩ series R, 1× 1N4148 (anti-backflow), 1× 100 nF cap (debounce/short pulse) |
| PCB cuts | None — taps gate line |
| Panel work | 1× 6 mm hole for the brass bolt (consistent with the other 8 touch bolts) |
| Schematic | `schematics/mod_m11_touch_envretrig.svg` |
| Safety | 100 kΩ + diode keeps body capacitance from latching the gate high |

**Wiring**: brass bolt → 100 kΩ → 1N4148 → 100 nF → gate node. The cap
+ diode shape the touch into a short pulse rather than holding the gate
high indefinitely.

### M12. ARG — audio-rate gate input [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M12 |
| Effect | Patch an audio signal through an LM393 comparator → produces a clean gate at zero-crossings. Lets you trigger the envelope from a kick drum, vocal, anything. |
| Affects | New panel jack + threshold pot. Gate output goes to envelope retrigger or aux output. |
| Parts | LM393 comparator, 1× 100 kΩ threshold pot, 1× 10 kΩ pull-up, 1× 100 nF DC-block, 1× 6 mm input jack |
| PCB cuts | None |
| Panel work | 1× 6 mm jack + 1× 7 mm pot |
| Schematic | `schematics/mod_m12_arg.svg` |
| Stripboard | `schematics/mod_m12_arg_stripboard.svg` |
| Safety | LM393 is open-collector; pull-up to +5V |

**Wiring**: audio in → DC-block → LM393 +input. Threshold pot biases the
−input. Comparator output (with 10 kΩ pull-up) drives the gate node.
Hysteresis from the LM393's natural ~few-mV gives clean gate edges.

### M13. VCO sync to envelope (toggle) [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M13 |
| Effect | SPDT routes the envelope decay edge to the VCO sync input — produces "synced sweep" tones (oscillator phase locks to envelope events). Replicates a classic DIY mod by toggle rather than patch cables. |
| Affects | VCO sync. Cooperates with M02 (active soft sync) — when M02 is in soft mode, M13 produces softer phase nudges. |
| Parts | 1× SPDT toggle, 1× 10 kΩ + 1× 100 nF (edge-shaper) |
| PCB cuts | None |
| Panel work | 1× 6.2 mm toggle hole |
| Schematic | `schematics/mod_m13_vco_sync_env.svg` |
| Safety | Edge-shaper limits sync slew rate |

**Wiring**: SPDT centre = VCO sync. Position A = external sync jack
(stock). Position B = via 10k+100n high-pass from the envelope decay
node. Same modulation can be done with patch cables — this is the
quick-toggle version.

### M14. Safe VCO bias starve (NOT supply rail) [[UNTESTED]] [[REVERSIBLE]]

| Field | Value |
|---|---|
| Mod ID | M14 |
| Effect | A current-limited body contact that loads down the **VCO pitch bias node** (not the +12V supply rail). Produces oscillator detuning and breakup similar to a classic "supply starve" without putting the LPC2361 DAC at risk. |
| Affects | VCO pitch bias network only. |
| Parts | 1× M3 brass bolt + nut, 1× 22 kΩ series R, 1× 1N4148 (anti-current-back-flow) |
| PCB cuts | None — taps the high-Z bias node |
| Panel work | 1× 6 mm bolt hole (could double as a 10th touch bolt position, alongside M11) |
| Schematic | `schematics/mod_m14_vco_bias_starve.svg` |
| Safety | **Critical:** 22 kΩ + body resistance + diode = max ~0.5 mA pull on a +12V node. The pitch bias is HIGH-Z so even this tiny load shifts pitch noticeably. **Do not** tap the +12V rail directly — that's the unsafe variant we explicitly rejected. |

**Wiring**: tap the VCO pitch bias node (high-Z point in the temperature-
compensation network — `bias_tp` area). Brass bolt → 22 kΩ → 1N4148 → bias
node. Body contact pulls the bias slightly low, oscillator detunes
musically.

> **Why this is safer than supply-rail starve:** the LPC2361 DAC and
> shared analog rails are NOT touched. Worst case: pitch drifts low,
> oscillator stops oscillating until you let go. No risk of cooking the
> digital chip.

---

## Panel summary

These mods add the following holes to the MicroBrute panel (consolidated
for the drilling template):

| Hole type | Quantity added | For mods |
|-----------|----------------|----------|
| 6 mm jack hole | 4 | M03 sine, M06 PWM CV (incl M09 normalled), M12 ARG audio in, M04 metalizer CV |
| 7 mm pot hole | 3 | M04 metalizer amount, M08 sub mix, M12 ARG threshold |
| 6.2 mm toggle hole | 6 | M02 soft-sync mode, M05 selfosc kill, M07 pitch starve, M08 sub enable, M10 brute extreme, M13 sync→env |
| 6 mm brass-bolt hole | 2 | M11 touch retrig (9th bolt), M14 bias starve |

Together with the existing panel mods (B1–B6 + 8 touch bolts), the
revised MicroBrute panel template (`panel/microbrute_panel_template.svg`)
must accommodate these new positions.

## BOM additions

| Part | Qty | Used for |
|------|-----|----------|
| LM393 dual comparator | 2 | M02 soft sync + M12 ARG |
| LM13700 OTA | 1 | M04 metalizer VCA |
| 74HC74 dual D-flip-flop | 1 | M08 sub-harmonic |
| 33 kΩ resistor (precise) | 1 | M01 triangle gain |
| 22 kΩ resistor | 1 | M14 bias starve |
| 39 kΩ resistor | 1 | M06 PWM CV |
| 470 Ω resistor | 1 | M07 pitch starve |
| 100 kΩ resistors | ~6 | various |
| 1N4148 diodes | ~4 | various (M02, M11, M14) |
| 100 nF caps | ~4 | various |
| 6 mm Thonkiconn jacks | 4 | new panel jacks |
| 6 mm switching jack | 1 | M09 normalled |
| 9 mm linear pots | 3 | M04, M08, M12 |
| SPDT mini-toggle | 5 | M02, M07, M08, M10, M13 |
| SPST mini-toggle | 1 | M05 selfosc kill |
| M3 brass bolts | 2 | M11, M14 (matching existing 8 touch bolts) |

Combined cost estimate: ~€15–20 (most parts shared with existing BOM, ICs
sourceable from TME).

## Build order

Recommended sequence after Phase 0 bench validation:

1. **M01** triangle gain — cheapest mod, immediate audible improvement, no PCB risk
2. **M06** PWM CV input + **M09** normalled jack — safe injection, big musical payoff
3. **M03** sine extraction — uses the spare op-amp from I6
4. **M11** + **M14** brass bolts — extend the existing touch-plate cluster
5. **M05** filter self-osc kill + **M07** pitch starve + **M10** brute extreme + **M13** sync→env — toggles, low risk
6. **M02** active soft sync — bench-test on breadboard first
7. **M12** ARG — bench-test on breadboard
8. **M08** sub-harmonic — most complex, needs stripboard
9. **M04** metalizer VCA — most invasive (cuts the metalizer feedback loop), do last

## Verification per mod

Each mod's schematic figure (`schematics/mod_m**.svg`) lives in the
generated SVG set. The complex ones (M02, M04, M08, M12) also have
stripboard layouts under `schematics/mod_m**_stripboard.svg`. Running
`python3 tools/generate_schematics.py` and `python3 tools/generate_layouts.py`
regenerates everything from source.

The revised panel template
(`panel/microbrute_panel_template.svg`) shows where each new hole sits
in the MicroBrute case overlay.
