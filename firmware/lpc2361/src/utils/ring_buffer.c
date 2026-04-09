#include "ring_buffer.h"

void ring_init(RingBuffer* rb) {
    rb->head = 0;
    rb->tail = 0;
}

bool ring_put(RingBuffer* rb, uint8_t byte) {
    uint16_t next = (rb->head + 1) & (RING_BUF_SIZE - 1);
    if (next == rb->tail) {
        return false;  // Full
    }
    rb->data[rb->head] = byte;
    rb->head = next;
    return true;
}

bool ring_get(RingBuffer* rb, uint8_t* byte) {
    if (rb->head == rb->tail) {
        return false;  // Empty
    }
    *byte = rb->data[rb->tail];
    rb->tail = (rb->tail + 1) & (RING_BUF_SIZE - 1);
    return true;
}

uint16_t ring_count(const RingBuffer* rb) {
    return (rb->head - rb->tail) & (RING_BUF_SIZE - 1);
}

bool ring_empty(const RingBuffer* rb) {
    return rb->head == rb->tail;
}

bool ring_full(const RingBuffer* rb) {
    return ((rb->head + 1) & (RING_BUF_SIZE - 1)) == rb->tail;
}
