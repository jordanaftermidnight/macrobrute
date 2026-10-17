"""
MACROBRUTE — Hardware Test Script
Run: mpremote run test_hw.py

Tests each peripheral independently via serial output.
Only the OLED test needs other files (display.py, config.py) on the Pico;
the rest diagnose wiring before the full firmware is copied.

Breadboard Wiring Quick Reference:
  Main OLED 1.3" 7-pin SPI (chip SSD1306 or SH1106, UNVERIFIED; pin order UNVERIFIED):
    VCC  → 3V3 (pin 36)        GND → GND
    D0   → GP2 (pin 4, SCK)    D1  → GP3 (pin 5, MOSI)
    DC   → GP4 (pin 6)         RES → GP5 (pin 7)        CS → GND (strapped, BT-14)
  The OLED test drives the module through display.OLED_SPI.

  Encoder HW040:
    CLK → GP14 (pin 19)        DT  → GP15 (pin 20)
    SW  → GP13 (pin 17)        +   → 3V3    GND → GND

  Tap Tempo Button:
    One leg → GP12 (pin 16)    Other leg → GND

  LEDs (active-low via 2N3904, or direct with resistor):
    GP8  (pin 11) → 220Ω → LED → GND   (Clock)
    GP9  (pin 12) → 220Ω → LED → GND   (Gate)
    GP10 (pin 14) → 220Ω → LED → GND   (Mode)

  LPC2361 Bridge (UART0, 115200 baud):
    TX → GP0 (pin 1)           RX → GP1 (pin 2)

  Clock I/O:
    OUT → GP22 (pin 29)        IN → GP21 (pin 27)
"""

import time
from machine import Pin, UART, PWM


def wait_press(pin, name, timeout_s=10):
    print(f"  Press {name}...")
    t0 = time.ticks_ms()
    while pin.value() == 1:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
            print(f"  SKIP — no press in {timeout_s}s")
            return False
        time.sleep_ms(10)
    while pin.value() == 0:
        time.sleep_ms(10)
    return True


def test_leds():
    print("\n[1/6] LED TEST")
    pins = [("CLOCK GP8", 8), ("GATE GP9", 9), ("MODE GP10", 10)]
    for name, num in pins:
        p = PWM(Pin(num))
        p.freq(1000)
        p.duty_u16(65535)
        print(f"  {name} ON")
        time.sleep(0.7)
        p.duty_u16(0)
        p.deinit()
    print("  OK — all LEDs cycled (verify visually)")


def test_button():
    print("\n[2/6] TAP BUTTON TEST")
    btn = Pin(12, Pin.IN, Pin.PULL_UP)
    print(f"  GP12 reads {btn.value()} (expect 1 = released)")
    if wait_press(btn, "tap button"):
        print(f"  OK — button works")


def test_encoder():
    print("\n[3/6] ENCODER TEST")
    clk = Pin(14, Pin.IN, Pin.PULL_UP)
    dt = Pin(15, Pin.IN, Pin.PULL_UP)
    sw = Pin(13, Pin.IN, Pin.PULL_UP)
    print(f"  CLK={clk.value()} DT={dt.value()} SW={sw.value()} (expect all 1)")

    print("  Rotate encoder at least 3 clicks...")
    last_clk = clk.value()
    pos = 0
    t0 = time.ticks_ms()
    while abs(pos) < 3:
        if time.ticks_diff(time.ticks_ms(), t0) > 8000:
            print(f"  SKIP — only {abs(pos)} clicks detected in 8s")
            break
        c = clk.value()
        if c != last_clk:
            if dt.value() != c:
                pos += 1
            else:
                pos -= 1
            print(f"    pos={pos}")
            last_clk = c
        time.sleep_ms(1)

    if wait_press(sw, "encoder button"):
        print("  OK — encoder rotation + button work")


def test_oled():
    print("\n[4/6] OLED TEST (SPI)")
    print("  Uses display.py + config.py from the Pico filesystem (copy them first).")
    print("  Wiring: GP2 SCK, GP3 MOSI, GP4 DC, GP5 RES, module CS strapped to GND.")
    try:
        import config
        from display import OLED_SPI

        oled = OLED_SPI()
        oled.clear()
        oled.text("MACROBRUTE", 24, 8)
        oled.text("HW TEST", 36, 24)
        oled.hline(0, 40, 128, 1)
        oled.text("SPI " + config.OLED_CHIP, 24, 48)
        oled.show()

        print(f"  Sent init + frame for OLED_CHIP={config.OLED_CHIP}, COL_OFFSET={config.OLED_COL_OFFSET}")
        print("  Display should show: MACROBRUTE / HW TEST / SPI <chip>")
        print("  SPI is write-only, so only your eyes can confirm the OLED works.")
        print("  Blank screen: check pin order (UNVERIFIED), RES, DC, then CS-to-GND (BT-14).")
        print("  Shifted 2 columns or garbage edge: try OLED_CHIP=\"SH1106\", OLED_COL_OFFSET=2.")

    except Exception as e:
        print(f"  FAIL — {e}")


def test_lpc_bridge():
    print("\n[5/6] LPC BRIDGE UART TEST")
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

    test_msg = bytearray([0xAA, 0x02, 0x00, 0x00])
    uart.write(test_msg)
    print("  Sent clock command on GP0 TX (UART0 @ 115200)")

    time.sleep_ms(50)
    if uart.any():
        data = uart.read()
        print(f"  Loopback received: {[hex(b) for b in data]}")
        print("  OK — UART loopback (remove jumper for LPC connection)")
    else:
        print("  No loopback (normal if GP0/GP1 not jumpered)")
        print("  Verify TX with scope/logic analyzer on GP0")
        print("  For loopback test: jumper GP0 → GP1")


def test_clock_io():
    print("\n[6/6] CLOCK I/O TEST")
    clk_out = Pin(22, Pin.OUT, value=0)
    clk_in = Pin(21, Pin.IN, Pin.PULL_DOWN)

    print("  Sending 5 pulses on GP22...")
    for i in range(5):
        clk_out.value(1)
        time.sleep_ms(10)
        clk_out.value(0)
        time.sleep_ms(490)

    print(f"  GP21 (Clock In) reads: {clk_in.value()} (expect 0 = idle)")
    print("  Verify clock LED or scope on GP22")
    print("  For input test: jumper GP22 → GP21")

    clk_out.value(1)
    time.sleep_ms(1)
    val = clk_in.value()
    clk_out.value(0)
    if val == 1:
        print("  Loopback detected — GP21 follows GP22")
        print("  OK — clock I/O works")


def main():
    print()
    print("=" * 44)
    print("  MACROBRUTE v0.1.0 — Hardware Test")
    print("=" * 44)

    print("\nTest order: LEDs → Button → Encoder → OLED → UART → Clock")
    print("Each test is independent. Failures don't block later tests.")
    print("Timeouts auto-skip after 8-10s if no input detected.\n")

    test_leds()
    test_button()
    test_encoder()
    test_oled()
    test_lpc_bridge()
    test_clock_io()

    print()
    print("=" * 44)
    print("  All tests complete!")
    print()
    print("  Next steps:")
    print("  1. Fix any failed tests (check wiring)")
    print("  2. Copy firmware: ./tools/flash_pico.sh")
    print("  3. Reset Pico — MACROBRUTE should boot")
    print("=" * 44)


main()
