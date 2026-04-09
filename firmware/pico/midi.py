"""MACROBRUTE Pico H — MIDI SysEx bridge for MicroBrute parameter control."""

from machine import UART, Pin
import config

# Arturia MicroBrute SysEx constants (from Matraszek RE)
SYSEX_START = 0xF0
SYSEX_END = 0xF7
ARTURIA_ID = bytes([0x00, 0x20, 0x6B])
DEVICE_ID = 0x05

# Command types
CMD_IDENTITY_REQUEST = 0x00
CMD_SET_STATE = 0x01

# Parameter codes (Set State command)
PARAM_NOTE_PRIORITY = 0x0B      # 0=Last, 1=Low, 2=High
PARAM_VELOCITY_RESPONSE = 0x11  # 0=Linear, 1=Logarithmic, 2=Exponential
PARAM_PLAY_MODE = 0x2E          # 0=Legato, 1=Retrigger
PARAM_SEQ_RETRIGGER = 0x34      # 0=Reset, 1=Legato, 2=Next
PARAM_STEP_SIZE = 0x3C          # 0=1/4, 1=1/8, 2=1/16, 3=1/32
PARAM_LFO_KEY_RETRIG = 0x41    # 0=Off, 1=On
PARAM_ENVELOPE_LEGATO = 0x48   # 0=Off, 1=On
PARAM_GATE_LENGTH = 0x4F        # 0=Short, 1=Medium, 2=Long, 3=Tie
PARAM_SYNC_MODE = 0x56          # 0=Internal, 1=MIDI, 2=USB, 3=Auto
PARAM_BEND_RANGE = 0x5D         # 1-12 semitones
PARAM_MIDI_RECV_CH = 0x05       # 0=All, 1-16
PARAM_MIDI_SEND_CH = 0x08       # 1-16
PARAM_PLAY_ON = 0x64            # 0=Hold, 1=Note On
PARAM_SEQ_SWING = 0x6B          # 50-75

# Human-readable names
PARAM_NAMES = {
    PARAM_NOTE_PRIORITY: "Note Priority",
    PARAM_VELOCITY_RESPONSE: "Velocity",
    PARAM_PLAY_MODE: "Play Mode",
    PARAM_SEQ_RETRIGGER: "Seq Retrig",
    PARAM_STEP_SIZE: "Step Size",
    PARAM_LFO_KEY_RETRIG: "LFO Retrig",
    PARAM_ENVELOPE_LEGATO: "Env Legato",
    PARAM_GATE_LENGTH: "Gate Length",
    PARAM_SYNC_MODE: "Sync Mode",
    PARAM_BEND_RANGE: "Bend Range",
    PARAM_MIDI_RECV_CH: "MIDI Rx Ch",
    PARAM_MIDI_SEND_CH: "MIDI Tx Ch",
    PARAM_PLAY_ON: "Play On",
    PARAM_SEQ_SWING: "Swing",
}


class MIDIBridge:
    """Send SysEx commands to MicroBrute via UART MIDI."""

    def __init__(self):
        self._uart = UART(1, baudrate=config.MIDI_BAUD,
                          tx=Pin(config.MIDI_TX), rx=Pin(config.MIDI_RX))
        self._counter = 0
        self._rx_buf = bytearray(64)
        self._rx_pos = 0
        self._in_sysex = False

    def _next_counter(self):
        self._counter = (self._counter + 1) & 0x7F
        return self._counter

    def set_param(self, param_code, value):
        """Send a Set State SysEx to MicroBrute."""
        msg = bytearray([
            SYSEX_START,
            *ARTURIA_ID,
            DEVICE_ID,
            CMD_SET_STATE,
            self._next_counter(),
            0x01,           # Sub-command
            param_code,
            value & 0x7F,
            SYSEX_END,
        ])
        self._uart.write(msg)

    def request_identity(self):
        """Send Identity Request."""
        msg = bytearray([
            SYSEX_START,
            *ARTURIA_ID,
            DEVICE_ID,
            CMD_IDENTITY_REQUEST,
            self._next_counter(),
            SYSEX_END,
        ])
        self._uart.write(msg)

    def send_clock(self):
        """Send MIDI Clock (0xF8)."""
        self._uart.write(bytearray([0xF8]))

    def send_start(self):
        """Send MIDI Start (0xFA)."""
        self._uart.write(bytearray([0xFA]))

    def send_stop(self):
        """Send MIDI Stop (0xFC)."""
        self._uart.write(bytearray([0xFC]))

    def send_note_on(self, note, velocity=100, channel=0):
        self._uart.write(bytearray([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F]))

    def send_note_off(self, note, channel=0):
        self._uart.write(bytearray([0x80 | (channel & 0x0F), note & 0x7F, 0]))

    def update(self):
        """Read incoming MIDI and parse SysEx responses."""
        while self._uart.any():
            byte = self._uart.read(1)
            if byte is None:
                break
            b = byte[0]
            if b == SYSEX_START:
                self._in_sysex = True
                self._rx_pos = 0
                self._rx_buf[0] = b
                self._rx_pos = 1
            elif self._in_sysex:
                if self._rx_pos < len(self._rx_buf):
                    self._rx_buf[self._rx_pos] = b
                    self._rx_pos += 1
                else:
                    # Buffer overflow — abort this message
                    self._in_sysex = False
                    self._rx_pos = 0
                    continue
                if b == SYSEX_END:
                    self._in_sysex = False
                    self._handle_sysex(self._rx_buf[:self._rx_pos])

    def _handle_sysex(self, data):
        """Process received SysEx. Override for custom handling."""
        pass
