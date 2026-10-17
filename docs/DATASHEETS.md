# MACROBRUTE reference datasheets

Collected 2026-10-16. Local copies live in `datasheets/<PART>/` (git-ignored: manufacturer
documents are not ours to redistribute). Re-download from the URLs below.

Page numbers below are **PDF page numbers** (page index within the file), which can differ from the
printed page number on the sheet. All downloaded files were checked with `file` (PDF/GIF/HTML as listed).
Text was read with `pdftotext` only.

## Part table

Status: **downloaded** = file present locally; **partial** = a related or older/mirror document only;
**NOT FOUND** = no usable document obtained.

| Part | Role in project | Manufacturer | Official / source URL | Local path (under `datasheets/`) | Doc revision / date | Status |
|---|---|---|---|---|---|---|
| TL074 | Quad JFET op-amp, MB-side buffers | Texas Instruments | https://www.ti.com/lit/ds/symlink/tl074.pdf | `TL074/tl074.pdf` | SLOS080W, Jul 2025 (shared TL071/2/4 sheet) | downloaded |
| TL072 | Dual JFET op-amp, slew limiter, CV out | Texas Instruments | https://www.ti.com/lit/ds/symlink/tl072.pdf | `TL072/tl072.pdf` | SLOS080W, Jul 2025 (same file as TL074) | downloaded |
| LM358 | LED driver / single-supply op-amp | Texas Instruments | https://www.ti.com/lit/ds/symlink/lm358.pdf | `LM358/lm358.pdf` | SLOS068AB, Oct 2024 | downloaded |
| LM393 | Comparator (referenced in docs) | Texas Instruments | https://www.ti.com/lit/ds/symlink/lm393.pdf | `LM393/lm393.pdf` | SLCS005AH, Apr 2025 | downloaded |
| NE5532 | Alternative to TL072 (BOM note) | Texas Instruments | https://www.ti.com/lit/ds/symlink/ne5532.pdf | `NE5532/ne5532.pdf` | SLOS075K, Dec 2025 | downloaded |
| LM13700 | Dual OTA (dropped from BOM, kept for reference) | Texas Instruments | https://www.ti.com/lit/ds/symlink/lm13700.pdf | `LM13700/lm13700.pdf` | SNOSBW2F, Nov 2015 | downloaded |
| CD40106B | Hex Schmitt trigger, gate buffer | Texas Instruments | https://www.ti.com/lit/ds/symlink/cd40106b.pdf | `CD40106/cd40106b.pdf` | SCHS097F, Mar 2017 | downloaded |
| CD4049UB | Hex inverting buffer / level shifter | Texas Instruments | https://www.ti.com/lit/ds/symlink/cd4049ub.pdf | `CD4049UBE/cd4049ub.pdf` | SCHS046L, Feb 2026 | downloaded |
| CD4051B | 8-ch analog mux | Texas Instruments | https://www.ti.com/lit/ds/symlink/cd4051b.pdf | `CD4051/cd4051b.pdf` | SCHS047O, May 2026 | downloaded |
| CD4066B | Quad bilateral switch (referenced; replaced by CD4051) | Texas Instruments | https://www.ti.com/lit/ds/symlink/cd4066b.pdf | `CD4066/cd4066b.pdf` | SCHS051J, Aug 2024 | downloaded |
| CD4024B | 7-stage counter (dropped; clock div in firmware) | Texas Instruments | https://www.ti.com/lit/ds/symlink/cd4024b.pdf | `CD4024/cd4024b.pdf` | SCHS030D, Dec 2003 | downloaded |
| LF398 (LF198/LF298/LF398-N) | Sample and hold | Texas Instruments (ex National) | https://www.ti.com/lit/ds/symlink/lf398-n.pdf | `LF398/lf398-n.pdf` | SNOSBI3C, Oct 2018 | downloaded |
| Owned-alternative S&H (CD4051/CD4066 + cap, per docs) | n/a | n/a | n/a | see CD4051 / CD4066 above | n/a | no separate S&H IC named in docs besides LF398 |
| BAT85 | Schottky, substitute for BAT54S | Philips/NXP (Nexperia successor) | https://www.nexperia.com/products/diodes/schottky-diodes-and-rectifiers/ (Nexperia direct PDF URL returned HTML) | `BAT85/bat85-nxp-mirror-aau.pdf` (2000 May 25), `BAT85/bat85-cryptomuseum.pdf` (1996 Mar 20) | Philips product spec 2000-05-25 (mirror copies; manufacturer URL not retrievable) | partial (original Philips data sheet via mirror) |
| BAT54S | Dual Schottky (SOT-23) | Diodes Inc | https://www.diodes.com/assets/Datasheets/ds11005.pdf | `BAT54S/bat54-series-diodes.pdf` | DS11005 Rev. 34-2, 2023 | downloaded |
| 1N5817 | Pico power Schottky | Vishay; Diodes Inc | https://www.vishay.com/docs/88525/1n5817.pdf ; https://www.diodes.com/assets/Datasheets/ds23001.pdf | `1N5817/1n5817-vishay.pdf`, `1N5817/1n5817-diodes.pdf` | Vishay 88525 rev 01-Jul-2020; Diodes DS23001 Rev. 10-2, Apr 2023 | downloaded |
| 1N4148 | Signal diode | Vishay | https://www.vishay.com/docs/81857/1n4148.pdf | `1N4148/1n4148.pdf` | Rev. 1.6, 07-Nov-2024 | downloaded |
| 2N3904 | Noise source, LED/gate drivers | onsemi (2N3903/2N3904 combined sheet) | https://www.onsemi.com/products/discrete-power-modules/bipolar-junction-transistors-bjt/2n3904 (direct PDF URL returned HTML) | `2N3904/2n3904-onsemi-mirror.pdf` | 2N3903/D Rev. 8, Aug 2012 (mirror copy) | partial (mirror of onsemi sheet) |
| BSS138 | Level-shift MOSFET (Pico BOM) | Diodes Inc | https://www.diodes.com/assets/Datasheets/BSS138.pdf | `BSS138/bss138-diodes.pdf` | undated (no revision string found) | downloaded |
| 78L05 | 5 V regulator (owned x4) | Texas Instruments (uA78L family) | https://www.ti.com/lit/ds/symlink/ua78l.pdf | `78L05/ua78l.pdf` | SLVS010X, Jun 2023 | downloaded |
| 6N138 | MIDI optocoupler (optional) | Vishay (6N138/6N139 sheet) | https://www.vishay.com/docs/83605/6n139.pdf | `6N138/6n138-139-vishay.pdf` | Doc 83605 Rev. 2.2, 29-May-2026 | downloaded |
| MCP4728 | 4-ch 12-bit I2C DAC | Microchip | https://ww1.microchip.com/downloads/en/DeviceDoc/22187E.pdf | `MCP4728/22187E.pdf` | DS22187E, 2010 | downloaded |
| MCP4725 | 12-bit I2C DAC (optional BOM item) | Microchip | https://ww1.microchip.com/downloads/en/DeviceDoc/22039d.pdf | `MCP4725/22039d.pdf` | DS22039D, 2009 | downloaded |
| LPC2361 data sheet | MicroBrute MCU (ARM7, LQFP100) | NXP | NXP product page lists LPC2361_62.pdf Rev. 5.1 (Oct 2013) but the nxp.com PDF URL returned 404/HTML to curl; copy from Keil: https://www.keil.com/dd/docs/datashts/philips/lpc2361_62_ds.pdf | `LPC2361/lpc2361_62_ds-keil.pdf` | LPC2361/62 Rev. 03, 11 Nov 2008 | partial (older revision, via Keil) |
| LPC2361 errata | Silicon errata | NXP | https://www.keil.com/dd/docs/datashts/philips/lpc2361_es.pdf | `LPC2361/lpc2361_errata-keil.pdf` | Version 1.1, 11 May 2009 | partial (older) |
| UM10211 | LPC23xx user manual | NXP | https://www.keil.com/dd/docs/datashts/philips/lpc23xx_um.pdf (nxp.com UM10211.pdf returned HTML) | `LPC2361/lpc23xx_um_UM10211_rev02-keil.pdf` | UM10211 Rev. 02, 11 Feb 2009 (covers LPC2361/62, added in this rev) | partial (older revision, via Keil) |
| RP2040 datasheet | Pico MCU | Raspberry Pi | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | `RP2040/rp2040-datasheet.pdf` | build-date 2025-02-20 (build 3184e62) | downloaded |
| Hardware design with RP2040 | Pico design guide | Raspberry Pi | https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf | `RP2040/hardware-design-with-rp2040.pdf` | undated in text | downloaded |
| Raspberry Pi Pico | Expander controller (standard Pico) | Raspberry Pi | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | `Pico/pico-datasheet.pdf` | Release 21, build 03/07/2026 | downloaded |
| Raspberry Pi Pico W datasheet (owned board: Raspberry Pi Pico (any variant with the standard 40-pin layout; RP2040 electrical facts quoted here come from the RP2040 datasheet and were not checked against Pico 2/RP2350)) | Expander controller as owned | Raspberry Pi | https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf | `Pico_W/pico-w-datasheet.pdf` | Release 7, build 03/07/2026 | downloaded |
| SSD1306 | 0.96" / 0.91" OLED controller | Solomon Systech | https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf (distributor copy) | `SSD1306/SSD1306.pdf` | Rev 1.1, Apr 2008 | downloaded |
| SH1106 | 1.3" OLED controller | Sino Wealth / Sino One (distributor copy) | https://www.pololu.com/file/0J1813/SH1106.pdf (distributor copy) | `SH1106/SH1106.pdf` | no revision string in file | downloaded |
| KY-040 / HW040 encoder module | Panel encoder | Keyes / Joy-IT (no manufacturer sheet) | n/a | none | n/a | NOT FOUND (module has no manufacturer datasheet; download attempts returned HTML) |
| PT2399 | Delay IC (spinoff only) | Princeton Technology | princeton.com.tw URL returned HTML; mirrors used | `PT2399/pt2399-chipdip.pdf` (V1.6, Feb 2010), `PT2399/pt2399-v1.2-mirror-sound-au.pdf` (v1.2, Sep 2000) | V1.6 Feb 2010 / v1.2 Sep 2000 | partial (distributor/mirror copies) |
| VTL5C3 vactrol / LDR04 / BF245C / BC547 | Vactrol and driver parts named in docs | Excelitas (ex PerkinElmer) / onsemi / various | n/a | none | n/a | NOT FOUND (manufacturer URLs tried returned HTML; LDR04 has no identified manufacturer) |
| Thonkiconn PJ398SM / PJ301M-12 | Panel jacks | Thonk (Qingpu WQP518MA family) | n/a | none | n/a | NOT FOUND (no drawing retrievable) |
| Behringer CP1A | Eurorack PSU reference | Behringer (Music Tribe) | https://www.behringer.com/en/products/0720-ABO (docs link to cdn-media.empowertribe.com) | `Behringer_CP1A/QSG_BE_0720-ABO_CP1A_WW.pdf`, `Behringer_CP1A/QSG_BE_EURORACK-RACK-CP1A.pdf` | Quick Start Guide (includes Specifications page); no full manual found | partial (QSG only) |
| Doepfer A-100 power / bus | Eurorack 16-pin bus spec | Doepfer | https://doepfer.de/a100_man/a100t_e.htm | `Doepfer_A100/a100t_e_technical_details.html`, `Doepfer_A100/a100b_e.gif` (bus connector pin-out drawing) | web page, no revision date | partial (HTML + GIF, no PDF) |
| D-sub DB-9 mechanical | DB-9 flange / hole / cutout | Spectrum Control, Winford Engineering, Switchcraft | https://spectrumcontrol.com/asset/d-sub-board-panel-cutouts.pdf ; https://www.bipom.com/documents/winford/dsub_panel_cutouts_dwg.pdf ; https://static.chipdip.ru/lib/064/DOC027064000.pdf | `DB9_Dsub/spectrumcontrol_dsub_panel_cutouts.pdf`, `DB9_Dsub/winford_dsub_panel_cutouts.pdf`, `DB9_Dsub/switchcraft_ehdb9.pdf` | Winford 02/03/2022; others undated | downloaded |
| Arturia MicroBrute | Host instrument | Arturia | https://downloads.arturia.com/products/microbrute/manual/MicroBrute_Manual_EN.pdf ; https://zwizwa.be/darcs/analog/schematics/MicroBrute/Arturia_MicroBrute-RearBoard_B2.pdf | `MicroBrute/MicroBrute_Manual_EN.pdf`, `MicroBrute/Arturia_MicroBrute-RearBoard_B2.pdf` | Manual 1st ed. Jul 2013; RearBoard B2 schematic 03/09/2015 (third-party host) | partial (user manual + one-board schematic; no official service manual) |
| Yusynth / community schematics | Reference circuits | Yusynth (Yves Usson) | n/a | none | n/a | NOT FOUND (no stable PDF located; a community S&H reference exists at github.com/holmesrichards/yash but was not downloaded) |

Counts: 42 PDFs + 1 HTML + 1 GIF across 34 directories. Parts fully downloaded from a manufacturer or
distributor: 24 rows; partial (mirror, older revision or non-PDF): 10 rows; NOT FOUND: 4 rows (KY-040/HW040,
vactrol/LDR04/BF245C/BC547, Thonkiconn, Yusynth).

## Key facts verified from datasheets

### (a) LF398 (TI SNOSBI3C, `LF398/lf398-n.pdf`)

- PDIP-8 pinout (Pin Functions table, p3): 1 V+, 2 OFFSET ADJUST, 3 INPUT, 4 V-, 5 OUTPUT, 6 Ch (hold capacitor),
  7 LOGIC REFERENCE, 8 LOGIC. (TO-99 uses the same numbering. SOIC-14 differs: it is a different pin map, so do
  not mix the two.) This settles the three conflicting pinouts in the docs: use the list above.
- Supply: +/-5 V to +/-18 V operating (p1 features); absolute max +/-18 V (p4); +/-15 V nominal.
  LF398-N temperature range 0 to 70 C (p4).
- Logic input: TTL/CMOS compatible; differential logic threshold 0.8 / 1.4 / 2.4 V min/typ/max (p5). Logic
  reference to logic differential must stay within the limits in p4 note (4); one logic pin must stay at least
  a threshold away from the other.
- Hold capacitor: 0.01 uF is the characterised value (hold step 1 mV typ, 2.5 mV max for LF398-N, p7); acquisition to
  0.1 % is 4 us at 1000 pF (10 V step) and 20 us at 0.01 uF (p5-p7). Leakage current into hold capacitor: 30 pA typ,
  200 pA max for LF398-N at TJ = 25 C (p7); 100 pA max for LF198/LF298 (p5).
- Droop: TI states "droop rates as low as 5 mV/min with a 1-uF hold capacitor" (p1). The sheet does not give a
  single droop number for 1 nF; the figure follows from leakage (dV/dt = I / C): 30 pA / 1 nF = 30 mV/s typ, 200 pA /
  1 nF = 200 mV/s max at 25 C (derived by us from p7, not stated by TI). Droop curve is Figure 4 (p9).
- Dielectric: p15 section 9.1.1 recommends polystyrene, polypropylene or Teflon for low dielectric absorption;
  mica and polycarbonate are called not nearly as good. COG ceramics also noted as low-DA. This confirms the docs'
  "1 nF ceramic is not for S&H".
- The same sheet notes stray capacitive coupling of logic to the hold capacitor adds hold step (1 pF with a 5 V logic
  swing and 0.01 uF adds 0.5 mV, p5).

### (b) LPC2361 (NXP data sheet Rev. 03, `LPC2361/lpc2361_62_ds-keil.pdf`)

- Package: LQFP100, 14 x 14 x 1.4 mm, SOT407-1 (p3; package outline p45). Part number LPC2361FBD100.
- **P0.2 / TXD0 = pin 98; P0.3 / RXD0 = pin 99** (Pin description table 3, p5). Alternate functions of P0.2 and P0.3 are
  TXD0 and RXD0 only (no further alternates listed).
- **P0.15 / TXD1 / SCK0 / SCK = pin 62; P0.16 / RXD1 / SSEL0 / SSEL = pin 63** (p6). The reviewer is right (62/63).
- **The docs' "97/96" are power pins, not P0.15/P0.16: pin 97 is VSS (ground) and pin 96 is VDD(3V3)** (p12).
  Any probe or wire landed on 96/97 per the old docs would be on supply or ground.
- I/O: 5 V tolerant pads with TTL levels and hysteresis (pad notes, p12-p13); input absolute max -0.5 to +6.0 V on
  5 V tolerant pins only when VDD(3V3) is present, otherwise VDD(3V3) + 0.5 V (Table 4 limiting values, p33). VDD(3V3)
  3.0-3.6 V (p33).
- Caveat: this is the 2008 Rev. 03 document. NXP lists Rev. 5.1 (Oct 2013) and marks the part not recommended for
  new designs; pin numbers above are from the older sheet and should be re-checked against Rev. 5.1 if it can be obtained.
  UM10211 Rev. 02 (`LPC2361/lpc23xx_um_UM10211_rev02-keil.pdf`) covers LPC2361/62 (added in this revision).

### (c) TL074 / TL072 / CD40106B / CD4049UB / CD4051B

- **TL072, 8-pin PDIP (P package), TI SLOS080W Fig 4-5 p5:** 1 1OUT, 2 1IN-, 3 1IN+, 4 VCC-, 5 2IN+, 6 2IN-, 7 2OUT, 8 VCC+.
- **TL074, 14-pin PDIP (N package), Fig 4-8 p8:** 1 1OUT, 2 1IN-, 3 1IN+, 4 VCC+, 5 2IN+, 6 2IN-, 7 2OUT, 8 3OUT, 9 3IN-,
  10 3IN+, 11 VCC-, 12 4IN+, 13 4IN-, 14 4OUT.
- TL07x limits (p10-p11): supply abs max 36 V (+/-18 V) for the NS/PS-package and M variants and 42 V for "all other"
  (TL07xH) variants; recommended supply 10-30 V (NS/PS/M) or 4.5-40 V (others). The table does not break out PDIP TL07xC
  separately, so for TL072CP/TL074CN treat +/-12 V operation (24 V total) as within both columns. Input clamp behavior:
  signal input current limited to +/-10 mA (50 mA for NS/PS/M), common-mode input abs max (VCC-) - 0.5 to (VCC+) + 0.5 V and
  differential up to VS + 0.2 V for "all other devices" (p10). Recommended input range (VCC-) + 4 V to (VCC+) + 0.1 V for
  those devices (p11), i.e. about 4 V below the positive rail is the linear limit for the H-class; check the C-class
  common-mode range in the electrical table before using inputs near the rails. Do not drive inputs beyond the rails.
- **CD40106B, 14-pin (TI SCHS097F p3):** 1 A, 2 G (=NOT A), 3 B, 4 H (=NOT B), 5 C, 6 I (=NOT C), 7 VSS, 8 J (=NOT D), 9 D,
  10 K (=NOT E), 11 E, 12 L (=NOT F), 13 F, 14 VDD. Supply 3-18 V recommended, abs max 20 V (p4). **Inputs: abs max -0.5 V to
  VDD + 0.5 V, +/-10 mA input current (p4): inputs above VDD are not allowed**, so drive from a 5 V domain only when VDD >= 5 V
  or add a series resistor with clamp-current in mind.
- **CD4049UB, 16-pin (TI SCHS046L p3):** 1 VCC, 2 G (out of A), 3 A, 4 H (out of B), 5 B, 6 I (out of C), 7 C, 8 VSS,
  9 D, 10 J (out of D), 11 E, 12 K (out of E), 13 NC, 14 F, 15 L (out of F), 16 NC. Supply 3-18 V recommended, abs max
  20 V VCC to VSS (p5-p6). **Input above VCC is explicitly allowed**: the description (p1) says the input high level (VIH)
  can exceed VCC when the device is used for logic-level conversion (high-to-low conversion; max input current 1 uA at 18 V
  over temperature, p1). The abs max table (p5) lists only +/-10 mA DC input clamp current and gives no separate input
  voltage limit, so keep the source current-limited (series resistor) and stay under the 18 V input/supply envelope. Note
  this differs from CD40106B/CD4051B, which have a VDD + 0.5 V input limit.
- **CD4051B, 16-pin (TI SCHS047O p3):** 1 Y4, 2 Y6, 3 COM, 4 Y7, 5 Y5, 6 INH, 7 VEE, 8 VSS, 9 C, 10 B, 11 A, 12 Y3, 13 Y0,
  14 Y1, 15 Y2, 16 VDD. Supply abs max 20 V (V+ to V-, referenced to VSS), DC input -0.5 to VDD + 0.5 V, +/-10 mA (p5).
  VEE is the analog negative rail; digital address/INH levels are referenced to VSS and need VDD - VSS adequate for
  the logic swing (check recommended-supply table in the sheet before using a 5 V VDD with +/-5 V analog).

### (d) RP2040 / Pico / Pico W

- **GPIO is not 5 V tolerant.** RP2040 datasheet Table 622 (p615): IOVDD abs max 3.63 V and voltage at IO pin abs max
  -0.5 V to IOVDD + 0.5 V (about 3.8 V at 3.3 V). The datasheet nowhere states 5 V tolerance. ADC GPIO26-29 additionally have
  an internal reverse diode to the IOVDD (3V3) rail, so their input voltage must not exceed 3.3 V (Pico datasheet p20).
- Output drive: selectable 2, 4, 8 or 12 mA (p616-p617, output voltage table). Maximum total current sourced by all GPIO + QSPI pins
  is 50 mA; maximum total sunk is 50 mA (p617). No per-pin absolute-maximum figure is given beyond the 12 mA drive setting;
  treat that as NOT FOUND as a separate per-pin abs max.
- ESD: 2 kV HBM (p615).
- Pico (non-W) pin map (Pico datasheet p8): pin 36 = 3V3 (OUT), pin 37 = 3V3_EN, pin 39 = VSYS, pin 40 = VBUS, pin 35 = ADC_VREF,
  pin 33 = AGND. **3V3 (pin 36)** can power external circuitry; maximum output current depends on RP2040 load and VSYS
  voltage; the datasheet recommends **keeping the load below 300 mA** (p9). **VSYS: 1.8 V to 5.5 V** (p9, p12, Recommended
  operating conditions table). Pico W gives the same VSYS range and 300 mA guidance (Pico W datasheet p9, p13).
- VBUS to VSYS goes through an on-board Schottky (D1) so VSYS = VBUS minus the diode drop (Pico datasheet p21); an external
  supply into VSYS should be ORed via another Schottky (p22). This confirms the 1N5817 from the 5 V rail into VSYS is a valid
  arrangement.

### (e) BAT85 and 1N5817

- **BAT85** (Philips data sheet 2000-05-25, `BAT85/bat85-nxp-mirror-aau.pdf`, p2-p3): VR 30 V, IF 200 mA continuous,
  IFRM 300 mA, IFSM 5 A (10 ms), Tj 125 C; VF 240 mV at 0.1 mA, 400 mV at 10 mA, 800 mV at 100 mA; IR 2 uA at 25 V; Cd 10 pF;
  trr 4 ns. Package SOD68 (DO-34 glass axial), not SOT-23. As a BAT54S substitute it is a single diode (BAT54S is a dual
  series pair in SOT-23: 30 V, 200 mA IO, 300 mA IFRM, VF 400 mV at 10 mA, IR 2 uA at 25 V; Diodes DS11005 p1-p2). It can
  stand in where only one diode of the pair is used; it is a through-hole part.
- **1N5817 is a 20 V part, not 40 V**: VRRM 20 V (1N5818 = 30 V, 1N5819 = 40 V), IO 1.0 A, IFSM 25 A (Vishay 88525 p1; Diodes
  DS23001 p2). Forward voltage at 1 A: 0.450 V max (1N5817), 0.55 V (1N5818), 0.60 V (1N5819) (Diodes p2). The BOM line
  "1N5817 Schottky diode (40V 1A)" is therefore wrong; a 40 V / 1 A part is the 1N5819. For a 5 V rail 1N5817 is adequate;
  use 1N5819 only if you want a 40 V rating. The owner's kit inventory (2026-10-17) lists 1N5819 x10; the actual part, its marking and a datasheet for it are UNVERIFIED (not saved under `datasheets/`; the series figures above come from the 1N5817-series sheet). The BOM's "0.3 V drop" applies at light load only; the Vishay forward-voltage curve (88525 Fig. 3, p2) gives the drop versus current.

### (f) Behringer CP1A and Eurorack 16-pin header

- CP1A (Quick Start Guide, `Behringer_CP1A/QSG_BE_0720-ABO_CP1A_WW.pdf`, Specifications page p20): two 16-pin (2 x 8, 2.54 mm)
  box headers wired in parallel. **+5 VDC @ 0.5 A (pins 11, 12); -12 VDC @ 1 A (pins 1, 2); +12 VDC @ 1 A (pins 9, 10); ground pins
  3-8.** External adapter 13 VDC, 3 A; consumption 35 W max (p20, p12). Pins 13-16 are marked "Not Used" in the pin-out (p15).
- **Pin 1 is -12 V and goes to the red stripe of the cable**; the sockets are keyed and the supplied ribbons have tabs matching the gaps
  (p15).
- Doepfer A-100 (`Doepfer_A100/a100t_e_technical_details.html` and `a100b_e.gif`): 16-pin module bus connector, 2 x 8, from the lower right corner
  of the board upward (each row is a pair of pins): -12 V, GND, GND, GND, +12 V, +5 V, CV, Gate. The 10-pin version, same orientation, is -12 V, GND, GND, GND, +12 V.
  This matches the CP1A order (pin 1 = -12 V, pins 3-8 = GND, pins 9-10 = +12 V, pins 11-12 = +5 V, pins 13-16 = CV/Gate). Doepfer states the
  coloured (red) wire of the ribbon marks -12 V and must point to the bottom of the bus board (page text, section on bus boards). Doepfer warns against polarised/boxed
  headers for A-100 modules (page text). The 16-pin version adds +5 V, CV and Gate. Doepfer PSU current ratings appear in the page text as a list of PSU models, not as a pin spec.
- CP1A rated currents (+12 V 1 A, -12 V 1 A, +5 V 0.5 A) agree with the retail listing; the CP1A is **not** a PSU with 5 V at more than 0.5 A, so Pico +
  OLEDs through a 1N5817 must stay well under that 0.5 A budget shared with all other +5 V consumers in the rack.

### (g) DB-9 mechanical (D-sub shell size 9 / "E" shell)

- Spectrum Control "Board and Panel Cutouts" (`DB9_Dsub/spectrumcontrol_dsub_panel_cutouts.pdf`, p1): **panel cutout for shell size 9**: mounting-hole
  centre spacing A = 0.984 in (24.99 mm); cutout width C = 0.777 in (19.74 mm); cutout height E = 0.440 in (11.18 mm); mounting holes 0.125 in (3.18 mm) dia,
  two holes. Row/contact pitch 0.109 in (2.77 mm); PCB-mount hole spacing 0.984 in (25.00 mm).
- Winford recommended panel cutout (`DB9_Dsub/winford_dsub_panel_cutouts.pdf`, p1): DB9: mounting holes 0.98 in apart, 0.125 in dia (2 places), cutout 0.81 x 0.45 in
  with R0.15 corners, maximum panel thickness 0.062 in. (Winford and Spectrum cutout width differ: 0.81 vs 0.777 in. Use the larger Winford cutout
  if the connector's own drawing is unavailable; confirm against the actual connector.)
- Switchcraft EHDB9 adapter drawing (`DB9_Dsub/switchcraft_ehdb9.pdf`, p1) for reference: hole spacing 0.945 in (24 mm), cutout 0.748 in (19 mm) wide, flange width about 1.22 in (31 mm)
  reference. This is a different (adapter) part: do not use its numbers for a bare DB-9 flange.
- Flange outer width / height of a bare DB-9 shell (the nominal 30.81 mm / 1.213 in figure): **NOT FOUND in the downloaded documents** (only an adapter-drawing
  reference of about 31 mm); get the specific connector's manufacturer drawing before cutting.

## Findings that contradict project docs

1. 1N5817 is rated 20 V, not 40 V (BOM line 9): see (e).
2. LPC2361 P0.15/P0.16 are pins 62/63; pins 96/97 are VDD(3V3)/VSS: see (b).
3. CD40106B inputs may not exceed VDD + 0.5 V (CD4049UB inputs may exceed VCC): see (c).
4. RP2040 GPIO is not 5 V tolerant (IOVDD + 0.5 V abs max): see (d).
5. LF398 PDIP-8 pinout is V+ 1, OFFSET 2, IN 3, V- 4, OUT 5, Ch 6, LOGIC REF 7, LOGIC 8: see (a).
