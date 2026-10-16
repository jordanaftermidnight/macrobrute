# MACROBRUTE — Complete Connection Map

Every signal, mod, bend, and wire in the system. This is the master
wiring reference for building, debugging, and expanding.

**Design sources (2026-10-17):** owner decisions in `docs/superpowers/reviews/2026-10-16-project-audit.md` section 1a,
datasheet facts in `docs/DATASHEETS.md`, and the back-feed and hum design note
`docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md` (cited below as "BF"). Nothing is built yet:
every value here is a design value, and anything marked UNVERIFIED waits for a bench check or an owner answer.

**Connector:** 2× DB-9 (VGA HD-15 rejected — shorts pins 6-8 to GND). Both mount on the MicroBrute **rear panel, left of Pitch/Gate** (owner decision a). Panel dimensions, free area and depth: UNVERIFIED until the owner measures (audit E-20, E-21). DB-9 mounting-hole spacing 24.99 mm (Spectrum Control cut-out, DATASHEETS (g)); flange size of the owner's part UNVERIFIED.
**Power:** split. The expander is powered only from the Eurorack rack; the MicroBrute-side breakout is powered only from the synth (TP70/TP71/TP72). **No supply rail crosses either DB-9 cable**; only ground is shared.
**OLED:** one **0.96" SSD1306 I²C 128×64** main display on the expander (driver `OLED_I2C` in `firmware/pico/display.py`, `OLED_CHIP="SSD1306"`). Size (0.96" vs 1.3"), controller and interface (4-pin I²C vs 7-pin SPI) of the owner's module: UNVERIFIED, owner to confirm (BF Q22). The 0.91" strip OLED is dropped (decision c). **No I²C crosses the DB-9 cable.**
**MIDI path:** Pico UART0 ↔ LPC2361 UART bridge @ 115200 baud (LPC side: see section 5.4). LPC firmware relays as internal MIDI SysEx. No direct 31250-baud MIDI from Pico.
**Firmware:** Pico MicroPython (14 modules + `_effigy_constants.py` generated from EFFIGY's C header; the EFFIGY pairing is SHELVED, section 5.6), LPC2361 ARM7 (stock + planned bridge extension). Pico variant: the docs say Pico WH; UNVERIFIED, owner to confirm (BF Q21).

---

## 1. Pico WH GPIO Allocation

Canonical source: `firmware/pico/config.py`. Update this table AND that file together.

| GPIO | Pico Pin | Function | Direction | Notes |
|------|----------|----------|-----------|-------|
| GP0 | 1 | UART0 TX → LPC2361 | OUT | 115200 baud, DB-9 B:1, 1kΩ series on the expander board (BF 3.1). Design rule: GP0 stays an input until GP1 reads high (firmware rule, not yet implemented) |
| GP1 | 2 | UART0 RX ← LPC2361 | IN | 115200 baud, DB-9 B:6, 1kΩ series on the expander board. Fault-tolerant pin (BF 3.1) |
| GP2 | 4 | Free, reserved (config.py still names it I²C1 SDA for the shelved EFFIGY code) | — | Fault-tolerant digital pin |
| GP3 | 5 | Free, reserved (config.py still names it I²C1 SCL for the shelved EFFIGY code) | — | Fault-tolerant digital pin |
| GP4 | 6 | I²C0 SDA | I/O | Main OLED 0x3C on the expander only (short on-board bus) · 4.7kΩ pull-up to 3V3 |
| GP5 | 7 | I²C0 SCL | OUT | Code runs I²C0 at 400 kHz (`display.py`); older docs said 100 kHz for the cable run, which no longer exists. Doc/code mismatch flagged (audit S05) |
| GP6 | 9 | Aux output 3 | OUT | Programmable: tap-div / euclidean / random / passthrough / PWM-CV |
| GP7 | 10 | Aux output 4 | OUT | Programmable, same modes as GP6 |
| GP8 | 11 | RGB LED R · Clock tick | OUT | PWM, owned exclusively by `leds.LEDManager` |
| GP9 | 12 | RGB LED G · Gate active | OUT | PWM |
| GP10 | 14 | RGB LED B · Mode | OUT | PWM (1 kHz), slice 5A |
| GP11 | 15 | Free, reserved (config.py still names it EFFIGY INT for the shelved EFFIGY code) | — | Fault-tolerant digital pin. Candidate for the gate input (BF 3.5); not assigned |
| GP12 | 16 | Tap button | IN | Pull-up; short = tap tempo, long-hold = manual gate |
| GP13 | 17 | Encoder switch | IN | Pull-up, short = select, long = back |
| GP14 | 19 | Encoder CLK (A) | IN | Pull-up, IRQ on both edges |
| GP15 | 20 | Encoder DT (B) | IN | Pull-up |
| GP16 | 21 | Clock divider out 1 | OUT | Firmware-driven, default ÷2 (configurable) |
| GP17 | 22 | Clock divider out 2 | OUT | Default ÷4 |
| GP18 | 24 | Clock divider out 3 | OUT | Default ÷8 |
| GP19 | 25 | Aux output 1 | OUT | Programmable (PWM-capable) |
| GP20 | 26 | Aux output 2 | OUT | Programmable |
| GP21 | 27 | Clock input | IN | Pull-down, external sync IRQ; fed through the CD4049UB buffer (section 4) |
| GP22 | 29 | Clock output | OUT | Master clock (plain GPIO from a Timer) through the CD4049UB buffer to the expander CLK OUT jack (section 4) |
| GP26 | 31 | ADC0 (free) | IN | Not fault tolerant, diode to IOVDD (Pico datasheet p20). PWM slice 5A shared with GP10 (section 12C) |
| GP27 | 32 | ADC1 (free) | IN | Not fault tolerant |
| GP28 | 34 | ADC2 (free) | IN | Not fault tolerant |
| 3V3 | 36 | 3V3 out | PWR | OLED + encoder + I²C0 pull-ups |
| VSYS | 39 | +5V input | PWR | From rack CP1A +5V via a Schottky OR diode + bulk + 100nF (section 10) |
| GND | 3,8,13,18,23,28,33,38 | Ground | — | To the expander star point (rack 0 V at the 16-pin header), not to TP72 (BF 4.1) |

**Free pins: 6** — GP2, GP3, GP11 (fault-tolerant digital) and GP26, GP27, GP28 (ADC-capable, not fault tolerant). Source: owner decision g, BF section 5.
Allocated in config.py: GP0, GP1, GP4, GP5, GP6, GP7, GP8, GP9, GP10, GP12, GP13, GP14, GP15, GP16, GP17, GP18, GP19, GP20, GP21, GP22.
GP23, GP24, GP25 and GP29 are RP2040-internal and not exposed on the Pico header.
Rule (BF 5): any input that can see a cable or jack signal while the Pico may be unpowered goes on a fault-tolerant pin (GP0-GP22), not on GP26-GP28.

**Tap button modes:** short press (< 400 ms release) → tap tempo. Held press
(≥ 400 ms) → manual gate (RGB-G LED full-bright while held; gate signal also
goes to LPC bridge as a synthetic note-on/off pair).

**RGB LED color semantics:**

| Channel | Pin | Meaning |
|---------|-----|---------|
| Red     | GP8 | Brief flash on each clock tick |
| Green   | GP9 | Solid while gate is high (manual or external) |
| Blue    | GP10 | Mode indicator (the old "paired with EFFIGY" meaning is shelved) |

Mixed colors arise naturally — yellow = clock + gate, cyan = gate + mode,
magenta = clock + mode, white = all three.

**USB-MIDI:** Pico micro-USB enumerates as a USB-MIDI class device via TinyUSB
(`firmware/pico/usbmidi.py`). Orthogonal to the LPC bridge — gives the host
DAW a "Macrobrute Pico" MIDI port. Pico does NOT drive 5-pin DIN MIDI; that
stays on the stock 6N138 → LPC2361 MIDI UART path inside the MicroBrute (UART3 per
the firmware disassembly, audit S06; the 6N138-to-pin-85 route is UNVERIFIED, audit E-02).
**USB ground rule (BF 4.3):** no USB cable on the Pico while the expander is rack-powered
and the DB-9 cables are connected; flash and debug with the DB-9 cables unplugged. Runtime
USB-MIDI with the cables connected needs a USB isolator, which is not owned (BF Q17).

---

## 2. DB-9 A — Outputs (MicroBrute → Expander)

From BF section 2.3. A has 8 signals and 1 ground, so no pin can be interleaved; the order is kept.
Connector face (insert numbering; neighbour geometry UNVERIFIED until BF BT-7):

```
   top row     [1 GATE]-[2 PITCH]-[3 ENV]-[4 LFO]-[5 MIX]
   bottom row        [6 VCF]-[7 SAW]-[8 SQUARE]-[9 GND]
```

| Pin | Signal | MB Source | Buffer | Series R (MB board) | Protection / Notes | Wire Color |
|-----|--------|-----------|--------|----------|----------|------------|
| 1 | Gate Out | TP83 | 2× CD40106 in series (keeps TP83 polarity) | 1kΩ at the CD40106 output | Expander: 22k / 33k divider into a Pico fault-tolerant GPIO; gate jack tapped before the divider. Provisional (BF 3.4, 3.5) | White |
| 2 | Pitch CV Out | Rear panel jack | Stock pitch buffer | 220Ω (new; was "direct") | Low-impedance source UNVERIFIED (E-16) | Yellow |
| 3 | Envelope Out | Mod matrix / TP5 | TL07x follower | 1kΩ after the feedback tap | Source choice UNVERIFIED (audit N23) | Orange |
| 4 | LFO Out | Mod matrix | TL07x follower | 1kΩ after the feedback tap | Source TP21 meaning UNVERIFIED (E-17) | Green |
| 5 | VCO Mix Out | TP30_MIXER_OUT | TL074 follower | 1kΩ in, 1kΩ out | — | Blue |
| 6 | VCF Out | TP19 | TL074 follower | 1kΩ in, 1kΩ out | — | Purple |
| 7 | Saw Out | TP94 | TL074 follower | 1kΩ in, 1kΩ out | Peak level UNVERIFIED (E-19) | Red |
| 8 | Square Out | TP93 | TL074 follower | 1kΩ in, 1kΩ out | Peak level UNVERIFIED (E-19) | Brown |
| 9 | GND | TP72 | — | — | TP72 star and expander star | Black |

Expander side of A: lines 2-8 go to panel jacks with no expander IC on them. If any A line is
later normalled into an expander circuit (slew, S&H), it enters through at least 100kΩ (BF 3.6).
The r5 re-order of A stays an owner option, decided by the BT-9 crosstalk check (BF Q14).

**Gate level note (Provisional, BF 3.5):** the CD40106 gate output (5V) reaches the Pico only
through the 22k / 33k divider on the expander (about 2.95 V high at a 5.0 V CD40106 supply).
No 5 V net touches a Pico GPIO. The CD4049UBE is not used on the gate path, because its
datasheet says its inputs clamp to VCC (TI SCHS046L p17).

---

## 3. DB-9 B — Digital + Essential CV (Expander ↔ MicroBrute)

From BF section 2.2. DB-9 B carries UART TX, UART RX, Filter CV, VCA CV and grounds only.
No supply rail and no I²C on this cable. Rule applied: the UART pair at one end, each CV pin
surrounded only by ground pins, no CV pin next to a digital pin.

Connector face (insert numbering; neighbour geometry UNVERIFIED until BF BT-7):

```
   top row     [1 UART TX]-[2 GND]-[3 VCA CV]-[4 GND]-[5 FILTER CV]
   bottom row        [6 UART RX]-[7 GND]-[8 GND]-[9 GND]
```

| Pin | Signal | Direction | Series R | Protection / Notes | Wire Color |
|-----|--------|-----------|----------|---------------------|------------|
| 1 | UART TX (Pico GP0 → LPC RXD1, section 5.4) | Expander → MB | 1kΩ at the Pico (expander board) + 1kΩ at the LPC (MB board) | GP0 high-impedance until GP1 reads high (BF 3.1). LPC UART choice UNVERIFIED (audit B01) | White |
| 2 | GND | — | — | Guard; TP72 star and expander star | Black |
| 3 | VCA CV In (to TP10) | Expander → MB | 10kΩ at the expander output + 100kΩ on the MB board | BAT85 to +12V_BRK and from -12V_BRK at the node after the 100kΩ; 1 nF to GND | Purple |
| 4 | GND | — | — | Guard | Black |
| 5 | Filter CV In (to TP26) | Expander → MB | 10kΩ at the expander output + 100kΩ on the MB board | As pin 3 | Blue |
| 6 | UART RX (LPC TXD1 → Pico GP1, section 5.4) | MB → Expander | 1kΩ at the LPC (MB board) + 1kΩ at the Pico (expander board) | GP1 is a fault-tolerant RP2040 pin (BF 3.1) | Yellow |
| 7 | GND | — | — | Guard | Black |
| 8 | GND | — | — | Guard | Black |
| 9 | GND | — | — | Star return | Black |

Freed pins: against the old map (1 TX, 2 RX, 3 SDA, 4 SCL, 5 Filter, 6 VCA, 7 +12 V, 8 -12 V,
9 GND), the two I²C pins and the two rail pins are freed and all carry ground (BF 2.2). Series
resistors sit on the board side of each connector (solder cup or first board pad), never in the
cable. Whether the synth's own 220kΩ / 100kΩ sit after TP26 / TP10 is UNVERIFIED (E-18); the extra
100kΩ may reduce CV depth (BF 3.3, bench check BT-4; fallback 47kΩ).

**Migrated to MB panel (no longer in DB-9 B):**

| Original DB-9 signal | Where it goes now |
|----------------------|-------------------|
| Resonance CV In  | New 3.5 mm jack on MB panel — wires internally to a TL072 voltage-to-current stage → vactrol LED on breakout (audit S37; sense resistor depends on the owned vactrol's LED rating, UNVERIFIED, BF Q2) |
| Sync In          | Use existing MB back-panel Sync In jack — no new drilling |
| Gate In          | Use existing MB back-panel Gate In jack — no new drilling |
| Ext Audio In     | Use existing MB back-panel Audio In jack — no new drilling |

**Cable spec:** two shielded 9-conductor cables (not ribbon), one per connector. Maximum length:
1 m working figure, UNVERIFIED until BF BT-6 (cable capacitance) and BT-1 (UART edges). Braid
bonded at the MicroBrute end only (section 11). A molded off-the-shelf cable bonds the braid at
both hoods and must be modified or built (BF 4.2).

**Crosstalk mitigation:** (1) shielded cables, braid at the MB end only; (2) each CV pin on B has
only ground neighbours; (3) the series resistors in the table below; (4) both cables bundled and
short. Pin-number order alone does not separate lines: on a D-sub, pin 6 sits between 1 and 2,
7 between 2 and 3, 8 between 3 and 4, 9 between 4 and 5 (audit S42, BF 2.1).

### Per-line series resistors and back-feed (copied from BF 3.8)

The expander (rack) and the synth can be powered at different times. Power states:

| State | Expander (rack, Pico) | Synth (MicroBrute, breakout, LPC) |
|---|---|---|
| S0 | off | off |
| S1 | on | off |
| S2 | off | on |
| S3 | on | on (either order; includes the power-up transient of whichever side starts second) |

| Line | Source | Destination | Series R | Protection | Powered-side assumption |
|---|---|---|---|---|---|
| B:1 UART TX | Pico GP0 | LPC P0.16 RXD1 (pin 63) | 1k expander + 1k MB | Firmware: GP0 high-Z until GP1 high | Pico never drives into an unpowered LPC |
| B:6 UART RX | LPC P0.15 TXD1 (pin 62) | Pico GP1 | 1k MB + 1k expander | GP1 fault tolerant; pull-down | LPC may drive while Pico is off: exceeds Table 622 abs max, relies on Table 614 FT, provisional (BT-2) |
| B:5 Filter CV | Expander op-amp | TP26 | 10k expander + 100k MB | 2x BAT85 to +/-12V_BRK, 1 nF | Either side may be off |
| B:3 VCA CV | Expander op-amp | TP10 | 10k expander + 100k MB | 2x BAT85 to +/-12V_BRK, 1 nF | Either side may be off |
| A:1 Gate | MB CD40106 (5 V) | Gate jack; Pico FT GPIO | 1k MB; 22k / 33k divider expander | Divider; no expander pull-up | Either side may be off |
| A:2 Pitch | Stock pitch buffer | Jack | 220 ohm MB | - | - |
| A:3-A:8 | MB followers | Jacks | 1k MB | >= 100k into any expander circuit | Synth may drive while rack is off |
| Clock IN | Rack jack | GP21 | 100k | 2x CD4049UB on 3V3, 100k pull-down | Rack domain only |
| Clock OUT | GP22 | Rack jack | 1k | 2x CD4049UB on 3V3 | Rack domain only |

Notes (BF 3.1-3.3): the UART needs no divider and no level shifter (both ends 3.3 V; LPC2361 VIH
2.0 V, datasheet Table 5 p34), so the old "1kΩ+2kΩ divider OR CD4049UBE" option is deleted (audit
S30). CV back-feed is bounded, not zero: in S1 up to about 89 µA flows into the unpowered breakout
rail through 110kΩ (acceptance BT-3: unpowered rails below about 0.3 V). Every value above is a
design value subject to the bench checks BT-1 to BT-5 in BF section 6.2. A PC817-isolated UART is a
documented alternative only (BF 3.9: realistic at 4800-9600 baud, UNVERIFIED; owner question Q20).

---

## 4. Clock Wiring (internal to the expander)

Both clock jacks and the Pico are on the expander, in the rack domain. **No clock cable runs
between the MicroBrute and the expander** (it would be a second ground tie; audit N08).

| Wire | From | To | Notes |
|------|------|----|-------|
| Clock Out | Pico GP22 (pin 29) | CD4049UB section → second section → 1kΩ → expander CLK OUT jack | 3.3V logic. Mis-patch tolerance of the 4049 output UNVERIFIED (BF Q16) |
| Clock In | Expander CLK IN jack → 100kΩ pull-down to GND → 100kΩ series → CD4049UB section (VCC = Pico 3V3) → second section | Pico GP21 (pin 27) | The RP2040 pin only sees the 4049 output (0-3.3 V). Bench check BF BT-11 |

The four buffer sections use one of the three owned CD4049UBE packages (BF 3.7). Ground strategy: section 11.

---

## 5. Internal MicroBrute Wiring

### 5.1 Test Point Taps — Rear Board (CU17002 v.B3)

All taps use 24AWG wire, soldered to test point pad.

| Test Point | Signal | ~Vpp | Series R | Destination |
|------------|--------|------|----------|-------------|
| TP94 | Sawtooth (raw) | ~10V | 1kΩ | TL074 A +in → DB-9 A:7 |
| TP93 | Square (raw) | ~10V | 1kΩ | TL074 B +in → DB-9 A:8 |
| TP124 | Triangle (raw) | ~10V | 1kΩ | TL072 +in (2× gain) → body jack |
| TP102 | Sub oscillator | ~10V | 1kΩ | Body jack (if installed) |
| TP109 | Metalizer (raw) | ~10V | 1kΩ | Body jack (if installed) |
| TP83 | Gate | level UNVERIFIED (E-09) | 10kΩ, 1 nF to GND at the CD40106 pin, no pull-up | 2× CD40106 → 1kΩ → DB-9 A:1 (Provisional, BF 3.4) |
| TP70 | +12V | — | Rail protection (section 5.3) | Breakout power |
| TP71 | -12V | — | Rail protection (section 5.3) | Breakout power |
| TP72 | GND | — | — | Breakout star ground |

### 5.2 Test Point Taps — Front Board (CU17001)

| Test Point | Signal | Notes | Series R | Destination |
|------------|--------|-------|----------|-------------|
| TP19 | VCF Output | Steiner-Parker out | 1kΩ | TL074 D +in → DB-9 A:6 |
| TP30 | VCO Mix (pre-filter, TP30_MIXER_OUT) | AudioOut | 1kΩ | TL074 C +in → DB-9 A:5 |
| TP10/TP11 | VCA CV inject | CV1/CV2, 100kΩ internal per TPV (R25); whether that 100kΩ is in series at TP10 is UNVERIFIED (E-18) | 100kΩ + clamp (section 3) | From DB-9 B:3 |
| TP26 | Filter CV inject | via R67 (220kΩ) per TPV; position of that resistor UNVERIFIED (E-18) | 100kΩ + clamp (section 3) | From DB-9 B:5 |
| TP5 | Envelope 2 Out | | 10kΩ | TL072 A +in → DB-9 A:3 |
| Mod matrix | LFO | Normalled switching jack | 10kΩ | TL072 B +in → DB-9 A:4 |
| Mod matrix | Envelope | Normalled switching jack | 10kΩ | Alternate to TP5 |

### 5.3 Power Taps

The breakout takes power **only** from the synth's TP70 / TP71 / TP72. Nothing powers it from the
cable, and no synth 5 V or 3V3 is tapped (TP56 is "per original doc" only, TP141 is the 5 V
precision reference, P4 pin 5 is the LPC's own +3V3ARM; audit B09).

| Source | Wire | Destination |
|--------|------|-------------|
| TP70 (+12V) | 22AWG Red | Rail protection → 10µF bulk → breakout +12V_BRK |
| TP71 (-12V) | 22AWG Blue | Rail protection → 10µF bulk → breakout -12V_BRK |
| TP72 (GND) | 22AWG Black | Breakout star ground; every DB-9 ground pin by its own short lead (BF 4.1) |
| Local +5V | — | Owned 78L05 from +12V_BRK, for the CD40106 only. Provisional (BF 3.4, audit decision 3, owner has not confirmed) |

Rail protection is open (audit conflict C12): an owned BAT85 per rail, or a 4.7-10Ω series
resistor. The 1N5817 used in older drawings is a 20 V / 1 A part (not 40 V; DATASHEETS (e)) and is
not owned. If a diode is used on -12 V, its **cathode goes to the TP71 / -12 V side and its anode to
the breakout rail** (audit B15). The 100µF parts in older drawings are not owned: use 2-4× owned
10µF / 63 V in parallel (BF 1.4). Synth rail capacity for the breakout load is UNVERIFIED (audit E-04).

### 5.4 LPC Bridge Wiring (replaces direct MIDI)

The bridge is the only description of the LPC side of the UART in this document; other sections refer here.

Pico speaks a custom framed protocol over its UART0 at 115200 baud to the LPC2361's **UART1:
P0.15 / TXD1 (LQFP pin 62) and P0.16 / RXD1 (LQFP pin 63)** (LPC2361 data sheet Rev. 03, Table 3,
p6). **UNVERIFIED** pending the Phase 0 continuity check (audit section 4 item 7): the stock firmware
uses SSP0/SPI, which shares these pins, so they may be wired to something on the board. Do not write
"confirmed" until that check passes. Fallback only if those pins are taken: the ISP UART (UART0,
LQFP pins 98/99), with the ISP conflict handled. Pins 96 and 97, given in older drawings, are
VDD(3V3) and VSS (data sheet p12): never probe or wire there.

The lines cross DB-9 B pins 1 and 6 (section 3), with the Pico on the expander, not inside the
MicroBrute case. The LPC firmware (modified via .mbf re-encryption) translates protocol messages
into internal MIDI SysEx, avoiding the 31250-baud MIDI path entirely. The UART wires are installed
in Phase 3 but unused until the Phase 6 bridge firmware (audit N17).

| From | To | Notes |
|------|----|-------|
| Pico GP0 (UART0 TX) | 1kΩ → DB-9 B:1 → 1kΩ → LPC2361 P0.16 / RXD1 (pin 63) | No divider, no level shifter (both 3.3 V) |
| LPC2361 P0.15 / TXD1 (pin 62) | 1kΩ → DB-9 B:6 → 1kΩ → Pico GP1 (UART0 RX) | GP1 fault tolerant |
| Shared GND | DB-9 B:2, B:4, B:7, B:8, B:9 | TP72 star (MB) and expander star |

**Protocol frame:** `0xAA · msg_type · counter · payload_len · payload[…] · xor_checksum`

The XOR checksum is the bitwise XOR of all bytes from `msg_type` through the
last payload byte (excluding the leading `0xAA` and the checksum itself).
Receivers compute and verify; bad frames are silently dropped. Both sides
(`firmware/pico/midi.py` and `firmware/lpc2361/include/pico_comm.h`) implement
identical framing.

### 5.5 (Removed)

Dropped by owner decision c (2026-10-17). Nothing on the MicroBrute panel uses I²C, and no I²C crosses the DB-9 cable.

### 5.6 EFFIGY Pair Header — SHELVED

SHELVED (owner decision b, 2026-10-17): the EFFIGY I²C pairing is kept as an idea for another
project and is not part of this build. No rear JST-XH header is fitted, and nothing is designed
around it. GP2, GP3 and GP11 are free, reserved (section 1). The protocol document
`docs/MACROBRUTE_EFFIGY_BRIDGE.md` and `firmware/pico/effigy_bridge.py` are archived as they are.

---

## 6. Panel Mods — Jacks (3)

| ID | Mod | Type | PCB Work | Wiring |
|----|-----|------|----------|--------|
| B1 | VCF Insert | 3.5mm switched | **Remove R23** (100kΩ) | Tip=VCA side, Ring=VCF side, Sleeve=GND. Normal: path closed. Inserted: breaks VCF→VCA |
| B2 | Metalizer Insert | 3.5mm switched | **Remove R216** (120kΩ) | Tip=wavefolder input, Ring=triangle output. Normal: triangle feeds wavefolder |
| B3 | VCA CV Input | 3.5mm mono | None | Direct wire to TP10 (a 100kΩ is in the circuit per TPV, UNVERIFIED, E-18). External VCA control |

---

## 7. Panel Mods — Toggles (3)

| ID | Mod | Switch | PCB Work | Wiring |
|----|-----|--------|----------|--------|
| B4 | Envelope Bypass | SPDT mini | None | Bridge D4+D5 (TS4148RY) in EnvDest circuit. OFF=stock. ON=full-range envelope to filter |
| B5 | Metalizer Boost | SPDT mini | None | Switch R216 between stock 120kΩ and 20kΩ alternate. Harder wavefolder drive |
| B6 | VCA Drone | SPDT mini | None | +12V → 100kΩ → TP10 (VCA CV). OFF=stock. ON=VCA always open |

---

## 8. Touch Bolts (8 designed → 6 to be selected after Phase 0 testing)

All bolts: M3 brass, 6mm panel hole, 18–20mm spacing between bolts.
Wiring: PCB point → safety R → brass bolt. Body capacitance/resistance to GND.

The table below lists all 8 designed bend points. Final selection of 6
happens after Phase 0 bench testing — pick the most musically useful and
least destructive on real hardware.

| ID | Name | PCB Point | Safety R | Effect | Intensity | Risk |
|----|------|-----------|----------|--------|-----------|------|
| T1 | PITCH | R309 area (near blue trimmers, rear) | 10kΩ | Pitch vibrato/detune | 4/5 | 1/5 |
| T2 | CRUNCH | C111 (wavefolder stage 3) | 4.7kΩ | Metalizer folding sweep | 5/5 | 2/5 |
| T3 | WAH | Filter CV input (Steiner-Parker) | 22kΩ | Manual filter sweep | 4/5 | 2/5 |
| T4 | DISTORT | Brute Factor feedback path | 15kΩ | Feedback → self-oscillation | 5/5 | 3/5 |
| T5 | HARM | C107 + C106 (wavefolder 1+2, dual bolt) | 10kΩ each | Cross-coupled harmonics | 5/5 | 2/5 |
| T6 | GATE | Metalizer output→input (feedback) | 1kΩ | Closes metalizer feedback loop | 5/5 | 4/5 |

**Reserve bends** (swap if above underperform in breadboard test):
- #5 Envelope Decay: ADSR cap area, 33kΩ, pluck-to-swell (3/5 intensity)
- #7 LFO Speed: LFO timing network, 47kΩ, tremolo/vibrato rate (3/5 intensity)

---

## 9. Breakout Board (Internal, ~90×50mm stripboard)

A buffer-only board powered from the synth (section 5.3). The Pico, the RGB LED and its drivers
live on the expander, so the old Pico header, LED transistors and 3.3 V level shifter are removed
from the breakout (audit S12, S13).

### ICs and Functions

| IC | Package | Function | Power |
|----|---------|----------|-------|
| U1 TL074 | DIP-14 | 4× waveform buffer (Saw, Sqr, Mix, VCF) | ±12V_BRK |
| U2 TL072 | DIP-8 | Env/LFO follower, triangle 2× gain, vactrol V-to-I driver. Four jobs on a two-section part: IC choice open (audit S17, conflict C10) | ±12V_BRK |
| U3 CD40106 | DIP-14 | Gate Schmitt trigger, 2 gates in series so A:1 follows TP83 polarity; unused inputs tied to GND (Provisional, BF 3.4) | +5V local |
| 78L05 | TO-92 | Local +5V for U3 only (Provisional, BF 3.4) | from +12V_BRK |

### Connector Headers

| Header | Pins | Connects To |
|--------|------|-------------|
| J_PWR | 3 | +12V, -12V, GND from TP70 / TP71 / TP72 only |
| J_IN | 8 | Flying leads from MB test points |
| J_OUT | 9 | DB-9 A solder cups |
| J_CV_IN | to re-derive (audit N22) | DB-9 B solder cups: VCA CV (B:3), Filter CV (B:5), grounds |

The UART lines (B:1, B:6) run from the DB-9 B cups through the MB-side 1kΩ resistors to the LPC
(section 5.4); they do not use the breakout's op-amps.

---

## 10. Expander (Eurorack — width OPEN: 17 HP or about 20 HP)

The expander hosts the Pico, the user interface (main OLED + encoder + tap button + RGB LED),
the I/O between MicroBrute and the rack, and three analog utilities: **slew limiter, LFO and
Sample & Hold**. The LFO and the S&H are standalone rack utilities: no synth cabling, rack power
only (decided 2026-10-16). Noise, mult and attenuverter stay out.

**Width: OPEN** until the owner measures the blank (decision e). 17 HP (the repo panel file is
87 mm, with mounting holes 79 mm apart, both UNVERIFIED against the A-100 spec; audit S53, E-22) or
about 20 HP (101.3 mm; audit S54). Plan both layouts. Depth behind the panel UNVERIFIED (E-23).

**Power (rack only):** Behringer CP1A 16-pin bus: -12 V @ 1 A on pins 1-2 (red stripe), GND on
pins 3-8, +12 V @ 1 A on pins 9-10, **+5 V @ 0.5 A on pins 11-12**, pins 13-16 not used (CP1A QSG
p15, p20; DATASHEETS (f)). The +5 V budget is 0.5 A shared with every other +5 V module in the
rack. Whether the owner's bus slot carries +5 V: UNVERIFIED (BF BT-12). Pico VSYS takes rack +5 V
through a Schottky OR diode (valid per Pico datasheet p21-p22): 1N5817 is a 20 V / 1 A part and is
not owned; an owned BAT85 can stand in (about 4.2 V at 100 mA, inside VSYS 1.8-5.5 V; BF 1.2).

### Hardware utilities on the expander

| # | Module | Footprint | ICs | Jacks | Pots |
|---|--------|-----------|-----|-------|------|
| 1 | Slew limiter | 30×15 mm | TL072 (1 section) + 2× 1N4148 (rise/fall steering; 1N4148 not owned, BF Q4) | 2 (in, out) | 1× 1MΩ rate (1MΩ pots not owned, BF Q6) |
| 2 | LFO | UNVERIFIED | TL072 integrator + CD40106 Schmitt (BF 1.1) | see total below | 1× rate |
| 3 | Sample & Hold | UNVERIFIED | LF398 (not owned, BF Q1) + 10 nF film hold cap (not owned; ceramic unsuitable, LF398 sheet p15) + TL072 buffer | see total below | — |

LF398 PDIP-8 pinout (TI SNOSBI3C p3; DATASHEETS (a)): 1 V+, 2 OFFSET ADJUST, 3 INPUT, 4 V-, 5 OUTPUT,
6 Ch (hold capacitor), 7 LOGIC REFERENCE, 8 LOGIC. Supply ±5 V to ±18 V. Hold-cap leakage 30 pA typ,
200 pA max (LF398-N, p7): with 1 nF that is about 30 mV/s typ droop (derived), hence 10 nF film.
LFO range with 1MΩ and 1µF is about 0.5-50 Hz (derived, audit S60; not measured, E-27); the 10k
series resistor in the integrator is mandatory (audit S61). S&H trigger conditioning is required
(audit S65); its design is open.

### Firmware-only utilities (no hardware on the expander)

| # | Module | Pico GPIO | Pin layout |
|---|--------|-----------|------------|
| 1 | Clock divider (3 outputs, configurable ratios — default ÷2 ÷4 ÷8) | GP16, GP17, GP18 | 3 panel jacks |
| 2 | Programmable aux outputs (4 channels — TAP_DIV / EUCLID / RANDOM / PASSTHRU / PWM_CV) | GP19, GP20, GP6, GP7 | 4 panel jacks |

### Dropped from the expander (covered elsewhere in the rack)

| Originally planned | What replaces it |
|--------------------|------------------|
| Buffered mult (TL074) | User's existing **'07 MULT** module |
| White noise gen (2N3904 + TL072) | User's existing **NOISE** module |
| Attenuverter (TL072 + center-detent pots) | User's existing **MMI Matrix** mixer covers the routing role |
| Manual gate button (CD40106) | Tap button on the expander now does double duty — short press = tempo, long-hold = manual gate |
| Clock divider chip (CD4024) | **Replaced by firmware** — 3 GPIO outputs at configurable ratios |

### Expander panel layout (top to bottom)

| Row | Element | Notes |
|-----|---------|-------|
| Title strip | "MACROBRUTE" silkscreen | — |
| 1 | Main OLED — 0.96" SSD1306 (size/interface UNVERIFIED, BF Q22) | I²C0 @ 0x3C, the only device on I²C0 |
| 2 | HW-040 encoder + tap button + RGB LED | Encoder = menu nav · Tap = tempo/gate · RGB = status |
| 3 | Clock IN, Clock OUT jacks | 3.5 mm panel jacks (type UNVERIFIED, BF Q8) |
| 4 | Clock divider outputs ÷2, ÷4, ÷8 | Firmware-driven (GP16/17/18) |
| 5 | Slew IN, Slew OUT, RATE pot | Analog |
| 6 | LFO outputs + RATE pot | Analog, standalone |
| 7 | S&H IN, TRIG, OUT | Analog, standalone |
| 8 | Aux 1, Aux 2, Aux 3, Aux 4 | Programmable, PWM-capable |

Rows 6-7 are a placeholder order: the layout depends on the 17 HP vs 20 HP decision.

**Total panel jacks: at least 16, and 2 pots** (audit S52: the existing set is clock I/O × 2,
divider outs × 3, slew × 2, aux × 4 = 11 jacks and 1 pot; the old "14" was an arithmetic error;
LFO + S&H raise the minimum to 16 jacks and 2 pots) — plus holes for OLED / encoder / tap and 1 RGB LED.

**Behind the panel:** Pico on a small sub-board, Pico VSYS filter (Schottky OR diode + bulk from
owned 10µF parts + 100nF), I²C0 pull-ups for the main OLED, the CD4049UB clock buffers (section 4),
the 22k / 33k gate divider (section 2), and 2× DB-9 connectors for the link to MicroBrute, with the
expander-side shells isolated from the panel by insulating shoulder washers (not owned, BF Q10;
section 11).

---

## 11. Ground Strategy

Single rule (BF 4.1): **exactly one ground connection between the synth and the rack — the cable
ground conductors** (A:9; B:2, B:4, B:7, B:8, B:9), all running between the same two star points.

- **MicroBrute star: TP72.** Every cable ground pin and the breakout ground go to TP72 by their own
  short wires, not through the breakout's ground strip (audit N13). The breakout takes power only
  from TP70 / TP71 / TP72.
- **Expander star:** where rack 0 V enters at the 16-pin header. Every cable ground pin, the Pico
  GND and all expander circuit grounds meet there.
- **No other synth-to-rack path:** no separate clock cable (section 4), no chassis or panel bond
  between the two cases, no USB on the Pico while the cables are connected (section 1, BF 4.3).
- **Shield (BF 4.2):** each cable's braid is bonded to its connector shell at the MicroBrute end
  only, and that MB-side panel shell is wired with a short lead to TP72. At the expander end the
  braid is cut back and insulated inside the hood, and the expander panel connector's shell is
  isolated from the aluminium panel with insulating shoulder washers. The shield never carries
  signal return. Shell-to-panel continuity: UNVERIFIED (E-15, BT-8).
- Both cables are bundled and kept short so the small loops between the ground conductors stay
  small. Adapter earth status (class II or not) is UNVERIFIED (audit N06).
- **No capacitor in series with any ground pin.** The old "100 nF in series with DB-9 GND" fix
  removes the DC ground reference for CV, gate and UART (audit S23) and is withdrawn.

**Fallback ladder (owned parts only, in order of cost; BF 4.5).** Do each step only if hum or
noise is still measured after the previous one (BT-9):

1. No parts: confirm the baseline. USB unplugged; no clock cable; cables bundled and short; both adapters on the same mains strip; measure with each cable unplugged in turn to locate the loop.
2. No parts: re-wire any ground that does not go to its star by its own lead; confirm no case-to-case contact.
3. No parts: swap the shield bond to the expander end and compare; keep whichever measures lower (the swapped expander shell gets a short lead to the expander star; compare the MB shell lead to TP72 in place and removed).
4. Owned resistor kit plus two BAT85 (conditional): on the expander, break the ground bundle from the expander star with 10Ω, bypassed by 100 nF in parallel and two anti-parallel BAT85. Keeps the DC reference. All 10 owned BAT85 are allocated, so this step needs two freed (audit C12, BF Q3). Recheck BT-2, BT-3, BT-5 afterwards.
5. Owned TL072 and resistors: dedicate one B ground pin (for example B:8) as a no-current ground-sense wire from TP72 and use it as the reference of difference-amplifier receivers on the expander's audio inputs. Needs matched resistors (1 % parts not owned, BF Q5).
6. Owned isolation transformer (46.9/82.4Ω windings) on the single worst audio line only, after its characterisation (E-29). It passes no DC, so never on CV, gate or UART.

---

## 12. Potential Expansions

### 12A. Signals Not on DB-9 (Would Need Additional Cable)

These signals exist at MB test points but have no DB-9 pin allocated:

| Signal | Source | Why Useful | Priority |
|--------|--------|------------|----------|
| Triangle Out | TP124 | Raw triangle waveform (2× gained on breakout) | HIGH — route to body jack instead |
| Sub Out | TP102 | Sub oscillator | MEDIUM — body jack |
| Metalizer Out | TP109/110 | Metalizer pre/post mix | MEDIUM — body jack |
| Velocity CV | DAC channel | Hidden velocity output | LOW — requires LPC RE |
| Mod Wheel CV | DAC Ch C | Mod wheel position | LOW — requires LPC RE |
| PWM CV In | PW summing | External pulse width control | MEDIUM — requires 39kΩ series R |
| Glide Out | TP53 | Portamento CV | LOW |
| Brute Factor CV | TP4 | Direct feedback path control | MEDIUM — partially covered by T4 touch bolt |

**Body jacks** (3.5mm, mounted on MB panel, no DB-9 needed):
Good candidates for Triangle, Sub, and Metalizer since they only need
a buffer + jack, no round-trip to expander.

### 12B. Additional Touch Bends (Beyond Current 6)

| # | Name | PCB Point | Safety R | Notes |
|---|------|-----------|----------|-------|
| 5 | Envelope Decay | ADSR cap area | 33kΩ | Reserve — swap if T1-T6 underperform |
| 7 | LFO Speed | LFO timing R network | 47kΩ | Reserve — manual LFO rate |
| — | VCO Sync Grind | VCO reset comparator | 22kΩ | Untested — needs breadboard validation |
| — | Sub Octave Glitch | Sub flip-flop clock | 10kΩ | Untested — may cause tuning issues |
| — | PWM Manual | Pulse width circuit | 15kΩ | Partially overlaps knob function |

### 12C. Additional Panel Mods (Tier 2 — Breadboard Test First)

| Mod | Wiring | Decision Criteria |
|-----|--------|-------------------|
| Pico DAC → Filter | Free Pico pin as PWM DAC → RC filter → summing node (see note) | Does PWM-filtered CV track accurately enough? |
| Envelope Inversion | TL072 inverting amp on envelope path | Worth the extra op-amp section? |
| Metalizer Feedback Pot | 100kΩ pot across wavefolder feedback path | Better than touch bolt T6? May replace it |
| Brute Factor CV | External CV → 100kΩ → feedback path | Overlaps T4, but CV-controllable |

**PWM slice note (audit S02):** RP2040 PWM slice = (GP >> 1) & 7, channel = GP & 1. GP26 is slice 5
channel A, the same channel as GP10 (LED_MODE, 1 kHz): **GP26 cannot be used as a PWM DAC** while
GP10 drives the mode LED. GP27 is slice 5 channel B and would be tied to GP10's 1 kHz slice
frequency. GP28 is slice 6 channel A, **the same channel as GP12** (channel = GP & 1, slice = (GP >> 1) & 7),
so the two share one duty value if both are ever PWM; GP12 is a plain input (tap button), so GP28 is
usable as PWM while it stays that way. A pin used as PWM cannot also be read as ADC. A Pico PWM output reaching the MicroBrute would also need a
cable pin, and DB-9 B has none free for signals (section 3).

### 12D. LPC2361 Firmware Bridge (Phase 6)

| Feature | Implementation |
|---------|----------------|
| UART bridge | Pico GP0/GP1 (UART0) ↔ LPC2361 UART1, as in section 5.4 (UNVERIFIED pending the continuity check) |
| ISP detection | Check P2.10 — if LOW, Pico stays passive (ISP mode active) |
| Protocol | Custom serial protocol for parameter query/set |
| SysEx proxy | Pico intercepts/modifies SysEx before forwarding to LPC |
| Free flash | 68KB available at 0xEDB8-0x1FFFF for custom code |
| Ghidra | Project at `macrobrute.gpr`, 427 functions, 107+ labels |

### 12G. Future GPIO Expansion

6 free pins (owner decision g, BF section 5):

| GPIO | Physical pin | Note | Type (RP2040 datasheet) |
|------|--------------|------|-------------------------|
| GP2 | 4 | Was EFFIGY I²C1 SDA (shelved) | Digital IO (FT) |
| GP3 | 5 | Was EFFIGY I²C1 SCL (shelved) | Digital IO (FT) |
| GP11 | 15 | Was EFFIGY INT (shelved). Candidate for the gate input (BF 3.5) | Digital IO (FT) |
| GP26 | 31 | PWM slice 5A shared with GP10 (12C) | Digital IO / ADC0, not FT, diode to IOVDD (Pico p20) |
| GP27 | 32 | — | Digital IO / ADC1, not FT |
| GP28 | 34 | — | Digital IO / ADC2, not FT |

Each expansion below must fit in those 6 pins; they do not all fit at once.

| Expansion | GPIOs Needed | Notes |
|-----------|-------------|-------|
| Gate input (Pico mirror of A:1) | 1 digital (FT) | GP11 suggested (BF 3.5); not assigned in config.py |
| Touch plate scanning (4ch) | 3 ADC + 3 digital (mux control) | CD4051 multiplexer; uses all 6 pins |
| DSO channel select | 3 digital | CD4051 address lines |
| Additional LEDs | 1-2 digital | Expander status |
| I2C peripherals | 2 (SDA/SCL) | GP2/GP3 (I²C1). DAC, sensors, etc. |
| Second encoder | 3 digital | Expander-side control |

If the owner's main OLED turns out to be SPI only (BF Q22), it would take GP2 and GP3 (SPI0 SCK /
MOSI) plus DC, RST and CS from the same free set.

---

## 13. Signal Flow (Post-Mod)

```
VCO ──┬── Saw ──────── [1kΩ] ── TL074 A ── [1kΩ] ── DB-9 A:7 ── Expander: SAW jack
      ├── Square ────── [1kΩ] ── TL074 B ── [1kΩ] ── DB-9 A:8 ── Expander: SQR jack
      ├── Triangle ──── [1kΩ] ── TL072 (2×) ──────── Body jack (not on the DB-9)
      ├── Sub ────────── [1kΩ] ────────────────────── Body jack (if installed)
      └── Metalizer ──── [1kΩ] ────────────────────── Body jack (if installed)
           │
           ├── [B2 Insert jack] ── (break point)
           │
       VCO Mix (TP30_MIXER_OUT) ── [1kΩ] ── TL074 C ── [1kΩ] ── DB-9 A:5 ── Expander: MIX jack
           │
      Steiner-Parker VCF ◄── Filter CV In (DB-9 B:5, 10kΩ + 100kΩ + clamp → TP26)
           │                ◄── Touch T3 WAH (22kΩ)
           │
      VCF Out (TP19) ── [1kΩ] ── TL074 D ── [1kΩ] ── DB-9 A:6 ── Expander: VCF jack
           │
           ├── [B1 VCF Insert jack] ── (break point)
           │
      VCA ◄── VCA CV In (DB-9 B:3, 10kΩ + 100kΩ + clamp → TP10)
          ◄── B3 VCA CV jack (TP10)
          ◄── B6 Drone toggle (+12V → 100kΩ → TP10)
           │
      Gate (TP83) ── [10kΩ] ── CD40106 ×2 ── [1kΩ] ── DB-9 A:1 ── Expander: gate jack + 22k/33k divider → Pico FT GPIO
           │
      Envelope ── [B4 Bypass toggle] ── TL072 A ── [1kΩ] ── DB-9 A:3
      LFO ── TL072 B ── [1kΩ] ── DB-9 A:4
           │
      Brute Factor ◄── Touch T4 DISTORT (15kΩ)
      Metalizer ◄── Touch T2 CRUNCH (4.7kΩ), T5 HARM (10kΩ×2), T6 GATE (1kΩ)
      Pitch ◄── Touch T1 PITCH (10kΩ)
      Resonance ◄── Vactrol (MB panel Resonance CV jack → TL072 V-to-I → LED+LDR ∥ RP13)
```

---

## 14. Component Inventory (Purchased)

Bought locally in Kaunas, April 2026, plus the owner's additions of 2026-10-17 (BF section 1).
This is the only list with a Have status; `docs/hardware/MACROBRUTE_BOM.md` and the shopping list
are purchase lists. The owner has further parts not yet listed (BF Q18).

| Part | Qty | Status |
|------|-----|--------|
| TL074C | 4 | ✓ Have |
| TL072IP | 6 | ✓ Have |
| CD4051 | 2 | ✓ Have (no role in the decided design) |
| CD40106 | 3 | ✓ Have |
| BF245C | 5 | ✓ Have |
| LDR04 | 4 | ✓ Have (for a home-made vactrol, only if the owned vactrols do not suit) |
| Vactrols | "some" | ✓ Have (owner 2026-10-17); part number and LED rating UNVERIFIED (BF Q2) |
| BAT85 | 10 | ✓ Have (substitutes for BAT54S); all 10 allocated (BF 1.2, Q3) |
| 78L05 | 4 | ✓ Have |
| 100nF ceramic | 20 | ✓ Have |
| 1µF ceramic | 5 | ✓ Have (dielectric unknown; not for timing or hold) |
| 1nF ceramic | 5 | ✓ Have (CV-input and TP83 filters; NOT for S&H) |
| 10µF/63V electrolytic | 10 | ✓ Have (used in place of 100µF: 2-4 in parallel per rail) |
| Resistor kit (through-hole) | — | ✓ Have (owner 2026-10-17); series, power rating and the values 220R, 1k, 2k, 4.7k, 10k, 22k, 33k, 100k, 10R, 560R, 680R, 1M UNVERIFIED (BF Q5) |
| 100kΩ pots | 4 | ✓ Have |
| 3.5mm jacks | 25 | ✓ Have (type UNVERIFIED, BF Q8) |
| Raspberry Pi Pico | 1 | ✓ Have; variant UNVERIFIED (docs say Pico WH; package says "Raspberry Pi Pico"; another description says "Pico H"), owner to confirm (BF Q21) |
| 0.96" SSD1306 OLED (main) | 1 | ✓ Have; size, controller and interface (I²C vs SPI) UNVERIFIED, owner to confirm (BF Q22) |
| 0.91" SSD1306 128×32 OLED | 1 | ✓ Have (spare; strip OLED dropped) |
| 1.3" SH1106 OLED | 1 | ✓ Have (spare) |
| KY-040 / HW-040 encoder | 1 | ✓ Have (owner 2026-10-17) |
| VGA HD-15 connectors | 2 | ✓ Have (rejected for this project → spare) |
| DB-9 connectors | 2 (earlier list) / "several" (owner 2026-10-17) | ✓ Have; count, gender and flange UNVERIFIED (BF Q9) |
| DSO138 oscilloscope | — | Moved to `spinoffs/dso138-desktop/` |
| JF-33 PCB | — | Moved to `spinoffs/jf33-eurorack/` |
| CD4049UBE | 3 | ✓ Have (expander clock I/O buffers, section 4) |
| Isolation transformer | 1 | ✓ Salvaged (46.9/82.4Ω); turns ratio and bandwidth UNVERIFIED (E-29) |
| Arduino Nano | 1 | ✓ Have (no role) |
| Assortment kit (resistors, capacitors, transistors, diodes, LEDs, trim pots) | — | ✓ Have; exact types and values UNVERIFIED (BF Q18) |

**IC assortment (owner photo, 2026-10-17), all Have:** PT2399 ×3, LM393 ×10, ICL7660S ×2,
PC817 optocoupler ×20, UC3842AN ×5, LM339 ×10, NE555 ×20, UC3843AN ×5, NE5532 ×5, LM358 ×10,
ULN2003AN ("UL2003AN") ×5, LM386 ×5, LM324 ×10, ULN2803APG ×5, TDA2030A ×2, TDA2822D ×5, JRC4558 ×10.
None is an LF398 equivalent. Possible uses are in BF 1.1a (for example PC817 for the documented
isolated-UART alternative, BF 3.9).

### Still Need

From BF section 1 (Missing parts). Nothing here is bought without the owner's approval.

| Part | Qty | Source | For |
|------|-----|--------|-----|
| LF398 (LF398N, DIP-8) | 1 | TME | Sample & Hold — no owned equivalent (BF Q1) |
| 10 nF film hold cap (polystyrene / polypropylene) | 1 | TME | S&H hold cap (BF Q1; ceramic unsuitable) |
| Film cap for LFO timing (1 µF, or 4.7-10 µF) | 1 | — | LFO (BF Q6) |
| 1MΩ pots | 3 | AliExpress | LFO rate, slew rise/fall (BF Q6) |
| 1N4148 | 2 | — | Slew-limiter steering, unless in the assortment kit (BF Q4) |
| 3.5 mm panel jacks (Thonkiconn-type) | as needed | Thonk | Only if the owned 25 do not suit (BF Q8) |
| Eurorack 16-pin keyed header + ribbon | 1 | Thonk | Expander power (BF Q11) |
| DB-9 panel connectors, 2 shielded 9-core cables with hoods | 4 connectors needed in total (owned count UNVERIFIED), 2 cables | — | DB-9 A and B links (BF Q9) |
| Insulating shoulder washers | as needed | — | Expander-side DB-9 shells (BF Q10) |
| RGB LED (common cathode), 6 mm tactile button | 1 each | — | Expander UI (BF Q12) |
| Stripboard, IC sockets, hook-up wire | — | — | All boards (BF Q13) |
| 100k trimmers | — | — | Aux-out trims, or fixed resistors (BF Q7) |
| Brass M3 bolts | 6 | Local | Touch bolt contacts (later phase) |
| SPDT mini toggles | 3 | Local/AliExpress | Panel mods B4-B6 (later phase) |

Not needed any more: LM7805 (78L05 owned), CD4024 (firmware dividers), 2N3904 (LED drivers deleted,
vactrol via TL072), 1N5817 (an owned BAT85 stands in, BF 1.2), ferrite beads (omit, or 10Ω + 10µF), BAT54S, BSS138.
