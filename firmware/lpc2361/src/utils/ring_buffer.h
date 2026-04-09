#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>

#define RING_BUF_SIZE 256  // Must be power of 2

typedef struct {
    uint8_t data[RING_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} RingBuffer;

void     ring_init(RingBuffer* rb);
bool     ring_put(RingBuffer* rb, uint8_t byte);
bool     ring_get(RingBuffer* rb, uint8_t* byte);
uint16_t ring_count(const RingBuffer* rb);
bool     ring_empty(const RingBuffer* rb);
bool     ring_full(const RingBuffer* rb);

#endif // RING_BUFFER_H
