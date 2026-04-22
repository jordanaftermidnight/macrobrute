# MACROBRUTE CONSOLIDATED SHOPPING LIST
## Ready-to-Order Part Numbers for TME, Mouser, Thonk & AliExpress

**Project:** MACROBRUTE MicroBrute Deep Mod  
**Author:** jordanaftermidnight  
**Date:** March 2026

---

## ORDER STRATEGY

I recommend splitting into 4 orders to optimize shipping:

| Order | Supplier | Contents | Est. Total |
|-------|----------|----------|------------|
| 1 | **TME** (tme.eu) | ICs, resistors, capacitors, diodes, sockets | ~€35 |
| 2 | **Mouser/Farnell** | J-Link, Pico, precision parts | ~€45 |
| 3 | **Thonk** | Jacks, pots, knobs | ~€25 |
| 4 | **AliExpress** | OLED, wire, connectors, hardware | ~€30 |

**Total: ~€135** (components only, you have tools)

---

# ORDER 1: TME (tme.eu)

**Free shipping threshold: €50** — consider adding extras to hit this

Copy these part numbers directly into TME search:

## Integrated Circuits

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| TL072CP | Dual op-amp DIP-8 (TI) | 6 | €0.40 ea |
| TL074CN | Quad op-amp DIP-14 (TI) | 2 | €0.55 ea |
| LM13700N | Dual OTA DIP-16 (TI) | 2 | €1.80 ea |
| CD4066BE | Quad bilateral switch DIP-14 | 2 | €0.35 ea |
| CD4017BE | Decade counter DIP-16 | 1 | €0.30 ea |
| CD4024BE | 7-stage counter DIP-14 | 1 | €0.30 ea |

**Alternative if TL072CP out of stock:** TL072IP, TL072ACP, or NE5532P

## Transistors

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| BC547B | NPN transistor TO-92 | 10 | €0.05 ea |
| BC557B | PNP transistor TO-92 | 10 | €0.05 ea |
| 2N3906 | PNP transistor TO-92 | 5 | €0.08 ea |

## Diodes

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| 1N4148 | Signal diode | 25 | €0.02 ea |
| 1N5817 | Schottky 40V 1A | 5 | €0.12 ea |
| BZX55C3V3 | 3.3V Zener (or BZX79C3V3) | 5 | €0.08 ea |

## IC Sockets

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| GS-8 | DIP-8 socket | 10 | €0.08 ea |
| GS-14 | DIP-14 socket | 6 | €0.10 ea |
| GS-16 | DIP-16 socket | 4 | €0.12 ea |

## Resistors (1/4W Metal Film 1%)

**Search format on TME:** "MF0207 [value]" or "ROYAL OHM [value]"

| Value | Qty | TME Search | Est. Price |
|-------|-----|------------|------------|
| 100Ω | 10 | MF0207FTE52-100R | €0.02 ea |
| 1kΩ | 20 | MF0207FTE52-1K | €0.02 ea |
| 2.2kΩ | 10 | MF0207FTE52-2K2 | €0.02 ea |
| 10kΩ | 30 | MF0207FTE52-10K | €0.02 ea |
| 22kΩ | 15 | MF0207FTE52-22K | €0.02 ea |
| 30kΩ | 10 | MF0207FTE52-30K | €0.02 ea |
| 47kΩ | 15 | MF0207FTE52-47K | €0.02 ea |
| 100kΩ | 30 | MF0207FTE52-100K | €0.02 ea |
| 120kΩ | 10 | MF0207FTE52-120K | €0.02 ea |
| 1MΩ | 10 | MF0207FTE52-1M | €0.02 ea |

## Capacitors - Ceramic/MLCC

| Value | Type | Qty | TME Search | Est. Price |
|-------|------|-----|------------|------------|
| 100nF | Ceramic | 30 | CC-100N (or search "100nF ceramic") | €0.03 ea |
| 10nF | Ceramic | 15 | CC-10N | €0.03 ea |

## Capacitors - Film (Polyester/Polypropylene)

| Value | Voltage | Qty | TME Search | Est. Price |
|-------|---------|-----|------------|------------|
| 470nF | 63V | 3 | MKS2-470N/63 (WIMA) | €0.25 ea |
| 1µF | 63V | 6 | MKS2-1U/63 (WIMA) | €0.35 ea |
| 100nF | 63V | 6 | MKS2-100N/63 (WIMA) | €0.15 ea |

## Capacitors - Electrolytic

| Value | Voltage | Qty | TME Search | Est. Price |
|-------|---------|-----|------------|------------|
| 10µF | 25V | 15 | CE-10/25PHT | €0.06 ea |
| 100µF | 25V | 6 | CE-100/25PHT | €0.10 ea |
| 4.7µF | 25V | 3 | CE-4U7/25PHT | €0.05 ea |

## Ferrite Beads (for Pi Pico power filtering)

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| BLM18AG601SN1D | 600Ω@100MHz 0805 SMD | 6 | €0.12 ea |

**Alternative through-hole:** Search "ferrite bead axial"

## MIDI Connector

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| MJ-401-5 | 5-pin DIN socket panel mount | 1 | €0.80 ea |

## Optocoupler (optional - for MIDI thru)

| TME Part Number | Description | Qty | Est. Price |
|-----------------|-------------|-----|------------|
| 6N138 | High-speed optocoupler | 2 | €0.70 ea |

---

## TME ORDER SUBTOTAL: ~€35-40

**Pro tip:** Add resistors/caps in multiples of 10-25 for spares. The price difference is negligible and you'll thank yourself later.

---

# ORDER 2: MOUSER or FARNELL

## JTAG Debugger (Farnell recommended for EU)

| Farnell Part # | Description | Qty | Price |
|----------------|-------------|-----|-------|
| 3106578 | SEGGER 8.08.91 J-Link EDU Mini | 1 | ~€21 |

**Alternative from Mouser:** 988-8.08.91 (J-LINK EDU MINI)

## Raspberry Pi Pico

| Mouser Part # | Description | Qty | Price |
|---------------|-------------|-----|-------|
| 358-SC0915 | Raspberry Pi Pico (RP2040) | 1 | ~€4.50 |
| 358-SC0918 | Raspberry Pi Pico WH (with headers) | 1 | ~€5.50 |

**Note:** Get the "H" version if you want pre-soldered headers

## Precision Components

| Mouser Part # | Description | Qty | Price |
|---------------|-------------|-----|-------|
| 652-3296W-1-103LF | Bourns 10kΩ trimmer | 4 | €0.85 ea |
| 652-3296W-1-104LF | Bourns 100kΩ trimmer | 4 | €0.85 ea |

**Alternative trimmers:** Search "3296 trimmer" - these are industry standard

## USB-TTL Adapter (ISP backup)

| Part | Description | Qty | Price |
|------|-------------|-----|-------|
| CP2102 module | USB-TTL 3.3V/5V | 1 | ~€3 (AliExpress) |

---

## MOUSER/FARNELL ORDER SUBTOTAL: ~€45

---

# ORDER 3: THONK (thonk.co.uk)

**Shipping to Lithuania:** ~£5-8 Royal Mail

Go to: https://www.thonk.co.uk/shop/

## 3.5mm Jack Sockets

| Product | Description | Qty | Price |
|---------|-------------|-----|-------|
| Thonkiconn PJ398SM | Switched 3.5mm jack (pack of 10) | 2 packs | £4.00/pack |
| Thonkiconn nuts | Knurled nuts (included with jacks) | — | included |

**Note:** PJ398SM is the switched version. For non-switched, get PJ301M-12 (same price).

## Potentiometers (9mm Alpha style)

| Product | Description | Qty | Price |
|---------|-------------|-----|-------|
| 9mm Alpha pot B100K | 100kΩ linear | 4 | £0.65 ea |
| 9mm Alpha pot B50K | 50kΩ linear | 3 | £0.65 ea |
| 9mm Alpha pot B10K | 10kΩ linear | 3 | £0.65 ea |

## Knobs

| Product | Description | Qty | Price |
|---------|-------------|-----|-------|
| Davies 1900H clone knobs | Small black pointer | 10 | £0.25 ea |

**Or search:** "Rogan knobs", "Eagle knobs" — whatever matches your aesthetic

## Switches (Thonk has limited selection - may need elsewhere)

| Product | Description | Qty | Price |
|---------|-------------|-----|-------|
| SPDT ON-ON toggle | Mini toggle | 5 | £0.80 ea |

**Alternative for switches:** Tayda Electronics (tayda.com) has better switch selection at lower prices

---

## THONK ORDER SUBTOTAL: ~£20-25 (~€23-29)

---

# ORDER 4: ALIEXPRESS

Search terms and recommended items:

## OLED Display — user already has 1.3" + 0.96"

The user has a 1.3" SH1106 I²C (primary) and a 0.96" SSD1306 I²C (fallback) on hand, plus a 24×2 I²C LCD module. No purchase required.

If an OLED module does need to be sourced:

**Search:** "1.3 inch OLED 128x64 SH1106 I2C"

| Item | Specs | Qty | Price |
|------|-------|-----|-------|
| 1.3" OLED SH1106 | 128×64, I²C, white/blue | 1 | ~€4-7 |

**CHECK:** Module should expose VCC/GND/SCL/SDA headers and advertise SH1106 (some listings mislabel SSD1306 driver chips).

## Connectors

| Search Term | Qty | Price |
|-------------|-----|-------|
| "JST PH 2.0mm connector kit" | 1 kit | ~€3 |
| "Dupont jumper wire kit" | 1 | ~€2 |
| "10-pin 1.27mm IDC cable" | 2 | ~€1 |

## Wire

| Search Term | Qty | Price |
|-------------|-----|-------|
| "28AWG silicone wire 8 colors" | 1 set | ~€6 |
| "22AWG stranded wire red black" | 1 set | ~€3 |

## Hardware

| Search Term | Qty | Price |
|-------------|-----|-------|
| "M2 brass standoff kit" | 1 | ~€3 |
| "M3 brass standoff kit" | 1 | ~€3 |
| "M4 brass bolt nut" | 1 pack | ~€2 |
| "Nylon washer M4" | 1 pack | ~€1 |

## Switches (if not from Thonk)

| Search Term | Qty | Price |
|-------------|-----|-------|
| "MTS-102 toggle switch" (SPDT ON-ON) | 10 | ~€2 |
| "MTS-202 toggle switch" (DPDT ON-ON) | 5 | ~€2 |

## Misc

| Search Term | Qty | Price |
|-------------|-----|-------|
| "Kapton tape 10mm" | 1 | ~€2 |
| "Heat shrink tubing kit" | 1 | ~€2 |
| "3M VHB tape" (or "VHB double sided tape") | 1 | ~€3 |
| "0.5mm polycarbonate sheet A5" | 1 | ~€3 |
| "CP2102 USB TTL" | 1 | ~€2 |
| "Logic analyzer 24MHz 8ch" | 1 | ~€8 |

---

## ALIEXPRESS ORDER SUBTOTAL: ~€45-55

---

# COMPLETE ORDER CHECKLIST

## ☐ TME Order (~€35-40)
```
□ TL072CP x6
□ TL074CN x2
□ LM13700N x2
□ CD4066BE x2
□ CD4017BE x1
□ CD4024BE x1
□ BC547B x10
□ BC557B x10
□ 2N3906 x5
□ 1N4148 x25
□ 1N5817 x5
□ BZX55C3V3 x5
□ DIP-8 sockets x10
□ DIP-14 sockets x6
□ DIP-16 sockets x4
□ Resistor kit (values listed above)
□ Capacitor kit (values listed above)
□ Ferrite beads x6
□ 5-pin DIN socket x1
□ 6N138 x2 (optional)
```

## ☐ Mouser/Farnell Order (~€45)
```
□ J-Link EDU Mini (8.08.91)
□ Raspberry Pi Pico (or Pico WH)
□ Bourns 3296 trimmers 10k x4
□ Bourns 3296 trimmers 100k x4
```

## ☐ Thonk Order (~€25)
```
□ Thonkiconn PJ398SM x20 (2 packs of 10)
□ 9mm Alpha B100K x4
□ 9mm Alpha B50K x3
□ 9mm Alpha B10K x3
□ Davies knobs x10
□ Toggle switches x5 (if available)
```

## ☐ AliExpress Order (~€50)
```
□ (OLED not needed — 1.3" SH1106 + 0.96" SSD1306 + 24x2 LCD already on hand)
□ JST PH connector kit
□ 28AWG silicone wire set
□ 22AWG wire red/black
□ M2/M3/M4 hardware kits
□ Toggle switches MTS-102 x10
□ Toggle switches MTS-202 x5
□ Kapton tape
□ Heat shrink kit
□ VHB tape
□ Polycarbonate sheet
□ CP2102 USB-TTL adapter
□ Logic analyzer 8ch
□ 10-pin IDC cables
```

---

# GRAND TOTAL: ~€155-170

(You said you have all tools, so this is components only)

---

# NOTES

1. **TME** has Lithuanian language interface - select it for easier ordering
2. **Free shipping thresholds:**
   - TME: €50 (add extras to hit this)
   - Mouser: €50
   - Thonk: Check current rates
3. **AliExpress shipping:** Select "AliExpress Standard Shipping" or "Cainiao" for trackable delivery to Lithuania (usually 2-3 weeks)
4. **Part substitutions:**
   - TL072 → TL082, NE5532 (pin compatible)
   - TL074 → TL084, MC33079 (pin compatible)
   - CD4066 → CD4016 (slightly different Ron)
5. **Buy extras** of resistors, caps, diodes - they're cheap and you'll use them

---

# QUICK TME BASKET BUILDER

Copy-paste this list into TME's Quick Buy feature:

```
TL072CP,6
TL074CN,2
LM13700N,2
CD4066BE,2
CD4017BE,1
CD4024BE,1
BC547B,10
BC557B,10
2N3906,5
1N4148,25
1N5817,5
GS-8,10
GS-14,6
GS-16,4
MJ-401-5,1
```

For resistors and capacitors, use TME's parametric search - it's faster than typing each value.

---

**Document Version:** 1.0  
**Created:** March 2026  
**Project:** MACROBRUTE
