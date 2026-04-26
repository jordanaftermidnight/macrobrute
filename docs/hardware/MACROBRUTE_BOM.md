# MACROBRUTE PROJECT — Complete Bill of Materials

**Project:** MicroBrute Deep Modification + Pi Pico Expansion Controller
**Author:** jordanaftermidnight
**Version:** 1.1 — April 2026 (Phase D refresh)

> **Phase D revisions:** Expander shrunk to 17HP. Behringer **CP1A** is the
> reference Eurorack PSU (±12V + 5V on bus). Pico powered from CP1A +5V via
> 3-part filter (1N5817 + 100µF + 100nF) — no LM7805 needed. **CD4024 dropped**
> — clock division is firmware (3 GPIO outputs). Noise gen, S&H, buffered
> mult, LFO, attenuverter all dropped from the expander BOM (covered by
> existing rack modules — NOISE / RND CV / '07 MULT / Tryfelo / MMI Matrix).
> Slew limiter is the only hardware utility on the expander.
>
> **New connector spec:** 5-pin JST-XH rear header for the EFFIGY pair bus
> (was 4-pin — INT line added). 0.91" SSD1306 strip OLED on MB panel. 2× DB-9
> shielded cables (no aux cable — DB-9 B carries digital + power + 2 CVs).

---

## QUICK COST SUMMARY

| Category | Cost |
|----------|------|
| Pi Pico Expansion Controller | ~€90 |
| Analog Modifications | ~€52 |
| Firmware Development Tools | ~€53 |
| Tools (if buying all new) | ~€365 |
| **GRAND TOTAL (maximum)** | **~€560** |
| **Components Only (you have tools)** | **~€195** |
| **Minimum Viable (basic mods + Pico + firmware)** | **~€195** |

---

## PART 1: RASPBERRY PI PICO EXPANSION CONTROLLER

### Core Hardware

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 1 | Raspberry Pi Pico (standard, NOT W) | 1 | €4.00 | €4.00 | Mouser/Pimoroni |
| 2 | 0.96" 128x64 OLED SSD1306 I²C (main, on hand) + 0.91" 128×32 SSD1306 (strip on MB, on hand) — fallback: 1.3" SH1106 (reserved for EFFIGY), 16×2 1602 I²C LCD (all on hand) | 2 | €0 | €0 | — |
| 3 | J-Link EDU Mini (JTAG debugger) | 1 | €20.00 | €20.00 | Segger/Mouser |

### Connectors & Cables

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 4 | JST-PH 2.0mm 4-pin connector kit | 5 | €0.30 | €1.50 | AliExpress |
| 5 | JST-PH 2.0mm 6-pin connector kit | 3 | €0.40 | €1.20 | AliExpress |
| 6 | 10-pin JTAG ribbon cable 1.27mm | 1 | €2.00 | €2.00 | AliExpress |
| 7 | 28AWG stranded silicone wire (8 colors) | 1 | €8.00 | €8.00 | AliExpress |
| 8 | 22AWG stranded wire (red/black) | 1 | €4.00 | €4.00 | AliExpress |

### Power & Protection

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 9 | 1N5817 Schottky diode (40V 1A) | 2 | €0.10 | €0.20 | Mouser/TME |
| 10 | Ferrite bead 600Ω@100MHz (0805) | 4 | €0.15 | €0.60 | Mouser/TME |
| 11 | 100nF MLCC capacitor 0805 | 10 | €0.05 | €0.50 | Mouser/TME |
| 12 | 10µF MLCC capacitor 0805 | 4 | €0.15 | €0.60 | Mouser/TME |
| 13 | BAT54S dual Schottky (SOT-23) | 2 | €0.20 | €0.40 | Mouser/TME |
| 14 | 3.3V Zener diode (BZX84C3V3) | 2 | €0.10 | €0.20 | Mouser/TME |

### CV Output Circuit (x4 channels)

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 15 | 10kΩ resistor 1% 0805 | 12 | €0.02 | €0.24 | Mouser/TME |
| 16 | 1µF film capacitor (through-hole) | 4 | €0.30 | €1.20 | Mouser/TME |
| 17 | 100nF film capacitor (through-hole) | 4 | €0.15 | €0.60 | Mouser/TME |
| 18 | TL072 dual op-amp (DIP-8) | 2 | €0.50 | €1.00 | Mouser/TME |
| 19 | DIP-8 socket | 2 | €0.15 | €0.30 | Mouser/TME |
| 20 | 100kΩ trimmer pot (Bourns 3296) | 4 | €0.80 | €3.20 | Mouser |

### Level Shifting & Buffering

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 21 | BSS138 N-MOSFET (SOT-23) | 4 | €0.15 | €0.60 | Mouser/TME |
| 22 | 10kΩ resistor 0805 (pull-ups) | 8 | €0.02 | €0.16 | Mouser/TME |
| 23 | 1kΩ resistor 0805 (series protection) | 10 | €0.02 | €0.20 | Mouser/TME |
| 24 | 100Ω resistor 0805 (MIDI current limit) | 2 | €0.02 | €0.04 | Mouser/TME |

### Mounting & Physical

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 25 | M2x6mm brass standoff | 4 | €0.20 | €0.80 | AliExpress |
| 26 | M2x4mm screw | 8 | €0.05 | €0.40 | AliExpress |
| 27 | 3M VHB 5952 tape (small roll) | 1 | €5.00 | €5.00 | Amazon |
| 28 | Kapton tape 10mm width | 1 | €3.00 | €3.00 | Amazon |
| 29 | Heat shrink tubing assortment | 1 | €4.00 | €4.00 | Amazon |
| 30 | 0.5mm clear polycarbonate sheet (A5) | 1 | €3.00 | €3.00 | Amazon |

### Optional / Future Expansion

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 31 | MCP4725 I2C DAC breakout (12-bit) | 2 | €3.00 | €6.00 | Adafruit/AliExpress |
| 32 | PT8211 I2S DAC (16-bit audio) | 1 | €1.50 | €1.50 | AliExpress |
| 33 | Copper tape adhesive (EMI shielding) | 1 | €4.00 | €4.00 | Amazon |

**PICO EXPANSION SUBTOTAL: ~€90**

---

## PART 2: MACROBRUTE ANALOG MODIFICATIONS

### 3.5mm Mono Jacks

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 1 | Thonkiconn PJ398SM switched jack | 8 | €0.50 | €4.00 | Thonk |
| 2 | Thonkiconn PJ301M-12 non-switched jack | 8 | €0.40 | €3.20 | Thonk |
| 3 | 3.5mm panel-mount jack nuts | 16 | €0.05 | €0.80 | Thonk |

### Potentiometers

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 4 | B100K linear 9mm pot | 3 | €0.80 | €2.40 | Thonk/Tayda |
| 5 | B50K linear 9mm pot | 2 | €0.80 | €1.60 | Thonk/Tayda |
| 6 | B10K linear 9mm pot | 2 | €0.80 | €1.60 | Thonk/Tayda |
| 7 | Knobs for 6mm D-shaft (black) | 7 | €0.30 | €2.10 | Tayda |

### Switches

| # | Component | Qty | Unit € | Total € | Source |
|---|-----------|-----|--------|---------|--------|
| 8 | SPDT ON-ON mini toggle (MTS-102) | 4 | €0.60 | €2.40 | Tayda/AliExpress |
| 9 | SPST momentary pushbutton (PBS-110) | 2 | €0.30 | €0.60 | Tayda |
| 10 | DPDT ON-ON mini toggle (MTS-202) | 1 | €0.80 | €0.80 | Tayda |

### Resistors (1/4W Metal Film 1%)

| # | Value | Qty | Unit € | Total € | Purpose |
|---|-------|-----|--------|---------|---------|
| 11 | 100Ω | 5 | €0.02 | €0.10 | MIDI, current limiting |
| 12 | 1kΩ | 15 | €0.02 | €0.30 | Output buffers, protection |
| 13 | 2.2kΩ | 5 | €0.02 | €0.10 | Various |
| 14 | 10kΩ | 20 | €0.02 | €0.40 | Protection, mixing, output |
| 15 | 22kΩ | 10 | €0.02 | €0.20 | Gate mod |
| 16 | 47kΩ | 10 | €0.02 | €0.20 | Various |
| 17 | 100kΩ | 20 | €0.02 | €0.40 | Mixing, CV processing |
| 18 | 120kΩ | 4 | €0.02 | €0.08 | Metalizer insert (R216) |
| 19 | 1MΩ | 5 | €0.02 | €0.10 | Various |
| 20 | 30kΩ | 4 | €0.02 | €0.08 | Metalizer timbre mod |

### Capacitors

| # | Value | Type | Qty | Unit € | Total € | Purpose |
|---|-------|------|-----|--------|---------|---------|
| 21 | 470nF | Film | 2 | €0.25 | €0.50 | Portamento speed mod (C38) |
| 22 | 100nF | Ceramic/MLCC | 20 | €0.03 | €0.60 | Decoupling |
| 23 | 10nF | Film | 10 | €0.10 | €1.00 | Various |
| 24 | 1µF | Film | 4 | €0.30 | €1.20 | Sample & hold |
| 25 | 10µF | Electrolytic 25V | 10 | €0.08 | €0.80 | Power filtering |
| 26 | 100µF | Electrolytic 25V | 4 | €0.12 | €0.48 | Power filtering |
| 27 | 4.7µF | Film | 1 | €0.40 | €0.40 | Portamento original (spare) |

### Semiconductors

| # | Component | Qty | Unit € | Total € | Purpose |
|---|-----------|-----|--------|---------|---------|
| 28 | TL072 dual op-amp (DIP-8) | 4 | €0.45 | €1.80 | Buffers, mixers |
| 29 | TL074 quad op-amp (DIP-14) | 2 | €0.60 | €1.20 | Multi-channel processing |
| 30 | LM13700 dual OTA (DIP-16) | 2 | €1.50 | €3.00 | VCA, VC-LFO rate |
| 31 | CD4066 quad bilateral switch (DIP-14) | 2 | €0.40 | €0.80 | Sample & hold |
| 32 | CD4017 decade counter (DIP-16) | — | — | — | **Dropped** — clock division now in Pico firmware (3 GPIO outputs, configurable ratios) |
| 33 | CD4024 7-stage counter (DIP-14) | — | — | — | **Dropped** — clock division now in Pico firmware |
| 34 | BC547 NPN transistor (TO-92) | 5 | €0.08 | €0.40 | Noise source, comparators |
| 35 | BC557 PNP transistor (TO-92) | 5 | €0.08 | €0.40 | Various |
| 36 | 2N3906 PNP transistor | 2 | €0.10 | €0.20 | Sequencer decoupling |
| 37 | 1N4148 signal diode | 20 | €0.03 | €0.60 | Protection, clipping |

### IC Sockets

| # | Component | Qty | Unit € | Total € |
|---|-----------|-----|--------|---------|
| 38 | DIP-8 socket | 6 | €0.10 | €0.60 |
| 39 | DIP-14 socket | 4 | €0.12 | €0.48 |
| 40 | DIP-16 socket | 4 | €0.15 | €0.60 |

### Circuit Bending / Body Contacts

| # | Component | Qty | Unit € | Total € |
|---|-----------|-----|--------|---------|
| 41 | M4x20mm brass bolt | 8 | €0.15 | €1.20 |
| 42 | M4 brass nut | 8 | €0.08 | €0.64 |
| 43 | M4 nylon insulating washer | 16 | €0.05 | €0.80 |
| 44 | 100kΩ linear potentiometer | 2 | €0.80 | €1.60 |

### MIDI Out Mod

| # | Component | Qty | Unit € | Total € |
|---|-----------|-----|--------|---------|
| 45 | 5-pin DIN panel mount socket | 1 | €1.00 | €1.00 |
| 46 | 6N138 optocoupler (optional MIDI thru) | 1 | €0.80 | €0.80 |

### Prototyping & Mounting

| # | Component | Qty | Unit € | Total € |
|---|-----------|-----|--------|---------|
| 47 | Stripboard 100x50mm | 3 | €1.50 | €4.50 |
| 48 | Breadboard 830 point | 1 | €3.00 | €3.00 |
| 49 | Pin headers 2.54mm male (40-pin) | 5 | €0.20 | €1.00 |
| 50 | Pin headers 2.54mm female (40-pin) | 5 | €0.25 | €1.25 |
| 51 | M3x8mm standoff brass | 10 | €0.15 | €1.50 |
| 52 | M3x6mm screw | 20 | €0.03 | €0.60 |

**ANALOG MODS SUBTOTAL: ~€52**

---

## PART 3: TOOLS & CONSUMABLES

### Essential Tools (if not owned)

| # | Tool | Price € | Source |
|---|------|---------|--------|
| 1 | Soldering station (Pinecil/TS100/Hakko FX888D) | €40-100 | Amazon/AliExpress |
| 2 | Fine soldering tip (0.5mm conical) x2 | €10.00 | Amazon |
| 3 | Hot air rework station (for SMD) | €35.00 | AliExpress |
| 4 | Digital multimeter (with continuity) | €15.00 | Amazon |
| 5 | USB oscilloscope (Hantek 6022BE) | €50.00 | Amazon/AliExpress |

### Fine Work Tools

| # | Tool | Price € | Source |
|---|------|---------|--------|
| 6 | Magnifying headset with LED (3.5x) | €12.00 | Amazon |
| 7 | Precision tweezers set (ESD-safe) | €8.00 | Amazon |
| 8 | Flush cutters (Hakko CHP-170) | €8.00 | Amazon |
| 9 | Wire strippers (AWG 20-30) | €10.00 | Amazon |
| 10 | Desoldering pump (Engineer SS-02) | €15.00 | Amazon |
| 11 | Desoldering wick 2.5mm x2 | €6.00 | Amazon |

### Consumables

| # | Item | Price € | Source |
|---|------|---------|--------|
| 12 | Solder 0.5mm 63/37 (100g) | €8.00 | Amazon |
| 13 | Flux paste (Amtech NC-559-V2) | €8.00 | Amazon |
| 14 | IPA isopropyl alcohol 99% (500ml) | €5.00 | Local pharmacy |
| 15 | ESD wrist strap | €5.00 | Amazon |
| 16 | Silicone soldering mat | €10.00 | Amazon |
| 17 | Label maker (Brother P-Touch) | €25.00 | Amazon |

### Panel Fabrication

| # | Tool | Price € | Source |
|---|------|---------|--------|
| 18 | Step drill bit set (for jack holes) | €12.00 | Amazon |
| 19 | Dremel rotary tool + cutting discs | €40.00 | Amazon |
| 20 | Needle file set | €8.00 | Amazon |
| 21 | Center punch | €5.00 | Amazon |

**TOOLS SUBTOTAL (if buying all): ~€365**

---

## PART 3B: FIRMWARE DEVELOPMENT TOOLS

### JTAG Debugger (Required)

| # | Component | Qty | Price € | Source | Notes |
|---|-----------|-----|---------|--------|-------|
| 1 | **J-Link EDU Mini** | 1 | €20 | Segger/Mouser | Recommended — excellent OpenOCD support |
| 2 | 10-pin JTAG ribbon cable (1.27mm) | 1 | €2 | AliExpress | |
| 3 | 10-pin IDC header (1.27mm) | 2 | €1 | AliExpress | For breakout/adapter |

### ISP Recovery (Backup Method)

| # | Component | Qty | Price € | Source | Notes |
|---|-----------|-----|---------|--------|-------|
| 4 | USB-TTL adapter (3.3V, CP2102) | 1 | €3 | AliExpress | For ISP programming if JTAG fails |
| 5 | Dupont jumper wires | 1 pack | €2 | AliExpress | |

### Debug & Analysis

| # | Component | Qty | Price € | Source | Notes |
|---|-----------|-----|---------|--------|-------|
| 6 | Logic analyzer (8ch, 24MHz) | 1 | €10 | AliExpress | Saleae clone |
| 7 | Oscilloscope probe | 1 | €15 | AliExpress | If you have scope |

### CRP Bypass (Only if Needed)

| # | Component | Qty | Price € | Source | Notes |
|---|-----------|-----|---------|--------|-------|
| 8 | ChipWhisperer Lite | 1 | €200 | NewAE Technology | Only if CRP is enabled |

### Required Software (Free)

| Software | Purpose | Source |
|----------|---------|--------|
| gcc-arm-none-eabi | ARM compiler | apt / ARM website |
| OpenOCD | JTAG/SWD debugger | apt / openocd.org |
| GDB | Debugger | Included with gcc |
| Ghidra | Disassembly/RE | ghidra-sre.org |
| Flash Magic | ISP programmer | flashmagictool.com |
| VSCode + Cortex-Debug | IDE | code.visualstudio.com |

**FIRMWARE TOOLS SUBTOTAL: ~€53 (without CRP bypass) / ~€253 (with CRP bypass)**

---

## PART 4: SOURCING GUIDE

### EU-Based Suppliers (recommended for Lithuania)

| Supplier | Website | Notes |
|----------|---------|-------|
| **TME** | tme.eu | Polish distributor. Best prices, fast EU shipping, Lithuanian interface. **HIGHLY RECOMMENDED** |
| **Mouser EU** | mouser.co.uk / mouser.de | ICs, precision components. Free shipping >€50 |
| **Reichelt** | reichelt.de | German distributor. Good prices, reliable |
| **Thonk** | thonk.co.uk | Eurorack specialist. Best for jacks, knobs, pots. UK but ships EU |
| **Tayda Electronics** | tayda.com | Budget components. Longer shipping but very cheap |
| **Electric Druid** | electricdruid.net | Specialty synth ICs (VCDO, LFO chips) |

### China Suppliers (budget, 2-4 week shipping)

| Supplier | Website | Notes |
|----------|---------|-------|
| **AliExpress** | aliexpress.com | Pi Pico, OLEDs, wire, connectors. Quality varies |
| **LCSC** | lcsc.com | SMD components, PCBs. Owned by JLCPCB |

### Specialty Sources

| Supplier | Website | Notes |
|----------|---------|-------|
| **Pimoroni** | pimoroni.com | Pi Pico, microcontroller accessories |
| **Adafruit** | adafruit.com | Quality breakouts. Ships via Mouser EU |
| **Segger** | segger.com | J-Link EDU Mini official source |
| **Synthcube** | synthcube.com | Synth DIY kits, panels |

---

## PART 5: WIRING REFERENCE

### Pi Pico GPIO Assignment

| Function | GPIO | Physical Pin | Notes |
|----------|------|--------------|-------|
| UART TX → LPC2361 | GP0 | Pin 1 | UART0 TX |
| UART RX ← LPC2361 | GP1 | Pin 2 | UART0 RX |
| OLED SDA (I2C) | GP4 | Pin 6 | I2C0 SDA |
| OLED SCL (I2C) | GP5 | Pin 7 | I2C0 SCL |
| OLED SCK (SPI) | GP18 | Pin 24 | SPI0 SCK |
| OLED MOSI (SPI) | GP19 | Pin 25 | SPI0 TX |
| OLED CS | GP17 | Pin 22 | SPI0 CSn |
| OLED DC | GP16 | Pin 21 | GPIO |
| OLED RST | GP20 | Pin 26 | GPIO |
| CV Output 1 | GP10 | Pin 14 | PWM5 A |
| CV Output 2 | GP11 | Pin 15 | PWM5 B |
| CV Output 3 | GP12 | Pin 16 | PWM6 A |
| CV Output 4 | GP13 | Pin 17 | PWM6 B |
| ADC Input 1 | GP26 | Pin 31 | ADC0 |
| ADC Input 2 | GP27 | Pin 32 | ADC1 |

### MicroBrute Test Points (Key Signals)

| Test Point | Signal | Board | Purpose |
|------------|--------|-------|---------|
| TP93 | Square wave | Rear | VCO square output |
| TP94 | Sawtooth wave | Rear | VCO saw output |
| TP102 | Sub oscillator | Rear | Sub-osc output |
| TP124 | Triangle wave | Rear | VCO triangle output |
| TP109 | Metalizer out | Rear | Wavefolder output |
| TP10/TP11 | VCA CV in | Front | External VCA CV injection |
| TP55 | Pitch CV | Front | Post-portamento CV |
| TP56 | Internal gate | Front | Gate signal |
| TP70 | +12V | Rear | Analog positive rail |
| TP71 | -12V | Rear | Analog negative rail |
| TP72 | GND | Rear | Ground reference |

### Power Distribution

```
MicroBrute +5V Rail (PSU-DIGITAL section)
    │
    └──► 1N5817 Schottky (0.3V drop)
          │
          └──► Pi Pico VSYS (Pin 39)
                │
                ├──► Pico 3V3 OUT ──► OLED VCC
                │
                └──► Pico internal 3.3V regulator
```

### CV Output Circuit (per channel)

```
Pico GPIO (PWM)
    │
    └──► 10kΩ ──┬──► 10kΩ ──┬──► TL072 (+) ──► CV OUT (0-10V)
                │           │
               1µF        100nF   TL072 powered from MicroBrute ±12V
                │           │     Gain set by feedback resistors
               GND         GND    100kΩ trimmer for calibration
```

---

## PART 6: PURCHASING STRATEGY

### Order 1: TME (EU, fast shipping)
- All resistors, capacitors, diodes (including the 3-part Pico filter: 1N5817 + 100µF/10V + 100nF)
- TL072 (slew limiter), TL074 (MB-side buffers), CD40106 (gate Schmitt), CD4049UBE (level shifter)
- BC547, BC557, 2N3906, 2N3904 (vactrol driver, gate buffer)
- IC sockets, ferrite beads, MLCCs
- ~~LM13700, CD4066, CD4017, CD4024~~ — **dropped** (utilities moved to firmware or covered by rack modules)

### Order 2: Thonk (UK)
- Thonkiconn jacks (all)
- 9mm pots
- Knobs

### Order 3: AliExpress (China, budget)
- Raspberry Pi Pico (if Pico WH not already on hand)
- JST-PH connectors
- Wire assortment
- M2/M3 hardware
- Toggle switches
- Breadboard
- (OLED already on hand — 0.96" SSD1306 main, 0.91" SSD1306 strip, 1.3" SH1106 fallback/EFFIGY, 16x2 1602 LCD)

### Order 4: Mouser/Amazon (fills)
- J-Link EDU Mini (or Segger direct)
- Bourns 3296 trimmers
- 3M VHB tape
- Specialty items

### Order 5: Local Hardware Store
- M4 brass bolts/nuts (body contacts)
- Nylon washers
- IPA alcohol

---

## NOTES

- **Buy 20-50% extra** of resistors, capacitors, and diodes — they're cheap and you'll lose some
- **TME** has a Lithuanian language interface and excellent EU shipping
- **Combine orders** to hit free shipping thresholds (Mouser €50, TME €50)
- The **OLED display** is the most critical sourcing item — verify dimensions (75.5 × 19.35 mm PCB) before ordering
- **J-Link EDU Mini** is worth it over cheap clones for JTAG work — much better software support
- Keep the **optional items** (MCP4725 DAC, PT8211, copper tape) for future expansion

---

*Document Version: 1.0*  
*Last Updated: March 2026*  
*Project: MACROBRUTE*
