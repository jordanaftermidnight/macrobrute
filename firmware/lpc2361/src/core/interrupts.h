#ifndef INTERRUPTS_H
#define INTERRUPTS_H

#include <stdint.h>

// Install an IRQ handler in the VIC
void vic_install(uint8_t channel, uint8_t priority, void (*handler)(void));

// Enable/disable specific VIC channel
void vic_enable(uint8_t channel);
void vic_disable(uint8_t channel);

// IRQ handlers (implemented in respective drivers)
void timer0_irq_handler(void);
void uart0_irq_handler(void);
void uart1_irq_handler(void);
void i2c0_irq_handler(void);

#endif // INTERRUPTS_H
