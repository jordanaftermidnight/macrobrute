"""Programmable aux outputs — 4 panel jacks, firmware-routable.

Each channel can be independently configured as one of:

    OFF        — output low, no activity
    TAP_DIV    — gate at master tempo divided by N
    EUCLID     — Euclidean(steps, pulses) gate generator
    RANDOM     — probabilistic gate per master tick
    PASSTHRU   — mirror another signal (clock_in, MIDI gate, etc.)
    PWM_CV     — PWM-filtered CV (requires external RC on jack)

Modes are toggled via menu; per-channel state is kept here.
"""

from machine import Pin, PWM
import random

import config


class AuxChannel:
    def __init__(self, gp_num):
        self._gp = gp_num
        self._mode = config.AUX_MODE_OFF
        self._pin = Pin(gp_num, Pin.OUT, value=0)
        self._pwm = None  # lazily created when entering PWM_CV mode

        # Mode-specific state
        self._tap_div_ratio = 4
        self._tap_div_counter = 0
        self._tap_div_gate_remaining = 0

        self._euclid_steps = 16
        self._euclid_pulses = 4
        self._euclid_index = 0
        self._euclid_pattern = self._compute_euclid(16, 4)

        self._random_probability = 0.25  # 0.0 to 1.0

        self._passthru_source = None  # callable returning 0/1

        self._pwm_value = 0  # 0–65535

    def set_mode(self, mode):
        # Tear down PWM if leaving PWM_CV
        if self._mode == config.AUX_MODE_PWM_CV and mode != config.AUX_MODE_PWM_CV:
            if self._pwm is not None:
                self._pwm.deinit()
                self._pwm = None
                self._pin = Pin(self._gp, Pin.OUT, value=0)

        # Spin up PWM if entering PWM_CV
        if mode == config.AUX_MODE_PWM_CV and self._pwm is None:
            self._pwm = PWM(Pin(self._gp))
            self._pwm.freq(20_000)  # 20 kHz, well above audio for clean RC filter
            self._pwm.duty_u16(self._pwm_value)

        self._mode = mode
        if mode == config.AUX_MODE_OFF:
            self._pin.value(0)

    def get_mode(self):
        return self._mode

    # --- mode-specific configuration ---

    def configure_tap_div(self, ratio):
        self._tap_div_ratio = max(1, int(ratio))
        self._tap_div_counter = 0

    def configure_euclid(self, steps, pulses):
        self._euclid_steps = max(1, min(64, int(steps)))
        self._euclid_pulses = max(0, min(self._euclid_steps, int(pulses)))
        self._euclid_pattern = self._compute_euclid(self._euclid_steps, self._euclid_pulses)
        self._euclid_index = 0

    def configure_random(self, probability):
        self._random_probability = max(0.0, min(1.0, probability))

    def configure_passthru(self, source_callable):
        self._passthru_source = source_callable

    def set_pwm_value(self, value_u16):
        """Set PWM duty cycle (0–65535) — only meaningful in PWM_CV mode."""
        self._pwm_value = max(0, min(65535, int(value_u16)))
        if self._mode == config.AUX_MODE_PWM_CV and self._pwm is not None:
            self._pwm.duty_u16(self._pwm_value)

    # --- per-tick driver ---

    def tick(self, gate_width_ticks=1):
        """Called from the master clock tick. Updates gate-mode outputs."""
        if self._mode == config.AUX_MODE_TAP_DIV:
            self._tap_div_counter += 1
            if self._tap_div_counter >= self._tap_div_ratio:
                self._tap_div_counter = 0
                self._pin.value(1)
                self._tap_div_gate_remaining = gate_width_ticks
            elif self._tap_div_gate_remaining > 0:
                self._tap_div_gate_remaining -= 1
                if self._tap_div_gate_remaining == 0:
                    self._pin.value(0)

        elif self._mode == config.AUX_MODE_EUCLID:
            on = self._euclid_pattern[self._euclid_index]
            self._pin.value(1 if on else 0)
            self._euclid_index = (self._euclid_index + 1) % self._euclid_steps

        elif self._mode == config.AUX_MODE_RANDOM:
            self._pin.value(1 if random.random() < self._random_probability else 0)

        elif self._mode == config.AUX_MODE_PASSTHRU:
            if self._passthru_source is not None:
                self._pin.value(1 if self._passthru_source() else 0)

        # OFF and PWM_CV — nothing per-tick (PWM updates via set_pwm_value)

    # --- helpers ---

    @staticmethod
    def _compute_euclid(steps, pulses):
        """Bjorklund's algorithm — distributes `pulses` evenly across `steps`."""
        if pulses == 0:
            return [0] * steps
        if pulses >= steps:
            return [1] * steps
        pattern = []
        bucket = 0
        for _ in range(steps):
            bucket += pulses
            if bucket >= steps:
                bucket -= steps
                pattern.append(1)
            else:
                pattern.append(0)
        return pattern


class AuxOutputs:
    """Container for the 4 aux channels — call tick() on the master clock."""

    def __init__(self):
        self.channels = [AuxChannel(p) for p in config.AUX_OUT_PINS]

    def tick(self, gate_width_ticks=1):
        for ch in self.channels:
            ch.tick(gate_width_ticks)

    def reset(self):
        for ch in self.channels:
            if ch.get_mode() != config.AUX_MODE_PWM_CV:
                ch._pin.value(0)
