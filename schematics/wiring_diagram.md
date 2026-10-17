# MACROBRUTE — Complete Internal Wiring Diagram

All connections from MicroBrute test points through breakout PCB,
DB-9 connectors, interconnect cable, and into the expander.

---

## Signal Flow Overview

Decided design (connection map sections 2-5, 11; back-feed and hum design note "BF"): two DB-9
connectors (confirmed by the owner), split power, **no supply and no I²C on either cable**, only
shared ground. EFFIGY is shelved and the strip OLED is dropped.

```
  MicroBrute PCB                Breakout PCB                          DB-9 (Rear)     Cable    Expander
  ═══════════                   ════════════                          ══════════      ═════    ════════
  TP94 (Saw) ─────[1kΩ]──── TL074 A follower ──[1kΩ]──────────────── A pin 7 ◄══════► A pin 7 ── SAW jack
  TP93 (Sqr) ─────[1kΩ]──── TL074 B follower ──[1kΩ]──────────────── A pin 8 ◄══════► A pin 8 ── SQR jack
  TP30 (Mix) ─────[1kΩ]──── TL074 C follower ──[1kΩ]──────────────── A pin 5 ◄══════► A pin 5 ── MIX jack
  TP19 (VCF) ─────[1kΩ]──── TL074 D follower ──[1kΩ]──────────────── A pin 6 ◄══════► A pin 6 ── VCF jack
  TP83 (Gate) ────[10kΩ]─── CD40106 ×2 (in series) ──[1kΩ]────────── A pin 1 ◄══════► A pin 1 ── GATE jack
                                                                                               └─ 22k/33k ── Pico GPIO (FT)
  Pitch CV (rear) ───────── stock buffer ──[220Ω]──────────────────── A pin 2 ◄══════► A pin 2 ── PITCH jack
  Envelope (mod) ──[10kΩ]── TL072 follower ──[1kΩ]─────────────────── A pin 3 ◄══════► A pin 3 ── ENV jack
  LFO (mod) ──────[10kΩ]── TL072 follower ──[1kΩ]─────────────────── A pin 4 ◄══════► A pin 4 ── LFO jack
  GND (TP72 star) ──────────────────────────────────────────────────── A pin 9 ◄══════► A pin 9 ── GND (expander star)

  LPC2361 RXD1 (pin 63) ──[1kΩ]────────────────────────────────────── B pin 1 ◄══════► B pin 1 ──[1kΩ]── Pico GP0 (UART0 TX)
  GND ─────────────────────────────────────────────────────────────── B pin 2 ◄══════► B pin 2 ── GND
  TP10 (VCA CV) ◄── clamp node ◄──[100kΩ]──────────────────────────── B pin 3 ◄══════► B pin 3 ──[10kΩ]── CV driver (TO DESIGN)
  GND ─────────────────────────────────────────────────────────────── B pin 4 ◄══════► B pin 4 ── GND
  TP26 (Filter CV) ◄── clamp node ◄──[100kΩ]───────────────────────── B pin 5 ◄══════► B pin 5 ──[10kΩ]── CV driver (TO DESIGN)
  LPC2361 TXD1 (pin 62) ──[1kΩ]────────────────────────────────────── B pin 6 ◄══════► B pin 6 ──[1kΩ]── Pico GP1 (UART0 RX)
  GND ─────────────────────────────────────────────────────────────── B pins 7, 8, 9 ◄═► B 7, 8, 9 ── GND
```

- A lines 2-8 go to expander panel jacks with no expander IC on them (BF 2.3). If one is later
  normalled into an expander circuit, it enters through at least 100kΩ (BF 3.6).
- Clamp node (B:3, B:5): BAT85 to +12V_BRK and from -12V_BRK, 1nF to GND (BF 3.3).
- The LPC UART (UART1, LQFP pins 62 / 63) is UNVERIFIED until the Phase 0 continuity gate G1.
- Gate stage, divider and the UART firmware rule are Provisional (BF 3.1, 3.4, 3.5).

---

## DB-9 Pin Assignment (Final)

From BF section 2. Neighbour geometry of the D-sub insert is UNVERIFIED until BF BT-7.

### DB-9 A: OUTPUTS (MicroBrute → Expander)

```
   top row     [1 GATE]-[2 PITCH]-[3 ENV]-[4 LFO]-[5 MIX]
   bottom row        [6 VCF]-[7 SAW]-[8 SQUARE]-[9 GND]
```

| Pin | Signal | Source | Buffer | Series R (MB board) | Wire Color (suggested) |
|-----|--------|--------|--------|---------------------|----------------------|
| 1 | Gate Out | TP83 | 2× CD40106 in series | 1kΩ | White |
| 2 | Pitch CV Out | Rear panel | Stock pitch buffer (low impedance UNVERIFIED, E-16) | 220Ω | Yellow |
| 3 | Envelope Out | Mod matrix / TP5 | TL072 follower | 1kΩ after the feedback tap | Orange |
| 4 | LFO Out | Mod matrix | TL072 follower | 1kΩ after the feedback tap | Green |
| 5 | VCO Mix Out | TP30 | TL074 follower | 1kΩ | Blue |
| 6 | VCF Out | TP19 | TL074 follower | 1kΩ | Purple |
| 7 | Saw Out | TP94 | TL074 follower | 1kΩ | Red |
| 8 | Square Out | TP93 | TL074 follower | 1kΩ | Brown |
| 9 | GND | TP72 | — | — | Black |

### DB-9 B: DIGITAL + CV (Expander ↔ MicroBrute)

```
   top row     [1 UART TX]-[2 GND]-[3 VCA CV]-[4 GND]-[5 FILTER CV]
   bottom row        [6 UART RX]-[7 GND]-[8 GND]-[9 GND]
```

| Pin | Signal | Direction | Series R | Protection | Wire Color (suggested) |
|-----|--------|-----------|----------|------------|----------------------|
| 1 | UART TX (Pico GP0 → LPC RXD1, pin 63) | Expander → MB | 1kΩ expander + 1kΩ MB | GP0 high-impedance until GP1 reads high | White |
| 2 | GND | — | — | Guard | Black |
| 3 | VCA CV In (to TP10) | Expander → MB | 10kΩ expander + 100kΩ MB | 2× BAT85 to ±12V_BRK, 1nF | Purple |
| 4 | GND | — | — | Guard | Black |
| 5 | Filter CV In (to TP26) | Expander → MB | 10kΩ expander + 100kΩ MB | As pin 3 | Blue |
| 6 | UART RX (LPC TXD1, pin 62 → Pico GP1) | MB → Expander | 1kΩ MB + 1kΩ expander | GP1 fault tolerant | Yellow |
| 7 | GND | — | — | Guard | Black |
| 8 | GND | — | — | Guard | Black |
| 9 | GND | — | — | Star return | Black |

The old B map (Filter, VCA, Resonance, Sync, Gate In, Ext Audio, +12V, -12V, GND) is withdrawn:
supplies do not cross the cable (split power), resonance CV moved to a new MB panel jack, and Sync
In, Gate In and Ext Audio In use the synth's existing rear jacks (connection map section 3).

---

## Clock I/O (internal to the expander)

Both clock jacks and the Pico are on the expander, in the rack domain. **No clock cable runs
between the MicroBrute and the expander** (it would be a second ground tie; audit N08).

```
  Pico GP22 (Clock Out) ── CD4049UB ×2 (on Pico 3V3) ──[1kΩ]── Expander CLK OUT jack
  Expander CLK IN jack ── 100kΩ pull-down + 100kΩ series ── CD4049UB ×2 ── Pico GP21 (Clock In)
```

Details: `expander_circuits.md` section 4 (BF 3.7).

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
  TP124 (Tri)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-5 (2x gain buffer → body jack)
  TP19  (VCF)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-3
  TP30  (Mix)    ── 24AWG ── [1kΩ] ── Breakout PCB J1-4
  TP83  (Gate)   ── 24AWG ── [10kΩ] ── Breakout PCB J2-1   (keep this lead short, audit N11)
```

### Front Board Taps

```
  Envelope (mod matrix) ── 24AWG ── [10kΩ] ── Breakout PCB J3-1
  LFO (mod matrix)      ── 24AWG ── [10kΩ] ── Breakout PCB J3-2
  TP10 (VCA CV)         ── 24AWG ── from the B:3 clamp node (100kΩ + 2× BAT85 + 1nF)
  TP26 (Filter CV)      ── 24AWG ── from the B:5 clamp node (100kΩ + 2× BAT85 + 1nF)
```

Whether the synth's own 220kΩ (R67, TP26) and 100kΩ (R25, TP10) sit after these points is
UNVERIFIED (E-18).

### Power Taps

```
  TP70 (+12V) ── 22AWG Red   ── Breakout PCB power header (rail protection, C12 OPEN)
  TP71 (-12V) ── 22AWG Blue  ── Breakout PCB power header (diode: cathode toward TP71)
  TP72 (GND)  ── 22AWG Black ── Breakout PCB power header; each DB-9 ground pin by its own lead
```

No synth +5V or 3V3 is tapped (audit B09). The breakout's only 5 V is a local 78L05 for the
CD40106 (Provisional).

### Pico Connections

None inside the MicroBrute: the Pico, OLED, encoder, button, LEDs and clock I/O are on the
expander (connection map sections 1 and 10). The only MB-side digital wires are the two UART lines
to the LPC (connection map section 5.4).

---

## Interconnect Cable Construction

### Cables: 2× DB-9, shielded 9-conductor

```
  MicroBrute rear ◄──── DB-9 ════════ DB-9 ────► Expander
  (panel mount)          (cable, 1 m working figure)   (panel mount, shell isolated)
```

- Two shielded 9-conductor cables, one per connector (not ribbon; audit N19).
- Braid bonded to the connector shell at the MicroBrute end only; that MB shell gets a short lead
  to TP72. At the expander end the braid is cut back and insulated in the hood, and the panel
  connector shell is isolated with insulating shoulder washers (not owned, BF Q10) (BF 4.2).
- A molded off-the-shelf cable (for example the Amphenol CS-DSPMDB09MF named earlier) bonds the
  braid at both hoods: it must be modified, or the cable built from 9-conductor + braid and
  solder-cup connectors.
- Length: 1 m working figure, UNVERIFIED until BF BT-6 (cable capacitance) and BT-1 (UART edges).
- Connector count, gender and flange of the owned DB-9s: UNVERIFIED (BF Q9).
- Series resistors sit on the board side of each connector, never in the cable.

### Additional Clock Cable

None (see Clock I/O above).

---

## Grounding Strategy

From BF 4.1-4.3 and connection map section 11.

- **Exactly one ground connection between synth and rack: the cable ground conductors** (A:9;
  B:2, B:4, B:7, B:8, B:9), all running between the same two star points.
- **MicroBrute star: TP72.** Every cable ground pin and the breakout ground go to TP72 by their own
  short wires, not through the breakout's ground strip.
- **Expander star:** where rack 0 V enters at the 16-pin header.
- Shield: MB end only (above); the shield never carries signal return.
- No USB on the Pico while the cables are connected (USB ground loop, BF 4.3).
- **Never create ground loops:** no chassis or panel bond between the two cases, no clock cable,
  no capacitor in series with any ground pin (audit S23).
- Hum fallback ladder (owned parts only): connection map section 11, BF 4.5.
