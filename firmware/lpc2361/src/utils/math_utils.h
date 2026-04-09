#ifndef MATH_UTILS_H
#define MATH_UTILS_H

#include <stdint.h>

// MIDI note to DAC value (1V/oct, 10-bit DAC)
// C0 = note 0 = 0V, C5 = note 60 = 5V
// 10-bit DAC: 0-1023 maps to 0V-3.3V (on-chip DAC)
// MCP4728 12-bit: 0-4095 maps to 0-Vref
uint16_t note_to_dac(uint8_t note);

// Scale quantization
// Returns the nearest note in the given scale
uint8_t quantize_to_scale(uint8_t note, uint8_t scale, uint8_t root);

// Pseudo-random number generator (LFSR)
uint16_t random_next(void);
uint8_t  random_range(uint8_t min, uint8_t max);
uint8_t  random_percent(void);

// Scale definitions (bit masks for 12 semitones)
#define SCALE_CHROMATIC  0x0FFF  // All 12 notes
#define SCALE_MAJOR      0x0AB5  // W W H W W W H
#define SCALE_MINOR_NAT  0x05AD  // W H W W H W W
#define SCALE_MINOR_HARM 0x09AD  // W H W W H WH H
#define SCALE_PENTATONIC 0x0295  // W W WH W WH
#define SCALE_BLUES      0x04A9  // WH W H H WH W
#define SCALE_DORIAN     0x06AD  // W H W W W H W
#define SCALE_PHRYGIAN   0x056B  // H W W W H W W
#define SCALE_WHOLE_TONE 0x0555  // W W W W W W

#endif // MATH_UTILS_H
