#!/bin/bash
# Serial monitor for debug output
# Usage: ./monitor.sh [/dev/tty.usbserial-XXXX] [115200]

PORT=${1:-$(ls /dev/tty.usbserial* 2>/dev/null | head -1)}
BAUD=${2:-"115200"}

if [ -z "$PORT" ]; then
    echo "No serial port found"
    echo "Available:"
    ls /dev/tty.usbserial* /dev/tty.usbmodem* 2>/dev/null || echo "  (none)"
    exit 1
fi

echo "MACROBRUTE Debug Monitor"
echo "Port: $PORT @ $BAUD baud"
echo "Press Ctrl+A then K to exit (screen)"
echo "=========================="

screen "$PORT" "$BAUD"
