# MACROBRUTE SHOPPING LIST — missing parts only

**Project:** MACROBRUTE MicroBrute Deep Mod
**Updated:** 2026-10-17 (rewritten from the March 2026 list)
**Source:** the owned-parts inventory in `docs/superpowers/reviews/2026-10-16-backfeed-hum-design.md` section 1 ("BF"), mirrored in `docs/hardware/MACROBRUTE_BOM.md` (Have/Missing table) and `docs/MACROBRUTE_CONNECTION_MAP.md` section 14.

The March 2026 list ordered CD4066, CD4017, CD4024, LM13700, BC547/BC557/2N3906, ferrite beads, 100 µF parts, a 40 V "1N5817" and other parts that are owned, dropped or wrong (audit S50). That list is replaced, not edited; it is in git history. **Nothing here is bought without the owner's approval.** The owner has further parts not yet listed (BF Q18), so some "Missing" rows may already be in a drawer.

## 1. Genuine purchases (no owned equivalent)

| Part | Qty | Why | Source | Note |
|------|-----|-----|--------|------|
| LF398N (DIP-8) | 1 | Expander Sample & Hold | TME | No owned part is a sample-and-hold. Pinout: 1 V+, 2 OFFSET ADJUST, 3 INPUT, 4 V-, 5 OUTPUT, 6 Ch, 7 LOGIC REFERENCE, 8 LOGIC (DATASHEETS (a)). BF Q1 |
| 10 nF film capacitor, polystyrene or polypropylene | 1 | LF398 hold capacitor | TME | Ceramic is unsuitable (LF398 sheet p15). The owned 1 nF is ceramic. BF Q1 |

## 2. Missing, owner decision needed

| Part | Qty | For | Owned alternative or question |
|------|-----|-----|-------------------------------|
| Film capacitor 1 µF, or 4.7-10 µF | 1 | LFO timing | Owned 1 µF ceramic has unknown dielectric; 10 µF electrolytics are polarised. BF Q6 |
| 1 MΩ pots | 3 | LFO rate, slew rise/fall | A 100 kΩ pot (4 owned) changes the ranges by 10×. BF Q6 |
| 1N4148 | 2 | Slew-limiter steering | May be in the assortment kit (UNVERIFIED); BAT85 stock is fully allocated. BF Q4 |
| 1N5817 (20 V, 1 A) | 1 | Pico VSYS OR diode | An owned BAT85 can stand in (about 4.2 V at 100 mA, inside VSYS 1.8-5.5 V), but all 10 BAT85 are allocated. BF 1.2, Q3 |
| 100 kΩ trimmers | up to 4 | Aux-out trims | Fixed resistors from the owned kit are the alternative. BF Q7 |
| Eurorack 16-pin keyed header + ribbon | 1 | Expander power | No owned alternative. BF Q11 |
| DB-9 panel connectors | 4 needed in total (owned count UNVERIFIED) | 2 on the MB rear panel, 2 on the expander | Owner reports "several"; earlier list says 2; gender and flange unknown. BF Q9 |
| Shielded 9-conductor cable ×2 with hoods | 2 | DB-9 A and B links | A ribbon cable is not acceptable (audit N19). BF Q9 |
| Insulating shoulder washers | as needed | Expander-side DB-9 shells | Alternative shield rule if declined. BF Q10 |
| RGB LED (common cathode), 6 mm tactile button | 1 each | Expander UI | BF Q12 |
| Stripboard, IC sockets, hook-up wire | — | All boards | Not on the owned list. BF Q13 |
| 3.5 mm panel jacks, Thonkiconn type | as needed | Expander and MB panels | Only if the owned 25 do not suit. BF Q8 |
| Brass M3 bolts ×6, SPDT mini toggles ×3 | — | Touch bolts, panel mods B4-B6 | Later phase |

## 3. Open owner questions that decide whether anything is bought

These are not resolved here (BF section 6.1): Pico variant (Q21), main OLED size and interface (Q22; an SPI-only module changes the display driver and pins), DB-9 count (Q9), expander width (17 HP or about 20 HP, audit decision e; a blank panel is owned per the earlier docs, its size is to be measured), and whether the PC817 isolated UART (BF 3.9) is wanted.

## 4. Not needed (do not buy)

CD4066, CD4017, CD4024, LM13700, BC547, BC557, 2N3906, 2N3904 (LED drivers deleted, vactrol via a TL072 stage), BSS138, BAT54S (use owned BAT85), BZX84C3V3, SMBJ12CA, BAT46, LM7805 (78L05 is owned), MCP4725, ferrite beads (omit, or 10 Ω + 10 µF), 100 µF and 47 µF electrolytics (use 2-4× owned 10 µF / 63 V in parallel), 10 MΩ resistors (1 MΩ replaces them), JST-XH 5-pin (EFFIGY shelved), a second Pico or OLED.

---

**Document Version:** 2.0
**Project:** MACROBRUTE
