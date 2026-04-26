"""Strip OLED driver — 0.91" SSD1306 128×32, mounted on the MicroBrute panel.

Shares I²C0 bus with the main 1.3" SH1106 OLED via DB-9 B pins 3/4. Uses the
alt I²C address 0x3D (jumper on the module), so both displays coexist on the
same bus without conflict.

Layout: three zones across the 128-pixel width.

    [tempo numeric]   [clock indicator strip]   [mode glyph]
        BPM 128            ●●●●○○○○                SYNC
        INT clock                                  Ch01

The `update()` method redraws when state changes — call at ~5 Hz from main.
"""

from machine import I2C, Pin
import framebuf
import time

import config

# Minimal SSD1306 init sequence (128×32 variant). Borrowed from the standard
# CircuitPython/MicroPython community drivers and trimmed.
_SET_CONTRAST        = const(0x81)
_SET_ENTIRE_ON       = const(0xA4)
_SET_NORM_INV        = const(0xA6)
_SET_DISP            = const(0xAE)
_SET_MEM_ADDR        = const(0x20)
_SET_COL_ADDR        = const(0x21)
_SET_PAGE_ADDR       = const(0x22)
_SET_DISP_START_LINE = const(0x40)
_SET_SEG_REMAP       = const(0xA0)
_SET_MUX_RATIO       = const(0xA8)
_SET_COM_OUT_DIR     = const(0xC0)
_SET_DISP_OFFSET     = const(0xD3)
_SET_COM_PIN_CFG     = const(0xDA)
_SET_DISP_CLK_DIV    = const(0xD5)
_SET_PRECHARGE       = const(0xD9)
_SET_VCOM_DESEL      = const(0xDB)
_SET_CHARGE_PUMP     = const(0x8D)


class StripDisplay:
    def __init__(self, i2c=None):
        if i2c is None:
            i2c = I2C(
                config.STRIP_OLED_I2C_ID,
                sda=Pin(config.OLED_SDA),
                scl=Pin(config.OLED_SCL),
                freq=400_000,
            )
        self._i2c = i2c
        self._addr = config.STRIP_OLED_ADDR
        self._w = config.STRIP_OLED_WIDTH
        self._h = config.STRIP_OLED_HEIGHT
        self._pages = self._h // 8

        self._buf = bytearray(self._w * self._pages)
        self._fb = framebuf.FrameBuffer(self._buf, self._w, self._h, framebuf.MONO_VLSB)

        self._available = self._init_display()
        if self._available:
            self.clear()
            self.show()

    def is_available(self):
        return self._available

    def _init_display(self):
        cmds = [
            _SET_DISP | 0x00,
            _SET_MEM_ADDR, 0x00,
            _SET_DISP_START_LINE | 0x00,
            _SET_SEG_REMAP | 0x01,
            _SET_MUX_RATIO, self._h - 1,
            _SET_COM_OUT_DIR | 0x08,
            _SET_DISP_OFFSET, 0x00,
            _SET_COM_PIN_CFG, 0x02,  # 128×32 → 0x02 (vs 0x12 for 128×64)
            _SET_DISP_CLK_DIV, 0x80,
            _SET_PRECHARGE, 0xF1,
            _SET_VCOM_DESEL, 0x30,
            _SET_CONTRAST, 0xFF,
            _SET_ENTIRE_ON,
            _SET_NORM_INV,
            _SET_CHARGE_PUMP, 0x14,
            _SET_DISP | 0x01,
        ]
        try:
            for c in cmds:
                self._cmd(c)
            return True
        except OSError:
            return False  # strip OLED not connected — silently disabled

    def _cmd(self, c):
        self._i2c.writeto(self._addr, bytes([0x80, c]))

    def _data(self, buf):
        self._i2c.writeto(self._addr, b"\x40" + buf)

    def clear(self):
        self._fb.fill(0)

    def show(self):
        if not self._available:
            return
        try:
            self._cmd(_SET_COL_ADDR)
            self._cmd(0)
            self._cmd(self._w - 1)
            self._cmd(_SET_PAGE_ADDR)
            self._cmd(0)
            self._cmd(self._pages - 1)
            self._data(self._buf)
        except OSError:
            self._available = False  # cable yanked? disable until next probe

    # ---------- high-level layout helpers ----------

    def render_status(self, bpm, clock_source, channel, paired):
        """Glanceable status line: tempo · clock source · MIDI channel · pair."""
        if not self._available:
            return
        self.clear()
        # Tempo (left, large-ish — 2 lines using 8x8 default font)
        self._fb.text("BPM", 0, 0)
        self._fb.text(str(int(bpm)), 0, 12)
        # Clock source label
        src_text = clock_source[:4].upper()
        self._fb.text(src_text, 36, 0)
        # MIDI channel
        self._fb.text("CH{:02d}".format(channel + 1), 36, 12)
        # Pair indicator (right edge)
        if paired:
            self._fb.text("PAIR", 96, 0)
            self._fb.fill_rect(120, 12, 6, 6, 1)
        else:
            self._fb.text("SOLO", 96, 0)
        # Bottom strip: small clock activity bar
        self._fb.hline(0, 24, 128, 1)
        self.show()

    def render_idle(self, frame):
        """Animated wordmark when idle (no recent input)."""
        if not self._available:
            return
        self.clear()
        # simple scrolling wordmark
        offset = (frame * 2) % 160
        self._fb.text("MACROBRUTE  ·  ", -offset, 12)
        self._fb.text("MACROBRUTE  ·  ", 128 - offset, 12)
        self.show()
