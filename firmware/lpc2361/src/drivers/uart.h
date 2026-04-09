#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>

// Initialize UART port (0 = debug, 1 = MIDI)
int uart_init(uint8_t port, uint32_t baudrate);

// Blocking single-byte I/O
void uart_putc(uint8_t port, char c);
char uart_getc(uint8_t port);

// Non-blocking check
bool uart_available(uint8_t port);

// Read byte (non-blocking, returns -1 if empty)
int uart_read(uint8_t port);

// Write buffer
void uart_write(uint8_t port, const uint8_t *data, uint16_t len);

// Write string
void uart_puts(uint8_t port, const char *str);

#endif // UART_H
