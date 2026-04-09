# MicroBrute .mbf Firmware File — Decryption & Analysis

## Encryption: CRACKED

The .mbf format uses a **repeating XOR cipher** with the key `ArturiaminiBruteFirmware` (24 bytes).

### Cipher Details

| Property | Value |
|----------|-------|
| Algorithm | Repeating XOR (symmetric — encrypt = decrypt) |
| Key | `ArturiaminiBruteFirmware` (24 bytes, ASCII) |
| Key start index | 4 (constructor does `keyIndex = 4 % keyLen`) |
| Header | First 24 bytes of decrypted file = the key itself (validation) |
| Separator | Null byte (0x00) after header — key is null-terminated C string |
| Payload | Intel HEX format (ASCII text) |

### How It Was Found

Disassembly of `MicroBrute Connection.app` (Mach-O i386, JUCE C++) using `otool -tV` and `nm`.

**Two C++ classes handle the firmware:**

`LPC23XXCrypter` — encryption engine:
```
struct LPC23XXCrypter {
    char* key;       // +0x00: strdup'd key bytes
    int   keyLen;    // +0x04: key length (24)
    int   keyIndex;  // +0x08: current position, wraps at keyLen
};

// Methods:
setKey(char*, int)      — sets key (strdup + store length)
resetKeyIndex()         — keyIndex = 4 % keyLen
skipKeyIndex(int n)     — keyIndex = (keyIndex + n) % keyLen
cypherData(char*, int)  — XOR each byte with key[keyIndex++], wrap at keyLen
uncypherData(char*, int)— IDENTICAL to cypherData (just a jmp — symmetric cipher)
```

`CryptedFile` — file wrapper:
```
CryptedFile(juce::String& path, juce::String& key):
    1. Read entire file into memory
    2. Create LPC23XXCrypter(key.toUTF8(), strlen(key))
    3. uncypherData(buffer, fileSize)
    4. strncmp(buffer, key, keyLen) — validate header matches key
    5. If mismatch: "This file is not a MicroBrute crypted firmware file."
```

`LPC23XXUpdater` — MIDI update protocol:
```
StartUpdate(MidiOutput*, InputStream*)  — begins update via SysEx
SendNextPacket()    — sends 0x1C (28) byte packets via SysEx
AckReceived()       — handles ACK from device
ResendLastPacket()  — retransmit on timeout
SendEndOfUpdateMsg()— finalize update
Reboot(MidiOutput*) — reboot device after flash
```

The key string `ArturiaminiBruteFirmware` and preset key `ArturiaminiBrutePresetFile` are both present in the binary.

### Decryption Tool

```
python3 tools/mbf_decrypt.py firmware.mbf              # → firmware.hex
python3 tools/mbf_decrypt.py firmware.mbf -b            # → firmware.hex + firmware.bin
```

---

## Decrypted Firmware Analysis

### v1.0.4.114 (latest)

| Property | Value |
|----------|-------|
| .mbf size | 148,200 bytes |
| Payload (Intel HEX) | 148,176 bytes, 3,296 lines |
| Binary size | 52,664 bytes (51.4 KB) |
| Base address | 0x00002000 (8KB bootloader reserved) |
| Entry point | 0x00002184 |
| Flash usage | 40.2% of 128KB |

### v1.0.3.2

| Property | Value |
|----------|-------|
| .mbf size | 137,956 bytes |
| Binary size | 49,024 bytes (47.9 KB) |
| Base address | 0x00002000 |
| Entry point | 0x00002184 (same) |
| Flash usage | 37.4% of 128KB |

### ARM Vector Table (at 0x2000)

| Vector | Instruction | Notes |
|--------|------------|-------|
| Reset | `LDR PC, [PC, #0x18]` | Standard ARM vector load |
| Undef | `LDR PC, [PC, #0x18]` | Shared handler setup |
| SWI | `LDR PC, [PC, #0x18]` | |
| PrefAbort | `LDR PC, [PC, #0x18]` | |
| DataAbort | `LDR PC, [PC, #0x18]` | |
| Checksum | `0x0000CD80` | NXP boot checksum (sum of vectors 0-4,6-7 + this = 0) |
| IRQ | `LDR PC, [PC, #-0x120]` | Reads VIC VectAddr register directly |
| FIQ | `LDR PC, [PC, #0x18]` | |

The IRQ vector `0xE51FF120` is the standard NXP pattern: `LDR PC, [0xFFFFF030]` (VICVectAddr).

### Memory Map

```
0x00000000 - 0x00001FFF  ISP Bootloader (8 KB, not in firmware image)
0x00002000 - 0x0000EDBD  Application firmware (v1.0.4: ~52 KB)
0x0000EDBE - 0x0001FFFF  Unused flash (~44 KB)
0x40000000 - 0x400087FF  SRAM (34 KB)
```

### Key Strings Found in Firmware

| Address | String | Significance |
|---------|--------|-------------|
| 0x0C7E4 | `SIGPVFN: Pure virtual fn called` | C++ runtime (Keil/ARM) |
| 0x0CA2C | `SIGRTMEM: Out of heap memory` | Heap allocation failure |
| 0x0CA4C | `: Heap memory corrupted` | Memory corruption detect |
| 0x0CA78 | `SIGABRT: Abnormal termination` | Abort handler |

These are ARM C/C++ runtime library strings — firmware is compiled with a commercial ARM toolchain (likely Keil MDK or IAR).

### Differential Analysis (v1.0.4.114 vs v1.0.3.2)

| Metric | Value |
|--------|-------|
| Size difference | 3,640 bytes (v1.0.4 larger) |
| Differing bytes | 47,050 of 49,024 shared (96%) |
| Diff regions | 1,293 |
| Entry point | Same (0x2184) |
| Vector table | Mostly same, handler addresses differ |

96% difference means these are full recompiles, not patches. Both versions share the entry point and basic architecture.

---

## CRP Status

The CRP (Code Read Protection) word lives at absolute address **0x1FC** — inside the bootloader area (0x0000-0x1FFF) which is NOT included in the firmware update image. This means:

1. The .mbf update **cannot change CRP** — it only writes to 0x2000+
2. CRP was set at **factory** and persists across firmware updates
3. The only way to determine CRP level is to **physically probe** UART0 (P0.2/P0.3) with ISP
4. If CRP is set, the firmware dump we have from .mbf decryption is already the application code — we don't need to bypass CRP for application analysis

**The .mbf decryption makes CRP bypass unnecessary for firmware analysis.** CRP bypass is only needed if we want to modify the bootloader area or read factory-specific calibration data.

---

## Update Protocol

The firmware update uses MIDI SysEx. From the `LPC23XXUpdater` disassembly:

1. `StartUpdate` — sends SysEx command to enter bootloader mode
2. File is divided into **28-byte (0x1C) packets**
3. Each packet sent via `SendNextPacket` as SysEx message
4. Device ACKs each packet (or updater retransmits)
5. `SendEndOfUpdateMsg` — signals completion
6. `Reboot` — resets device

The Intel HEX text is sent directly (not the binary) — 28 bytes at a time.

Total packets: `148,176 / 28 = 5,292 packets`

---

## Previous Analysis Corrections

The earlier analysis of "360-byte block structure with 5-byte signatures" was observing **patterns in the XOR keystream**, not real data structures. Since the key is 24 bytes and repeats, and the Intel HEX format has regular line structure (`:10XXXX00...` = 43+ chars per line), the interaction between key period (24) and HEX line length created apparent 360-byte periodicities (LCM effects). The "fixed signatures" were key bytes XOR'd with predictable HEX format characters (`:`, hex digits, newlines).

---

## Files

| File | Contents |
|------|----------|
| `firmware/MicroBrute_Firmware_Update_1_0_4_114.mbf` | Original encrypted v1.0.4.114 |
| `firmware/MicroBrute_Firmware_Update_1_0_4_114.hex` | Decrypted Intel HEX |
| `firmware/MicroBrute_Firmware_Update_1_0_4_114.bin` | Raw ARM binary (load at 0x2000) |
| `firmware/MicroBrute_1_0_3_2.bin` | Raw ARM binary v1.0.3.2 |
| `tools/mbf_decrypt.py` | Decryption tool |

### Peripheral Usage Map

From literal pool analysis — addresses referencing LPC2361 peripheral registers:

| Peripheral | Base Address | Code References | Likely Purpose |
|-----------|-------------|-----------------|----------------|
| System Control | 0xE01FC000 | 0x2170, 0xA39C | PLL, clocking, power |
| PINSEL | 0xE002C000 | 0x2C44, 0x3EB4, 0x4350, 0x6CAC, 0x752C | Pin mux config |
| VIC | 0xFFFFF000 | 0x2C64, 0x3250, 0x3F7C, 0x4340, 0x6114 | Interrupt setup (5 refs) |
| UART0 | 0xE000C000 | 0x3EA8 | MIDI or debug serial |
| Timer0 | 0xE0004000 | 0x3F70, 0x6750 | Tempo/timing |
| Timer1 | 0xE0008000 | 0x9C5C | Secondary timing |
| SPI | 0xE0028000 | 0x4348, 0x6B78 | External device comm |
| SSP0 | 0xE0020000 | 0xE3B4 | SPI-like interface |
| PWM0/1 | 0xE001C000 | 0x4610 | Waveform/indicator |
| Fast GPIO 0 | 0x3FFFC000 | 0x669C, 0x6B74 | LEDs, buttons, control |

**Not found as literals** (accessed via helper functions or indirectly):
- I2C0 (0xE0044000) — for MCP4728 DAC
- DAC (0xE006C000) — on-chip 10-bit DAC
- ADC (0xE004C000)
- UART1 (0xE0010000) — MIDI?

### Code Statistics

| Metric | Value |
|--------|-------|
| Thumb functions (~PUSH {.., LR}) | ~327 |
| ARM functions (~STMDB SP!) | ~18 |
| Printable strings (6+ chars) | 4 (runtime only) |
| Exception handlers | 0x2040-0x2054 |

### Loading in Ghidra

1. Import `.bin` file
2. Language: `ARM:LE:32:v4t` (ARM7TDMI)
3. Base address: `0x00002000`
4. Install SVD-Loader, load LPC23xx SVD for peripheral labels
5. Entry point: `0x00002184`
6. Mark 0x2040-0x2054 as exception handler pointer table
7. Functions start predominantly as Thumb — enable Thumb disassembly
