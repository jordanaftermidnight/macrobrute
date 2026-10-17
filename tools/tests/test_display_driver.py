"""Hardware-free checks for firmware/pico/display.py (the main SPI OLED driver).

`machine`, `framebuf` and `time` are stubbed through sys.modules so the
MicroPython module can be imported under CPython. Every pin write and SPI
transfer lands in one ordered event log.
"""
import ast
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PICO = ROOT / "firmware" / "pico"
DISPLAY = PICO / "display.py"


def _load_config(**overrides):
    spec = importlib.util.spec_from_file_location("config", PICO / "config.py")
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return cfg


def _stubs(log):
    machine = types.ModuleType("machine")

    class Pin:
        OUT, IN, PULL_UP = 1, 0, 2

        def __init__(self, gp, mode=None, pull=None, value=None):
            self.gp = gp
            self.mode = mode
            if value is not None:
                log.append(("pin", gp, value))

        def __call__(self, v=None):
            if v is not None:
                log.append(("pin", self.gp, v))

        def value(self, v=None):
            self(v)

        on = lambda self: self(1)
        off = lambda self: self(0)

    class SPI:
        def __init__(self, ident, baudrate=None, polarity=0, phase=0, sck=None, mosi=None, miso=None, **kw):
            log.append(("spi_init", ident, baudrate, sck.gp if sck else None, mosi.gp if mosi else None, miso))

        def write(self, buf):
            log.append(("spi", bytes(buf)))

    machine.Pin = Pin
    machine.SPI = SPI

    framebuf = types.ModuleType("framebuf")
    framebuf.MONO_VLSB = 0

    class FrameBuffer:
        def __init__(self, buf, w, h, fmt):
            self.buf = buf

        def fill(self, c):
            for i in range(len(self.buf)):
                self.buf[i] = 0xFF if c else 0

        def __getattr__(self, name):
            return lambda *a, **k: None

    framebuf.FrameBuffer = FrameBuffer

    fake_time = types.ModuleType("time")
    fake_time.sleep_ms = lambda ms: log.append(("sleep", ms))
    fake_time.ticks_ms = lambda: 0
    fake_time.ticks_diff = lambda a, b: a - b
    return machine, framebuf, fake_time


def _load_display(monkeypatch, **cfg_overrides):
    log = []
    machine, framebuf, fake_time = _stubs(log)
    cfg = _load_config(**cfg_overrides)
    monkeypatch.setitem(sys.modules, "machine", machine)
    monkeypatch.setitem(sys.modules, "framebuf", framebuf)
    monkeypatch.setitem(sys.modules, "config", cfg)
    # Swap `time` only while the module body runs: it binds the stub as its
    # own `time`, and CPython's real module is restored straight after.
    real_time = sys.modules["time"]
    sys.modules["time"] = fake_time
    try:
        spec = importlib.util.spec_from_file_location("display_under_test", DISPLAY)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.modules["time"] = real_time
    return mod, cfg, log


def _commands(log, dc_gp):
    """Bytes sent while DC was low (commands) and high (data), in order."""
    dc = None
    cmds, data = [], []
    for ev in log:
        if ev[0] == "pin" and ev[1] == dc_gp:
            dc = ev[2]
        elif ev[0] == "spi":
            assert dc in (0, 1), "SPI write before DC was driven"
            (cmds if dc == 0 else data).append(ev[1])
    return cmds, data


def test_display_py_parses():
    ast.parse(DISPLAY.read_text())


def test_no_i2c_and_chip_is_owner_stated_sh1106():
    src = DISPLAY.read_text()
    assert "I2C" not in src and "WARNING" not in src
    doc = ast.get_docstring(ast.parse(src))
    assert "SH1106" in doc and "owner-stated" in doc
    assert "UNVERIFIED" in doc  # current draw and CS tied low (BT-14) stay unverified


def test_config_defaults_to_sh1106_with_column_offset():
    cfg = _load_config()
    assert cfg.OLED_CHIP == "SH1106" and cfg.OLED_COL_OFFSET == 2


def test_spi_bus_and_reset_pulse(monkeypatch):
    mod, cfg, log = _load_display(monkeypatch)
    mod.OLED_SPI()
    init = [e for e in log if e[0] == "spi_init"]
    assert init == [("spi_init", cfg.OLED_SPI_ID, init[0][2], cfg.OLED_SCK, cfg.OLED_MOSI, None)]
    assert 0 < init[0][2] <= 4_000_000
    res = [e[2] for e in log if e[0] == "pin" and e[1] == cfg.OLED_RES]
    edges = [v for i, v in enumerate(res) if i == 0 or v != res[i - 1]]
    assert edges == [1, 0, 1], "RES must pulse high, low, high"
    assert any(e[0] == "sleep" for e in log), "reset pulse needs a hold time"
    first_spi = next(i for i, e in enumerate(log) if e[0] == "spi")
    last_res = max(i for i, e in enumerate(log) if e[0] == "pin" and e[1] == cfg.OLED_RES)
    assert last_res < first_spi, "reset completes before any SPI byte"


@pytest.mark.parametrize("chip, pump, absent", [
    ("SSD1306", b"\x8d\x14", b"\xad\x8b"),
    ("SH1106", b"\xad\x8b", b"\x8d\x14"),
])
def test_init_sends_chip_specific_charge_pump(monkeypatch, chip, pump, absent):
    mod, cfg, log = _load_display(monkeypatch, OLED_CHIP=chip)
    mod.OLED_SPI()
    cmds, data = _commands(log, cfg.OLED_DC)
    stream = b"".join(cmds)
    assert pump in stream and absent not in stream
    assert stream.startswith(b"\xae") and stream.endswith(b"\xaf")
    assert data == []


@pytest.mark.parametrize("chip, offset", [("SSD1306", 0), ("SH1106", 2)])
def test_show_writes_pages_with_dc_low_for_commands(monkeypatch, chip, offset):
    mod, cfg, log = _load_display(monkeypatch, OLED_CHIP=chip, OLED_COL_OFFSET=offset)
    oled = mod.OLED_SPI()
    log.clear()
    oled.show()
    cmds, data = _commands(log, cfg.OLED_DC)
    assert len(data) == 8 and all(len(d) == 128 for d in data)
    expected = b"".join(bytes([0xB0 + p, offset & 0x0F, 0x10 | (offset >> 4)]) for p in range(8))
    assert b"".join(cmds) == expected
    # Order: 3 command bytes then one data block per page.
    kinds = []
    dc = None
    for ev in log:
        if ev[0] == "pin" and ev[1] == cfg.OLED_DC:
            dc = ev[2]
        elif ev[0] == "spi":
            kinds.append("D" if dc else "C")
    assert "".join(kinds) == "CCCD" * 8 or "".join(kinds) == "CD" * 8


def test_cs_untouched_when_not_configured(monkeypatch):
    mod, cfg, log = _load_display(monkeypatch, OLED_CS=None)
    oled = mod.OLED_SPI()
    oled.show()
    used = {e[1] for e in log if e[0] == "pin"}
    assert used == {cfg.OLED_DC, cfg.OLED_RES}


def test_cs_toggled_around_each_transfer_when_configured(monkeypatch):
    mod, cfg, log = _load_display(monkeypatch, OLED_CS=27)
    oled = mod.OLED_SPI()
    log.clear()
    oled.show()
    cs = None
    for ev in log:
        if ev[0] == "pin" and ev[1] == 27:
            cs = ev[2]
        elif ev[0] == "spi":
            assert cs == 0, "CS must be low during a transfer"
    assert cs == 1, "CS released after the last transfer"


def test_display_manager_api(monkeypatch):
    mod, cfg, log = _load_display(monkeypatch, OLED_CS=None)
    d = mod.Display()
    for name in ("clear", "text", "show", "fb", "hline", "contrast", "pixel"):
        assert hasattr(d.oled, name)
    d.render_now(lambda o: o.text("X", 0, 0))
    assert any(e[0] == "spi" for e in log)


@pytest.mark.parametrize("chip", ["SSD1306", "SH1106"])
def test_spi_clock_within_the_slower_chip_limit(monkeypatch, chip):
    # SH1106 write clock is about 4 MHz (datasheet memory, UNVERIFIED): stay at or below it
    mod, cfg, log = _load_display(monkeypatch, OLED_CHIP=chip)
    mod.OLED_SPI()
    baud = [e for e in log if e[0] == "spi_init"][0][2]
    assert baud == 4_000_000
