"""MACROBRUTE Raspberry Pi Pico — Hardware configuration and pin assignments.

Authoritative source for pin allocation. The connection map (docs/
MACROBRUTE_CONNECTION_MAP.md §1) and this file must be kept in sync.
"""

# ---------------------------------------------------------------------------
# Main OLED — baseline (owner ruling, 2026-10-17): the owner's Keyestudio-clone
#   IIC/SPI 1.3" V2.0 module, 128×64, 7-pin SPI header, write-only on SPI0 (no
#   MISO), driven by display.py (OLED_SPI). Owner-stated, not bench-verified:
#   chip SH1106 and header order GND, VCC, CLK, MOSI, RES, DC, CS. Pin
#   mapping: GND→GND, VCC→3V3, CLK→GP2, MOSI→GP3, RES→GP5, DC→GP4, CS→GND.
#   The module's CS pin is strapped to GND (single device on the bus; that the
#   module works with CS tied low is UNVERIFIED, bench check BT-14). Fallback
#   if it does not: CS back on a GPIO (set OLED_CS to it) and the gate input
#   moves to GP27/GP28 with the BT-5 leakage check or a series diode / 3V3
#   buffer. If the board has IIC/SPI selection pads or resistors they must be
#   in the SPI position (UNVERIFIED: no manual found). SH1106 needs
#   OLED_COL_OFFSET=2; the driver still supports OLED_CHIP="SSD1306" with
#   offset 0. Powered from the Pico 3V3 pin, 3V3 logic; current draw
#   UNVERIFIED. A 1.3" module is larger than the old 0.96" panel cutout, which
#   bears on the open expander width.
#
#   The earlier 4-pin I²C 1.3" module is in a TD-3 and is not available. An
#   I²C display would need GP4/GP5, which are DC/RES here, so it requires
#   re-pinning (not a drop-in). No I²C is used anywhere on the expander.
# ---------------------------------------------------------------------------
OLED_CHIP        = "SH1106"   # "SSD1306" or "SH1106" (SH1106: owner-stated)
OLED_WIDTH       = 128
OLED_HEIGHT      = 64
OLED_COL_OFFSET  = 2       # SH1106 = 2; SSD1306 = 0
OLED_SPI_ID      = 0       # SPI0, write-only (no MISO)
OLED_SCK         = 2       # GP2  — SPI0 SCK  → module CLK
OLED_MOSI        = 3       # GP3  — SPI0 TX   → module MOSI
OLED_DC          = 4       # GP4  — data/command select
OLED_RES         = 5       # GP5  — reset (active low)
OLED_CS          = None    # CS strapped to GND, no GPIO (PROVISIONAL, BT-14)

# Legacy I²C driver values. strip_display.py (dropped, no longer built by
#   main.py) still reads these; a firmware follow-up removes them. They are
#   not pin roles: GP4/GP5 are OLED DC/RES above.
OLED_I2C_ID      = 0       # legacy (I²C driver), not wired
OLED_SDA         = 4       # legacy (I²C driver); GP4 is OLED_DC in this design
OLED_SCL         = 5       # legacy (I²C driver); GP5 is OLED_RES in this design
OLED_ADDR        = 0x3C    # legacy (I²C driver)

# ---------------------------------------------------------------------------
# Strip OLED — DROPPED (owner decision, 2026-10-17). Nothing on the
#   MicroBrute panel uses I²C, no I²C crosses the DB-9 cable and the expander
#   has no I²C bus. These values remain only because strip_display.py still
#   reads them; a later firmware task removes both.
# ---------------------------------------------------------------------------
STRIP_OLED_I2C_ID = 0      # DROPPED (strip OLED); no I²C bus exists on the expander
STRIP_OLED_WIDTH  = 128
STRIP_OLED_HEIGHT = 32
STRIP_OLED_ADDR   = 0x3D   # SSD1306 alt address (must be jumpered on module)

# ---------------------------------------------------------------------------
# LPC2361 ↔ Pico UART bridge — Pico UART0 over DB-9 B pin 1 (TX) and pin 6 (RX)
#   LPC side: UART1, P0.16/RXD1 (LQFP pin 63) and P0.15/TXD1 (pin 62).
#   UNVERIFIED until the Phase 0 continuity check (connection map §5.4).
#   1 kΩ series at each end of each line; no divider, no level shifter.
#   Frame: 0xAA [msg_type] [counter] [len] [payload...] [xor_checksum]
#   Pico is the controller; LPC firmware handles routing of stock MIDI events.
# ---------------------------------------------------------------------------
LPC_TX     = 0             # GP0  — UART0 TX → DB-9 B:1 → LPC2361 P0.16 (RXD1)
LPC_RX     = 1             # GP1  — UART0 RX ← DB-9 B:6 ← LPC2361 P0.15 (TXD1)
LPC_BAUD   = 115200

# ---------------------------------------------------------------------------
# Rotary encoder (HW-040) — on expander panel
# ---------------------------------------------------------------------------
ENC_CLK    = 14            # GP14 — Rotation A
ENC_DT     = 15            # GP15 — Rotation B
ENC_SW     = 13            # GP13 — Push button (short press, long press)

# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
BTN_TAP    = 12            # GP12 — Tap tempo (short) · Manual gate (long)

# ---------------------------------------------------------------------------
# RGB LED — common-cathode, owned exclusively by leds.LEDManager
#   R = clock tick · G = gate activity · B = mode indicator
# ---------------------------------------------------------------------------
LED_CLOCK  = 8             # GP8  — RGB R channel (clock pulse)
LED_GATE   = 9             # GP9  — RGB G channel (gate activity)
LED_MODE   = 10            # GP10 — RGB B channel (mode indicator; the old "pair status" meaning is shelved)

# ---------------------------------------------------------------------------
# Gate input — Pico mirror of the MicroBrute gate (DB-9 A:1), PROVISIONAL
#   (owner ruling 2026-10-17, BT-14). Direction IN. Fed from the MicroBrute
#   CD40106 stage output through the 22k/33k divider (backfeed/hum note,
#   section 3.5). GP11 is a fault-tolerant pin (GPIO0-25, RP2040 datasheet),
#   which is what the unpowered-Pico case needs; that case stays provisional
#   until BT-5. No firmware module reads it yet.
# ---------------------------------------------------------------------------
GATE_IN    = 11            # GP11 — gate input (IN), PROVISIONAL (BT-14)

# ---------------------------------------------------------------------------
# Clock I/O (3.3 V logic on expander panel jacks)
# ---------------------------------------------------------------------------
CLOCK_OUT  = 22            # GP22 — Master clock out (plain GPIO, Timer-driven)
CLOCK_IN   = 21            # GP21 — External clock in (IRQ rising edge)

# ---------------------------------------------------------------------------
# Firmware clock divider — fans out master clock to 3 panel jacks
#   Replaces the CD4024 chip from earlier hardware plans. Divisions are
#   reconfigurable via menu (default /2, /4, /8).
# ---------------------------------------------------------------------------
CLK_DIV_PINS    = (16, 17, 18)         # GP16/17/18 — divider outputs
CLK_DIV_DEFAULTS = (2, 4, 8)            # default ratios for the 3 outputs

# ---------------------------------------------------------------------------
# Programmable aux outputs — 4 panel jacks, firmware-routable
#   Each can be: tap-tempo divided, Pico-pattern (Euclidean/random), passthrough,
#   or PWM-filtered CV. Mode set per-jack via menu.
# ---------------------------------------------------------------------------
AUX_OUT_PINS = (19, 20, 6, 7)          # GP19, GP20, GP6, GP7

# Aux output modes (bit values for menu state)
AUX_MODE_OFF       = 0
AUX_MODE_TAP_DIV   = 1   # tap tempo divided (rate set per-jack)
AUX_MODE_EUCLID    = 2   # Euclidean(n,k) gate generator
AUX_MODE_RANDOM    = 3   # probabilistic gate (probability per-jack)
AUX_MODE_PASSTHRU  = 4   # mirror another signal (clock in, MIDI gate, etc.)
AUX_MODE_PWM_CV    = 5   # PWM-filtered CV (needs RC on jack)

# ---------------------------------------------------------------------------
# ADC — GP26-28 are the only free pins (touch plate sensing is a future option)
# ---------------------------------------------------------------------------
ADC_0      = 26            # GP26 — ADC0
ADC_1      = 27            # GP27 — ADC1
ADC_2      = 28            # GP28 — ADC2

# ---------------------------------------------------------------------------
# I²C1 — EFFIGY peer-pair bus — SHELVED (owner decision, 2026-10-17)
#   Kept as an idea for another project; not part of this build. No rear
#   header is fitted. GP2 and GP3 are now the main OLED's SCK and MOSI and
#   GP11 is the gate input (above), so these values must not be used: they remain only because
#   effigy_bridge.py still reads them (a firmware follow-up removes them).
#   See docs/MACROBRUTE_EFFIGY_BRIDGE.md (archived) for the register map.
# ---------------------------------------------------------------------------
DAISY_I2C_ID = 1
DAISY_SDA    = 2           # SHELVED; GP2 is OLED_SCK
DAISY_SCL    = 3           # SHELVED; GP3 is OLED_MOSI
DAISY_INT    = 11          # SHELVED; GP11 is GATE_IN
DAISY_ADDR   = 0x42        # Shared contract — see bridge spec
DAISY_FREQ   = 100_000     # SHELVED, n/a: no rear cable is fitted (EFFIGY pairing shelved)

# ---------------------------------------------------------------------------
# Free GPIO inventory
#   3 free pins: GP26, GP27, GP28 (ADC-capable, not fault tolerant). GP2 and
#   GP3 are the main OLED (SPI); GP11 is the gate input. GP26 PWM is slice 5A, the same channel
#   as GP10 (LED_MODE).
#   GP23, GP24, GP25, GP29 are RP2040-internal — not exposed.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Clock defaults
# ---------------------------------------------------------------------------
DEFAULT_BPM     = 120
MIN_BPM         = 20
MAX_BPM         = 300
CLOCK_GATE_MS   = 10        # gate pulse width in ms
TAP_TIMEOUT_MS  = 2000      # reset tap buffer after this silence
TAP_DEBOUNCE_MS = 50        # minimum time between taps
TAP_BUFFER_SIZE = 8         # rolling window of taps

# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------
ENC_DEBOUNCE_MS = 2         # hardware RC filter handles most bounce
LONG_PRESS_MS   = 600       # hold encoder button for "back"

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
DISPLAY_FPS           = 20      # target refresh rate (main OLED)
STRIP_DISPLAY_FPS     = 5       # strip OLED (dropped) — kept for strip_display.py
MENU_VISIBLE_ITEMS    = 4       # lines visible on 64-px tall OLED
FONT_HEIGHT           = 12      # pixels per text line (with spacing)
SCREENSAVER_TIMEOUT_S = 120     # dim main OLED after 2 minutes idle
SCREENSAVER_DIM_LEVEL = 32      # 0–255 contrast value during screensaver

# ---------------------------------------------------------------------------
# USB-MIDI (Pico micro-USB enumerates as MIDI-class device via TinyUSB)
# ---------------------------------------------------------------------------
USBMIDI_VENDOR_ID  = 0x2E8A   # Raspberry Pi Foundation
USBMIDI_PRODUCT_ID = 0x000A   # generic Pico
USBMIDI_NAME       = "Macrobrute Pico"
USBMIDI_CHANNEL    = 0        # default MIDI channel (0–15) for outgoing events

# ---------------------------------------------------------------------------
# Tap button modes
# ---------------------------------------------------------------------------
TAP_MODE_TEMPO     = 0   # short presses → tap tempo
TAP_MODE_GATE      = 1   # long press → manual gate (released = gate off)
TAP_LONG_PRESS_MS  = 400 # hold tap > this many ms to enter manual-gate mode
