# LPC2361 Firmware Investigation — Step-by-Step Guide

## Prerequisites

### Hardware
- PL2303HX USB-TTL adapter (3.3V) — already owned
- Multimeter with continuity mode
- Oscilloscope (DSO130 or external)
- Fine probe tips or test clips

### Software (macOS)
```bash
# Install lpc21isp (ISP flash tool)
brew install lpc21isp

# Install Ghidra (disassembler)
brew install --cask ghidra

# Python tools
pip3 install pyserial binwalk
```

### Optional (if CRP is enabled)
- PicoEMP (~$50): https://github.com/newaetech/chipshouter-picoemp
- Second Raspberry Pi Pico for PicoEMP build

---

## Phase 1: Locate ISP Pins on Physical PCB

### Target Pins

| LPC2361 Pin | Function | Package Pin | PCB Location |
|-------------|----------|-------------|--------------|
| P0.2 | TXD0 | Pin 98 | Rear board, near JTAG header |
| P0.3 | RXD0 | Pin 99 | Rear board, near JTAG header |
| P2.10 | ISP entry | Pin 53 | Rear board |
| RESET | System reset | Pin 17 | Rear board |
| GND | Ground | Multiple | TP72 |

### Procedure

1. Open MicroBrute (6 screws on bottom)
2. Photograph rear board at high resolution
3. Locate LPC2361 (QFP-100 package, largest IC on rear board)
4. Locate JTAG header (10-pin, fully populated per docs)
5. Trace pin 98 (P0.2/TXD0) — likely accessible at JTAG header or nearby via
6. Trace pin 99 (P0.3/RXD0) — same area
7. Find P2.10 (pin 53) — may need to probe with multimeter
8. Use JTAG header pin mapping from NXP LPC2361 JTAG standard:
   - Pin 1: TMS
   - Pin 3: TCK
   - Pin 5: TDO
   - Pin 7: TDI
   - Pin 9: nTRST
   - Even pins: GND
   Note: UART0 pins may NOT be on JTAG header — they're separate

---

## Phase 2: Connect PL2303HX

### Wiring

```
  PL2303HX          LPC2361
  ────────          ───────
  TX  ──────────── P0.3 (RXD0, pin 99)
  RX  ──────────── P0.2 (TXD0, pin 98)
  GND ──────────── GND (TP72)
  3.3V ── DO NOT CONNECT (LPC2361 has own power)
```

**CRITICAL:** Do NOT connect PL2303HX VCC to LPC2361. The synth
powers the MCU. External voltage can cause latch-up.

### Enter ISP Mode

1. Power off MicroBrute (unplug power adapter)
2. Connect PL2303HX wiring
3. Pull P2.10 LOW (jumper wire to GND)
4. Power on MicroBrute
5. LPC2361 enters ISP bootloader (instead of user firmware)

### Detect Chip

```bash
# On macOS, find the serial port
ls /dev/tty.usbserial*

# Attempt detection (12MHz crystal confirmed)
lpc21isp -detectonly dummy.hex /dev/tty.usbserial-XXXX 115200 12000
```

### Expected Results

| Response | Meaning | Next Step |
|----------|---------|-----------|
| Part ID: 0x1600F701 | LPC2361 confirmed | Proceed to read |
| Read success | No CRP! | **DUMP IMMEDIATELY** |
| Error 19 | CRP1 or CRP2 | Flash is locked |
| No response | CRP3, wiring issue, or wrong baud | Check wiring, try 38400 |

---

## Phase 3A: No CRP — Dump Flash

If ISP read succeeds (unlikely but best case):

```bash
# Read entire 128KB flash
lpc21isp -readdump firmware_dump.bin /dev/tty.usbserial-XXXX 115200 12000

# Verify
hexdump -C firmware_dump.bin | head -20

# Check for ARM vector table at 0x0
# First word should be stack pointer (0x4000xxxx = SRAM)
# Second word should be reset vector (0x000000xx)
```

---

## Phase 3B: CRP Detected — Alternative Approaches

### Approach 1: Capture .mbf Firmware Update

```bash
# Download latest firmware from Arturia MIDI Control Center
# File: MicroBrute_firmware_v1.0.4.114.mbf (144.73 KB)

# Analyze with binwalk
binwalk MicroBrute_firmware_v1.0.4.114.mbf

# Check entropy (high = encrypted/compressed)
binwalk -E MicroBrute_firmware_v1.0.4.114.mbf

# Extract strings
strings MicroBrute_firmware_v1.0.4.114.mbf | head -50

# Check for known headers
hexdump -C MicroBrute_firmware_v1.0.4.114.mbf | head -30

# MIDI 7-bit encoding test: 144KB × 7/8 = 126KB (close to 128KB flash)
# This suggests the file IS the firmware, 7-bit encoded for MIDI transport
```

### Approach 2: Capture SysEx During Update

```bash
# On macOS, use SysEx Librarian or amidi

# Install amidi (part of alsa-utils on Linux, use SysEx Librarian on Mac)
# 1. Connect MicroBrute via USB
# 2. Start SysEx capture
# 3. Trigger firmware update from MIDI Control Center
# 4. Capture all SysEx messages
# 5. Analyze captured data for firmware binary
```

### Approach 3: PicoEMP Electromagnetic Fault Injection

Based on Aaron Christophel's successful EMFI on LPC2388 (same family).

**Build PicoEMP:**
```bash
git clone https://github.com/newaetech/chipshouter-picoemp
# Follow build instructions — requires Pico + few passive components
# Total cost: ~$50
```

**Procedure:**
1. Position PicoEMP coil near LPC2361 VDD pins
2. Enter ISP mode (P2.10 LOW during reset)
3. Send ISP "Read Memory" command via UART
4. Simultaneously trigger PicoEMP pulse during CRP check
5. If glitch timing is correct, CRP check fails to match → defaults to unlocked
6. Window: ~100-110ns during bootloader CRP word read
7. May require hundreds/thousands of attempts (automated with Python script)

**Reference videos:**
- https://www.youtube.com/watch?v=q9o9sKY2hk8 (POC)
- https://www.youtube.com/watch?v=tcqLgjmzUzM (Success)
- https://www.youtube.com/watch?v=YNpJ3c1GJoc (Gerlinsky RECON 2017)

---

## Phase 4: Ghidra Analysis (If Firmware Obtained)

### Setup

```bash
# Launch Ghidra
ghidra

# Create new project: MACROBRUTE_FW

# Import binary:
# Language: ARM:LE:32:v4t (ARM7TDMI)
# Compiler: default
# Base address: 0x00000000
```

### Install SVD Loader for Peripheral Labels

```bash
# Clone SVD loader
git clone https://github.com/leveldown-security/SVD-Loader-Ghidra

# Or the newer version
git clone https://github.com/antoniovazquezblanco/GhidraSVD

# Install: Copy to Ghidra extensions directory
# Load LPC23xx SVD from CMSIS-SVD database
```

### Key Analysis Targets

| Function | How to Find |
|----------|-------------|
| Vector table | Address 0x0000_0000 — first 32 words |
| CRP word | Address 0x0000_01FC — one of the magic values |
| MIDI parser | Search for 0xF0 (SysEx start byte) |
| DAC write | Search for I2C transactions to address 0x60 (MCP4728) |
| Keyboard scan | Search for GPIO reads on keyboard matrix pins |
| Sequencer | Search for arrays of note data structures |
| UART handler | Search for UART0/UART1 register addresses |

### LPC2361 Memory Map (for Ghidra)

```
  0x0000_0000 — 0x0001_FFFF : Flash (128KB)
  0x4000_0000 — 0x4000_87FF : SRAM (34KB)
  0xE000_0000 — 0xE01F_FFFF : Peripheral registers
  0xFFFF_F000 — 0xFFFF_FFFF : Boot ROM
```

### Reference: KeyStep RE Walkthrough
Daniel Gruss documented Arturia KeyStep firmware analysis with Ghidra:
https://dsgruss.github.io/notes/2020/10/02/keystep1.html

---

## Phase 5: Live UART Communication (Experimental)

No one has publicly documented this. Worth attempting.

### Procedure

1. Connect PL2303HX to LPC2361 UART0 (while synth is running normally)
2. Do NOT pull P2.10 LOW (normal boot, not ISP)
3. Open serial monitor at various baud rates:

```bash
# Try common baud rates
for baud in 9600 19200 38400 57600 115200; do
  echo "Trying $baud..."
  screen /dev/tty.usbserial-XXXX $baud
  # Wait 5 seconds, check for output
done
```

4. Play notes, trigger sequencer, send MIDI — watch for debug output
5. If no output, the firmware may not initialize UART0 (likely uses USB only)

### Alternative: Pico as UART Sniffer

```python
# Use Pico to sniff UART traffic between LPC2361 and other ICs
# Connect Pico GP0 to LPC2361 TX (listen only)
from machine import UART
uart = UART(0, baudrate=115200, rx=Pin(1))
while True:
    if uart.any():
        print(uart.read(), end='')
```
