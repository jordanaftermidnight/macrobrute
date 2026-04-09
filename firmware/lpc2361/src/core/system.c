/*
 * LPC2361 System Initialization
 * PLL setup: 12MHz crystal -> 60MHz CPU clock
 * MAM: Full acceleration
 */

#include "system.h"
#include "lpc2361.h"
#include "config.h"
#include "utils/debug.h"

static volatile uint32_t sys_tick_ms = 0;

int system_init(void) {
    // 1. Enable main oscillator (12MHz crystal)
    SCS |= (1 << 5);                // OSCEN
    while (!(SCS & (1 << 6)));      // Wait for OSCSTAT

    // 2. Select main oscillator as PLL clock source
    CLKSRCSEL = 0x01;               // Main oscillator

    // 3. Configure PLL0
    // Target: 60MHz CPU clock from 12MHz crystal
    // Fcco = 2 * M * Fin / N
    // M = 5, N = 1 -> Fcco = 2 * 5 * 12 = 120MHz
    // CCLK = Fcco / CCLKCFG = 120 / 2 = 60MHz
    PLL0CFG = ((1 - 1) << 16) | (5 - 1);   // N=1, M=5
    PLL0CON = 0x01;                 // Enable PLL
    PLL0FEED = 0xAA;
    PLL0FEED = 0x55;

    // Wait for PLL lock
    while (!(PLL0STAT & (1 << 26)));

    // 4. Set CPU clock divider
    CCLKCFG = 2 - 1;               // CCLK = Fcco / 2 = 60MHz

    // 5. Connect PLL
    PLL0CON = 0x03;                 // Enable + Connect
    PLL0FEED = 0xAA;
    PLL0FEED = 0x55;

    // 6. Setup Memory Accelerator Module
    MAMTIM = 3;                     // 3 clocks for >40MHz
    MAMCR = 2;                      // Full acceleration

    // 7. Set peripheral clock to CPU clock (no divider)
    PCLKSEL0 = 0x00000000;          // All peripherals at CCLK/4 default
    PCLKSEL1 = 0x00000000;

    // 8. Enable Fast GPIO
    SCS |= 0x01;                    // GPIOM bit

    return 0;
}

uint32_t system_tick_ms(void) {
    return sys_tick_ms;
}

// Called from Timer0 IRQ
void system_tick_increment(void) {
    sys_tick_ms++;
}

void delay_ms(uint32_t ms) {
    uint32_t start = sys_tick_ms;
    while ((sys_tick_ms - start) < ms);
}

void delay_us(uint32_t us) {
    // Rough busy-wait at 60MHz (~15 cycles per iteration)
    volatile uint32_t count = (us * (CPU_FREQ / 1000000)) / 15;
    while (count--);
}

void irq_enable(void) {
    __asm volatile ("mrs r0, cpsr\n"
                    "bic r0, r0, #0x80\n"
                    "msr cpsr_c, r0" ::: "r0");
}

void irq_disable(void) {
    __asm volatile ("mrs r0, cpsr\n"
                    "orr r0, r0, #0x80\n"
                    "msr cpsr_c, r0" ::: "r0");
}
