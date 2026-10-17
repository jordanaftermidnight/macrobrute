# MACROBRUTE PROJECT — Complete Bill of Materials

**Project:** MicroBrute Deep Modification + Pi Pico Expansion Controller
**Author:** jordanaftermidnight
**Version:** 1.2 — 2026-10-17 (reconciled with the project audit)

> **2026-10-17 revisions** (sources: audit `docs/superpowers/reviews/2026-10-16-project-audit.md`,
> back-feed and hum design note `docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md` = "BF",
> `docs/DATASHEETS.md`, `docs/MACROBRUTE_CONNECTION_MAP.md`):
> - **Power is split.** The expander runs only from the rack (Behringer **CP1A**: -12 V @ 1 A,
>   +12 V @ 1 A, +5 V @ 0.5 A). The MB-side breakout runs only from the synth (TP70/TP71/TP72).
>   No supply rail crosses the DB-9 cable. Pico VSYS takes rack +5 V through a Schottky OR diode
>   + bulk + 100 nF; no LM7805 is needed.
> - **Expander scope:** slew limiter, LFO and Sample & Hold (LF398) as hardware utilities, plus
>   firmware dividers, clock I/O and 4 aux outs. **CD4024 dropped** (clock division is firmware).
>   Noise, buffered mult and attenuverter stay out (covered by existing rack modules).
> - **Width OPEN:** 17 HP or about 20 HP, until the owner measures the blank.
> - **Connector:** 2× DB-9, CONFIRMED by the owner (2026-10-17); 2× shielded 9-conductor DB-9 cables (not ribbon); DB-9 B carries UART TX/RX,
>   Filter CV, VCA CV and grounds only. **No I²C on the cable.** The 0.91" strip OLED is dropped and
>   the EFFIGY 5-pin JST-XH header is shelved.
> - **Owned parts only:** the Have/Missing table below (from BF section 1) is the ownership record.
>   Rows in Parts 1 and 2 that are not named there are Missing. Items marked "owner to confirm" are
>   open owner questions (Pico variant, whether the 0.96" SSD1306 has arrived, DB-9 count); they are not decided here.
> - **Later owner decisions (2026-10-17):** the main OLED baseline is the owner's 1.3" 7-pin SPI module (owner ruling; chip SSD1306 or SH1106 and pin order UNVERIFIED: read the module; the 4-pin I²C module is wired into a TD-3 and not available); kit transistors and diodes from the owner's pasted inventory are Have (card contents UNVERIFIED), including 2N3904 and 1N5819 (a possible stand-in for the 1N5817, UNVERIFIED part); LF398 stays the S&H default.

---

## OWNED vs MISSING (Have / Missing)

Source: BF section 1 and `docs/MACROBRUTE_CONNECTION_MAP.md` section 14 (the only list with a Have
status before this table). The owner has further parts not yet listed (BF Q18). A part not in this
table is Missing, even where it is likely in a drawer.

| Part | Qty | Status | Used for / note |
|------|-----|--------|-----------------|
| Raspberry Pi Pico | 1 | Have, **variant owner to confirm** (docs say WH; package says no W; another description says H) | Expander controller. Nothing here uses wireless (BF Q21) |
| 1.3" 7-pin SPI OLED (chip SSD1306 or SH1106 and pin order UNVERIFIED: read the module) | 1 | Have | Expander main display, baseline (owner ruling 2026-10-17, BF Q22): SPI0 SCK GP2, MOSI GP3, DC GP4, RES GP5, CS GP11. Larger than the 0.96" panel cutout; bears on the open expander width |
| 1.3" 4-pin I²C OLED | 1 | Have, not available | Wired into a TD-3 |
| 0.96" SSD1306 OLED | 1 | **Owner to confirm** (may not have arrived) | Alternative only: as an I²C module it needs GP4/GP5 (OLED DC/RES), so re-pinning |
| 0.91" SSD1306 128×32 | 1 | Have, no longer used | Strip OLED dropped; spare |
| KY-040 / HW-040 encoder | 1 | Have | Expander encoder |
| TL074C | 4 | Have | Breakout U1; expander outputs |
| TL072IP | 6 | Have | Breakout U2, V-to-I, slew, LFO, S&H buffer |
| CD40106 | 3 | Have | Breakout gate stage; LFO Schmitt |
| CD4049UBE | 3 | Have | Expander clock IN/OUT buffers |
| CD4051 | 2 | Have | No role in the decided design (only the owned-parts S&H alternative: charge injection UNVERIFIED, supply TO DESIGN, abs max 20 V) |
| 78L05 | 4 | Have | Breakout-local +5 V for the CD40106 (Provisional) |
| BF245C JFET | 5 | Have | No role |
| Vactrol(s) | "some" | Have (type and LED rating unknown, BF Q2) | Resonance CV |
| LDR04 | 4 | Have | Home-made vactrol only if needed |
| Isolation transformer | 1 | Have (salvaged, 46.9/82.4 Ω) | Hum ladder last step |
| Arduino Nano | 1 | Have | No role |
| IC assortment: PT2399 ×3, LM393 ×10, ICL7660S ×2, PC817 10-20 (photo label ×20, about 10 in the owner's later list; owner to confirm), UC3842AN ×5, LM339 ×10, NE555 ×20, UC3843AN ×5, NE5532 ×5, LM358 ×10, ULN2003AN ×5, LM386 ×5, LM324 ×10, ULN2803APG ×5, TDA2030A ×2, TDA2822D ×5, JRC4558 ×10 | as listed | Have | None is an LF398 equivalent. PC817 is the optional isolated-UART part (BF 3.9) |
| BAT85 | 10 | Have | CV clamps (4), Pico VSYS (1), expander rails (3), breakout rails (2): all 10 allocated (BF Q3) |
| 100 nF ceramic | 20 | Have | Decoupling |
| 1 µF ceramic | 5 | Have (dielectric unknown) | Not for timing or hold |
| 1 nF ceramic | 5 | Have | CV and gate filters; NOT for S&H |
| 10 µF / 63 V electrolytic | 10 | Have | 2-4 in parallel per rail in place of 100 µF |
| Resistors, through-hole kit | — | **Have, values to confirm** (series, power rating, and the values 220R, 1k, 2k, 4.7k, 10k, 22k, 33k, 100k, 10R, 560R, 680R, 1M; BF Q5) | All resistor rows below |
| Assortment kit (capacitors, transistors, diodes, LEDs, trim pots) | — | Have, exact types UNVERIFIED (BF Q18) | Rows not named in the next rows stay Missing until the card is read |
| 2N3904, 2N3906, S8050, S8550, 2N5401, 2N5551 | 10+ each | Have (owner's pasted inventory; card contents UNVERIFIED) | 2N3904 is OWNED. No role in the decided design |
| 1N4148 | 25+ | Have (same inventory, UNVERIFIED; BF Q4) | Slew-limiter steering; may replace BAT85 in hum-ladder step 4 (provisional) |
| 1N5819 (40 V Schottky) | 10 | Have (same inventory); datasheet not in `datasheets/`, UNVERIFIED | May serve where a 1N5817 was wanted (Pico VSYS OR diode, rail protection); provisional, frees BAT85 (BF 1.2) |
| 1N5822 | 5 | Have (same inventory, UNVERIFIED) | No role |
| 1N270 germanium | 2 | Have (same inventory, UNVERIFIED) | No role |
| 100 kΩ pots | 4 | Have | Expander controls |
| 3.5 mm jacks | 25 | Have, type unknown (BF Q8) | Expander and MB panel jacks |
| DB-9 connectors | "several" per owner 2026-10-17 (earlier list: 2) | Have, **count / gender / flange owner to confirm** (BF Q9, E-32) | 4 panel connectors are needed in total |
| VGA HD-15 connectors | 2 | Have, rejected | Spare (the VGA line in a pasted inventory was an error; DB-9 are confirmed) |
| **LF398 (LF398N, DIP-8)** | 1 | **Missing — genuine purchase** | Expander S&H, the default (BF Q1). Owned-parts alternative: CD4051 + TL072 + film hold cap (charge injection UNVERIFIED, supply TO DESIGN) |
| **10 nF film (polystyrene / polypropylene) hold capacitor** | 1 | **Missing — genuine purchase** | LF398 hold cap; ceramic is unsuitable (LF398 sheet p15) |
| Film capacitor for LFO timing (1 µF, or 4.7-10 µF) | 1 | Missing, owner decision (BF Q6) | LFO |
| 1 MΩ pots | 3 | Missing, owner decision (BF Q6) | LFO rate, slew rise/fall |
| 1N5817 | 1 | Missing; **20 V part, not 40 V** (DATASHEETS (e)) | Only the Pico VSYS path needs a real one; an owned 1N5819 (UNVERIFIED part) or BAT85 can stand in (BF 1.2) |
| 100k trimmers | — | Missing (BF Q7) | Aux-out trims, or fixed resistors |
| Eurorack 16-pin keyed header + ribbon | 1 | Missing (BF Q11) | Expander power |
| DB-9 connectors (to reach 4 panel + cable ends), 2 shielded 9-core cables with hoods | — | Missing (BF Q9) | A and B links; ribbon is not acceptable |
| Insulating shoulder washers | — | Missing (BF Q10) | Expander-side DB-9 shells |
| RGB LED (common cathode), 6 mm tactile button | 1 each | Missing (BF Q12) | Expander UI |
| Stripboard, IC sockets, hook-up wire | — | Not on the owned list (BF Q13) | All boards |
| 100 µF / 25 V, 100 µF / 10 V, 47 µF electrolytics | — | Missing | Use 2-4× 10 µF / 63 V in parallel instead |
| Ferrite beads | — | Missing | Omit, or 10 Ω + 10 µF |
| BC547, BC557, BSS138, BAT54S, BZX84C3V3, SMBJ12CA, BAT46, LM7805, MCP4725, LM13700, CD4066, CD4024 | — | Missing, **not needed** | Dropped or replaced (BF 1.1, 1.2) |

---

## QUICK COST SUMMARY

The euro figures below predate the Have/Missing table and the scope change; they are not recomputed. Most Part 1 and Part 2 lines are owned or no longer needed (see the table above).

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
| 1 | Raspberry Pi Pico — **Have** (variant owner to confirm; see the table above, no purchase) | 1 | €0 | €0 | — |
| 2 | 1.3" 128x64 7-pin SPI OLED (main baseline, on hand; chip and pin order UNVERIFIED) — also on hand: 0.91" 128×32 SSD1306 (strip OLED dropped), 16×2 1602 I²C LCD; the 1.3" 4-pin I²C is in a TD-3; 0.96" SSD1306 owner to confirm | 1 | €0 | €0 | — |
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
| 9 | 1N5817 Schottky diode (**20 V** 1 A, not 40 V; **Missing**, owned 1N5819 (UNVERIFIED part) or BAT85 can stand in) | 1 | €0.10 | €0.10 | Mouser/TME |
| 10 | ~~Ferrite bead 600Ω@100MHz (0805)~~ — **not needed** (omit, or 10 Ω + 10 µF) | — | — | — | — |
| 11 | 100nF MLCC capacitor 0805 | 10 | €0.05 | €0.50 | Mouser/TME |
| 12 | 10µF MLCC capacitor 0805 | 4 | €0.15 | €0.60 | Mouser/TME |
| 13 | ~~BAT54S dual Schottky (SOT-23)~~ — **Have BAT85 ×10** instead (two per clamp) | — | — | — | — |
| 14 | ~~3.3V Zener diode (BZX84C3V3)~~ — **not needed** (audit B17) | — | — | — | — |

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
| 21 | ~~BSS138 N-MOSFET (SOT-23)~~ — **not needed** (UART is 3.3 V to 3.3 V, no level shifter) | — | — | — | — |
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
| 31 | MCP4725 I2C DAC breakout (12-bit); needs 2 free Pico pins, none free now (only GP26-28, and I²C would take 2 of them) | 2 | €3.00 | €6.00 | Adafruit/AliExpress |
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

### Resistors (1/4W Metal Film 1%) — Have (owner kit); values to confirm (BF Q5)

The owned through-hole kit covers these rows; 1 % parts are not assumed. Older docs used 10 MΩ for the TL074 input bias; 1 MΩ replaces it (audit N11).

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
| 24 | 1µF | Film | 4 | €0.30 | €1.20 | LFO timing (1 µF or 4.7-10 µF film; owner decision, BF Q6). The S&H hold capacitor is a 10 nF film part (row 24a) |
| 24a | 10nF | Film (polystyrene / polypropylene) | 1 | €0.30 | €0.30 | LF398 hold cap — **Missing, genuine purchase** |
| 25 | 10µF | Electrolytic 25V | 10 | €0.08 | €0.80 | Power filtering |
| 26 | 100µF | Electrolytic 25V | — | — | — | **Missing; use 2-4× owned 10 µF/63 V in parallel instead** |
| 27 | 4.7µF | Film | 1 | €0.40 | €0.40 | Portamento original (spare) |

### Semiconductors

| # | Component | Qty | Unit € | Total € | Purpose |
|---|-----------|-----|--------|---------|---------|
| 28 | TL072 dual op-amp (DIP-8) | 4 | €0.45 | €1.80 | Buffers, mixers |
| 29 | TL074 quad op-amp (DIP-14) | 2 | €0.60 | €1.20 | Multi-channel processing |
| 30 | ~~LM13700 dual OTA (DIP-16)~~ — **dropped** | — | — | — | — |
| 31 | ~~CD4066 quad bilateral switch (DIP-14)~~ — replaced by the owned CD4051 where a switch is wanted; the decided S&H uses an **LF398** (row 31a), so neither is needed | — | — | — | — |
| 31a | **LF398N sample-and-hold (DIP-8) — Missing, genuine purchase** (pinout: DATASHEETS (a)) | 1 | €— | €— | TME |
| 32 | CD4017 decade counter (DIP-16) | — | — | — | **Dropped** — clock division now in Pico firmware (3 GPIO outputs, configurable ratios) |
| 33 | CD4024 7-stage counter (DIP-14) | — | — | — | **Dropped** — clock division now in Pico firmware |
| 34 | ~~BC547 NPN transistor~~ — **not needed** (noise dropped) | — | — | — | — |
| 35 | ~~BC557 PNP transistor~~ — **not needed** | — | — | — | — |
| 36 | ~~2N3906 PNP transistor~~ — **not needed** | — | — | — | — |
| 37 | 1N4148 signal diode (**Have, 25+**, owner's inventory, UNVERIFIED) | 20 | €0.03 | €0.60 | Protection, clipping |

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

**Superseded.** The earlier table here (SPI OLED on GP16-20, CV outputs on GP10-13) predates the
firmware and is removed (audit S04). The canonical source is `firmware/pico/config.py`; the table is
mirrored in `docs/MACROBRUTE_CONNECTION_MAP.md` section 1 and `schematics/pico_pinout.md`. Free pins:
GP26-GP28 only (ADC-capable, not fault tolerant); GP2, GP3 and GP11 are the SPI main OLED.

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
| TP56 | Internal gate (the test-points file lists it as Gate In; another doc calls it +5VNUM: UNVERIFIED, never use it as a +5 V tap, audit B09) | Front | Gate signal |
| TP70 | +12V | Rear | Analog positive rail |
| TP71 | -12V | Rear | Analog negative rail |
| TP72 | GND | Rear | Ground reference |

### Power Distribution

Two independent chains; no supply crosses the DB-9 cable (only ground is shared).

```
EXPANDER (rack only)                          BREAKOUT (synth only)
CP1A 16-pin bus                               MicroBrute TP70 (+12 V), TP71 (-12 V), TP72 (GND)
  ├─ +5 V (pins 11-12, 0.5 A shared)            │
  │    └─► Schottky OR diode (1N5817 not        └─► rail protection (BAT85 or 4.7-10 Ω)
  │         owned; 1N5819/BAT85 stand-in) + bulk            └─► 2-4× 10 µF/63 V ─► +12V_BRK / -12V_BRK
  │         + 100 nF ─► Pico VSYS (pin 39)           └─► owned 78L05 ─► +5 V for the CD40106 only
  │            └─► Pico 3V3 ─► OLED, encoder,            (Provisional, BF 3.4)
  │                CD4049UB clock buffers
  └─ ±12 V ─► slew, LFO, S&H, TL07x
```

### CV Output Circuit (per channel)

```
Pico GPIO (PWM)
    │
    └──► 10kΩ ──┬──► 10kΩ ──┬──► TL072 (+) ──► CV OUT (0-10V)
                │           │
               1µF        100nF   TL072 powered from the rack ±12V (expander aux-out circuit, audit S11)
                │           │     Gain set by feedback resistors
               GND         GND    100kΩ trimmer for calibration
```

---

## PART 6: PURCHASING STRATEGY

### Order 1: TME (EU, fast shipping)
- Only what the Have/Missing table marks as a genuine purchase or owner decision: **LF398N**, the 10 nF film hold capacitor, and (owner decision) the LFO film capacitor. See `MACROBRUTE_SHOPPING_LIST.md`.
- Everything else in this order (TL072/TL074/CD40106/CD4049UBE, resistors, 100 nF, BAT85, transistors) is owned or no longer needed.
- ~~LM13700, CD4066, CD4017, CD4024, BC547, BC557, ferrite beads~~ (2N3904 and 2N3906 are owned, not needed) — **dropped or not needed**

### Order 2: Thonk (UK)
- Thonkiconn jacks (all)
- 9mm pots
- Knobs

### Order 3: AliExpress (China, budget)
- Raspberry Pi Pico — not needed (Have; variant owner to confirm)
- JST-PH connectors
- Wire assortment
- M2/M3 hardware
- Toggle switches
- Breadboard
- (OLED already on hand — 1.3" 7-pin SPI main (chip and pin order UNVERIFIED), spares 0.91" SSD1306, 16x2 1602 LCD; the 1.3" 4-pin I²C is in a TD-3; 0.96" SSD1306 owner to confirm)

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

*Document Version: 1.2*  
*Last Updated: 2026-10-17*  
*Project: MACROBRUTE*
