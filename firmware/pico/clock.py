"""MACROBRUTE Pico WH — Clock generator, tap tempo, and external clock detection."""

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
        self._ext_pending_period = 0  # Set in ISR, processed in update()
        self._ext_tick_pending = False  # Set in ISR, fires tick in update()

        # Tap tempo
        self._tap_times = []

        # Gate output timing
        self._gate_off_time = 0

        # Internal clock deferred tick
        self._tick_pending = False  # Set in timer ISR, fires tick in update()

        # LED_CLOCK (GP8) is owned by leds.LEDManager — the main loop's
        # on_tick callback pulses it. Do not drive it from here.

    # --- BPM / Tempo ---
    # `bpm` returns the *displayed* value (external if synced, internal otherwise).
    # `internal_bpm` always targets the internal clock rate — adjust this from UI.

    @property
    def bpm(self):
        return self._ext_bpm if self._ext_sync else self._bpm

    @bpm.setter
    def bpm(self, val):
        # Setting bpm always writes internal — keeps UI rotate consistent even
        # when ext-sync is active (change takes effect when ext-sync is disabled).
        self.internal_bpm = val

    @property
    def internal_bpm(self):
        return self._bpm

    @internal_bpm.setter
    def internal_bpm(self, val):
        self._bpm = max(config.MIN_BPM, min(config.MAX_BPM, val))
        if self._running and not self._ext_sync:
            self._restart_timer()

    @property
    def period_ms(self):
        active_bpm = self.bpm if self.bpm > 0 else self._bpm
        return int(60_000 / active_bpm)

    @property
    def running(self):
        return self._running

    @property
    def ext_sync(self):
        return self._ext_sync

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
        """Timer ISR — set flag only, no heavy work."""
        if not self._running or self._ext_sync:
            return
        self._tick_pending = True

    def _fire_tick(self):
        self._tick_count += 1

        # Pulse clock output (LED is handled by the on_tick callback via LEDManager)
        self._clock_out.value(1)
        self._gate_off_time = time.ticks_add(time.ticks_ms(), config.CLOCK_GATE_MS)

        if self._on_tick:
            self._on_tick(self._tick_count)

    def update(self):
        """Call from main loop to process deferred ISR work."""
        # Fire deferred internal clock tick
        if self._tick_pending:
            self._tick_pending = False
            self._fire_tick()

        # Fire deferred external clock tick
        if self._ext_tick_pending:
            self._ext_tick_pending = False
            self._fire_tick()

        # Clear stale external clock data after 2s of silence
        if self._ext_sync and self._ext_periods and self._ext_last_edge > 0:
            if time.ticks_diff(time.ticks_us(), self._ext_last_edge) >= 2_000_000:
                self._ext_periods.clear()
                self._ext_bpm = 0

        # Process deferred external clock period measurement
        period = self._ext_pending_period
        if period > 0:
            self._ext_pending_period = 0
            self._ext_periods.append(period)
            if len(self._ext_periods) > config.TAP_BUFFER_SIZE:
                self._ext_periods.pop(0)
            sorted_p = sorted(self._ext_periods)
            self._ext_bpm = round(60_000_000 / sorted_p[len(sorted_p) // 2])

        # Handle gate-off timing
        now = time.ticks_ms()
        if self._gate_off_time > 0 and time.ticks_diff(now, self._gate_off_time) >= 0:
            self._clock_out.value(0)
            self._gate_off_time = 0

    # --- External clock detection ---

    def _ext_clock_irq(self, pin):
        """External clock ISR — minimal work, defer processing to update()."""
        now = time.ticks_us()
        if self._ext_last_edge > 0:
            period_us = time.ticks_diff(now, self._ext_last_edge)
            if 10_000 < period_us < 6_000_000:  # 10ms (~6000 BPM) to 6s (~10 BPM)
                self._ext_pending_period = period_us
                if self._ext_sync and self._running:
                    self._ext_tick_pending = True
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
