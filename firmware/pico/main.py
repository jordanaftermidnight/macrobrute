"""
MACROBRUTE — Pico H Firmware
Arturia MicroBrute Expansion Controller

Handles: OLED display, encoder navigation, clock generation/detection,
tap tempo, LED indicators, MIDI SysEx bridge to MicroBrute.
"""

import time
from machine import Pin
import config
from display import Display
from encoder import Encoder
from clock import Clock
from menu import Menu, MenuItem, MenuSystem
from midi import MIDIBridge, PARAM_BEND_RANGE, PARAM_GATE_LENGTH, PARAM_STEP_SIZE, PARAM_SEQ_SWING
from leds import LEDManager

# ---- Global State ----

VERSION = "0.1.0"

display = Display()
clock = Clock()
midi = MIDIBridge()
leds = LEDManager()

# Gate output (directly from button)
gate_out = Pin(config.LED_GATE, Pin.OUT, value=0)
btn_tap = Pin(config.BTN_TAP, Pin.IN, Pin.PULL_UP)
btn_tap_last = 1


# ---- Clock callbacks ----

def on_clock_tick(count):
    leds.clock.pulse(30)
    midi.send_clock()


clock._on_tick = on_clock_tick


# ---- Menu Construction ----

def build_menus():
    """Build the full menu tree."""

    # Clock submenu
    clock_menu = Menu("CLOCK", [
        MenuItem("BPM",
                 value_fn=lambda: clock.bpm,
                 adjust_fn=lambda d: setattr(clock, 'bpm', clock.bpm + d)),
        MenuItem("Run/Stop", action=clock.toggle),
        MenuItem("Tap Tempo", action=clock.tap),
        MenuItem("Ext Sync",
                 value_fn=lambda: "ON" if clock._ext_sync else "OFF",
                 adjust_fn=lambda d: (clock.enable_ext_sync() if d > 0 else clock.disable_ext_sync())),
    ])

    # MIDI submenu
    midi_menu = Menu("MIDI", [
        MenuItem("Bend Range",
                 value_fn=lambda: _state.get("bend", 2),
                 adjust_fn=lambda d: _midi_adjust("bend", PARAM_BEND_RANGE, d, 1, 12)),
        MenuItem("Gate Length",
                 value_fn=lambda: ["Short", "Med", "Long", "Tie"][_state.get("gate_len", 1)],
                 adjust_fn=lambda d: _midi_adjust("gate_len", PARAM_GATE_LENGTH, d, 0, 3)),
        MenuItem("Step Size",
                 value_fn=lambda: ["1/4", "1/8", "1/16", "1/32"][_state.get("step", 0)],
                 adjust_fn=lambda d: _midi_adjust("step", PARAM_STEP_SIZE, d, 0, 3)),
        MenuItem("Swing",
                 value_fn=lambda: _state.get("swing", 50),
                 adjust_fn=lambda d: _midi_adjust("swing", PARAM_SEQ_SWING, d, 50, 75)),
    ])

    # Info screen
    info_menu = Menu("INFO", [
        MenuItem("MACROBRUTE"),
        MenuItem("FW v" + VERSION),
        MenuItem("Pico H RP2040"),
    ])

    # Root menu
    root = Menu("MACROBRUTE", [
        MenuItem("Clock", submenu=clock_menu),
        MenuItem("MIDI", submenu=midi_menu),
        MenuItem("Info", submenu=info_menu),
    ])

    return root


# Mutable state for MIDI params
_state = {
    "bend": 2,
    "gate_len": 1,
    "step": 0,
    "swing": 50,
}


def _midi_adjust(key, param, delta, lo, hi):
    v = _state.get(key, lo)
    v = max(lo, min(hi, v + delta))
    _state[key] = v
    midi.set_param(param, v)
    display.invalidate()


# ---- Display Drawing ----

def draw_home(oled):
    """Home screen: BPM, clock status, mode."""
    oled.text("MACROBRUTE", 20, 0)
    oled.hline(0, 10, config.OLED_WIDTH, 1)

    # BPM display (large)
    bpm_str = str(clock.bpm)
    oled.text("BPM", 4, 16)
    oled.text(bpm_str, 40, 16)

    # Clock status
    status = "EXT" if clock._ext_sync else ("RUN" if clock._running else "STOP")
    oled.text(status, 88, 16)

    # Tick counter
    oled.text("Tick:" + str(clock.tick_count), 4, 30)

    # Divider
    oled.hline(0, 42, config.OLED_WIDTH, 1)
    oled.text("[ENC] Menu", 4, 48)
    oled.text("[TAP] Tempo", 4, 56)


# ---- Main ----

def main():
    print(f"MACROBRUTE v{VERSION} — booting...")

    # LED startup test
    leds.startup_sequence()

    # Boot screen
    def draw_boot(oled):
        oled.text("MACROBRUTE", 20, 20)
        oled.text("v" + VERSION, 44, 34)
        oled.text("Booting...", 28, 50)

    display.render_now(draw_boot)
    time.sleep_ms(1000)

    # Build menu system
    root_menu = build_menus()
    menu_sys = MenuSystem(root_menu)
    in_menu = False

    # Encoder callbacks
    def on_rotate(delta):
        nonlocal in_menu
        if in_menu:
            menu_sys.on_rotate(delta)
        else:
            # Adjust BPM from home screen
            clock.bpm = clock.bpm + delta
        display.invalidate()

    def on_press():
        nonlocal in_menu
        if in_menu:
            menu_sys.on_press()
        else:
            in_menu = True
        display.invalidate()

    def on_long_press():
        nonlocal in_menu
        if in_menu:
            menu_sys.on_back()
            if len(menu_sys._stack) == 1 and not menu_sys.editing:
                in_menu = False
        display.invalidate()

    encoder = Encoder(on_rotate=on_rotate, on_press=on_press, on_long_press=on_long_press)

    # Start clock
    clock.start()

    print("MACROBRUTE ready.")

    # Main loop
    btn_tap_last_val = 1
    while True:
        # Poll encoder
        encoder.update()

        # Poll tap tempo button
        btn_val = btn_tap.value()
        if btn_val == 0 and btn_tap_last_val == 1:
            clock.tap()
            leds.gate.pulse(50)
            display.invalidate()
        btn_tap_last_val = btn_val

        # Update subsystems
        clock.update()
        midi.update()
        leds.update()

        # Render display
        if in_menu:
            display.render(menu_sys.draw)
        else:
            display.render(draw_home)

        time.sleep_ms(1)


if __name__ == "__main__":
    main()
