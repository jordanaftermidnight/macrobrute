"""MACROBRUTE Pico H — LPC2361 bridge for MicroBrute parameter control.

Pico sends commands to LPC2361 over UART0 (GP0/GP1 at 115200 baud).
LPC firmware translates these into MIDI SysEx messages sent to the
MicroBrute internally. This replaces the previous direct MIDI UART approach,
freeing GP4/GP5 for I2C OLED.
"""

from machine import UART, Pin
import config

ARTURIA_ID = bytes([0x00, 0x20, 0x6B])
DEVICE_ID = 0x05

CMD_SET_STATE = 0x01
CMD_IDENTITY_REQUEST = 0x00

PARAM_NOTE_PRIORITY = 0x0B
PARAM_VELOCITY_RESPONSE = 0x11
PARAM_PLAY_MODE = 0x2E
PARAM_SEQ_RETRIGGER = 0x34
PARAM_STEP_SIZE = 0x3C
PARAM_LFO_KEY_RETRIG = 0x41
PARAM_ENVELOPE_LEGATO = 0x48
PARAM_GATE_LENGTH = 0x4F
PARAM_SYNC_MODE = 0x56
PARAM_BEND_RANGE = 0x5D
PARAM_MIDI_RECV_CH = 0x05
PARAM_MIDI_SEND_CH = 0x08
PARAM_PLAY_ON = 0x64
PARAM_SEQ_SWING = 0x6B

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

MSG_PARAM_SET = 0x01
MSG_CLOCK = 0x02
MSG_START = 0x03
MSG_STOP = 0x04
MSG_NOTE_ON = 0x05
MSG_NOTE_OFF = 0x06


class LPCBridge:
    """Communicate with LPC2361 over UART for MIDI SysEx relay."""

    def __init__(self):
        self._uart = UART(0, baudrate=config.LPC_BAUD,
                          tx=Pin(config.LPC_TX), rx=Pin(config.LPC_RX))
        self._counter = 0
        self._rx_buf = bytearray(128)
        self._rx_pos = 0
        self._in_msg = False

    def _next_counter(self):
        self._counter = (self._counter + 1) & 0x7F
        return self._counter

    def _send(self, msg_type, payload=b''):
        hdr = bytearray([
            0xAA,
            msg_type,
            self._next_counter(),
            len(payload) & 0xFF,
        ])
        self._uart.write(hdr + payload)

    def set_param(self, param_code, value):
        self._send(MSG_PARAM_SET, bytearray([param_code, value & 0x7F]))

    def send_clock(self):
        self._send(MSG_CLOCK)

    def send_start(self):
        self._send(MSG_START)

    def send_stop(self):
        self._send(MSG_STOP)

    def send_note_on(self, note, velocity=100, channel=0):
        self._send(MSG_NOTE_ON, bytearray([channel & 0x0F, note & 0x7F, velocity & 0x7F]))

    def send_note_off(self, note, channel=0):
        self._send(MSG_NOTE_OFF, bytearray([channel & 0x0F, note & 0x7F]))

    def update(self):
        while self._uart.any():
            byte = self._uart.read(1)
            if byte is None:
                break
            b = byte[0]
            if b == 0xAA and not self._in_msg:
                self._in_msg = True
                self._rx_pos = 0
                self._rx_buf[0] = b
                self._rx_pos = 1
            elif self._in_msg:
                if self._rx_pos < len(self._rx_buf):
                    self._rx_buf[self._rx_pos] = b
                    self._rx_pos += 1
                if self._rx_pos >= 4:
                    payload_len = self._rx_buf[3]
                    total = 4 + payload_len
                    if self._rx_pos >= total:
                        self._in_msg = False
                        self._handle_response(self._rx_buf[:self._rx_pos])

    def _handle_response(self, data):
        pass
