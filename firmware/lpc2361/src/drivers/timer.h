#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

// Initialize Timer0 for 1ms system tick
int timer_init(void);

// Get current tick count (ms)
uint32_t timer_get_ms(void);

// Get microsecond counter (Timer1, free-running)
uint32_t timer_get_us(void);

#endif // TIMER_H
