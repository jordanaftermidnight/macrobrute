"""MACROBRUTE Pico H — OLED display driver (SH1106 SPI)."""

from machine import Pin, SPI
import framebuf
import time
import config


class SH1106_SPI:
    """SH1106 128x64 OLED driver over SPI."""

    def __init__(self):
        self.width = config.OLED_WIDTH
        self.height = config.OLED_HEIGHT
        self.pages = self.height // 8

        self.dc = Pin(config.OLED_DC, Pin.OUT)
        self.cs = Pin(config.OLED_CS, Pin.OUT)
        self.rst = Pin(config.OLED_RST, Pin.OUT)

        self.spi = SPI(
            config.OLED_SPI_ID,
            baudrate=4_000_000,
            polarity=0,
            phase=0,
            sck=Pin(config.OLED_SCK),
            mosi=Pin(config.OLED_MOSI),
        )

        self.buf = bytearray(self.width * self.pages)
        self.fb = framebuf.FrameBuffer(self.buf, self.width, self.height, framebuf.MONO_VLSB)
        self._init_display()

    def _init_display(self):
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(10)

        init_cmds = [
            0xAE,        # Display OFF
            0xD5, 0x80,  # Clock div ratio
            0xA8, 0x3F,  # Multiplex ratio (64-1)
            0xD3, 0x00,  # Display offset
            0x40,        # Start line 0
            0x8D, 0x14,  # Charge pump ON
            0x20, 0x00,  # Horizontal addressing
            0xA1,        # Segment remap (flip horizontal)
            0xC8,        # COM scan direction (flip vertical)
            0xDA, 0x12,  # COM pins config
            0x81, 0xCF,  # Contrast
            0xD9, 0xF1,  # Pre-charge period
            0xDB, 0x40,  # VCOMH deselect level
            0xA4,        # Display from RAM
            0xA6,        # Normal display (not inverted)
            0xAF,        # Display ON
        ]
        for cmd in init_cmds:
            self._cmd(cmd)

    def _cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def show(self):
        """Push framebuffer to display."""
        for page in range(self.pages):
            self._cmd(0xB0 + page)       # Set page
            self._cmd(0x02)              # Lower column (SH1106 offset)
            self._cmd(0x10)              # Upper column
            self.dc.value(1)
            self.cs.value(0)
            self.spi.write(self.buf[page * self.width:(page + 1) * self.width])
            self.cs.value(1)

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
        self.oled = SH1106_SPI()
        self._dirty = True
        self._last_render = 0
        self._frame_interval_ms = 1000 // config.DISPLAY_FPS
        self._idle_since = time.ticks_ms()
        self._dimmed = False

    def invalidate(self):
        self._dirty = True
        self._idle_since = time.ticks_ms()
        if self._dimmed:
            self.oled.contrast(0xCF)
            self._dimmed = False

    def needs_render(self):
        now = time.ticks_ms()
        if not self._dirty:
            # Check screensaver
            if not self._dimmed and time.ticks_diff(now, self._idle_since) > config.SCREENSAVER_TIMEOUT_S * 1000:
                self.oled.contrast(0x00)
                self._dimmed = True
            return False
        if time.ticks_diff(now, self._last_render) < self._frame_interval_ms:
            return False
        return True

    def render(self, draw_fn):
        """Call draw_fn(oled) then push to screen if due."""
        if not self.needs_render():
            return
        self.oled.clear()
        draw_fn(self.oled)
        self.oled.show()
        self._dirty = False
        self._last_render = time.ticks_ms()

    def render_now(self, draw_fn):
        """Force immediate render."""
        self.oled.clear()
        draw_fn(self.oled)
        self.oled.show()
        self._dirty = False
        self._last_render = time.ticks_ms()
