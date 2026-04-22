#!/usr/bin/env bash
# MACROBRUTE — Flash all firmware modules to Pico WH via mpremote
# Usage: ./tools/flash_pico.sh [port]
#
# Prerequisites:
#   pip3 install mpremote
#   MicroPython already flashed to Pico WH (hold BOOTSEL, drag .uf2)
#
# If port is omitted, mpremote auto-detects.
# Example: ./tools/flash_pico.sh /dev/tty.usbmodem1101

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FW_DIR="$SCRIPT_DIR/../firmware/pico"
PORT="${1:-}"

echo "MACROBRUTE — Pico Firmware Flash"
echo "================================"

if ! command -v mpremote &>/dev/null; then
    echo "ERROR: mpremote not found"
    echo "  pip3 install mpremote"
    exit 1
fi

CONNECT=""
if [ -n "$PORT" ]; then
    CONNECT="connect $PORT"
    echo "Port: $PORT"
else
    echo "Port: auto-detect"
fi

FILES=(config.py display.py encoder.py clock.py menu.py midi.py leds.py main.py)

echo ""
for f in "${FILES[@]}"; do
    printf "  %-14s → :%-14s " "$f" "$f"
    mpremote $CONNECT cp "$FW_DIR/$f" ":$f" 2>/dev/null && echo "OK" || echo "FAIL"
done

echo ""
echo "All files copied. Resetting Pico..."
mpremote $CONNECT reset 2>/dev/null || true
echo ""
echo "MACROBRUTE should now boot."
echo "Monitor: mpremote $CONNECT repl"
