/*
 * VIC (Vectored Interrupt Controller) setup
 */

#include "interrupts.h"
#include "lpc2361.h"
#include "utils/debug.h"

void vic_install(uint8_t channel, uint8_t priority, void (*handler)(void)) {
    // VIC vector address registers are at 0xFFFFF100 + (channel * 4)
    volatile uint32_t *vect_addr = (volatile uint32_t *)(0xFFFFF100 + (channel * 4));
    volatile uint32_t *vect_prio = (volatile uint32_t *)(0xFFFFF200 + (channel * 4));

    *vect_addr = (uint32_t)handler;
    *vect_prio = priority & 0x0F;

    VICIntEnable = (1 << channel);

    DBG_INFO("VIC: ch%d -> prio %d", channel, priority);
}

void vic_enable(uint8_t channel) {
    VICIntEnable = (1 << channel);
}

void vic_disable(uint8_t channel) {
    VICIntEnClr = (1 << channel);
}
