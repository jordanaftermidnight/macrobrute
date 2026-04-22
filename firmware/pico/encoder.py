"""MACROBRUTE Pico WH — Rotary encoder + button driver (interrupt-driven)."""

from machine import Pin
import time
import config


class Encoder:
    """HW040 rotary encoder with push button. Interrupt-driven, hardware debounced."""

    def __init__(self, on_rotate=None, on_press=None, on_long_press=None):
        self._on_rotate = on_rotate
        self._on_press = on_press
        self._on_long_press = on_long_press

        self._clk = Pin(config.ENC_CLK, Pin.IN, Pin.PULL_UP)
        self._dt = Pin(config.ENC_DT, Pin.IN, Pin.PULL_UP)
        self._sw = Pin(config.ENC_SW, Pin.IN, Pin.PULL_UP)

        self._last_clk = self._clk.value()
        self._position = 0
        self._delta = 0

        # Button state
        self._btn_down_time = 0
        self._btn_handled = False
        self._btn_state = 1  # Active low
        self._btn_event = None  # "press" or "long_press", set in ISR

        # Set up interrupts
        self._clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._rotation_irq)
        self._sw.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_irq)

    def _rotation_irq(self, pin):
        clk = self._clk.value()
        if clk != self._last_clk:
            if self._dt.value() != clk:
                self._delta += 1
            else:
                self._delta -= 1
            self._last_clk = clk

    def _button_irq(self, pin):
        """Button ISR — classify event, defer callback to update()."""
        self._btn_state = self._sw.value()
        now = time.ticks_ms()
        if self._btn_state == 0:  # Pressed (active low)
            self._btn_down_time = now
            self._btn_handled = False
        else:  # Released
            if not self._btn_handled and self._btn_down_time > 0:
                duration = time.ticks_diff(now, self._btn_down_time)
                if duration > config.TAP_DEBOUNCE_MS:
                    if duration >= config.LONG_PRESS_MS:
                        self._btn_event = "long_press"
                    else:
                        self._btn_event = "press"
                    self._btn_handled = True

    def update(self):
        """Poll for accumulated rotation and deferred button events. Call from main loop."""
        d = self._delta
        if d != 0:
            self._delta = 0
            self._position += d
            if self._on_rotate:
                self._on_rotate(d)
            return d

        # Process deferred button events from ISR
        event = self._btn_event
        if event:
            self._btn_event = None
            if event == "long_press" and self._on_long_press:
                self._on_long_press()
            elif event == "press" and self._on_press:
                self._on_press()

        # Check for long press while still held (timeout detection)
        if self._btn_state == 0 and not self._btn_handled:
            held = time.ticks_diff(time.ticks_ms(), self._btn_down_time)
            if held >= config.LONG_PRESS_MS:
                if self._on_long_press:
                    self._on_long_press()
                self._btn_handled = True
        return 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def pressed(self):
        return self._btn_state == 0
