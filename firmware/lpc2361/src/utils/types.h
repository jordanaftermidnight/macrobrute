#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Volatile register access
#define __IO  volatile
#define __I   volatile const
#define __O   volatile

// Bit manipulation
#define BIT(n)           (1UL << (n))
#define BITS(h, l)       (((1UL << ((h) - (l) + 1)) - 1) << (l))
#define SET_BIT(reg, n)  ((reg) |= BIT(n))
#define CLR_BIT(reg, n)  ((reg) &= ~BIT(n))
#define TST_BIT(reg, n)  ((reg) & BIT(n))

// Min/max
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define CLAMP(x, lo, hi) (MIN(MAX((x), (lo)), (hi)))

// Array count
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

// MIDI note range
#define MIDI_NOTE_MIN  0
#define MIDI_NOTE_MAX  127

// CV voltage (millivolts)
typedef int16_t cv_mv_t;

// Error codes
typedef enum {
    ERR_OK = 0,
    ERR_TIMEOUT = -1,
    ERR_INVALID = -2,
    ERR_BUSY = -3,
    ERR_OVERFLOW = -4,
    ERR_HARDWARE = -5,
} error_t;

#endif // TYPES_H
