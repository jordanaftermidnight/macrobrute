/*
 * UART driver for LPC2361
 * UART0: Debug/ISP/Pico comm (P0.2 TXD0, P0.3 RXD0)
 * UART1: MIDI IN (P0.16 RXD1)
 */

#include "uart.h"
#include "lpc2361.h"
#include "config.h"
#include "utils/ring_buffer.h"
#include "core/interrupts.h"

static RingBuffer uart0_rx_buf;
static RingBuffer uart1_rx_buf;

int uart_init(uint8_t port, uint32_t baudrate) {
    // Calculate divisor: DL = PCLK / (16 * baud)
    // PCLK = CPU_FREQ / 4 = 15MHz (default PCLKSEL)
    uint32_t pclk = CPU_FREQ / 4;
    uint16_t dl = pclk / (16 * baudrate);

    if (port == 0) {
        ring_init(&uart0_rx_buf);

        // Enable UART0 power (on by default)
        PCONP |= (1 << 3);

        // Pin select: P0.2 = TXD0 (func 01), P0.3 = RXD0 (func 01)
        PINSEL0 &= ~((3 << 4) | (3 << 6));
        PINSEL0 |=  ((1 << 4) | (1 << 6));

        // 8N1
        U0LCR = 0x83;          // DLAB=1, 8-bit, 1 stop, no parity
        U0DLL = dl & 0xFF;
        U0DLM = (dl >> 8) & 0xFF;
        U0LCR = 0x03;          // DLAB=0

        // Enable FIFO, reset
        U0FCR = 0x07;          // Enable FIFO, clear RX/TX

        // Enable RX interrupt
        U0IER = 0x01;          // RBR interrupt enable

        // Install VIC handler
        vic_install(VIC_UART0, 6, uart0_irq_handler);

    } else if (port == 1) {
        ring_init(&uart1_rx_buf);

        // Enable UART1 power
        PCONP |= (1 << 4);

        // Pin select: P0.16 = RXD1 (PINSEL1 bits [1:0] = 01)
        PINSEL1 &= ~(3 << 0);
        PINSEL1 |=  (1 << 0);

        // 8N1 for MIDI (31250 baud)
        U1LCR = 0x83;
        U1DLL = dl & 0xFF;
        U1DLM = (dl >> 8) & 0xFF;
        U1LCR = 0x03;

        U1FCR = 0x07;
        U1IER = 0x01;

        vic_install(VIC_UART1, 5, uart1_irq_handler);
    }

    return 0;
}

void uart_putc(uint8_t port, char c) {
    if (port == 0) {
        while (!(U0LSR & U0LSR_THRE));
        U0THR = c;
    } else {
        while (!(U1LSR & (1 << 5)));
        U1THR = c;
    }
}

char uart_getc(uint8_t port) {
    uint8_t byte;
    RingBuffer *rb = (port == 0) ? &uart0_rx_buf : &uart1_rx_buf;
    while (!ring_get(rb, &byte));
    return (char)byte;
}

bool uart_available(uint8_t port) {
    RingBuffer *rb = (port == 0) ? &uart0_rx_buf : &uart1_rx_buf;
    return !ring_empty(rb);
}

int uart_read(uint8_t port) {
    uint8_t byte;
    RingBuffer *rb = (port == 0) ? &uart0_rx_buf : &uart1_rx_buf;
    if (ring_get(rb, &byte)) {
        return byte;
    }
    return -1;
}

void uart_write(uint8_t port, const uint8_t *data, uint16_t len) {
    for (uint16_t i = 0; i < len; i++) {
        uart_putc(port, data[i]);
    }
}

void uart_puts(uint8_t port, const char *str) {
    while (*str) {
        uart_putc(port, *str++);
    }
}

// UART0 IRQ handler
void uart0_irq_handler(void) {
    uint32_t iir = U0IIR;
    if ((iir & 0x0E) == 0x04) {     // RDA interrupt
        while (U0LSR & U0LSR_RDR) {
            uint8_t byte = U0RBR;
            ring_put(&uart0_rx_buf, byte);
        }
    }
    VICVectAddr = 0;                // Acknowledge VIC
}

// UART1 IRQ handler (MIDI)
void uart1_irq_handler(void) {
    uint32_t iir = U1IIR;
    if ((iir & 0x0E) == 0x04) {
        while (U1LSR & (1 << 0)) {
            uint8_t byte = U1RBR;
            ring_put(&uart1_rx_buf, byte);
        }
    }
    VICVectAddr = 0;
}
