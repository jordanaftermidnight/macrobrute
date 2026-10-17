"""MACROBRUTE Pico — main OLED driver (128×64, SPI, write-only).

Targets the owner's Keyestudio-clone IIC/SPI 1.3" V2.0 module (7-pin SPI header)
on SPI0: SCK (header CLK) GP2, MOSI GP3,
DC GP4, RES GP5 (pins from config.py). The module's CS pin is strapped to
GND (one device on the bus), so config.OLED_CS is None and this driver never
drives CS; if CS is moved back onto a GPIO, set config.OLED_CS to that GP and
the driver toggles it around each transfer.

The controller chip is SH1106 (owner-stated, not bench-verified), so config.py
sets OLED_CHIP = "SH1106" and OLED_COL_OFFSET = 2; SSD1306 stays supported as
an option (OLED_CHIP = "SSD1306", OLED_COL_OFFSET = 0). Module current draw is
UNVERIFIED, and so is the module working with CS tied low (bench check BT-14).
"""

from machine import Pin, SPI
import framebuf
import time
import config

# 4 MHz for both chips. Write-clock limits from datasheet memory, UNVERIFIED:
# SSD1306 about 10 MHz, SH1106 about 4 MHz (the module's chip is owner-stated
# SH1106), so 4 MHz suits either chip and is forgiving of breadboard leads. A full 1 KB frame at 4 MHz takes about 2 ms.
SPI_BAUD = 4_000_000


class OLED_SPI:
    """128×64 OLED driver — works with both SSD1306 and SH1106 chips.

    The two chips share most registers; the differences are the charge-pump
    command (0x8D vs 0xAD) and a 2-column offset on SH1106. `config.OLED_CHIP`
    selects which init sequence to send; `config.OLED_COL_OFFSET` handles the
    offset. Pages are written in page-addressing mode, which both chips use.
    """

    def __init__(self):
        self.width = config.OLED_WIDTH
        self.height = config.OLED_HEIGHT
        self.pages = self.height // 8
        self.col_offset = config.OLED_COL_OFFSET
        self.chip = getattr(config, "OLED_CHIP", "SSD1306").upper()

        # Write-only: no MISO is wired. SPI0 default MISO GP16 may be claimed at
        # init; ClockDivider re-claims GP16 as GPIO afterwards; do not re-init
        # the SPI later (UNVERIFIED, from the rp2 port source).
        self.spi = SPI(
            config.OLED_SPI_ID,
            baudrate=SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(config.OLED_SCK),
            mosi=Pin(config.OLED_MOSI),
        )
        self.dc = Pin(config.OLED_DC, Pin.OUT, value=0)
        self.res = Pin(config.OLED_RES, Pin.OUT, value=1)
        cs = getattr(config, "OLED_CS", None)
        self.cs = None if cs is None else Pin(cs, Pin.OUT, value=1)

        self.buf = bytearray(self.width * self.pages)
        self.fb = framebuf.FrameBuffer(self.buf, self.width, self.height, framebuf.MONO_VLSB)
        self._reset()
        self._init_display()

    def _reset(self):
        # RES is active low: hold high, pulse low, release, then let the
        # controller settle before the first command.
        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        time.sleep_ms(10)

    def _init_display(self):
        # Chip-specific charge-pump command differs between SSD1306 and SH1106.
        if self.chip == "SH1106":
            charge_pump = [0xAD, 0x8B]   # SH1106 DC-DC enable
        else:
            charge_pump = [0x8D, 0x14]   # SSD1306 charge-pump enable

        init_cmds = [
            0xAE,        # Display OFF
            0xD5, 0x80,  # Clock divide / oscillator frequency
            0xA8, 0x3F,  # Multiplex ratio (64 rows - 1)
            0xD3, 0x00,  # Display offset = 0
            0x40,        # Display start line = 0
            *charge_pump,
            0xA1,        # Segment remap (flip horizontal)
            0xC8,        # COM output scan direction (flip vertical)
            0xDA, 0x12,  # COM pins hardware config (128×64)
            0x81, 0x80,  # Contrast
            0xD9, 0x22,  # Pre-charge period
            0xDB, 0x35,  # VCOM deselect level
            0xA4,        # Entire display ON from RAM
            0xA6,        # Normal (non-inverted) display
            0xAF,        # Display ON
        ]
        for cmd in init_cmds:
            self._cmd(cmd)

    def _write(self, dc, buf):
        self.dc(dc)
        if self.cs is not None:
            self.cs(0)
        self.spi.write(buf)
        if self.cs is not None:
            self.cs(1)

    def _cmd(self, cmd):
        self._write(0, bytearray([cmd]))

    def _data(self, buf):
        self._write(1, buf)

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
        self.oled = OLED_SPI()
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
