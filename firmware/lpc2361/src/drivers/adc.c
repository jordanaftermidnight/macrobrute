/*
 * ADC driver for LPC2361
 * 10-bit, 8 channels, burst mode available
 */

#include "adc.h"
#include "lpc2361.h"
#include "config.h"
#include "utils/debug.h"

int adc_init(void) {
    // Power on ADC
    PCONP |= (1 << 12);

    // PCLK = 15MHz, ADC clock must be <= 4.5MHz
    // CLKDIV = (15MHz / 4.5MHz) - 1 = 2.33 -> use 3
    AD0CR = (1 << 21)      // PDN (power on)
          | (3 << 8);      // CLKDIV = 3 -> ADC clock = 3.75MHz

    DBG_INFO("ADC: init complete");
    return 0;
}

uint16_t adc_read(uint8_t channel) {
    if (channel > 7) return 0;

    // Select channel, start conversion
    AD0CR &= ~(0xFF | (7 << 24));           // Clear channel select and start
    AD0CR |= (1 << channel) | (1 << 24);    // Select channel, start now

    // Wait for completion
    volatile uint32_t *dr = (volatile uint32_t *)(0xE0034010 + (channel * 4));
    while (!(*dr & (1UL << 31)));            // Wait for DONE bit

    // Read 10-bit result (bits [15:6])
    uint16_t result = (*dr >> 6) & 0x3FF;

    return result;
}

uint16_t adc_read_mv(uint8_t channel) {
    uint16_t raw = adc_read(channel);
    return (uint32_t)raw * 3300 / 1023;
}
