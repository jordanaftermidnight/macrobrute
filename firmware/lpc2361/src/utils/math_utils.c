#include "math_utils.h"

// LFSR state (seeded on boot from timer)
static uint16_t lfsr_state = 0xACE1;

// DAC lookup table: note -> DAC value
// Assumes MCP4728 with internal 2.048V reference, gain 2x = 4.096V
// 1V/oct: note 0 (C-1) = 0V, note 60 (C4) = 5V
// DAC value = note * (4095 / (4.096 / (1.0/12)))
// Simplified: each semitone = 4095 / (12 * 4.096) ~= 83.3
// Pre-computed for speed
static const uint16_t note_table[] = {
    // Octave 0 (C0-B0): notes 0-11
    0, 83, 167, 250, 333, 417, 500, 583, 667, 750, 833, 917,
    // Octave 1: notes 12-23
    1000, 1083, 1167, 1250, 1333, 1417, 1500, 1583, 1667, 1750, 1833, 1917,
    // Octave 2: notes 24-35
    2000, 2083, 2167, 2250, 2333, 2417, 2500, 2583, 2667, 2750, 2833, 2917,
    // Octave 3: notes 36-47
    3000, 3083, 3167, 3250, 3333, 3417, 3500, 3583, 3667, 3750, 3833, 3917,
    // Octave 4+: clamp at 4095
    4000, 4083, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095,
};

uint16_t note_to_dac(uint8_t note) {
    if (note >= sizeof(note_table) / sizeof(note_table[0])) {
        return 4095;
    }
    return note_table[note];
}

uint8_t quantize_to_scale(uint8_t note, uint8_t scale, uint8_t root) {
    static const uint16_t scale_masks[] = {
        SCALE_CHROMATIC,
        SCALE_MAJOR,
        SCALE_MINOR_NAT,
        SCALE_MINOR_HARM,
        SCALE_PENTATONIC,
        SCALE_BLUES,
        SCALE_DORIAN,
        SCALE_PHRYGIAN,
        SCALE_WHOLE_TONE,
    };

    if (scale == 0 || scale >= sizeof(scale_masks) / sizeof(scale_masks[0])) {
        return note;
    }

    uint16_t mask = scale_masks[scale];
    uint8_t degree = (note - root + 12) % 12;

    // If this degree is in the scale, return as-is
    if (mask & (1 << degree)) {
        return note;
    }

    // Find nearest note in scale (search up and down)
    for (int offset = 1; offset <= 6; offset++) {
        uint8_t up = (degree + offset) % 12;
        if (mask & (1 << up)) {
            return note + offset;
        }
        uint8_t down = (degree - offset + 12) % 12;
        if (mask & (1 << down)) {
            return note - offset;
        }
    }

    return note;  // Fallback (shouldn't reach)
}

uint16_t random_next(void) {
    // 16-bit Galois LFSR, maximal period
    uint16_t bit = ((lfsr_state >> 0) ^ (lfsr_state >> 2) ^
                    (lfsr_state >> 3) ^ (lfsr_state >> 5)) & 1;
    lfsr_state = (lfsr_state >> 1) | (bit << 15);
    return lfsr_state;
}

uint8_t random_range(uint8_t min, uint8_t max) {
    if (min >= max) return min;
    return min + (random_next() % (max - min));
}

uint8_t random_percent(void) {
    return random_next() % 101;
}
