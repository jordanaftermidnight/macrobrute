/*
 * DAC driver
 * On-chip 10-bit DAC on P0.26 (AOUT)
 * MCP4728 4-channel 12-bit I2C DAC at address 0x60
 */

#include "dac.h"
#include "lpc2361.h"
#include "config.h"
#include "utils/debug.h"

int dac_init(void) {
    // Configure P0.26 as DAC output (PINSEL1 bits [21:20] = 10)
    PINSEL1 &= ~(3 << 20);
    PINSEL1 |=  (2 << 20);

    // Set initial value to 0
    DACR = 0;

    DBG_INFO("DAC: on-chip 10-bit ready");
    return 0;
}

void dac_write(uint16_t value) {
    if (value > 1023) value = 1023;
    // DACR bits [15:6] = value, bit 16 = BIAS (0 = max settling, 1 = power save)
    DACR = (value << 6);
}

void dac_write_mv(uint16_t mv) {
    if (mv > 3300) mv = 3300;
    uint16_t value = (uint32_t)mv * 1023 / 3300;
    dac_write(value);
}

int mcp4728_init(void) {
    // Enable I2C0 power
    PCONP |= (1 << 7);

    // Configure I2C0 pins: P0.27 = SDA0, P0.28 = SCL0
    PINSEL1 &= ~((3 << 22) | (3 << 24));
    PINSEL1 |=  ((1 << 22) | (1 << 24));

    // I2C clock: ~100kHz
    // PCLK = 15MHz, I2C period = SCLH + SCLL
    // 15MHz / 100kHz = 150, split evenly
    I2C0SCLH = 75;
    I2C0SCLL = 75;

    // Enable I2C0
    I2C0CONCLR = 0x6C;             // Clear all flags
    I2C0CONSET = I2C_EN;           // Enable

    DBG_INFO("DAC: MCP4728 I2C init (addr 0x%02X)", MCP4728_ADDR);
    return 0;
}

// I2C helper: wait for SI flag
static void i2c_wait(void) {
    while (!(I2C0CONSET & I2C_SI));
}

void mcp4728_write(uint8_t channel, uint16_t value) {
    if (channel > 3) return;
    if (value > 4095) value = 4095;

    // Multi-write command: 0x40 | (channel << 1)
    uint8_t cmd = 0x40 | (channel << 1);
    uint8_t hi = (value >> 8) & 0x0F;   // Upper 4 bits + Vref/PD/Gain
    uint8_t lo = value & 0xFF;           // Lower 8 bits

    // Internal Vref, gain 2x, powered on
    hi |= 0x90;                          // Vref=1(internal), PD=00, Gain=1(2x)

    // START
    I2C0CONSET = I2C_STA;
    i2c_wait();

    // Send address + write
    I2C0DAT = (MCP4728_ADDR << 1);
    I2C0CONCLR = I2C_STA | I2C_SI;
    i2c_wait();

    // Send command
    I2C0DAT = cmd;
    I2C0CONCLR = I2C_SI;
    i2c_wait();

    // Send data high
    I2C0DAT = hi;
    I2C0CONCLR = I2C_SI;
    i2c_wait();

    // Send data low
    I2C0DAT = lo;
    I2C0CONCLR = I2C_SI;
    i2c_wait();

    // STOP
    I2C0CONSET = I2C_STO;
    I2C0CONCLR = I2C_SI;
}
