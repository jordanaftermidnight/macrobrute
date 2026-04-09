#ifndef PICO_COMM_H
#define PICO_COMM_H

#include <stdint.h>

/*
 * Pico <-> LPC2361 UART Communication Protocol
 *
 * Simple binary protocol over UART0:
 *   [SYNC] [CMD] [LEN] [DATA...] [CHECKSUM]
 *
 * Commands:
 *   0x01 = Set parameter
 *   0x02 = Get parameter
 *   0x03 = Parameter response
 *   0x10 = Sequencer state update
 *   0x11 = Clock state update
 *   0x20 = Debug message (string)
 *   0xFF = Heartbeat
 */

#define PICO_SYNC      0xAA
#define PICO_CMD_SET    0x01
#define PICO_CMD_GET    0x02
#define PICO_CMD_RESP   0x03
#define PICO_CMD_SEQ    0x10
#define PICO_CMD_CLK    0x11
#define PICO_CMD_DEBUG  0x20
#define PICO_CMD_HEART  0xFF

int pico_comm_init(void);
void pico_comm_update(void);

// Send parameter value to Pico
void pico_send_param(uint8_t param_id, uint16_t value);

// Send debug string to Pico
void pico_send_debug(const char* str);

#endif // PICO_COMM_H
