"""
MACROBRUTE — Pico WH Firmware
Arturia MicroBrute Expansion Controller

Handles: main + strip OLED, encoder navigation, clock generation/detection,
firmware clock divider, programmable aux outputs, tap tempo + manual gate,
RGB LED indicators, MIDI SysEx bridge to MicroBrute (LPC2361), USB-MIDI,
EFFIGY peer-pair bus.
"""

import time
from machine import Pin

import config
from display import Display
from strip_display import StripDisplay
from encoder import Encoder
from clock import Clock
from menu import Menu, MenuItem, MenuSystem
from midi import LPCBridge, PARAM_BEND_RANGE, PARAM_GATE_LENGTH, PARAM_STEP_SIZE, PARAM_SEQ_SWING
from leds import LEDManager
from clock_divider import ClockDivider
from aux_outputs import AuxOutputs
from effigy_bridge import EffigyBridge
from usbmidi import USBMidi

# ---- Global State ----

VERSION = "0.2.0"

display = Display()
strip   = StripDisplay()
midi    = LPCBridge()
leds    = LEDManager()
divider = ClockDivider()
aux     = AuxOutputs()
effigy  = EffigyBridge()
usbmidi = USBMidi()

btn_tap = Pin(config.BTN_TAP, Pin.IN, Pin.PULL_UP)


# ---- Clock callbacks ----

def on_clock_tick(count):
    leds.clock.pulse(30)
    midi.send_clock()
    divider.tick()
    aux.tick()
    if effigy.is_paired():
        effigy.send_clock_tick()
    if usbmidi.is_available():
        usbmidi.send_clock_tick()


clock = Clock(on_tick=on_clock_tick)


# ---- Menu Construction ----

def build_menus():
    """Build the full menu tree."""

    clock_menu = Menu("CLOCK", [
        MenuItem("BPM",
                 value_fn=lambda: clock.bpm,
                 adjust_fn=lambda d: setattr(clock, 'internal_bpm', clock.internal_bpm + d)),
        MenuItem("Run/Stop", action=clock.toggle),
        MenuItem("Tap Tempo", action=clock.tap),
        MenuItem("Ext Sync",
                 value_fn=lambda: "ON" if clock.ext_sync else "OFF",
                 adjust_fn=lambda d: (clock.enable_ext_sync() if d > 0 else clock.disable_ext_sync())),
    ])

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

    div_menu = Menu("DIVIDER", [
        MenuItem("Out 1 ÷",
                 value_fn=lambda: divider.get_ratios()[0],
                 adjust_fn=lambda d: _set_div_ratio(0, d)),
        MenuItem("Out 2 ÷",
                 value_fn=lambda: divider.get_ratios()[1],
                 adjust_fn=lambda d: _set_div_ratio(1, d)),
        MenuItem("Out 3 ÷",
                 value_fn=lambda: divider.get_ratios()[2],
                 adjust_fn=lambda d: _set_div_ratio(2, d)),
    ])

    pair_menu = Menu("PAIR", [
        MenuItem("Status",
                 value_fn=lambda: "PAIRED" if effigy.is_paired() else "SOLO"),
        MenuItem("Engine",
                 value_fn=lambda: effigy.engine_name or "—"),
        MenuItem("Probe",
                 action=lambda: _try_pair()),
    ])

    info_menu = Menu("INFO", [
        MenuItem("MACROBRUTE"),
        MenuItem("FW v" + VERSION),
        MenuItem("Pico WH RP2040"),
        MenuItem("USB-MIDI " + ("ON" if usbmidi.is_available() else "—")),
    ])

    root = Menu("MACROBRUTE", [
        MenuItem("Clock",   submenu=clock_menu),
        MenuItem("Divider", submenu=div_menu),
        MenuItem("MIDI",    submenu=midi_menu),
        MenuItem("Pair",    submenu=pair_menu),
        MenuItem("Info",    submenu=info_menu),
    ])

    return root


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


def _set_div_ratio(idx, delta):
    ratios = list(divider.get_ratios())
    ratios[idx] = max(1, ratios[idx] + delta)
    divider.set_ratios(tuple(ratios))
    display.invalidate()


def _try_pair():
    if effigy.probe():
        effigy.set_paired(True)
    display.invalidate()


# ---- Display Drawing ----

def draw_home(oled):
    oled.text("MACROBRUTE", 20, 0)
    oled.hline(0, 10, config.OLED_WIDTH, 1)

    bpm_str = str(clock.bpm)
    oled.text("BPM", 4, 16)
    oled.text(bpm_str, 40, 16)

    if clock.ext_sync:
        status = "EXT" + ("*" if clock.ext_detected else "?")
    elif clock.running:
        status = "RUN"
    else:
        status = "STOP"
    oled.text(status, 84, 16)

    oled.text("Tick:" + str(clock.tick_count), 4, 30)

    oled.hline(0, 42, config.OLED_WIDTH, 1)
    pair_label = "PAIR" if effigy.is_paired() else "SOLO"
    oled.text("[ENC] Menu  " + pair_label, 4, 48)
    oled.text("[TAP] Tempo", 4, 56)


# ---- Strip OLED rendering ----

_strip_frame = 0


def update_strip():
    """Refresh the MicroBrute-panel strip OLED."""
    global _strip_frame
    src = "EXT" if clock.ext_sync else "INT"
    strip.render_status(
        bpm=clock.bpm,
        clock_source=src,
        channel=config.USBMIDI_CHANNEL,
        paired=effigy.is_paired(),
    )
    _strip_frame += 1


# Screensaver dimming is handled internally by Display.needs_render().
# Any call to display.invalidate() (triggered by user input) resets the idle timer.

# ---- Main ----

def main():
    print("MACROBRUTE v" + VERSION + " — booting...")

    leds.startup_sequence()

    def draw_boot(oled):
        oled.text("MACROBRUTE", 20, 20)
        oled.text("v" + VERSION, 44, 34)
        oled.text("Booting...", 28, 50)

    display.render_now(draw_boot)
    time.sleep_ms(800)

    root_menu = build_menus()
    menu_sys = MenuSystem(root_menu)
    in_menu = False

    def on_rotate(delta):
        nonlocal in_menu
        if in_menu:
            menu_sys.on_rotate(delta)
        else:
            clock.internal_bpm = clock.internal_bpm + delta
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
            if menu_sys.at_root and not menu_sys.editing:
                in_menu = False
        display.invalidate()

    encoder = Encoder(on_rotate=on_rotate, on_press=on_press, on_long_press=on_long_press)

    # Probe EFFIGY at boot — non-blocking single attempt
    if effigy.probe():
        effigy.set_paired(True)
        print("EFFIGY paired @ 0x42")

    clock.start()

    print("MACROBRUTE ready.")

    btn_tap_last_val = 1
    btn_tap_press_ms = 0
    last_strip_update_ms = 0
    strip_period_ms = 1000 // max(1, config.STRIP_DISPLAY_FPS)

    while True:
        encoder.update()

        # Tap button — short press = tempo tap, long hold = manual gate
        now = time.ticks_ms()
        btn_val = btn_tap.value()
        if btn_val == 0 and btn_tap_last_val == 1:
            btn_tap_press_ms = now
            display.invalidate()
        elif btn_val == 1 and btn_tap_last_val == 0:
            held = time.ticks_diff(now, btn_tap_press_ms)
            if held < config.TAP_LONG_PRESS_MS:
                clock.tap()
                leds.gate.pulse(50)
            else:
                leds.gate.off()  # release manual gate
            display.invalidate()
        elif btn_val == 0 and time.ticks_diff(now, btn_tap_press_ms) >= config.TAP_LONG_PRESS_MS:
            # Held past long-press threshold — manual gate ON
            leds.gate.on()
        btn_tap_last_val = btn_val

        clock.update()
        midi.update()
        leds.update()
        usbmidi.poll()
        effigy.poll()

        if in_menu:
            display.render(menu_sys.draw)
        else:
            display.render(draw_home)

        if time.ticks_diff(now, last_strip_update_ms) >= strip_period_ms:
            last_strip_update_ms = now
            update_strip()

        time.sleep_ms(1)


if __name__ == "__main__":
    main()
