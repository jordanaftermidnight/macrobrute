#!/usr/bin/env python3
"""
Static analysis of MicroBrute LPC2361 firmware binary.

Extracts function boundaries, string references, peripheral accesses,
and SysEx-related code without requiring Ghidra.

Usage:
    python3 tools/analyze_firmware.py                    # analyze v1.0.4.114
    python3 tools/analyze_firmware.py firmware/other.bin  # analyze specific binary
    python3 tools/analyze_firmware.py --sysex             # focus on SysEx/MIDI
    python3 tools/analyze_firmware.py --peripherals       # focus on peripheral accesses
"""

import argparse
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from mbf_decrypt import decrypt_mbf, validate_and_strip, ihex_to_bin

BASE = 0x2000
FLASH_END = 0x20000  # 128KB


# LPC2361 peripheral base addresses
PERIPHERALS = {
    0xE0004000: "Timer0",
    0xE0008000: "Timer1",
    0xE000C000: "UART0",
    0xE0010000: "UART1_MIDI",
    0xE001C000: "I2C0_MCP4728",
    0xE002C000: "PINSEL",
    0xE0034000: "ADC",
    0xE006C000: "DAC",
    0xE0068000: "SSP0_SPI",
    0xE01FC000: "SysCtrl",
    0x3FFFC000: "FastGPIO",
    0xFFFFF000: "VIC",
}


def load_firmware(path):
    """Load firmware from .mbf, .hex, or .bin file."""
    if path.endswith('.mbf'):
        with open(path, 'rb') as f:
            data = f.read()
        dec = decrypt_mbf(data)
        payload = validate_and_strip(dec)
        hex_text = payload.decode('ascii', errors='replace')
        base, binary, entry = ihex_to_bin(hex_text)
        return base, binary, entry
    elif path.endswith('.hex'):
        with open(path, 'r') as f:
            hex_text = f.read()
        return ihex_to_bin(hex_text)
    else:
        with open(path, 'rb') as f:
            binary = f.read()
        return BASE, binary, None


def find_strings(binary, min_len=4):
    """Find printable ASCII strings in the binary."""
    strings = []
    current = []
    start = None
    for i, b in enumerate(binary):
        if 0x20 <= b <= 0x7E:
            if not current:
                start = i
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append((start, ''.join(current)))
            current = []
            start = None
    if len(current) >= min_len:
        strings.append((start, ''.join(current)))
    return strings


def find_thumb_functions(binary):
    """Find Thumb function prologues (PUSH {.., LR}) and their BX LR returns."""
    functions = []
    for i in range(0, len(binary) - 1, 2):
        hw = binary[i] | (binary[i + 1] << 8)
        # PUSH {regs, LR}: 0xB5xx where bit 8 is set (LR push)
        if (hw & 0xFF00) == 0xB500:
            regs = hw & 0xFF
            reg_list = []
            for bit in range(8):
                if regs & (1 << bit):
                    reg_list.append(f"r{bit}")
            reg_list.append("lr")
            functions.append((i, reg_list))
    return functions


def find_arm_functions(binary):
    """Find ARM mode function indicators (STMFD SP!, {.., LR})."""
    functions = []
    for i in range(0, len(binary) - 3, 4):
        word = struct.unpack_from('<I', binary, i)[0]
        # STMFD SP!, {regs, LR}: 0xE92D4xxx or 0xE92Dxxxx with bit 14 set
        if (word & 0xFFFF0000) == 0xE92D0000 and (word & (1 << 14)):
            functions.append(i)
    return functions


def find_peripheral_refs(binary, base):
    """Find references to peripheral base addresses in the binary."""
    refs = {}
    for i in range(0, len(binary) - 3, 4):
        word = struct.unpack_from('<I', binary, i)[0]
        for periph_base, name in PERIPHERALS.items():
            # Check for exact base address or base + small offset
            if periph_base <= word < periph_base + 0x400:
                offset = word - periph_base
                addr = base + i
                if name not in refs:
                    refs[name] = []
                refs[name].append((addr, word, offset))
    return refs


def find_sysex_markers(binary, base):
    """Find potential SysEx-related code (0xF0 start, 0xF7 end, Arturia ID)."""
    results = []

    # Look for 0xF0 (SysEx start) in data/immediate values
    for i in range(0, len(binary) - 1, 2):
        hw = binary[i] | (binary[i + 1] << 8)
        # CMP Rn, #0xF0
        if (hw & 0xFF00) == 0x2800 and (hw & 0xFF) == 0xF0:
            results.append((base + i, "CMP Rn, #0xF0 (SysEx start check)"))
        # CMP Rn, #0xF7
        if (hw & 0xFF00) == 0x2800 and (hw & 0xFF) == 0xF7:
            results.append((base + i, "CMP Rn, #0xF7 (SysEx end check)"))

    # Also check for Thumb MOV #imm with these values
    for i in range(0, len(binary) - 1, 2):
        hw = binary[i] | (binary[i + 1] << 8)
        # MOV Rn, #0xF0
        if (hw & 0xFF00) == 0x2000 and (hw & 0xFF) == 0xF0:
            results.append((base + i, "MOV Rn, #0xF0 (SysEx start byte)"))
        if (hw & 0xFF00) == 0x2000 and (hw & 0xFF) == 0xF7:
            results.append((base + i, "MOV Rn, #0xF7 (SysEx end byte)"))

    # Look for Arturia manufacturer IDs in data
    # Arturia: 0x00 0x20 0x6B (3-byte SysEx manufacturer ID)
    for i in range(len(binary) - 2):
        if binary[i] == 0x00 and binary[i + 1] == 0x20 and binary[i + 2] == 0x6B:
            results.append((base + i, "Arturia manufacturer ID (00 20 6B)"))

    # Look for 0x1C (28 = SysEx packet size from LPC23XXUpdater)
    for i in range(0, len(binary) - 1, 2):
        hw = binary[i] | (binary[i + 1] << 8)
        if (hw & 0xFF00) == 0x2800 and (hw & 0xFF) == 0x1C:
            results.append((base + i, "CMP Rn, #0x1C (28-byte SysEx packet size?)"))

    return results


def find_branch_targets(binary, base):
    """Find Thumb branch targets to map call graph."""
    branches = {}
    for i in range(0, len(binary) - 3, 2):
        hw = binary[i] | (binary[i + 1] << 8)

        # Thumb BL (32-bit): first half 0xF000-0xF7FF, second half 0xF800-0xFFFF
        if (hw & 0xF800) == 0xF000:
            hw2 = binary[i + 2] | (binary[i + 3] << 8)
            if (hw2 & 0xF800) == 0xF800:
                # Decode BL offset
                s = (hw >> 10) & 1
                imm10 = hw & 0x3FF
                j1 = (hw2 >> 13) & 1
                j2 = (hw2 >> 11) & 1
                imm11 = hw2 & 0x7FF
                i1 = ~(j1 ^ s) & 1
                i2 = ~(j2 ^ s) & 1
                offset = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    offset |= 0xFE000000  # sign extend
                    offset = offset - 0x100000000
                target = base + i + 4 + offset
                src = base + i
                if target not in branches:
                    branches[target] = []
                branches[target].append(src)

    return branches


def analyze_uart0_region(binary, base):
    """Deep-dive analysis of the UART0 init region around 0x3EA8."""
    start_offset = 0x3EA8 - base
    # Analyze 256 bytes around UART0 init
    region_start = max(0, start_offset - 64)
    region_end = min(len(binary), start_offset + 192)

    print("\n=== UART0 Region Disassembly (0x{:04X}-0x{:04X}) ===".format(
        base + region_start, base + region_end))

    # Find all data words that look like addresses or constants
    for i in range(region_start, region_end - 3, 4):
        word = struct.unpack_from('<I', binary, i)[0]
        addr = base + i
        notes = []

        # Check if it's a peripheral address
        for periph_base, name in PERIPHERALS.items():
            if periph_base <= word < periph_base + 0x400:
                notes.append(f"{name}+0x{word - periph_base:X}")

        # Check if it's a code address
        if BASE <= word < BASE + len(binary):
            notes.append(f"code_ref")

        # Check for baud rate divisors
        # PCLK=15MHz: 115200 baud -> DL=8, 31250 baud -> DL=30
        if word in (8, 30, 0x08, 0x1E):
            notes.append(f"possible baud divisor")

        if notes:
            print(f"  0x{addr:08X}: 0x{word:08X}  [{', '.join(notes)}]")


def main():
    parser = argparse.ArgumentParser(description="Static firmware analysis for MicroBrute LPC2361")
    parser.add_argument("input", nargs='?',
                        default=os.path.join(os.path.dirname(__file__), '..',
                                             'firmware', 'MicroBrute_Firmware_Update_1_0_4_114.mbf'),
                        help="Firmware file (.mbf, .hex, or .bin)")
    parser.add_argument("--sysex", action="store_true", help="Focus on SysEx/MIDI analysis")
    parser.add_argument("--peripherals", action="store_true", help="Focus on peripheral accesses")
    parser.add_argument("--strings", action="store_true", help="Dump all strings")
    parser.add_argument("--functions", action="store_true", help="List all detected functions")
    parser.add_argument("--uart", action="store_true", help="Deep-dive UART0 region")
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    args = parser.parse_args()

    if not any([args.sysex, args.peripherals, args.strings, args.functions, args.uart, args.all]):
        args.all = True

    base, binary, entry = load_firmware(args.input)
    print(f"Firmware: {args.input}")
    print(f"Base: 0x{base:08X}, Size: {len(binary)} bytes ({len(binary)/1024:.1f} KB)")
    if entry:
        print(f"Entry: 0x{entry:08X}")

    # ================================================================
    # Functions
    # ================================================================
    if args.functions or args.all:
        thumb_fns = find_thumb_functions(binary)
        arm_fns = find_arm_functions(binary)
        print(f"\n=== Function Detection ===")
        print(f"Thumb functions (PUSH {{.., LR}}): {len(thumb_fns)}")
        print(f"ARM functions (STMFD SP!, {{.., LR}}): {len(arm_fns)}")

        # Show first/last few
        if thumb_fns:
            print(f"\nFirst 10 Thumb functions:")
            for offset, regs in thumb_fns[:10]:
                print(f"  0x{base + offset:08X}: PUSH {{{', '.join(regs)}}}")
            print(f"\nLast 5 Thumb functions:")
            for offset, regs in thumb_fns[-5:]:
                print(f"  0x{base + offset:08X}: PUSH {{{', '.join(regs)}}}")

        # Call graph hotspots
        branches = find_branch_targets(binary, base)
        if branches:
            # Sort by number of callers
            hotspots = sorted(branches.items(), key=lambda x: len(x[1]), reverse=True)
            print(f"\nTop 20 most-called targets:")
            for target, callers in hotspots[:20]:
                print(f"  0x{target:08X}: {len(callers)} callers")

    # ================================================================
    # Strings
    # ================================================================
    if args.strings or args.all:
        strings = find_strings(binary, min_len=4)
        print(f"\n=== Strings ({len(strings)} found, min 4 chars) ===")

        # Categorize strings
        midi_strings = [(o, s) for o, s in strings if any(
            k in s.lower() for k in ['midi', 'sysex', 'note', 'channel', 'velocity'])]
        error_strings = [(o, s) for o, s in strings if any(
            k in s.lower() for k in ['error', 'fail', 'abort', 'pure', 'heap', 'memory'])]
        arturia_strings = [(o, s) for o, s in strings if 'arturia' in s.lower() or 'brute' in s.lower()]

        if arturia_strings:
            print(f"\nArturia/MicroBrute strings:")
            for offset, s in arturia_strings:
                print(f"  0x{base + offset:08X}: \"{s}\"")

        if error_strings:
            print(f"\nError/runtime strings:")
            for offset, s in error_strings:
                print(f"  0x{base + offset:08X}: \"{s}\"")

        if midi_strings:
            print(f"\nMIDI-related strings:")
            for offset, s in midi_strings:
                print(f"  0x{base + offset:08X}: \"{s}\"")

        # Show all strings in compact format
        print(f"\nAll strings:")
        for offset, s in strings:
            truncated = s[:80] + "..." if len(s) > 80 else s
            print(f"  0x{base + offset:08X}: \"{truncated}\"")

    # ================================================================
    # Peripheral References
    # ================================================================
    if args.peripherals or args.all:
        refs = find_peripheral_refs(binary, base)
        print(f"\n=== Peripheral References ===")
        for name in sorted(refs.keys()):
            locations = refs[name]
            print(f"\n{name} ({len(locations)} references):")
            for addr_loc, value, offset in sorted(locations):
                print(f"  0x{addr_loc:08X}: 0x{value:08X} (+0x{offset:03X})")

    # ================================================================
    # SysEx / MIDI Analysis
    # ================================================================
    if args.sysex or args.all:
        markers = find_sysex_markers(binary, base)
        print(f"\n=== SysEx/MIDI Markers ({len(markers)} found) ===")
        for addr_loc, description in sorted(markers):
            print(f"  0x{addr_loc:08X}: {description}")

    # ================================================================
    # UART0 Deep Dive
    # ================================================================
    if args.uart or args.all:
        analyze_uart0_region(binary, base)

    # ================================================================
    # Free Space Analysis
    # ================================================================
    if args.all:
        # Find the last non-zero byte
        last_nonzero = len(binary) - 1
        while last_nonzero > 0 and binary[last_nonzero] == 0x00:
            last_nonzero -= 1
        last_nonzero += 1  # exclusive end

        # Find largest runs of 0xFF (erased flash)
        ff_runs = []
        current_start = None
        for i in range(len(binary)):
            if binary[i] == 0xFF:
                if current_start is None:
                    current_start = i
            else:
                if current_start is not None and i - current_start >= 16:
                    ff_runs.append((current_start, i - current_start))
                current_start = None
        if current_start is not None and len(binary) - current_start >= 16:
            ff_runs.append((current_start, len(binary) - current_start))

        print(f"\n=== Flash Space Analysis ===")
        print(f"Binary size: {len(binary)} bytes")
        print(f"Last non-zero byte: 0x{base + last_nonzero:08X} (offset {last_nonzero})")
        print(f"Effective code end: 0x{base + last_nonzero:08X}")
        print(f"Free flash (to 128KB): {FLASH_END - base - last_nonzero} bytes "
              f"({(FLASH_END - base - last_nonzero) / 1024:.1f} KB)")

        if ff_runs:
            ff_runs.sort(key=lambda x: x[1], reverse=True)
            print(f"\nLargest erased (0xFF) regions:")
            for start, size in ff_runs[:5]:
                print(f"  0x{base + start:08X} - 0x{base + start + size:08X}: "
                      f"{size} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
