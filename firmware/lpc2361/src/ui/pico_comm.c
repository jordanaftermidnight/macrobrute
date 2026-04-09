/*
 * Pico communication over UART0
 * Bidirectional binary protocol
 */

#include "pico_comm.h"
#include "config.h"

#if FEATURE_PICO_COMM

#include "drivers/uart.h"
#include "utils/debug.h"
#include <string.h>

#define RX_BUF_SIZE 64

typedef enum {
    RX_IDLE,
    RX_CMD,
    RX_LEN,
    RX_DATA,
    RX_CHECKSUM
} RxState;

static RxState rx_state = RX_IDLE;
static uint8_t rx_cmd;
static uint8_t rx_len;
static uint8_t rx_buf[RX_BUF_SIZE];
static uint8_t rx_idx;
static uint8_t rx_checksum;

int pico_comm_init(void) {
    rx_state = RX_IDLE;
    DBG_INFO("Pico comm: ready on UART0");
    return 0;
}

static uint8_t calc_checksum(uint8_t cmd, uint8_t len, const uint8_t* data) {
    uint8_t cs = cmd ^ len;
    for (uint8_t i = 0; i < len; i++) {
        cs ^= data[i];
    }
    return cs;
}

static void send_packet(uint8_t cmd, const uint8_t* data, uint8_t len) {
    uart_putc(0, PICO_SYNC);
    uart_putc(0, cmd);
    uart_putc(0, len);
    for (uint8_t i = 0; i < len; i++) {
        uart_putc(0, data[i]);
    }
    uart_putc(0, calc_checksum(cmd, len, data));
}

static void handle_packet(uint8_t cmd, const uint8_t* data, uint8_t len) {
    switch (cmd) {
        case PICO_CMD_SET:
            if (len >= 3) {
                uint8_t param = data[0];
                uint16_t value = (data[1] << 8) | data[2];
                DBG_VERB("Pico: SET param %d = %d", param, value);
                // TODO: route to params module
            }
            break;

        case PICO_CMD_GET:
            if (len >= 1) {
                uint8_t param = data[0];
                DBG_VERB("Pico: GET param %d", param);
                // TODO: respond with param value
            }
            break;

        case PICO_CMD_HEART:
            // Respond with heartbeat
            send_packet(PICO_CMD_HEART, NULL, 0);
            break;

        default:
            DBG_VERB("Pico: unknown cmd 0x%02X", cmd);
            break;
    }
}

void pico_comm_update(void) {
    while (uart_available(0)) {
        uint8_t byte = (uint8_t)uart_read(0);

        switch (rx_state) {
            case RX_IDLE:
                if (byte == PICO_SYNC) {
                    rx_state = RX_CMD;
                }
                break;

            case RX_CMD:
                rx_cmd = byte;
                rx_state = RX_LEN;
                break;

            case RX_LEN:
                rx_len = byte;
                rx_idx = 0;
                rx_checksum = 0;
                if (rx_len == 0 || rx_len > RX_BUF_SIZE) {
                    rx_state = (rx_len == 0) ? RX_CHECKSUM : RX_IDLE;
                } else {
                    rx_state = RX_DATA;
                }
                break;

            case RX_DATA:
                rx_buf[rx_idx++] = byte;
                if (rx_idx >= rx_len) {
                    rx_state = RX_CHECKSUM;
                }
                break;

            case RX_CHECKSUM:
                if (byte == calc_checksum(rx_cmd, rx_len, rx_buf)) {
                    handle_packet(rx_cmd, rx_buf, rx_len);
                } else {
                    DBG_ERR("Pico: checksum fail");
                }
                rx_state = RX_IDLE;
                break;
        }
    }
}

void pico_send_param(uint8_t param_id, uint16_t value) {
    uint8_t data[3] = {param_id, (uint8_t)(value >> 8), (uint8_t)(value & 0xFF)};
    send_packet(PICO_CMD_RESP, data, 3);
}

void pico_send_debug(const char* str) {
    uint8_t len = strlen(str);
    if (len > RX_BUF_SIZE) len = RX_BUF_SIZE;
    send_packet(PICO_CMD_DEBUG, (const uint8_t*)str, len);
}

#endif // FEATURE_PICO_COMM
