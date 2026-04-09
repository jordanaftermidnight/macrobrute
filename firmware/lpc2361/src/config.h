#ifndef CONFIG_H
#define CONFIG_H

// ===================
// BUILD CONFIGURATION
// ===================

// Debug level (0=off, 1=err, 2=info, 3=verbose)
#define DEBUG_LEVEL 2

// Debug UART baud rate
#define DEBUG_BAUD 115200

// ===================
// FEATURE FLAGS
// ===================

// Enable extended sequencer (64 steps vs 8)
#define FEATURE_EXTENDED_SEQ 1

// Enable per-step probability
#define FEATURE_PROBABILITY 1

// Enable ratcheting
#define FEATURE_RATCHET 1

// Enable euclidean patterns
#define FEATURE_EUCLIDEAN 1

// Enable arpeggiator
#define FEATURE_ARPEGGIATOR 1

// Enable Pico communication
#define FEATURE_PICO_COMM 1

// Enable MIDI output (requires hardware mod)
#define FEATURE_MIDI_OUT 0

// ===================
// HARDWARE CONFIG
// ===================

// Crystal frequency (Hz)
#define XTAL_FREQ 12000000

// CPU frequency (Hz) — PLL multiplied from 12MHz crystal
#define CPU_FREQ 60000000

// Peripheral clock divider (PCLK = CPU_FREQ / PCLK_DIV)
#define PCLK_DIV 1

// Sequencer
#define SEQ_MAX_STEPS 64
#define SEQ_MAX_PATTERNS 8

// MIDI
#define MIDI_BAUD 31250

// ===================
// PIN ASSIGNMENTS
// ===================

// UART0 (Debug + ISP + Pico comm)
#define PIN_UART0_TX_PORT  0
#define PIN_UART0_TX_PIN   2   // P0.2 (TXD0)
#define PIN_UART0_RX_PORT  0
#define PIN_UART0_RX_PIN   3   // P0.3 (RXD0)

// UART1 (MIDI IN via optocoupler)
#define PIN_MIDI_RX_PORT   0
#define PIN_MIDI_RX_PIN    16  // P0.16 (RXD1) — verify on PCB

// ISP entry (active LOW during reset)
#define PIN_ISP_ENTRY_PORT 2
#define PIN_ISP_ENTRY_PIN  10  // P2.10

// DAC output (10-bit, pitch CV)
#define PIN_DAC_OUT        26  // P0.26 (AOUT)

// Gate output
#define PIN_GATE_PORT      0
#define PIN_GATE_PIN       25  // P0.25 — verify on PCB

// I2C0 (MCP4728 DAC)
#define PIN_I2C0_SDA_PORT  0
#define PIN_I2C0_SDA_PIN   27  // P0.27 (SDA0)
#define PIN_I2C0_SCL_PORT  0
#define PIN_I2C0_SCL_PIN   28  // P0.28 (SCL0)

// MCP4728 I2C address
#define MCP4728_ADDR       0x60

#endif // CONFIG_H
