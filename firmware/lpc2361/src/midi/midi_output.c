/*
 * MIDI output (requires hardware MIDI OUT mod)
 * Sends via UART — port TBD
 */

#include "midi_output.h"
#include "config.h"

#if FEATURE_MIDI_OUT

#include "drivers/uart.h"

// MIDI output port (could be UART0 or additional UART)
#define MIDI_OUT_PORT 0

void midi_out_init(void) {
    // UART already initialized elsewhere
}

void midi_out_note_on(uint8_t channel, uint8_t note, uint8_t velocity) {
    uart_putc(MIDI_OUT_PORT, 0x90 | (channel & 0x0F));
    uart_putc(MIDI_OUT_PORT, note & 0x7F);
    uart_putc(MIDI_OUT_PORT, velocity & 0x7F);
}

void midi_out_note_off(uint8_t channel, uint8_t note) {
    uart_putc(MIDI_OUT_PORT, 0x80 | (channel & 0x0F));
    uart_putc(MIDI_OUT_PORT, note & 0x7F);
    uart_putc(MIDI_OUT_PORT, 0);
}

void midi_out_cc(uint8_t channel, uint8_t cc, uint8_t value) {
    uart_putc(MIDI_OUT_PORT, 0xB0 | (channel & 0x0F));
    uart_putc(MIDI_OUT_PORT, cc & 0x7F);
    uart_putc(MIDI_OUT_PORT, value & 0x7F);
}

void midi_out_clock(void) {
    uart_putc(MIDI_OUT_PORT, 0xF8);
}

void midi_out_start(void) {
    uart_putc(MIDI_OUT_PORT, 0xFA);
}

void midi_out_stop(void) {
    uart_putc(MIDI_OUT_PORT, 0xFC);
}

#endif // FEATURE_MIDI_OUT
