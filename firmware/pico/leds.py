"""MACROBRUTE Pico WH — LED indicator driver."""

from machine import Pin, PWM
import time
import config


class LED:
    """Single LED with on/off, pulse, and breathe modes."""

    def __init__(self, pin_num):
        self._pin = PWM(Pin(pin_num))
        self._pin.freq(1000)
        self._pin.duty_u16(0)
        self._mode = "off"
        self._pulse_off_time = 0

    def on(self, brightness=65535):
        self._mode = "on"
        self._pin.duty_u16(brightness)

    def off(self):
        self._mode = "off"
        self._pin.duty_u16(0)

    def pulse(self, duration_ms=50):
        """Brief flash."""
        self._mode = "pulse"
        self._pin.duty_u16(65535)
        self._pulse_off_time = time.ticks_add(time.ticks_ms(), duration_ms)

    def update(self):
        if self._mode == "pulse" and self._pulse_off_time > 0:
            if time.ticks_diff(time.ticks_ms(), self._pulse_off_time) >= 0:
                self._pin.duty_u16(0)
                self._mode = "off"
                self._pulse_off_time = 0


class LEDManager:
    """Manage RGB LED (common cathode) for status indication.

    Single RGB LED replaces 3 discrete LEDs. Same GPIO pins:
      GP8 = Red (clock), GP9 = Green (gate), GP10 = Blue (mode)
    Colors: red=clock tick, green=gate active, blue=mode indicator.
    Combined states produce mixed colors (yellow=clock+gate, etc).
    """

    def __init__(self):
        self.clock = LED(config.LED_CLOCK)   # Red channel
        self.gate = LED(config.LED_GATE)     # Green channel
        self.mode = LED(config.LED_MODE)     # Blue channel

    def update(self):
        self.clock.update()
        self.gate.update()
        self.mode.update()

    def all_off(self):
        self.clock.off()
        self.gate.off()
        self.mode.off()

    def set_color(self, r=0, g=0, b=0):
        """Set RGB brightness (0-65535 each)."""
        self.clock.on(r)
        self.gate.on(g)
        self.mode.on(b)

    def startup_sequence(self):
        """RGB color cycle on boot."""
        for r, g, b in [(65535, 0, 0), (0, 65535, 0), (0, 0, 65535),
                         (65535, 65535, 65535)]:
            self.set_color(r, g, b)
            time.sleep_ms(150)
        self.all_off()
