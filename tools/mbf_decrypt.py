#!/usr/bin/env python3
"""
MicroBrute .mbf firmware decryptor

.mbf files use a repeating XOR cipher with the key "ArturiaminiBruteFirmware".
The key index starts at offset 4 (i.e., 4 % keyLen). After decryption, the
first 24 bytes of the file equal the key string (validation check). The
remaining payload is Intel HEX (ihex) format containing the ARM firmware.

Discovered by disassembling the LPC23XXCrypter class in
MicroBrute Connection.app (Mach-O i386, JUCE C++).

Usage:
    python3 mbf_decrypt.py firmware.mbf              # outputs firmware.hex
    python3 mbf_decrypt.py firmware.mbf -b            # also outputs firmware.bin
    python3 mbf_decrypt.py firmware.mbf -o out.hex    # custom output name
"""

import argparse
import struct
import sys


KEY = b"ArturiaminiBruteFirmware"
KEY_START_INDEX = 4  # constructor does: keyIndex = 4 % keyLen


def decrypt_mbf(data: bytes) -> bytes:
    """Decrypt .mbf data using XOR cipher. Returns raw decrypted bytes."""
    key_len = len(KEY)
    ki = KEY_START_INDEX % key_len
    result = bytearray(len(data))
    for i in range(len(data)):
        result[i] = data[i] ^ KEY[ki]
        ki = (ki + 1) % key_len
    return bytes(result)


def validate_and_strip(decrypted: bytes) -> bytes:
    """Validate key header and return Intel HEX payload.

    .mbf structure after decryption: [24-byte key][0x00 null][Intel HEX text]
    """
    if decrypted[:len(KEY)] != KEY:
        print(f"ERROR: Header mismatch. Expected {KEY!r}, got {decrypted[:len(KEY)]!r}",
              file=sys.stderr)
        sys.exit(1)
    # Skip key + null terminator
    offset = len(KEY)
    if offset < len(decrypted) and decrypted[offset] == 0x00:
        offset += 1
    return decrypted[offset:]


def ihex_to_bin(hex_text: str) -> tuple[int, bytes, int | None]:
    """Parse Intel HEX text into (base_address, binary, entry_point)."""
    segments: dict[int, bytes] = {}
    base_addr = 0
    entry = None

    for line in hex_text.splitlines():
        line = line.strip()
        if not line or not line.startswith(":"):
            continue

        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        data_hex = line[9:9 + byte_count * 2]

        # Verify checksum
        raw = bytes.fromhex(line[1:])
        if sum(raw) & 0xFF != 0:
            print(f"WARNING: Checksum error in line: {line[:40]}...", file=sys.stderr)

        if record_type == 0x00:  # Data
            segments[base_addr + address] = bytes.fromhex(data_hex)
        elif record_type == 0x04:  # Extended Linear Address
            base_addr = int(data_hex[:4], 16) << 16
        elif record_type == 0x05:  # Start Linear Address (entry point)
            entry = int(data_hex[:8], 16)
        elif record_type == 0x01:  # EOF
            break

    if not segments:
        return 0, b"", entry

    min_addr = min(segments.keys())
    max_addr = max(k + len(v) for k, v in segments.items())
    binary = bytearray(max_addr - min_addr)
    for addr, data in segments.items():
        binary[addr - min_addr: addr - min_addr + len(data)] = data

    return min_addr, bytes(binary), entry


def print_info(base: int, binary: bytes, entry: int | None):
    """Print firmware analysis."""
    print(f"  Base address:  0x{base:08X}")
    print(f"  Binary size:   {len(binary)} bytes ({len(binary)/1024:.1f} KB)")
    if entry is not None:
        print(f"  Entry point:   0x{entry:08X}")

    # ARM vector table
    if len(binary) >= 32:
        labels = ["Reset", "Undef", "SWI", "PrefAbort", "DataAbort",
                   "Checksum", "IRQ", "FIQ"]
        print("  Vector table:")
        for i in range(8):
            word = struct.unpack_from("<I", binary, i * 4)[0]
            print(f"    {labels[i]:>12}: 0x{word:08X}")

    # Flash usage (LPC2361 = 128KB)
    flash_size = 128 * 1024
    print(f"  Flash usage:   {len(binary)*100/flash_size:.1f}% of {flash_size//1024}KB")


def main():
    parser = argparse.ArgumentParser(description="Decrypt Arturia MicroBrute .mbf firmware files")
    parser.add_argument("input", help="Input .mbf file")
    parser.add_argument("-o", "--output", help="Output Intel HEX file (default: input with .hex extension)")
    parser.add_argument("-b", "--binary", action="store_true", help="Also output raw binary (.bin)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress info output")
    args = parser.parse_args()

    # Read and decrypt
    with open(args.input, "rb") as f:
        encrypted = f.read()

    if not args.quiet:
        print(f"Input: {args.input} ({len(encrypted)} bytes)")

    decrypted = decrypt_mbf(encrypted)
    payload = validate_and_strip(decrypted)

    if not args.quiet:
        print(f"Decrypted payload: {len(payload)} bytes (Intel HEX)")

    # Output Intel HEX
    out_hex = args.output or args.input.rsplit(".", 1)[0] + ".hex"
    with open(out_hex, "wb") as f:
        f.write(payload)
    if not args.quiet:
        print(f"Wrote: {out_hex}")

    # Optional binary output
    if args.binary:
        hex_text = payload.decode("ascii", errors="replace")
        base, binary, entry = ihex_to_bin(hex_text)
        out_bin = out_hex.rsplit(".", 1)[0] + ".bin"
        with open(out_bin, "wb") as f:
            f.write(binary)
        if not args.quiet:
            print(f"Wrote: {out_bin}")
            print_info(base, binary, entry)


if __name__ == "__main__":
    main()
