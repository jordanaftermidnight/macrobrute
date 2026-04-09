#ifndef MIDI_OUTPUT_H
#define MIDI_OUTPUT_H

#include <stdint.h>

#if FEATURE_MIDI_OUT

void midi_out_init(void);
void midi_out_note_on(uint8_t channel, uint8_t note, uint8_t velocity);
void midi_out_note_off(uint8_t channel, uint8_t note);
void midi_out_cc(uint8_t channel, uint8_t cc, uint8_t value);
void midi_out_clock(void);
void midi_out_start(void);
void midi_out_stop(void);

#endif // FEATURE_MIDI_OUT

#endif // MIDI_OUTPUT_H
