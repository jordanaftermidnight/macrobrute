# LPC2361 Firmware Reverse Engineering — Research Findings

Compiled 2026-04-09 from web research.

---

## Key New Discoveries

### 1. No Public MicroBrute Firmware Dumps Exist
- No community reports of successful firmware extraction on ModWiggler, Reddit, or EEVblog
- Hardware mod community focuses entirely on analog modifications

### 2. Crystal Frequency Confirmed: 12MHz
- Confirmed from hackabrute.yusynth.net schematics (SF17002 ARM Board PDF)
- Supports 72MHz PLL configuration (standard LPC2361 setup)

### 3. CRP Bypass — Three Viable Approaches

**Voltage Fault Injection (VFI):**
- 0x01 Team demonstrated bypass of NXP LPC-family debug checks (hardwear.io NL22, 2022)
- Video: https://www.youtube.com/watch?v=RlV9t0gXTLI

**Electromagnetic Fault Injection (EMFI):**
- Aaron Christophel demonstrated on LPC2388 (same architecture family, 2024)
- POC: https://www.youtube.com/watch?v=q9o9sKY2hk8
- Success: https://www.youtube.com/watch?v=tcqLgjmzUzM
- PicoEMP (~$50 tool): https://github.com/newaetech/chipshouter-picoemp (719 stars)

**Chris Gerlinsky RECON 2017 — "Breaking CRP on NXP LPC":**
- 55-minute talk with practical bypass methods
- Video: https://www.youtube.com/watch?v=YNpJ3c1GJoc
- 3-part blog series on LPC1343 bootloader bypass at firmwaresecurity.com

### 4. KeyStep Firmware RE (Reference Project)
- Daniel Gruss reverse-engineered Arturia KeyStep firmware using Ghidra (2020)
- Same Arturia ecosystem, ARM-based
- Walkthrough: https://dsgruss.github.io/notes/2020/10/02/keystep1.html
- Covers: file metadata, memory structure, Ghidra workflow

### 5. .mbf File Format — Uncracked
- No public RE of .mbf format found
- 144.73KB exceeds 128KB flash — suggests encoding, compression, or multi-section
- .mbpz (preset) files were reverse-engineered (legacy Arturia forums) but not .mbf
- Arturia MiniLab 3 firmware analysis by Fenugrec (YouTube 2024) — different MCU but methodology applicable

### 6. MCP4728 DAC
- Default I2C address: **0x60** (configurable via EEPROM)
- 4 channels, 12-bit resolution
- No public confirmation of hidden velocity/aftertouch/mod wheel channels beyond Matraszek's SysEx documentation

### 7. Ghidra SVD Files Available
- SVD-Loader-Ghidra: https://github.com/leveldown-security/SVD-Loader-Ghidra (567 stars)
- GhidraSVD: https://github.com/antoniovazquezblanco/GhidraSVD (41 stars)
- LPC23xx SVD files in CMSIS-SVD database

### 8. No Live UART Communication Reports
- Nobody has documented communicating with LPC2361 via UART while synth is running
- This remains unexplored territory

---

## Recommended RE Approach

1. **Phase 1:** Use Matraszek SysEx protocol + Gruss KeyStep methodology
2. **Phase 2:** Connect PL2303HX to UART0, detect CRP level
3. **Phase 3 (if CRP):** PicoEMP for EMFI — cheapest viable bypass (~$50 vs $300 ChipWhisperer)
4. **Phase 4:** Analyze .mbf file with binwalk, strings, entropy analysis
5. **Phase 5:** Load into Ghidra with SVD-Loader for peripheral labeling

---

## Source URLs

- https://matraszek.dev/posts/reverse-engineering-arturia-microbrute-midi-sysex-protocol.html
- https://matraszek.dev/files/microbrust_sysex.pdf
- https://dsgruss.github.io/notes/2020/10/02/keystep1.html
- https://www.youtube.com/watch?v=YNpJ3c1GJoc (Gerlinsky RECON 2017)
- https://www.youtube.com/watch?v=RlV9t0gXTLI (0x01 Team VFI)
- https://www.youtube.com/watch?v=q9o9sKY2hk8 (Christophel EMFI POC)
- https://www.youtube.com/watch?v=tcqLgjmzUzM (Christophel EMFI Success)
- https://github.com/newaetech/chipshouter-picoemp
- https://github.com/leveldown-security/SVD-Loader-Ghidra
- https://github.com/antoniovazquezblanco/GhidraSVD
- https://hackabrute.yusynth.net/MICROBRUTE/schematics_en.html
- https://firmwaresecurity.com/
- https://www.modwiggler.com/forum/viewtopic.php?t=152071
