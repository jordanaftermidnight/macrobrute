#ifndef KEYBOARD_H
#define KEYBOARD_H

#include <stdint.h>
#include <stdbool.h>

// Key event callback
typedef void (*key_callback_t)(uint8_t note, uint8_t velocity, bool pressed);

int keyboard_init(void);

// Scan matrix (called from main loop)
void keyboard_scan(void);

// Register callback for key events
void keyboard_set_callback(key_callback_t cb);

// Get current state
uint8_t keyboard_last_note(void);
bool keyboard_any_pressed(void);

#endif // KEYBOARD_H
