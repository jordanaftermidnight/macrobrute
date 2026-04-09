#!/usr/bin/env python3
"""
MicroBrute .mbf firmware encryptor

Takes an Intel HEX file (or raw binary + base address) and produces
an encrypted .mbf file that can be flashed via MicroBrute Connection
or direct MIDI SysEx.

The .mbf format:
  [24-byte key "ArturiaminiBruteFirmware"][\x00][Intel HEX text]
  All XOR-encrypted with the key, starting at key index 4.

Usage:
    python3 mbf_encrypt.py firmware.hex                 # from Intel HEX
    python3 mbf_encrypt.py firmware.bin --binary        # from raw binary (base 0x2000)
    python3 mbf_encrypt.py firmware.bin -b -a 0x2000    # explicit base address
    python3 mbf_encrypt.py firmware.hex -o custom.mbf   # custom output name
"""

import argparse
import struct
import sys


KEY = b"ArturiaminiBruteFirmware"
KEY_START_INDEX = 4


def encrypt_mbf(data: bytes) -> bytes:
    """Encrypt data using the .mbf XOR cipher. Same as decrypt (symmetric)."""
    key_len = len(KEY)
    ki = KEY_START_INDEX % key_len
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ KEY[ki]
        ki = (ki + 1) % key_len
    return bytes(result)


def bin_to_ihex(binary: bytes, base_addr: int = 0x2000, entry: int | None = None) -> str:
    """Convert raw binary to Intel HEX format."""
    lines = []

    # Extended Linear Address record if base >= 0x10000
    if base_addr >= 0x10000:
        upper = (base_addr >> 16) & 0xFFFF
        data = f"{upper:04X}"
        line = f":02000004{data}"
        raw = bytes.fromhex(line[1:])
        checksum = (-sum(raw)) & 0xFF
        lines.append(f"{line}{checksum:02X}")
        base_offset = base_addr & 0xFFFF
    else:
        # Still emit extended address record for consistency
        lines.append(":020000040000FA")
        base_offset = base_addr

    # Data records (16 bytes per line)
    for offset in range(0, len(binary), 16):
        chunk = binary[offset:offset + 16]
        byte_count = len(chunk)
        address = (base_offset + offset) & 0xFFFF
        record = f":{byte_count:02X}{address:04X}00"
        for b in chunk:
            record += f"{b:02X}"
        raw = bytes.fromhex(record[1:])
        checksum = (-sum(raw)) & 0xFF
        record += f"{checksum:02X}"
        lines.append(record)

    # Start Linear Address record (entry point)
    if entry is not None:
        data = f"{entry:08X}"
        line = f":04000005{data}"
        raw = bytes.fromhex(line[1:])
        checksum = (-sum(raw)) & 0xFF
        lines.append(f"{line}{checksum:02X}")

    # EOF record
    lines.append(":00000001FF")

    return "\n".join(lines) + "\n"


def validate_arm_binary(binary: bytes, base_addr: int):
    """Sanity check the binary looks like valid ARM firmware."""
    if len(binary) < 64:
        print("WARNING: Binary is very small (<64 bytes)", file=sys.stderr)
        return False

    # Check vector table has LDR PC instructions
    ldr_count = 0
    for i in range(8):
        if i == 5:  # checksum slot
            continue
        word = struct.unpack_from('<I', binary, i * 4)[0]
        if (word & 0xFFFFF000) in (0xE59FF000, 0xE51FF000):
            ldr_count += 1

    if ldr_count < 5:
        print(f"WARNING: Only {ldr_count}/7 vectors are LDR PC instructions",
              file=sys.stderr)
        return False

    # Check handler addresses are in range
    for i in range(8):
        if i == 5:
            continue
        addr = struct.unpack_from('<I', binary, 0x20 + i * 4)[0]
        if not (base_addr <= addr < base_addr + len(binary) + 0x1000):
            print(f"WARNING: Handler {i} at 0x{addr:08X} may be out of range",
                  file=sys.stderr)

    # Check it fits in LPC2361 flash
    if base_addr + len(binary) > 0x20000:
        print(f"ERROR: Binary exceeds 128KB flash boundary", file=sys.stderr)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt firmware into Arturia MicroBrute .mbf format")
    parser.add_argument("input", help="Input file (Intel HEX or raw binary)")
    parser.add_argument("-o", "--output", help="Output .mbf file")
    parser.add_argument("-b", "--binary", action="store_true",
                        help="Input is raw binary (not Intel HEX)")
    parser.add_argument("-a", "--address", default="0x2000",
                        help="Base address for binary input (default: 0x2000)")
    parser.add_argument("-e", "--entry", default=None,
                        help="Entry point address (default: auto-detect from binary)")
    parser.add_argument("--no-validate", action="store_true",
                        help="Skip ARM binary validation")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    base_addr = int(args.address, 0)

    if args.binary:
        # Raw binary input — convert to Intel HEX
        with open(args.input, "rb") as f:
            binary = f.read()

        if not args.no_validate:
            if not validate_arm_binary(binary, base_addr):
                print("Binary validation failed. Use --no-validate to force.",
                      file=sys.stderr)
                sys.exit(1)

        entry = int(args.entry, 0) if args.entry else None
        hex_text = bin_to_ihex(binary, base_addr, entry)

        if not args.quiet:
            print(f"Input binary: {len(binary)} bytes at 0x{base_addr:08X}")
    else:
        # Intel HEX input — read as-is
        with open(args.input, "r") as f:
            hex_text = f.read()

        if not args.quiet:
            print(f"Input Intel HEX: {len(hex_text)} bytes")

    # Build the plaintext: key + null + hex data
    plaintext = KEY + b"\x00" + hex_text.encode("ascii")

    # Encrypt
    encrypted = encrypt_mbf(plaintext)

    # Output
    out_path = args.output or args.input.rsplit(".", 1)[0] + ".mbf"
    with open(out_path, "wb") as f:
        f.write(encrypted)

    if not args.quiet:
        print(f"Wrote: {out_path} ({len(encrypted)} bytes)")


if __name__ == "__main__":
    main()
