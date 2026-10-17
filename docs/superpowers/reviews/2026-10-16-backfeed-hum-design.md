# MACROBRUTE back-feed and hum design note

Date: 2026-10-17
Branch: project-review-diagram-redesign
Inputs: `docs/superpowers/plans/2026-10-16-project-review-and-diagram-redesign.md` (Global Constraints, Task 4b), `docs/superpowers/reviews/2026-10-16-project-audit.md` (sections 1a, 1b, 3, 4, 5), `docs/DATASHEETS.md`, reviewer reports r1, r2, r3, r5 (`.superpowers/sdd/2026-10-16-project-review-and-diagram-redesign/audit/`), `docs/MACROBRUTE_CONNECTION_MAP.md` section 14 (CM), `docs/hardware/MACROBRUTE_BOM.md`, `docs/hardware/MACROBRUTE_PHASE0_BOM.md`.

Rules of this note:
- Nothing is built. Every value is a design value. Anything not proven by a datasheet, the audit or a reviewer report is marked UNVERIFIED, with the bench check that settles it in section 6.
- Datasheet page numbers are PDF page numbers. Facts marked "(read for this note)" were read directly from the datasheet PDF in `datasheets/` and are not yet in `docs/DATASHEETS.md`.
- Items marked "Provisional (audit recommendation, owner has not confirmed)" follow the audit's recommendation and wait for the owner.
- Decided facts used here: split power (no supply on the cable, only ground); no I2C on the cable; EFFIGY shelved; strip OLED dropped; DB-9 B carries UART TX/RX, Filter CV, VCA CV and grounds; DB-9 A carries Gate, Pitch, Env, LFO, Mix, VCF, Saw, Square and ground (audit section 1a).

Power states used throughout:

| State | Expander (rack, Pico) | Synth (MicroBrute, breakout, LPC) |
|---|---|---|
| S0 | off | off |
| S1 | on | off |
| S2 | off | on |
| S3 | on | on (either order; includes the power-up transient of whichever side starts second) |

## 1. Owned-parts inventory

Ownership source: CM section 14 "Component Inventory (Purchased)" (CM:481-511) is the only list with a Have status. `docs/hardware/MACROBRUTE_BOM.md` and `MACROBRUTE_SHOPPING_LIST.md` are purchase lists with no Have column (this settles audit conflict C7 in favour of r3/r5). Owner additions of 2026-10-17: the KY-040 (HW-040) encoder, some vactrols, a through-hole resistor kit (values to be confirmed, section 1.3) and an IC assortment (photo, section 1.1a) are Have. Later owner decisions of 2026-10-17 (plan Global Constraints): the connector is CONFIRMED as 2x DB-9; the owner has two 1.3 inch OLEDs; and the kit parts listed in section 1.2 (from the owner's pasted inventory of the assortment kit; card contents UNVERIFIED) are owned. The owner has further components not yet listed (Q18). Anything not on these lists is Missing, even where it is very likely in a drawer; those are flagged as owner questions (Q-numbers, section 6).

### 1.1 Active parts and modules

| Part | Used for | Status (qty) | Owned alternative or owner question |
|---|---|---|---|
| Raspberry Pi Pico (variant UNVERIFIED) | Expander controller | Have (1) | The docs say Pico WH; the package says "Raspberry Pi Pico" (no W); another owner description says "Pico H". Nothing in this design uses wireless, so any variant works electrically; docs may need renaming (Q21). |
| Main OLED: 1.3 inch 7-pin SPI module (chip SSD1306 or SH1106 and pin order UNVERIFIED: read the module) | Expander main display, SPI0: SCK GP2, MOSI GP3, DC GP4, RES GP5, CS GP11 | Have (owner, 2026-10-17) | Baseline per the later owner ruling (2026-10-17). Needs an SPI driver (firmware follow-up); SH1106 would also need `OLED_COL_OFFSET=2`. The module is larger than the 0.96 inch panel cutout, which bears on the open expander width (17 vs about 20 HP stays OPEN). Q22. |
| 1.3 inch 4-pin I2C OLED | Was the baseline | Have, not available | Wired into a TD-3. |
| 0.96" SSD1306 OLED | Was the baseline main display | Owner to confirm (it may not have arrived) | Alternative only: as an I2C module it needs GP4/GP5 (now OLED DC/RES), so re-pinning. |
| 0.91" SSD1306 128x32 | Was the strip OLED | Have (1), no longer used | Dropped (decision c); spare. |
| KY-040 / HW-040 encoder | Expander encoder | Have (1) (owner, 2026-10-17) | - |
| TL074C | MB breakout U1 buffers; expander aux outs | Have (4) | - |
| TL072IP | Breakout U2 (env/LFO), vactrol V-to-I, slew, LFO, S&H buffer, clock conditioning | Have (6) | Section count for U2 is audit conflict C10; 6 owned cover r3's 2x TL072 plan. |
| CD40106 | Breakout gate conditioner; expander LFO Schmitt | Have (3) | - |
| CD4049UBE | Expander Clock IN and Clock OUT buffers (section 3) | Have (3) | Not used on the gate path (section 3.5). |
| CD4051 | Not used by the decided design | Have (2) | Only as the unproven S&H alternative below (owned-parts option; charge injection UNVERIFIED; its supply is TO DESIGN, CD4051 abs max 20 V). |
| 78L05 | Breakout-local 5 V for the CD40106 (Provisional) | Have (4) | - |
| LF398 | Expander S&H | Missing | No owned equivalent. LF398 stays the default. Alternative CD4051 + TL072 + film hold cap (r3) is an owned-parts option with charge injection UNVERIFIED, a supply TO DESIGN (CD4051 abs max 20 V) and it still needs a film cap. Q1: buy LF398N? |
| BF245C JFET | No role in the decided design | Have (5) | - |
| 2N3904, 2N3906, S8050, S8550, 2N5401, 2N5551 | Kit transistors (owner's pasted inventory) | Have (10+ each, card contents UNVERIFIED) | 2N3904 is OWNED (no longer Missing). Not needed by the decided design: LED drivers deleted (S12), vactrol via TL072 V-to-I stage (S37). |
| BC547 / BC557 | Listed in BOM rows | Missing (purchase list only) | Not needed. |
| BSS138 | Old level shifter | Missing | Not needed (UART is 3.3 V to 3.3 V; gate uses a divider, section 3.5). |
| LM13700, CD4024, CD4066 | Dropped circuits | Missing | Not needed. |
| LM7805 | "Spares" | Missing | Not needed (78L05 owned). |
| MCP4725 | Optional DAC | Missing | Not needed. |
| Vactrol | Resonance CV (breakout) | Have ("some", owner 2026-10-17) | Part number and type unknown. Q2: read the marking; the TL072 V-to-I driver's sense resistor depends on the vactrol LED's forward-current rating. |
| LDR04 | Home-made vactrol | Have (4) | Only needed if the owned vactrols do not suit. |
| Isolation transformer | Hum ladder last step, one audio line | Have (1, salvaged, 46.9/82.4 ohm DCR) | Turns ratio, inductance, bandwidth UNVERIFIED (E-29). |
| Arduino Nano | No role (parked) | Have (1) (owner, 2026-10-17) | - |
| Assortment kit (resistors, capacitors, transistors, diodes, LEDs, trim pots) | Possible source for the Missing transistor, diode and trimmer rows | Have (owner, 2026-10-17); exact types and values UNVERIFIED | Owner to send close-ups of the insert card (Q18). The parts the owner's pasted inventory names are listed as Have in this section (card contents UNVERIFIED); rows not named there stay Missing. |

### 1.1a IC assortment (owner photo, 2026-10-17)

All Have. None of these is an LF398 equivalent (no part here is a sample-and-hold with a low-leakage hold switch), so Q1 stands.

| Part | Qty | Possible use in this project |
|---|---|---|
| PC817 optocoupler | 10-20, owner to confirm (photo label x20; about 10 in the owner's later list) | Isolated UART alternative (section 3.9). |
| NE5532 | 5 | Audio op-amp sections (for example ladder step 5 difference receivers). Supply: recommended +/-5 V to +/-15 V, abs max +/-18 V (TI SLOS075K p3), so +/-12 V is in range. Back-to-back input diodes conduct above about 0.6 V differential (p3 note 4), so not for comparators or Schmitt stages; bipolar inputs (bias current not read for this note, UNVERIFIED) make it a poor choice for high-impedance nodes (S&H buffer, 1M bias). |
| JRC4558 | 10 | Audio op-amp sections, same role as NE5532. No datasheet in `datasheets/`: supply range and input limits UNVERIFIED. |
| LM358 | 10 | Single-supply op-amp; datasheet in `datasheets/LM358/` (not read for this note). |
| LM324 | 10 | Quad version of LM358; no datasheet in `datasheets/` (UNVERIFIED). |
| LM393 | 10 | Comparator; datasheet in `datasheets/LM393/` (not read for this note). |
| LM339 | 10 | Quad comparator; no datasheet in `datasheets/` (UNVERIFIED). |
| NE555 | 20 | Not needed by the decided design. |
| PT2399 | 3 | Delay IC (spinoff only, DATASHEETS row). |
| ICL7660S | 2 | Charge-pump inverter; not needed (no negative rail is missing). |
| UC3842AN, UC3843AN | 5 each | PWM controllers; not needed. |
| ULN2003AN (listed as "UL2003AN"), ULN2803APG | 5 each | Darlington arrays; not needed. |
| LM386, TDA2030A, TDA2822D | 5, 2, 5 | Power audio amplifiers; not needed. |

### 1.2 Diodes

| Part | Used for | Status | Owned alternative or owner question |
|---|---|---|---|
| BAT85 | CV clamps, rail protection | Have (10) | Budget: 4 for the two CV clamps (section 3.3), 1 for Pico VSYS, 3 for expander +12/-12/+5 V, 2 for breakout rails = 10. Exactly the stock, so none is left for hum-ladder step 4. If audit conflict C12 goes to r2's series resistor on the breakout rails, 2 are freed and step 4 becomes buildable. Owned 1N5819 (x10) and 1N4148 (25+) can now take over some of these roles (see the 1N5819 and 1N4148 rows), which would free BAT85; provisional, no decision changed. Q3: confirm before more BAT85 uses are added. |
| BAT54S | CV clamps (old docs) | Missing | BAT85, two per clamp (DATASHEETS (e)). |
| 1N5819 (40 V Schottky), 1N5822 | Kit diodes (owner's pasted inventory) | Have (1N5819 x10, 1N5822 x5; card contents UNVERIFIED) | 1N5819 is OWNED and may serve where this note wanted a 1N5817: the Pico VSYS OR diode and the expander rail reverse protection (provisional). `docs/DATASHEETS.md` (e) quotes 1N5819 as 40 V with VF 0.60 V at 1 A from the 1N5817-series sheet (Diodes DS23001); the owner's actual part and its datasheet are UNVERIFIED (not saved under `datasheets/`). If 1N5819 takes the three expander rail diodes and the VSYS diode, up to 4 BAT85 are freed (provisional). |
| 1N5817 | Pico VSYS OR diode, expander rail reverse protection | Missing (not owned; the owned 1N5819 may replace it, row above) | BAT85 can also stand in: IF 200 mA continuous, VF 800 mV at 100 mA (BAT85 p2-p3). On VSYS that gives about 4.2 V at 100 mA, inside the Pico's 1.8-5.5 V VSYS range (Pico datasheet p9). Note 1N5817 is a 20 V part, not 40 V (DATASHEETS (e)). |
| 1N4148 | Slew-limiter steering, old clamps | Have (25+, owner's pasted inventory; card contents UNVERIFIED) | Owned 1N4148 can serve the hum-ladder step 4 anti-parallel pair and the slew steering, instead of BAT85 (provisional; VF differs from BAT85, so recheck BT-2, BT-3 and BT-5). Q4: confirm the stock. |
| 1N270 | Germanium diode | Have (x2, owner's pasted inventory; card contents UNVERIFIED) | No role in the decided design. |
| BZX84C3V3, SMBJ12CA, BAT46 | Old protection drawings | Missing | Not needed (audit B17, r2). |

### 1.3 Resistors

Status: Have (owner resistor kit, 2026-10-17). Series and power rating are not yet confirmed; this note assumes a standard E12/E24 through-hole 1/4 W kit. Q5: owner to confirm 220R, 1k, 2k, 4.7k, 10k, 22k, 33k, 100k are present, plus the other values this note uses (10 ohm, 560 ohm, 680 ohm, 1M); if a value is missing, the nearest kit value is acceptable where the row says so. 1 % parts for ladder step 5 are not assumed.

| Value | Where | Tolerance of substitution |
|---|---|---|
| 220 ohm | A:2 Pitch series (MB side) | 100-330 ohm acceptable. |
| 1k | UART series (4), A:3-A:8 output series (6), A:1 gate source, Clock OUT jack | 680 ohm-2.2k acceptable for UART if the BT-1 edge check passes. |
| 10k | CV series at the expander (2), TP83 input series | 4.7k-22k acceptable. |
| 22k + 33k | Gate divider on the expander | Any pair giving 2.6-3.2 V from 5 V with a total of 40-60k. |
| 100k | CV series on the MB side (2), Clock IN series, Clock IN pull-down, inputs normalled from A lines | 82k-150k acceptable. |
| 1M | TL074 input bias (replaces 10M, audit N11) | - |
| 10 ohm | Optional hum-ladder ground resistor, optional rail series R (C12) | 4.7-22 ohm. |
| 560 ohm, 4.7k | PC817 UART alternative only (section 3.9): LED series (2x 560 ohm) and emitter load (2x 4.7k) | 560 ohm: 470-680 ohm; 4.7k: 3.9k-6.8k (see 3.9). |

### 1.4 Capacitors

| Part | Used for | Status | Owned alternative or owner question |
|---|---|---|---|
| 100 nF ceramic | Decoupling | Have (20) | - |
| 1 uF ceramic | General | Have (5) | Dielectric unknown; not for timing or hold. |
| 1 nF ceramic | CV-input filter (section 3.3), TP83 filter | Have (5) | Not for S&H (LF398 p15). |
| 10 uF / 63 V electrolytic | Rail bulk | Have (10) | Used for the 100 uF positions below. |
| 100 uF / 25 V, 100 uF / 10 V, 47 uF | Rail and VSYS bulk | Missing | 2-4x 10 uF / 63 V in parallel per rail (audit decision 8). |
| 10 nF film (polystyrene / polypropylene) | LF398 hold cap | Missing | No owned alternative (ceramic unsuitable, LF398 p15). Part of Q1. |
| 1 uF film, or 4.7-10 uF film | LFO timing (audit S60) | Missing | Owned 1 uF ceramic has unknown dielectric; 10 uF electrolytic is polarised and unsuitable for a bipolar integrator. Q6. |
| 10 nF ceramic | Old CV-filter value | Missing | 1 nF owned is used instead (section 3.3). |

### 1.5 Pots, jacks, connectors, cable, hardware

| Part | Used for | Status | Owned alternative or owner question |
|---|---|---|---|
| 100k pots | Expander controls | Have (4) | - |
| 1M pots | LFO rate, slew rise/fall | Missing (3) | A 100k pot changes the ranges by 10x; Q6 together with the LFO cap. |
| 100k trimmers | Aux-out trims (BOM) | Missing (assortment kit has trim pots, values UNVERIFIED) | Q7, or fixed resistors. |
| 3.5 mm jacks | Expander panel (16+ jacks after LFO + S&H, audit S52), MB panel jacks | Have (25), type unknown | Q8: are these PJ398SM / PJ301M style panel jacks (E-25)? |
| DB-9 connectors | 2 on the MB rear panel, 2 on the expander | Have ("several" per owner 2026-10-17; count UNVERIFIED, earlier list says 2), gender and flange UNVERIFIED | Needs 4 panel connectors plus 2 cables (or 4 cable ends): how many are Missing depends on the real count (UNVERIFIED), plus the cables. Q9 (E-32). |
| HD-15 connectors | Rejected | Have (2), spare (the VGA line in a pasted inventory was an error; DB-9 stay in this project) | Not usable (cable shorts pins 6-8 to GND, plan). |
| Shielded 9-core cable (x2) and hoods | DB-9 A and B links | Missing | Q9. A ribbon cable is not acceptable (N19). |
| Insulating shoulder washers | Expander-side DB-9 shells (section 4.2) | Missing | Q10. |
| Eurorack 16-pin keyed header and ribbon | Expander power | Missing | No owned alternative. Q11. |
| Ferrite beads | Old rail and UART filters | Missing | Omit; 10 ohm + 10 uF where filtering is wanted (audit decision 8). |
| RGB LED (common cathode), 6 mm tactile button | Expander UI | Missing (Phase 0 BOM lists them, not owned) | Q12. |
| SPDT toggles, brass M3 bolts | Panel mods B4-B6, touch bolts (later phase) | Missing | Later phase. |
| Stripboard, IC sockets, wire | All boards | Not on the owned list | Q13. |
| JST-XH 5-pin | EFFIGY header | Not needed | EFFIGY shelved. |

## 2. DB-9 A and DB-9 B final pin maps

### 2.1 Neighbour geometry (UNVERIFIED)

Standard D-sub 9 layout, as numbered on the connector insert: top row pins 1-5, bottom row pins 6-9, offset by half a pitch. Pin 6 sits between 1 and 2, 7 between 2 and 3, 8 between 3 and 4, 9 between 4 and 5. Direct neighbours:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Neighbours | 2, 6 | 1, 3, 6, 7 | 2, 4, 7, 8 | 3, 5, 8, 9 | 4, 9 | 1, 2, 7 | 2, 3, 6, 8 | 3, 4, 7, 9 | 4, 5, 8 |

The downloaded D-sub drawings give contact pitch 0.109 in (2.77 mm) and mounting-hole spacing 24.99 mm (Spectrum Control p1) but not the row offset for the owner's part. The geometry stays UNVERIFIED until BT-7 (caliper or the exact connector's drawing). Male and female faces are mirror images; always use the numbers moulded into the insert.

### 2.2 DB-9 B (Digital + CV, expander to and from MicroBrute)

Rule applied: the UART pair at one end, each high-impedance CV pin surrounded only by ground pins, no CV pin next to a digital pin, grounds interleaved.

Connector face (insert numbering):

```
   top row     [1 UART TX]-[2 GND]-[3 VCA CV]-[4 GND]-[5 FILTER CV]
   bottom row        [6 UART RX]-[7 GND]-[8 GND]-[9 GND]
```

Check against the neighbour table: UART TX (1) touches 2 GND and 6 RX; UART RX (6) touches 1 TX, 2 GND, 7 GND. VCA CV (3) touches 2, 4, 7, 8, all ground. Filter CV (5) touches 4 and 9, both ground. No CV touches a digital pin or the other CV. Filter CV, the most sensitive input (summing node, audit H-4), takes pin 5: the corner farthest from the UART.

Why not the alternatives: r5's and r3's maps were built around I2C on the cable, which is now off (audit section 1a c, d). Placing both CVs on 5 and 9 (also "at the far end") would make them neighbours of each other and give pin 9 only two ground neighbours; the 3/5 placement guards each CV on every side.

| Pin | Signal | Direction | Series R | Protection | Wire colour |
|---|---|---|---|---|---|
| 1 | UART TX (Pico GP0 to LPC P0.16 / RXD1, LQFP pin 63) | Expander to MB | 1k at the Pico (expander board) + 1k at the LPC (MB board) | Pico firmware keeps GP0 high-impedance until GP1 reads high (section 3.1). LPC UART choice UNVERIFIED (audit B01). | White |
| 2 | GND | - | - | Guard; TP72 star and expander star | Black |
| 3 | VCA CV in (to TP10, per CM) | Expander to MB | 10k at the expander output + 100k at the MB board | BAT85 to +12V_BRK and from -12V_BRK at the node after the 100k; 1 nF to GND | Purple |
| 4 | GND | - | - | Guard | Black |
| 5 | Filter CV in (to TP26, per CM) | Expander to MB | 10k at the expander output + 100k at the MB board | As pin 3 | Blue |
| 6 | UART RX (LPC P0.15 / TXD1, LQFP pin 62, to Pico GP1) | MB to expander | 1k at the LPC (MB board) + 1k at the Pico (expander board) | GP1 is a fault-tolerant RP2040 pin (section 3.1) | Yellow |
| 7 | GND | - | - | Guard | Black |
| 8 | GND | - | - | Guard | Black |
| 9 | GND | - | - | Star return | Black |

Freed pins: compared with the old CM map (1 TX, 2 RX, 3 SDA, 4 SCL, 5 Filter, 6 VCA, 7 +12 V, 8 -12 V, 9 GND), four pins are freed (the two I2C and the two rail pins). All carry ground. No signal is justified on them: r2's MB_ALIVE sense line is unnecessary because the Pico can see that the LPC is powered from the UART RX idle level (section 3.1), and a ground-sense line is kept only as a fallback-ladder option (section 4.5). Five ground conductors also lower the return impedance for the CV and UART currents.

Series resistors sit on the board side of each connector (soldered at the solder cup or the first board pad), never in the cable (r5 7.2). Both ends get one on the UART so either board survives a cable fault on its own.

Consequences for other documents (Task 5, not done here): the UART moves from B:1/B:2 to B:1/B:6 and the CVs from B:5/B:6 to B:5/B:3. `firmware/pico/config.py` mentions DB-9 pin numbers only in comments (r5); those comments and the CM tables change together.

### 2.3 DB-9 A (Outputs, MicroBrute to expander)

A has 8 signals and 1 ground: no pin can be interleaved, only reordered. The order is kept as in CM:76-86. Justification: no reviewer proved a crosstalk or ground problem with it. r5's re-order (N21) was offered as optional with its benefit marked UNVERIFIED by r5 itself; every A line is driven from a low impedance (op-amp follower or stock buffer) through a small series R, so capacitive coupling is expected to be small. The one weak spot is the Gate (pin 1) next to Pitch (2) and VCF (6). The re-order stays an owner option (Q14) to be decided by the BT-9 crosstalk measurement.

Connector face (insert numbering):

```
   top row     [1 GATE]-[2 PITCH]-[3 ENV]-[4 LFO]-[5 MIX]
   bottom row        [6 VCF]-[7 SAW]-[8 SQUARE]-[9 GND]
```

| Pin | Signal (MB source) | Direction | Series R | Protection | Wire colour |
|---|---|---|---|---|---|
| 1 | Gate (TP83 via 2x CD40106) | MB to expander | 1k at the CD40106 output (MB board) | Expander: 22k / 33k divider into a Pico fault-tolerant GPIO (section 3.5; pin OPEN, CM 12G); gate jack tapped before the divider. Provisional. | White |
| 2 | Pitch CV (stock rear Pitch buffer) | MB to expander | 220 ohm at the MB board (new; was "direct") | Low-impedance source UNVERIFIED (E-16) | Yellow |
| 3 | Envelope (TL07x follower) | MB to expander | 1k after the feedback tap (audit S36, R3-15) | - | Orange |
| 4 | LFO (TL07x follower) | MB to expander | 1k after the feedback tap | Source TP21 meaning UNVERIFIED (E-17) | Green |
| 5 | VCO Mix (TP30, TL074 follower) | MB to expander | 1k in, 1k out | - | Blue |
| 6 | VCF out (TP19, TL074 follower) | MB to expander | 1k in, 1k out | - | Purple |
| 7 | Saw (TP94, TL074 follower) | MB to expander | 1k in, 1k out | Peak level UNVERIFIED (E-19) | Red |
| 8 | Square (TP93, TL074 follower) | MB to expander | 1k in, 1k out | Peak level UNVERIFIED (E-19) | Brown |
| 9 | GND | - | - | TP72 star and expander star | Black |

Expander side of A: lines 2-8 go to panel jacks with no expander IC on them. If any A line is later normalled into an expander circuit (slew, S&H), it enters through at least 100k (section 3.6).

Pitch series value (audit conflict C2: r5 1k vs r3 100-220 ohm): 220 ohm is chosen. The back-feed into an unpowered receiving module is set by that module's own input resistor (typically 100k, UNVERIFIED), so 1k adds no back-feed protection, while it costs about 1 % scale into a 100k input (r3). 220 ohm still isolates the cable capacitance from the stock buffer.

## 3. Back-feed analysis per cable line

Datasheet limits used:
- LPC2361 (Rev. 03): standard pins 62, 63, 98, 99 are 5 V tolerant pads (footnote [1], p5-p6, p12). Table 4 (p33) gives -0.5 to +6.0 V for 5 V tolerant pins "only valid when the VDD(3V3) supply voltage is present", and VDD(3V3) + 0.5 V for "other I/O pins". The limit for a 5 V tolerant pin with VDD absent is therefore not specified; this note treats it as at most 0.5 V (the "other I/O pins" figure at VDD = 0). VIH 2.0 V min, VOH VDD - 0.4 V at 4 mA, pull-up current 15-85 uA (Table 5, p34; read for this note). The datasheet gives no injection-current figure for an unpowered pad: the actual current is UNVERIFIED.
- RP2040: VPIN abs max IOVDD + 0.5 V, and Table 622's scope names both Standard and Fault Tolerant IO (Table 622, p615); VIH 2.0 V at IOVDD 3.3 V, pull-up and pull-down 50-80 kohm, input leakage 1 uA (Table 625, p616-p617; read for this note). GPIO0-22 are "Digital IO (FT)": "very little current flows into the pin whilst it is below 3.63 V and IOVDD is 0 V" (Table 614, p613; read for this note); their reset state is pull-down (Table 615, p613-p614). GPIO26-29 are not FT and have a diode to IOVDD (Pico datasheet p20). The two statements conflict for an unpowered chip: any voltage above 0.5 V on a pin of an unpowered RP2040 exceeds the Table 622 absolute maximum, and only the Table 614 FT sentence says it is tolerated. Every S2 case below where a pin of the unpowered RP2040 sits above 0.5 V is therefore labelled "exceeds Table 622 abs max, relies on Table 614 FT, provisional", and BT-2 / BT-5 measure the pin current, not only the rail.
- CD4049UB: TI SCHS046L contradicts itself: p1 says VIH can exceed VCC; section 8.2.2 (p17) says inputs have clamp diodes to VCC and must stay below VCC (read for this note). This note treats the input as clamped to VCC.
- CD40106B: inputs -0.5 to VDD + 0.5 V, +/-10 mA (p4); VT+ at VDD 5 V 2.2 / 2.9 / 3.6 V min / typ / max (p5-p6; read for this note).
- BAT85: VF 240 mV at 0.1 mA, 400 mV at 10 mA (p2-p3).
- TL07x: input current limit +/-10 mA, inputs must stay within the rails (TI SLOS080W p10).

Decision on audit conflict C2 (one table): UART 1k at both ends (r5) rather than r2's 4.7k or r3's 1-2.2k at the Pico end only. CV: 10k at the expander (r5) plus 100k on the MB side (r2 and r3's "100k or more", replacing r5's 1k). Gate: 1k at the source (r3) and a divider on the expander (this note, section 3.5). Reasons are in each subsection.

### 3.1 UART TX (B:1, Pico GP0 to LPC RXD1) and UART RX (B:6, LPC TXD1 to Pico GP1)

| State | UART TX (Pico drives) | UART RX (LPC drives) |
|---|---|---|
| S0 | No source. | No source. |
| S1 (expander on, synth off) | Risk: Pico TX idles high (3.3 V) into an LPC pin treated as rated to 0.5 V when unpowered (p33, see above). Fix: firmware rule, GP0 stays an input (high-impedance, reset pull-down) until GP1 has read high; with the LPC off, GP1 is pulled low by its own pull-down, so GP0 never drives. Backstop if firmware fails: 2k total limits any current to below (3.3 - 0.6) / 2k = 1.35 mA, assuming a clamp to VDD exists (UNVERIFIED; the datasheet does not say). | LPC unpowered: no source. GP1 reads low (pull-down). |
| S2 (synth on, expander off) | Pico off, so no Pico source. The LPC's P0.16 (RXD1) pin, if left with its reset pull-up under stock firmware (15-85 uA, p34; reset default UNVERIFIED), pulls the line toward 3.3 V into the unpowered GP0 through 2k. The current is bounded by the pull-up (at most 85 uA) and GP0 is FT; the pin voltage can still exceed 0.5 V: exceeds Table 622 abs max, relies on Table 614 FT, provisional. | LPC TX (bridge firmware, Phase 6) idles high, or the LPC pin pull-up (15-85 uA, p34) under stock firmware, into unpowered GP1. Exceeds Table 622 abs max (pin up to 3.3 V vs 0.5 V), relies on Table 614 FT ("very little current" below 3.63 V with IOVDD = 0, p613), provisional. LPC VOH cannot exceed VDD 3.3 V. Backstop: 2k limits a worst-case clamp current to below 1.35 mA. BT-2 measures the pin current. |
| S3 | Normal. If the LPC starts second, GP1 goes high, and only then does the Pico enable GP0 as UART TX. | Normal. GP1's pull-down to the LPC's 4 mA push-pull high gives a clean high through 2k. |

Firmware rule (to add in a later firmware task; no firmware change here): `GP0` stays an input until the bridge is enabled and `GP1` has read high continuously for a debounce time (value is a firmware choice); it returns to input when `GP1` stays low (LPC powered off). Caution: a UART break sent by the LPC (line held low for longer than a character) looks the same as "LPC off" and would trip this rule. The "stays low" timeout must be longer than any break the bridge protocol uses, or the bridge protocol must not use breaks. Until the Phase 6 bridge firmware exists, the UART lines are wired but unused (audit N17), so GP0 never drives.

Value justification (1k + 1k = 2k per line):
- Edge rate: bit time at 115200 baud is 8.68 us. Cable capacitance is UNVERIFIED (E-13); the audit's working figure is about 150 pF for 1 m plus pins. RC = 2k x 150 pF = 0.30 us; 10-90 % rise = 2.2 RC = 0.66 us, 7.6 % of a bit, inside the BT-1 pass criterion of 0.9 us (about 10 % of a bit). At 300 pF (about 3 m at 100 pF/m) it is 1.32 us, which fails BT-1; for such a cable either shorten it or lower the resistors to 680 ohm at each end (1.36k x 300 pF x 2.2 = 0.90 us) and repeat BT-2, since a lower R raises any back-feed current. r2's 4.7k at one end gives 1.55 us at 150 pF, already outside BT-1.
- Drive current: peak charging current at most 3.3 V / 2k = 1.65 mA, inside the 4 mA rating of both drivers (LPC p34, RP2040 default 4 mA drive). DC load is only receiver leakage (3 uA LPC, 1 uA RP2040), so the high level at the receiver stays at the driver's VOH, above both VIH = 2.0 V figures.
- Fault: a cable conductor shorted to ground limits each driver to 3.3 V / 1k = 3.3 mA.
- Back-feed: with the firmware rule and the FT receiver, the series R is a backstop, not the primary protection. BT-2 sets the acceptance: the unpowered side's 3V3 rail below about 0.3 V.
- No divider, no level shifter: both ends are 3.3 V and LPC VIH is 2.0 V (p34); the old "1k + 2k divider OR CD4049" note is deleted (audit S30).

### 3.2 Why no MB_ALIVE line

The UART RX line already tells the Pico whether the LPC is powered (GP1 high with the bridge firmware running, low otherwise). A separate sense line would need a GPIO and a freed pin and would itself cross the cable. With the stock firmware the LPC pull-up versus the RP2040 pull-down gives an undefined level, which is harmless because GP0 is not used before the bridge firmware.

### 3.3 Filter CV (B:5) and VCA CV (B:3), expander to MicroBrute

Circuit per line: expander driver (op-amp output, up to about 10 V; source circuit not yet chosen) -> 10k on the expander board -> cable -> 100k on the MB board -> clamp node: BAT85 anode to node, cathode to +12V_BRK; BAT85 anode to -12V_BRK, cathode to node; 1 nF (owned) to GND -> existing injection point (TP26 for Filter CV, TP10 for VCA CV, per CM; whether the stock 220k / 100k resistors sit after these points is UNVERIFIED, E-18).

| State | Current path and size |
|---|---|
| S0 | No source. |
| S1 | Expander CV (up to 10 V) through 110k into the upper BAT85 and the unpowered +12V_BRK rail: at most (10 - 0.24) / 110k = 89 uA (BAT85 VF at 0.1 mA, p2-p3). Negative CV mirrors into -12V_BRK. The same 110k bounds any current into the synth's own injection path. |
| S2 | The MB node (TP26 / TP10 voltage UNVERIFIED) through 110k into the unpowered expander op-amp output: under 0.11 mA for any node voltage within +/-12 V. |
| S3 | Normal. Clamps conduct only for a fault above the breakout rails. |

Deviation from the plan's back-feed rule: for the CV lines the rule ("no current can flow into an unpowered IC's input protection diodes") is reduced, not met. In S1 up to 89 uA still flows into the unpowered +12V_BRK (or -12V_BRK) rail, and the same 110k path feeds the synth's own injection path (TP26 through the stock 220k, and TP10) while the synth is off. CV back-feed is bounded, not zero: the design limits the current; it does not remove it. Acceptance is BT-3 (unpowered rails below about 0.3 V). Owner option (Q19): a firmware mute that holds both CV outputs at 0 V until the Pico sees the synth powered (GP1 high, section 3.1) would make the S1 current zero in normal use; it needs a firmware change and the CV source circuit to support a defined 0 V output.

Why these values: with r5's 1k on the MB side, the S1 current is about (10 - 0.24) / 11k = 0.89 mA, which r2 and r3 warn can partly power the breakout op-amps. 100k cuts it by ten. The 10k at the expander isolates the op-amp output from the cable capacitance and limits a cable short to about 1 mA. Cost: the extra 100k reduces the CV depth if the synth's own 220k / 100k is in series after the injection point (to about 0.69 for Filter and 0.5 for VCA in that case; UNVERIFIED until E-18 and BT-4). If the depth is too small, reduce the MB-side resistor to 47k (S1 current about 0.17 mA) and repeat BT-3. The 1 nF with 100k gives a 0.1 ms time constant (about 1.6 kHz corner), which removes edge pickup without slowing control-rate CV; r3's 10 nF is not owned and would cut the corner to about 160 Hz.

Rail-diode note: whether the injected S1 current stays on the breakout rails or reaches the synth's TP70 / TP71 depends on audit conflict C12 (series diode or series resistor on the breakout rails). BT-3 measures both.

### 3.4 Gate A:1 on the MicroBrute side and the 5 V supply

Provisional (audit recommendation, owner has not confirmed):
- TP83 -> 10k series -> CD40106 pin 1, 1 nF (owned) from pin 1 to GND, no pull-up (audit B14). CD40106 pins 2 -> 3, pin 4 -> 1k -> A:1, so A:1 follows TP83 polarity (audit S33). Unused CD40106 inputs (5, 9, 11, 13) tied to GND (audit S34).
- The breakout needs 5 V only for this CD40106 (the strip OLED is dropped). Supply: owned 78L05 from +12V_BRK (dropout 1.7 V typ, TI SLVS010X device tables; quiescent current 3.8 mA, p1). Dissipation about (11.7 - 5) V x 4 mA = 27 mW.
- Open condition: the CD40106 at VDD 5 V needs TP83 above VT+ (3.6 V max, p5-p6). If TP83 is 3.3 V logic (E-09 UNVERIFIED), triggering is not guaranteed and this stage must be redesigned (Q15); do not tap the synth's +3V3ARM (audit B09).

### 3.5 Gate A:1 into the Pico: no 5 V net reaches a GPIO

Provisional (audit recommendation, owner has not confirmed), with one justified change: the audit recommends a CD4049UBE on Pico 3V3 as the level shifter. Because the CD4049UB datasheet itself says its inputs have clamp diodes to VCC (p17), a 5 V input to a 3.3 V-powered 4049 would push current into the Pico 3V3 rail, and in S2 into the unpowered rail. A resistive divider into a fault-tolerant RP2040 GPIO avoids both:

A:1 -> (gate panel jack tapped here) -> 22k -> node -> 33k to GND; node -> Pico GPIO (an FT pin; GP11 was the example, but it is now OLED CS (owner ruling, 2026-10-17), so no FT pin is free and the pin is OPEN; no firmware change in this task).

- High level: 5 V x 33k / (1k + 22k + 33k) = 2.95 V at a 5.0 V CD40106 supply; above RP2040 VIH 2.0 V and below 3.63 V (FT limit) and IOVDD + 0.5 V = 3.8 V. The 78L05 output tolerance was not read for this note; a +/-5 % supply would give 2.80-3.09 V (UNVERIFIED margin, BT-5).
- No 5 V net touches a GPIO: the highest node voltage is the divided value. The validator rule (plan Task 8) sees a `DIV` endpoint.

| State | Current path |
|---|---|
| S0 | None. |
| S1 | Cable side is the unpowered CD40106 output; the 33k pulls the node low; no expander-side pull-up exists (r2: keep every gate pull-up on the MB side), so nothing flows toward the synth. GPIO reads gate off. |
| S2 | CD40106 high into an unpowered FT pin: Thevenin source 2.95 V through 13.6k. Exceeds Table 622 abs max (2.95 V vs 0.5 V on an unpowered RP2040), relies on Table 614 FT ("very little current", p613), provisional. Worst case if it behaved like a clamp: (2.95 - 0.6) / 13.6k = 0.17 mA. BT-5 measures the pin current. |
| S3 | Normal. Edge: 13.6k into the pin capacitance (a few pF) is far faster than any gate. |

### 3.6 A outputs (A:2 to A:8)

| State | Current path |
|---|---|
| S0 | None. |
| S1 | MB followers unpowered. Expander jacks are passive, so the expander drives nothing into the MB. A rack module output wrongly patched into an expander output jack would drive the MB follower output through 1k; this is misuse, not a design path. |
| S2 | MB followers (about +/-5 V typical, peaks UNVERIFIED E-19) through 1k (220 ohm on pitch) into whatever rack input is patched, which is unpowered: limited by that module's input resistor (typically 100k, UNVERIFIED) to about 0.1 mA. No expander IC is on these lines. If an A line is normalled into an expander circuit, use at least 100k at that input so S2 current is at most about 0.1 mA, far below the TL07x 10 mA input limit (p10). |
| S3 | Normal. |

### 3.7 Clock jacks on the expander

Both clock jacks and the Pico are in the rack domain; no clock wire crosses to the synth (audit N08). The synth states do not apply; the relevant extra state is the Pico on USB with the rack off.

- Clock IN: jack -> 100k pull-down to GND at the jack -> 100k series -> CD4049UB section (VCC = Pico 3V3) -> second section -> GP21 (r3, audit S46). A +10 V input pushes at most (10 - 3.3 - 0.6) / 100k = 61 uA into the 4049's VCC clamp, which the powered 3V3 rail absorbs; a -10 V input pushes 94 uA through the VSS clamp, far under the +/-10 mA DC clamp rating (p5). The RP2040 pin only ever sees the 4049 output (0-3.3 V). With the Pico on USB and the rack off, the source module is off.
- Clock OUT: GP22 -> CD4049UB section -> second section -> 1k -> jack. The buffer takes any mis-patch fault instead of the RP2040, whose per-pin injection limit is NOT FOUND in the datasheet (DATASHEETS (d)). Whether the 4049 output tolerates a mis-patched +/-10 V through 1k (about 6 mA) is UNVERIFIED (Q16). With the rack off and the Pico on USB, the output drives an unpowered rack input through 1k plus that input's own resistor.
- These four sections use one of the three owned CD4049UBE packages.

### 3.8 Per-line summary (for the connection map and the Task 8 validator)

| Line | Source | Destination | Series R | Protection | Powered-side assumption |
|---|---|---|---|---|---|
| B:1 UART TX | Pico GP0 | LPC P0.16 RXD1 (pin 63) | 1k expander + 1k MB | Firmware: GP0 high-Z until GP1 high | Pico never drives into an unpowered LPC |
| B:6 UART RX | LPC P0.15 TXD1 (pin 62) | Pico GP1 | 1k MB + 1k expander | GP1 fault tolerant; pull-down | LPC may drive while Pico is off: exceeds Table 622 abs max, relies on Table 614 FT, provisional (BT-2) |
| B:5 Filter CV | Expander op-amp | TP26 | 10k expander + 100k MB | 2x BAT85 to +/-12V_BRK, 1 nF | Either side may be off |
| B:3 VCA CV | Expander op-amp | TP10 | 10k expander + 100k MB | 2x BAT85 to +/-12V_BRK, 1 nF | Either side may be off |
| A:1 Gate | MB CD40106 (5 V) | Gate jack; Pico FT GPIO (pin OPEN, CM 12G) | 1k MB; 22k / 33k divider expander | Divider; no expander pull-up | Either side may be off |
| A:2 Pitch | Stock pitch buffer | Jack | 220 ohm MB | - | - |
| A:3-A:8 | MB followers | Jacks | 1k MB | >= 100k into any expander circuit | Synth may drive while rack is off |
| Clock IN | Rack jack | GP21 | 100k | 2x CD4049UB on 3V3, 100k pull-down | Rack domain only |
| Clock OUT | GP22 | Rack jack | 1k | 2x CD4049UB on 3V3 | Rack domain only |

### 3.9 Alternative: PC817-isolated UART (documented option, not the decided design)

The decided UART (3.1) stays as written; it is provisional because it relies on the RP2040 FT sentence and on an unpowered LPC pad. This section evaluates the owned PC817 (10-20 owned, owner to confirm) as a replacement for both UART directions. Datasheet: Sharp PC817X Series, sheet D2-A03101EN (`datasheets/PC817/73758.pdf`, read for this note); a second Sharp sheet (OP18002EN, PC817XxNSZ1B) gives the same IC, fc, tr and tf rows (its cover page states CTR 50-400 % instead of 50-600 %). The owned parts come from an assortment: maker, CTR rank mark and whether they meet the Sharp figures are UNVERIFIED.

Datasheet figures used (Ta = 25 C):
- LED: IF abs max 50 mA, VR abs max 6 V (p4); VF 1.2 V typ, 1.4 V max at IF 20 mA (p4); about 1.1 V at 3-5 mA (Fig. 7, p7, typical curve, reference only).
- CTR: IC 2.5-30 mA at IF 5 mA, VCE 5 V, i.e. CTR 50-600 % (p4); ranks A-D from 4-8 mA up to 15-30 mA (p5). No minimum is given at any other IF; "while operating at IF < 1.0 mA, CTR variation may increase" and IRED output degrades by about 50 % over 5 years (p9).
- Speed: fc 80 kHz typ at VCE 5 V, IC 2 mA, RL 100 ohm (p4); tr 4 us typ / 18 us max, tf 3 us typ / 18 us max at VCE 2 V, IC 2 mA, RL 100 ohm (p4). Fig. 13 (p8, "for reference and not for guarantee") shows tr and tf rising with load resistance: about 20 us each at RL 1k and about 50-75 us at 10k; read at RL 4.7k by log interpolation, about 40-50 us. Fig. 15 (p8) puts the -3 dB point near 20-30 kHz at RL 1k and a few kHz at 10k (reference only).
- Dark current ICEO at most 100 nA at VCE 50 V (p4).
- Drivers: LPC2361 IOH / IOL 4 mA at VOH = VDD - 0.4 V / VOL = 0.4 V, VIL 0.8 V (Table 5, p34). RP2040 VOL at most 0.5 V and VOH at least 2.62 V at the selected 2 / 4 / 8 / 12 mA drive, VIL 0.8 V, total IOVDD current 50 mA (Table 625, p616-p617).

Topology (chosen so that polarity is kept, no supply crosses the cable and the B map does not change):
- One PC817 per direction, at the receiver end. The driver GPIO drives the LED directly: driver TX pin -> 560 ohm on the driver board -> cable -> PC817 LED anode on the receiver board; LED cathode to the receiver board's ground star, returning over the shared cable grounds.
- Output as an emitter follower: collector to the receiver's own supply, emitter to the receiver's RX pin with 4.7k to the receiver's ground. LED on (TX high, the idle state) gives RX high, so the UART is not inverted.
- B:1 carries the Pico-to-LPC LED drive, B:6 the LPC-to-Pico LED drive. The ground pins stay as in 2.2. The 1k series resistors of 3.1 are not used (the 560 ohm takes their place); a cable short to ground draws at most about 3.9 mA from the driver.

LED current (the driver sources it, TX high = LED on): IF = (VOH - 1.1) / 560. LPC: VOH at least 2.9 V (p34) gives at least 3.2 mA. RP2040: VOH at least 2.62 V at the 4 mA setting (p617) gives at least 2.7 mA. Either way at most (3.3 - 1.1) / 560 = 3.9 mA, within the 4 mA figure of both drivers. Because UART idle is high, each LED is lit whenever its driver is idle, so each side spends about 3-4 mA continuously while the bridge runs, and the LEDs age faster than with a short duty cycle (p9).

Output level: high needs IC x 4.7k above VIH 2.0 V, i.e. IC at least 0.43 mA; the follower then saturates near the receiver supply. Assuming CTR at least 50 % at IF 2.7 mA (UNVERIFIED: the minimum is only specified at 5 mA, though the typical CTR curve, Fig. 6 p6, is higher at 3 mA than at 5 mA), IC is at least 1.35 mA new and 0.68 mA after the 50 % degradation (p9): margin about 1.6x. Low is dark current only (100 nA x 4.7k = 0.5 mV). A 1k load would need IC 2 mA for VIH, i.e. CTR about 75 % new and 150 % after degradation at IF 2.7 mA, which only rank B or higher would cover (rank figures are at 5 mA, p5; owned rank UNVERIFIED). 4.7k is therefore the load that works on the guaranteed figures.

Maximum baud: working criterion (this note, not a datasheet rule): each edge at most about 25 % of a bit, so the receiver's mid-bit sample sees a settled level.
- 115200 (bit 8.68 us): does not work. Even at RL 100 ohm, which this circuit cannot use, tr and tf are up to 18 us (p4), longer than two bits.
- 38400 (bit 26 us): does not work. Edges of about 20 us at 1k and 40-50 us at 4.7k (Fig. 13) are as long as or longer than a bit.
- 19200 (bit 52 us): not expected with the 4.7k load (edges near a whole bit); possibly with a 1k load and a rank B-D part (edges about 40 % of a bit): UNVERIFIED.
- 9600 (bit 104 us): marginal with 4.7k (edges about 40-50 % of a bit): UNVERIFIED, bench check BT-13.
- 4800 (bit 208 us): expected to work with 4.7k (edges about 25 % of a bit), on reference curves only: UNVERIFIED until BT-13.
The Fig. 13 curves are for VCE 2 V and IC 2 mA in the linear region; in this circuit the transistor saturates at about 0.7 mA, where turn-off can be slower. All baud figures above are UNVERIFIED until BT-13 is done on the owned parts.

Back-feed, per power state: S1 (synth off): GP0 drives the Pico-to-LPC LED, which sits on the MB board and returns to ground; no IC pin is on that path. The unpowered LPC RX pin sees the phototransistor emitter with the collector on the unpowered MB supply, so there is no source on the LPC side. The LPC-driven line (B:6) connects only to the unpowered LPC pin through 560 ohm and the LED, which the Pico side does not drive. S2 (Pico off): the mirror image. No GPIO of an unpowered chip is driven above 0 V by the other system in any state, so the Table 622 / Table 614 conflict (3.1) and the unpowered LPC pad limit (Table 4, p33) no longer apply to the UART. The firmware rule of 3.1 is no longer needed for protection, but GP1 still reads low when the LPC is off, so it can stay as the "LPC alive" sense (with the same UART-break caution).

What each side's supply must provide:
- Pico side: 3-4 mA from GP0 for the TX LED (sourced through IOVDD, inside the 50 mA total), and at most 3.3 V / 4.7k = 0.7 mA through the RX phototransistor from Pico 3V3.
- MB side: 3-4 mA from the LPC TXD1 pin for the RX LED (from the LPC's own supply through its pin), and a collector supply for the TX phototransistor, at most 0.7 mA. The MB board has no 3.3 V rail of its own. Options: (a) a resistor tap on the synth's +3V3ARM, which audit B09 rejects for the gate stage and the owner would have to accept here; (b) the Provisional 78L05 (5 V): RXD1 (pin 63) is a 5 V tolerant pad, but -0.5 to +6.0 V is "only valid when VDD(3V3) is present" (Table 4, p33), so it depends on the 78L05 not coming up before the LPC's 3.3 V (sequencing UNVERIFIED); (c) common-emitter output with the LPC's internal pull-up (15-85 uA, p34) and no rail, which inverts the signal and is far too slow (about 40-220k equivalent). None is free of a new owner decision (Q20).

Ground: in this topology the LED currents return over the shared cable grounds, so the UART does not break any ground path. Full galvanic isolation of the UART would need each LED's return on its own conductor (2 more pins). On DB-9 B that leaves 3 ground pins for 2 CVs; by the neighbour table (2.1) pin 5 is the only CV position with only-ground neighbours, so the second CV would have to sit next to a UART return. And the synth and rack grounds stay joined by A:9 and the remaining B grounds, which the CV, gate and audio lines need, so isolating the UART alone gives no hum benefit (4.1). Not recommended.

Consequences for the DB-9 B map: none in the recommended topology (B:1 and B:6 change from logic lines to LED drive lines, about 3-4 mA DC while idle instead of near zero). Parts: 2x PC817, 2x 560 ohm, 2x 4.7k, all owned (resistor values Q5).

Verdict: the PC817 UART removes UART back-feed in every power state and needs only owned parts, but it does not work at 115200 or 38400; 9600 is marginal and 4800 is the realistic rate, both UNVERIFIED until BT-13. It costs an MB-side collector supply (Q20). It is worth taking only if BT-2 fails or the bridge can live with 4800-9600 baud.

## 4. Hum design

### 4.1 Ground topology

- Exactly one ground connection between the synth and the rack: the cable ground conductors (A:9; B:2, B:4, B:7, B:8, B:9), six conductors in two cables, all running between the same two star points. Strictly they form small loops (between the conductors inside each cable, and between the two cables); keeping both cables bundled and short keeps that loop area small, so they are not expected to pick up mains hum the way a second, separately routed ground would (r5 F-05). Measured by BT-9.
- MicroBrute side: every cable ground pin and the breakout ground go by their own short wires to the TP72 star (TPV:27), not through the breakout's ground strip (audit N13). The breakout takes power only from TP70 / TP71 / TP72.
- Expander side: every cable ground pin, the Pico GND and all expander circuit grounds meet at one star point where the rack 0 V enters at the 16-pin header.
- No other synth-to-rack path: no separate clock cable (audit N08), no chassis or panel bond between the two cases, and the USB rule below.
- The earth status of the two adapters (class II or not) is UNVERIFIED (audit N06); if either is earthed, mains earth is part of any loop.
- Outside this design: both systems' audio outputs going to the same mixer or interface form a loop through the audio cables (r2). The cable design cannot cut that loop; the ladder in 4.5 handles it.

### 4.2 Shield termination (resolves audit conflict C8)

Rule: each cable's braid is bonded to its connector shell at the MicroBrute end only, and that MB-side panel connector shell is wired with a short lead to TP72. At the expander end the braid is cut back and insulated inside the hood, and the expander panel connector's shell is isolated from the aluminium panel with insulating shoulder washers (Missing, Q10). The shield never carries signal return; returns stay on the ground pins.

Why the MicroBrute end: it matches the existing CM rule and two of the three reviewers (r3, r5; r2 preferred the expander end). The shield then drains into TP72, the node where every cable return already meets, instead of into the expander panel and rack rails, whose bond to rack 0 V is unknown. The MB rear panel appears to be plastic (r5, IMG_6973; UNVERIFIED), so the MB shell does not touch another ground. A molded off-the-shelf cable bonds the braid at both hoods (r2 P-D3, r5 F-06): it must be modified or built. Shell-to-panel continuity on both ends is checked in BT-8 (E-15). If the owner rejects washers, the fallback is r2's rule (bond at the expander end, cut at the MB end), tried in ladder step 3.

### 4.3 USB ground

Rule: no USB cable on the Pico while the expander is rack-powered and the DB-9 cables are connected. Flash and debug the Pico with the DB-9 cables unplugged. Reason: the Pico micro-USB ties expander ground to the computer, and the MicroBrute's own USB to the same computer then closes a loop through the cable ground (audit S25). No USB isolator is owned. USB and rack 5 V at the same time is electrically safe for the Pico (on-board VBUS Schottky, Pico datasheet p21-p22); the rule is about hum only. Consequence: runtime USB-MIDI from the Pico (CM:67-70) cannot be used with the cables connected without an isolator (Q17).

### 4.4 Pin interleaving

DB-9 B: the UART pair sits at the pin-1 end; each CV pin has only ground neighbours (section 2.2). DB-9 A: no free pin; order kept (section 2.3). Both cables are run together and kept short to keep the loop area between the two cable grounds small. Maximum cable length: 1 m working figure (audit S38, r3), UNVERIFIED until BT-6 measures the cable capacitance and BT-1 the UART edges.

### 4.5 Fallback ladder (owned parts only, in order of cost)

Do each step only if hum or noise is still measured after the previous one (BT-9). The "100 nF in series with the ground pin" fix in the current docs is wrong (it removes the DC ground reference for CV, gate and UART; audit S23) and is not part of this ladder.

1. No parts: confirm the baseline. USB unplugged (4.3); no clock cable; cables bundled and short; both adapters on the same mains strip; measure with each cable unplugged in turn to locate the loop.
2. No parts: re-wire any ground that does not go to its star by its own lead (4.1); confirm no case-to-case contact.
3. No parts: swap the shield bond to the expander end (r2's rule) and compare; keep whichever measures lower. In the swapped arrangement the braid is bonded at the expander hood; because the expander panel shell is isolated by the washers (4.2), wire that expander shell with a short lead to the expander star (rack 0 V); cut the braid back and insulate it inside the MB-end hood, and leave the MB shell's lead to TP72 in place or remove it (compare both).
4. Owned resistor kit plus two BAT85 (conditional): on the expander, break the ground bundle from the expander star with 10 ohm, bypassed by 100 nF (owned) in parallel and two anti-parallel BAT85 so fault current has a path. This keeps the DC reference (r2 step 4, r3 H-1). Condition: all 10 owned BAT85 are already allocated (section 1.2), so this step can only be built from BAT85 if two are freed by taking the series-resistor option on the breakout rails (audit C12, Q3). Since the owner's kit has 1N4148 (25+) and 1N5819 (x10), the anti-parallel pair can instead be two owned 1N4148 or 1N5819 (provisional; the forward voltage differs from BAT85, so the checks below matter more). Without the diodes, 10 ohm in parallel with 100 nF still keeps the DC reference, but a fault current between the systems then has only the 10 ohm path (it would burn the resistor): flagged, not recommended. Recheck BT-2, BT-3 and BT-5 afterwards: the gate, CV and UART references now ride on up to the BAT85 forward voltage.
5. Owned op-amps (TL072) and resistors: dedicate one B ground pin (for example B:8) as a no-current ground-sense wire from TP72 and use it as the reference of difference-amplifier receivers on the expander's audio inputs (r2 step 3). Needs matched resistors (1 % parts are not owned, Q5).
6. Owned isolation transformer on the single worst audio line only, after its characterisation (E-29). It passes no DC, so never on CV, gate or UART (r2, r3).

## 5. GPIO note

With I2C off the cable and EFFIGY shelved, GP2, GP3 and GP11 were free when this note was written. Update (owner ruling, 2026-10-17): they are now the SPI main OLED's SCK, MOSI and CS, so only these Pico pins are free:

| GPIO | Physical pin | Type (RP2040 datasheet) | Note |
|---|---|---|---|
| GP26 | 31 | Digital IO / ADC0, not FT, diode to IOVDD (Pico p20) | PWM slice 5A is shared with GP10 (LED_MODE) (audit S02). |
| GP27 | 32 | Digital IO / ADC1, not FT | - |
| GP28 | 34 | Digital IO / ADC2, not FT | - |

Rule: any input that can see a signal from the cable or a jack while the Pico may be unpowered goes on an FT pin (GP0-22), not on GP26-28.

Update (owner ruling, 2026-10-17): no FT pin is free, so the gate mirror of A:1 (section 3.5) has no pin under this rule. Options for the owner, none chosen here:

1. Tie the OLED CS input permanently low, if the module allows it; that frees GP11 (FT). UNVERIFIED and module-dependent.
2. Use GP27 or GP28 and accept the clamp current in S2: about 0.17 mA worst case by the section 3.5 arithmetic ((2.95 - 0.6) V / 13.6k). Bench-test with BT-5.
3. Add a series diode or a 3V3-powered buffer in front of a GP26-28 pin; needs a part decision.

## 6. Open items and bench checks

### 6.1 Owner questions

| ID | Question |
|---|---|
| Q1 | Buy an LF398N and a 10 nF polystyrene or polypropylene hold capacitor? No owned equivalent. |
| Q2 | Vactrol marking (part number, LED forward-current rating). Needed for the TL072 V-to-I driver's sense resistor. |
| Q3 | BAT85 stock is exactly used up (10); approve, or free two by using a series resistor on the breakout rails (C12)? |
| Q4 | 1N4148 stock for the slew limiter: the owner's pasted inventory says 25+; confirm from the kit card. |
| Q5 | The resistor kit is Have: confirm 220R, 1k, 2k, 4.7k, 10k, 22k, 33k, 100k are present, plus 10 ohm, 560 ohm, 680 ohm and 1M; its series (E12 / E24) and power rating; any 1 % parts for ladder step 5? |
| Q6 | LFO timing: buy a film capacitor and 1M pots, or accept a different range with owned parts? |
| Q7 | Aux-out trimmers: buy or use fixed resistors? |
| Q8 | Type of the 25 owned 3.5 mm jacks (panel mount, Thonkiconn-compatible?). |
| Q9 | DB-9 count: 4 panel connectors plus 2 shielded cables needed; the owner has "several" connectors (count UNVERIFIED; the earlier list said 2; gender and flange unknown). |
| Q10 | Insulating shoulder washers for the expander-side DB-9 shells, or accept the alternative shield rule? |
| Q11 | Keyed Eurorack 16-pin header and ribbon. |
| Q12 | RGB LED and tactile button for the expander UI. |
| Q13 | Stripboard, IC sockets, hook-up wire on hand? |
| Q14 | Keep the DB-9 A order (recommended) or adopt r5's re-order if BT-9 shows gate crosstalk on Pitch? |
| Q15 | If TP83 is 3.3 V logic, how should the gate stage change (no synth 3V3 tap allowed)? |
| Q16 | Is mis-patch protection on Clock OUT worth more than the 4049 buffer plus 1k? |
| Q17 | Is runtime USB-MIDI from the Pico needed while the synth is connected? If yes, an isolator must be bought. |
| Q18 | List the further components not in the 2026-10-17 photo, and send close-ups of the assortment kit's insert card (transistor, diode, LED and trim-pot types; resistor values). |
| Q19 | Firmware mute of the CV outputs until the synth is seen powered (section 3.3): wanted? |
| Q20 | PC817-isolated UART (section 3.9): accept a bridge baud of 4800-9600 (115200 and 38400 do not work) in exchange for zero UART back-feed? If yes, which MB-side collector supply: a +3V3ARM tap (against audit B09) or the Provisional 78L05 (power-up sequencing UNVERIFIED)? |
| Q21 | Pico variant: the package says "Raspberry Pi Pico" (no W), the docs say Pico WH, another description says "Pico H". Which is it? Nothing here uses wireless; docs may need renaming once confirmed. |
| Q22 | Main OLED: the baseline is now the owner's 1.3 inch 7-pin SPI module (owner ruling, 2026-10-17; the 4-pin I2C module is in a TD-3). Owner to read its chip marking (SSD1306 or SH1106, UNVERIFIED) and pin order, and to confirm whether the 0.96 inch SSD1306 has arrived. Pins: SPI0 SCK = GP2, MOSI = GP3, DC = GP4, RES = GP5, CS = GP11; free pins are GP26-28 only. |
| Q23 | Connector: RESOLVED (owner, 2026-10-17): CONFIRMED as 2x DB-9. The VGA / HD-15 line in a pasted inventory was an error (HD-15 rejected because the cable shorts pins 6-8 to ground). |
| Q24 | The owner's earlier IC list could not be found in local history and a shared chat link was not readable. Re-send it if it differs from the 2026-10-17 photo. |

Other open items carried from the audit: LPC bridge UART choice (B01, E-01); CV depth and injection resistors (E-18); TP83 level (E-09); rear-panel and connector dimensions (E-20, E-21); expander width (decision e).

### 6.2 Bench checks that settle each UNVERIFIED value

| ID | Check | Pass criterion | Settles |
|---|---|---|---|
| BT-1 | Scope the UART edge at each receiver pin with the real cable and 1k + 1k. | 10-90 % rise at most 0.9 us (about 10 % of a bit at 115200). | UART series R, cable length |
| BT-2 | UART back-feed: S1 with the Pico running, measure LPC +3V3ARM (P4 pin 5) and the B:1 pin; S2 with the LPC bridge firmware idling (and again with stock firmware), measure Pico 3V3 (pin 36), the GP1 and GP0 pin voltages, and the pin current: the voltage across the receiver-end 1k (1 mV = 1 uA), or a uA meter in series with the pin. | Unpowered rail below about 0.3 V and pin current in the "very little" range (record it; propose under 10 uA as the working limit, UNVERIFIED since the datasheet gives no number). If not, raise the receiver-end resistor to 2.2k and repeat BT-1, or take the PC817 alternative (3.9). | RP2040 FT behaviour, LPC unpowered pad (E-11) |
| BT-3 | CV back-feed: S1 with both expander CV outputs at their maximum, measure +12V_BRK, -12V_BRK, TP70, TP71. | Below about 0.3 V. | CV series values, rail-diode choice (C12) |
| BT-4 | CV depth: S3, sweep each CV and compare filter and VCA response with and without the 100k. | Owner judges the depth acceptable; else 47k and repeat BT-3. | E-18 |
| BT-5 | Gate: scope TP83 high and low; scope the CD40106 output and the Pico GPIO node; then in S2 measure Pico 3V3 and the current into the GPIO pin (uA meter between the divider node and the pin, or compute it from the 22k / 33k node voltage with and without the pin connected). | TP83 high above 3.6 V for a 5 V CD40106; node 2.6-3.2 V high, below 0.3 V low; in S2 Pico 3V3 below 0.3 V and pin current in the "very little" range (working limit under 10 uA, UNVERIFIED). | E-09, divider margin, 78L05 need, FT behaviour |
| BT-6 | LCR meter on each cable: one conductor to all others plus shield. | Record pF/m; recompute BT-1 margins. | E-13 |
| BT-7 | Caliper the owner's DB-9 insert (or obtain its drawing) for row offset and pin numbering. | Neighbour table in 2.1 confirmed. | Pin-map geometry |
| BT-8 | Continuity: MB shell to TP72; expander shell to panel and to rack 0 V. | Under 1 ohm at the MB end; open at the expander end. | E-15, shield rule |
| BT-9 | Hum and crosstalk: record the MB audio output and the expander outputs into one interface, cables connected, USB off; then Pitch and VCF with the gate toggling. | No audible hum; no visible gate edges on Pitch. Work the ladder in 4.5 if not. | Hum design, A order (Q14) |
| BT-10 | CD4049UB input: with VCC = 3.3 V, apply 5 V through 100k and measure input current and VCC rise; repeat with VCC unpowered. | Confirms whether the input clamps to VCC (TI p1 vs p17). | C16, E-10 |
| BT-11 | Clock IN: feed +/-10 V through the 100k into the 4049 stage. | GP21 stays within 0-3.3 V; 3V3 rail unchanged. | Clock IN protection |
| BT-12 | Meter the CP1A bus slot pins 11-12 for +5 V. | Present. | E-14 |
| BT-13 | Only if the PC817 alternative (3.9) is considered: build one direction with an owned PC817, 560 ohm and 4.7k on the real cable; send a repeating 0x55 pattern at 4800, 9600 and 19200 baud; scope the receiver pin and run a loop-back byte-error count. Also read the part's rank mark. | Edges at most about 25 % of a bit and no byte errors over a long run at the chosen baud. | PC817 baud, CTR rank |
