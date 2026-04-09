"""MACROBRUTE Pico H — Clock generator, tap tempo, and external clock detection."""

from machine import Pin, Timer
import time
import rp2
import config


class Clock:
    """Master clock with tap tempo, external sync, and clock division."""

    def __init__(self, on_tick=None):
        self._on_tick = on_tick
        self._bpm = config.DEFAULT_BPM
        self._running = False
        self._ext_sync = False
        self._tick_count = 0

        # Internal clock timer
        self._timer = Timer()

        # Clock output pin
        self._clock_out = Pin(config.CLOCK_OUT, Pin.OUT, value=0)

        # Clock input (external sync)
        self._clock_in = Pin(config.CLOCK_IN, Pin.IN, Pin.PULL_DOWN)
        self._clock_in.irq(trigger=Pin.IRQ_RISING, handler=self._ext_clock_irq)

        # External clock timing
        self._ext_last_edge = 0
        self._ext_periods = []  # Rolling median buffer
        self._ext_bpm = 0

        # Tap tempo
        self._tap_times = []

        # Gate output timing
        self._gate_off_time = 0

        # LED pin for clock pulse
        self._led = Pin(config.LED_CLOCK, Pin.OUT, value=0)

    # --- BPM / Tempo ---

    @property
    def bpm(self):
        return self._ext_bpm if self._ext_sync else self._bpm

    @bpm.setter
    def bpm(self, val):
        self._bpm = max(config.MIN_BPM, min(config.MAX_BPM, val))
        if self._running and not self._ext_sync:
            self._restart_timer()

    @property
    def period_ms(self):
        return int(60_000 / self.bpm)

    # --- Start / Stop ---

    def start(self):
        self._running = True
        self._tick_count = 0
        if not self._ext_sync:
            self._restart_timer()

    def stop(self):
        self._running = False
        self._timer.deinit()
        self._clock_out.value(0)
        self._led.value(0)

    def toggle(self):
        if self._running:
            self.stop()
        else:
            self.start()

    # --- Internal clock ---

    def _restart_timer(self):
        self._timer.deinit()
        self._timer.init(
            period=self.period_ms,
            mode=Timer.PERIODIC,
            callback=self._timer_tick,
        )

    def _timer_tick(self, t):
        if not self._running or self._ext_sync:
            return
        self._fire_tick()

    def _fire_tick(self):
        self._tick_count += 1

        # Pulse clock output
        self._clock_out.value(1)
        self._led.value(1)
        self._gate_off_time = time.ticks_add(time.ticks_ms(), config.CLOCK_GATE_MS)

        if self._on_tick:
            self._on_tick(self._tick_count)

    def update(self):
        """Call from main loop to handle gate-off timing."""
        now = time.ticks_ms()
        if self._gate_off_time > 0 and time.ticks_diff(now, self._gate_off_time) >= 0:
            self._clock_out.value(0)
            self._led.value(0)
            self._gate_off_time = 0

    # --- External clock detection ---

    def _ext_clock_irq(self, pin):
        now = time.ticks_us()
        if self._ext_last_edge > 0:
            period_us = time.ticks_diff(now, self._ext_last_edge)
            # Reject obvious outliers
            if 10_000 < period_us < 6_000_000:  # ~10 BPM to ~6000 BPM range
                self._ext_periods.append(period_us)
                if len(self._ext_periods) > config.TAP_BUFFER_SIZE:
                    self._ext_periods.pop(0)
                # Rolling median
                sorted_p = sorted(self._ext_periods)
                median_us = sorted_p[len(sorted_p) // 2]
                self._ext_bpm = round(60_000_000 / median_us)

                if self._ext_sync and self._running:
                    self._fire_tick()

        self._ext_last_edge = now

    def enable_ext_sync(self):
        self._ext_sync = True
        self._ext_periods.clear()
        self._ext_last_edge = 0
        if self._running:
            self._timer.deinit()

    def disable_ext_sync(self):
        self._ext_sync = False
        if self._running:
            self._restart_timer()

    @property
    def ext_detected(self):
        if not self._ext_periods:
            return False
        # Consider external clock lost after 2 seconds of silence
        return time.ticks_diff(time.ticks_us(), self._ext_last_edge) < 2_000_000

    # --- Tap tempo ---

    def tap(self):
        now = time.ticks_ms()

        # Reset if too long since last tap
        if self._tap_times and time.ticks_diff(now, self._tap_times[-1]) > config.TAP_TIMEOUT_MS:
            self._tap_times.clear()

        self._tap_times.append(now)
        if len(self._tap_times) > config.TAP_BUFFER_SIZE:
            self._tap_times.pop(0)

        if len(self._tap_times) >= 2:
            intervals = []
            for i in range(1, len(self._tap_times)):
                intervals.append(time.ticks_diff(self._tap_times[i], self._tap_times[i - 1]))
            avg_ms = sum(intervals) / len(intervals)
            if avg_ms > 0:
                self.bpm = round(60_000 / avg_ms)

    # --- Clock division ---

    def is_div(self, divisor):
        """Check if current tick aligns with division."""
        return self._tick_count % divisor == 0

    @property
    def tick_count(self):
        return self._tick_count
