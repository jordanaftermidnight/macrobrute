"""
MACROBRUTE — Hardware Test Script
Run: mpremote run test_hw.py

Tests each peripheral independently via serial output.
No OLED dependency — diagnose wiring issues before full firmware.

Breadboard Wiring Quick Reference:
  OLED SH1106 (SPI0):
    VCC  → 3V3 (pin 36)        GND → GND
    SCK  → GP18 (pin 24)       MOSI/SDA → GP19 (pin 25)
    CS   → GP17 (pin 22)       DC  → GP16 (pin 21)
    RST  → GP20 (pin 26)

  Encoder HW040:
    CLK → GP14 (pin 19)        DT  → GP15 (pin 20)
    SW  → GP13 (pin 17)        +   → 3V3    GND → GND

  Tap Tempo Button:
    One leg → GP12 (pin 16)    Other leg → GND

  LEDs (active-low via 2N3904, or direct with resistor):
    GP8  (pin 11) → 220Ω → LED → GND   (Clock)
    GP9  (pin 12) → 220Ω → LED → GND   (Gate)
    GP10 (pin 14) → 220Ω → LED → GND   (Mode)

  MIDI UART1 (31250 baud):
    TX → GP4 (pin 6)           RX → GP5 (pin 7)

  Clock I/O:
    OUT → GP22 (pin 29)        IN → GP21 (pin 27)
"""

import time
from machine import Pin, SPI, UART, PWM


def wait_press(pin, name, timeout_s=10):
    """Wait for a button/switch press (active low). Returns True if pressed."""
    print(f"  Press {name}...")
    t0 = time.ticks_ms()
    while pin.value() == 1:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
            print(f"  SKIP — no press in {timeout_s}s")
            return False
        time.sleep_ms(10)
    # Wait for release
    while pin.value() == 0:
        time.sleep_ms(10)
    return True


# ---- Individual Tests ----

def test_leds():
    """Cycle through 3 LEDs."""
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
    """Test tap tempo button on GP12."""
    print("\n[2/6] TAP BUTTON TEST")
    btn = Pin(12, Pin.IN, Pin.PULL_UP)
    print(f"  GP12 reads {btn.value()} (expect 1 = released)")
    if wait_press(btn, "tap button"):
        print(f"  OK — button works")


def test_encoder():
    """Test encoder rotation and push button."""
    print("\n[3/6] ENCODER TEST")
    clk = Pin(14, Pin.IN, Pin.PULL_UP)
    dt = Pin(15, Pin.IN, Pin.PULL_UP)
    sw = Pin(13, Pin.IN, Pin.PULL_UP)
    print(f"  CLK={clk.value()} DT={dt.value()} SW={sw.value()} (expect all 1)")

    # Rotation test
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

    # Button test
    if wait_press(sw, "encoder button"):
        print("  OK — encoder rotation + button work")


def test_oled():
    """Initialize SH1106 OLED and display test pattern."""
    print("\n[4/6] OLED TEST")
    try:
        spi = SPI(0, baudrate=4_000_000, polarity=0, phase=0,
                  sck=Pin(18), mosi=Pin(19))
        dc = Pin(16, Pin.OUT)
        cs = Pin(17, Pin.OUT, value=1)
        rst = Pin(20, Pin.OUT)

        # Hardware reset
        rst.value(0)
        time.sleep_ms(10)
        rst.value(1)
        time.sleep_ms(10)

        # Send init sequence
        def cmd(c):
            dc.value(0)
            cs.value(0)
            spi.write(bytearray([c]))
            cs.value(1)

        for c in [0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
                  0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
                  0x81, 0xCF, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF]:
            cmd(c)

        # Draw test screen
        import framebuf
        buf = bytearray(128 * 8)
        fb = framebuf.FrameBuffer(buf, 128, 64, framebuf.MONO_VLSB)
        fb.fill(0)
        fb.text("MACROBRUTE", 24, 8)
        fb.text("HW TEST", 36, 24)
        fb.hline(0, 40, 128, 1)
        fb.text("OLED OK", 36, 48)

        # Push to display (SH1106 page-by-page)
        for page in range(8):
            cmd(0xB0 + page)
            cmd(0x02)   # SH1106 column offset
            cmd(0x10)
            dc.value(1)
            cs.value(0)
            spi.write(buf[page * 128:(page + 1) * 128])
            cs.value(1)

        print("  Display should show: MACROBRUTE / HW TEST / OLED OK")
        print("  OK — SPI OLED initialized")

    except Exception as e:
        print(f"  FAIL — {e}")
        print("  Check wiring: VCC→3V3, GND, SCK→GP18, MOSI→GP19,")
        print("                CS→GP17, DC→GP16, RST→GP20")


def test_midi():
    """Test MIDI UART1 output. Optionally test loopback (jumper GP4→GP5)."""
    print("\n[5/6] MIDI UART TEST")
    uart = UART(1, baudrate=31250, tx=Pin(4), rx=Pin(5))

    # Send test bytes
    test_data = bytearray([0xF8, 0xF8, 0xF8])  # 3 MIDI clock ticks
    uart.write(test_data)
    print("  Sent 3× MIDI Clock (0xF8) on GP4 TX")

    time.sleep_ms(50)
    if uart.any():
        data = uart.read()
        print(f"  Loopback received: {[hex(b) for b in data]}")
        if data == test_data:
            print("  OK — UART loopback perfect (remove jumper for real MIDI)")
        else:
            print("  WARN — loopback data mismatch")
    else:
        print("  No loopback (normal if GP4/GP5 not jumpered)")
        print("  Verify TX with scope/logic analyzer on GP4")
        print("  For loopback test: jumper GP4 → GP5")


def test_clock_io():
    """Test clock output (GP22) and input (GP21) pins."""
    print("\n[6/6] CLOCK I/O TEST")
    clk_out = Pin(22, Pin.OUT, value=0)
    clk_in = Pin(21, Pin.IN, Pin.PULL_DOWN)

    # Generate 5 pulses at ~120 BPM (500ms period)
    print("  Sending 5 pulses on GP22...")
    for i in range(5):
        clk_out.value(1)
        time.sleep_ms(10)
        clk_out.value(0)
        time.sleep_ms(490)

    print(f"  GP21 (Clock In) reads: {clk_in.value()} (expect 0 = idle)")
    print("  Verify clock LED or scope on GP22")
    print("  For input test: jumper GP22 → GP21")

    # Quick loopback if jumpered
    clk_out.value(1)
    time.sleep_ms(1)
    val = clk_in.value()
    clk_out.value(0)
    if val == 1:
        print("  Loopback detected — GP21 follows GP22")
        print("  OK — clock I/O works")


# ---- Main ----

def main():
    print()
    print("=" * 44)
    print("  MACROBRUTE v0.1.0 — Hardware Test")
    print("=" * 44)

    print("\nTest order: LEDs → Button → Encoder → OLED → MIDI → Clock")
    print("Each test is independent. Failures don't block later tests.")
    print("Timeouts auto-skip after 8-10s if no input detected.\n")

    test_leds()
    test_button()
    test_encoder()
    test_oled()
    test_midi()
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
