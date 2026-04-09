"""MACROBRUTE Pico H — Hardware configuration and pin assignments."""

# --- OLED Display (SH1106 1.3" SPI) ---
OLED_SPI_ID = 0
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_SCK = 18    # GP18 — SPI0 SCK
OLED_MOSI = 19   # GP19 — SPI0 TX
OLED_CS = 17     # GP17 — SPI0 CSn
OLED_DC = 16     # GP16 — Data/Command
OLED_RST = 20    # GP20 — Reset

# --- Rotary Encoder (HW040) ---
ENC_CLK = 14     # GP14 — Rotation A
ENC_DT = 15      # GP15 — Rotation B
ENC_SW = 13      # GP13 — Push button

# --- Buttons ---
BTN_TAP = 12     # GP12 — Red button (tap tempo / manual gate)

# --- LEDs ---
LED_CLOCK = 8    # GP8  — Clock pulse indicator
LED_GATE = 9     # GP9  — Gate activity
LED_MODE = 10    # GP10 — Mode indicator

# --- Clock I/O ---
CLOCK_OUT = 22   # GP22 — Clock output (PIO)
CLOCK_IN = 21    # GP21 — Clock input (IRQ)

# --- MIDI (UART1 to MicroBrute MIDI IN via SysEx) ---
MIDI_TX = 4      # GP4  — UART1 TX
MIDI_RX = 5      # GP5  — UART1 RX
MIDI_BAUD = 31250

# --- LPC2361 UART (future, UART0) ---
LPC_TX = 0       # GP0  — UART0 TX
LPC_RX = 1       # GP1  — UART0 RX

# --- ADC (spare) ---
ADC_0 = 26       # GP26 — ADC0
ADC_1 = 27       # GP27 — ADC1

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
