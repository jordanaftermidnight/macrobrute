# MicroBrute .mbf Firmware File Analysis

File: `MicroBrute_Firmware_Update_1_0_4_114.mbf`

## File Properties

| Property | Value |
|----------|-------|
| Size | 148,200 bytes (144.73 KB) |
| Byte range | 0x00-0x7F only (100% 7-bit MIDI-safe) |
| Shannon entropy | 5.79 bits/byte (72.4%) |
| SysEx markers (0xF0/0xF7) | None |
| Arturia manufacturer ID | Not found (encoded) |

## Key Finding: 360-Byte Block Structure

The file consists of **411 full blocks of 360 bytes** + 240-byte remainder.

### Intra-Block Structure

Each 360-byte block contains **8 fixed 5-byte signatures** at regular 45-byte intervals:

| Block Offset | Signature (hex) | ASCII |
|-------------|-----------------|-------|
| +0x028 (40) | `7A 6B 48 54 71` | `zkHTq` |
| +0x055 (85) | `64 78 57 46 51` | `dxWFQ` |
| +0x082 (130) | `79 6F 7C 58 42` | `yo\|XB` |
| +0x0AF (175) | `4F 78 4F 45 55` | `OxOEU` |
| +0x0DC (220) | `64 64 53 73 42` | `ddSsB` |
| +0x109 (265) | `64 6B 57 58 5E` | `dkWX^` |
| +0x136 (310) | `79 7F 48 58 51` | `y.HXQ` |
| +0x163 (355) | `68 4B 48 45 45` | `hKHEE` |

These signatures are **identical across all 411+ blocks** — they mark sub-block boundaries.

### Sub-Block Layout (45 bytes each)

```
  +0x00: [40 bytes encoded data] [5 bytes signature]
  +0x2D: [40 bytes encoded data] [5 bytes signature]
  +0x5A: [40 bytes encoded data] [5 bytes signature]
  ...
  Total: 8 sub-blocks × 45 bytes = 360 bytes per block
  Data per block: 8 × 40 = 320 bytes
  Overhead: 8 × 5 = 40 bytes (12.5%)
```

### Additional Fixed Bytes

Many single-byte positions are constant across all blocks, suggesting the
encoding maps specific byte patterns (likely 0x00 or 0xFF from erased flash)
to fixed encoded values.

Notable fixed positions beyond signatures:
- +0x030: always `0x42 0x59 0x51`
- +0x05D-05F: always `0x42 0x44 0x45`
- +0x08A-08C: always `0x42 0x55 0x71`
- +0x0B7-0B9: always `0x5D 0x47 0x51`
- +0x0E4-0E6: always `0x76 0x59 0x42`
- +0x111-113: always `0x45 0x44 0x55`
- +0x13E-140: always `0x59 0x72 0x42`

## MicroBrute Connection App Binary Analysis

The `MicroBrute Connection.app` (Mach-O i386, JUCE C++ framework) contains
the firmware update logic. Key strings extracted:

| String | Significance |
|--------|-------------|
| `"This file is not a MicroBrute crypted firmware file."` | Confirms .mbf is **encrypted** |
| `"14LPC23XXUpdater"` | C++ class handling LPC23XX firmware updates |
| `"MBFD"` | Probable magic header (MicroBrute Firmware Data?) |
| `"Downloading the firmware, do not unplug..."` | Update progress message |
| `"Firmware update: complete"` | Success message |

**Next step:** Disassemble `MicroBrute Connection` binary with Ghidra or Hopper.
Focus on `LPC23XXUpdater` class methods — the decrypt/encode routines will be
in methods that read the .mbf file and check for the "MBFD" magic header.

## Encoding Analysis

### Not Simple XOR
Adjacent block XOR does not produce recognizable plaintext. The encoding is
more complex than single-byte XOR.

### Not Standard MIDI 7-bit Packing
Standard MIDI 7-bit unpacking (MSB byte first or last) does not produce
ARM vector table signatures at offset 0.

### Characteristics of the Encoding
1. **Strictly 7-bit** — designed for MIDI SysEx transport
2. **Block-structured** — 360-byte blocks with internal signatures
3. **Fixed overhead** — 12.5% (40 of 360 bytes are signatures)
4. **Position-dependent** — same plaintext byte at same block position
   always produces same encoded byte (not stream cipher)
5. **No visible ARM code** — vector table, CRP word not recognizable

### Possible Encoding Schemes
1. **Custom substitution + bit manipulation** — Arturia proprietary
2. **Scrambled byte ordering** within each 40-byte data section
3. **Lookup table encoding** (like base64 but 7-bit custom)
4. **Multi-pass encoding** — 7-bit pack + scramble + signature insert

## Size Mathematics

```
  File size:                148,200 bytes
  Full blocks:              411 × 360 = 147,960 bytes
  Remainder:                240 bytes
  Data per block:           320 bytes (8 × 40)
  Total data:               411 × 320 + ? = 131,520+ bytes
  LPC2361 flash:            131,072 bytes (128 KB)
  Ratio:                    ~1.004× (very close!)
```

The 131,520 bytes of encoded data closely matches the 131,072-byte flash,
with ~448 bytes for metadata/checksums.

## Attack Vectors for Decoding

### 1. Known Plaintext Attack
ARM7TDMI vector table at address 0x0 is partially predictable:
- Word 0 (reset): `LDR PC, [PC, ...]` = `0xE59FFxxx`
- Words 1-6: exception vectors (also LDR PC patterns)
- Word 7 (reserved): checksum

Map these known bytes to the first block's encoded bytes to derive
the encoding scheme.

### 2. Flash Erase Pattern
Large sections of unused flash = `0xFF`. The highly repetitive
patterns in later blocks (near block 400+) likely represent erased
flash. Use these to determine how `0xFF` is encoded.

### 3. CRP Word
Address `0x000001FC` contains the CRP value. If CRP is disabled,
this word is `0xFFFFFFFF`. This maps to a specific block and offset:
- Block: `0x1FC / 320 = 1.59` → partially in block 1
- Look for distinctive patterns at that position

### 4. Differential Analysis
Compare with firmware from other Arturia products (.mbf files for
MiniBrute, MicroBrute SE) — shared encoding would confirm the scheme
and provide more known-plaintext pairs.

### 5. Capture Live SysEx
Use SysEx Librarian during a firmware update to capture the raw MIDI
stream. Compare with .mbf file to determine if additional framing/
headers exist in the MIDI transport layer.

## Differential Analysis: v1.0.4.114 vs v1.0.3.2

Second file: `MicroBrute_Firmware_Release_V1.0.3.2.mbf`

| Property | v1.0.4.114 | v1.0.3.2 |
|----------|-----------|----------|
| Size | 148,200 bytes | 137,956 bytes |
| Blocks | 411 full + 240 | 383 full + 76 |
| Entropy | 5.7903 | 5.7897 |
| 7-bit only | Yes | Yes |
| Block size | 360 | 360 |

### Key Differential Findings

1. **All block signatures are IDENTICAL between versions**
   - Confirms signatures are encoding structural markers, not data-dependent
   - The encoding scheme is the same between firmware versions

2. **Blocks 1 and 2 are identical between versions**
   - Flash addresses 0x140-0x3BF (block 1-2, 640 bytes)
   - Likely bootloader or exception handler code (unchanged between versions)
   - Block 0 differs only in later sub-blocks (first 48 bytes match)

3. **64.6% of shared bytes differ** — extensive code changes between versions

4. **Late blocks (383-410) are all unique** — not just erased flash
   - v1.0.4 contains more code than v1.0.3
   - No simple "erased = 0xFF" pattern visible

5. **Block 0 partial match** — first 48 bytes identical (ARM vector table
   entry points are the same), but later bytes differ (some vectors changed)

### Encoding Scheme Constraints (from differential)

- Position-dependent encoding (same plaintext at same position = same output)
- Not simple XOR (blocks with mostly 0xFF would produce recognizable patterns)
- Likely involves bit manipulation and/or substitution
- 7-bit constraint is enforced per-byte (no escape sequences)
- Block boundaries are meaningful — encoding restarts each block

## Recommendations

1. **Priority: Decompile MIDI Control Center**
   - Arturia's update tool contains the .mbf encoder/decoder
   - Java-based (use JD-GUI or CFR to decompile)
   - Search for the 5-byte signature constants in the binary
2. **Capture SysEx during update** — reveals MIDI framing around .mbf data
3. **Known plaintext attack on block 0**
   - First 32 bytes of ARM7 vector table are predictable (LDR PC instructions)
   - Compare with encoded block 0 data to derive mapping
4. **Acquire MiniBrute .mbf** — same MCU family, may use identical encoding
5. **Block 1-2 are stable** — use as additional known-plaintext reference
   if bootloader code is ever dumped
