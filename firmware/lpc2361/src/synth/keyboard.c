/*
 * Keyboard matrix scanner
 *
 * The MicroBrute has a 25-key keyboard (2 octaves + 1 note).
 * Keys are scanned via a matrix — exact pin mapping requires
 * tracing from the PCB or firmware RE.
 *
 * This is a skeleton implementation. Actual row/column pins
 * must be determined from the LPC2361 firmware dump.
 */

#include "keyboard.h"
#include "drivers/gpio.h"
#include "utils/debug.h"

// Matrix dimensions (estimated — verify from hardware)
#define KEY_ROWS 5
#define KEY_COLS 5
#define KEY_COUNT 25

// Note offset: lowest key = F1 (MIDI note 29) on MicroBrute
#define BASE_NOTE 29

static key_callback_t key_cb = NULL;
static uint8_t prev_state[KEY_ROWS];
static uint8_t last_note = 0;

// TODO: Determine actual row/column GPIO pins from firmware RE
// These are placeholders
static const uint8_t row_pins[KEY_ROWS] = {0, 1, 2, 3, 4};
static const uint8_t col_pins[KEY_COLS] = {5, 6, 7, 8, 9};
static const uint8_t row_port = 1;  // Port 1
static const uint8_t col_port = 1;  // Port 1

int keyboard_init(void) {
    // Configure row pins as outputs
    for (int r = 0; r < KEY_ROWS; r++) {
        gpio_set_output(row_port, row_pins[r]);
        gpio_clear(row_port, row_pins[r]);
    }

    // Configure column pins as inputs
    for (int c = 0; c < KEY_COLS; c++) {
        gpio_set_input(col_port, col_pins[c]);
    }

    // Clear previous state
    for (int r = 0; r < KEY_ROWS; r++) {
        prev_state[r] = 0;
    }

    DBG_INFO("Keyboard: init %d keys (base note %d)", KEY_COUNT, BASE_NOTE);
    return 0;
}

void keyboard_scan(void) {
    for (int r = 0; r < KEY_ROWS; r++) {
        // Drive this row high
        gpio_set(row_port, row_pins[r]);

        // Small settling delay
        for (volatile int d = 0; d < 10; d++);

        // Read columns
        uint8_t cols = 0;
        for (int c = 0; c < KEY_COLS; c++) {
            if (gpio_read(col_port, col_pins[c])) {
                cols |= (1 << c);
            }
        }

        // Drive row back low
        gpio_clear(row_port, row_pins[r]);

        // Detect changes
        uint8_t changed = cols ^ prev_state[r];
        if (changed && key_cb) {
            for (int c = 0; c < KEY_COLS; c++) {
                if (changed & (1 << c)) {
                    uint8_t note = BASE_NOTE + (r * KEY_COLS) + c;
                    bool pressed = (cols & (1 << c)) != 0;
                    if (pressed) last_note = note;
                    key_cb(note, pressed ? 100 : 0, pressed);
                    DBG_VERB("Key: note %d %s", note, pressed ? "ON" : "OFF");
                }
            }
        }

        prev_state[r] = cols;
    }
}

void keyboard_set_callback(key_callback_t cb) {
    key_cb = cb;
}

uint8_t keyboard_last_note(void) {
    return last_note;
}

bool keyboard_any_pressed(void) {
    for (int r = 0; r < KEY_ROWS; r++) {
        if (prev_state[r] != 0) return true;
    }
    return false;
}
