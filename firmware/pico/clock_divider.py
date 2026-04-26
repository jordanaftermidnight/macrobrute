"""Firmware clock divider — replaces the CD4024 chip from earlier hardware plans.

Fans out the master clock (driven by clock.Clock.tick()) to 3 GPIO outputs at
configurable division ratios. Default /2, /4, /8 — but any positive integer is
allowed (triplets, dotted, polyrhythm).

Usage:
    div = ClockDivider()
    div.set_ratios((3, 6, 12))   # triplet feel
    # in clock tick callback:
    div.tick()
"""

from machine import Pin

import config


class ClockDivider:
    """Up to 3 GPIO outputs, each toggling every Nth master tick."""

    def __init__(self, pins=None, ratios=None):
        pins = pins if pins is not None else config.CLK_DIV_PINS
        ratios = ratios if ratios is not None else config.CLK_DIV_DEFAULTS

        self._pins = [Pin(p, Pin.OUT, value=0) for p in pins]
        self._ratios = list(ratios)
        self._counters = [0] * len(self._pins)
        self._states = [0] * len(self._pins)
        self._gate_remaining = [0] * len(self._pins)
        self._gate_width_ticks = 1  # toggle high for 1 tick by default

    def set_ratios(self, ratios):
        """Reconfigure division ratios. List length must match pin count."""
        if len(ratios) != len(self._pins):
            raise ValueError("ratios length must match pin count")
        self._ratios = list(ratios)
        self._counters = [0] * len(self._pins)
        self._states = [0] * len(self._pins)
        self._gate_remaining = [0] * len(self._pins)

    def get_ratios(self):
        return tuple(self._ratios)

    def set_gate_width_ticks(self, width):
        """How many master ticks each divided output stays high. Default 1."""
        if width < 1:
            raise ValueError("gate width must be ≥ 1")
        self._gate_width_ticks = int(width)

    def tick(self):
        """Call on every master clock tick. Toggles outputs as appropriate."""
        for i, ratio in enumerate(self._ratios):
            self._counters[i] += 1
            if self._counters[i] >= ratio:
                self._counters[i] = 0
                self._pins[i].value(1)
                self._gate_remaining[i] = self._gate_width_ticks
            elif self._gate_remaining[i] > 0:
                self._gate_remaining[i] -= 1
                if self._gate_remaining[i] == 0:
                    self._pins[i].value(0)

    def reset(self):
        """Force all outputs low and zero counters (e.g. on transport stop)."""
        for i in range(len(self._pins)):
            self._pins[i].value(0)
            self._counters[i] = 0
            self._gate_remaining[i] = 0
