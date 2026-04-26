"""MACROBRUTE Pico WH — Hardware configuration and pin assignments.

Authoritative source for pin allocation. The connection map (docs/
MACROBRUTE_CONNECTION_MAP.md §1) and this file must be kept in sync.
"""

# ---------------------------------------------------------------------------
# Main OLED — SH1106 1.3" I²C, 128×64
#   Fallbacks: 0.96" SSD1306 (same pins, set OLED_COL_OFFSET=0),
#              16×2 1602 I²C LCD (different driver entirely)
# Bus: I²C0 — shared with strip OLED below.
# ---------------------------------------------------------------------------
OLED_I2C_ID      = 0
OLED_WIDTH       = 128
OLED_HEIGHT      = 64
OLED_SDA         = 4       # GP4  — I²C0 SDA
OLED_SCL         = 5       # GP5  — I²C0 SCL
OLED_ADDR        = 0x3C    # SH1106/SSD1306 default (alt 0x3D = strip OLED)
OLED_COL_OFFSET  = 2       # SH1106 needs 2; SSD1306 = 0

# ---------------------------------------------------------------------------
# Strip OLED — 0.91" SSD1306 128×32, mounted on the MicroBrute panel
#   Shares I²C0 bus with the main OLED. Bus is carried over DB-9 B pins 3/4.
#   Strip OLED uses alt I²C address 0x3D (jumper on module).
# ---------------------------------------------------------------------------
STRIP_OLED_I2C_ID = 0      # Same bus as main OLED
STRIP_OLED_WIDTH  = 128
STRIP_OLED_HEIGHT = 32
STRIP_OLED_ADDR   = 0x3D   # SSD1306 alt address (must be jumpered on module)

# ---------------------------------------------------------------------------
# LPC2361 ↔ Pico UART bridge — UART0 over DB-9 B pins 1/2
#   Frame: 0xAA [msg_type] [counter] [len] [payload...] [xor_checksum]
#   Pico is the controller; LPC firmware handles routing of stock MIDI events.
# ---------------------------------------------------------------------------
LPC_TX     = 0             # GP0  — UART0 TX → LPC2361 P0.16 (RXD1)
LPC_RX     = 1             # GP1  — UART0 RX ← LPC2361 P0.15 (TXD1)
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
LED_MODE   = 10            # GP10 — RGB B channel (mode / pair status)

# ---------------------------------------------------------------------------
# Clock I/O (3.3 V logic on expander panel jacks)
# ---------------------------------------------------------------------------
CLOCK_OUT  = 22            # GP22 — Master clock out (PIO)
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
# ADC (spare — touch plate sensing future)
# ---------------------------------------------------------------------------
ADC_0      = 26            # GP26 — ADC0
ADC_1      = 27            # GP27 — ADC1
ADC_2      = 28            # GP28 — ADC2

# ---------------------------------------------------------------------------
# I²C1 — EFFIGY peer-pair bus (rear JST-XH header, hidden behind panel)
#   Pico is the controller. EFFIGY (Daisy Seed) is the I²C target at 0x42.
#   See docs/MACROBRUTE_EFFIGY_BRIDGE.md for the full register map.
# ---------------------------------------------------------------------------
DAISY_I2C_ID = 1
DAISY_SDA    = 2           # GP2  — I²C1 SDA
DAISY_SCL    = 3           # GP3  — I²C1 SCL
DAISY_INT    = 11          # GP11 — INT input from EFFIGY (active-low, pull-up)
DAISY_ADDR   = 0x42        # Shared contract — see bridge spec
DAISY_FREQ   = 100_000     # 100 kHz over rear cable

# ---------------------------------------------------------------------------
# Free GPIO inventory
#   No truly free pins remain after this allocation — all GPIO are assigned.
#   GP23, GP24, GP25 are RP2040-internal (SMPS / VBUS / LED) — not exposed.
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
STRIP_DISPLAY_FPS     = 5       # strip OLED — slower, glanceable status only
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
