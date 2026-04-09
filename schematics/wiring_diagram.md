# MACROBRUTE — Complete Internal Wiring Diagram

All connections from MicroBrute test points through breakout PCB,
DB-9 connectors, interconnect cable, and into the expander.

---

## Signal Flow Overview

```
  MicroBrute PCB                Breakout PCB              DB-9 (Rear)           Cable           Expander
  ═══════════                   ════════════              ══════════            ═════           ════════
  TP94 (Saw) ─────[1kΩ]──── TL074 A follower ──[1kΩ]── DB-9 A pin 7 ◄══════► DB-9 A pin 7 ── buffer ── SAW jack
  TP93 (Sqr) ─────[1kΩ]──── TL074 B follower ──[1kΩ]── DB-9 A pin 8 ◄══════► DB-9 A pin 8 ── buffer ── SQR jack
  TP30 (Mix) ─────[1kΩ]──── TL074 C follower ──[1kΩ]── DB-9 A pin 5 ◄══════► DB-9 A pin 5 ── buffer ── MIX jack
  TP19 (VCF) ─────[1kΩ]──── TL074 D follower ──[1kΩ]── DB-9 A pin 6 ◄══════► DB-9 A pin 6 ── buffer ── VCF jack
  TP83 (Gate) ────[10kΩ]──── CD40106 Schmitt ────────── DB-9 A pin 1 ◄══════► DB-9 A pin 1 ── direct ── GATE jack
  Pitch CV (rear) ────────── direct ─────────────────── DB-9 A pin 2 ◄══════► DB-9 A pin 2 ── buffer ── PITCH jack
  Envelope (mod) ──[10kΩ]─── TL074 #2 follower ─────── DB-9 A pin 3 ◄══════► DB-9 A pin 3 ── buffer ── ENV jack
  LFO (mod) ──────[10kΩ]─── TL074 #2 follower ─────── DB-9 A pin 4 ◄══════► DB-9 A pin 4 ── buffer ── LFO jack
  GND ─────────────────────────────────────────────── DB-9 A pin 9 ◄══════► DB-9 A pin 9 ── GND

  Expander jack ── [attenuator pot] ── [BAT54S clamp] ── DB-9 B pin 1 ◄══════► DB-9 B pin 1 ── [1kΩ] ── Filter summing node
  Expander jack ── [attenuator pot] ── [BAT54S clamp] ── DB-9 B pin 2 ◄══════► DB-9 B pin 2 ── direct ── TP10/11 (VCA CV)
  Expander jack ── [attenuator pot] ── LED driver ────── DB-9 B pin 3 ◄══════► DB-9 B pin 3 ── [1kΩ] ── Vactrol LED ── RP13
  Expander jack ──────────────────────────────────────── DB-9 B pin 4 ◄══════► DB-9 B pin 4 ── direct ── VCO sync point
  Expander jack ── [diode protect] ─── ──────────────── DB-9 B pin 5 ◄══════► DB-9 B pin 5 ── direct ── Gate circuit
  Expander jack ───────────────────────────────────────── DB-9 B pin 6 ◄══════► DB-9 B pin 6 ── direct ── Mixer ext input
  +12V (Eurorack bus) ── [fuse] ── [1N5817] ────────── DB-9 B pin 7 ◄══════► DB-9 B pin 7 ── breakout +12V
  -12V (Eurorack bus) ── [fuse] ── [1N5817] ────────── DB-9 B pin 8 ◄══════► DB-9 B pin 8 ── breakout -12V
  GND ─────────────────────────────────────────────── DB-9 B pin 9 ◄══════► DB-9 B pin 9 ── GND
```

---

## DB-9 Pin Assignment (Final)

### DB-9 A: OUTPUTS (MicroBrute → Expander)

| Pin | Signal | Source | Buffer | Wire Color (suggested) |
|-----|--------|--------|--------|----------------------|
| 1 | Gate Out | TP83 | CD40106 Schmitt | White |
| 2 | Pitch CV Out | Rear panel | Direct (stock) | Yellow |
| 3 | Envelope Out | Mod matrix | TL074 follower | Orange |
| 4 | LFO Out | Mod matrix | TL074 follower | Green |
| 5 | VCO Mix Out | TP30 | TL074 follower | Blue |
| 6 | VCF Out | TP19 | TL074 follower | Purple |
| 7 | Saw Out | TP94 | TL074 follower | Red |
| 8 | Square Out | TP93 | TL074 follower | Brown |
| 9 | GND | TP72 | — | Black |

### DB-9 B: INPUTS + POWER (Expander → MicroBrute)

| Pin | Signal | Destination | Protection | Wire Color (suggested) |
|-----|--------|-------------|------------|----------------------|
| 1 | Filter CV In | U8A summing node | 220kΩ series (on expander) | White |
| 2 | VCA CV In | TP10/11 | Direct or 100kΩ | Yellow |
| 3 | Resonance CV | Vactrol LED | 1kΩ current limit | Orange |
| 4 | Sync In | VCO sync point | Direct | Green |
| 5 | Gate In | Gate circuit | 1N4148 diode | Blue |
| 6 | Ext Audio In | Mixer | Direct or switched | Purple |
| 7 | +12V | Breakout PCB | 1N5817 + fuse | Red |
| 8 | -12V | Breakout PCB | 1N5817 + fuse | Brown (or Red/Black stripe) |
| 9 | GND | Star ground | — | Black |

---

## Clock I/O (Separate from DB-9)

Clock signals bypass DB-9 via direct wiring from Pico H to expander.

```
  Pico GP22 (Clock Out) ──[wire through case]── Expander CLK OUT jack
  Pico GP21 (Clock In)  ──[wire through case]── Expander CLK IN jack
  Pico GND              ──[wire through case]── Expander GND

  3 wires total, routed through same rear panel hole as DB-9 cables.
  Use 3-conductor shielded cable or individual 24AWG in sleeve.
```

---

## Internal Wiring (Inside MicroBrute)

### Rear Board Test Point Taps

```
  TP94 (Saw)     ── 24AWG ── [1kΩ SMD or axial] ── Breakout PCB J1-1
  TP93 (Square)  ── 24AWG ── [1kΩ] ── Breakout PCB J1-2
  TP102 (Sub)    ── 24AWG ── [1kΩ] ── Body jack (if installed)
  TP109 (Metal)  ── 24AWG ── [1kΩ] ── Body jack (if installed)
  TP119 (Ultra)  ── 24AWG ── [1kΩ] ── Body jack (if installed)
  TP122 (PWM)    ── 24AWG ── [1kΩ] ── Body jack (if installed)
  TP124 (Tri)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-5 (2x gain buffer)
  TP19  (VCF)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-3
  TP30  (Mix)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-4
  TP83  (Gate)   ── 24AWG ── [10kΩ] ── Breakout PCB J2-1
```

### Front Board Taps

```
  Envelope (mod matrix) ── 24AWG ── [10kΩ] ── Breakout PCB J3-1
  LFO (mod matrix)      ── 24AWG ── [10kΩ] ── Breakout PCB J3-2
  TP10/11 (VCA CV)      ── 24AWG ── from DB-9 B pin 2
  Filter summing node   ── 24AWG ── from DB-9 B pin 1 via 220kΩ
```

### Power Taps

```
  TP70 (+12V) ── 22AWG Red   ── Breakout PCB power header
  TP71 (-12V) ── 22AWG Blue  ── Breakout PCB power header
  TP72 (GND)  ── 22AWG Black ── Breakout PCB power header + DB-9 pin 9
  +5V rail    ── 22AWG Orange ── Breakout PCB (Pico VSYS via 1N5817)
```

### Pico H Connections

```
  Breakout PCB ── 7-pin ribbon ── OLED (SCK, MOSI, CS, DC, RST, VCC, GND)
  Breakout PCB ── 5-pin ribbon ── Encoder (CLK, DT, SW, VCC, GND)
  Breakout PCB ── 3-pin        ── Button (SIG, VCC, GND)
  Breakout PCB ── 6-pin        ── LEDs (CLK, GATE, MODE × 2 wires each)
  Breakout PCB ── 2-pin        ── Clock Out (GP22, GND)
  Breakout PCB ── 2-pin        ── Clock In (GP21, GND)
  Breakout PCB ── 2-pin        ── MIDI TX/RX (GP4, GP5) — future LPC2361
```

---

## Interconnect Cable Construction

### Cable: 2× DB-9 Male-to-Female

```
  MicroBrute rear ◄──── DB-9M ════════ DB-9F ────► Expander panel
  (panel mount F)        (cable)  1m max  (cable)    (panel mount F)
```

- Use Amphenol double-shielded DB-9 cables (CS-DSPMDB09MF)
- Or build custom: 9-conductor + shield, solder-cup DB-9 connectors
- Keep cable under 3m for unbalanced audio
- Gold-plated contacts recommended for frequent mating

### Additional Clock Cable

```
  3× 24AWG in shielded sleeve, ~1m
  Pin 1: Clock Out (Pico GP22)
  Pin 2: Clock In (Pico GP21)
  Shield: GND
```

Route through same rear panel grommet as DB-9 cables.

---

## Grounding Strategy

**Star ground at DB-9 connectors:**
- All signal grounds converge at DB-9 pin 9 (both A and B)
- Single point connection between MicroBrute GND and Expander GND
- Power ground returns separately through DB-9 B pin 9
- Chassis/shield ground via DB-9 shell (both connectors)

**Never create ground loops:**
- Do not connect MB chassis to expander chassis via separate path
- Only ground connection is through DB-9 pin 9 (signal) and shell (shield)
