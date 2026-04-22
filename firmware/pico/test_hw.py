"""
MACROBRUTE — Hardware Test Script
Run: mpremote run test_hw.py

Tests each peripheral independently via serial output.
No OLED dependency — diagnose wiring issues before full firmware.

Breadboard Wiring Quick Reference:
  OLED SH1106 1.3" (I2C0) — primary. 0.96" SSD1306 works with same pins.
    VCC  → 3V3 (pin 36)        GND → GND
    SDA  → GP4 (pin 6)         SCL → GP5 (pin 7)

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
from machine import Pin, I2C, UART, PWM


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
    print("\n[4/6] OLED TEST (I2C)")
    try:
        i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
        devices = i2c.scan()
        print(f"  I2C devices found: {[hex(d) for d in devices]}")
        if 0x3C not in devices and 0x3D not in devices:
            print("  WARN — no OLED at 0x3C or 0x3D")
            print("  Check wiring: VCC→3V3, GND, SDA→GP4, SCL→GP5")
            return

        addr = 0x3C if 0x3C in devices else 0x3D

        def cmd(c):
            i2c.writeto(addr, bytearray([0x00, c]))

        def data(buf):
            i2c.writeto(addr, b'\x40' + buf)

        # SH1106-tuned init (also works on SSD1306 for this test draw)
        for c in [0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
                  0xAD, 0x8B, 0xA1, 0xC8, 0xDA, 0x12,
                  0x81, 0x80, 0xD9, 0x22, 0xDB, 0x35,
                  0xA4, 0xA6, 0xAF]:
            cmd(c)

        import framebuf
        buf = bytearray(128 * 8)
        fb = framebuf.FrameBuffer(buf, 128, 64, framebuf.MONO_VLSB)
        fb.fill(0)
        fb.text("MACROBRUTE", 24, 8)
        fb.text("HW TEST", 36, 24)
        fb.hline(0, 40, 128, 1)
        fb.text("I2C OK", 36, 48)

        # SH1106 uses 2-col offset. Set to 0 if testing SSD1306.
        col_offset = 2
        col_lo = col_offset & 0x0F
        col_hi = 0x10 | ((col_offset >> 4) & 0x0F)
        for page in range(8):
            cmd(0xB0 + page)
            cmd(col_lo)
            cmd(col_hi)
            data(buf[page * 128:(page + 1) * 128])

        print("  Display should show: MACROBRUTE / HW TEST / I2C OK")
        print("  OK — I2C OLED initialized")

    except Exception as e:
        print(f"  FAIL — {e}")
        print("  Check wiring: VCC→3V3, GND, SDA→GP4, SCL→GP5")


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
