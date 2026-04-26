"""EFFIGY ↔ MACROBRUTE I²C peer-pair bridge (Pico controller side).

Implements the register-file protocol defined in docs/MACROBRUTE_EFFIGY_BRIDGE.md.
EFFIGY is the I²C target at address 0x42; this module reads/writes its register
map and drains its event queue when INT fires.

This is a SKELETON. Network framing, error handling, and pair lifecycle are in
place; DSP-side parameter application happens in caller code (menu.py adapters
write to the appropriate registers).
"""

from machine import I2C, Pin
from micropython import const
import time

import config

# ---------------------------------------------------------------------------
# Register addresses — must match docs/MACROBRUTE_EFFIGY_BRIDGE.md §4 exactly.
# Same numeric values as src/macrobrute_bridge.h on the EFFIGY side.
# ---------------------------------------------------------------------------

# Device / pair management
REG_DEVICE_ID        = const(0x00)  # 8 bytes "EFFIGY1\0"
REG_FW_VERSION_MAJOR = const(0x01)
REG_FW_VERSION_MINOR = const(0x02)
REG_CAPABILITIES     = const(0x03)  # 4 bytes bitfield
REG_HEARTBEAT        = const(0x0F)  # ticks every 100 ms

# Parameter control (controller writes)
REG_MASS              = const(0x10)
REG_ENTROPY           = const(0x11)
REG_POSITION          = const(0x12)
REG_TEXTURE           = const(0x13)
REG_MIX               = const(0x14)
REG_FOLD              = const(0x15)
REG_FILTER            = const(0x16)
REG_REVERB            = const(0x17)
REG_CRUSH             = const(0x18)
REG_DESTRUCTION_MACRO = const(0x19)
REG_ENGINE_INDEX      = const(0x1A)
REG_HARMONIZER_INT    = const(0x1B)
REG_MICRO_LFO_RATE    = const(0x1C)
REG_ENV_SHAPE         = const(0x1D)
REG_TRIG_VOICE_1      = const(0x30)
REG_FREEZE            = const(0x31)
REG_PANEL_OVERRIDE    = const(0x32)

# State telemetry (controller reads)
REG_LEVEL_L           = const(0x40)
REG_LEVEL_R           = const(0x41)
REG_CLIP_FLAGS        = const(0x42)
REG_ENGINE_NAME       = const(0x43)  # 12 bytes
REG_PRESET_SLOT       = const(0x44)
REG_CPU_LOAD          = const(0x45)
REG_GRAIN_BUFFER_FILL = const(0x46)
REG_FREEZE_STATE      = const(0x47)
REG_ENV_STAGE         = const(0x48)
REG_CV_OUT_1_VALUE    = const(0x49)  # 2 bytes signed
REG_CV_OUT_2_VALUE    = const(0x4A)

# Event queue — INT-driven async
REG_EVENT_COUNT = const(0x60)
REG_EVENT_POP   = const(0x61)  # 4 bytes per pop
REG_EVENT_CLEAR = const(0x62)

# Routing / coordination
REG_PAIR_ACTIVE     = const(0x80)
REG_CLOCK_MASTER    = const(0x81)
REG_MENU_OWNER      = const(0x82)
REG_FOCUS_OWNER     = const(0x83)
REG_CLOCK_TICK      = const(0x90)
REG_CLOCK_BPM       = const(0x91)  # 2 bytes, BPM × 10
REG_TRANSPORT_STATE = const(0x92)
REG_PRESET_RECALL   = const(0x93)

# Cross-modulation
REG_SRC_COUNT = const(0xA0)
REG_SRC_NAME  = const(0xA1)  # 8 bytes per source name, indices 0–14

# Diagnostics
REG_ERROR_STATUS = const(0xF0)
REG_RESET_BRIDGE = const(0xFF)

# Event types (first byte returned by EVENT_POP)
EVENT_ENCODER = const(0x01)
EVENT_BUTTON  = const(0x02)
EVENT_PRESET  = const(0x03)
EVENT_ENGINE  = const(0x04)
EVENT_CLIP    = const(0x05)
EVENT_PANEL   = const(0x06)

# Error codes
ERR_OK                 = const(0x00)
ERR_INVALID_REGISTER   = const(0x01)
ERR_WRITE_TO_READONLY  = const(0x02)
ERR_VALUE_OUT_OF_RANGE = const(0x03)
ERR_PANEL_LOCKED       = const(0x04)
ERR_PROTOCOL_ERROR     = const(0x05)

# Pair-loss timeout: number of consecutive identical heartbeat reads before
# we declare the link dead and revert to solo mode.
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
