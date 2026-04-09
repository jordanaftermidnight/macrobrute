"""MACROBRUTE Pico H — LED indicator driver."""

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
    """Manage all three status LEDs."""

    def __init__(self):
        self.clock = LED(config.LED_CLOCK)
        self.gate = LED(config.LED_GATE)
        self.mode = LED(config.LED_MODE)

    def update(self):
        self.clock.update()
        self.gate.update()
        self.mode.update()

    def all_off(self):
        self.clock.off()
        self.gate.off()
        self.mode.off()

    def startup_sequence(self):
        """Brief LED test on boot."""
        for led in (self.clock, self.gate, self.mode):
            led.on()
            time.sleep_ms(100)
        time.sleep_ms(200)
        self.all_off()
