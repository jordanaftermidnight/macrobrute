#!/bin/bash
# Flash MACROBRUTE firmware via ISP
# Usage: ./flash.sh firmware.hex [/dev/tty.usbserial-XXXX]

FIRMWARE=${1:-"build/macrobrute.hex"}
PORT=${2:-$(ls /dev/tty.usbserial* 2>/dev/null | head -1)}

echo "==================================="
echo "  MACROBRUTE ISP Flash Utility"
echo "==================================="
echo "Firmware: $FIRMWARE"
echo "Port: $PORT"
echo ""

if [ ! -f "$FIRMWARE" ]; then
    echo "ERROR: Firmware file not found: $FIRMWARE"
    exit 1
fi

if [ -z "$PORT" ] || [ ! -e "$PORT" ]; then
    echo "ERROR: Serial port not found"
    echo "Available ports:"
    ls /dev/tty.usbserial* /dev/tty.usbmodem* 2>/dev/null || echo "  (none found)"
    exit 1
fi

echo "*** Put MicroBrute in ISP mode: ***"
echo "  1. Power off MicroBrute"
echo "  2. Connect P2.10 to GND (ISP entry)"
echo "  3. Power on MicroBrute"
echo "  4. Press Enter to continue..."
read

echo "Flashing..."
lpc21isp -control -verify "$FIRMWARE" "$PORT" 115200 12000

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "  Flash complete!"
    echo "==================================="
    echo "Remove ISP jumper and reset MicroBrute"
else
    echo ""
    echo "ERROR: Flash failed!"
    echo "Try: lpc21isp -detectonly dummy.hex $PORT 115200 12000"
    exit 1
fi
