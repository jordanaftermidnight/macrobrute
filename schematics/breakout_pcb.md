# MACROBRUTE Internal Breakout PCB — Schematic

Mounts inside MicroBrute. Houses Pico H, output buffers, gate buffer,
LED drivers, vactrol driver, and DB-9 header connections.

## Power Supply (from MicroBrute rails)

```
MicroBrute +12V (TP70) ──[1N5817]──┬──[100Ω ferrite]──┬── +12V_BRK
                                    │                   │
                                   100µF/25V          100nF
                                    │                   │
                                   GND                 GND

MicroBrute -12V (TP71) ──[1N5817]──┬──[100Ω ferrite]──┬── -12V_BRK
                                    │                   │
                                   100µF/25V          100nF
                                    │                   │
                                   GND                 GND

MicroBrute +5V ──[1N5817]──┬── Pico VSYS (pin 39)
                            │
                          100nF
                            │
                           GND

Pico 3V3_OUT (pin 36) ── 3V3 rail for OLED, encoder pull-ups
```

## Output Buffer Board (TL074 #1 — 4 channels)

Buffers waveform test point taps. Unity-gain voltage followers prevent
loading the MicroBrute's internal circuits.

```
                    +12V_BRK
                       │
                 ┌─────┤
                 │   ┌──┴──┐
  TP94 (Saw) ────┤   │     │
       via 1kΩ   ├───┤+ TL074├─── DB-9 A pin 7 (Saw Out)
                 │   │  A   │
                 │   └──┬──┘
                 │      │
                 └──────┘ (feedback: output → inverting input)
                       │
                    -12V_BRK

  TP93 (Square) ──1kΩ──┤+  TL074 B├─── DB-9 A pin 8 (Square Out)
  TP30 (VCO Mix)──1kΩ──┤+  TL074 C├─── DB-9 A pin 5 (VCO Mix Out)
  TP19 (VCF Out)──1kΩ──┤+  TL074 D├─── DB-9 A pin 6 (VCF Out)
```

Each channel:
```
  Test Point ──[1kΩ]──┬──[TL074 +in]
                      │        │
                     GND      out──┬── to DB-9
                      via     │    │
                     10MΩ    [1kΩ] │  (output isolation)
                             │    feedback
                            GND   to -in
```

**Component values per channel:**
- R_series: 1kΩ (input protection / isolation)
- R_bias: 10MΩ to GND (DC bias path for AC-coupled signals)
- R_output: 1kΩ (output isolation for cable drive)
- C_decouple: 100nF ceramic per supply pin

## Gate Buffer (CD40106 Schmitt Trigger)

TP83 has 100kΩ source impedance — too weak for direct use.

```
                         +5V
                          │
                        10kΩ
                          │
  TP83 (Gate) ──[10kΩ]──┬─── CD40106 pin 1 (input A)
                         │
                       100nF  (noise filter)
                         │
                        GND

  CD40106 pin 2 (output A) ──── DB-9 A pin 1 (Gate Out)

  CD40106 pin 14 = +5V
  CD40106 pin 7  = GND
  100nF decoupling on Vcc
```

**Output:** Clean 0/5V gate, low impedance (~50Ω)

## Envelope & LFO Taps (from mod matrix)

These signals are available at the front panel mod matrix connections.
Buffer with TL074 #2 (spare sections from expander design or add second IC).

```
  Envelope (mod matrix) ──[10kΩ]──┤+ TL074 follower├── DB-9 A pin 3
  LFO (mod matrix)      ──[10kΩ]──┤+ TL074 follower├── DB-9 A pin 4
```

## LED Drivers (3x 2N3904 NPN)

Pico GPIO at 3.3V, LEDs need ~10-20mA.

```
  Per LED:

  Pico GPIO ──[1kΩ]── 2N3904 Base
                       │
                    Collector ──[470Ω]── LED anode
                       │                  │
                    Emitter              LED cathode
                       │                  │
                      GND               +3.3V
```

Wait — LEDs are active-high from the NPN collector. Corrected:

```
  +3.3V ──[470Ω]── LED anode ── LED cathode ──┬── 2N3904 Collector
                                                │
  Pico GPIO ──[1kΩ]── 2N3904 Base              │
                                                │
                       2N3904 Emitter ──────── GND
```

**R_base:** 1kΩ → I_base = (3.3 - 0.7) / 1k = 2.6mA (saturates 2N3904)
**R_led:** 470Ω → I_led = (3.3 - 2.0 - 0.2) / 470 = ~2.3mA (dim but visible)
For brighter: use 220Ω → ~5mA

## Vactrol Driver (Resonance CV)

The CV signal arrives from expander via DB-9 B pin 3.
Inside the MicroBrute, it drives a vactrol (LED+LDR) that parallels
the resonance control (RP13 / JFET path).

```
  DB-9 B pin 3 ──[1kΩ]──┬── TL072 non-inv amp (+in)
  (Resonance CV)         │         │
                        GND       out ──[1kΩ]──┬── Vactrol LED anode
                        via               │     │
                       10MΩ               │   Vactrol LED cathode
                                          │     │
                                         GND   GND (via 100Ω current limit)
```

Full vactrol driver:
```
                    +12V_BRK
                       │
                 ┌─────┤
                 │   ┌──┴──┐
  DB-9 B pin 3 ──┤   │     │
     via 1kΩ     │   │TL072│── out ──[1kΩ]── 2N3904 Base
                 │   │  A  │                    │
                 │   └──┬──┘                 Collector
                 │      │                       │
                 └──────┘                  Vactrol LED (+)
                       │                       │
                    -12V_BRK              Vactrol LED (-)
                                               │
                                             [100Ω]
                                               │
                                              GND

  Vactrol LDR ── wired in parallel with RP13 (resonance JFET)
  Higher CV → more LED light → lower LDR resistance → more resonance
```

**Current limit:** 100Ω → max LED current = (12 - 2 - 0.2) / 100 = ~98mA
Too high! Use 470Ω → ~21mA. Or better: 1kΩ → ~10mA (sufficient for vactrol).

**Corrected R_limit: 1kΩ**

## CV Input Protection (DB-9 B inputs)

Each CV input from the expander gets protection at the breakout board.

```
  DB-9 B pin N ──[1kΩ]──┬── to injection point
                         │
                    ┌────┤────┐
                  BAT54S      BAT54S
                    │         │
                  +12V      -12V
```

This clamps any input to ±12.3V (Schottky forward drop).
The 1kΩ limits fault current to ~12mA.

## Pico H Mounting

- Mount via pin headers on breakout PCB
- Or solder directly (more reliable in vibrating synth environment)
- Route ribbon cable to OLED (5 wires: SCK, MOSI, CS, DC, RST + VCC + GND)
- Route 3 wires to encoder (CLK, DT, SW + VCC + GND)
- Route 2 wires to button
- Route 3 wires to LEDs
- Route 2 wires to clock I/O

## PCB Size Estimate

- ~60mm x 40mm (fits inside MicroBrute near digital board)
- Single-sided perfboard adequate
- Mount with VHB tape or M2 standoffs

## Component Summary

| Component | Qty | Package |
|-----------|-----|---------|
| TL074CN | 1 | DIP-14 |
| TL072CP | 1 | DIP-8 |
| CD40106 | 1 | DIP-14 |
| 2N3904 | 3 | TO-92 |
| 1N5817 | 3 | DO-41 |
| 1kΩ | 12 | 1/4W |
| 10kΩ | 3 | 1/4W |
| 470Ω | 3 | 1/4W |
| 10MΩ | 4 | 1/4W |
| 100nF ceramic | 6 | — |
| 100µF/25V electrolytic | 2 | — |
| Ferrite bead 100Ω | 2 | Axial |
| BAT54S | 3 | SOT-23 |
| DIP-14 socket | 2 | — |
| DIP-8 socket | 1 | — |
| Pin headers | various | 2.54mm |
| DB-9 solder-cup | 2 | — |
