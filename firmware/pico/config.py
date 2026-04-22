"""MACROBRUTE Pico WH — Hardware configuration and pin assignments."""

# --- OLED Display (SH1106 1.3" I2C, 128x64) ---
# Fallbacks: 0.96" SSD1306 I2C (same pins, swap driver), 16x2 1602 I2C LCD (different driver)
OLED_I2C_ID = 0
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_SDA = 4      # GP4  — I2C0 SDA
OLED_SCL = 5      # GP5  — I2C0 SCL
OLED_ADDR = 0x3C  # Standard SH1106/SSD1306 I2C address (alt: 0x3D)
OLED_COL_OFFSET = 2  # SH1106 column offset; set to 0 for SSD1306

# --- LPC2361 Pico Bridge (UART0) ---
LPC_TX = 0        # GP0  — UART0 TX → LPC2361 P0.16 (RXD1)
LPC_RX = 1        # GP1  — UART0 RX ← LPC2361 P0.15 (TXD1)
LPC_BAUD = 115200

# --- Rotary Encoder (HW040) ---
ENC_CLK = 14      # GP14 — Rotation A
ENC_DT = 15       # GP15 — Rotation B
ENC_SW = 13       # GP13 — Push button

# --- Buttons ---
BTN_TAP = 12      # GP12 — Red button (tap tempo / manual gate)

# --- LEDs ---
LED_CLOCK = 8     # GP8  — Clock pulse indicator
LED_GATE = 9      # GP9  — Gate activity
LED_MODE = 10     # GP10 — Mode indicator

# --- Clock I/O ---
CLOCK_OUT = 22    # GP22 — Clock output (PIO)
CLOCK_IN = 21     # GP21 — Clock input (IRQ)

# --- ADC (spare) ---
ADC_0 = 26       # GP26 — ADC0
ADC_1 = 27       # GP27 — ADC1

# --- Free GPIO (GP16-GP20, previously SPI OLED) ---
# GP16, GP17, GP18, GP19, GP20 available for future expansion
# (SD card, extra encoders, expansion header, etc.)

# --- Clock defaults ---
DEFAULT_BPM = 120
MIN_BPM = 20
MAX_BPM = 300
CLOCK_GATE_MS = 10          # Gate pulse width in ms
TAP_TIMEOUT_MS = 2000       # Reset tap buffer after this silence
TAP_DEBOUNCE_MS = 50        # Minimum time between taps
TAP_BUFFER_SIZE = 8         # Rolling window of taps

# --- Encoder ---
ENC_DEBOUNCE_MS = 2         # Hardware RC filter handles most bounce
LONG_PRESS_MS = 600         # Hold encoder button for "back"

# --- Display ---
DISPLAY_FPS = 20            # Target refresh rate
MENU_VISIBLE_ITEMS = 4      # Lines visible on 64px tall OLED
FONT_HEIGHT = 12            # Pixels per text line (with spacing)
SCREENSAVER_TIMEOUT_S = 120 # Dim after 2 minutes idle
