# LPC2361 Firmware Reverse Engineering — Research Findings

Compiled 2026-04-09 from web research + binary analysis.

---

## BREAKTHROUGH: .mbf Encryption Cracked

**The .mbf firmware format has been fully decoded.** See `docs/research/mbf_analysis.md` for complete details.

- **Algorithm:** Repeating XOR cipher with key `ArturiaminiBruteFirmware` (24 bytes)
- **Key start index:** 4 (not 0)
- **Payload:** Intel HEX format containing ARM binary (loads at 0x2000)
- **Validation:** First 24 decrypted bytes must equal the key string
- **Tool:** `tools/mbf_decrypt.py` — decrypts .mbf → .hex → .bin
- **CRP is irrelevant for firmware analysis** — the .mbf gives us the full application code

### Firmware Binary Summary (v1.0.4.114)
- 52,664 bytes (51.4 KB), base address 0x2000, entry 0x2184
- ARM7TDMI with Thumb interworking, C++ runtime (Keil/IAR toolchain)
- 40.2% flash usage — significant room for custom firmware
- Ready for Ghidra analysis: `ARM:LE:32:v4t`, base `0x2000`

---

## Key Discoveries

### 1. No Public MicroBrute Firmware Dumps Exist (But We Have One Now)
- No community reports of successful firmware extraction on ModWiggler, Reddit, or EEVblog
- Hardware mod community focuses entirely on analog modifications
- **We decrypted the .mbf file directly — no hardware access needed**

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

### 5. .mbf File Format — CRACKED
- **Repeating XOR cipher, key = `ArturiaminiBruteFirmware`**
- 148KB .mbf → 148KB Intel HEX → 52KB ARM binary
- Size exceeds flash because Intel HEX is ~2.8x larger than binary
- Preset files (.mbpz) likely use key `ArturiaminiBrutePresetFile` (also found in binary)
- No public RE of .mbf existed prior to this analysis

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

## Recommended RE Approach (Updated)

1. **DONE:** Decrypt .mbf using `tools/mbf_decrypt.py`
2. **Next:** Load .bin into Ghidra (`ARM:LE:32:v4t`, base `0x2000`, SVD-Loader for peripherals)
3. **Next:** Map MIDI SysEx handlers, DAC output code, sequencer, parameter tables
4. **Optional:** Connect PL2303HX to UART0, check for debug output while running
5. **Optional:** PicoEMP for EMFI — only needed for bootloader area or factory calibration
6. **Optional:** Capture live SysEx during firmware update to map protocol details

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

---

## Additional Tools & Resources (from research)

### Open Source MicroBrute Tools
- **microbrust** (Rust): https://github.com/jmatraszek/microbrust — Linux SysEx interface
- **Elektroid** (C): https://github.com/dagargo/elektroid — Modern device manager supporting MicroBrute (372 stars, active)
- **microdude** (Python): https://github.com/dagargo/microdude — Deprecated, use Elektroid instead
- **avril firmware tools**: https://github.com/pichenettes/avril-firmware_tools — .mid/.syx conversion (Mutable Instruments)

### MicroBrute Connection App Analysis (COMPLETE)
- Binary: Mach-O i386, C++ with JUCE framework
- **`LPC23XXCrypter`** class: repeating XOR cipher (encrypt/decrypt are same function)
  - `setKey()`, `cypherData()`, `uncypherData()` (jmp to cypherData), `resetKeyIndex()`, `skipKeyIndex()`
- **`CryptedFile`** class: reads file, creates crypter, decrypts, validates header = key
- **`LPC23XXUpdater`** class: MIDI SysEx update protocol (28-byte packets, ACK-based)
- Key strings: `ArturiaminiBruteFirmware` (firmware), `ArturiaminiBrutePresetFile` (presets)
- Magic header `MBFD` is actually a reference, not the key — the key IS the header after decryption
- Firmware is NOT embedded in app — `.mbf` file is loaded from disk
