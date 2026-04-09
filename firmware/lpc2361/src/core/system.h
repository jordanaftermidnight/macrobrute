#ifndef SYSTEM_H
#define SYSTEM_H

#include <stdint.h>

// Initialize PLL, MAM, clock dividers
int system_init(void);

// Get system tick (milliseconds since boot)
uint32_t system_tick_ms(void);

// Busy-wait delay
void delay_ms(uint32_t ms);
void delay_us(uint32_t us);

// Enable/disable global interrupts
void irq_enable(void);
void irq_disable(void);

#endif // SYSTEM_H
