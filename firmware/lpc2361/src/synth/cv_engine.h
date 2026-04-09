#ifndef CV_ENGINE_H
#define CV_ENGINE_H

#include <stdint.h>

// Initialize CV/Gate engine
int cv_engine_init(void);

// Set pitch CV from MIDI note
void cv_set_note(uint8_t note);

// Set pitch CV from raw DAC value
void cv_set_raw(uint16_t value);

// Gate control
void cv_gate_on(void);
void cv_gate_off(void);

// Schedule gate off after percentage of step time
void cv_schedule_gate_off(uint8_t percent);

// Update (called from main loop for gate timing)
void cv_engine_update(void);

#endif // CV_ENGINE_H
