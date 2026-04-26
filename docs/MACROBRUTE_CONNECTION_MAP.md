# MACROBRUTE — Complete Connection Map

Every signal, mod, bend, and wire in the system. This is the master
wiring reference for building, debugging, and expanding.

**Connector:** 2× DB-9 (VGA HD-15 rejected — shorts pins 6-8 to GND)
**OLED:** **0.96" SSD1306 I²C 128×64** main display on expander (driver `OLED_I2C` in `firmware/pico/display.py`, `OLED_CHIP="SSD1306"`). Plus a **0.91" SSD1306 128×32** strip on the MB panel sharing the same I²C0 bus at 0x3D. Fallback chips: 1.3" SH1106 (set `OLED_CHIP="SH1106"`), 16×2 1602 I²C LCD.
**MIDI path:** Pico ↔ LPC2361 UART bridge over UART0 @ 115200 baud. LPC firmware relays as internal MIDI SysEx. No direct 31250-baud MIDI from Pico.
**Firmware:** Pico WH MicroPython (9 modules), LPC2361 ARM7 (stock + planned bridge extension)

---

## 1. Pico WH GPIO Allocation

Canonical source: `firmware/pico/config.py`. Update this table AND that file together.

| GPIO | Pico Pin | Function | Direction | Notes |
|------|----------|----------|-----------|-------|
| GP0 | 1 | UART0 TX → LPC2361 | OUT | 115200 baud, via DB-9 B:1, ferrite at Pico end |
| GP1 | 2 | UART0 RX ← LPC2361 | IN | 115200 baud, via DB-9 B:2 |
| GP2 | 4 | I²C1 SDA → EFFIGY | I/O | Rear JST-XH pin 1, 4.7kΩ pull-up to 3V3 |
| GP3 | 5 | I²C1 SCL → EFFIGY | OUT | Rear JST-XH pin 2, 100 kHz |
| GP4 | 6 | I²C0 SDA (shared) | I/O | Main OLED 0x3C (expander) + strip OLED 0x3D (MB panel via DB-9 B:3) |
| GP5 | 7 | I²C0 SCL (shared) | OUT | 100 kHz on shared bus (longer cable to MB strip OLED) |
| GP6 | 9 | Aux output 3 | OUT | Programmable: tap-div / euclidean / random / passthrough / PWM-CV |
| GP7 | 10 | Aux output 4 | OUT | Programmable, same modes as GP6 |
| GP8 | 11 | RGB LED R · Clock tick | OUT | PWM, owned exclusively by `leds.LEDManager` |
| GP9 | 12 | RGB LED G · Gate active | OUT | PWM |
| GP10 | 14 | RGB LED B · Mode/Pair | OUT | PWM |
| GP11 | 15 | EFFIGY INT | IN | Pull-up to 3V3, falling-edge IRQ from EFFIGY (rear JST-XH pin 3) |
| GP12 | 16 | Tap button | IN | Pull-up; short = tap tempo, long-hold = manual gate |
| GP13 | 17 | Encoder switch | IN | Pull-up, short = select, long = back |
| GP14 | 19 | Encoder CLK (A) | IN | Pull-up, IRQ on both edges |
| GP15 | 20 | Encoder DT (B) | IN | Pull-up |
| GP16 | 21 | Clock divider out 1 | OUT | Firmware-driven, default ÷2 (configurable) |
| GP17 | 22 | Clock divider out 2 | OUT | Default ÷4 |
| GP18 | 24 | Clock divider out 3 | OUT | Default ÷8 |
| GP19 | 25 | Aux output 1 | OUT | Programmable (PWM-capable) |
| GP20 | 26 | Aux output 2 | OUT | Programmable |
| GP21 | 27 | Clock input | IN | Pull-down, external sync IRQ |
| GP22 | 29 | Clock output | OUT | Master clock to expander panel jack (3.3V) |
| GP26 | 31 | ADC0 (spare) | IN | Reserved for future touch plate sensing |
| GP27 | 32 | ADC1 (spare) | IN | Reserved |
| GP28 | 34 | ADC2 (spare) | IN | Reserved |
| 3V3 | 36 | 3V3 out | PWR | OLED + encoder + I²C pull-ups |
| VSYS | 39 | +5V input | PWR | From Eurorack CP1A +5V via 1N5817 + 100µF + 100nF |
| GND | 3,8,13,18,23,28,33,38 | Ground | — | Multiple pins, star return at TP72 |

**No truly spare GPIO.** All exposed Pico GP pins are now allocated.
GP23/24/25 are RP2040-internal (SMPS / VBUS / on-board LED) and not exposed.

**Tap button modes:** short press (< 400 ms release) → tap tempo. Held press
(≥ 400 ms) → manual gate (RGB-G LED full-bright while held; gate signal also
goes to LPC bridge as a synthetic note-on/off pair).

**RGB LED color semantics:**

| Channel | Pin | Meaning |
|---------|-----|---------|
| Red     | GP8 | Brief flash on each clock tick |
| Green   | GP9 | Solid while gate is high (manual or external) |
| Blue    | GP10 | Mode indicator: dim = solo, bright = paired with EFFIGY |

Mixed colors arise naturally — yellow = clock + gate, cyan = gate + paired,
magenta = clock + paired, white = all three.

**USB-MIDI:** Pico micro-USB enumerates as a USB-MIDI class device via TinyUSB
(`firmware/pico/usbmidi.py`). Orthogonal to the LPC bridge — gives the host
DAW a "Macrobrute Pico" MIDI port. Pico does NOT drive 5-pin DIN MIDI; that
stays on the stock 6N138 → LPC2361 UART0 path inside the MicroBrute.

---

## 2. DB-9 A — Outputs (MicroBrute → Expander)

| Pin | Signal | MB Source | Buffer | Series R | Wire Color |
|-----|--------|-----------|--------|----------|------------|
| 1 | Gate Out | TP83 | CD40106 Schmitt | 10kΩ in + 10kΩ pull-up | White |
| 2 | Pitch CV Out | Rear panel jack | Direct (stock buffer) | — | Yellow |
| 3 | Envelope Out | Mod matrix | TL072 follower | 10kΩ in | Orange |
| 4 | LFO Out | Mod matrix | TL072 follower | 10kΩ in | Green |
| 5 | VCO Mix Out | TP30_MIXER_OUT | TL074 follower | 1kΩ in, 1kΩ out | Blue |
| 6 | VCF Out | TP19 | TL074 follower | 1kΩ in, 1kΩ out | Purple |
| 7 | Saw Out | TP94 | TL074 follower | 1kΩ in, 1kΩ out | Red |
| 8 | Square Out | TP93 | TL074 follower | 1kΩ in, 1kΩ out | Brown |
| 9 | GND | TP72 | — | — | Black |

**Level shifter note:** CD40106 gate output (5V) going to Pico GP needs
CD4049UBE level shifter (powered from 3.3V, accepts >VDD inputs).

---

## 3. DB-9 B — Digital + Power + Essential CV (Expander ↔ MicroBrute)

**Revised pin map (replaces earlier all-CV layout).** DB-9 B now carries the
UART bridge, the I²C0 bus to the strip OLED on the MB panel, two essential CV
inputs that benefit from expander-routed modulation, and ±12V to power the
MB-side breakout op-amps. No third aux cable required.

| Pin | Signal | Direction | Protection / Notes | Wire Color |
|-----|--------|-----------|---------------------|------------|
| 1 | UART TX (Pico GP0) | Expander → MB (LPC P0.16 RXD1) | Ferrite bead at Pico end · 115200 baud · 1kΩ+2kΩ divider OR CD4049UBE level shift | White |
| 2 | UART RX (Pico GP1) | Expander ← MB (LPC P0.15 TXD1) | Ferrite bead at Pico end · 115200 baud · direct (LPC is 3.3V) | Yellow |
| 3 | I²C0 SDA (Pico GP4) | Bidirectional | Pull-up 4.7kΩ to 3V3 (Pico side) · drives strip OLED on MB panel @ 0x3D | Orange |
| 4 | I²C0 SCL (Pico GP5) | Expander → MB | Pull-up 4.7kΩ · 100 kHz max for cable length | Green |
| 5 | Filter CV In | Expander → MB | BAT54S clamp · 220kΩ series · summing node U8A | Blue |
| 6 | VCA CV In | Expander → MB | BAT54S clamp · 100kΩ series · TP10/TP11 | Purple |
| 7 | +12V | Expander → MB breakout | 1N5817 + ferrite · powers MB-side op-amps only | Red |
| 8 | -12V | Expander → MB breakout | 1N5817 + ferrite · op-amp negative rail | Brown/Stripe |
| 9 | GND | shared | Star ground (TP72) · single return path | Black |

**Migrated to MB panel (no longer in DB-9 B):**

| Original DB-9 signal | Where it goes now |
|----------------------|-------------------|
| Resonance CV In  | New 3.5 mm jack on MB panel — wires internally to 2N3904 → vactrol LED on breakout |
| Sync In          | Use existing MB back-panel Sync In jack — no new drilling |
| Gate In          | Use existing MB back-panel Gate In jack — no new drilling |
| Ext Audio In     | Use existing MB back-panel Audio In jack — no new drilling |

**Cable spec:** shielded DB-9 (e.g., quality D-Sub serial cable), shell tied
to shield drain on MB side only. Pin layout deliberately puts digital lines
(1–4) physically apart from the analog CV inputs (5–6), with power and GND
acting as buffers in between.

**Crosstalk mitigation cumulative:** (1) shielded cable, (2) physical pin
separation, (3) ferrite beads on UART/I²C lines at the Pico end, (4) I²C
spec'd at 100 kHz (not 400 kHz). Apply all four — they're cheap and additive.

---

## 4. Clock Wiring (Separate from DB-9)

Routed through rear panel grommet alongside DB-9 cables.

| Wire | From | To | Notes |
|------|------|----|-------|
| Clock Out | Pico GP22 (pin 29) | Expander CLK OUT jack | 3.3V logic |
| Clock In | Expander CLK IN jack | Pico GP21 (pin 27) | Pull-down, IRQ |
| GND | Pico GND | Expander GND | Shield drain |

3-conductor shielded cable, <1m.

**Ground loop warning:** Connect DB-9 shield drain to GND at ONE end only (MicroBrute side). Connecting both ends creates a ground loop that introduces 50/60Hz hum into audio paths. Use star grounding: all grounds converge at MicroBrute TP72, single path to expander.

---

## 5. Internal MicroBrute Wiring

### 5.1 Test Point Taps — Rear Board (CU17002 v.B3)

All taps use 24AWG wire, soldered to test point pad.

| Test Point | Signal | ~Vpp | Series R | Destination |
|------------|--------|------|----------|-------------|
| TP94 | Sawtooth (raw) | ~10V | 1kΩ | TL074 A +in → DB-9 A:7 |
| TP93 | Square (raw) | ~10V | 1kΩ | TL074 B +in → DB-9 A:8 |
| TP124 | Triangle (raw) | ~10V | 1kΩ | TL072 D +in (2× gain) |
| TP102 | Sub oscillator | ~10V | 1kΩ | Body jack (if installed) |
| TP109 | Metalizer (raw) | ~10V | 1kΩ | Body jack (if installed) |
| TP83 | Gate | 0/5V | 10kΩ | CD40106 → DB-9 A:1 |
| TP70 | +12V | — | Ferrite | Breakout power |
| TP71 | -12V | — | Ferrite | Breakout power |
| TP72 | GND | — | — | Breakout star ground |

### 5.2 Test Point Taps — Front Board (CU17001)

| Test Point | Signal | Notes | Series R | Destination |
|------------|--------|-------|----------|-------------|
| TP19 | VCF Output | Steiner-Parker out | 1kΩ | TL074 D +in → DB-9 A:6 |
| TP30 | VCO Mix (pre-filter, TP30_MIXER_OUT) | AudioOut | 1kΩ | TL074 C +in → DB-9 A:5 |
| TP10/TP11 | VCA CV inject | CV1/CV2, 100kΩ internal | — | From DB-9 B:2 |
| TP5 | Envelope 2 Out | | 10kΩ | TL072 A +in → DB-9 A:3 |
| Mod matrix | LFO | Normalled switching jack | 10kΩ | TL072 B +in → DB-9 A:4 |
| Mod matrix | Envelope | Normalled switching jack | 10kΩ | Alternate to TP5 |

### 5.3 Power Taps

| Source | Wire | Destination |
|--------|------|-------------|
| TP70 (+12V) | 22AWG Red | D1 1N5817 → ferrite → breakout +12V rail |
| TP71 (-12V) | 22AWG Blue | D2 1N5817 → ferrite → breakout -12V rail |
| TP72 (GND) | 22AWG Black | Breakout star ground + DB-9 pin 9 |
| +5V rail | 22AWG Orange | D3 1N5817 → Pico VSYS (pin 39) |

### 5.4 LPC Bridge Wiring (replaces direct MIDI)

Pico speaks a custom framed protocol to the LPC2361 over UART0 at 115200 baud,
carried across DB-9 B pins 1/2 (with the Pico now living on the expander, not
inside the MicroBrute case). The LPC firmware (modified via .mbf re-encryption)
translates protocol messages into internal MIDI SysEx, avoiding the 31250-baud
MIDI path entirely and freeing GP4/GP5 for the shared I²C0 bus (main OLED on
the expander + strip OLED on the MB panel).

| From | To | Notes |
|------|----|-------|
| Pico GP0 (UART0 TX) | DB-9 B:1 → LPC2361 P0.16 (RXD1) | Ferrite at Pico · 1kΩ+2kΩ divider OR CD4049UBE |
| LPC2361 P0.15 (TXD1) | DB-9 B:2 → Pico GP1 (UART0 RX) | Ferrite at Pico · direct (LPC is 3.3V) |
| Shared GND | DB-9 B:9 | Single star return at TP72 |

**Protocol frame:** `0xAA · msg_type · counter · payload_len · payload[…] · xor_checksum`

The XOR checksum is the bitwise XOR of all bytes from `msg_type` through the
last payload byte (excluding the leading `0xAA` and the checksum itself).
Receivers compute and verify; bad frames are silently dropped. Both sides
(`firmware/pico/midi.py` and `firmware/lpc2361/include/pico_comm.h`) implement
identical framing.

### 5.5 Strip OLED Wiring (MB panel)

The 0.91" SSD1306 128×32 strip display lives on the MB panel where the
"microbrute" silkscreen sits. It shares the Pico's I²C0 bus with the main
0.96" SSD1306 on the expander (different addresses: 0x3C main, 0x3D strip).

| From | To | Notes |
|------|----|-------|
| Pico GP4 (I²C0 SDA) | DB-9 B:3 → strip OLED SDA | Ferrite at Pico end · pull-up 4.7kΩ to 3V3 |
| Pico GP5 (I²C0 SCL) | DB-9 B:4 → strip OLED SCL | Ferrite at Pico end · pull-up 4.7kΩ to 3V3 |
| MB +5V (local) | Strip OLED VCC | Powered from MB internal 5V — onboard LDO + level shifter on the module |
| TP72 GND | Strip OLED GND | Shared with star ground |

The strip OLED's I²C address jumper must be set to **0x3D** (alt) — verify
on your specific module before mounting; some boards require a small SMD
resistor swap rather than a solder pad jumper.

### 5.6 EFFIGY Pair Header (rear, hidden)

5-pin JST-XH on the rear of the expander, accessed with the case open. Wires
the Pico's I²C1 bus + an INT line to a separately-built EFFIGY Daisy Seed
module. See `docs/MACROBRUTE_EFFIGY_BRIDGE.md` for the protocol.

| Pin | Signal | Pico side |
|-----|--------|-----------|
| 1 | SDA   | GP2 (I²C1 SDA) · 4.7kΩ pull-up to 3V3 |
| 2 | SCL   | GP3 (I²C1 SCL) · 4.7kΩ pull-up to 3V3 |
| 3 | INT   | GP11 input · pull-up to 3V3 · falling-edge IRQ |
| 4 | +3.3V | Pico 3V3 — for header pull-ups only (EFFIGY has its own power) |
| 5 | GND   | Shared reference |

Cable: shielded twisted-pair, < 30 cm. Bus speed: 100 kHz (matches I²C0
speed for the long DB-9 B run).

---

## 6. Panel Mods — Jacks (3)

| ID | Mod | Type | PCB Work | Wiring |
|----|-----|------|----------|--------|
| B1 | VCF Insert | 3.5mm switched | **Remove R23** (100kΩ) | Tip=VCA side, Ring=VCF side, Sleeve=GND. Normal: path closed. Inserted: breaks VCF→VCA |
| B2 | Metalizer Insert | 3.5mm switched | **Remove R216** (120kΩ) | Tip=wavefolder input, Ring=triangle output. Normal: triangle feeds wavefolder |
| B3 | VCA CV Input | 3.5mm mono | None | Direct wire to TP10 (100kΩ already in circuit). External VCA control |

---

## 7. Panel Mods — Toggles (3)

| ID | Mod | Switch | PCB Work | Wiring |
|----|-----|--------|----------|--------|
| B4 | Envelope Bypass | SPDT mini | None | Bridge D4+D5 (TS4148RY) in EnvDest circuit. OFF=stock. ON=full-range envelope to filter |
| B5 | Metalizer Boost | SPDT mini | None | Switch R216 between stock 120kΩ and 20kΩ alternate. Harder wavefolder drive |
| B6 | VCA Drone | SPDT mini | None | +12V → 100kΩ → TP10 (VCA CV). OFF=stock. ON=VCA always open |

---

## 8. Touch Bolts (6 selected from 8 tested)

All bolts: M3 brass, 6mm panel hole, 18-20mm spacing between bolts.
Wiring: PCB point → safety R → brass bolt. Body capacitance/resistance to GND.

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

### ICs and Functions

| IC | Package | Function | Power |
|----|---------|----------|-------|
| U1 TL074 | DIP-14 | 4× waveform buffer (Saw, Sqr, Mix, VCF) | ±12V |
| U2 TL072 | DIP-8 | Env/LFO follower, triangle 2× gain, vactrol driver | ±12V |
| U3 CD40106 | DIP-14 | Gate Schmitt trigger (1 of 6 gates used) | +5V |
| U4 CD4049UBE | DIP-16 | 5V→3.3V level shifter for Pico (1 gate used) | +3.3V |
| Q1-Q3 2N3904 | TO-92 | RGB LED drivers (1kΩ base, 220Ω collector) | — |

### Connector Headers

| Header | Pins | Connects To |
|--------|------|-------------|
| J_PWR | 4 | +12V, -12V, +5V, GND from MB test points |
| J_IN | 8 | Flying leads from MB test points |
| J_OUT | 9 | DB-9 A solder cups |
| J_CV_IN | 6 | DB-9 B solder cups (CV inputs) |
| J_PICO | 12 | Ribbon to Pico WH |

---

## 10. Expander (42HP, Eurorack)

### Module List

| # | Module | Board Size | ICs | Jacks | Pots |
|---|--------|------------|-----|-------|------|
| 1 | Buffered mult (1→3) | 25×15mm | TL074 (3 sections) | 4 | — |
| 2 | White noise | 30×20mm | TL072 (1 section) + 2N3904 | 1 out | — |
| 3 | LFO (tri+sqr) | 40×20mm | TL072 (both sections) | 2 out | 1MΩ rate |
| 4 | Clock divider (/2/4/8) | 30×15mm | CD4024 + CD40106 | 4 (in + 3 out) | — |
| 5 | Sample & Hold | 25×15mm | LF398 | 3 (sig, clk, out) | — |
| 6 | Slew limiter | 30×15mm | TL072 (1 section) | 2 (in, out) | 2× 1MΩ rise/fall |
| 7 | Attenuverter (2ch) | 30×20mm | TL072 (both sections) | 4 (2in, 2out) | 2× 100kΩ center-detent |
| 8 | Manual gate button | 15×10mm | — (or shared CD40106) | 1 out | — |

### Expander Panel Jacks (Patchbay)

**Output jacks (from DB-9 A, buffered):**
Saw, Square, VCO Mix, VCF Out, Gate, Pitch CV, Envelope, LFO

**Input jacks (to DB-9 B, attenuated):**
Filter CV, VCA CV, Resonance CV, Sync, Gate In, Ext Audio

**Utility jacks:**
Noise Out, LFO Tri, LFO Sqr, Clock /2, Clock /4, Clock /8,
S&H Out, Slew Out, Atten Out ×2, Mult Out ×3, Manual Gate

**Total: ~31 Thonkiconn jacks**

---

## 11. Ground Strategy

- **Star ground** at DB-9 connectors (pin 9 on both A and B)
- Single ground path between MicroBrute and Eurorack via DB-9
- Power GND returns through DB-9 B:9
- Shield/chassis ground via DB-9 shell only
- **If hum:** 100nF ceramic in series with DB-9 GND pin
- **If persistent:** Isolation transformer available (46.9/82.4Ω windings)
- **NEVER** connect MB chassis to expander chassis via separate path

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
| Pico DAC → Filter | GP26 ADC as DAC (PWM) → RC filter → summing node | Does PWM-filtered CV track accurately enough? |
| Envelope Inversion | TL072 inverting amp on envelope path | Worth the extra op-amp section? |
| Metalizer Feedback Pot | 100kΩ pot across wavefolder feedback path | Better than touch bolt T6? May replace it |
| Brute Factor CV | External CV → 100kΩ → feedback path | Overlaps T4, but CV-controllable |

### 12D. JF-33 Delay — Separate Eurorack Module

The Joyo JF-33 (PT2399 delay) PCB is extracted and available.
Build as a standalone Eurorack module rather than integrating into MB.

| Feature | Implementation |
|---------|----------------|
| Anti-latch-up | BC337 + 100kΩ/1µF RC (300ms startup delay) |
| Delay Time CV | TL072 → 2N3904 current sink, 1kΩ emitter R (0-5mA range) |
| Eurorack level match | Input: 10kΩ attenuator. Output: TL072 gain stage |
| Feedback CV | Optional: SSI2164 VCA or simple pot |
| Power | +12V from Eurorack bus, onboard 78L05 for PT2399 |
| Panel | 6HP: In, Out, Time CV, Feedback, Mix, Time knob |
| Schematic | `schematics/jf33_cv_control.md` |

**Why separate:** PT2399 is noisy and benefits from isolated power.
Keeping it off the MB PSU avoids clock noise bleeding into VCO.

### 12E. DSO138 Oscilloscope — Separate Eurorack Module

Built DSO138 kit available. Convert to Eurorack signal monitor.

| Feature | Implementation |
|---------|----------------|
| Input protection | BAT54S clamps to ±12V + 1kΩ series R per channel |
| Signal mux | CD4051 (8:1) — select which signal to display |
| Mux channels | Saw, Square, Mix, VCF, Gate, Envelope, LFO, External |
| Mux control | 3-bit from Pico (GP spare) or manual rotary switch |
| Power | +12V → LM7809 → DSO138 (test on raw 12V first) |
| Panel | 10HP: LCD display, input jack, channel select, probe clip |
| Firmware | Optional: DLO-138 (open source, adds serial export) |

**Why separate:** Display is large, needs its own panel real estate.
Better as a utility module than crammed into MB panel.

### 12F. LPC2361 Firmware Bridge (Phase 6)

| Feature | Implementation |
|---------|----------------|
| UART0 bridge | Pico GP0/GP1 ↔ LPC2361 P0.2/P0.3 (TXD0/RXD0) |
| ISP detection | Check P2.10 — if LOW, Pico stays passive (ISP mode active) |
| Protocol | Custom serial protocol for parameter query/set |
| SysEx proxy | Pico intercepts/modifies SysEx before forwarding to LPC |
| Free flash | 68KB available at 0xEDB8-0x1FFFF for custom code |
| Ghidra | Project at `macrobrute.gpr`, 427 functions, 107+ labels |

### 12G. Future GPIO Expansion

With 8 spare GPIOs (GP2,3,6,7,11,23,24,25) + 3 ADC (GP26,27,28):

| Expansion | GPIOs Needed | Notes |
|-----------|-------------|-------|
| Touch plate scanning (4ch) | 3 ADC + 3 digital (mux control) | CD4051 multiplexer |
| DSO channel select | 3 digital | CD4051 address lines |
| Additional LEDs | 1-2 digital | Expander status |
| I2C peripherals | 2 (SDA/SCL) | DAC, sensors, etc. |
| Second encoder | 3 digital | Expander-side control |

---

## 13. Signal Flow (Post-Mod)

```
VCO ──┬── Saw ──────── [1kΩ] ── TL074 A ── [1kΩ] ── DB-9 A:7 ── Expander: SAW jack
      ├── Square ────── [1kΩ] ── TL074 B ── [1kΩ] ── DB-9 A:8 ── Expander: SQR jack
      ├── Triangle ──── [1kΩ] ── TL072 (2×) ──────── Body jack (or spare pin)
      ├── Sub ────────── [1kΩ] ────────────────────── Body jack (if installed)
      └── Metalizer ──── [1kΩ] ────────────────────── Body jack (if installed)
           │
           ├── [B2 Insert jack] ── (break point)
           │
       VCO Mix (TP30_MIXER_OUT) ── [1kΩ] ── TL074 C ── [1kΩ] ── DB-9 A:5 ── Expander: MIX jack
           │
      Steiner-Parker VCF ◄── Filter CV In (DB-9 B:1, 220kΩ)
           │                ◄── Touch T3 WAH (22kΩ)
           │
      VCF Out (TP19) ── [1kΩ] ── TL074 D ── [1kΩ] ── DB-9 A:6 ── Expander: VCF jack
           │
           ├── [B1 VCF Insert jack] ── (break point)
           │
      VCA ◄── VCA CV In (DB-9 B:2, 100kΩ)
          ◄── B3 VCA CV jack (TP10)
          ◄── B6 Drone toggle (+12V → 100kΩ → TP10)
           │
      Gate (TP83) ── [10kΩ] ── CD40106 ── CD4049UBE ── DB-9 A:1 + Pico mirror
           │
      Envelope ── [B4 Bypass toggle] ── TL072 A ── DB-9 A:3
      LFO ── TL072 B ── DB-9 A:4
           │
      Brute Factor ◄── Touch T4 DISTORT (15kΩ)
      Metalizer ◄── Touch T2 CRUNCH (4.7kΩ), T5 HARM (10kΩ×2), T6 GATE (1kΩ)
      Pitch ◄── Touch T1 PITCH (10kΩ)
      Resonance ◄── Vactrol (DB-9 B:3 → 2N3904 → LED+LDR ∥ RP13)
```

---

## 14. Component Inventory (Purchased)

Bought locally in Kaunas, April 2026:

| Part | Qty | Status |
|------|-----|--------|
| TL074C | 4 | ✓ Have |
| TL072IP | 6 | ✓ Have |
| CD4051 | 2 | ✓ Have (replaces CD4066) |
| CD40106 | 3 | ✓ Have |
| BF245C | 5 | ✓ Have |
| LDR04 | 4 | ✓ Have (for vactrols) |
| BAT85 | 10 | ✓ Have (substitutes for BAT54S) |
| 78L05 | 4 | ✓ Have |
| 100nF ceramic | 20 | ✓ Have |
| 1µF ceramic | 5 | ✓ Have |
| 1nF ceramic | 5 | ✓ Have (NOT for S&H — need polystyrene) |
| 10µF/63V electrolytic | 10 | ✓ Have |
| 100kΩ pots | 4 | ✓ Have |
| 3.5mm jacks | 25 | ✓ Have |
| Pico WH | 1 | ✓ Have |
| 0.96" SSD1306 OLED (main) | 1 | ✓ Have |
| 0.91" SSD1306 128×32 OLED (strip on MB panel) | 1 | ✓ Have |
| 1.3" SH1106 OLED (reserved for EFFIGY / fallback) | 1 | ✓ Have |
| HW040 encoder | 1 | ✓ Have |
| VGA HD-15 connectors | 2 | ✓ Have (rejected for this project → spare) |
| DB-9 connectors | 2 | ✓ Have |
| DSO138 oscilloscope | 1 | ✓ Built |
| JF-33 PCB | 1 | ✓ Extracted |
| CD4049UBE | 3 | ✓ Have (level shifter) |
| Isolation transformer | 1 | ✓ Salvaged (46.9/82.4Ω) |

### Still Need

| Part | Qty | Source | For |
|------|-----|--------|-----|
| 1nF polystyrene cap | 1 | TME | S&H hold cap (CRITICAL) |
| LM7809 | 1-2 | Local/TME | DSO138 power |
| LM7805 | 2 | Local/TME | Spares |
| Thonkiconn PJ398SM | ~20 | Thonk | Expander jacks |
| Eurorack 16-pin header | 1 | Thonk | Expander power |
| LF398 | 1 | TME | Sample & Hold |
| CD4024 | 1 | TME | Clock divider |
| 2N3904 | 5-8 | Local/TME | Noise source + LED drivers |
| 1MΩ pots | 3 | AliExpress | LFO rate, slew rise/fall |
| Brass M3 bolts | 6 | Local | Touch bolt contacts |
| SPDT mini toggles | 3 | Local/AliExpress | Panel mods B4-B6 |
