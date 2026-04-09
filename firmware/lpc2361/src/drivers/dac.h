#ifndef DAC_H
#define DAC_H

#include <stdint.h>

// Initialize on-chip 10-bit DAC (P0.26/AOUT)
int dac_init(void);

// Write raw 10-bit value (0-1023)
void dac_write(uint16_t value);

// Write voltage in millivolts (0-3300)
void dac_write_mv(uint16_t mv);

// Initialize I2C for MCP4728 external DAC
int mcp4728_init(void);

// Write to MCP4728 channel (0-3), 12-bit value (0-4095)
void mcp4728_write(uint8_t channel, uint16_t value);

#endif // DAC_H
