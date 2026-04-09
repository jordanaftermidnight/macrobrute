#ifndef ADC_H
#define ADC_H

#include <stdint.h>

// Initialize ADC (10-bit)
int adc_init(void);

// Read single channel (0-7), returns 10-bit value (0-1023)
uint16_t adc_read(uint8_t channel);

// Read channel in millivolts (0-3300)
uint16_t adc_read_mv(uint8_t channel);

#endif // ADC_H
