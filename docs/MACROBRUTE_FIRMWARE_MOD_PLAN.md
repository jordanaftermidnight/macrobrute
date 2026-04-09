# MACROBRUTE — Custom Firmware Modification Plan

## Overview

With the .mbf encryption cracked, we can create modified MicroBrute firmware
and flash it via the standard MIDI SysEx update process. This document plans
what modifications are worth pursuing and how they integrate with the broader
MACROBRUTE project.

---

## Flash Budget

| Region | Size | Usage |
|--------|------|-------|
| Bootloader (0x0000-0x1FFF) | 8 KB | NXP ISP — **do not touch** |
| Stock firmware (0x2000-0xEDB7) | 51 KB | Application code (v1.0.4.114) |
| Free flash (0xEDB8-0x1FFFF) | 68 KB | Available for custom code |
| **Total app space** | **120 KB** | 43% used, 57% free |

68KB free is more than the stock firmware itself. We could nearly triple the codebase.

---

## Re-encryption Pipeline

To flash modified firmware:

```
1. Modify .bin (ARM binary)
2. arm-none-eabi-objcopy -I binary -O ihex --change-addresses 0x2000 mod.bin mod.hex
3. Prepend: key string (24 bytes) + null byte (0x00) + Intel HEX text
4. XOR-encrypt with key "ArturiaminiBruteFirmware", start index 4
5. Flash via MicroBrute Connection or direct MIDI SysEx (28-byte packets)
```

A `tools/mbf_encrypt.py` tool will automate steps 3-4.

### Safety Measures

- **Always preserve the vector table** (first 0x54 bytes)
- **Never modify addresses below 0x2000** (bootloader)
- **Keep a stock .mbf backup** — can always re-flash via MIDI SysEx
- **Test on breadboard LPC2361 first** if available
- **Worst case:** ISP recovery via PL2303HX on UART0 (P0.2/P0.3, P2.10 LOW)

---

## Modification Tiers

### Tier 1: Binary Patching (Low Risk)

Modify existing firmware bytes without adding new code. Safest approach.

| Mod | What | Risk | Benefit |
|-----|------|------|---------|
| Parameter range extension | Patch min/max values in param tables | Very low | Wider bend range, extended swing |
| Default value changes | Change power-on defaults | Very low | Custom startup state |
| DAC curve tweaks | Modify pitch CV lookup values | Low | Custom tuning tables |
| MIDI channel defaults | Change default MIDI channels | Very low | Convenience |

### Tier 2: Code Injection (Medium Risk)

Add new code in free flash space, patch jump targets to redirect execution.

| Mod | What | Risk | Benefit |
|-----|------|------|---------|
| Pico UART bridge | Add UART0 handler for Pico ↔ LPC2361 communication | Medium | Real-time parameter control from Pico |
| Extended SysEx | Add custom SysEx commands beyond Arturia protocol | Medium | PC/DAW control of hidden parameters |
| Debug output | Enable UART serial output of internal state | Medium | Live debugging during development |
| Custom sequencer modes | Add Euclidean, probability, ratchet to built-in seq | Medium-High | Musical features |

### Tier 3: Major Rewrite (High Risk)

Replace significant sections of firmware.

| Mod | What | Risk | Benefit |
|-----|------|------|---------|
| Alternative tuning systems | Replace pitch calculation with microtonal support | High | Microtonal synthesis |
| Custom oscillator modes | Modify waveform generation parameters | High | New timbres |
| Full sequencer rewrite | Replace stock sequencer with custom engine | High | Advanced sequencing |

---

## Priority Modifications for MACROBRUTE

Given the project goals (semi-modular expansion, Pico digital brain, industrial/techno focus):

### 1. Pico ↔ LPC2361 UART Bridge (Tier 2, HIGHEST PRIORITY)

**Why:** The Pico currently can only send SysEx to the MicroBrute via MIDI. A direct
UART link between Pico (GP0/GP1, UART0) and LPC2361 (P0.2/P0.3, UART0) would enable:
- Real-time parameter reads (not just writes)
- Low-latency bidirectional communication
- Custom binary protocol (faster than SysEx)
- State synchronization between Pico display and MicroBrute

**Implementation:**
1. In Ghidra: locate UART0 init code (we know it's around 0x3EA8)
2. Find unused UART0 IRQ slot in VIC
3. Add ring buffer + simple command parser in free flash
4. Connect to existing parameter structures
5. Pico side: `firmware/pico/lpc_comm.py` already designed for this

**Risk mitigation:** UART0 is the ISP programming port. Our code must NOT interfere
with ISP mode (P2.10 LOW at reset). Only activate UART bridge after boot, when P2.10 is HIGH.

### 2. Debug Serial Output (Tier 2, HIGH PRIORITY)

**Why:** Understanding the firmware's runtime behavior before making bigger changes.

**Implementation:** Redirect C++ runtime error handlers (SIGPVFN, SIGRTMEM at 0xC7E4)
to output via UART0. Add lightweight printf-like output for key events.

### 3. Extended SysEx Commands (Tier 2, MEDIUM PRIORITY)

**Why:** Allow Pico to query current parameter values, not just set them.

**Implementation:** Hook the existing SysEx dispatcher, add new command codes:
- `0x80+`: Query parameter value (response with current state)
- `0x90+`: Dump all parameters
- `0xA0+`: Trigger sequencer events

### 4. Parameter Range Extension (Tier 1, LOW PRIORITY)

**Why:** Some parameters have artificially limited ranges (e.g., bend range 1-12,
swing 50-75). Extending these could unlock new musical territory.

**Implementation:** Binary patch the bounds-checking constants in the param table area.

---

## Ghidra Analysis Roadmap

Before any modifications, we need a thorough Ghidra analysis:

### Phase 1: Structural Mapping
1. Load `firmware/MicroBrute_Firmware_Update_1_0_4_114.bin` as `ARM:LE:32:v4t`, base `0x2000`
2. Install SVD-Loader with LPC23xx SVD
3. Mark vector table at 0x2000, handler pointers at 0x2020
4. Auto-analyze, then manual pass on unresolved functions
5. Label all peripheral register accesses (use our peripheral map)

### Phase 2: Function Identification
1. **UART0 init** — around 0x3EA8 (references UART0 base 0xE000C000)
2. **SPI handler** — around 0x4348 (MCP4728 DAC communication?)
3. **Timer0 handler** — around 0x3F70 (tempo/sequencer timing?)
4. **SysEx parser** — search for 0xF0 handling in UART/MIDI receive path
5. **Parameter store** — find read/write functions for SysEx param codes
6. **DAC output** — trace MCP4728 I2C writes for pitch CV
7. **GPIO handlers** — button/LED control at 0x669C

### Phase 3: Modification Points
1. Map the SysEx command dispatch table
2. Find free VIC interrupt slots for UART0
3. Identify safe hook points for code injection
4. Document all discovered function signatures

---

## Integration with MACROBRUTE Build Plan

| Build Phase | Firmware Mod Integration |
|-------------|------------------------|
| Phase 0 (Toolchain) | Install `arm-none-eabi-gcc`, Ghidra. Write `mbf_encrypt.py` |
| Phase 1 (Pico bring-up) | Test Pico firmware on breadboard, ready for UART bridge |
| Phase 2 (Internal wiring) | Wire UART0 (P0.2/P0.3) to breakout PCB → DB-9 → Pico GP0/GP1 |
| Phase 3 (Panel) | No firmware changes needed |
| Phase 4 (Expander) | No firmware changes needed |
| Phase 5 (Integration) | Flash custom firmware with UART bridge, test Pico ↔ LPC2361 comm |
| Phase 6A (RE) | Ghidra analysis, identify modification points |

### Recommended Order

1. **Ghidra analysis** (can do now, no hardware needed)
2. **Write `mbf_encrypt.py`** (can do now)
3. **Binary patch: debug serial output** (first custom firmware test)
4. **UART bridge** (after Ghidra identifies safe hook points)
5. **Extended SysEx** (after UART bridge working)
6. **Parameter tuning** (after understanding param table format)

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Brick during flash | Low | Stock .mbf backup, ISP recovery via PL2303HX |
| Corrupt parameter EEPROM | Low | Parameters are reset on firmware update |
| Break MIDI functionality | Medium | Test SysEx before/after modification |
| Break audio output | Medium | Preserve DAC init and output path code |
| ISP bootloader damage | None | Bootloader is at 0x0000, we only write 0x2000+ |

**The ISP bootloader cannot be damaged** by flashing custom firmware through the
normal update process — it only writes to the application area (0x2000+).

---

## Files

| File | Purpose |
|------|---------|
| `tools/mbf_decrypt.py` | Decrypt .mbf → .hex → .bin |
| `tools/mbf_encrypt.py` | Encrypt .bin/.hex → .mbf (with `--verify` round-trip) |
| `tools/test_mbf_decrypt.py` | Automated test suite (52 tests: cipher, decrypt, encrypt, round-trip) |
| `tools/ghidra_label_firmware.py` | Ghidra script: labels vectors, peripherals, known code locations |
| `firmware/*.mbf` | Stock firmware backups (v1.0.4.114, v1.0.3.2) |
| `firmware/*.bin` | Decrypted ARM binaries (gitignored, regenerate with decrypt tool) |
| `docs/research/mbf_analysis.md` | Full technical analysis of cipher and firmware |
