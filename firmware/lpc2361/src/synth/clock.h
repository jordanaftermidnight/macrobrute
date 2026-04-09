#ifndef CLOCK_H
#define CLOCK_H

#include <stdint.h>

// Clock callback (called on each tick)
typedef void (*clock_tick_fn)(void);

int clock_init(void);
void clock_update(void);

void clock_set_bpm(uint16_t bpm);
uint16_t clock_get_bpm(void);

void clock_start(void);
void clock_stop(void);

// Set external tick callback (for sequencer)
void clock_set_tick_callback(clock_tick_fn fn);

// Get step duration in ms (for gate length calc)
uint32_t clock_step_duration_ms(void);

#endif // CLOCK_H
