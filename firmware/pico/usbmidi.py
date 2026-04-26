"""USB-MIDI — Pico WH enumerates as a USB-MIDI class device over micro-USB.

The Pico's RP2040 has a USB 2.0 PHY; MicroPython exposes it via a TinyUSB-
based `machine.USBDevice` API on recent firmware builds. This module wraps
that API into a simple send/receive interface for the MACROBRUTE menu, clock,
and EFFIGY bridge to use.

NOTE: the underlying TinyUSB MIDI class binding is provided by the MicroPython
build's `usb_midi` (or `usbmidi`) module. If unavailable, this wrapper degrades
to a no-op so the rest of the firmware still boots cleanly.

Reference: https://docs.micropython.org/en/latest/rp2/quickref.html#usb-device
"""

import config

try:
    import usb_midi as _usbmidi
    _AVAILABLE = True
except ImportError:
    try:
        import usbmidi as _usbmidi
        _AVAILABLE = True
    except ImportError:
        _AVAILABLE = False


# Standard MIDI status bytes (channel ORed in low nibble)
NOTE_OFF        = 0x80
NOTE_ON         = 0x90
POLY_AFTERTOUCH = 0xA0
CONTROL_CHANGE  = 0xB0
PROGRAM_CHANGE  = 0xC0
CHANNEL_PRESS   = 0xD0
PITCH_BEND      = 0xE0
SYSTEM          = 0xF0

# System realtime
CLOCK_TICK   = 0xF8
CLOCK_START  = 0xFA
CLOCK_CONT   = 0xFB
CLOCK_STOP   = 0xFC
ACTIVE_SENSE = 0xFE
SYS_RESET    = 0xFF


class USBMidi:
    """Simple wrapper around MicroPython's USB-MIDI class endpoint."""

    def __init__(self, channel=None):
        self.channel = channel if channel is not None else config.USBMIDI_CHANNEL
        self.on_message = None  # callback(status, data1, data2)
        self._available = _AVAILABLE
        if self._available:
            try:
                self._dev = _usbmidi.MIDIDevice()  # exact API may vary
            except Exception:
                self._available = False
                self._dev = None
        else:
            self._dev = None

    def is_available(self):
        return self._available

    # ---------- send ----------

    def send_note_on(self, note, velocity=100):
        self._send(NOTE_ON | (self.channel & 0x0F), note & 0x7F, velocity & 0x7F)

    def send_note_off(self, note, velocity=0):
        self._send(NOTE_OFF | (self.channel & 0x0F), note & 0x7F, velocity & 0x7F)

    def send_cc(self, controller, value):
        self._send(CONTROL_CHANGE | (self.channel & 0x0F), controller & 0x7F, value & 0x7F)

    def send_program_change(self, program):
        self._send(PROGRAM_CHANGE | (self.channel & 0x0F), program & 0x7F, None)

    def send_clock_tick(self):
        self._send(CLOCK_TICK, None, None)

    def send_clock_start(self):
        self._send(CLOCK_START, None, None)

    def send_clock_stop(self):
        self._send(CLOCK_STOP, None, None)

    # ---------- receive ----------

    def poll(self):
        """Drain inbound MIDI messages — call regularly from the main loop."""
        if not self._available:
            return
        try:
            while self._dev.has_data():
                msg = self._dev.read()
                if msg and self.on_message:
                    status = msg[0]
                    d1 = msg[1] if len(msg) > 1 else 0
                    d2 = msg[2] if len(msg) > 2 else 0
                    self.on_message(status, d1, d2)
        except Exception:
            pass  # device disconnected or transient — silently skip

    # ---------- internal ----------

    def _send(self, status, d1, d2):
        if not self._available:
            return
        try:
            if d2 is not None:
                self._dev.send(bytes([status, d1, d2]))
            elif d1 is not None:
                self._dev.send(bytes([status, d1]))
            else:
                self._dev.send(bytes([status]))
        except Exception:
            pass
