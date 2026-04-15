# MACROBRUTE Expander — DB-37 Pinout Specification

## Connector: DB-37 (DE-37)

- **MicroBrute side:** DB-37 Female (socket) — panel mount or flying lead
- **Expander side:** DB-37 Male (plug) — panel mount
- **Cable:** DB-37 Male-to-Female extension, or hand-wired with individual conductors

---

## Pinout Map

```
DB-37 Female (MicroBrute side, looking at solder cups)

         1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
        ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
        │⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│⚫│
        └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
           └──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┘
              20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37
```

---

## Pin Assignments

### Power Section (Pins 1-4)

| Pin | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| 1 | **+12V** | MB → Exp | Through 100Ω ferrite bead at MB end |
| 2 | **GND (Power)** | — | Dedicated power ground |
| 3 | **−12V** | MB → Exp | Through 100Ω ferrite bead at MB end |
| 4 | **GND (Power)** | — | Dedicated power ground |

### CV Outputs from MicroBrute (Pins 5-12)

| Pin | Signal | Direction | Source | Notes |
|-----|--------|-----------|--------|-------|
| 5 | **Pitch CV Out** | MB → Exp | Rear panel / DAC | 1V/Oct, C1=0V |
| 6 | **Gate Out** | MB → Exp | TP83 | **MUST buffer** — 100kΩ source Z |
| 7 | **GND (CV)** | — | | Ground between CV signals |
| 8 | **Velocity CV Out** | MB → Exp | PT675 | Hidden DAC output! |
| 9 | **Envelope Out** | MB → Exp | Mod matrix | 0 to +4.5V |
| 10 | **LFO Out** | MB → Exp | Mod matrix | ±5V |
| 11 | **Mod Wheel CV Out** | MB → Exp | DAC Ch C | Via buffer |
| 12 | **GND (CV)** | — | | Ground after CV group |

### Audio Outputs from MicroBrute (Pins 13-21)

| Pin | Signal | Direction | Source | Notes |
|-----|--------|-----------|--------|-------|
| 13 | **VCO Mix Out** | MB → Exp | UB6 pin 7 | Pre-filter, buffered |
| 14 | **VCF Out** | MB → Exp | TP19 | Post-filter tap |
| 15 | **GND (Audio)** | — | | Ground between audio |
| 16 | **Saw Out** | MB → Exp | TP94 | Via 1kΩ resistor |
| 17 | **Square Out** | MB → Exp | TP93 | Via 1kΩ resistor |
| 18 | **Triangle Out** | MB → Exp | TP124 | Via 1kΩ resistor |
| 19 | **Sub Out** | MB → Exp | TP102 | Via 1kΩ resistor |
| 20 | **Metalizer Out** | MB → Exp | TP109 | Via 1kΩ resistor |
| 21 | **GND (Audio)** | — | | Ground after audio group |

### CV/Audio Inputs to MicroBrute (Pins 22-28)

| Pin | Signal | Direction | Destination | Notes |
|-----|--------|-----------|-------------|-------|
| 22 | **Filter CV In** | Exp → MB | Summing node | Via 220kΩ series R |
| 23 | **VCA CV In** | Exp → MB | TP10/TP11 | 0-5V effective range |
| 24 | **PWM CV In** | Exp → MB | PW summing | Via 39kΩ series R |
| 25 | **GND (CV In)** | — | | Ground for input CVs |
| 26 | **Ext Audio In** | Exp → MB | Mixer input | Attenuate from Eurorack |
| 27 | **VCF Insert** | Bidirectional | R23 junction | Switched jack breaks path |
| 28 | **Metalizer Insert** | Bidirectional | R216 junction | Switched jack breaks path |

### Gate/Trigger/Sync (Pins 29-32)

| Pin | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| 29 | **GND (Gate)** | — | Ground for gate signals |
| 30 | **Gate In** | Exp → MB | +5V threshold |
| 31 | **Sync In** | Exp → MB | Hard/soft sync to VCO |
| 32 | **Clock Out** | MB → Exp | From Pico (or 555) |

### Expansion / Future (Pins 33-37)

| Pin | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| 33 | **SPARE 1** | — | Future: Resonance CV? |
| 34 | **SPARE 2** | — | Future: Brute Factor CV? |
| 35 | **SPARE 3** | — | Future: Body contacts? |
| 36 | **SPARE 4** | — | Future: Additional audio? |
| 37 | **GND (Spare)** | — | Ground for expansion |

---

## Signal Summary

| Category | Count | Pin Range |
|----------|-------|-----------|
| Power (+12V, −12V) | 2 | 1, 3 |
| Power Ground | 2 | 2, 4 |
| CV Outputs | 6 | 5-6, 8-11 |
| CV Ground | 2 | 7, 12 |
| Audio Outputs | 7 | 13-14, 16-20 |
| Audio Ground | 2 | 15, 21 |
| CV/Audio Inputs | 6 | 22-24, 26-28 |
| Input Ground | 1 | 25 |
| Gate/Sync | 3 | 30-32 |
| Gate Ground | 1 | 29 |
| Spare | 4 | 33-36 |
| Spare Ground | 1 | 37 |
| **TOTAL** | **37** | |

**Signals: 24 active + 4 spare = 28**
**Grounds: 9 pins**

---

## Ground Distribution Strategy

Grounds are interleaved between signal groups to minimize crosstalk:

```
[PWR GND] — [CV OUT] — [GND] — [CV OUT] — [GND] — [AUDIO] — [GND] — [AUDIO] — [GND] — [CV IN] — [GND] — [GATE] — [GND] — [SPARE] — [GND]
```

All grounds connect to a **single star point** on the expander PCB, then to chassis/panel ground at one point only.

---

## MicroBrute Internal Wiring Reference

### Test Points to Wire

| Signal | Test Point | Board | Series R | Notes |
|--------|------------|-------|----------|-------|
| Velocity CV | PT675 | Rear | — | Hidden DAC, direct tap |
| VCO Mix | TP30 → UB6 | Front | 1kΩ out | Use unused op-amp half |
| VCF Out | TP19 | Front | 1kΩ | Post-filter |
| Saw | TP94 | Rear | 1kΩ | Raw waveform |
| Square | TP93 | Rear | 1kΩ | Raw waveform |
| Triangle | TP124 | Rear | 1kΩ | Raw waveform |
| Sub | TP102 | Rear | 1kΩ | Affected by knob |
| Metalizer | TP109 | Rear | 1kΩ | Affected by knob |
| Gate (internal) | TP83 | Rear | — | Needs buffer on expander |
| Filter CV | **TP26** | Front | 220kΩ in | "Misc Cutoff Input" per schematic (TP27/28 also available) |
| VCA CV | TP10 or TP11 | Front | — | Direct injection |
| PWM CV | R289 junction | Rear | 39kΩ in | PW circuit |
| +12V | TP70 | Front | Ferrite | Power tap |
| −12V | TP71 | Front | Ferrite | Power tap |
| GND | TP72 or TP73 (**UNVERIFIED**) | Front | — | Multiple GND points |

### Insert Mods (Resistor Removal)

| Insert | Resistor | Value | Location | Procedure |
|--------|----------|-------|----------|-----------|
| VCF Insert | R23 | 100kΩ | Front board | Remove, wire NC to VCF side, Tip to VCA side via 100kΩ |
| Metalizer Insert | R216 | 120kΩ | Rear board | Remove, wire NC to triangle side, Tip to wavefolder via 120kΩ |

---

## Cable Construction

### Option A: Individual Wires (Recommended)

- **Wire:** 26 AWG stranded, multiple colors
- **Length:** 0.5m – 1.5m max
- **Shielding:** Optional braided sleeve over bundle
- **Termination:** Solder cups on DB-37

Color coding suggestion:
- Red: +12V
- Blue: −12V
- Black: All grounds (9 wires)
- Yellow: CV outputs
- Orange: CV inputs
- White: Audio outputs
- Green: Audio inputs / inserts
- Purple: Gate/sync

### Option B: Ribbon Cable (Easier but Less Flexible)

- **Cable:** 40-conductor IDC ribbon
- **Adapters:** IDC-to-DB37 breakout at each end
- **Caution:** No individual shielding, potential crosstalk on long runs

---

## Expander Panel Layout (28HP)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MACROBRUTE EXPANDER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CV OUTPUTS          AUDIO OUTPUTS           WAVEFORMS              │
│  ┌───┐ ┌───┐        ┌───┐ ┌───┐            ┌───┐ ┌───┐ ┌───┐ ┌───┐ │
│  │PCH│ │GAT│        │MIX│ │VCF│            │SAW│ │SQR│ │TRI│ │SUB│ │
│  └───┘ └───┘        └───┘ └───┘            └───┘ └───┘ └───┘ └───┘ │
│  ┌───┐ ┌───┐        ┌───┐                  ┌───┐                    │
│  │VEL│ │ENV│        │MTL│                  │CLK│                    │
│  └───┘ └───┘        └───┘                  └───┘                    │
│  ┌───┐ ┌───┐                                                        │
│  │LFO│ │MOD│        INSERTS                                         │
│  └───┘ └───┘        ┌───┐ ┌───┐                                     │
│                     │VCF│ │MTL│  ← Accent color                     │
│  CV INPUTS          └───┘ └───┘                                     │
│  ○ FILT  ┌───┐                              GATE/SYNC               │
│  └──┬────┤   │      AUDIO IN               ┌───┐ ┌───┐              │
│     ╰pot─┘   │      ┌───┐                  │G.I│ │SYN│              │
│  ○ VCA   ┌───┐      │EXT│                  └───┘ └───┘              │
│  └──┬────┤   │      └───┘                                           │
│     ╰pot─┘   │                                                      │
│  ○ PWM   ┌───┐                             ┌─────────────────────┐  │
│  └──┬────┤   │                             │      [DB-37]        │  │
│     ╰pot─┘   │                             │                     │  │
│                                            └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

Legend:
○ = Attenuator pot (100kΩ)
┌───┐ = 3.5mm Thonkiconn jack
```

**Jack count:** 22 jacks + 3 attenuator pots + DB-37

---

## Buffer Circuit Requirements (Expander Side)

All signals from MicroBrute need buffering on the expander:

```
                      +12V
                       │
              ┌────────┴────────┐
From DB-37 ───┤+     TL074     ├───┬─── To Eurorack Jack
      │       │    (1/4)       │   │
      R1      └────────┬───────┘   R2
      1MΩ              │           1kΩ
      │                │           │
     GND         ──────┴───────   GND
                 (feedback)

R1: 1MΩ input bias (prevents floating when disconnected)
R2: 1kΩ output protection (inside feedback loop)
```

**ICs needed:**
- 3× TL074 (12 buffers total) — covers all outputs
- 1× TL072 (2 buffers) — for inserts or spares

**Gate buffer** needs a comparator or Schmitt trigger to clean up the weak MicroBrute gate:
- Use 1/4 of a CD40106 hex Schmitt inverter
- Or LM393 comparator with ~2.5V threshold

---

## Power Options

### Option A: Power from MicroBrute (Desktop Use)

- Tap +12V from TP70, −12V from TP71
- Include 100Ω ferrite beads in series
- Expander draws ~50-80mA — within MicroBrute headroom
- Pro: Single power supply
- Con: Shared ground may introduce noise

### Option B: Power from Eurorack Bus (Rack Use)

- Standard 16-pin or 10-pin Eurorack power header on expander
- DB-37 pins 1-4 left unconnected (or use for ground only)
- Pro: Clean, isolated power
- Con: Requires rack power

### Option C: Dedicated Supply (Desktop Use)

- MeanWell RD-35A (5V/12V) or similar dual-output
- Or 7812/7912 regulators from 15-18V AC adapter
- Pro: Maximum isolation
- Con: Another wall wart

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 2026 | Initial DB-37 pinout |

---

## Next Steps

1. [ ] Photograph MicroBrute PCBs with test point locations marked
2. [ ] Verify TP numbering against actual boards
3. [ ] Prototype buffer board on stripboard
4. [ ] Test individual signals before committing to DB-37
5. [ ] Design expander PCB in KiCad
6. [ ] Order DB-37 connectors, backshells, hardware
7. [ ] Drill MicroBrute case for DB-37 (or route cable through existing opening)
