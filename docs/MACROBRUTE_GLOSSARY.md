# MACROBRUTE Glossary

Acronyms, part codes, and project-specific terms that appear across the
manual. Skim this once if you're new to the synth-DIY / Eurorack world —
the rest of the manual leans on these without re-defining them.

---

## Project parts of speech

| Term | What it means |
|---|---|
| **MACROBRUTE** | This whole project — modified MicroBrute *plus* its 17 HP expander, treated as one instrument. |
| **MicroBrute (MB)** | The stock Arturia MicroBrute analog mono synth this project starts from. |
| **Breakout (board)** | The small buffer-only stripboard mounted *inside* the MB that taps test points, buffers signals, and exposes them via 2× DB-9 connectors on the rear panel. Powered only from the synth (TP70/TP71/TP72). |
| **Expander** | The 17 HP Eurorack module that pairs to the MB through the DB-9 cable. Self-contained — runs only from the rack's ±12 V / +5 V supply; nothing is powered over the DB-9. |
| **Touch bolt** | An exposed brass bolt on the panel that, when touched, completes a circuit-bend (changes pitch / timbre / gating). The 6 selected ones are documented in `touch_bend_specs.md`. |
| **Test point (TP)** | A pre-existing solder pad on the MB rear PCB. Numbered TP1–TP124 in Arturia's reference; this manual uses ~18 of them. See `MACROBRUTE_TEST_POINTS_VERIFIED.md`. |
| **Mod ID (M01…M14)** | The 14 curated panel/electronic mods, indexed in `macrobrute_mod_catalog.md`. |
| **Spinoff** | An idea that was researched but moved out of the canonical project. Currently: the JF-33 analog delay rebuild and the DSO138 oscilloscope. They live in `spinoffs/`. |

---

## MicroBrute architecture

| Term | What it means |
|---|---|
| **Steiner-Parker filter** | The MB's voltage-controlled filter topology — multimode, distinctive snarl, will self-oscillate at high resonance. |
| **Brute Factor** | The MB's signature feedback knob — routes the audio output back into the filter input for distortion / drive. |
| **Metalizer** | The MB's wavefolder — adds harmonics by folding the wave around a CV-controllable threshold. |
| **VCO / VCF / VCA** | Voltage-controlled oscillator / filter / amplifier — the three classic analog synth blocks the MB is built from. |
| **LFO** | Low-frequency oscillator (the modulation source — typically 0.04 to 40 Hz). |
| **ADSR / envelope** | Attack-Decay-Sustain-Release amplitude envelope generator. |
| **CV** | Control voltage — the analog modulation signal standard. MB uses 0–5 V; Eurorack typically uses ±5 V or 1 V/oct for pitch. |
| **Gate** | A binary on/off signal that triggers the envelope (typically 0 V off, 5 V on). |

---

## Connectors + pinouts

| Term | What it means |
|---|---|
| **DB-9** | The 9-pin D-sub connector used between the MB and the expander. Two of them: DB-9 A carries the 8 outputs + GND; DB-9 B carries UART TX/RX, Filter CV, VCA CV and grounds. No supply and no I²C cross the cable. |
| **HP** | "Horizontal pitch", the Eurorack panel-width unit. 1 HP = 5.08 mm. The expander is 17 HP (≈ 86 mm) or about 20 HP (≈ 101 mm); width is open. |
| **GP / GPIO** | General-purpose I/O pin on the Pico. GP4 = GPIO 4. |
| **TP / TP-N** | See "Test point" above. Always followed by a number (TP70 = +12 V, TP72 = GND, etc.). |
| **JF-33 / DSO138** | Spinoff parts no longer in the canonical build. Search "spinoffs" if you care. |

---

## Components by part code

| Part | What it is |
|---|---|
| **TL072 / TL074** | JFET-input op-amps (dual / quad). Used for buffering MB test-point taps and Eurorack-side reception. |
| **CD40106** | Hex Schmitt-trigger inverter. Used for clean gate squaring and as the LFO core in the expander. |
| **CD4051** | 8-channel analog multiplexer. Owned x2, but it has no role in the decided design. |
| **CD4024** | 7-stage binary counter. Dropped: the clock dividers /2, /4, /8 are firmware. |
| **CD4049UBE** | Hex inverting buffer used for the expander's clock IN/OUT buffers on Pico 3V3. Its inputs clamp to VCC (TI SCHS046L p17), so it is not used as the gate level shifter. |
| **74HC74** | Dual D flip-flop. Used in the M08 sub-harmonic divider. |
| **LM358 / LM393** | Op-amp / comparator pair. LM393 (open-collector comparator) is used for M02 active soft sync and M12 audio-rate gate. |
| **LM13700** | Dual operational transconductance amplifier (OTA). Used in M04 Metalizer VCA. |
| **LF398** | Sample-and-hold IC for the expander S&H module (not owned; needs a film hold capacitor). |
| **78L05 / 78L09** | Three-terminal +5 V / +9 V linear regulators in TO-92 packages. |
| **2N3904** | NPN small-signal transistor. Owned (kit, 10+, card contents UNVERIFIED) and not needed by the decided design (LED drivers deleted, vactrol driven by a TL072 stage, noise dropped). |
| **1N4148** | Small-signal silicon switching diode (~0.7 V drop, fast). Used as clamp / mixer diode. Owned (kit, 25+, card contents UNVERIFIED). |
| **1N5817** | Schottky diode, 20 V / 1 A (not 40 V), not owned. Intended for the Pico VSYS path; an owned 1N5819 or BAT85 can stand in. |
| **1N5819** | Schottky diode, 40 V / 1 A. Owned (x10, kit; the part and its datasheet are UNVERIFIED). May serve where a 1N5817 was wanted (provisional). |
| **BAT54S** | Dual Schottky in SOT-23. Not owned; two owned BAT85 take its place as the CV-input clamp to ±supply rails. |
| **Vactrol** | Optocoupler made from an LED + LDR (light-dependent resistor) pair sealed in a black package. Used for smooth, click-free resonance modulation. |
| **MPR121** | Capacitive touch sensor IC (12 channels, I²C). Optional alternative to direct touch bolts on GPIO. |

---

## Microcontrollers + protocols

| Term | What it means |
|---|---|
| **Pico WH** | Raspberry Pi Pico W with pre-soldered headers: the variant the docs assume. The owned variant is UNVERIFIED: owner to confirm (Pico / Pico H / Pico WH; BF Q21); nothing here uses wireless. RP2040, 133 MHz, 264 KB SRAM, 2 MB Flash. Runs MicroPython in this project. |
| **LPC2361** | The MicroBrute's stock CPU. ARM7TDMI core, 72 MHz, 128 KB Flash, 34 KB SRAM. Custom firmware build is optional. |
| **RP2040** | The chip on the Pico (used interchangeably with "Pico" when context is clear). |
| **MicroPython** | Subset of Python that runs on microcontrollers. Used for all Pico firmware in this project. |
| **UART** | Asynchronous serial protocol. Used for Pico ↔ LPC2361 bridge (115 200 baud) and for MIDI (31 250 baud). |
| **I²C** | Two-wire synchronous serial bus (SDA + SCL). Not used in this build: the main OLED is SPI, no I²C crosses the DB-9, and the rear Daisy Seed (EFFIGY) expansion is shelved. |
| **SPI** | Synchronous serial bus with a clock (SCK), data out (MOSI), optional data in (MISO) and a chip select (CS). The main OLED uses Pico SPI0 write-only (SCK GP2, MOSI GP3) plus DC GP4, RES GP5 and CS GP11. |
| **PIO** | RP2040's Programmable I/O — small state machines that handle precise timing-critical I/O without the CPU. Used for the clock-out generator. |
| **PWM** | Pulse-width modulation. Used for LED brightness and for low-resolution analog CV output (filtered to DC). |
| **ADC** | Analog-to-digital converter. Pico has 4 channels @ 12-bit. |
| **DAC** | Digital-to-analog converter. The LPC2361 has a 10-bit DAC; the Pico does not (uses PWM-as-DAC). |
| **ISP** | In-System Programming — the LPC2361's bootloader-mode UART flashing protocol. Used to flash custom firmware without JTAG. |
| **CRP** | Code Read Protection — a one-way fuse on the LPC2361 that, if blown, prevents firmware readback. The stock MB has CRP enabled; custom firmware loads regardless. |
| **JTAG** | Hardware debug interface (5-pin connector). The MB has it populated but unused in this project — printf-over-UART is the debug path. |
| **TinyUSB** | The USB device-class library on the Pico that exposes it as a USB-MIDI device to the host computer. |
| **MIDI / DIN MIDI / USB-MIDI** | Standard music-control protocol (31 250 baud serial). The 5-pin DIN port is on the LPC2361 path; the micro-USB port on the Pico is a separate USB-MIDI device. |

---

## Build / process terms

| Term | What it means |
|---|---|
| **Phase 0 / Phase 1 / …** | The 7 sequential build phases (see `MACROBRUTE_BUILD_PLAN.md`). Phase 0 is non-destructive bench work; Phase 3 is the irreversible panel-cutting step. |
| **Stripboard** | Perfboard with horizontal copper strips already etched on the back. Cheaper than a custom PCB; cut tracks with a 3 mm drill twisted by hand. |
| **Track cut** | A break deliberately made in a stripboard's copper strip — drawn as a red **X** in the layouts. Always verify with a multimeter. |
| **Eurorack** | The dominant modular-synth format (3U panels, ±12 V power, 3.5 mm jacks, 1 V/oct CV). The expander is a Eurorack module. |
| **Brute Factor** | See "MicroBrute architecture" above. |
| **Star ground** | A grounding scheme where every ground wire returns to one central point, instead of daisy-chaining. Used here at TP72. |
| **Decoupling cap** | A small (typically 100 nF ceramic) capacitor placed between an IC's power pin and ground, within ~10 mm of the pin. Filters supply noise. |
| **Bias resistor** | A high-value (typically ≥1 MΩ) resistor that sets the DC operating point of an op-amp input when there's no DC path through the signal source. |
| **Inline series resistor** | A resistor placed in series on a signal path — used here as input protection (limits fault current) and as part of summing networks. |
