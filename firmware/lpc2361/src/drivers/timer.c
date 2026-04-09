/*
 * Timer driver for LPC2361
 * Timer0: 1ms system tick (interrupt-driven)
 * Timer1: Free-running microsecond counter
 */

#include "timer.h"
#include "lpc2361.h"
#include "config.h"
#include "core/interrupts.h"
#include "core/system.h"

int timer_init(void) {
    uint32_t pclk = CPU_FREQ / 4;  // Default PCLK divider

    // --- Timer0: 1ms system tick ---
    PCONP |= (1 << 1);             // Power on Timer0

    T0TCR = 0x02;                   // Reset counter
    T0PR = 0;                       // No prescaler
    T0MR0 = pclk / 1000;           // Match every 1ms
    T0MCR = 0x03;                   // Interrupt + reset on MR0 match
    T0TCR = 0x01;                   // Enable counter

    vic_install(VIC_TIMER0, 1, timer0_irq_handler);

    // --- Timer1: Free-running microsecond counter ---
    PCONP |= (1 << 2);             // Power on Timer1

    T1TCR = 0x02;                   // Reset
    T1PR = (pclk / 1000000) - 1;   // Prescale to 1MHz (1us ticks)
    T1MCR = 0;                      // No match actions, free-run
    T1TCR = 0x01;                   // Enable

    return 0;
}

uint32_t timer_get_ms(void) {
    return system_tick_ms();
}

uint32_t timer_get_us(void) {
    return T1TC;
}

// Timer0 IRQ handler (1ms tick)
void timer0_irq_handler(void) {
    T0IR = 0x01;                    // Clear MR0 interrupt
    system_tick_increment();
    VICVectAddr = 0;                // Acknowledge VIC
}
