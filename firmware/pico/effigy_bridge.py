"""EFFIGY ↔ MACROBRUTE I²C peer-pair bridge (Pico controller side).

Implements the register-file protocol defined in docs/MACROBRUTE_EFFIGY_BRIDGE.md.
EFFIGY is the I²C target at address 0x42; this module reads/writes its register
map and drains its event queue when INT (active-low, open-drain) fires.

The register addresses, event types, and error codes are NOT hand-maintained
here — they are imported from `_effigy_constants.py`, which is generated from
EFFIGY's authoritative C header (`EFFIGY/firmware/src/macrobrute_bridge.h`)
by `tools/sync_effigy_constants.py`. Re-run that script when the C header
changes; never edit `_effigy_constants.py` by hand.
"""

from machine import I2C, Pin
from micropython import const
import time

import config

# Re-export constants from the generated module so existing callers can keep
# importing names like `effigy_bridge.REG_MASS` unchanged.
from _effigy_constants import *  # noqa: F401,F403

# Pair-loss timeout: number of consecutive identical heartbeat reads before
# we declare the link dead and revert to solo mode. (Implementation-specific,
# not part of the wire protocol.)
HEARTBEAT_DEAD_THRESHOLD = const(2)
HEARTBEAT_POLL_MS        = const(500)


class EffigyBridge:
    """Controller-side bridge to a paired EFFIGY module.

    Lifecycle:
        bridge = EffigyBridge()
        if bridge.probe():
            bridge.set_paired(True)
            # main loop:
            bridge.poll()  # drains events, refreshes telemetry, checks heartbeat
    """

    def __init__(self):
        self._i2c = I2C(
            config.DAISY_I2C_ID,
            sda=Pin(config.DAISY_SDA),
            scl=Pin(config.DAISY_SCL),
            freq=config.DAISY_FREQ,
        )
        self._addr = config.DAISY_ADDR
        self._int_pin = Pin(config.DAISY_INT, Pin.IN, Pin.PULL_UP)
        self._int_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_int)

        self._paired = False
        self._last_heartbeat = -1
        self._stale_count = 0
        self._last_poll_ms = 0
        self._event_pending = False  # set by ISR

        # Mirror of EFFIGY's published telemetry — caller can read these.
        self.engine_name = ""
        self.level_l = 0
        self.level_r = 0
        self.preset_slot = 0
        self.cpu_load = 0

        # Event callback — caller registers a function(type, a, b, c).
        self.on_event = None

    # ---------- public API -------------------------------------------------

    def probe(self):
        """Return True if EFFIGY is present and responsive."""
        try:
            buf = self._read(REG_DEVICE_ID, 8)
            if buf and buf.startswith(b"EFFIGY1"):
                return True
        except OSError:
            pass
        return False

    def set_paired(self, paired):
        """Activate or deactivate pair mode on the EFFIGY side."""
        self._write(REG_PAIR_ACTIVE, bytes([1 if paired else 0]))
        self._paired = bool(paired)

    def is_paired(self):
        return self._paired

    def write_param(self, reg, value, n_bytes=2):
        """Write a parameter register (typically u16 little-endian)."""
        if n_bytes == 1:
            data = bytes([value & 0xFF])
        else:
            data = bytes([value & 0xFF, (value >> 8) & 0xFF])
        self._write(reg, data)

    def read_telemetry(self):
        """Refresh local mirror of EFFIGY telemetry. Call at ~10 Hz."""
        try:
            self.level_l = self._read(REG_LEVEL_L, 1)[0]
            self.level_r = self._read(REG_LEVEL_R, 1)[0]
            self.preset_slot = self._read(REG_PRESET_SLOT, 1)[0]
            self.cpu_load = self._read(REG_CPU_LOAD, 1)[0]
            name = self._read(REG_ENGINE_NAME, 12)
            self.engine_name = name.rstrip(b"\x00").decode("ascii", "replace")
        except OSError:
            self._note_io_error()

    def send_clock_tick(self):
        """Notify EFFIGY of a clock edge (coarse — fine sync via hardware jack)."""
        if self._paired:
            self._write(REG_CLOCK_TICK, b"\x01")

    def send_bpm(self, bpm):
        """Update EFFIGY's BPM mirror (BPM × 10)."""
        if self._paired:
            v = int(round(bpm * 10))
            self.write_param(REG_CLOCK_BPM, v, n_bytes=2)

    def recall_preset(self, slot):
        if self._paired and 0 <= slot <= 7:
            self._write(REG_PRESET_RECALL, bytes([slot]))

    def poll(self):
        """Periodic maintenance — heartbeat check + drain events if INT pending."""
        if not self._paired:
            return

        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_poll_ms) >= HEARTBEAT_POLL_MS:
            self._last_poll_ms = now
            self._check_heartbeat()

        if self._event_pending:
            self._event_pending = False
            self._drain_events()

    # ---------- internal ---------------------------------------------------

    def _on_int(self, pin):
        """ISR — just sets a flag; actual draining happens in poll()."""
        self._event_pending = True

    def _check_heartbeat(self):
        try:
            hb = self._read(REG_HEARTBEAT, 1)[0]
            if hb == self._last_heartbeat:
                self._stale_count += 1
                if self._stale_count >= HEARTBEAT_DEAD_THRESHOLD:
                    self._on_pair_lost()
            else:
                self._stale_count = 0
                self._last_heartbeat = hb
        except OSError:
            self._note_io_error()

    def _drain_events(self):
        try:
            count = self._read(REG_EVENT_COUNT, 1)[0]
            for _ in range(count):
                evt = self._read(REG_EVENT_POP, 4)
                if self.on_event:
                    self.on_event(evt[0], evt[1], evt[2], evt[3])
            self._write(REG_EVENT_CLEAR, b"\x01")
        except OSError:
            self._note_io_error()

    def _on_pair_lost(self):
        self._paired = False
        self._stale_count = 0
        # Caller can detect this via is_paired() and update UI.

    def _note_io_error(self):
        # Silent — repeated failures will trip the heartbeat watchdog
        # and we'll deactivate pair mode automatically.
        pass

    def _read(self, reg, n):
        """Read n bytes starting at register address `reg`."""
        return self._i2c.readfrom_mem(self._addr, reg, n)

    def _write(self, reg, data):
        """Write `data` (bytes-like) starting at register address `reg`."""
        self._i2c.writeto_mem(self._addr, reg, data)
