"""MACROBRUTE Pico WH — OLED display driver (SH1106 1.3" I2C, 128x64).

Primary target is the SH1106 1.3" module. The driver also works with the
0.96" SSD1306 fallback — set OLED_COL_OFFSET = 0 in config.py for that.
"""

from machine import Pin, I2C
import framebuf
import time
import config


class SH1106_I2C:
    """SH1106 128x64 OLED driver over I2C (page addressing mode).

    SH1106 uses page addressing with a 2-column offset (visible area starts
    at column 2). SSD1306 is addressable from column 0 in horizontal mode.
    Set config.OLED_COL_OFFSET to switch between them.
    """

    def __init__(self):
        self.width = config.OLED_WIDTH
        self.height = config.OLED_HEIGHT
        self.pages = self.height // 8
        self.addr = config.OLED_ADDR
        self.col_offset = config.OLED_COL_OFFSET

        self.i2c = I2C(
            config.OLED_I2C_ID,
            scl=Pin(config.OLED_SCL),
            sda=Pin(config.OLED_SDA),
            freq=400_000,
        )

        self.buf = bytearray(self.width * self.pages)
        self.fb = framebuf.FrameBuffer(self.buf, self.width, self.height, framebuf.MONO_VLSB)
        self._init_display()

    def _init_display(self):
        init_cmds = [
            0xAE,        # Display OFF
            0xD5, 0x80,  # Clock divide ratio / oscillator freq
            0xA8, 0x3F,  # Multiplex ratio (64 rows - 1)
            0xD3, 0x00,  # Display offset = 0
            0x40,        # Display start line = 0
            0xAD, 0x8B,  # SH1106 DC-DC charge pump enable (SSD1306 ignores; use 0x8D,0x14 for SSD1306)
            0xA1,        # Segment remap (flip horizontal)
            0xC8,        # COM output scan direction (flip vertical)
            0xDA, 0x12,  # COM pins hardware config
            0x81, 0x80,  # Contrast
            0xD9, 0x22,  # Pre-charge period
            0xDB, 0x35,  # VCOM deselect level
            0xA4,        # Entire display ON from RAM (not forced)
            0xA6,        # Normal (non-inverted) display
            0xAF,        # Display ON
        ]
        for cmd in init_cmds:
            self._cmd(cmd)

    def _cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x00, cmd]))

    def _data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)

    def show(self):
        col_lo = self.col_offset & 0x0F
        col_hi = 0x10 | ((self.col_offset >> 4) & 0x0F)
        for page in range(self.pages):
            self._cmd(0xB0 + page)
            self._cmd(col_lo)
            self._cmd(col_hi)
            start = page * self.width
            self._data(self.buf[start:start + self.width])

    def clear(self):
        self.fb.fill(0)

    def text(self, string, x, y, color=1):
        self.fb.text(string, x, y, color)

    def pixel(self, x, y, color=1):
        self.fb.pixel(x, y, color)

    def hline(self, x, y, w, color=1):
        self.fb.hline(x, y, w, color)

    def vline(self, x, y, h, color=1):
        self.fb.vline(x, y, h, color)

    def rect(self, x, y, w, h, color=1):
        self.fb.rect(x, y, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        self.fb.fill_rect(x, y, w, h, color)

    def contrast(self, value):
        self._cmd(0x81)
        self._cmd(value & 0xFF)

    def invert(self, on=True):
        self._cmd(0xA7 if on else 0xA6)

    def power_off(self):
        self._cmd(0xAE)

    def power_on(self):
        self._cmd(0xAF)


class Display:
    """High-level display manager with dirty-flag rendering."""

    def __init__(self):
        self.oled = SH1106_I2C()
        self._dirty = True
        self._last_render = 0
        self._frame_interval_ms = 1000 // config.DISPLAY_FPS
        self._idle_since = time.ticks_ms()
        self._dimmed = False

    def invalidate(self):
        self._dirty = True
        self._idle_since = time.ticks_ms()
        if self._dimmed:
            self.oled.contrast(0x80)
            self._dimmed = False

    def needs_render(self):
        now = time.ticks_ms()
        if not self._dirty:
            if not self._dimmed and time.ticks_diff(now, self._idle_since) > config.SCREENSAVER_TIMEOUT_S * 1000:
                self.oled.contrast(0x00)
                self._dimmed = True
            return False
        if time.ticks_diff(now, self._last_render) < self._frame_interval_ms:
            return False
        return True

    def render(self, draw_fn):
        if not self.needs_render():
            return
        self.oled.clear()
        draw_fn(self.oled)
        self.oled.show()
        self._dirty = False
        self._last_render = time.ticks_ms()

    def render_now(self, draw_fn):
        self.oled.clear()
        draw_fn(self.oled)
        self.oled.show()
        self._dirty = False
        self._last_render = time.ticks_ms()
