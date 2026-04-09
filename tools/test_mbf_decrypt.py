#!/usr/bin/env python3
"""
Test suite for MicroBrute .mbf firmware decryption.

Validates the cipher, decryption tool, Intel HEX parsing, and ARM binary integrity.
Run: python3 tools/test_mbf_decrypt.py
"""

import struct
import sys
import os

# Add tools dir to path
sys.path.insert(0, os.path.dirname(__file__))
from mbf_decrypt import decrypt_mbf, validate_and_strip, ihex_to_bin, KEY, KEY_START_INDEX

FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), '..', 'firmware')

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {detail}")


def run_tests():
    global passed, failed

    # ================================================================
    # 1. Cipher algorithm tests
    # ================================================================
    print("\n=== Cipher Algorithm ===")

    test("Key is 24 bytes ASCII",
         len(KEY) == 24 and all(0x20 <= b <= 0x7E for b in KEY))

    test("Key start index is 4",
         KEY_START_INDEX == 4)

    test("Symmetric: decrypt(decrypt(x)) == x",
         decrypt_mbf(decrypt_mbf(b"test data " * 100)) == b"test data " * 100)

    # Empty data
    test("Empty data decrypts to empty", decrypt_mbf(b"") == b"")

    # Single byte
    single = decrypt_mbf(b"\x00")
    test("Single byte XOR with key[4]",
         single == bytes([KEY[KEY_START_INDEX % len(KEY)]]))

    # Key wrapping: after 24 bytes, should restart
    zeros = bytes(48)
    dec_zeros = decrypt_mbf(zeros)
    # Bytes 0-23 should XOR with key[4:] + key[:4]
    # Bytes 24-47 should XOR with same pattern again
    test("Key wraps correctly after keyLen bytes",
         dec_zeros[0:24] == dec_zeros[24:48],
         f"first24={dec_zeros[0:24].hex()}, second24={dec_zeros[24:48].hex()}")

    # ================================================================
    # 2. v1.0.4.114 decryption
    # ================================================================
    mbf_path_1 = os.path.join(FIRMWARE_DIR, 'MicroBrute_Firmware_Update_1_0_4_114.mbf')
    if os.path.exists(mbf_path_1):
        print("\n=== v1.0.4.114 Decryption ===")
        with open(mbf_path_1, 'rb') as f:
            mbf1 = f.read()

        dec1 = decrypt_mbf(mbf1)
        test("Header matches key", dec1[:len(KEY)] == KEY)

        payload1 = validate_and_strip(dec1)
        test("Payload is pure ASCII",
             all(b < 128 for b in payload1))

        test("Payload starts with Intel HEX record",
             payload1[0:1] == b':',
             f"got {payload1[:5]!r}")

        # Parse Intel HEX
        hex_text = payload1.decode('ascii', errors='replace')
        base1, bin1, entry1 = ihex_to_bin(hex_text)

        test("Base address is 0x2000", base1 == 0x2000)
        test("Entry point is 0x2184", entry1 == 0x2184)
        test("Binary size is 52664 bytes", len(bin1) == 52664)
        test("Fits in 128KB flash", base1 + len(bin1) <= 0x20000)

        # Intel HEX checksums
        csum_errors = 0
        for line in hex_text.splitlines():
            line = line.strip()
            if line.startswith(':'):
                raw = bytes.fromhex(line[1:])
                if sum(raw) & 0xFF != 0:
                    csum_errors += 1
        test("All Intel HEX checksums valid", csum_errors == 0,
             f"{csum_errors} errors")

        # ARM vector table
        print("\n=== v1.0.4.114 ARM Vector Table ===")
        vectors = [struct.unpack_from('<I', bin1, i * 4)[0] for i in range(8)]

        ldr_mask = 0xFFFFF000
        ldr_pc_patterns = (0xE59FF000, 0xE51FF000)
        for i, v in enumerate(vectors):
            if i == 5:  # checksum slot
                continue
            is_ldr = (v & ldr_mask) in ldr_pc_patterns
            labels = ["Reset", "Undef", "SWI", "PrefAbort", "DataAbort",
                       "Checksum", "IRQ", "FIQ"]
            test(f"Vector {labels[i]} is LDR PC (0x{v:08X})", is_ldr)

        # Handler addresses in range
        print("\n=== v1.0.4.114 Handler Addresses ===")
        for i in range(8):
            addr = struct.unpack_from('<I', bin1, 0x20 + i * 4)[0]
            if i == 5:
                continue
            test(f"Handler {i} addr 0x{addr:08X} in flash range",
                 0x2000 <= addr < 0x20000)

        # IRQ vector is NXP VIC pattern
        test("IRQ vector is NXP VIC pattern (0xE51FF120)",
             vectors[6] == 0xE51FF120)

        # Known strings
        print("\n=== v1.0.4.114 Known Strings ===")
        test("Contains 'Pure virtual fn called'",
             b"Pure virtual fn called" in bin1)
        test("Contains 'Out of heap memory'",
             b"Out of heap memory" in bin1)

        # Thumb code patterns
        bx_lr = sum(1 for i in range(0, len(bin1) - 1, 2)
                     if bin1[i] == 0x70 and bin1[i + 1] == 0x47)
        test(f"Has Thumb BX LR returns ({bx_lr})", bx_lr > 100)

        push_lr = sum(1 for i in range(0, len(bin1) - 1, 2)
                       if bin1[i + 1] & 0xFF == 0xB5)
        test(f"Has Thumb PUSH {{..,LR}} ({push_lr})", push_lr > 100)

        # Round trip
        test("Round-trip: encrypt(decrypt(mbf)) == mbf",
             decrypt_mbf(dec1) == mbf1)

    else:
        print(f"\n  SKIP: {mbf_path_1} not found")

    # ================================================================
    # 3. v1.0.3.2 decryption (if available)
    # ================================================================
    mbf_path_2 = os.path.expanduser(
        '~/Downloads/MicroBrute_1_0_3_2_mac/MicroBrute_Firmware_Release_V1.0.3.2.mbf')
    if os.path.exists(mbf_path_2):
        print("\n=== v1.0.3.2 Decryption ===")
        with open(mbf_path_2, 'rb') as f:
            mbf2 = f.read()

        dec2 = decrypt_mbf(mbf2)
        test("Header matches key", dec2[:len(KEY)] == KEY)

        payload2 = validate_and_strip(dec2)
        test("Payload is pure ASCII", all(b < 128 for b in payload2))

        hex_text2 = payload2.decode('ascii', errors='replace')
        base2, bin2, entry2 = ihex_to_bin(hex_text2)

        test("Base address is 0x2000", base2 == 0x2000)
        test("Entry point is 0x2184", entry2 == 0x2184)
        test("Binary size is 49024 bytes", len(bin2) == 49024)
        test("Fits in 128KB flash", base2 + len(bin2) <= 0x20000)

        test("Round-trip matches original", decrypt_mbf(dec2) == mbf2)

        # Both versions share entry point
        test("Both versions share entry point 0x2184",
             entry1 == entry2 == 0x2184)

        # Both versions have same base
        test("Both versions load at 0x2000",
             base1 == base2 == 0x2000)
    else:
        print(f"\n  SKIP: {mbf_path_2} not found")

    # ================================================================
    # Summary
    # ================================================================
    print(f"\n{'=' * 50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print(f"{'=' * 50}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
